# weekly error report — 19 jun to 25 jun 2026

**date range:** 2026-06-19 → 2026-06-25
**total errors:** 65
**clusters:** 15

---

## summary table

| # | severity | error type | count | dc | side |
|---|----------|------------|-------|----|------|
| 1 | high | XmlRpcException 502 — ListSurveysAction (bg thread) | 15 | EU | other |
| 2 | high | InvocationTargetException — AJSServlet (panel.do) | 14 | EU+QA | panel |
| 3 | medium | NoSuchElementException — renameUserFile | 7 | QA+US | other |
| 4 | medium | NullPointerException — PanelMember.getSelectedLanguage (error.jsp) | 6 | US | panel |
| 5 | medium | SQL syntax error — updatePanelMemberProfile | 5 | EU | portal |
| 6 | medium | InvocationTargetException — AJSServlet (showDiscussionModeration) | 4 | EU | panel |
| 7 | medium | ArrayIndexOutOfBoundsException — panelLanguageTranslationImport | 2 | EU | panel |
| 8 | medium | IndexOutOfBoundsException — loadResponse | 2 | US | other |
| 9 | low | NullPointerException — takeProfileSurvey | 4 | QA | other |
| 10 | low | UnsupportedOperationException — stopBroadcastProcess | 1 | EU | panel |
| 11 | low | Duplicate entry — editPanelMember | 1 | US | panel |
| 12 | low | SocketTimeoutException — notification progress | 1 | US | other |
| 13 | low | NullPointerException — email compose (no session) | 1 | US | other |
| 14 | low | Duplicate entry — inviteUsers | 1 | QA | panel |
| 15 | low | NullPointerException — inviteUsers PanelMemberField | 1 | QA | panel |

---

## dc & side breakdown

| dc | total | patterns | repetitive | one-offs | portal | panel | other |
|----|-------|----------|-----------|---------|--------|-------|-------|
| us | 13 | 6 | 10 | 3 | 0 | 3 | 10 |
| eu | 39 | 10 | 33 | 6 | 9 | 7 | 23 |
| qa | 13 | 5 | 11 | 2 | 0 | 2 | 11 |

- **repetitive** = errors belonging to a hash seen >1 time (recurring bug)
- **one-offs** = hash seen exactly once (new or transient)
- **portal** = member-facing | **panel** = admin-facing

---

## cluster details

### 1. XmlRpcException 502 — ListSurveysAction background thread *(high, 15 errors)*

**root cause:** eu-data.questionpro.net returning HTTP 502, causing all ListSurveysAction background thread calls to fail across EU prod nodes.

**summary:** EU data service (`eu-data.questionpro.net/a/xmlrpc`) was returning 502 during the week. ListSurveysAction calls this via XML-RPC in a background thread; all EU app nodes (pveuadminapp1, pveuqprun4, pveuqpweb1–4) hit the failure. Likely a transient EU data service outage or degradation. Check eu-data service health and XML-RPC endpoint availability.

**stack trace:**
```
org.apache.xmlrpc.XmlRpcException: Failed to create input stream: Server returned HTTP response code: 502 for URL: http://eu-data.questionpro.net/a/xmlrpc
    at org.apache.xmlrpc.client.XmlRpcSunHttpTransport.getInputStream(XmlRpcSunHttpTransport.java:65)
    at org.apache.xmlrpc.client.XmlRpcStreamTransport.sendRequest(XmlRpcStreamTransport.java:141)
    at org.apache.xmlrpc.client.XmlRpcHttpTransport.sendRequest(XmlRpcHttpTransport.java:94)
```

**dc / side:** eu · other (background thread — no user-facing URL)
**affected endpoints:** (background thread — no HTTP endpoint)
**affected hosts:** pveuadminapp1, pveuqprun4, pveuqpweb1, pveuqpweb2, pveuqpweb3, pveuqpweb4
**error ids (sample):** 519700, 519716, 519740 *(15 total)*

---

### 2. InvocationTargetException — AJSServlet from panel.do *(high, 14 errors)*

**root cause:** AJSServlet call initiated from panel dashboard (`panel.do`) throws InvocationTargetException; real cause wrapped — Metabase log truncates before getCause().

**summary:** 13 EU prod rows + some QA rows. Referrer is `fivebargatefarming.questionpro.eu/a/panel.do` — a real EU customer panel. The AJS action is unknown (log truncated). InvocationTargetException means the real error is one level deeper; must pull full trace from Resin logs for `pveuadminapp1` / `pveuqprun*` to identify root cause. May be related to KI-002 pattern (AJSServlet wrapped exception in EU).

**stack trace:**
```
java.lang.reflect.InvocationTargetException
    at java.base/jdk.internal.reflect.DirectMethodHandle...
    [wrapped — check getCause() in Resin logs]
```

**dc / side:** eu · panel
**affected endpoints:** AJSServlet (action unknown — log truncated)
**affected hosts:** pveuadminapp1, pveuqprun1, pveuqprun3, pveuqprun4, qaweb2
**error ids (sample):** 511277, 519643, 521964 *(14 total)*

---

### 3. NoSuchElementException — renameUserFile *(medium, 7 errors)*

**root cause:** `Optional.get()` called without `isPresent()` check in rename file flow — fails when the file entry has no value.

**summary:** Triggered by `payal.pandey@questionpro.com` on both QA (qaweb2) and US prod (pvqpadminapp1) via showImageLibrary. Referrer: `qa-priority.questionpro.com/a/showImageLibrary.do`. The rename action crashes with `java.util.NoSuchElementException: No value present` from `Optional.get()`. Fix: guard with `isPresent()` or use `orElseThrow()` with a meaningful message.

**stack trace:**
```
java.util.NoSuchElementException: No value present
    at java.base/java.util.Optional.get(Optional.java:143)
    [/a/renameUserFile.do][mode=update&userFileID=4204224&...]
```

**dc / side:** us+qa · other (image library — admin panel)
**affected endpoints:** /a/renameUserFile.do
**affected hosts:** pvqpadminapp1, qaweb2
**error ids (sample):** 521111, 521116, 521118 *(7 total)*

---

### 4. NullPointerException — PanelMember.getSelectedLanguage on error.jsp *(medium, 6 errors)*

**root cause:** `member` object is null when `error.jsp` tries to call `PanelMember.getSelectedLanguage()` — error page itself crashes when member session is absent.

**summary:** All 6 errors from `pvqpadminapp1` (US prod admin node), user `payal.pandey@questionpro.com`, referrer `showQPointInventory.do`. The error JSP is rendered when a prior action fails, but then NPEs because member is null — double-fault scenario. Fix: null-check member before calling `getSelectedLanguage()` in error.jsp rendering path.

**stack trace:**
```
java.lang.NullPointerException: Cannot invoke "com.surveyconsole.micropanel.PanelMember.getSelectedLanguage()" because "member" is null
    at com.surveyconsole.micropanel.re...
JSP Error: [/a/jsp/includes/error.jsp][ajax=true&engine=dojo]
```

**dc / side:** us · panel
**affected endpoints:** /a/jsp/includes/error.jsp (triggered from showQPointInventory flow)
**affected hosts:** pvqpadminapp1
**error ids (sample):** 564124, 564125, 564127 *(6 total)*

---

### 5. SQL syntax error — updatePanelMemberProfile *(medium, 5 errors)*

**root cause:** malformed SQL generated by `updatePanelMemberProfile.do` when processing EU panel member custom field values — likely unescaped special characters or invalid date sentinel (-1) being written into SQL directly.

**summary:** 5 errors across pveuqpweb1 and pveuqpweb4; different hashes due to slightly different field values per request but same exception type and endpoint. Members unable to save profile updates on the EU panel. Custom date fields with `-1` sentinel values (Day=-1, month=-1, year=-1) likely not handled correctly in the SQL builder. Fix: validate/sanitize custom field values before SQL construction; use PreparedStatement binding for all custom field params.

**stack trace:**
```
You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version
    [/a/updatePanelMemberProfile.do][cf_25638_year=-1&...]
```

**dc / side:** eu · portal
**affected endpoints:** /a/updatePanelMemberProfile.do
**affected hosts:** pveuqpweb1, pveuqpweb4
**error ids (sample):** 494739, 544300, 544303 *(5 total)*

---

### 6. InvocationTargetException — AJSServlet from showDiscussionModeration *(medium, 4 errors)*

**root cause:** AJSServlet action called from discussion moderation page throws InvocationTargetException; real cause wrapped — check getCause() in Resin logs.

**summary:** 4 consecutive errors on pveuqpweb2 (IDs 564176–564179), EU prod, German user (cf-ipcountry: DE). Referrer: `eu.questionpro.com/a/showDiscussionModeration.do`. All 4 hit the same node in rapid succession suggesting a specific discussion action is broken for this user's session or data. Pull getCause() from Resin logs on pveuqpweb2.

**stack trace:**
```
java.lang.reflect.InvocationTargetException
    at java.base/jdk.internal.reflect.DirectMethodHandle...
    [wrapped — check getCause() in Resin logs]
AJSServlet : {"headers":{"referer":"https://eu.questionpro.com/a/showDiscussionModeration.do",...}}
```

**dc / side:** eu · panel
**affected endpoints:** AJSServlet (action unknown — log truncated)
**affected hosts:** pveuqpweb2
**error ids (sample):** 564176, 564177, 564178 *(4 total)*

---

### 7. ArrayIndexOutOfBoundsException — panelLanguageTranslationImport *(medium, 2 errors — KI-003 recurrence)*

**root cause:** off-by-one in PanelTranslation import loop — index 164 out of bounds for length 164 (zero-indexed, iterates one step too far).

**summary:** recurrence of KI-003 (first seen week of May 29–Jun 4, count=3). Same endpoint, same EU admin host (pveuadminapp1), user `muzaffar.quraishi+eu@questionpro.com`, referrer `editLanguage.do`. Count dropped from 3 → 2 but issue persists. Bug is an unguarded loop boundary in `com.surveyconsole.micropanel.language.PanelTranslation`.

**stack trace:**
```
java.lang.ArrayIndexOutOfBoundsException: Index 164 out of bounds for length 164
    at com.surveyconsole.micropanel...
[/a/panelLanguageTranslationImport.do][mode=import]
```

**dc / side:** eu · panel
**affected endpoints:** /a/panelLanguageTranslationImport.do
**affected hosts:** pveuadminapp1
**error ids (sample):** 523259, 523315 *(2 total)*

---

### 8. IndexOutOfBoundsException — loadResponse *(medium, 2 errors)*

**root cause:** response set load attempts to read index 0 from an empty list — likely a deleted or inaccessible response.

**summary:** 2 errors on qpweb1 (US prod), external customer `thomas.conrad@salesfactory.com`, referrer `frame.do?mode=viewIndividual`. Viewing individual survey responses fails with `IndexOutOfBoundsException: Index 0 out of bounds for length 0`. The response set (ID 148363643) may have been deleted or the user lacks access. Fix: guard the list access with an empty-check and return a proper 404/permission error.

**stack trace:**
```
java.lang.IndexOutOfBoundsException: Index 0 out of bounds for length 0
    at java.base/java.util...
[/a/loadResponse.do][surveyID=13323446&responseSetID=148363643]
```

**dc / side:** us · other
**affected endpoints:** /a/loadResponse.do
**affected hosts:** qpweb1
**error ids (sample):** 525151, 525158 *(2 total)*

---

### 9. NullPointerException — takeProfileSurvey *(low, 4 errors — QA only)*

**root cause:** `RunSurveyShell.getPanelM...` returns null — panel member context not set when continuing a profile survey with empty/invalid date field values.

**stack trace:**
```
java.lang.NullPointerException: Cannot invoke "com.surveyconsole.run.RunSurveyShell.getPanelM..."
[/a/takeProfileSurvey.do][mode=continue&cf_466054_year=-1&...]
```

**dc / side:** qa · other
**affected hosts:** qaweb2
**error ids (sample):** 544298, 544357, 544369 *(4 total)*

---

### 10. UnsupportedOperationException — stopBroadcastProcess *(low, 1 error)*

**root cause:** `Thread.stop()` called in `LongProcessHandler.stopProcess()` — deprecated since Java 1.2, throws `UnsupportedOperationException` in Java 11+.

**stack trace:**
```
java.lang.UnsupportedOperationException
    at java.base/java.lang.Thread.stop(Thread.java:1667)
    at com.surveyconsole.batch.LongProcessHandler.stopProcess(...)
[/a/stopBroadcastProcess.do][id=1604333467]
```

**dc / side:** eu · panel
**affected hosts:** pveuqpweb3
**error ids (sample):** 543290 *(1 total)*

---

### 11. Duplicate entry — editPanelMember *(low, 1 error)*

**root cause:** DB unique constraint violation when saving edited panel member — duplicate on a composite key.

**stack trace:**
```
Duplicate entry '149770-80439514-80439514-...'
[/a/editPanelMember.do][userAction=save&emailAddress=metmadison752@outlook.com&...]
```

**dc / side:** us · panel
**affected hosts:** qpweb1
**error ids (sample):** 525161 *(1 total)*

---

### 12. SocketTimeoutException — notification progress *(low, 1 error)*

**root cause:** outbound SSL socket read timed out while notifying progress — downstream service too slow.

**stack trace:**
```
java.net.SocketTimeoutException: Read timed out
    at java.base/sun.nio.ch.NioSocketImpl.timedRead(...)
Error In Processing Item While_Notifying Progress
```

**dc / side:** us · other
**affected hosts:** qpweb2
**error ids (sample):** 569482 *(1 total)*

---

### 13. NullPointerException — email compose (expired session) *(low, 1 error)*

**root cause:** `User` object null in session when `fromEmailDropDown.jsp` renders — session expired or invalid.

**stack trace:**
```
java.lang.NullPointerException: Cannot invoke "com.surveyconsole.user.User.hasSmtpSettings()" because "<local40>" is null
    at _jsp._survey._sendsurvey._compose._email._fromEmailDropDown__jsp._jspService(...:1748)
JSP Error: No User Object in Session Referrer [null]
```

**dc / side:** us · other
**affected hosts:** qpweb3
**error ids (sample):** 570128 *(1 total)*

---

### 14. Duplicate entry — inviteUsers *(low, 1 error — QA only)*

**root cause:** selenium test re-invites an already-existing member — DB unique constraint on `inviteUsers`.

**dc / side:** qa · panel
**affected hosts:** qa11
**error ids (sample):** 515188 *(1 total)*

---

### 15. NullPointerException — inviteUsers PanelMemberField *(low, 1 error — QA only)*

**root cause:** `PanelMemberFieldV...` null during invite flow on QA SA environment.

**dc / side:** qa · panel
**affected hosts:** saqaapp1
**error ids (sample):** 570964 *(1 total)*

---

## recommended actions

| priority | action |
|----------|--------|
| p1 | check eu-data.questionpro.net xmlrpc health; confirm if 502s were transient (cluster 1) |
| p1 | pull getCause() from Resin logs on pveuadminapp1/pveuqprun* and pveuqpweb2 for clusters 2 and 6 |
| p2 | fix SQL syntax error in updatePanelMemberProfile — use PreparedStatement binding for custom field values; guard date sentinels (-1) (cluster 5) |
| p2 | null-check member before getSelectedLanguage() in error.jsp (cluster 4) |
| p2 | fix Optional.get() in renameUserFile flow — add isPresent() guard (cluster 3) |
| p2 | fix LongProcessHandler.stopProcess() — replace Thread.stop() with interrupt-based shutdown (cluster 10) |
| p3 | fix panelLanguageTranslationImport loop boundary — off-by-one in PanelTranslation (KI-003, cluster 7) |
| p3 | guard loadResponse list access — return 404 when response set empty or inaccessible (cluster 8) |

---

## pdm report

```
65 errors logged (2026-06-19 → 2026-06-25)

us dc — 2 panel, 0 portal
eu dc — 4 panel, 1 portal
qa    — 2 panel, 0 portal  (non-production)
```

counts = distinct error types (clusters), not total rows.
portal = member-facing. panel = admin-facing.

---

## engineering update

```
65 errors | panel-2, portal-0 (us) | panel-4, portal-1 (eu)

~ 15 : eu — listsurveys background thread — xmlrpc 502 from eu-data.questionpro.net — eu survey listing broken
~ 14 : eu+qa — ajsservlet invocationtargetexception (panel.do) — real cause wrapped — pull getcause() from resin logs
~ 7  : qa+us — renameUserFile — nosuchelementexception optional.get() — rename fails when file entry has no value
~ 6  : us — error.jsp double-fault — nullpointerexception panelmember.getselectedlanguage() member=null
~ 5  : eu — updatepanelmemberprofile — sql syntax error — profile save blocked for eu members (date sentinels -1 unescaped)
```
