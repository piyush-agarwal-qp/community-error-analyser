# Weekly Error Analyser Skill

Use this skill to generate weekly error reports for the Communities product.
`fetcher.py` handles Metabase — you handle the analysis.

## When to use this skill

Trigger when the user says things like:
- "generate this week's error report"
- "analyse errors from last 7 days"
- "what errors happened between [date] and [date]"
- "run the weekly error analysis"
- "show me this week's production errors"

## How to run it — step by step

### Step 1: Run fetcher.py to get the data

```bash
python fetcher.py --days 7
```

Or for a specific date range:
```bash
python fetcher.py --from 2026-05-29 --to 2026-06-04
```

The script prints JSON to stdout and progress messages to stderr.
Capture stdout only — that's the error data.

### Step 2: Parse the JSON output

The output has this shape:
```json
{
  "date_from": "2026-05-29",
  "date_to":   "2026-06-04",
  "count":     47,
  "rows": [
    {
      "id":     123,
      "ts":     "2026-05-29T08:12:00Z",
      "host":   "qprun3.questionpro.net",
      "hash":   "-2000475069",
      "module": "",
      "url":    "survey-angular.panel.portal.PortalDashBoardAJSHandler-GetTaskDetails",
      "st":     "java.lang.reflect.InvocationTargetException\nCaused by: ..."
    }
  ]
}
```

### Step 3: Cluster by root cause

Group the rows into error clusters. Rules:
- Same DB table missing across different shards/hosts = **one cluster**
- Same exception class + same call site = **one cluster**
- Different panels/users hitting the same bug = **one cluster**
- Genuinely different failures = separate clusters

For each cluster produce:
- **type**: short name ≤ 6 words
- **severity**: critical (service down) / high (feature broken) / medium (degraded) / low (noise)
- **count**: number of rows
- **ids**: list of error IDs in the cluster
- **root_cause**: one sentence — what exactly is failing and why
- **summary**: 2-3 sentences — component affected, user impact, suggested fix direction
- **affected_hosts**: unique hostnames
- **affected_endpoints**: unique URL values

### Step 4: Render the report

Output a markdown report with:
1. Header: date range, total errors, cluster count
2. Summary table: severity | error type | count | hosts
3. Detail section per cluster: root cause, summary, endpoints, hosts, IDs

## CLI options for fetcher.py

| Flag | Default | Description |
|------|---------|-------------|
| `--days N` | 7 | Past N days |
| `--from YYYY-MM-DD` | — | Start date |
| `--to YYYY-MM-DD` | today | End date |
| `--limit N` | 500 | Max rows |
| `--question-id N` | from .env | Saved Metabase question ID |
| `--db-id N` | from .env | Database ID (raw SQL mode) |
| `--input FILE` | — | Local JSON file, skips Metabase |

## .env required

```
METABASE_URL=https://your-metabase.company.com
METABASE_SESSION=<value of metabase.SESSION browser cookie>
METABASE_QUESTION_ID=112
```

## If fetcher.py returns count: 0

Tell the user no errors were found for that date range and suggest
widening the range or checking that the Metabase session is still valid.

## Saving the report

If the user asks to save the report, write it as markdown:
```
error_report_YYYY-MM-DD.md
```
