---
name: slow-endpoint-report
description: >
  Generates the "Top 3 Slowest Queries" section from Metabase question 7304
  (slow-endpoint-communities). Runs automatically as part of run_all.py — this
  skill documents the module for standalone runs and troubleshooting.
---

## When to use this skill

- User asks to (re)generate just the slow-endpoint / top-3-slowest-queries section
- `slow_endpoint_report.md` is missing or looks wrong and needs regenerating standalone
- Investigating why a specific endpoint is/isn't showing in the top 3

**Normally you don't invoke this directly** — `run_all.py` runs it in parallel
with the other 4 modules as part of `.claude/skills/weekly-report.md`.

---

## What it does

Metabase question 7304 returns each endpoint's `avg_worst_sql_ms` (average
worst-case SQL time) and `request_count` for a date range — but querying the
full week directly is slow (same class of problem as the admin/portal
performance questions), and the average it returns is **per-query-window**,
not summable across days.

So `modules/slow_endpoint_report.py`:

1. Splits the week into daily `(date_from, date_to)` pairs
2. Runs question 7304 once per day, all in parallel (`ThreadPoolExecutor`)
3. Each day's result is that day's slowest endpoints with their own
   `avg_worst_sql_ms` + `request_count`
4. Combines across days with a **request-count-weighted average** per
   endpoint (`sum(avg_ms * count) / sum(count)`) — a straight average of
   averages would under-weight heavy days
5. Sorts descending by weighted average latency, takes the top 3

**Known limitation:** the question itself only returns a handful of rows per
day (whatever it considers "slow" that day). An endpoint that's consistently
mediocre every day but never the single worst on any given day won't surface.
This approximates the true weekly top-3, it doesn't guarantee it — good
enough for a weekly trend read, not for exhaustive SLO tracking.

---

## Output format

```bash
python3 modules/slow_endpoint_report.py --from 2026-08-07 --to 2026-08-13
```

Writes `reports/{START}_to_{END}/slow_endpoint_report.md` containing:
- The copy-paste block (below)
- A full breakdown table of every endpoint seen across the week's daily
  top-slots, not just the final top 3 — useful for spotting near-misses

Copy-paste block format (this is what lands in `weekly_report.md`):

```
Top 3 Slowest Queries
         • /showPanelAPIRequestLog.do – Latency : 282517 ms
         • /getCrosstabResults – Latency : 2222 ms
         • /addProfileCrosstabReport – Latency : 1900 ms
```

Endpoint display names are simplified in `display_endpoint()`:
- `.do` actions: `/a/showPanelAPIRequestLog.do` → `/showPanelAPIRequestLog.do` (just drop `/a`)
- AJS handlers: `/a/ajs/survey-angular.panel.ProfileCrossTabAJSHandler-GetCrosstabResults`
  → `/getCrosstabResults` (method name after the last `-`, lowercase first letter)

---

## Config

`.env` — `METABASE_QUESTION_ID_SLOW_ENDPOINT=7304` (question:
https://metabase.questionpro.net/question/7304-slow-endpoint-communities).

Same auth as every other module — `METABASE_SESSION_TOKEN` in `.env`.

---

## Troubleshooting

- **Timeout on a heavy day** — question is queried per-day already; if a
  single day still times out, check if that day had an unusual traffic spike,
  or bump `QUERY_TIMEOUT` in `slow_endpoint_report.py` (currently 300s, same
  as the admin/portal performance questions).
- **Top 3 looks suspiciously stable week to week** — likely the same
  chronic-slow endpoint (e.g. `showPanelAPIRequestLog.do` doing a full table
  scan) rather than a bug in this module — cross-check against
  `perf_report.md`'s `> 1000ms` bucket trend for the same week.
- **An endpoint you expected isn't there** — see the known limitation above;
  check the full breakdown table in `slow_endpoint_report.md`, it may show up
  there ranked just outside the top 3.
