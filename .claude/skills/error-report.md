---
name: error-report
description: >
  Deep-dive skill for investigating a specific 500 error cluster beyond what
  the automated error_report.md shows. Use this when you need to understand
  a specific bug's root cause, check if it's recurring, or update KNOWN_ISSUES.md.
  The standard automated report (run_all.py) handles generation — this skill
  is for investigation only.
---

## When to use this skill

- User asks to investigate a specific error cluster (e.g. "look into cluster #2")
- User asks "is this a known issue?"
- User asks to update KNOWN_ISSUES.md after reviewing the report
- Automated `error_report.md` shows `InvocationTargetException` or `Root Exception :` as root cause — real cause may be deeper in Resin logs or needs manual trace

**Do NOT use this skill to regenerate the report** — run `python3 run_all.py` instead.

---

## Step 1 — Locate error data

Raw data is at:
```
reports/{START}_to_{END}/raw/errors_combined.json
```

Check it exists:
```bash
ls reports/{START}_to_{END}/raw/errors_combined.json
```

If missing, fetch first:
```bash
python3 fetcher.py --from {START} --to {END} \
  --output reports/{START}_to_{END}/raw/errors_combined.json
```

---

## Step 2 — Inspect a specific cluster

Pull all rows for a given hash to see full stacktraces across multiple occurrences:

```bash
python3 -c "
import json
data = json.loads(open('reports/{START}_to_{END}/raw/errors_combined.json').read())
rows = [r for r in data['rows'] if str(r.get('hash')) == '{HASH}']
print(f'{len(rows)} rows for hash {HASH}')
for r in rows:
    print(f\"  id={r['id']}  host={r['host']}  ts={r['ts']}\")
    print(f\"  url={r.get('url','')}\")
    print(f\"  st={r['st'][:1000]}\")
    print()
"
```

Look for:
- Whether all occurrences have the same stacktrace or vary
- Whether it's one customer or many (check org/panel IDs in params)
- Whether it's time-clustered (one-day spike vs spread across the week)

---

## Step 3 — Check if it's a known issue

```bash
grep -i "{KEYWORD}" KNOWN_ISSUES.md
```

If found → check last seen date and count trend.
If not found and it appears 2+ consecutive weeks → add a new entry.

---

## Step 4 — Update KNOWN_ISSUES.md

For each cluster reviewed:

| State | Action |
|---|---|
| Active, seen before | Bump `last_seen` date, update count trend |
| Resolved (not in this week's data) | Mark `resolved: YYYY-MM-DD` |
| New, 2nd consecutive week | Add new `KI-NNN` entry |
| New, first time | Note in error_report.md summary, don't add KI yet |

---

## Classification reference

**DC:**
| Host pattern | DC |
|---|---|
| `pveu*`, `onepoll*` | EU |
| `qa*`, `qaapp*`, `qaweb*`, `qa11`, `saqa*` | QA |
| everything else | US |

**Side:**
- Portal = member-facing (`/a/panel.do`, `showMemberSurveys`, `showRewardTab`, `memberRedeemReward`, etc.)
- Panel = admin-facing (`showPanelUserReport`, `showDiscussionModeration`, `inviteUsers`, `showPanelManagement`, `showQPointInventory`, etc.)
- Referrer (classic `Referrer [URL]` or JSON `"referer"`) is the most reliable signal
- `PanelMember` / `PanelDetail` in the stack does NOT mean panel-side — both portal and panel paths use these classes

**Common pitfalls:**
- `InvocationTargetException` wraps the real cause — check `Caused by:` chain
- `Root Exception :` with no following line = stacktrace was truncated — check if STACKTRACE_CHARS in `fetcher.py` needs increasing
- 65 rows = Metabase question row limit — real volume may be higher
- QA-only clusters = low severity, non-production
