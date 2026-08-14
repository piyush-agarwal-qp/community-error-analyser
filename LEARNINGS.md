# Learnings — Weekly Report Generation

Append-only log. Every session that runs the weekly report, add an entry
here for anything that made generation harder than it should've been, or
any accuracy gap found. Goal: fine-tune the process/scripts week over week.

**Format per entry:** date, what happened, root cause, fix/action taken (or
recommended change if not yet applied).

---

## 2026-08-14 — first run in fresh environment

- **No venv existed, deps not installed.** `ModuleNotFoundError: No module
  named 'dotenv'` on first `run_all.py` call. Root cause: fresh checkout,
  no `.venv/`, system Python is externally-managed (PEP 668) so `pip
  install` needs a venv, not `--break-system-packages`.
  **Action:** created `.venv/`, ran `pip install -r requirements.txt`.
  **Recommend:** document venv setup as an explicit first-time step in
  CLAUDE.md/README (`python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`).

- **`run_all.py` spawns `modules/fetcher.py` via hardcoded `["python3", ...]`
  subprocess** (run_all.py:53) instead of `sys.executable`. This resolves
  `python3` from `$PATH` at call time, not from whichever interpreter is
  running `run_all.py`. Result: even after creating `.venv` and running
  `run_all.py` with `.venv/bin/python`, the fetcher subprocess still hit
  bare system `python3` and failed on `dotenv` — while radar/metrics/perf
  (in-process, not subprocessed) worked fine.
  **Action (this session):** ran with `PATH="$(pwd)/.venv/bin:$PATH"`
  prefixed so the bare `python3` lookup resolves inside the venv, without
  editing the script (user preference — see below).
  **User feedback:** user pushed back on changing `subprocess.run(["python3", ...])`
  to `sys.executable`, since it "was working earlier correctly with python3"
  — earlier runs likely had the venv activated (or deps installed globally)
  so plain `python3` on PATH already resolved correctly. Don't change this
  call; **always activate the venv (`source .venv/bin/activate`) or prefix
  PATH before running `run_all.py`**, rather than editing run_all.py.

- **Metabase session token expired mid-session** and user re-pasted a new
  `METABASE_SESSION_TOKEN` into `.env`. Note: `.env` has both a
  `METABASE_SESSION` (unused legacy/example var) and `METABASE_SESSION_TOKEN`
  (actually read by `lib/metabase.py`) — easy to update the wrong one.
  **Recommend:** if re-auth is ever needed again, confirm the var name is
  `METABASE_SESSION_TOKEN` specifically before editing.

- **Transient DNS/network failure**: `metabase.questionpro.net` failed to
  resolve on one run (`NameResolutionError`), then resolved fine seconds
  later on retry. Not an auth issue, not a code issue — looked like a VPN/
  internal-network blip. **Recommend:** on `NameResolutionError`/connection
  refused, retry once via a quick `curl -m5 https://metabase.questionpro.net/api/user/current`
  before assuming the session token is bad — saves a wasted re-auth cycle.

- **KNOWN_ISSUES.md recurrence check is manual.** No prior week's
  `error_report.md` was diffed against this week's 13 clusters — all 13
  looked like first-time occurrences vs. the last logged KI-001/002/003
  (dormant since 2026-06-04), but this was eyeballed, not automated.
  **Recommend:** a small script/step that diffs this week's cluster root
  causes against KNOWN_ISSUES.md's open KI entries and flags exact or
  fuzzy matches, instead of relying on memory across weeks.

---

<!-- Add new dated entries above this line -->
