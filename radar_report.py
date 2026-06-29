#!/usr/bin/env python3
"""
Weekly Communities radar tickets report.

Fetches radar tickets from Metabase question 7302, extracts key fields,
generates a brief from body_text, and writes a markdown report.

Usage:
    python radar_report.py --start 2026-06-19 --end 2026-06-25
    python radar_report.py                     # auto: last Fri → last Thu
    python radar_report.py --dry-run
"""

import argparse
import os
import re
import sys
from datetime import date, timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).parent
load_dotenv(SCRIPT_DIR / ".env")

METABASE_URL = os.environ.get("METABASE_URL", "https://metabase.questionpro.net").rstrip("/")
SESSION_TOKEN = os.environ.get("METABASE_SESSION_TOKEN", "")
QUESTION_ID = int(os.environ.get("METABASE_QUESTION_ID_RADAR", "7302"))

BRIEF_CHARS = 300


def get_week_range() -> tuple[str, str]:
    today = date.today()
    days_back = (today.weekday() - 3) % 7 or 7
    last_thursday = today - timedelta(days=days_back)
    last_friday = last_thursday - timedelta(days=6)
    return str(last_friday), str(last_thursday)


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


def fetch_tickets(session: requests.Session, question_id: int,
                  start: str, end: str) -> list[dict]:
    body = {
        "parameters": [
            {
                "type": "date/single",
                "target": ["variable", ["template-tag", "date_from"]],
                "value": start,
            },
            {
                "type": "date/single",
                "target": ["variable", ["template-tag", "date_to"]],
                "value": end,
            },
        ]
    }
    resp = session.post(
        f"{METABASE_URL}/api/card/{question_id}/query",
        json=body, timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()["data"]
    cols = [c["name"] for c in data["cols"]]
    return [dict(zip(cols, row)) for row in data["rows"]]


def make_brief(body_text: str) -> str:
    """Extract first 2-3 sentences from body_text, max BRIEF_CHARS."""
    if not body_text:
        return ""
    # Strip HTML tags
    text = re.sub(r"<[^>]+>", " ", body_text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    # Split on sentence boundaries
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
        ticket_id = t.get("id", "?")
        subject   = t.get("subject") or "_(no subject)_"
        body_text = t.get("body_text") or ""
        dc        = t.get("warehouse") or "?"
        brief     = make_brief(body_text)

        lines += [
            f"### #{ticket_id} — {subject}",
            "",
            f"**DC:** {dc}",
            "",
            f"**Brief:** {brief}",
            "",
            "---",
            "",
        ]

    # Copy-paste block for weekly summary
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

    tickets = fetch_tickets(session, QUESTION_ID, start_date, end_date)
    print(f"[radar] {len(tickets)} ticket(s) found")

    md = render_md(start_date, end_date, tickets)

    if output_dir is None:
        output_dir = SCRIPT_DIR / "reports" / f"{start_date}_to_{end_date}"
    output_dir.mkdir(parents=True, exist_ok=True)

    md_file = output_dir / "radar_report.md"
    md_file.write_text(md)
    print(f"[radar] saved → {md_file}")

    return {
        "module": "radar",
        "status": "ok",
        "count": len(tickets),
        "md": str(md_file),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Weekly radar tickets report")
    parser.add_argument("--start",   help="Start date YYYY-MM-DD")
    parser.add_argument("--end",     help="End date YYYY-MM-DD")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    main(start_date=args.start, end_date=args.end, dry_run=args.dry_run)
