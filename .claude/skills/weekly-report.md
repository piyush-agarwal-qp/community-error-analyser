---
name: weekly-report
description: >
  Master skill — runs all Communities weekly report modules in parallel,
  runs error analysis, then assembles the final weekly_report.md.
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

This runs simultaneously:
- `metabase_report.py` → `metrics_report.md`
- `fetcher.py` + `error_report.py` → `errors_combined.json` + `error_report.md`
- `radar_report.py` → `radar_report.md`
- `performance_report.py` → `perf_report.md`

After all modules complete, `run_all.py` calls `assemble_report.py` automatically
→ `reports/{START}_to_{END}/weekly_report.md`

Output folder: `reports/{START}_to_{END}/`

If any module fails with auth error → re-copy `metabase.SESSION` cookie from browser → update `.env` as `METABASE_SESSION_TOKEN`.

---

## Step 3 — Review errors (optional)

`error_report.md` is now generated automatically with:
- Cluster details (hash-based grouping, severity, DC, portal/panel side)
- PDM block  
- Engineering update block

If deeper RCA is needed on a specific cluster, follow `.claude/skills/error-report.md`
pointing at `reports/{START}_to_{END}/errors_combined.json`.

Update `KNOWN_ISSUES.md` with new recurring issues found.

---

## Step 4 — Show final report

Print the contents of `reports/{START}_to_{END}/weekly_report.md` to the user.
(`run_all.py` already assembled it — no need to run `assemble_report.py` again.)

---

Remind them to fill in the manual sections:
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

## Output folder summary

```
reports/{START}_to_{END}/
  metrics_report.csv      ← raw counts
  metrics_report.md       ← formatted survey/login metrics
  errors_combined.json    ← raw 500 error data (65 rows)
  error_report.md         ← clustered analysis + PDM + engineering update
  radar_report.md         ← radar tickets with brief
  perf_report.md          ← slow query breakdown (admin + portal)
  weekly_report.md        ← combined copy-paste block ← SHARE THIS
```

## Auth errors

Session token expires ~2 weeks or on logout.
Re-copy: browser → F12 → Application → Cookies → `metabase.SESSION` → paste as `METABASE_SESSION_TOKEN` in `.env`.
