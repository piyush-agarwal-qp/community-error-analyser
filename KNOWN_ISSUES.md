# Known Recurring Issues

Track errors that appear in multiple weekly reports. Update this file after each report is generated.

**How to use:**
- Add an issue here when it appears in **2 or more consecutive weeks**.
- Update **Last seen** each week it recurs.
- Mark as **Resolved** (with date) when it disappears for a full week.
- Reference the `error_report_YYYY-MM-DD.md` file where it was first and last seen.

---

## Active Issues

### KI-001 · GetTaskDetails AJS Failure — US Production
- **Severity:** Critical
- **First seen:** 2026-06-04 (`error_report_2026-06-04.md`, cluster 1)
- **Last seen:** 2026-06-04
- **Count trend:** 438 (week of May 29–Jun 4) → 0 (week of Jun 19–25)
- **Affected:** All US qprun nodes (1–11), all Communities tenants
- **Exception:** `java.lang.reflect.InvocationTargetException` in `PortalDashBoardAJSHandler-GetTaskDetails`
- **Status:** Possibly resolved — not seen in Jun 19–25 data. Confirm after next week.
- **Notes:** Gap week Jun 5–18 not analysed. Needs `.getCause()` pulled from full Resin log if it recurs.

---

### KI-002 · GetSurveyDetails AJS Failure — EU Production
- **Severity:** High
- **First seen:** 2026-06-04 (`error_report_2026-06-04.md`, cluster 2)
- **Last seen:** 2026-06-04
- **Count trend:** 15 (week of May 29–Jun 4) → 0 (week of Jun 19–25)
- **Affected:** pveuqprun2, pveuqprun4 — onepoll EU tenants
- **Exception:** `java.lang.reflect.InvocationTargetException` in `PortalDashBoardAJSHandler-GetSurveyDetails`
- **Status:** Possibly resolved — not seen in Jun 19–25 data. Confirm after next week.
- **Notes:** A new AJSServlet InvocationTargetException appeared in EU this week (cluster 2, panel.do referrer) — may be related but different handler.

---

### KI-003 · Panel Language Translation Import Failure — EU
- **Severity:** Medium
- **First seen:** 2026-06-04 (`error_report_2026-06-04.md`, cluster 6)
- **Last seen:** 2026-06-25 (`error_report_2026-06-25.md`, cluster 7)
- **Count trend:** 3 (week of May 29–Jun 4) → 2 (week of Jun 19–25)
- **Affected:** pveuadminapp1 — user `muzaffar.quraishi+eu@questionpro.com`
- **Exception:** `ArrayIndexOutOfBoundsException: Index 164 out of bounds for length 164` in `com.surveyconsole.micropanel.language.PanelTranslation`
- **Status:** Open — recurring second consecutive week
- **Notes:** Off-by-one in PanelTranslation import loop. Referrer: `editLanguage.do?mode=importTranslation`. Not fixed yet.

---

### KI-004 · ConcurrentModificationException — GetAllSurveys (Portal)
- **Severity:** High
- **First seen:** 2026-08-07 (`reports/2026-08-07_to_2026-08-13/error_report.md`, cluster 1)
- **Last seen:** 2026-08-12
- **Count trend:** 14 (week of Aug 7–13)
- **Affected:** EU+US portal — pveuqprun2/3/4, pvweb1
- **Exception:** `java.util.ConcurrentModificationException` in `PanelLogSurveyFetcher.getCachedSurveyIds` → `PortalSurveyAJSHandler.apiGetAllSurveys`
- **Status:** Open — first seen, watching
- **Notes:** Unsynchronized collection mutated during iteration in the panel-log survey-ID cache path. Referer `showMemberSurveys.do`.

---

### KI-005 · VerifyDomainAuthenticationAction NPE on null EmailDomain
- **Severity:** Medium
- **First seen:** 2026-08-09 (`reports/2026-08-07_to_2026-08-13/error_report.md`, clusters 2 + 6)
- **Last seen:** 2026-08-09
- **Count trend:** 12 (8 + 4) (week of Aug 7–13)
- **Affected:** US — pvweb2
- **Exception:** `java.lang.NullPointerException` in `VerifyDomainAuthenticationAction.getAjaxResponse` / `.addSuccessOrErrorMessage` — calls `EmailDomain.isVerifiedEmailDomain()` / `.getID()` on a null `emailDomain`
- **Status:** Open — first seen, watching
- **Notes:** Same action class + method, two call sites failing on the same null lookup — consolidated per error-report skill's action-class+exception grouping rule (was reported as 2 separate clusters by Metabase hash). Endpoint `/a/verifyDomainAuthentication.do`.

---

### KI-006 · KickStartServices Connection Refused — exportPanelHealthDashboardPDF
- **Severity:** Medium
- **First seen:** 2026-08-11 (`reports/2026-08-07_to_2026-08-13/error_report.md`, cluster 3)
- **Last seen:** 2026-08-11
- **Count trend:** 4 (week of Aug 7–13)
- **Affected:** US panel — pvweb1
- **Exception:** `java.net.ConnectException: Connection refused` in `KickStartServices.startProcessingItem` → `DownloadKickStartServiceHandler.callKickStartService`
- **Status:** Open — first seen, watching
- **Notes:** Endpoint `/a/exportPanelHealthDashboardPDF.do`. Downstream service refusing connection — check if pvdata/kickstart service was down/restarting 2026-08-11.

---

### KI-007 · QPointLogHelper Insert Failure — editPanelMember (EU)
- **Severity:** Medium
- **First seen:** 2026-08-11 (`reports/2026-08-07_to_2026-08-13/error_report.md`, clusters 4 + 8)
- **Last seen:** 2026-08-11
- **Count trend:** 6 (4 + 2) (week of Aug 7–13)
- **Affected:** EU panel — pveuqpweb4, pveuadminapp1
- **Exception:** `UserPreparedStatement[SpyPreparedStatement[null]]` in `QPointLogHelper.insertData` → `PanelMember.addQPointLog`
- **Status:** Open — first seen, watching
- **Notes:** Same action class/method across two EU hosts — consolidated per skill's cross-host rule. Endpoint `/a/editPanelMember.do`. Root cause string is generic (SpyPreparedStatement wrapper) — needs full Resin log `.getCause()` to see the actual SQL failure.

---

### KI-008 · XmlRpcException — Failed to read servers response (pvdata)
- **Severity:** Medium
- **First seen:** 2026-08-08 (`reports/2026-08-07_to_2026-08-13/error_report.md`, clusters 5 + 12)
- **Last seen:** 2026-08-10
- **Count trend:** 6 (4 + 2) (week of Aug 7–13)
- **Affected:** US other — pvweb1, pvweb2
- **Exception:** `org.apache.xmlrpc.XmlRpcException: Failed to read servers response` in `KickStartServices.getSurveyResponseCountByDataSource` → `ListSurveysAction$1.runLogged`
- **Status:** Open — first seen, watching
- **Notes:** Consolidated two clusters — hostnames differ only as `pvdata.questionpro.net` vs `pv-data.questionpro.net` (same target, cosmetic hostname variance), same action class + exception. XML-RPC call to data-source service timing out/failing intermittently.

---

### KI-009 · IndexOutOfBoundsException — loadResponse TEXTLoader
- **Severity:** Low
- **First seen:** 2026-08-11 (`reports/2026-08-07_to_2026-08-13/error_report.md`, cluster 7)
- **Last seen:** 2026-08-11
- **Count trend:** 2 (week of Aug 7–13)
- **Affected:** US other — qpweb3
- **Exception:** `java.lang.IndexOutOfBoundsException: Index 0 out of bounds for length 0` in `TEXTLoader.loadInternal` → `ResponseLoader.loadData`
- **Status:** Open — first seen, watching
- **Notes:** Endpoint `/a/loadResponse.do`. Likely a response with an empty/missing text-question answer set.

---

### KI-010 · NPE PanelMember.getID() — showPanelUserReport (EU)
- **Severity:** Low
- **First seen:** 2026-08-10 (`reports/2026-08-07_to_2026-08-13/error_report.md`, cluster 9)
- **Last seen:** 2026-08-10
- **Count trend:** 2 (week of Aug 7–13)
- **Affected:** EU panel — pveuqpweb4
- **Exception:** `java.lang.NullPointerException: Cannot invoke "com.surveyconsole.micropanel.PanelMember.getID()"` — stack dominated by generic filter chain (MDCFilter/FilterAdapter/IntercomAppFilter), no deeper `com.surveyconsole` business-logic frame captured
- **Status:** Open — first seen, watching
- **Confidence:** Medium — action class is the filter chain only; true call site not visible in the truncated trace captured here
- **Notes:** Endpoint `/a/showPanelUserReport.do`. If this recurs, pull the full Resin log for the actual `PanelMember` lookup site.

---

### KI-011 · SQL Syntax Error — showPanelSegment totalActiveCount (EU)
- **Severity:** Low
- **First seen:** 2026-08-10 (`reports/2026-08-07_to_2026-08-13/error_report.md`, cluster 10)
- **Last seen:** 2026-08-10
- **Count trend:** 2 (week of Aug 7–13)
- **Affected:** EU other — pveuqprun4
- **Exception:** MySQL syntax error near `)) AND pm.last_activity_ts > '1970-01-01'` in `Panel.getPanelMemberCount` → `CompositePanelMemberFilterCriteria.getTotalActiveMemberCount`
- **Status:** Open — first seen, watching
- **Notes:** Endpoint `/a/showPanelSegment.do?mode=totalActiveCount`. Looks like a malformed dynamic WHERE-clause builder for a specific segment filter combination — likely an empty/edge-case filter producing a dangling `AND`.

---

### KI-012 · BulkProfileInsertProcessor NPE — inviteUsers (QA)
- **Severity:** Low (QA — non-production)
- **First seen:** 2026-08-09 (`reports/2026-08-07_to_2026-08-13/error_report.md`, cluster 11)
- **Last seen:** 2026-08-09
- **Count trend:** 2 (week of Aug 7–13)
- **Affected:** QA panel — qa1.du (aeqa)
- **Exception:** `java.lang.NullPointerException: Cannot invoke "com.surveyconsole.micropanel.PanelMemberFieldValues.hasCustomVariables()"` in `BulkProfileInsertProcessor.prepareInsert`
- **Status:** Open — first seen, watching (non-prod)
- **Notes:** Params look like a Selenium test payload — may just be automated-test noise rather than a real bug. Watch for recurrence in prod QA runs before prioritizing.

---

### KI-013 · NPE User.getBuildHeader() — showPanelHealthDashboard
- **Severity:** Low
- **First seen:** 2026-08-08 (`reports/2026-08-07_to_2026-08-13/error_report.md`, cluster 13)
- **Last seen:** 2026-08-08
- **Count trend:** 2 (week of Aug 7–13)
- **Affected:** US other — qpweb2
- **Exception:** `java.lang.NullPointerException: Cannot invoke "com.surveyconsole.user.User.getBuildHeader()"` — stack dominated by generic filter chain, no deeper business-logic frame captured
- **Status:** Open — first seen, watching
- **Confidence:** Medium — same truncation issue as KI-010; deepest captured frame is filter plumbing, not the real call site
- **Notes:** Endpoint `/a/showPanelHealthDashboard.do`. Session/User object appears null/expired at header-build time — check if tied to session timeout.

---

## Resolved Issues

*(none yet)*

---

## Issue Template

```
### KI-NNN · [Short Title]
- **Severity:** Critical / High / Medium / Low
- **First seen:** YYYY-MM-DD (`error_report_YYYY-MM-DD.md`, cluster N)
- **Last seen:** YYYY-MM-DD
- **Count trend:** N (week N), N (week N+1)
- **Affected:** [hosts / region / customers]
- **Exception:** [exception class + call site]
- **Status:** Open / Resolved (YYYY-MM-DD)
- **Notes:** [anything useful for the next person looking at this]
```
