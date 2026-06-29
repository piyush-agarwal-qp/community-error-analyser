#!/usr/bin/env python3
"""
Weekly Communities performance metrics report.

Uses saved Metabase questions (Admin=7301, Portal=7300) queried day-by-day
to avoid timeouts. Sums daily results and writes a detailed markdown report.

Usage:
    python performance_report.py --start 2026-06-19 --end 2026-06-25
    python performance_report.py          # auto: last Fri → last Thu
    python performance_report.py --dry-run
"""

import argparse
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).parent
load_dotenv(SCRIPT_DIR / ".env")

METABASE_URL  = os.environ.get("METABASE_URL", "https://metabase.questionpro.net").rstrip("/")
SESSION_TOKEN = os.environ.get("METABASE_SESSION_TOKEN", "")
ADMIN_Q_ID    = int(os.environ.get("METABASE_QUESTION_ID_PERF_ADMIN",  "7301"))
PORTAL_Q_ID   = int(os.environ.get("METABASE_QUESTION_ID_PERF_PORTAL", "7300"))

MAX_RETRIES   = 3
RETRY_BACKOFF = 2

BUCKETS = ["total_all_queries", "fast_lt_50ms", "slow_50_100ms",
           "slow_100_200ms", "slow_200_500ms", "slow_500_1000ms", "gt_than_1000ms"]


# ── Date helpers ──────────────────────────────────────────────────────────────

def get_week_range() -> tuple[str, str]:
    today = date.today()
    days_back = (today.weekday() - 3) % 7 or 7
    last_thursday = today - timedelta(days=days_back)
    last_friday = last_thursday - timedelta(days=6)
    return str(last_friday), str(last_thursday)


def daily_splits(start: date, end_inclusive: date) -> list[tuple[str, str]]:
    """Returns (date_from, date_to) pairs where date_to = next day (upper bound for <=)."""
    splits = []
    d = start
    while d <= end_inclusive:
        splits.append((str(d), str(d + timedelta(days=1))))
        d += timedelta(days=1)
    return splits


# ── Metabase helpers ──────────────────────────────────────────────────────────

def authenticate(session: requests.Session) -> None:
    if not SESSION_TOKEN:
        print("ERROR: METABASE_SESSION_TOKEN not set in .env", file=sys.stderr)
        sys.exit(1)
    session.headers["X-Metabase-Session"] = SESSION_TOKEN
    resp = session.get(f"{METABASE_URL}/api/user/current", timeout=15)
    if resp.status_code == 401:
        print("ERROR: Session token expired — re-copy from browser.", file=sys.stderr)
        sys.exit(1)
    resp.raise_for_status()
    print(f"Authenticated as: {resp.json().get('email', '?')}")


def run_question_day(session: requests.Session, question_id: int,
                     date_from: str, date_to: str,
                     label: str = "", dry_run: bool = False) -> Optional[dict]:
    if dry_run:
        print(f"  [DRY RUN] q={question_id} {label} {date_from}→{date_to}")
        return None

    body = {
        "parameters": [
            {"type": "date/single", "target": ["variable", ["template-tag", "date_from"]], "value": date_from},
            {"type": "date/single", "target": ["variable", ["template-tag", "date_to"]],   "value": date_to},
        ]
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = session.post(
                f"{METABASE_URL}/api/card/{question_id}/query",
                json=body, timeout=300,
            )
            resp.raise_for_status()
            data = resp.json()
            if data.get("status") == "failed":
                print(f"  Query failed ({label}): {data.get('error', '?')}", file=sys.stderr)
                return None
            cols = [c["name"] for c in data["data"]["cols"]]
            rows = data["data"]["rows"]
            return dict(zip(cols, rows[0])) if rows else {}
        except requests.RequestException as exc:
            if attempt == MAX_RETRIES:
                print(f"  HTTP error ({label}): {exc}", file=sys.stderr)
                return None
            wait = RETRY_BACKOFF * attempt
            print(f"  Attempt {attempt} failed, retrying in {wait}s...")
            time.sleep(wait)

    return None


# ── Aggregation ───────────────────────────────────────────────────────────────

def zero_buckets() -> dict:
    return {k: 0 for k in BUCKETS}


def add_row(totals: dict, row: Optional[dict]) -> dict:
    if not row:
        return totals
    result = dict(totals)
    for k in BUCKETS:
        result[k] += int(row.get(k, 0) or 0)
    return result


# ── Formatting ────────────────────────────────────────────────────────────────

def fmt(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.2f}M"
    if n >= 1_000:
        return f"{n / 1_000:.2f}K"
    return str(n)


def pct(n: int, total: int) -> str:
    return "0.00%" if total == 0 else f"{n / total * 100:.2f}%"


def render_block(label: str, d: dict) -> str:
    t = d["total_all_queries"]
    return "\n".join([
        f"• {label}",
        f"        Total Queries     : {fmt(t)}",
        f"         • < 50ms           : {fmt(d['fast_lt_50ms'])}  ({pct(d['fast_lt_50ms'], t)})",
        f"         • 50–100ms     : {fmt(d['slow_50_100ms'])}  ({pct(d['slow_50_100ms'], t)})",
        f"         • 100–200ms   : {fmt(d['slow_100_200ms'])}  ({pct(d['slow_100_200ms'], t)})",
        f"         • 200–500ms   : {fmt(d['slow_200_500ms'])}  ({pct(d['slow_200_500ms'], t)})",
        f"         • 500–1000ms : {fmt(d['slow_500_1000ms'])}   ({pct(d['slow_500_1000ms'], t)})",
        f"         • > 1000ms       : {fmt(d['gt_than_1000ms'])}   ({pct(d['gt_than_1000ms'], t)})",
    ])


# ── Main ──────────────────────────────────────────────────────────────────────

def main(start_date: str = None, end_date: str = None, dry_run: bool = False,
         output_dir: Path = None) -> dict:

    if not start_date or not end_date:
        start_date, end_date = get_week_range()

    print(f"[perf] {start_date} → {end_date}  admin=q{ADMIN_Q_ID}  portal=q{PORTAL_Q_ID}")

    session = requests.Session()
    if not dry_run:
        authenticate(session)

    splits = daily_splits(date.fromisoformat(start_date), date.fromisoformat(end_date))
    total_queries = len(splits) * 2
    print(f"[perf] {len(splits)} day(s) × 2 questions = {total_queries} queries (all parallel)")

    if dry_run:
        for i, (d_from, d_to) in enumerate(splits, 1):
            print(f"  [DRY RUN] admin-{i} {d_from}  portal-{i} {d_from}")
        print("[perf] [DRY RUN] done")
        return {"module": "performance", "status": "ok"}

    # Build task list: (label, question_id, d_from, d_to)
    tasks = []
    for i, (d_from, d_to) in enumerate(splits, 1):
        tasks.append((f"admin-{i}  {d_from}", ADMIN_Q_ID,  d_from, d_to))
        tasks.append((f"portal-{i} {d_from}", PORTAL_Q_ID, d_from, d_to))

    admin_totals  = zero_buckets()
    portal_totals = zero_buckets()
    completed = 0

    with ThreadPoolExecutor(max_workers=total_queries) as executor:
        futures = {
            executor.submit(
                run_question_day, session, qid, d_from, d_to, label
            ): label
            for label, qid, d_from, d_to in tasks
        }
        for future in as_completed(futures):
            label = futures[future]
            row = future.result()
            completed += 1
            print(f"  [perf] ✓ {label}  ({completed}/{total_queries})")
            if label.startswith("admin"):
                admin_totals  = add_row(admin_totals,  row)
            else:
                portal_totals = add_row(portal_totals, row)

    admin_block  = render_block("Community Admin",  admin_totals)
    portal_block = render_block("Community Portal", portal_totals)

    copy_paste = "\n".join([
        f"Slow Query Report [{start_date} – {end_date}]",
        "",
        admin_block,
        "",
        portal_block,
    ])

    md = "\n".join([
        f"# Performance Report: {start_date} to {end_date}",
        "",
        copy_paste,
        "",
        "---",
        "",
        "## Copy-paste block",
        "",
        "```",
        copy_paste,
        "```",
    ])

    if output_dir is None:
        output_dir = SCRIPT_DIR / "reports" / f"{start_date}_to_{end_date}"
    output_dir.mkdir(parents=True, exist_ok=True)

    md_file = output_dir / "perf_report.md"
    md_file.write_text(md)
    print(f"[perf] saved → {md_file}")

    return {
        "module": "performance",
        "status": "ok",
        "md": str(md_file),
        "admin": admin_totals,
        "portal": portal_totals,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Weekly performance metrics report")
    parser.add_argument("--start",   help="Start date YYYY-MM-DD")
    parser.add_argument("--end",     help="End date YYYY-MM-DD")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    main(start_date=args.start, end_date=args.end, dry_run=args.dry_run)
