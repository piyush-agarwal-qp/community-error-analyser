---
name: error-report
description: >
  Generate weekly Communities error report from Metabase. Clusters errors,
  splits by DC and portal/panel side, outputs PDM + Engineering Update blocks.
  Caveman style — no filler, no padding, dense output only.
---

Activate caveman mode for entire output. No summaries, no padding, no "here is the report". Just data.

## Trigger

- "generate this week's error report"
- "analyse errors from [date] to [date]"
- "run weekly error analysis"
- "show production errors"

---

## Step 1 — Fetch

```bash
python3 fetcher.py --days 7 2>/tmp/fetcher_stderr.log
# or
python3 fetcher.py --from YYYY-MM-DD --to YYYY-MM-DD 2>/tmp/fetcher_stderr.log
```

Stdout = JSON data. Stderr = progress (discard). If fails, check `/tmp/fetcher_stderr.log`.

---

## Step 2 — Pre-cluster analysis (run this first, always)

```bash
python3 fetcher.py --from ... --to ... 2>/dev/null | python3 -c "
import json, sys, collections, re
data = json.load(sys.stdin)
rows = data['rows']

def dc(host):
    h = host.lower()
    if 'pveu' in h or 'onepoll' in h: return 'EU'
    if h.startswith('qa') or 'qaapp' in h or 'qaweb' in h or h == 'qa11': return 'QA'
    return 'US'

PORTAL = {'showPanelMemberDashBoard','showMemberSurveys','showRewardTab','showMemberAccount','framework2AdHocPortal'}
PANEL  = {'showPanelUserReport','showDiscussionModeration','searchSurveyCampaignBatch',
          'panelLanguageTranslationImport','inviteUsers','showPanelProjectHistory',
          'showPanelIdeasSetup','editLanguage','editFlashletSurvey','twitterSignIn','loadResponse'}

def side(url, st):
    if 'PortalDashBoardAJSHandler' in url or 'portal' in url.lower(): return 'portal'
    m = re.search(r'\"referer\":\"([^\"]+)\"', st)
    ref = m.group(1) if m else ''
    for p in PORTAL:
        if p.lower() in ref.lower() or p.lower() in st.lower(): return 'portal'
    for p in PANEL:
        if p.lower() in ref.lower() or p.lower() in st.lower(): return 'panel'
    if 'panel' in st.lower(): return 'panel'
    return 'other'

# Clusters
by_hash = collections.defaultdict(list)
for r in rows: by_hash[r['hash']].append(r)
print('=== CLUSTERS ===')
for h, rs in sorted(by_hash.items(), key=lambda x: -len(x[1])):
    urls = sorted(set(r['url'] for r in rs if r['url']))
    dcs  = sorted(set(dc(r['host']) for r in rs))
    print(f'hash={h} count={len(rs)} dc={dcs} urls={urls[:2]}')
    print(f'  {rs[0][\"st\"].split(chr(10))[0][:150]}')

# DC breakdown
print()
print('=== DC BREAKDOWN ===')
for d in ['US','EU','QA']:
    rs = [r for r in rows if dc(r['host']) == d]
    if not rs: continue
    hc = collections.Counter(r['hash'] for r in rs)
    sides = collections.Counter(side(r['url'], r['st']) for r in rs)
    rpt = sum(1 for r in rs if hc[r['hash']] > 1)
    oof = sum(1 for r in rs if hc[r['hash']] == 1)
    print(f'{d}: total={len(rs)} patterns={len(hc)} repetitive={rpt} one-off={oof} portal={sides[\"portal\"]} panel={sides[\"panel\"]} other={sides[\"other\"]}')
"
```

---

## Step 3 — Clustering rules

| Rule | Action |
|------|--------|
| Same hash, same URL → one cluster | Merge |
| Same hash, **different URLs** → split | Separate cluster per URL (e.g. GetTaskDetails ≠ GetSurveyDetails even if hash matches) |
| Same exception + same call site, multi-host → one cluster | Merge |
| QA hosts only → severity=low, note QA-only | Keep separate |
| InvocationTargetException → note getCause() needed, cause is truncated in Metabase log | Always flag |

---

## Step 4 — DC & Side classification

**DC rules:**
| Host pattern | DC |
|---|---|
| `pveu*`, `onepoll*` | EU |
| `qa*`, `*qaapp*`, `*qaweb*`, `qa11` | QA |
| everything else | US |

**Side rules (Communities-specific):**

Portal = **member-facing** (what panel members see):
- AJS handler: `PortalDashBoardAJSHandler-GetTaskDetails`, `PortalDashBoardAJSHandler-GetSurveyDetails`
- Pages: `showPanelMemberDashBoard`, `showMemberSurveys`, `showRewardTab`, `showMemberAccount`, `framework2AdHocPortal`

Panel = **admin-facing** (what panel managers see):
- Pages: `showPanelUserReport`, `searchSurveyCampaignBatch`, `panelLanguageTranslationImport`, `showDiscussionModeration`, `showPanelProjectHistory`, `showPanelIdeasSetup`, `editLanguage`, `twitterSignIn`, `inviteUsers`, `loadResponse`

Classify by: AJS URL first → referrer header → stack trace keywords → fallback `other`.

---

## Step 5 — Severity scale

| Level | Criteria |
|-------|---------|
| critical | Feature/service broken for all users across all prod nodes |
| high | Feature broken for a region or significant user subset |
| medium | Feature broken for specific customers / edge paths |
| low | QA-only, deprecated integrations, single-user config, one-offs |

---

## Step 6 — Report format (output exactly this structure, caveman dense)

```markdown
# Weekly Error Report — DD Mon to DD Mon YYYY

**Date range:** YYYY-MM-DD → YYYY-MM-DD
**Total errors:** N [add "(query limit hit)" if N=500]
**Clusters:** N

---

## Summary Table

| # | Severity | Error Type | Count | DC | Side |
|---|----------|-----------|-------|-----|------|
...

---

## DC & Side Breakdown

| DC | Total | Patterns | Repetitive | One-offs | Portal | Panel | Other |
|----|-------|---------|-----------|---------|--------|-------|-------|
| US | ... |
| EU | ... |
| QA | ... |

- **Repetitive** = errors belonging to a hash seen >1 time (known recurring bug)
- **One-offs** = errors with hash seen exactly once (new/transient)
- **Portal** = member-facing errors | **Panel** = admin-facing errors

---

## Cluster Details

### N. [Type] *([Severity], [count] errors)*

**Root cause:** one sentence

**Summary:** 2-3 sentences — component, user impact, fix direction

**Stack trace:**
\`\`\`
ExceptionClass: message
    at com.surveyconsole.Package.Class.method(Class.java:LINE)
    [note if wrapped — getCause() needed]
\`\`\`

**DC / Side:** US · portal
**Affected endpoints:** ...
**Affected hosts:** ...
**Error IDs (all N):** comma-separated

---

## Recommended Actions

| Priority | Action |
|----------|--------|
| P0 | ... (cluster N) |

---

## PDM Report

\`\`\`
[Total] Errors Logged ([date range])

US DC — [N] panel, [N] portal
EU DC — [N] panel, [N] portal
QA    — [N] panel, [N] portal  (non-production)
\`\`\`

> Counts = distinct error types (clusters), not total rows.
> Portal = member-facing. Panel = admin-facing.

---

## Engineering Update

\`\`\`
[Total] Errors | Panel-[N], Portal-[N] (US) | Portal-[N], Panel-[N] (EU)

~ [count] : [one line lowercase — what broke, where, user impact]

~ [count] : [one line lowercase]
...
\`\`\`

Engineering bullets: significant clusters only (count > 1, production only). One line each.
Format: `~ [count] : [component] — [exception type short] — [impact]`
All text lowercase. No capitalisation except class/method names in stack traces.
```

---

## Step 7 — Save report

```
error_report_YYYY-MM-DD.md   ← use --to date (or today for --days)
```

---

## Step 8 — Update KNOWN_ISSUES.md

- Resolved this week → mark Resolved + date
- Still active → bump Last seen date + update count trend
- New issue appearing 2nd consecutive week → add KI-NNN entry

---

## Common pitfalls

- Same hash ≠ same bug when URL differs — split by endpoint
- `InvocationTargetException` wraps real cause — Metabase truncates it, note getCause() in report
- 500 rows = limit hit — note in header, real volume higher
- QA hosts always Low severity, never Critical
- `pveu*` = EU. Everything else without qa prefix = US.
- Zoom/SMTP/Twitter failures → classify side as panel (admin integration), not portal
