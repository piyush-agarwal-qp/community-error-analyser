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

## Step 1.5 — Extract action class + exception type precisely

The automated `error_report.py` clusters by Metabase's pre-computed `hash`
column — this can bucket two truly-related errors apart (different hash,
same real cause) or lump unrelated ones together. When investigating,
re-derive the two signals that actually identify a root cause:

- **Exception type** — the class name on the top-level line or the
  **deepest** `Caused by:` line (e.g. `SQLIntegrityConstraintViolationException`,
  `java.lang.NullPointerException`). Deepest `Caused by:` wins — same rule
  `extract_root_cause()` in `error_report.py` already follows.
- **Action class + method** — the **deepest** `com.surveyconsole.*` (or
  `com.bhaskaran.*`) stack frame matching `<ActionClass>.<method>`, taken
  from that same deepest `Caused by:` block, not the top of the trace. The
  top frame is usually generic servlet/dispatcher plumbing — the deepest
  codebase frame is where the bug actually lives.

```bash
python3 -c "
import re
st = open('/tmp/one_stacktrace.txt').read()  # paste one row's 'st' field here
frames = re.findall(r'at (com\.(?:surveyconsole|bhaskaran)\.[\w.]+)\(', st)
print('deepest action frame:', frames[-1] if frames else '(none found)')
"
```

**Regroup manually when:**
- Same action class + same exception type across different hashes/hosts →
  it's one issue, not several — merge for KNOWN_ISSUES.md purposes.
- Same action class + *different* exception types → likely related (same
  buggy method failing in more than one way) — call this out together in
  the write-up even if kept as separate clusters.
- Different hostnames/DCs but same action+exception → consolidate into a
  single reported issue; DC is a symptom of traffic distribution, not a
  distinct root cause.

**Confidence, when reporting a regrouping to the user:**
- **high** — action class and exception type both cleanly extracted from a
  real codebase frame.
- **medium** — exception type clear, but no `com.surveyconsole`/`com.bhaskaran`
  frame in the trace (e.g. pure framework/SQL driver exception) — action
  class is a guess from the endpoint instead.
- **low** — stacktrace truncated or frames dominated by generic library
  code — flag it rather than force a grouping.

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
- Action class: always take the **deepest** `com.surveyconsole`/`com.bhaskaran`
  frame in the deepest `Caused by:` block, not the first frame in the trace —
  the top frame is dispatcher/servlet plumbing, not where the bug lives
- Metabase's `hash` column ≠ true root cause — two hashes with the same
  action class + exception type are the same issue (see Step 1.5)
