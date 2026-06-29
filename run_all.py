#!/usr/bin/env python3
"""
run_all.py — Communities weekly report orchestrator.

Runs all report modules in parallel via concurrent.futures, then assembles
a combined weekly_report.md. Each module can itself spawn internal threads.

Usage:
    python3 run_all.py --from 2026-06-19 --to 2026-06-25
    python3 run_all.py --dry-run
"""

import argparse
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent


def get_week_range() -> tuple[str, str]:
    today = date.today()
    days_back = (today.weekday() - 3) % 7 or 7
    last_thursday = today - timedelta(days=days_back)
    last_friday = last_thursday - timedelta(days=6)
    return str(last_friday), str(last_thursday)


def run_metrics(start: str, end: str, output_dir: Path, dry_run: bool) -> dict:
    from metabase_report import main as metrics_main
    from pathlib import Path as _Path
    print("[metrics] starting...")
    result = metrics_main(
        start_date=start,
        end_date=end,
        dry_run=dry_run,
        output_dir=output_dir,
    )
    print("[metrics] done")
    return {"module": "metrics", "status": "ok", **result}


def run_errors(start: str, end: str, output_dir: Path, dry_run: bool) -> dict:
    """Fetch 500 errors then run automated analysis (cluster, classify, generate report)."""
    import subprocess as _subprocess
    from error_report import main as error_main

    raw_dir = output_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    combined_out = raw_dir / "errors_combined.json"

    if dry_run:
        print(f"[errors] [DRY RUN] would fetch + analyse → {combined_out}")
        return {"module": "errors", "status": "ok"}

    # Step 1: fetch
    print(f"[errors] fetching...")
    r = _subprocess.run(
        ["python3", "fetcher.py", "--from", start, "--to", end,
         "--output", str(combined_out)],
        capture_output=True, text=True,
        cwd=str(SCRIPT_DIR),
    )
    if r.returncode != 0:
        print(f"[errors] fetch failed:\n{r.stderr}", file=sys.stderr)
        return {"module": "errors", "status": "error", "error": r.stderr.strip()}

    for line in r.stderr.splitlines():
        if line.strip():
            print(f"[errors] {line}")

    # Step 2: analyse
    print(f"[errors] analysing...")
    result = error_main(
        start_date=start,
        end_date=end,
        input_file=str(combined_out),
        output_dir=output_dir,
    )
    return result


def run_radar(start: str, end: str, output_dir: Path, dry_run: bool) -> dict:
    from radar_report import main as radar_main
    print("[radar] starting...")
    result = radar_main(start_date=start, end_date=end, dry_run=dry_run, output_dir=output_dir)
    print("[radar] done")
    return result


def run_performance(start: str, end: str, output_dir: Path, dry_run: bool) -> dict:
    from performance_report import main as perf_main
    print("[performance] starting...")
    result = perf_main(start_date=start, end_date=end, dry_run=dry_run, output_dir=output_dir)
    print("[performance] done")
    return result


MODULES = [
    ("metrics",     run_metrics),
    ("errors",      run_errors),
    ("radar",       run_radar),
    ("performance", run_performance),
]




def main() -> None:
    parser = argparse.ArgumentParser(description="Run all Communities weekly reports in parallel")
    parser.add_argument("--from", dest="date_from", help="Start date YYYY-MM-DD")
    parser.add_argument("--to",   dest="date_to",   help="End date YYYY-MM-DD")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    start, end = (args.date_from, args.date_to) if args.date_from and args.date_to else get_week_range()

    output_dir = SCRIPT_DIR / "reports" / f"{start}_to_{end}"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Communities weekly reports: {start} → {end}")
    print(f"Output: {output_dir}")
    print()

    results = []
    futures = {}

    with ThreadPoolExecutor(max_workers=len(MODULES)) as executor:
        for name, fn in MODULES:
            future = executor.submit(fn, start, end, output_dir, args.dry_run)
            futures[future] = name

        for future in as_completed(futures):
            name = futures[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as exc:
                print(f"[{name}] ERROR: {exc}", file=sys.stderr)
                results.append({"module": name, "status": "error", "error": str(exc)})

    print()
    from assemble_report import main as assemble_main
    weekly_file = assemble_main(start=start, end=end)
    print(f"Weekly report → {weekly_file}")
    print()

    # Summary
    print("── Results ──────────────────────────")
    for r in results:
        icon = "✓" if r.get("status") == "ok" else "·" if r.get("status") in ("pending", "fetched") else "✗"
        print(f"  {icon} {r.get('module', '?'):12} {r.get('status', '?')}")
    print()


if __name__ == "__main__":
    main()
