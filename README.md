# communities-weekly-reports

Automated weekly report generator for the Communities product. Runs all report
modules in parallel and produces a single copy-paste block for the team update.

---

## What it generates

One run produces the following files under `reports/YYYY-MM-DD_to_YYYY-MM-DD/`:

| File | Contents |
|---|---|
| `weekly_report.md` | Combined copy-paste block — this is what you post |
| `error_report.md` | 500 error clustering: root causes, DC split, portal/panel |
| `metrics_report.md` | Panel login + survey activity counts by DC |
| `metrics_report.csv` | Same data as CSV |
| `radar_report.md` | Radar tickets for the week |
| `perf_report.md` | Slow query breakdown (Admin + Portal) |
| `raw/us_errors.json` | Raw error rows from US DC (Metabase) |
| `raw/eu_errors.json` | Raw error rows from EU DC (Metabase) |
| `raw/errors_combined.json` | Merged US + EU rows fed into error_report |

---

## Setup

### 1. Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> If `pip install -r requirements.txt` fails outside a venv with
> `error: externally-managed-environment` — that's PEP 668 (modern Debian/
> Ubuntu Python). Use the venv steps above, don't pass `--break-system-packages`.
>
> **Always `source .venv/bin/activate` before running `run_all.py`** (each
> new shell). `run_all.py` spawns `modules/fetcher.py` as `python3` via
> `$PATH` — if the venv isn't active, that subprocess silently falls back
> to system Python and fails with `ModuleNotFoundError: No module named 'dotenv'`
> even though `run_all.py` itself started fine.

### 2. Configure `.env`

```bash
cp .env.example .env
```

Open `.env` and fill in only one value — your Metabase session token:

```
METABASE_SESSION_TOKEN=paste-your-metabase.SESSION-cookie-value-here
```

All other values (URL, question IDs) are already set to the correct defaults in `.env.example`.

**How to get the session token:**
1. Open [metabase.questionpro.net](https://metabase.questionpro.net) in Chrome and sign in via Google
2. Press F12 → Application tab → Cookies → `metabase.questionpro.net`
3. Find the cookie named `metabase.SESSION` → copy its Value
4. Paste it as `METABASE_SESSION_TOKEN` in `.env`

> The token expires ~2 weeks or on logout. When you start seeing 401 errors, re-copy it from the browser.

---

## Running

### Generate this week's report (auto date range: last Fri → last Thu)

```bash
python3 run_all.py
```

### Generate for a specific date range

```bash
python3 run_all.py --from 2026-06-19 --to 2026-06-25
```

### Dry-run (validates config without hitting Metabase)

```bash
python3 run_all.py --from 2026-06-19 --to 2026-06-25 --dry-run
```

All four modules run in parallel. Total runtime is ~3–5 minutes (bottleneck is the
Admin slow-query question which takes up to 4 min on heavy days).

---

## Running a single module

Each module can also be run standalone:

```bash
python3 modules/metabase_report.py --from 2026-06-19 --to 2026-06-25
python3 modules/radar_report.py    --from 2026-06-19 --to 2026-06-25
python3 modules/performance_report.py --from 2026-06-19 --to 2026-06-25

# Fetch raw error data only (US or EU separately)
python3 modules/fetcher.py --from 2026-06-19 --to 2026-06-25 --question-id 7162  # US
python3 modules/fetcher.py --from 2026-06-19 --to 2026-06-25 --question-id 7163  # EU
```

---

## Project structure

```
run_all.py              ← entry point: orchestrates all modules in parallel
modules/                ← individual report generators
  fetcher.py            ← Metabase data fetcher (used as subprocess)
  error_report.py       ← 500 error clustering + classification
  metabase_report.py    ← survey/login metrics
  radar_report.py       ← radar tickets
  performance_report.py ← slow query breakdown
  assemble_report.py    ← combines all outputs into weekly_report.md
lib/                    ← shared utilities (imported by modules)
  utils.py              ← ROOT path, get_week_range()
  metabase.py           ← Metabase auth + run_question()
reports/                ← generated output (one folder per week, gitignored)
config.yaml             ← database source IDs per DC (metrics module)
.env                    ← your secrets — never committed
.env.example            ← template with all defaults filled in
KNOWN_ISSUES.md         ← recurring errors tracked across weeks
```

---

## DC and side classification (500 errors)

**DC** is determined by hostname:

| Host pattern | DC |
|---|---|
| `pveu*`, `onepoll*` | EU |
| `qa*`, `*qaapp*`, `*qaweb*`, `qa11`, `saqa*` | QA (non-production) |
| everything else | US |

**Side** is determined by URL signals in the request + stacktrace:

| Side | Meaning |
|---|---|
| Portal | Member-facing (panel members logging in, taking surveys) |
| Panel | Admin-facing (panel managers, reports, moderation) |

---

## Tracking recurring issues

`KNOWN_ISSUES.md` tracks errors that appear across multiple weeks.

After each report:
- Bump **last seen** date for active issues
- Mark **resolved** for anything that disappeared
- Add a new `KI-NNN` entry for issues appearing a second consecutive week
