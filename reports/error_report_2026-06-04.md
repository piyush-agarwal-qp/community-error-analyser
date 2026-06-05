# Weekly Error Report — 29 May to 4 June 2026

**Date range:** 2026-05-29 → 2026-06-04  
**Total errors:** 500 (query limit hit; actual volume likely higher)  
**Clusters:** 11

---

## Summary Table

| # | Severity | Error Type | Count | Hosts |
|---|----------|-----------|-------|-------|
| 1 | Critical | GetTaskDetails AJS failure — US production | 438 | 11 |
| 2 | High | GetSurveyDetails AJS failure — EU production | 15 | 2 |
| 3 | Medium | Campaign Batch Search NPE | 7 | 1 |
| 4 | Medium | Zoom API User Creation 400 | 6 | 1 |
| 5 | Medium | loadResponse Index Out of Bounds | 4 | 1 |
| 6 | Medium | Panel Language Translation Import | 3 | 2 |
| 7 | Low | Portal Dashboard AJS — QA | 18 | 2 |
| 8 | Low | Twitter / X Sign-In API Failures | 3 | 2 |
| 9 | Low | JSP / Portal Page Null Pointer | 3 | 2 |
| 10 | Low | SMTP / Email Config Errors | 2 | 2 |
| 11 | Low | QA Selenium SQL Syntax Error | 1 | 1 |

---

## DC & Side Breakdown

| DC | Total | Error Patterns | Repetitive | One-offs | Portal-side | Panel-side | Other |
|----|-------|---------------|-----------|---------|------------|-----------|-------|
| US | 453 | 7 (3 repeated, 4 unique) | 449 | 4 | 439 | 10 | 4 |
| EU | 30 | 8 (5 repeated, 3 unique) | 27 | 3 | 11 | 12 | 7 |
| QA | 17 | 3 (2 repeated, 1 unique) | 16 | 1 | 12 | 5 | 0 |
| **Total** | **500** | **11** | **492** | **8** | **462** | **27** | **11** |

**Columns:**
- **Error Patterns** — distinct error hashes in the DC. *Repeated* = same hash hit multiple times (an ongoing bug). *Unique* = hash seen once (isolated incident or new issue).
- **Repetitive** — error rows that belong to a repeated pattern (i.e., a known recurring bug firing again).
- **One-offs** — error rows with a hash seen exactly once in the DC (new or transient).
- **Portal-side** — errors triggered from the member-facing portal (dashboard, surveys tab, rewards, member account). Classified by `PortalDashBoardAJSHandler` URL or referrer containing `showPanelMemberDashBoard` / `showMemberSurveys` / `showRewardTab` / `showMemberAccount`.
- **Panel-side** — errors triggered from the admin panel management side (user reports, campaign search, language import, moderation, invites). Classified by referrer containing `showPanelUserReport` / `searchSurveyCampaignBatch` / `panelLanguageTranslationImport` / `showDiscussionModeration` / `showPanelProjectHistory` etc.

**Reading this week's data:**
- The US DC is overwhelmingly portal-side (439/453) — the `GetTaskDetails` regression is purely a member dashboard issue.
- The EU DC is more balanced (11 portal / 12 panel / 7 other) — diverse smaller issues across admin and member paths.
- QA skews portal (12/17) because the same AJS regression is reproduced there.

---

## Cluster Details

---

### 1. GetTaskDetails AJS Failure — US Production *(Critical, 438 errors)*

**Root cause:** `PortalDashBoardAJSHandler-GetTaskDetails` throws `java.lang.reflect.InvocationTargetException` — the handler method dispatched by AJSServlet is failing when panel members load their task list on the dashboard.

**Summary:** All 11 US production `qprun` nodes are affected, covering all Communities tenants (survanta, energizeridealab, onepoll, etc.). This is the single largest failure this week at 87 % of all captured errors. The `InvocationTargetException` wraps the real cause — it is truncated in the Metabase log. The next step is to pull the full stack from the Resin log (`make logs`) and call `.getCause()` on the exception to find the underlying NPE or missing-data failure.

**Affected endpoint:** `survey-angular.panel.portal.PortalDashBoardAJSHandler-GetTaskDetails`  
**Affected hosts:** qprun1, qprun2, qprun3, qprun4, qprun5, qprun6, qprun7, qprun8, qprun9, qprun10, qprun11

**Stack trace:**
```
java.lang.reflect.InvocationTargetException
    at java.base/jdk.internal.reflect.DirectMethodHandleAccessor.invoke(...)
    [real cause wrapped — check Resin logs for getCause() output]
```

**Error IDs (all 438):**
49417, 50408, 51007, 51544, 51548, 52803, 53056, 53059, 53078, 53087, 54053, 54056, 55846, 55850, 55873, 55887, 55889, 55980, 56085, 56985, 57632, 58499, 58512, 58538, 58552, 58565, 58570, 58572, 58573, 58602, 58627, 58653, 58694, 58695, 58709, 58747, 58800, 58962, 59004, 59144, 59155, 59277, 59330, 59371, 59378, 59522, 59531, 59593, 59648, 60037, 60055, 60676, 61000, 61123, 61655, 61833, 61987, 62008, 62086, 62129, 62208, 62298, 62873, 62875, 62882, 62884, 62931, 62938, 62949, 62953, 62977, 63741, 64032, 64278, 65047, 65052, 65057, 65419, 65471, 66776, 67823, 67871, 67881, 67886, 67902, 67940, 67960, 67968, 67969, 68040, 68083, 68086, 68120, 68169, 68493, 68496, 69187, 69193, 69805, 70476, 70796, 71195, 71218, 71333, 71377, 71378, 71389, 73539, 73661, 73719, 73986, 74010, 74016, 74032, 74034, 74056, 74057, 74181, 74186, 74894, 74896, 75196, 75576, 75580, 75582, 75829, 76113, 76275, 76550, 76764, 76943, 76988, 77224, 77229, 77233, 77283, 77320, 77321, 77413, 77766, 77947, 78059, 78062, 78067, 80482, 80486, 80497, 83470, 83494, 83544, 84065, 84071, 84075, 84080, 86222, 86223, 86289, 86461, 86912, 87035, 87043, 87231, 87403, 87680, 88789, 89254, 89831, 89833, 89836, 89860, 92062, 92112, 92113, 92178, 92514, 92850, 92969, 93472, 94024, 94153, 94236, 94370, 94998, 95705, 95847, 95852, 96309, 96311, 96343, 96858, 96946, 96966, 96986, 97273, 97294, 97569, 97571, 99473, 99574, 99956, 99961, 100304, 101523, 102559, 102682, 103064, 103072, 103081, 103613, 103621, 103631, 103723, 104378, 104676, 104770, 105532, 105679, 105739, 106126, 106210, 106618, 107636, 107977, 108338, 109459, 109480, 110086, 110231, 110280, 110290, 110327, 110337, 110411, 110479, 110482, 110487, 110502, 110576, 110580, 110964, 111090, 111124, 111167, 111172, 111180, 111189, 111191, 111310, 111456, 111461, 111463, 111474, 111626, 111755, 111807, 111825, 111879, 111886, 112056, 112109, 112336, 112352, 112868, 112883, 113086, 113089, 113103, 113131, 113158, 113186, 113187, 113188, 113235, 113248, 113292, 113341, 113838, 113980, 114005, 114009, 114013, 114116, 114141, 114149, 114166, 114389, 114406, 114503, 114725, 114755, 114759, 114884, 114898, 115174, 115265, 115613, 115616, 115631, 115869, 115877, 116006, 116505, 116612, 116615, 116616, 117168, 118339, 118383, 118574, 119690, 119705, 119752, 119777, 119835, 119836, 119841, 120260, 120269, 121574, 121586, 121637, 121646, 121657, 121663, 122627, 123027, 129201, 129206, 129217, 129424, 129730, 129742, 130429, 131148, 131167, 131168, 131796, 131803, 132612, 133383, 133486, 133503, 134242, 134429, 134492, 134507, 134510, 134589, 134687, 134751, 135549, 135553, 136303, 137135, 137708, 137724, 138011, 139262, 139629, 139634, 140070, 140225, 140956, 140960, 141124, 141346, 141353, 141581, 141592, 141601, 141865, 141872, 143849, 144160, 144162, 145013, 145533, 145853, 146302, 147381, 148129, 151036, 151277, 151490, 153271, 153467, 154549, 154965, 155995, 157519, 157678, 158469, 158490, 158684, 158768, 159048, 161244, 162379, 162391, 162399, 162876, 162879, 163304, 164013, 164585, 164597, 164599, 164639, 164646, 164672, 164698, 164701, 164704, 164708, 164715, 164716, 164720, 164721, 164722, 164723, 164987, 165029, 165038, 165040, 165045, 165182, 165190, 165222, 165224, 165992, 166404, 166425, 166820, 166991, 166994, 169044, 169100, 169404

---

### 2. GetSurveyDetails AJS Failure — EU Production *(High, 15 errors)*

**Root cause:** Same `InvocationTargetException` pattern as cluster 1, but in `PortalDashBoardAJSHandler-GetSurveyDetails` — members on EU portals (onepolluk.questionpro.eu) cannot load their survey list from the dashboard.

**Summary:** Confined to EU nodes (pveuqprun2, pveuqprun4). Though lower count than cluster 1, this is a separate handler method and likely a separate code path failing. It may share the same underlying root cause, or it may be an independent bug introduced in the same release. Should be investigated alongside cluster 1 but tracked separately.

**Affected endpoint:** `survey-angular.panel.portal.PortalDashBoardAJSHandler-GetSurveyDetails`  
**Affected hosts:** pveuqprun2.questionpro.net, pveuqprun4.questionpro.net (+ qa11)

**Stack trace:**
```
java.lang.reflect.InvocationTargetException
    at java.base/jdk.internal.reflect.DirectMethodHandleAccessor.invoke(...)
    [real cause wrapped — check Resin logs on pveuqprun for getCause() output]
```

**Error IDs (all 15):**
55836, 55837, 57096, 57097, 57163, 57164, 89980, 89981, 90019, 90020, 111509, 127354, 127592, 134869, 152071

---

### 3. Campaign Batch Search NPE *(Medium, 7 errors)*

**Root cause:** `java.lang.NullPointerException` at `Objects.requireNonNull → TreeMap.put` in `/a/searchSurveyCampaignBatch.do` — a null value is being inserted into a sorted map during email-subject search, crashing the request.

**Summary:** All 7 occurrences happened in rapid succession from the same admin user (`georgia.fitzsimons@norstella.com`) on the admin server. The campaign batch search page is broken for this customer; they cannot search their campaign history. A null guard before the `TreeMap.put` call would fix this.

**Stack trace:**
```
java.lang.NullPointerException
    at java.base/java.util.Objects.requireNonNull(Objects.java:233)
    at java.base/java.util.TreeMap.put(TreeMap.java:844)
    [origin: campaign batch search, sorting/indexing results into TreeMap]
```

**Affected endpoints:** `/a/searchSurveyCampaignBatch.do`  
**Affected hosts:** pvqpadminapp2.questionpro.net  
**Error IDs:** 102596, 102598, 102599, 102600, 102602, 102603, 102604

---

### 4. Zoom API User Creation 400 *(Medium, 6 errors)*

**Root cause:** `java.io.IOException: Server returned HTTP response code: 400` from `https://api.zoom.us/v2/users` — Zoom is rejecting the create-user payload as invalid.

**Summary:** Six consecutive failures all from the EU admin server, indicating a systematic problem with the request payload being sent to Zoom (likely a malformed or missing required field). The feature for auto-provisioning Zoom users in Communities panels is non-functional on the EU region. Inspecting the JSON body sent to Zoom's `/v2/users` endpoint and comparing against their API spec should reveal the missing field.

**Stack trace:**
```
java.io.IOException: Server returned HTTP response code: 400 for URL: https://api.zoom.us/v2/users
    at java.base/sun.net.www.protocol.http.HttpURLConnection$10.run(HttpURLConnection.java:2085)
    [origin: ZoomAPI.createUser()]
```

**Affected endpoints:** `/a/` (Zoom integration, no direct URL logged)  
**Affected hosts:** pveuadminapp1.questionpro.net  
**Error IDs:** 103182, 103444, 103454, 103469, 103483, 103496

---

### 5. loadResponse Index Out of Bounds *(Medium, 4 errors)*

**Root cause:** `java.lang.IndexOutOfBoundsException: Index 0 out of bounds for length 0` in `/a/loadResponse.do` — the code tries to access the first element of an empty list when rendering an individual survey response.

**Summary:** Four occurrences for the same survey (ID 13606505) and same user (`thomas.conrad@salesfactory.com`), suggesting a data-integrity issue with that specific response set (147745721) where expected data rows are absent. An empty-list guard before the index access would prevent the crash and allow a graceful "no data" message.

**Stack trace:**
```
java.lang.IndexOutOfBoundsException: Index 0 out of bounds for length 0
    at java.base/jdk.internal.util.Preconditions.outOfBounds(Preconditions.java:64)
    [origin: loadResponse.do — accessing element 0 of an empty list when building response view]
```

**Affected endpoints:** `/a/loadResponse.do`  
**Affected hosts:** qpweb1.questionpro.net  
**Error IDs:** 111520, 133697, 133699, 133731

---

### 6. Panel Language Translation Import Failure *(Medium, 3 errors)*

**Root cause:** Two related failures in `/a/panelLanguageTranslationImport.do` for the same EU customer (`trpresearch.com`): an `ArrayIndexOutOfBoundsException` (index 164 in a length-164 array — off-by-one) and a `NullPointerException` on `PanelDetail.getID()` when the active survey context is null.

**Summary:** The language translation import feature is broken for at least one EU customer. The off-by-one error in `PanelTranslation` suggests the import loop iterates one index too many, and a missing null-check on `PanelDetail` causes a second failure path when the panel context isn't resolved. Both issues are in `com.surveyconsole.micropanel.language.PanelTranslation`.

**Stack traces:**
```
// Error IDs 130344, 130367 — off-by-one in import loop
java.lang.ArrayIndexOutOfBoundsException: Index 164 out of bounds for length 164
    at com.surveyconsole.micropanel.language.PanelTranslation.<method>(PanelTranslation.java)

// Error ID 149047 — null panel context
java.lang.NullPointerException: Cannot invoke "com.surveyconsole.micropanel.PanelDetail.getID()"
    because the return value of "com.surveyconsole..." is null
    at com.surveyconsole.micropanel.language.PanelTranslation.<method>(PanelTranslation.java)
```

**Affected endpoints:** `/a/panelLanguageTranslationImport.do`  
**Affected hosts:** pveuqpweb3.questionpro.net, pveuqpweb4.questionpro.net  
**Error IDs:** 130344, 130367, 149047

---

### 7. Portal Dashboard AJS — QA *(Low, 18 errors)*

**Root cause:** Same `InvocationTargetException` as cluster 1, but isolated to QA and release-candidate environments (`qa-release.questionpro.com`, `qaweb1`).

**Summary:** The QA environment mirrors the production bug in cluster 1, confirming this is a code-level regression (not infrastructure). These errors likely pre-date the production incidents and should disappear once cluster 1 is resolved.

**Affected endpoints:** `survey-angular.panel.portal.PortalDashBoardAJSHandler-GetSurveyDetails`  
**Affected hosts:** pveuadminapp1.questionpro.net, qaweb1  
**Stack trace:** Same as cluster 1 — `java.lang.reflect.InvocationTargetException` in `PortalDashBoardAJSHandler`.

**Error IDs (all 18):** 125314, 125375, 125436, 125890, 125920, 125939, 126012, 126017, 126025, 126557, 154508, 155382, 155497, 155498, 155508, 155509, 155513, 155514

---

### 8. Twitter / X Sign-In API Failures *(Low, 3 errors)*

**Root cause:** Twitter API returning `400 Bad Request` (rate limit) and `403 Forbidden` (update limits) for `/a/twitterSignIn` — the Twitter/X developer app credentials are either rate-limited or the app's write permissions have been revoked.

**Summary:** Internal QP users (`payal.pandey+eu@questionpro.com`, `karishma.rao@questionpro.com`) attempted Twitter sign-in for panel Ideas Setup and hit API-level rejections. Twitter's v1 API access has become increasingly restricted; this integration likely needs re-evaluation against X's current API tier before it can work reliably again.

**Stack traces:**
```
// ID 105541, 105581 — rate limited
400: The request was invalid. [...rate limiting per https://dev.twitter.com/pages/rate-limiting]
    at /a/twitterSignIn [panelID=1602638566]

// ID 105261 — forbidden / update limits
403: The request is understood, but it has been refused.
    [update limits per https://support.twitter.com/...]
    at /a/twitterSignIn [panelID=148318]
```

**Affected endpoints:** `/a/twitterSignIn`  
**Affected hosts:** pveuadminapp1.questionpro.net, pvqpadminapp1.questionpro.net  
**Error IDs:** 105261, 105541, 105581

---

### 9. JSP / Portal Page Null Pointer *(Low, 3 errors)*

**Root cause:** Two distinct NPEs: `Panel.isFlashletType()` called on a null panel in `/a/framework2AdHocPortal.do`, and `PanelMember.getID()` called on a null member in the JSP error page itself.

**Summary:** Three isolated one-off errors from internal users (`guy.casters@questionpro.com`, `karishma.rao@questionpro.com`) and one EU customer. The security layer in `framework2AdHocPortal` does not guard against a null panel lookup. The JSP error page NPE is a secondary failure that obscures the original error — the error-rendering path itself has a null-check gap.

**Stack traces:**
```
// ID 82343 — null panel in security check
java.lang.NullPointerException: Cannot invoke "com.surveyconsole.micropanel.Panel.isFlashletType()"
    because "panel" is null
    at com.surveyconsole.security.<method> [/a/framework2AdHocPortal.do]

// ID 157448 — null member in JSP error page
java.lang.NullPointerException: Cannot invoke "com.surveyconsole.micropanel.PanelMember.getID()"
    because "<local43>" is null
    at _jsp [/a/jsp/includes/error.jsp]

// ID 158022 — null processing item in JSP error page
java.lang.NullPointerException: Cannot invoke "com.surveyconsole.batch.ProcessingItem.getClassName()"
    because "<local34>" is null
    at _jsp [/a/jsp/includes/error.jsp]
```

**Affected endpoints:** `/a/framework2AdHocPortal.do`, `/a/jsp/includes/error.jsp`  
**Affected hosts:** qpweb1.questionpro.net, pvqpadminapp1.questionpro.net, pveuqprun4.questionpro.net  
**Error IDs:** 82343, 157448, 158022

---

### 10. SMTP / Email Config Errors *(Low, 2 errors)*

**Root cause:** Two independent email delivery failures: `Unknown SMTP host: mail-relay.emea.corpinter.net` (a customer's private relay is unreachable) and `AddressException: Illegal address in string ''` (blank reply-to email address stored in SMTP preferences).

**Summary:** Both errors are customer configuration issues rather than platform bugs. The SMTP host failure (Corpinter customer) will self-resolve if their relay comes back online. The blank reply-to address (`SMTPEmailAddressManager.getReplyToEmail`) indicates a missing validation when saving SMTP preferences — an empty string slips through and causes a crash at send time.

**Stack traces:**
```
// ID 106663 — customer SMTP relay unreachable
javax.mail.MessagingException: Unknown SMTP host: mail-relay.emea.corpinter.net
    nested: java.net.UnknownHostException: mail-relay.emea.corpinter.net
    at com.sun.mail.smtp.SMTPTransport.openServer(SMTPTransport.java:1389)
    at com.surveyconsole.campaign.CampaignBatch.getTransport(CampaignBatch.java:759)

// ID 47942 — blank reply-to address
javax.mail.internet.AddressException: Illegal address in string ''
    at javax.mail.internet.InternetAddress.<init>(InternetAddress.java:108)
    at com.surveyconsole.micropanel.send.preference.SMTPEmailAddressManager.getReplyToEmail(SMTPEmailAddressManager.java:58)
    at com.surveyconsole.micropanel.PanelMember$ContactOptions.updateSMTPPreferenceEmails(PanelMember.java:4002)
```

**Affected endpoints:** Campaign send, `/a/` (SMTP setup)  
**Affected hosts:** pveuadminapp1.questionpro.net, sarun1.questionpro.net  
**Error IDs:** 106663, 47942

---

### 11. QA Selenium SQL Syntax Error *(Low, 1 error)*

**Root cause:** `UserPreparedStatement` throws a SQL syntax error during a Selenium-driven `inviteUsers` test on QA — the generated SQL is malformed.

**Summary:** A single automated test failure on `saqaapp1`. The SQL is built from test data (`selenium-communities test sa@questionpro.com`) and is not valid. This is a QA test defect, not a production concern.

**Stack trace:**
```
UserPreparedStatement[SpyPreparedStatement[null]]
You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version
    at /a/inviteUsers.do [text=selenium-communities test sa@questionpro.com,TestTest123,...]
```

**Affected endpoints:** `/a/inviteUsers.do`  
**Affected hosts:** saqaapp1.questionpro.net  
**Error IDs:** 111827

---

## Recommended Actions

| Priority | Action |
|----------|--------|
| P0 | Investigate `PortalDashBoardAJSHandler-GetTaskDetails` — pull full Resin logs on any qprun node, find `getCause()` of the `InvocationTargetException`, fix and redeploy (cluster 1) |
| P0 | Separately investigate `GetSurveyDetails` on EU nodes pveuqprun2/4 — may share or differ from cluster 1 root cause (cluster 2) |
| P0 | Check cluster 7 (QA AJS) — if it reproduces the same root cause, use QA to iterate the fix faster |
| P1 | Add null guard before `TreeMap.put` in campaign batch search (cluster 3) |
| P1 | Audit Zoom create-user payload against current API spec for EU region (cluster 4) |
| P2 | Guard empty-list access in `loadResponse.do` (cluster 5) |
| P2 | Fix off-by-one loop bound and add null-check on `PanelDetail` in language import (cluster 6) |
| P3 | Add server-side validation to reject blank reply-to email before saving SMTP prefs (cluster 10) |
| P3 | Evaluate Twitter/X integration viability against current API tier (cluster 8) |

---

## PDM Report

```
500 Errors Logged (29 May – 4 Jun 2026)

US DC — 2 panel, 1 portal
  Hosts: qprun1–11, qpweb1, pvqpadminapp1/2, sarun1

EU DC — 3 panel, 1 portal
  Hosts: pveuqprun2/4, pveuqpweb3/4, pveuadminapp1

QA  — 1 panel, 1 portal (non-production, excluded from counts above)
```

> Counts reflect **distinct error types** (clusters), not total error rows.
> Portal = member-facing (dashboard, surveys, rewards, account).
> Panel = admin-facing (campaign search, user management, moderation, imports).

---

## Engineering Update

```
500 Errors | Panel-2, Portal-1 (US) | Portal-1, Panel-3 (EU)

~ #49417 : Member dashboard task list broken (GetTaskDetails) — InvocationTargetException
           across all US prod nodes (qprun1–11). Member portal down for all tenants.

~ #55836 : Member survey list broken (GetSurveyDetails) — same exception pattern, EU
           onepoll nodes only (pveuqprun2/4). Separate investigation needed from #49417.

~ #103182 : Zoom create-user API returning HTTP 400 — EU admin panel Zoom integration
            non-functional. Likely malformed request payload to api.zoom.us/v2/users.

~ #102596 : NullPointerException in campaign send history search — admin panel,
            TreeMap.put receiving null value. Broken for at least one customer.

~ #130344 : ArrayIndexOutOfBoundsException in panel language translation import — EU
            off-by-one in import loop. Affects trpresearch.com on eu.questionpro.com.

~ #111520 : IndexOutOfBoundsException loading individual survey response — empty result
            set accessed at index 0. Isolated to one customer/survey on qpweb1.
```
