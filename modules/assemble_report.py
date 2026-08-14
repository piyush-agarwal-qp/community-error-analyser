#!/usr/bin/env python3
"""
assemble_report.py — Combines all weekly report modules into weekly_report.md.

Reads from the week folder and produces the final copy-paste block.
Safe to run multiple times — overwrites weekly_report.md each time.
Run this after the error-report skill completes (to include error analysis).

Usage:
    python assemble_report.py --from 2026-06-19 --to 2026-06-25
"""

import argparse
import re
import sys
from datetime import date
from pathlib import Path

# Allow running as `python3 modules/assemble_report.py` directly
_pkg_root = str(Path(__file__).parent.parent)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from lib.utils import ROOT, get_week_range


# ── Parsers ───────────────────────────────────────────────────────────────────

def extract_copy_paste_block(md: str) -> str:
    """Extract content between the first ``` ``` block after '## Copy-paste block'."""
    section = md.split("## Copy-paste block", 1)
    if len(section) < 2:
        return ""
    after = section[1]
    m = re.search(r"```\n(.*?)```", after, re.DOTALL)
    return m.group(1).strip() if m else ""


def parse_radar(md: str) -> tuple[int, str]:
    """Returns (count, copy-paste block)."""
    count = 0
    m = re.search(r"\*\*Total:\*\* (\d+)", md)
    if m:
        count = int(m.group(1))
    block = extract_copy_paste_block(md)
    return count, block


def parse_error_pdm(md: str) -> dict:
    """
    Parse the PDM report section of error_report.md.
    Returns {us_panel, us_portal, eu_panel, eu_portal}.
    """
    result = {"us_panel": "?", "us_portal": "?", "eu_panel": "?", "eu_portal": "?"}
    # Look for "us dc — N panel, N portal"
    for line in md.splitlines():
        line_l = line.lower()
        m = re.search(r"(\d+)\s+panel.*?(\d+)\s+portal", line_l)
        if not m:
            continue
        if "us dc" in line_l or "us " in line_l and "eu" not in line_l and "qa" not in line_l:
            result["us_panel"] = m.group(1)
            result["us_portal"] = m.group(2)
        elif "eu dc" in line_l or "eu " in line_l and "qa" not in line_l:
            result["eu_panel"] = m.group(1)
            result["eu_portal"] = m.group(2)
    return result


def parse_perf_block(md: str) -> str:
    return extract_copy_paste_block(md)


def parse_metrics_block(md: str) -> str:
    return extract_copy_paste_block(md)


def parse_slow_endpoint_block(md: str) -> str:
    return extract_copy_paste_block(md)


def fmt_date_header(end_date: str) -> str:
    """'2026-06-25' → 'June 25'"""
    d = date.fromisoformat(end_date)
    return d.strftime("%B %-d")


# ── Assembler ─────────────────────────────────────────────────────────────────

def assemble(start: str, end: str, folder: Path) -> str:
    radar_file         = folder / "radar_report.md"
    error_file         = folder / "error_report.md"
    perf_file          = folder / "perf_report.md"
    metrics_file       = folder / "metrics_report.md"
    slow_endpoint_file = folder / "slow_endpoint_report.md"

    # ── Radar ─────────────────────────────────────────────────────────────────
    radar_count, radar_block = 0, ""
    if radar_file.exists():
        radar_count, radar_block = parse_radar(radar_file.read_text())
    else:
        print(f"  [assemble] radar_report.md missing — using defaults")

    # ── 500 errors PDM ────────────────────────────────────────────────────────
    error_pdm = {"us_panel": "NA", "us_portal": "NA", "eu_panel": "NA", "eu_portal": "NA"}
    error_available = False
    if error_file.exists():
        error_pdm = parse_error_pdm(error_file.read_text())
        error_available = True
    else:
        print(f"  [assemble] error_report.md missing — run error-report skill first")

    # ── Performance ───────────────────────────────────────────────────────────
    perf_block = ""
    if perf_file.exists():
        perf_block = parse_perf_block(perf_file.read_text())
    else:
        print(f"  [assemble] perf_report.md missing — performance pending")

    # ── Slow endpoint ─────────────────────────────────────────────────────────
    slow_endpoint_block = ""
    if slow_endpoint_file.exists():
        slow_endpoint_block = parse_slow_endpoint_block(slow_endpoint_file.read_text())
    else:
        print(f"  [assemble] slow_endpoint_report.md missing — slow-endpoint pending")

    # ── Metrics ───────────────────────────────────────────────────────────────
    metrics_block = ""
    if metrics_file.exists():
        metrics_block = parse_metrics_block(metrics_file.read_text())
    else:
        print(f"  [assemble] metrics_report.md missing")

    # ── Build combined block ──────────────────────────────────────────────────
    header_date = fmt_date_header(end)

    lines = [
        f"Updates {header_date}",
        "Enhancement:",
        "",
        "• [paste from sprint board]",
        "",
        "500 Error:",
        " Admin -",
        "",
    ]

    if error_available:
        lines.append(f"• Admin — {error_pdm['us_panel']} Panel (US), {error_pdm['eu_panel']} Panel (EU).")
    else:
        lines.append("• NA.")

    lines += [
        "",
        " Portal -",
        "",
    ]

    if error_available:
        lines.append(f"• Portal — {error_pdm['us_portal']} Portal (US), {error_pdm['eu_portal']} Portal (EU).")
    else:
        lines.append("• NA.")

    lines += [
        "",
        "Bugs:",
        "",
        "• [paste from sprint board]",
        "",
        "UX:",
        "",
        "• [paste from sprint board]",
        "",
        "Performance",
        "",
        "• [paste from sprint board]",
        "",
        "Test & Coverage:",
        "",
        "• [paste iron test coverage here]",
        "",
        "---",
        "",
    ]

    # Radar section
    if radar_block:
        lines += [radar_block, ""]
    else:
        lines += [f"Radar tickets : {radar_count}", ""]

    # 500 Errors Logged
    if error_available:
        lines += [
            "500 Errors Logged :",
            "",
            f"• US DC - {error_pdm['us_panel']} Panel {error_pdm['us_portal']} Portal.",
            f"• EU DC - {error_pdm['eu_panel']} Panel {error_pdm['eu_portal']} Portal.",
            "",
        ]
    else:
        lines += [
            "500 Errors Logged :",
            "",
            "• [run error-report skill to populate]",
            "",
        ]

    # Slow Query
    if perf_block:
        lines += [perf_block, ""]
    else:
        lines += [
            f"Slow Query Report [{start} – {end}]",
            "",
            "• [performance report pending]",
            "",
        ]

    # Top 3 Slowest Queries
    if slow_endpoint_block:
        lines += [slow_endpoint_block, ""]
    else:
        lines += ["Top 3 Slowest Queries", "", "• [slow-endpoint report pending]", ""]

    # Metrics Sheet
    lines += ["Metrics Sheet", ""]
    if metrics_block:
        lines += [metrics_block, ""]
    else:
        lines += ["• [metrics report pending]", ""]

    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

def main(start: str = None, end: str = None) -> Path:
    if not start or not end:
        start, end = get_week_range()

    folder = ROOT / "reports" / f"{start}_to_{end}"
    if not folder.exists():
        print(f"ERROR: {folder} does not exist — run run_all.py first")
        return None

    print(f"[assemble] {start} → {end}")
    content = assemble(start, end, folder)

    out = folder / "weekly_report.md"
    out.write_text(content)
    print(f"[assemble] saved → {out}")
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Assemble weekly_report.md from module outputs")
    parser.add_argument("--from", dest="date_from", help="Start date YYYY-MM-DD")
    parser.add_argument("--to",   dest="date_to",   help="End date YYYY-MM-DD")
    args = parser.parse_args()
    main(start=args.date_from, end=args.date_to)
