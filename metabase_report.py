#!/usr/bin/env python3
"""
Weekly Metabase survey/login metrics report.

Queries panel_login_session and discussion_activity across all configured
database sources. Writes a CSV + markdown report.

Usage:
    python metabase_report.py --start 2026-06-19 --end 2026-06-25
    python metabase_report.py                     # auto: last Fri → last Thu
    python metabase_report.py --dry-run
"""

import argparse
import csv
import os
import sys
import time
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

import requests
import yaml
from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).parent
load_dotenv(SCRIPT_DIR / ".env")

METABASE_URL = os.environ.get("METABASE_URL", "https://metabase.questionpro.net").rstrip("/")
SESSION_TOKEN = os.environ.get("METABASE_SESSION_TOKEN", "")

QUERIES = {
    "panel_login_session": (
        "select count(*) from panel_login_session "
        "where (panel_member_id is not null or panel_member_id != '') "
        "and session_start_ts >= '{start} 00:00:00' and session_start_ts <= '{end} 23:59:59'"
    ),
    "discussion_activity": (
        "select count(*) from discussion_activity "
        "where activity_type = 23 "
        "and ts >= '{start} 00:00:00' and ts <= '{end} 23:59:59'"
    ),
}

MAX_RETRIES = 3
RETRY_BACKOFF = 2


def get_week_range() -> tuple[str, str]:
    today = date.today()
    days_back = (today.weekday() - 3) % 7 or 7
    last_thursday = today - timedelta(days=days_back)
    last_friday = last_thursday - timedelta(days=6)
    return str(last_friday), str(last_thursday)


def authenticate(session: requests.Session) -> None:
    if not SESSION_TOKEN:
        print(
            "ERROR: METABASE_SESSION_TOKEN not set in .env\n"
            "  1. Open metabase.questionpro.net in Chrome\n"
            "  2. F12 → Network → any /api/... request → Headers → Cookie\n"
            "  3. Copy value after 'metabase.SESSION='\n"
            "  4. Paste as METABASE_SESSION_TOKEN in .env",
            file=sys.stderr,
        )
        sys.exit(1)
    session.headers["X-Metabase-Session"] = SESSION_TOKEN
    resp = session.get(f"{METABASE_URL}/api/user/current", timeout=15)
    if resp.status_code == 401:
        print("ERROR: Session token expired — re-copy from browser.", file=sys.stderr)
        sys.exit(1)
    resp.raise_for_status()
    print(f"Authenticated as: {resp.json().get('email', '?')}")


def run_query(
    session: requests.Session,
    database_id: int,
    sql: str,
    dry_run: bool = False,
) -> Optional[int]:
    if dry_run:
        print(f"    [DRY RUN] db={database_id} sql={sql[:80]}...")
        return None

    payload = {
        "type": "native",
        "native": {"template-tags": {}, "query": sql},
        "database": database_id,
        "parameters": [],
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = session.post(f"{METABASE_URL}/api/dataset", json=payload, timeout=120)
            resp.raise_for_status()
            data = resp.json()
            if data.get("status") == "completed":
                rows = data["data"]["rows"]
                return rows[0][0] if rows else 0
            print(f"    Query error (db={database_id}): {data.get('error', 'unknown')}", file=sys.stderr)
            return None
        except requests.RequestException as exc:
            if attempt == MAX_RETRIES:
                print(f"    HTTP error after {MAX_RETRIES} attempts: {exc}", file=sys.stderr)
                return None
            wait = RETRY_BACKOFF * attempt
            print(f"    Attempt {attempt} failed ({exc}), retrying in {wait}s...")
            time.sleep(wait)

    return None


def validate_config(config: dict) -> None:
    for dc, sources in config.get("databases", {}).items():
        for src in sources:
            db_id = src.get("database_id")
            if db_id == "FILL_IN" or not isinstance(db_id, int):
                print(
                    f"ERROR: config.yaml — DC '{dc}' source {src.get('result_source')} "
                    f"has database_id={db_id!r}. Run list_databases.py to find the real ID.",
                    file=sys.stderr,
                )
                sys.exit(1)


def fmt_count(n) -> str:
    if n is None or n == "ERROR":
        return str(n)
    return f"{int(n):,}"


def main(start_date: str = None, end_date: str = None, dry_run: bool = False,
         config_path: Path = None, output_dir: Path = None) -> dict:
    """
    Run the metrics report. Can be called directly or via CLI.
    Returns summary dict for use by run_all.py.
    """
    if config_path is None:
        config_path = SCRIPT_DIR / "config.yaml"
    if not config_path.exists():
        print(f"ERROR: {config_path} not found", file=sys.stderr)
        sys.exit(1)

    with open(config_path) as f:
        config = yaml.safe_load(f)

    if not dry_run:
        validate_config(config)

    if not start_date or not end_date:
        start_date, end_date = get_week_range()

    print(f"[metrics] {start_date} → {end_date}")

    session = requests.Session()
    if not dry_run:
        authenticate(session)

    col_login = f"({start_date} - {end_date}) panel_login_session"
    col_disc  = f"({start_date} - {end_date}) discussion_activity"

    output_rows = []
    totals = {col_login: 0, col_disc: 0}

    for dc_name, sources in config["databases"].items():
        print(f"  [{dc_name}]")
        for src in sources:
            result_source = src["result_source"]
            db_id = src["database_id"]

            row: dict = {
                "DC": dc_name,
                "DC Result Source": result_source,
                col_login: None,
                col_disc: None,
            }

            for query_key, col_name in [
                ("panel_login_session", col_login),
                ("discussion_activity", col_disc),
            ]:
                sql = QUERIES[query_key].format(start=start_date, end=end_date)
                count = run_query(session, db_id, sql, dry_run=dry_run)
                row[col_name] = count if count is not None else "ERROR"
                if isinstance(count, int):
                    totals[col_name] += count
                print(f"    source={result_source:>3}  db={db_id:<6}  {query_key}: {count}")

            output_rows.append(row)

    output_rows.append({
        "DC": "TOTAL",
        "DC Result Source": "",
        col_login: totals[col_login],
        col_disc: totals[col_disc],
    })

    print(f"\n  TOTAL panel_login_session : {totals[col_login]:,}")
    print(f"  TOTAL discussion_activity : {totals[col_disc]:,}")

    if dry_run:
        return {"start": start_date, "end": end_date, "totals": totals}

    # ── Output folder ─────────────────────────────────────────────────────────
    if output_dir is None:
        output_dir = SCRIPT_DIR / "reports" / f"{start_date}_to_{end_date}"
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── CSV ───────────────────────────────────────────────────────────────────
    csv_file = output_dir / "metrics_report.csv"
    fieldnames = ["DC", "DC Result Source", col_login, col_disc]
    with open(csv_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    # ── Markdown ──────────────────────────────────────────────────────────────
    md_lines = [
        f"# Metrics Report: {start_date} to {end_date}",
        "",
        "| DC | Source | Logins | Survey Activity |",
        "|---|---|---|---|",
    ]
    for r in output_rows:
        dc  = r["DC"]
        src = r["DC Result Source"]
        lg  = fmt_count(r[col_login])
        da  = fmt_count(r[col_disc])
        md_lines.append(f"| {dc} | {src} | {lg} | {da} |")

    md_lines += [
        "",
        "## Copy-paste block",
        "",
        "```",
        f"Metrics [{start_date} – {end_date}]",
        "",
        f"Total Logins (panel_login_session) : {totals[col_login]:,}",
        f"Total Survey Activity              : {totals[col_disc]:,}",
    ]

    # Per-DC totals for the copy-paste block
    dc_totals: dict[str, dict] = {}
    for r in output_rows:
        if r["DC"] == "TOTAL":
            continue
        dc = r["DC"]
        if dc not in dc_totals:
            dc_totals[dc] = {"login": 0, "disc": 0}
        v_login = r[col_login]
        v_disc  = r[col_disc]
        if isinstance(v_login, int):
            dc_totals[dc]["login"] += v_login
        if isinstance(v_disc, int):
            dc_totals[dc]["disc"] += v_disc

    for dc, vals in dc_totals.items():
        md_lines.append(f"  {dc} — logins: {vals['login']:,}  activity: {vals['disc']:,}")

    md_lines.append("```")

    md_file = output_dir / "metrics_report.md"
    md_file.write_text("\n".join(md_lines))

    print(f"\n  Saved → {csv_file}")
    print(f"  Saved → {md_file}")

    return {
        "start": start_date,
        "end": end_date,
        "totals": totals,
        "csv": str(csv_file),
        "md": str(md_file),
        "dc_totals": dc_totals,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Weekly Metabase survey/login metrics")
    parser.add_argument("--start",   help="Start date YYYY-MM-DD")
    parser.add_argument("--end",     help="End date YYYY-MM-DD")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--config",  default=None)
    args = parser.parse_args()

    main(
        start_date=args.start,
        end_date=args.end,
        dry_run=args.dry_run,
        config_path=Path(args.config) if args.config else None,
    )
