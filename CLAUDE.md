# Communities Weekly Reports

Master report generator for the Communities product weekly update.
Runs all report modules in parallel and assembles a combined copy-paste block.

## Trigger phrases

- "generate weekly report from DATE to DATE"
- "run weekly reports for June 19 to June 25"
- "generate this week's communities report"

## On trigger: follow `.claude/skills/weekly-report.md` exactly

## Quick reference

**Run all reports (parallel):**
```bash
python3 run_all.py --from YYYY-MM-DD --to YYYY-MM-DD
```

**Run a single module:**
```bash
python3 metabase_report.py --start YYYY-MM-DD --end YYYY-MM-DD
python3 fetcher.py --from YYYY-MM-DD --to YYYY-MM-DD --question-id 7162 > /tmp/us_errors.json
python3 fetcher.py --from YYYY-MM-DD --to YYYY-MM-DD --question-id 7163 > /tmp/eu_errors.json
python3 radar_report.py --start YYYY-MM-DD --end YYYY-MM-DD
python3 performance_report.py --start YYYY-MM-DD --end YYYY-MM-DD
```

**Output folder:**
```
reports/YYYY-MM-DD_to_YYYY-MM-DD/
  metrics_report.csv      ← survey/login counts (raw)
  metrics_report.md       ← survey/login counts (formatted)
  error_report.md         ← 500 errors analysis
  radar_report.md         ← radar tickets
  perf_report.md          ← slow query breakdown
  weekly_report.md        ← combined copy-paste block
```

## .env required

```
METABASE_URL=https://metabase.questionpro.net
METABASE_SESSION_TOKEN=<metabase.SESSION browser cookie>
METABASE_QUESTION_ID_US=7162
METABASE_QUESTION_ID_EU=7163
METABASE_QUESTION_ID_RADAR=7302
```

## Auth errors

If any script returns 401 / "session expired": re-copy `metabase.SESSION` from browser
→ F12 → Application → Cookies → metabase.SESSION → paste into `.env` as `METABASE_SESSION_TOKEN`.

## Report modules

| Module | Script | Status |
|---|---|---|
| Survey/Login metrics | `metabase_report.py` | ✓ |
| 500 Errors | `fetcher.py` + skill | ✓ |
| Radar tickets | `radar_report.py` | ✓ |
| Performance / slow queries | `performance_report.py` | pending |
| Combined assembler | `run_all.py` | in progress |
