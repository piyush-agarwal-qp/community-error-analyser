#!/usr/bin/env python3
"""
Weekly radar tickets report.

Fetches radar tickets from Metabase, generates a brief from body_text,
and writes a markdown report.

Usage:
    python3 radar_report.py --from 2026-06-19 --to 2026-06-25
    python3 radar_report.py          # auto: last Fri → last Thu
    python3 radar_report.py --dry-run
"""

import argparse
import os
import re
import sys
from pathlib import Path

# Allow running as `python3 modules/radar_report.py` directly
_pkg_root = str(Path(__file__).parent.parent)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

import requests

from lib.metabase import authenticate, run_question
from lib.utils import ROOT, get_week_range

QUESTION_ID = int(os.environ.get("METABASE_QUESTION_ID_RADAR", "7302"))
BRIEF_CHARS = 300


def make_brief(body_text: str) -> str:
    """First 2-3 sentences of body_text stripped of HTML, max BRIEF_CHARS."""
    if not body_text:
        return ""
    text = re.sub(r"<[^>]+>", " ", body_text)
    text = re.sub(r"\s+", " ", text).strip()
    sentences = re.split(r"(?<=[.!?])\s+", text)
    brief = ""
    for s in sentences[:3]:
        if len(brief) + len(s) > BRIEF_CHARS:
            break
        brief = (brief + " " + s).strip()
    return brief or text[:BRIEF_CHARS]


def render_md(start: str, end: str, tickets: list[dict]) -> str:
    count = len(tickets)
    lines = [
        f"# Radar Tickets: {start} to {end}",
        "",
        f"**Total:** {count}",
        "",
    ]

    if not tickets:
        lines.append("_No radar tickets for this period._")
        return "\n".join(lines)

    lines += ["---", ""]

    for t in tickets:
        brief = make_brief(t.get("body_text") or "")
        lines += [
            f"### #{t.get('id', '?')} — {t.get('subject') or '_(no subject)_'}",
            "",
            f"**DC:** {t.get('warehouse') or '?'}",
            "",
            f"**Brief:** {brief}",
            "",
            "---",
            "",
        ]

    lines += [
        "## Copy-paste block",
        "",
        "```",
        f"Radar tickets : {count}",
    ]
    for t in tickets:
        lines.append(f"• #{t.get('id', '?')} — {t.get('subject', '')[:80]}")
    lines.append("```")

    return "\n".join(lines)


def main(start_date: str = None, end_date: str = None, dry_run: bool = False,
         output_dir: Path = None) -> dict:

    if not start_date or not end_date:
        start_date, end_date = get_week_range()

    print(f"[radar] {start_date} → {end_date}  question={QUESTION_ID}")

    if dry_run:
        print(f"[radar] [DRY RUN] would fetch question {QUESTION_ID}")
        return {"module": "radar", "status": "ok", "count": 0}

    session = requests.Session()
    authenticate(session)

    result = run_question(session, QUESTION_ID, date_from=start_date, date_to=end_date)
    tickets = result if isinstance(result, list) else ([result] if result else [])
    print(f"[radar] {len(tickets)} ticket(s) found")

    md = render_md(start_date, end_date, tickets)

    if output_dir is None:
        output_dir = ROOT / "reports" / f"{start_date}_to_{end_date}"
    output_dir.mkdir(parents=True, exist_ok=True)

    md_file = output_dir / "radar_report.md"
    md_file.write_text(md)
    print(f"[radar] saved → {md_file}")

    return {"module": "radar", "status": "ok", "count": len(tickets), "md": str(md_file)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Weekly radar tickets report")
    parser.add_argument("--from",    dest="date_from", help="Start date YYYY-MM-DD")
    parser.add_argument("--to",      dest="date_to",   help="End date YYYY-MM-DD")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    main(start_date=args.date_from, end_date=args.date_to, dry_run=args.dry_run)
