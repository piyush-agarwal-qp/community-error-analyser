"""
fetcher.py — Metabase error fetcher for Claude Code
----------------------------------------------------
Connects to Metabase, pulls condensed error rows, and prints them as JSON
to stdout. Claude Code reads that output and does the analysis.

No Anthropic API key needed — Claude Code's own session handles the AI part.

Usage (Claude Code calls this automatically via CLAUDE.md):
    python fetcher.py --days 7
    python fetcher.py --from 2026-05-29 --to 2026-06-04
    python fetcher.py --days 7 --question-id 112
    python fetcher.py --from 2026-05-29 --to 2026-06-04 --input errors.json

Output: JSON to stdout, progress/errors to stderr (so they don't mix).
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone

import requests
from dotenv import load_dotenv

load_dotenv()

# ── Constants ──────────────────────────────────────────────────────────────────

STACKTRACE_CHARS = 8000
EXTRA_INFO_CHARS = 2000


# ── Helpers ────────────────────────────────────────────────────────────────────

def _env(key: str, default: str = "") -> str:
    return os.getenv(key, default)

def _err(msg: str) -> None:
    """Print to stderr so it doesn't pollute the JSON stdout."""
    print(f"[fetcher] {msg}", file=sys.stderr)

def _die(msg: str) -> None:
    _err(f"ERROR: {msg}")
    sys.exit(1)


# ── Metabase client ────────────────────────────────────────────────────────────

class MetabaseClient:
    def __init__(self, base_url: str, api_key: str = "", session: str = "",
                 username: str = "", password: str = ""):
        self.base_url = base_url.rstrip("/")
        self.api_key  = api_key
        self.token    = session

        if api_key:
            _err("Auth: API key")
            r = requests.get(f"{self.base_url}/api/user/current",
                             headers=self._h(), timeout=15)
            r.raise_for_status()
            _err(f"Connected as {r.json().get('common_name', '?')} (API key)")

        elif session:
            _err("Auth: session token")
            r = requests.get(f"{self.base_url}/api/user/current",
                             headers=self._h(), timeout=15)
            r.raise_for_status()
            _err(f"Connected as {r.json().get('common_name', '?')} (session)")

        elif username and password:
            _err("Auth: username/password")
            resp = requests.post(f"{self.base_url}/api/session",
                                 json={"username": username, "password": password},
                                 timeout=15)
            resp.raise_for_status()
            self.token = resp.json()["id"]
            _err("Connected (password)")

        else:
            _die(
                "No Metabase auth in .env.\n"
                "  Set METABASE_SESSION (browser cookie)  — recommended for Google SSO\n"
                "  Set METABASE_API_KEY                   — if on Metabase >= v0.47\n"
                "  Set METABASE_USER + METABASE_PASS      — for password login"
            )

    def _h(self) -> dict:
        if self.api_key:
            return {"x-api-key": self.api_key}
        return {"X-Metabase-Session": self.token}

    def list_databases(self) -> list[dict]:
        r = requests.get(f"{self.base_url}/api/database",
                         headers=self._h(), timeout=15)
        r.raise_for_status()
        return r.json().get("data", r.json())

    def run_sql(self, database_id: int, sql: str) -> list[dict]:
        r = requests.post(
            f"{self.base_url}/api/dataset",
            json={"type": "native", "native": {"query": sql}, "database": database_id},
            headers=self._h(), timeout=60,
        )
        r.raise_for_status()
        data = r.json()["data"]
        cols = [c["name"] for c in data["cols"]]
        return [dict(zip(cols, row)) for row in data["rows"]]

    def run_question(self, question_id: int, date_from: str = "",
                     date_to: str = "") -> list[dict]:
        body: dict = {}
        if date_from or date_to:
            # IMPORTANT: template-tag names ("date_from", "date_to") must match
            # the variable names defined in the saved Metabase question exactly.
            # If the question uses different names, dates are silently ignored
            # and the query returns unfiltered or wrong-date data.
            # Verify in Metabase: question → edit → variables panel.
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
        r = requests.post(
            f"{self.base_url}/api/card/{question_id}/query",
            json=body, headers=self._h(), timeout=60,
        )
        r.raise_for_status()
        data = r.json()["data"]
        cols = [c["name"] for c in data["cols"]]
        return [dict(zip(cols, row)) for row in data["rows"]]


# ── SQL query ──────────────────────────────────────────────────────────────────

def _build_sql(date_from: str, date_to: str, limit: int) -> str:
    excluded = "', '".join(["cmlabs1", "cmlabs2", "cmlabs"])
    return f"""
SELECT
    id,
    action,
    ts,
    hostname,
    hash_code,
    class_id,
    SUBSTRING(additional_info_json, 1, {EXTRA_INFO_CHARS}) AS additional_info_json,
    SUBSTRING(stacktrace, 1, {STACKTRACE_CHARS})           AS stacktrace
FROM error
WHERE active_product = 'Communities'
  AND hostname NOT IN ('{excluded}')
  AND ts >= '{date_from} 00:00:00'
  AND ts <= '{date_to} 23:59:59'
  AND stacktrace NOT LIKE '%Javascript Error%'
  AND hash_code != 0
ORDER BY ts ASC
LIMIT {limit}
""".strip()


# ── Row condenser ──────────────────────────────────────────────────────────────

def _condense(row: dict) -> dict:
    """Strip each row to the minimum fields Claude needs — keeps token count low."""
    st   = (row.get("stacktrace") or "")[:STACKTRACE_CHARS]
    info = (row.get("additional_info_json") or "")[:EXTRA_INFO_CHARS]

    url = ""
    try:
        # additional_info_json is truncated at EXTRA_INFO_CHARS — attempt a
        # targeted regex extraction instead of trying to repair broken JSON,
        # which fails silently whenever the cut lands mid-string.
        m = re.search(r'"url"\s*:\s*"([^"]*)"', info)
        if m:
            url = m.group(1)
    except Exception:
        pass

    return {
        "id":     row.get("id"),
        "ts":     str(row.get("ts", "")),
        "host":   row.get("hostname", ""),
        "hash":   row.get("hash_code", ""),
        "module": row.get("module") or row.get("class_id") or "",
        "url":    url,
        "st":     st,
    }


# ── Auth builder ───────────────────────────────────────────────────────────────

def _build_client() -> MetabaseClient:
    url     = _env("METABASE_URL").rstrip("/")
    api_key = _env("METABASE_API_KEY")
    session = _env("METABASE_SESSION_TOKEN") or _env("METABASE_SESSION")
    user    = _env("METABASE_USER")
    pw      = _env("METABASE_PASS")

    if not url:
        _die("METABASE_URL not set in .env")

    return MetabaseClient(url, api_key=api_key, session=session,
                          username=user, password=pw)


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(
        description="Fetch Metabase errors and print condensed JSON to stdout.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python fetcher.py --days 7
  python fetcher.py --from 2026-05-29 --to 2026-06-04
  python fetcher.py --days 7 --question-id 112
  python fetcher.py --input errors.json --from 2026-05-29 --to 2026-06-04
""",
    )
    p.add_argument("--days",        type=int, default=7,   help="Past N days (default 7)")
    p.add_argument("--from",        dest="date_from",      help="Start date YYYY-MM-DD")
    p.add_argument("--to",          dest="date_to",        help="End date YYYY-MM-DD")
    p.add_argument("--limit",       type=int, default=500, help="Max rows (default 500)")
    p.add_argument("--question-id", type=int, default=0,   help="Saved Metabase question ID")
    p.add_argument("--db-id",       type=int, default=0,   help="Metabase database ID")
    p.add_argument("--input",                              help="Local JSON file — skips Metabase")
    p.add_argument("--output",                             help="Save JSON to file instead of stdout")
    args = p.parse_args()

    # Resolve dates
    today     = datetime.now(tz=timezone.utc).date()
    date_to   = args.date_to   or str(today)
    date_from = args.date_from or str(today - timedelta(days=args.days - 1))

    _err(f"Date range: {date_from} → {date_to}")

    rows: list[dict] = []

    # ── Source: local file ─────────────────────────────────────────────────────
    if args.input:
        _err(f"Reading from {args.input}")
        with open(args.input) as f:
            rows = json.load(f)
        if not isinstance(rows, list):
            rows = [rows]
        rows = [r for r in rows
                if date_from <= str(r.get("ts", ""))[:10] <= date_to]
        rows = rows[:args.limit]
        _err(f"Loaded {len(rows)} rows from file")

    # ── Source: Metabase ───────────────────────────────────────────────────────
    else:
        mb = _build_client()

        question_id = args.question_id or int(_env("METABASE_QUESTION_ID", "0"))

        if question_id:
            _err(f"Running saved question {question_id}")
            rows = mb.run_question(question_id, date_from=date_from, date_to=date_to)
            # Client-side date safety net
            rows = [r for r in rows
                    if date_from <= str(r.get("ts", ""))[:10] <= date_to]
            rows = rows[:args.limit]

        else:
            db_id = args.db_id or int(_env("METABASE_DB_ID", "0"))
            if not db_id:
                dbs = mb.list_databases()
                _err("Available databases:")
                for d in dbs:
                    _err(f"  [{d['id']}] {d['name']}")
                _die("Set METABASE_DB_ID in .env or pass --db-id")
            _err(f"Running SQL on database {db_id}")
            rows = mb.run_sql(db_id, _build_sql(date_from, date_to, args.limit))

        _err(f"Fetched {len(rows)} rows")

    if not rows:
        _err("No rows found for date range — nothing to analyse")
        # Still emit valid JSON so Claude Code gets a clear signal
        print(json.dumps({
            "date_from": date_from,
            "date_to": date_to,
            "count": 0,
            "rows": [],
        }))
        return

    # Condense and emit
    condensed = [_condense(r) for r in rows]
    output = {
        "date_from": date_from,
        "date_to":   date_to,
        "count":     len(condensed),
        "rows":      condensed,
    }
    if args.output:
        import pathlib
        pathlib.Path(args.output).write_text(json.dumps(output))
        _err(f"Done — {len(condensed)} condensed rows written to {args.output}")
    else:
        print(json.dumps(output))   # stdout — Claude Code reads this
        _err(f"Done — {len(condensed)} condensed rows written to stdout")


if __name__ == "__main__":
    main()
