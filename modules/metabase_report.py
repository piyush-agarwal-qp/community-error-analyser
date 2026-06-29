#!/usr/bin/env python3
"""
Weekly survey/login metrics report.

Queries panel_login_session and discussion_activity across all configured
database sources via Metabase. Writes a CSV + markdown report.

Usage:
    python3 metabase_report.py --from 2026-06-19 --to 2026-06-25
    python3 metabase_report.py          # auto: last Fri → last Thu
    python3 metabase_report.py --dry-run
"""

import argparse
import csv
import sys
import time
from pathlib import Path

# Allow running as `python3 modules/metabase_report.py` directly
_pkg_root = str(Path(__file__).parent.parent)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

import requests
import yaml

from lib.metabase import METABASE_URL, SESSION_TOKEN, authenticate
from lib.utils import ROOT, get_week_range

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


def run_query(session: requests.Session, database_id: int, sql: str,
              dry_run: bool = False) -> int | None:
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
                    f"has database_id={db_id!r}.",
                    file=sys.stderr,
                )
                sys.exit(1)


def fmt_count(n) -> str:
    if n is None or n == "ERROR":
        return str(n)
    return f"{int(n):,}"


def main(start_date: str = None, end_date: str = None, dry_run: bool = False,
         config_path: Path = None, output_dir: Path = None) -> dict:

    if config_path is None:
        config_path = ROOT / "config.yaml"
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

    if output_dir is None:
        output_dir = ROOT / "reports" / f"{start_date}_to_{end_date}"
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_file = output_dir / "metrics_report.csv"
    fieldnames = ["DC", "DC Result Source", col_login, col_disc]
    with open(csv_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    md_lines = [
        f"# Metrics Report: {start_date} to {end_date}",
        "",
        "| DC | Source | Logins | Survey Activity |",
        "|---|---|---|---|",
    ]
    for r in output_rows:
        md_lines.append(
            f"| {r['DC']} | {r['DC Result Source']} "
            f"| {fmt_count(r[col_login])} | {fmt_count(r[col_disc])} |"
        )

    dc_totals: dict[str, dict] = {}
    for r in output_rows:
        if r["DC"] == "TOTAL":
            continue
        dc = r["DC"]
        if dc not in dc_totals:
            dc_totals[dc] = {"login": 0, "disc": 0}
        if isinstance(r[col_login], int):
            dc_totals[dc]["login"] += r[col_login]
        if isinstance(r[col_disc], int):
            dc_totals[dc]["disc"] += r[col_disc]

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
    parser = argparse.ArgumentParser(description="Weekly survey/login metrics report")
    parser.add_argument("--from",    dest="date_from", help="Start date YYYY-MM-DD")
    parser.add_argument("--to",      dest="date_to",   help="End date YYYY-MM-DD")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--config",  default=None)
    args = parser.parse_args()
    main(
        start_date=args.date_from,
        end_date=args.date_to,
        dry_run=args.dry_run,
        config_path=Path(args.config) if args.config else None,
    )
