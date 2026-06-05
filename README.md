# community-error-analyser

weekly error report generator for the communities product. pulls errors from metabase, clusters by root cause, splits by dc and portal/panel side, outputs pdm + engineering update formats.

---

## setup

**1. install dependencies**

```bash
pip install -r requirements.txt
```

**2. configure `.env`**

copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

| key | what to put |
|-----|-------------|
| `METABASE_URL` | your metabase instance url |
| `METABASE_SESSION` | session token from browser cookies (f12 → application → cookies → `metabase.SESSION`) |
| `METABASE_QUESTION_ID` | id of the saved metabase question (from the url: `/question/112` → `112`) |
| `METABASE_DB_ID` | leave blank on first run — script will list available dbs |

> session token expires ~2 weeks or on logout. re-copy from browser when fetcher starts returning auth errors.

---

## usage

**fetch last 7 days:**

```bash
python3 fetcher.py --days 7
```

**fetch a specific date range:**

```bash
python3 fetcher.py --from 2026-05-29 --to 2026-06-04
```

**fetch to a local file (skip metabase):**

```bash
python3 fetcher.py --input errors.json
```

output is json on stdout. progress messages go to stderr.

**all cli flags:**

| flag | default | description |
|------|---------|-------------|
| `--days N` | 7 | past n days |
| `--from YYYY-MM-DD` | — | start date |
| `--to YYYY-MM-DD` | today | end date |
| `--limit N` | 500 | max rows |
| `--question-id N` | from `.env` | saved metabase question id |
| `--db-id N` | from `.env` | database id (raw sql mode) |
| `--input FILE` | — | local json file, skips metabase |

---

## generating the report

once you have data, hand it to claude code with:

> "analyse errors from 2026-05-29 to 2026-06-04 and save the report"

claude will run the fetcher, cluster errors, and produce a dated markdown file:

```
error_report_YYYY-MM-DD.md
```

the report contains:
- summary table (severity, type, count, dc, side)
- dc & side breakdown (us/eu/qa × portal/panel)
- per-cluster detail with stack trace + all error ids
- recommended actions
- **pdm report** — copy-paste block for product/management
- **engineering update** — `~ count : one-line description` bullets

---

## report structure

### dc classification

| host pattern | dc |
|---|---|
| `pveu*`, `onepoll*` | eu |
| `qa*`, `*qaapp*`, `*qaweb*`, `qa11` | qa |
| everything else | us |

### communities side classification

**portal** = member-facing (what panel members see)
- `PortalDashBoardAJSHandler-GetTaskDetails`
- `PortalDashBoardAJSHandler-GetSurveyDetails`
- pages: `showPanelMemberDashBoard`, `showMemberSurveys`, `showRewardTab`, `showMemberAccount`

**panel** = admin-facing (what panel managers see)
- pages: `showPanelUserReport`, `searchSurveyCampaignBatch`, `panelLanguageTranslationImport`, `showDiscussionModeration`, `showPanelProjectHistory`, `inviteUsers`, `editLanguage`

---

## tracking recurring issues

`KNOWN_ISSUES.md` tracks errors that appear across multiple weeks.

after each report:
- bump **last seen** date for active issues
- mark **resolved** for anything that disappeared
- add a new `KI-NNN` entry for any issue appearing a second consecutive week

---

## output example

**pdm report block:**
```
500 errors logged (29 may – 4 jun 2026)

us dc — 2 panel, 1 portal
eu dc — 3 panel, 1 portal
qa    — 1 panel, 1 portal  (non-production)
```

**engineering update block:**
```
500 errors | panel-2, portal-1 (us) | portal-1, panel-3 (eu)

~ 438 : member dashboard task list broken (gettaskdetails) — invocationtargetexception — all us prod nodes
~ 15  : member survey list broken (getsurveydetails) — eu onepoll nodes
~ 6   : zoom create-user api http 400 — eu admin panel zoom integration broken
~ 7   : nullpointerexception in campaign send history search — admin panel
~ 3   : arrayindexoutofboundsexception in panel language translation import — eu
```
