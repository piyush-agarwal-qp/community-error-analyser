---
name: weekly-report
description: >
  Master skill — runs all Communities weekly report modules in parallel,
  assembles the final weekly_report.md, and commits.
---

## Trigger phrases

- "generate weekly report from DATE to DATE"
- "run weekly reports for June 19 to June 25"
- "generate this week's communities report"

---

## Step 1 — Parse dates

Extract START and END from user input. Accept natural language or ISO:
- `from june 19 to june 25` → `2026-06-19` / `2026-06-25`
- `2026-06-19 to 2026-06-25`

Confirm dates before proceeding if ambiguous.

---

## Step 2 — Run all modules in parallel

```bash
python3 run_all.py --from {START} --to {END}
```

This fires all 5 modules simultaneously:

| Module | Script | Output |
|---|---|---|
| Survey/Login metrics | `metabase_report.py` | `metrics_report.md` |
| 500 Errors (fetch + analyse) | `fetcher.py` + `error_report.py` | `error_report.md` |
| Radar tickets | `radar_report.py` | `radar_report.md` |
| Slow query performance | `performance_report.py` (14 queries parallel) | `perf_report.md` |
| Top 3 slowest endpoints | `slow_endpoint_report.py` (1 query/day parallel) | `slow_endpoint_report.md` |

After all modules complete, `run_all.py` calls `assemble_report.py` automatically
→ `reports/{START}_to_{END}/weekly_report.md`

Expected runtime: **3–5 minutes** (bottleneck is performance, 14 parallel queries).

If any module fails with 401 / auth error → re-copy `metabase.SESSION` from browser
→ F12 → Application → Cookies → paste as `METABASE_SESSION_TOKEN` in `.env`.

---

## Step 3 — Review error report (optional)

`error_report.md` is generated automatically with:
- Root cause per cluster (deepest `Caused by:` in chain)
- Codebase frames from the `Caused by:` block
- Request context (referer, IP, country, params)
- DC (US/EU/QA) + side (portal/panel/other) classification
- PDM block + engineering update block

For deeper RCA on a specific cluster, follow `.claude/skills/error-report.md`.

Update `KNOWN_ISSUES.md` with any new recurring issues found.

---

## Step 4 — Show final report

Print contents of `reports/{START}_to_{END}/weekly_report.md`.

Remind user to fill in manual sections:
- **Enhancement / Bugs / UX / Performance / Test & Coverage** → paste from sprint board
- **Iron test coverage** → paste from CI

---

## Step 5 — Commit

```bash
git add reports/{START}_to_{END}/
git add KNOWN_ISSUES.md
git status --short
```

Show what will be committed. Ask: **"Commit these files? (y/n)"**

If yes:
```bash
git commit -m "weekly reports: {START} to {END}"
```

---

## Output folder structure

```
reports/{START}_to_{END}/
  weekly_report.md        ← combined copy-paste block  ← SHARE THIS
  error_report.md         ← clustered analysis + PDM + engineering update
  metrics_report.md       ← survey/login counts (formatted)
  metrics_report.csv      ← survey/login counts (raw)
  radar_report.md         ← radar tickets with brief
  perf_report.md          ← slow query breakdown (admin + portal)
  slow_endpoint_report.md ← top 3 slowest endpoints by weighted avg latency
  raw/
    errors_combined.json  ← raw 500 error fetch data (processing only)
```

## Auth errors

Session token expires ~2 weeks or on logout.
Re-copy: browser → F12 → Application → Cookies → `metabase.SESSION` → paste as `METABASE_SESSION_TOKEN` in `.env`.
