#!/usr/bin/env python3
"""
run_all.py — Communities weekly report orchestrator.

Runs all report modules in parallel via concurrent.futures, then assembles
the combined weekly_report.md.

Usage:
    python3 run_all.py --from 2026-06-19 --to 2026-06-25
    python3 run_all.py          # auto: last Fri → last Thu
    python3 run_all.py --dry-run
"""

import argparse
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from lib.utils import ROOT, get_week_range


def run_metrics(start: str, end: str, output_dir: Path, dry_run: bool) -> dict:
    from modules.metabase_report import main as metrics_main
    print("[metrics] starting...")
    result = metrics_main(start_date=start, end_date=end, dry_run=dry_run, output_dir=output_dir)
    print("[metrics] done")
    return {"module": "metrics", "status": "ok", **result}


def run_errors(start: str, end: str, output_dir: Path, dry_run: bool) -> dict:
    """Fetch US + EU 500 errors in parallel, merge, then run automated analysis."""
    import json
    import os
    import subprocess
    from modules.error_report import main as error_main

    raw_dir = output_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    us_out       = raw_dir / "us_errors.json"
    eu_out       = raw_dir / "eu_errors.json"
    combined_out = raw_dir / "errors_combined.json"

    us_qid = os.environ.get("METABASE_QUESTION_ID_US", "7162")
    eu_qid = os.environ.get("METABASE_QUESTION_ID_EU", "7163")

    if dry_run:
        print(f"[errors] [DRY RUN] would fetch US q{us_qid} + EU q{eu_qid} → {combined_out}")
        return {"module": "errors", "status": "ok"}

    def fetch(label: str, qid: str, out: Path) -> bool:
        print(f"[errors] fetching {label} (q{qid})...")
        r = subprocess.run(
            ["python3", "modules/fetcher.py",
             "--from", start, "--to", end,
             "--question-id", qid,
             "--output", str(out)],
            capture_output=True, text=True, cwd=str(ROOT),
        )
        for line in r.stderr.splitlines():
            if line.strip():
                print(f"[errors:{label}] {line}")
        if r.returncode != 0:
            print(f"[errors] {label} fetch failed", file=sys.stderr)
            return False
        return True

    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=2) as ex:
        us_ok = ex.submit(fetch, "US", us_qid, us_out)
        eu_ok = ex.submit(fetch, "EU", eu_qid, eu_out)
        us_ok, eu_ok = us_ok.result(), eu_ok.result()

    if not us_ok and not eu_ok:
        return {"module": "errors", "status": "error", "error": "both US and EU fetches failed"}

    # Merge rows from whichever fetches succeeded
    all_rows = []
    for path in (us_out, eu_out):
        if path.exists():
            try:
                data = json.loads(path.read_text())
                all_rows.extend(data.get("rows", []))
            except Exception:
                pass

    combined = {"date_from": start, "date_to": end, "count": len(all_rows), "rows": all_rows}
    combined_out.write_text(json.dumps(combined))
    print(f"[errors] combined {len(all_rows)} rows → {combined_out}")

    print("[errors] analysing...")
    return error_main(start_date=start, end_date=end, input_file=str(combined_out), output_dir=output_dir)


def run_radar(start: str, end: str, output_dir: Path, dry_run: bool) -> dict:
    from modules.radar_report import main as radar_main
    print("[radar] starting...")
    result = radar_main(start_date=start, end_date=end, dry_run=dry_run, output_dir=output_dir)
    print("[radar] done")
    return result


def run_performance(start: str, end: str, output_dir: Path, dry_run: bool) -> dict:
    from modules.performance_report import main as perf_main
    print("[performance] starting...")
    result = perf_main(start_date=start, end_date=end, dry_run=dry_run, output_dir=output_dir)
    print("[performance] done")
    return result


def run_slow_endpoint(start: str, end: str, output_dir: Path, dry_run: bool) -> dict:
    from modules.slow_endpoint_report import main as slow_endpoint_main
    print("[slow-endpoint] starting...")
    result = slow_endpoint_main(start_date=start, end_date=end, dry_run=dry_run, output_dir=output_dir)
    print("[slow-endpoint] done")
    return result


MODULES = [
    ("metrics",       run_metrics),
    ("errors",        run_errors),
    ("radar",         run_radar),
    ("performance",   run_performance),
    ("slow_endpoint", run_slow_endpoint),
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run all Communities weekly reports in parallel")
    parser.add_argument("--from",    dest="date_from", help="Start date YYYY-MM-DD")
    parser.add_argument("--to",      dest="date_to",   help="End date YYYY-MM-DD")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    start, end = (args.date_from, args.date_to) if args.date_from and args.date_to else get_week_range()

    output_dir = ROOT / "reports" / f"{start}_to_{end}"
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
                results.append(future.result())
            except Exception as exc:
                print(f"[{name}] ERROR: {exc}", file=sys.stderr)
                results.append({"module": name, "status": "error", "error": str(exc)})

    print()
    from modules.assemble_report import main as assemble_main
    weekly_file = assemble_main(start=start, end=end)
    print(f"Weekly report → {weekly_file}")
    print()

    print("── Results ──────────────────────────")
    for r in sorted(results, key=lambda x: x.get("module", "")):
        icon = "✓" if r.get("status") == "ok" else "·" if r.get("status") in ("pending", "fetched") else "✗"
        print(f"  {icon} {r.get('module', '?'):12} {r.get('status', '?')}")
    print()


if __name__ == "__main__":
    main()
