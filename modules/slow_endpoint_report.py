#!/usr/bin/env python3
"""
Weekly slow-endpoint report — top 3 slowest endpoints by request-weighted latency.

Uses saved Metabase question 7304 ("slow-endpoint-communities"). Querying the
full week directly is slow (same problem as performance_report's admin/portal
questions), so this queries day-by-day in parallel, then combines: the
question already returns each day's slowest endpoints with their own
avg_worst_sql_ms + request_count, so we can't just sum latencies across days —
we recompute a request_count-weighted average per endpoint across all days
before picking the final top 3.

Usage:
    python3 slow_endpoint_report.py --from 2026-08-07 --to 2026-08-13
    python3 slow_endpoint_report.py          # auto: last Fri → last Thu
    python3 slow_endpoint_report.py --dry-run
"""

import argparse
import collections
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta
from pathlib import Path

# Allow running as `python3 modules/slow_endpoint_report.py` directly
_pkg_root = str(Path(__file__).parent.parent)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

import requests

from lib.metabase import authenticate, run_question
from lib.utils import ROOT, get_week_range

SLOW_ENDPOINT_Q_ID = int(os.environ.get("METABASE_QUESTION_ID_SLOW_ENDPOINT", "7304"))

QUERY_TIMEOUT = 300  # same class of question as admin/portal perf — can be slow on heavy days
TOP_N = 3


def daily_splits(start: date, end_inclusive: date) -> list[tuple[str, str]]:
    """(date_from, date_to) pairs — date_to = next day so SQL <= catches the full day."""
    splits, d = [], start
    while d <= end_inclusive:
        splits.append((str(d), str(d + timedelta(days=1))))
        d += timedelta(days=1)
    return splits


def display_endpoint(ep: str) -> str:
    """
    '/a/showPanelAPIRequestLog.do' -> '/showPanelAPIRequestLog.do'
    '/a/ajs/survey-angular.panel.ProfileCrossTabAJSHandler-GetCrosstabResults'
        -> '/getCrosstabResults'  (AJS handler: take method name after last '-', lowercase first letter)
    """
    ep = ep.replace("/a/ajs/", "").replace("/a/", "/")
    if not ep.endswith(".do") and "-" in ep:
        method = ep.rsplit("-", 1)[-1]
        ep = "/" + (method[0].lower() + method[1:] if method else method)
    return ep


def aggregate(daily_rows: list[list[dict]]) -> list[dict]:
    """Request-count-weighted average latency per endpoint, across all days it appeared in."""
    weighted_sum: dict[str, float] = collections.defaultdict(float)
    total_count: dict[str, int] = collections.defaultdict(int)

    for rows in daily_rows:
        for row in rows or []:
            ep = row.get("endpoint", "")
            if not ep:
                continue
            count = int(row.get("request_count", 0) or 0)
            avg_ms = float(row.get("avg_worst_sql_ms", 0) or 0)
            weighted_sum[ep] += avg_ms * count
            total_count[ep] += count

    combined = [
        {
            "endpoint": ep,
            "avg_latency_ms": (weighted_sum[ep] / total_count[ep]) if total_count[ep] else 0,
            "request_count": total_count[ep],
        }
        for ep in weighted_sum
    ]
    return sorted(combined, key=lambda r: -r["avg_latency_ms"])


def render_copy_paste(top: list[dict]) -> str:
    lines = ["Top 3 Slowest Queries"]
    for r in top[:TOP_N]:
        latency = int(round(r["avg_latency_ms"]))
        lines.append(f"         • {display_endpoint(r['endpoint'])} – Latency : {latency} ms")
    return "\n".join(lines)


def main(start_date: str = None, end_date: str = None, dry_run: bool = False,
         output_dir: Path = None) -> dict:

    if not start_date or not end_date:
        start_date, end_date = get_week_range()

    print(f"[slow-endpoint] {start_date} → {end_date}  question=q{SLOW_ENDPOINT_Q_ID}")

    splits = daily_splits(date.fromisoformat(start_date), date.fromisoformat(end_date))
    print(f"[slow-endpoint] {len(splits)} day(s) × 1 question = {len(splits)} queries (all parallel)")

    if dry_run:
        for i, (d_from, _) in enumerate(splits, 1):
            print(f"  [DRY RUN] day-{i} {d_from}")
        print("[slow-endpoint] [DRY RUN] done")
        return {"module": "slow_endpoint", "status": "ok"}

    session = requests.Session()
    authenticate(session)

    daily_rows: list[list[dict]] = []
    completed = 0
    with ThreadPoolExecutor(max_workers=len(splits)) as executor:
        futures = {
            executor.submit(
                run_question, session, SLOW_ENDPOINT_Q_ID, d_from, d_to, QUERY_TIMEOUT, f"day-{i}"
            ): f"day-{i} {d_from}"
            for i, (d_from, d_to) in enumerate(splits, 1)
        }
        for future in as_completed(futures):
            label = futures[future]
            result = future.result()
            completed += 1
            print(f"  [slow-endpoint] ✓ {label}  ({completed}/{len(splits)})")
            if result is None:
                continue
            daily_rows.append(result if isinstance(result, list) else [result])

    ranked = aggregate(daily_rows)
    top = ranked[:TOP_N]
    copy_paste = render_copy_paste(ranked)

    md_lines = [
        f"# Slow Endpoint Report: {start_date} to {end_date}",
        "",
        copy_paste,
        "",
        "---",
        "",
        "## full breakdown (all endpoints seen across the week's top daily slots)",
        "",
        "| endpoint | avg latency (ms) | total requests |",
        "|---|---|---|",
    ]
    for r in ranked:
        md_lines.append(
            f"| `{r['endpoint']}` | {int(round(r['avg_latency_ms']))} | {r['request_count']} |"
        )

    md_lines += [
        "",
        "---",
        "",
        "## Copy-paste block",
        "",
        "```",
        copy_paste,
        "```",
    ]

    if output_dir is None:
        output_dir = ROOT / "reports" / f"{start_date}_to_{end_date}"
    output_dir.mkdir(parents=True, exist_ok=True)

    md_file = output_dir / "slow_endpoint_report.md"
    md_file.write_text("\n".join(md_lines))
    print(f"[slow-endpoint] saved → {md_file}")

    return {
        "module": "slow_endpoint",
        "status": "ok",
        "md": str(md_file),
        "top": top,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Weekly slow-endpoint report (top 3 by latency)")
    parser.add_argument("--from",    dest="date_from", help="Start date YYYY-MM-DD")
    parser.add_argument("--to",      dest="date_to",   help="End date YYYY-MM-DD")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    main(start_date=args.date_from, end_date=args.date_to, dry_run=args.dry_run)
