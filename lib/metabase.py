"""Shared Metabase client utilities — auth, question runner."""

import os
import sys
import time

import requests

from lib.utils import ROOT

METABASE_URL = os.environ.get("METABASE_URL", "https://metabase.questionpro.net").rstrip("/")
SESSION_TOKEN = (
    os.environ.get("METABASE_SESSION_TOKEN", "")
    or os.environ.get("METABASE_SESSION", "")
)

MAX_RETRIES = 3
RETRY_BACKOFF = 2


def authenticate(session: requests.Session) -> None:
    """Attach session token and verify it's still valid. Exits on failure."""
    if not SESSION_TOKEN:
        print(
            "ERROR: METABASE_SESSION_TOKEN not set in .env\n"
            "  Re-copy: browser → F12 → Application → Cookies → metabase.SESSION\n"
            "  Paste as METABASE_SESSION_TOKEN in .env",
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


def run_question(
    session: requests.Session,
    question_id: int,
    date_from: str = "",
    date_to: str = "",
    timeout: int = 60,
    label: str = "",
) -> list[dict] | dict | None:
    """
    POST /api/card/{id}/query with optional date_from / date_to template tags.

    Returns a list of row dicts for multi-row questions, or a single row dict
    for aggregate (single-row) questions. Returns None on failure after retries.
    """
    body: dict = {}
    if date_from or date_to:
        body["parameters"] = []
        if date_from:
            body["parameters"].append({
                "type": "date/single",
                "target": ["variable", ["template-tag", "date_from"]],
                "value": date_from,
            })
        if date_to:
            body["parameters"].append({
                "type": "date/single",
                "target": ["variable", ["template-tag", "date_to"]],
                "value": date_to,
            })

    tag = f" ({label})" if label else ""

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = session.post(
                f"{METABASE_URL}/api/card/{question_id}/query",
                json=body,
                timeout=timeout,
            )
            resp.raise_for_status()
            data = resp.json()
            if data.get("status") == "failed":
                print(f"  Query failed{tag}: {data.get('error', '?')}", file=sys.stderr)
                return None
            cols = [c["name"] for c in data["data"]["cols"]]
            rows = [dict(zip(cols, row)) for row in data["data"]["rows"]]
            # Single-row aggregate questions return the row dict directly
            return rows[0] if len(rows) == 1 else rows
        except requests.RequestException as exc:
            if attempt == MAX_RETRIES:
                print(f"  HTTP error{tag} after {MAX_RETRIES} attempts: {exc}", file=sys.stderr)
                return None
            wait = RETRY_BACKOFF * attempt
            print(f"  Attempt {attempt} failed{tag}, retrying in {wait}s...")
            time.sleep(wait)

    return None
