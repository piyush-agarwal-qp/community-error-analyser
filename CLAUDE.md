# Weekly Error Analyser

Generates weekly error reports for the Communities product.
`fetcher.py` fetches from Metabase. Full analysis instructions are in `.claude/skills/error-report.md`.

## Trigger phrases

- "generate this week's error report"
- "analyse errors from last 7 days"
- "what errors happened between [date] and [date]"
- "run the weekly error analysis"
- "show me this week's production errors"

## On trigger: follow `.claude/skills/error-report.md` exactly

Do not improvise steps. The skill file has the fetch command, pre-cluster script, clustering rules, DC/portal/panel classification, report format, PDM block, engineering update format, and KNOWN_ISSUES.md update procedure.

## Quick reference

**Fetch:**
```bash
python3 fetcher.py --days 7
python3 fetcher.py --from YYYY-MM-DD --to YYYY-MM-DD
```

**Save output first, analyse from file — never fetch twice:**
```bash
python3 fetcher.py --from YYYY-MM-DD --to YYYY-MM-DD > /tmp/errors.json 2>/tmp/fetcher_stderr.log
```

**If count = 0:** tell user no errors found, suggest widening range or refreshing `METABASE_SESSION` in `.env`.

**If count = 500:** note "query limit hit" in report header — real volume is higher.

**Save report as:** `error_report_YYYY-MM-DD.md` (always save, don't wait to be asked).

## .env required

```
METABASE_URL=https://your-metabase.company.com
METABASE_SESSION=<metabase.SESSION browser cookie value>
METABASE_QUESTION_ID=<saved question id>
```
