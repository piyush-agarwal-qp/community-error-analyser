---
name: error-report
description: >
  Generate weekly Communities error report from Metabase. Clusters errors,
  splits by DC and portal/panel side, outputs PDM + Engineering Update blocks.
  Dense output only — no filler.
---

## Output style (embedded — no external skill needed)

Respond terse. Drop: articles, filler (just/really/basically), pleasantries, hedging.
Fragments OK. Arrows for causality (X → Y). Short synonyms. Abbreviate (DB/config/req).
Technical terms, class names, error messages stay exact. Code blocks unchanged.
All prose lowercase. No capitalisation except Java class/method names and acronyms (DC, US, EU, QA, AJS, PDM).
Pattern: `[thing] [action] [reason]. [next step].`

---

## Trigger

- "generate this week's error report"
- "analyse errors from [date] to [date]"
- "run weekly error analysis"
- "show production errors"

---

## Step 1 — Fetch and save (once — never fetch twice)

```bash
python3 fetcher.py --from YYYY-MM-DD --to YYYY-MM-DD > /tmp/errors.json 2>/tmp/fetcher_stderr.log
```

All subsequent steps read from `/tmp/errors.json`. If fetch fails, check `/tmp/fetcher_stderr.log`.

---

## Step 2 — Pre-cluster analysis

Run this on the saved file to understand shape before writing the report:

```bash
python3 -c "
import json, sys, collections, re

with open('/tmp/errors.json') as f:
    data = json.load(f)
rows = data['rows']

def dc(host):
    h = host.lower()
    if 'pveu' in h or 'onepoll' in h: return 'EU'
    if h.startswith('qa') or 'qaapp' in h or 'qaweb' in h or h == 'qa11': return 'QA'
    return 'US'

PORTAL = {'showPanelMemberDashBoard','showMemberSurveys','showRewardTab',
          'showMemberAccount','framework2AdHocPortal'}
PANEL  = {'showPanelUserReport','showDiscussionModeration','searchSurveyCampaignBatch',
          'panelLanguageTranslationImport','inviteUsers','showPanelProjectHistory',
          'showPanelIdeasSetup','editLanguage','editFlashletSurvey','twitterSignIn','loadResponse'}

def side(url, st):
    # AJS handler URL is definitive
    if 'PortalDashBoardAJSHandler' in url or 'portal' in url.lower(): return 'portal'
    # extract referrer from AJSServlet header block
    m = re.search(r'\"referer\":\"([^\"]+)\"', st)
    ref = m.group(1) if m else ''
    for p in PORTAL:
        if p.lower() in ref.lower(): return 'portal'
    for p in PANEL:
        if p.lower() in ref.lower(): return 'panel'
    # stack trace keyword fallback — referrer preferred above; class names alone are unreliable
    # (PanelMember/PanelDetail appear in both portal and panel paths)
    for p in PORTAL:
        if p.lower() in st.lower(): return 'portal'
    for p in PANEL:
        if p.lower() in st.lower(): return 'panel'
    return 'other'  # do NOT fall back to 'panel' — 'panel' in st is too broad

# --- clusters ---
by_hash = collections.defaultdict(list)
for r in rows: by_hash[r['hash']].append(r)
print('=== CLUSTERS ===')
for h, rs in sorted(by_hash.items(), key=lambda x: -len(x[1])):
    urls = sorted(set(r['url'] for r in rs if r['url']))
    dcs  = sorted(set(dc(r['host']) for r in rs))
    # split on both newline and <BR> — AJSServlet uses <BR><BR> not \n
    first_line = re.split(r'<BR>|\n', rs[0]['st'])[0][:150]
    print(f'hash={h} count={len(rs)} dc={dcs} urls={urls[:2]}')
    print(f'  {first_line}')

# --- DC breakdown ---
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
| Same hash, same URL → one cluster | merge |
| Same hash, **different URLs** → split | separate cluster per URL — `GetTaskDetails` ≠ `GetSurveyDetails` even if hash matches |
| Same exception + same call site, multi-host → one cluster | merge |
| QA hosts only → severity = low, label QA-only | keep separate from prod |
| `InvocationTargetException` → real cause is wrapped; Metabase log truncates it | always note: "check getCause() in Resin logs" |

---

## Step 4 — DC & Side classification

**DC:**
| Host pattern | DC |
|---|---|
| `pveu*`, `onepoll*` | EU |
| `qa*`, `*qaapp*`, `*qaweb*`, `qa11` | QA |
| everything else (qprun*, qpweb*, pvqpadminapp*, sarun*, adminapp*) | US |

**Side (Communities-specific):**

Portal = member-facing (what panel members see):
- AJS URL contains `PortalDashBoardAJSHandler`
- Referrer contains: `showPanelMemberDashBoard`, `showMemberSurveys`, `showRewardTab`, `showMemberAccount`, `framework2AdHocPortal`

Panel = admin-facing (what panel managers see):
- Referrer contains: `showPanelUserReport`, `searchSurveyCampaignBatch`, `panelLanguageTranslationImport`, `showDiscussionModeration`, `showPanelProjectHistory`, `showPanelIdeasSetup`, `editLanguage`, `twitterSignIn`, `inviteUsers`

**Classify by priority:** AJS URL → referrer → stack trace keywords → `other`

Do NOT classify as `panel` just because `PanelMember` or `PanelDetail` appears in the stack — these classes are used in both portal and panel paths. Referrer is the reliable signal.

---

## Step 5 — Severity scale

| Level | Criteria |
|-------|---------|
| critical | broken for all users across all prod nodes in a DC |
| high | broken for a region or significant user subset |
| medium | broken for specific customers / edge paths |
| low | QA-only, deprecated integrations, single-user config, count ≤ 2 |

---

## Step 6 — Report format

```markdown
# weekly error report — DD mon to DD mon YYYY

**date range:** YYYY-MM-DD → YYYY-MM-DD
**total errors:** N [add "(query limit hit — real volume higher)" if N=500]
**clusters:** N

---

## summary table

| # | severity | error type | count | dc | side |
|---|----------|-----------|-------|-----|------|
...

---

## dc & side breakdown

| dc | total | patterns | repetitive | one-offs | portal | panel | other |
|----|-------|---------|-----------|---------|--------|-------|-------|
| us | ... |
| eu | ... |
| qa | ... |

- **repetitive** = errors belonging to a hash seen >1 time (recurring bug)
- **one-offs** = hash seen exactly once (new or transient)
- **portal** = member-facing | **panel** = admin-facing

---

## cluster details

### N. [type] *([severity], [count] errors)*

**root cause:** one sentence

**summary:** 2-3 sentences — component, user impact, fix direction

**stack trace:**
\`\`\`
ExceptionClass: message
    at com.surveyconsole.Package.Class.method(Class.java:LINE)
    [wrapped — check getCause() in Resin logs]
\`\`\`

**dc / side:** us · portal
**affected endpoints:** ...
**affected hosts:** ...
**error ids (sample):** 3 representative ids only — e.g. 49417, 58512, 113186 *(438 total)*

---

## recommended actions

| priority | action |
|----------|--------|
| p0 | ... (cluster N) |

---

## pdm report

\`\`\`
[total] errors logged ([date range])

us dc — [N] panel, [N] portal
eu dc — [N] panel, [N] portal
qa    — [N] panel, [N] portal  (non-production)
\`\`\`

counts = distinct error types (clusters), not total rows.
portal = member-facing. panel = admin-facing.

---

## engineering update

\`\`\`
[total] errors | panel-[N], portal-[N] (us) | portal-[N], panel-[N] (eu)

~ [count] : [one line lowercase — what broke, where, user impact]
~ [count] : [one line lowercase]
\`\`\`

include only: production clusters, count ≥ 5, or severity critical/high regardless of count.
format: `~ [count] : [component] — [exception short] — [impact]`
all text lowercase.
```

---

## Step 7 — Save report

```
reports/error_report_YYYY-MM-DD.md   ← use --to date (or today for --days)
```

Create `reports/` dir if it doesn't exist. Always save. Do not wait for user to ask.

---

## Step 8 — Update KNOWN_ISSUES.md

- still active → bump last seen date, update count trend line
- resolved (not in this week's data) → mark resolved + date
- new issue appearing 2nd consecutive week → add KI-NNN entry

---

## Common pitfalls

- same hash ≠ same bug when URL differs — always split by endpoint
- `InvocationTargetException` wraps real cause — Metabase truncates it; note getCause() needed
- 500 rows = query limit hit — real volume higher, note in header
- QA hosts = low severity, never critical
- `pveu*` = EU; `sarun*`, `qprun*`, `qpweb*`, `pvqpadminapp*` = US
- `PanelMember`/`PanelDetail` in stack trace does NOT mean panel-side — use referrer
- Zoom/SMTP/Twitter = panel-side (admin integrations)
- never fetch twice — save to `/tmp/errors.json` and reuse
