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

## 2026-08-14 — added slow-endpoint report module

- **New module `slow_endpoint_report.py`** (question 7304) hits the same
  problem as the existing performance module: full-week query is slow, and
  the value returned is an **average**, not summable across days. Reused
  performance_report's day-split + parallel-fetch pattern, but the
  combine step differs — instead of summing bucket counts, aggregated with
  a **request-count-weighted average per endpoint** across days before
  ranking top 3. A plain average-of-averages would under-weight heavy days.
  **Recommend:** if another "average metric per day" question ever needs
  wiring up, weighted-average-by-volume is the right combine, not sum or
  plain mean — check what the underlying question actually returns first.

- **The question only returns a handful of "slow" rows per day** — it's not
  an unlimited list we can slice top-3 from ourselves; each day's rows are
  already whatever Metabase's query considers slow that day. An endpoint
  that's chronically mediocre but never the single worst on any given day
  can't surface in this design. Documented as a known limitation in the
  new `.claude/skills/slow-endpoint-report.md` rather than silently
  presenting the top-3 as exhaustive.

- **Endpoint display names need cleanup for the copy-paste format** —
  AJS handler paths like `.../ProfileCrossTabAJSHandler-GetCrosstabResults`
  aren't human-readable; extracting the method name after the last `-` and
  lowercasing the first letter reproduces the requested format
  (`/getCrosstabResults`). Verified against the user-provided sample JSON
  before wiring into the real Metabase call — cheap way to catch parsing
  mismatches before spending an API round-trip.

<!-- Add new dated entries above this line -->
