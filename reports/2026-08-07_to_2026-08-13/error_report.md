# weekly error report — 2026-08-07 to 2026-08-13

**date range:** 2026-08-07 → 2026-08-13
**total errors:** 52
**clusters:** 13

---

## summary table

| # | sev | root cause | count | dc | side | dates |
|---|-----|-----------|-------|-----|------|-------|
| 1 | high | java.util.ConcurrentModificationException | 14 | EU+US | portal | 2026-08-07 → 2026-08-12 |
| 2 | medium | java.lang.NullPointerException: Cannot invoke "com.surveyconsole.user.globalsett | 8 | US | other | 2026-08-09 |
| 3 | medium | java.net.ConnectException: Connection refused | 4 | US | panel | 2026-08-11 |
| 4 | medium | UserPreparedStatement[SpyPreparedStatement[null]] | 4 | EU | panel | 2026-08-11 |
| 5 | medium | Root Exception :
org.apache.xmlrpc.XmlRpcException: Failed to read servers respo | 4 | US | other | 2026-08-10 |
| 6 | medium | java.lang.NullPointerException: Cannot invoke "com.surveyconsole.user.globalsett | 4 | US | other | 2026-08-09 |
| 7 | low | java.lang.IndexOutOfBoundsException: Index 0 out of bounds for length 0 | 2 | US | other | 2026-08-11 |
| 8 | low | UserPreparedStatement[SpyPreparedStatement[null]] | 2 | EU | panel | 2026-08-11 |
| 9 | low | java.lang.NullPointerException: Cannot invoke "com.surveyconsole.micropanel.Pane | 2 | EU | panel | 2026-08-10 |
| 10 | low | You have an error in your SQL syntax; check the manual that corresponds to your  | 2 | EU | other | 2026-08-10 |
| 11 | low | java.lang.NullPointerException: Cannot invoke "com.surveyconsole.micropanel.Pane | 2 | QA | panel | 2026-08-09 |
| 12 | low | Root Exception :
org.apache.xmlrpc.XmlRpcException: Failed to read servers respo | 2 | US | other | 2026-08-08 |
| 13 | low | java.lang.NullPointerException: Cannot invoke "com.surveyconsole.user.User.getBu | 2 | US | other | 2026-08-08 |

---

## dc & side breakdown

| dc | portal | panel | other |
|----|--------|-------|-------|
| us | 1 | 1 | 6 |
| eu | 1 | 3 | 1 |
| qa | 0 | 1 | 0 |

---

## cluster details

### 1. java.util.ConcurrentModificationException *(high, 14 hits)*

**dc / side:** eu + us · portal
**endpoint:** `survey-angular.panel.portal.PortalSurveyAJSHandler-GetAllSurveys`
**dates:** 2026-08-07 → 2026-08-12
**affected hosts:** pveuqprun2.questionpro.net, pveuqprun3.questionpro.net, pveuqprun4.questionpro.net, pvweb1
**error ids (sample 5/14):** 2393000, 2391250, 2382217, 2382216, 2379258

**request context:**

- referer: `https://onepolluk.questionpro.eu/a/showMemberSurveys.do?lppn=false`
- ip: `195.188.226.111` (GB)

**root cause:**
```
java.util.ConcurrentModificationException
```

**codebase frames:**
```
at com.surveyconsole.angular.panel.portal.PanelLogSurveyFetcher.getCachedSurveyIds(PanelLogSurveyFetcher.java:48)
at com.surveyconsole.angular.panel.portal.PanelLogSurveyFetcher.getMemberSurveyIdsFromPanelLog(PanelLogSurveyFetcher.java:56)
at com.surveyconsole.angular.panel.portal.PanelMemberSurveyFetcher.updateCachedSurveysOfPanelLog(PanelMemberSurveyFetcher.java:81)
at com.surveyconsole.angular.panel.portal.PanelMemberSurveyFetcher.getPanelMemberSurveysObject(PanelMemberSurveyFetcher.java:94)
at com.surveyconsole.angular.panel.portal.PortalSurveyAJSHandler.apiGetAllSurveys(PortalSurveyAJSHandler.java:25)
```

---

### 2. java.lang.NullPointerException: Cannot invoke "com.surveyconsole.user. *(medium, 8 hits)*

**dc / side:** us · other
**endpoint:** `/a/verifyDomainAuthentication.do`
**dates:** 2026-08-09
**affected hosts:** pvweb2
**error ids (sample 5/8):** 2365016, 2365015, 2365014, 2365013, 2365016

**request context:**

- referer: `null`
- params: `ajax=true&engine=dojo&mode=list&ID=1`

**root cause:**
```
java.lang.NullPointerException: Cannot invoke "com.surveyconsole.user.globalsettings.domainauthentication.iron.EmailDomain.isVerifiedEmailDomain()" because "emailDomain" is null
```

**codebase frames:**
```
at com.surveyconsole.user.globalsettings.domainauthentication.action.iron.VerifyDomainAuthenticationAction.addSuccessOrErrorMessage(VerifyDomainAuthenticationAction.java:52)
at com.surveyconsole.user.globalsettings.domainauthentication.action.iron.VerifyDomainAuthenticationAction.getAjaxResponse(VerifyDomainAuthenticationAction.java:72)
at com.bhaskaran.ui.ActionAdapter.perform(ActionAdapter.java:398)
at com.surveyconsole.application.logs.filter.MDCFilter.filter(MDCFilter.java:26)
at com.bhaskaran.application.filter.FilterAdapter.doFilter(FilterAdapter.java:14)
at com.surveyconsole.intercom.IntercomAppFilter.filter(IntercomAppFilter.java:28)
```

---

### 3. java.net.ConnectException: Connection refused *(medium, 4 hits)*

**dc / side:** us · panel
**endpoint:** `/a/exportPanelHealthDashboardPDF.do`
**dates:** 2026-08-11
**affected hosts:** pvweb1
**error ids (sample 4/4):** 2384959, 2384924, 2384959, 2384924

**request context:**

- referer: `https://pv.questionpro.com/a/showPanelHealthDashboard.do?lcfpn=false`
- params: `ajax=true&engine=dojo&endDate=1786485236940&startDate=1778709236940`

**root cause:**
```
java.net.ConnectException: Connection refused
```

**codebase frames:**
```
at com.surveyconsole.batch.KickStartServices.startProcessingItem(KickStartServices.java:89)
at com.surveyconsole.batch.DownloadKickStartServiceHandler.callKickStartService(DownloadKickStartServiceHandler.java:6)
at com.surveyconsole.batch.KickStartServiceHandlerTemplate.addItem(KickStartServiceHandlerTemplate.java:91)
at com.surveyconsole.batch.XmlRpcService.addItem(XmlRpcService.java:15)
at com.surveyconsole.batch.ProcessingItemFactory.addItem(ProcessingItemFactory.java:3191)
at com.surveyconsole.batch.ProcessingItemFactory.addItem(ProcessingItemFactory.java:3184)
```

---

### 4. UserPreparedStatement[SpyPreparedStatement[null]] *(medium, 4 hits)*

**dc / side:** eu · panel
**endpoint:** `/a/editPanelMember.do`
**dates:** 2026-08-11
**affected hosts:** pveuqpweb4.questionpro.net
**error ids (sample 4/4):** 2379378, 2379372, 2379378, 2379372

**request context:**

- referer: `https://eu.questionpro.com/a/showPanelUserReport.do?lcfpn=false`
- params: `engine=dojo&moderator=0&mobileNumber=7828616352&pageOrigin=&username=&ID=25917439&custom1=&custom2=&custom3=&countryCode=+44&lastname=Jellicoe&middlename=&userAction=save&ajax=true&custom4=&custom5=&s`

**root cause:**
```
UserPreparedStatement[SpyPreparedStatement[null]]
```

**codebase frames:**
```
at com.bhaskaran.database.PreparedInsertCommand.executeWithConnection(PreparedInsertCommand.java:39)
at com.bhaskaran.database.ConnectionCommand.execute(ConnectionCommand.java:66)
at com.bhaskaran.database.PreparedInsertCommand.execute(PreparedInsertCommand.java:123)
at com.surveyconsole.micropanel.reward.QPointLogHelper.insertData(QPointLogHelper.java:483)
at com.surveyconsole.micropanel.reward.QPointLog.insert(QPointLog.java:43)
at com.surveyconsole.micropanel.PanelMember.addQPointLog(PanelMember.java:4678)
```

---

### 5. Root Exception :
org.apache.xmlrpc.XmlRpcException: Failed to read ser *(medium, 4 hits)*

**dc / side:** us · other
**endpoint:** `(unknown)`
**dates:** 2026-08-10
**affected hosts:** pvweb1, pvweb2
**error ids (sample 4/4):** 2376573, 2370961, 2376573, 2370961

**root cause:**
```
Root Exception :
org.apache.xmlrpc.XmlRpcException: Failed to read servers response: pvdata.questionpro.net
	at org.apache.xmlrpc.client.XmlRpcStreamTransport.sendRequest(XmlRpcStreamTransport.java:15
```

**codebase frames:**
```
at com.surveyconsole.batch.KickStartServices.getSurveyResponseCountByDataSource(KickStartServices.java:325)
at com.surveyconsole.builder.ListSurveysAction$1.runLogged(ListSurveysAction.java:370)
at com.bhaskaran.processor.ErrorLoggedThread.run(ErrorLoggedThread.java:66)
at com.surveyconsole.batch.KickStartServices.getSurveyResponseCountByDataSource(KickStartServices.java:328)
at com.surveyconsole.builder.ListSurveysAction$1.runLogged(ListSurveysAction.java:370)
at com.bhaskaran.processor.ErrorLoggedThread.run(ErrorLoggedThread.java:66)
```

---

### 6. java.lang.NullPointerException: Cannot invoke "com.surveyconsole.user. *(medium, 4 hits)*

**dc / side:** us · other
**endpoint:** `/a/verifyDomainAuthentication.do`
**dates:** 2026-08-09
**affected hosts:** pvweb2
**error ids (sample 4/4):** 2365010, 2365006, 2365010, 2365006

**request context:**

- referer: `https://pv.questionpro.com/a/showUpgradeUser.do?payment=creditCardUpdate`
- params: `ajax=true&engine=dojo&ID=2010`

**root cause:**
```
java.lang.NullPointerException: Cannot invoke "com.surveyconsole.user.globalsettings.domainauthentication.iron.EmailDomain.getID()" because "emailDomain" is null
```

**codebase frames:**
```
at com.surveyconsole.user.globalsettings.domainauthentication.action.iron.VerifyDomainAuthenticationAction.getAjaxResponse(VerifyDomainAuthenticationAction.java:70)
at com.bhaskaran.ui.ActionAdapter.perform(ActionAdapter.java:398)
at com.surveyconsole.application.logs.filter.MDCFilter.filter(MDCFilter.java:26)
at com.bhaskaran.application.filter.FilterAdapter.doFilter(FilterAdapter.java:14)
at com.surveyconsole.intercom.IntercomAppFilter.filter(IntercomAppFilter.java:28)
at com.bhaskaran.application.filter.FilterAdapter.doFilter(FilterAdapter.java:14)
```

---

### 7. java.lang.IndexOutOfBoundsException: Index 0 out of bounds for length  *(low, 2 hits)*

**dc / side:** us · other
**endpoint:** `/a/loadResponse.do`
**dates:** 2026-08-11
**affected hosts:** qpweb3.questionpro.net
**error ids (sample 2/2):** 2382693, 2382693

**request context:**

- referer: `https://www.questionpro.com/a/frame.do?mode=viewIndividual&surveyID=53qAImxRSpO3tRJFsXAu1AVy2e6uQ62W8qN_86mxeXI-&responseSetID=13oSvt4OdDdLXG1BB_tF36PW656ym_D66gZaqYFyrpo-`
- params: `surveyID=13363233&responseSetID=150384081`

**root cause:**
```
java.lang.IndexOutOfBoundsException: Index 0 out of bounds for length 0
```

**codebase frames:**
```
at com.surveyconsole.html.TEXTLoader.loadInternal(TEXTLoader.java:44)
at com.surveyconsole.html.Loader.load(Loader.java:36)
at com.surveyconsole.analysis.ResponseLoader.loadData(ResponseLoader.java:832)
at com.surveyconsole.analysis.ResponseLoader.loadSectionResponse(ResponseLoader.java:776)
at com.surveyconsole.analysis.ResponseLoader.load(ResponseLoader.java:718)
at com.surveyconsole.analysis.ResponseLoader.load(ResponseLoader.java:695)
```

---

### 8. UserPreparedStatement[SpyPreparedStatement[null]] *(low, 2 hits)*

**dc / side:** eu · panel
**endpoint:** `/a/editPanelMember.do`
**dates:** 2026-08-11
**affected hosts:** pveuadminapp1.questionpro.net
**error ids (sample 2/2):** 2380536, 2380536

**request context:**

- referer: `https://euadmin.questionpro.com/a/showPanelUserReport.do?lcfpn<BR><BR>UserPreparedStatement[SpyPreparedStatement[null`
- params: `engine=dojo&moderator=0&mobileNumber=&pageOrigin=&username=sid9965&ID=1603932056&custom1=&custom2=&custom3=&countryCode=+91&lastname=Bandewar&middlename=&userAction=save&ajax=true&custom4=&custom5=&st`

**root cause:**
```
UserPreparedStatement[SpyPreparedStatement[null]]
```

**codebase frames:**
```
at com.bhaskaran.database.PreparedInsertCommand.executeWithConnection(PreparedInsertCommand.java:39)
at com.bhaskaran.database.ConnectionCommand.execute(ConnectionCommand.java:66)
at com.bhaskaran.database.PreparedInsertCommand.execute(PreparedInsertCommand.java:123)
at com.surveyconsole.micropanel.reward.QPointLogHelper.insertData(QPointLogHelper.java:483)
at com.surveyconsole.micropanel.reward.QPointLog.insert(QPointLog.java:43)
at com.surveyconsole.micropanel.PanelMember.addQPointLog(PanelMember.java:4678)
```

---

### 9. java.lang.NullPointerException: Cannot invoke "com.surveyconsole.micro *(low, 2 hits)*

**dc / side:** eu · panel
**endpoint:** `/a/showPanelUserReport.do`
**dates:** 2026-08-10
**affected hosts:** pveuqpweb4.questionpro.net
**error ids (sample 2/2):** 2369401, 2369401

**request context:**

- referer: `https://eu.questionpro.com/a/showPanelUserReport.do?lcfpn=false`

**root cause:**
```
java.lang.NullPointerException: Cannot invoke "com.surveyconsole.micropanel.PanelMember.getID()" because "<local43>" is null
```

**codebase frames:**
```
at com.surveyconsole.application.logs.filter.MDCFilter.filter(MDCFilter.java:26)
at com.bhaskaran.application.filter.FilterAdapter.doFilter(FilterAdapter.java:14)
at com.surveyconsole.intercom.IntercomAppFilter.filter(IntercomAppFilter.java:28)
at com.bhaskaran.application.filter.FilterAdapter.doFilter(FilterAdapter.java:14)
at com.surveyconsole.infra.XSSPreventionFilter.filter(XSSPreventionFilter.java:131)
at com.bhaskaran.application.filter.FilterAdapter.doFilter(FilterAdapter.java:14)
```

---

### 10. You have an error in your SQL syntax; check the manual that correspond *(low, 2 hits)*

**dc / side:** eu · other
**endpoint:** `/a/showPanelSegment.do`
**dates:** 2026-08-10
**affected hosts:** pveuqprun4.questionpro.net
**error ids (sample 2/2):** 2368483, 2368483

**request context:**

- referer: `https://onepoll.questionpro.eu/a/showPanelSample.do?lcfpn=false`
- params: `ajax=true&engine=dojo&mode=totalActiveCount&segmentID=1602638452`

**root cause:**
```
You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near ')) AND pm.last_activity_ts > '1970-01-01'' at line 1
```

**codebase frames:**
```
at com.bhaskaran.database.PreparedConnectionCommand.executeWithConnection(PreparedConnectionCommand.java:75)
at com.bhaskaran.database.ConnectionCommand.execute(ConnectionCommand.java:66)
at com.bhaskaran.database.PreparedConnectionCommand.execute(PreparedConnectionCommand.java:117)
at com.bhaskaran.database.CountCommand.executeLong(CountCommand.java:31)
at com.surveyconsole.micropanel.Panel.getPanelMemberCount(Panel.java:4825)
at com.surveyconsole.micropanel.CompositePanelMemberFilterCriteria.getTotalActiveMemberCount(CompositePanelMemberFilterCriteria.java:144)
```

---

### 11. java.lang.NullPointerException: Cannot invoke "com.surveyconsole.micro *(low, 2 hits)*

**dc / side:** qa · panel
**endpoint:** `/a/inviteUsers.do`
**dates:** 2026-08-09
**affected hosts:** qa1.du
**error ids (sample 2/2):** 2365660, 2365660

**request context:**

- referer: `https://aeqa.questionpro.com/a/showPanelUserReport.do?lcfpn=false`
- params: `ajax=true&engine=dojo&text=selenium-communities+test+ae@questionpro.com,TestTest123,7894561239,TestA,TestB,TestC,Selenium@123&info=-1`

**root cause:**
```
java.lang.NullPointerException: Cannot invoke "com.surveyconsole.micropanel.PanelMemberFieldValues.hasCustomVariables()" because "fieldValues" is null
```

**codebase frames:**
```
at com.surveyconsole.micropanel.processor.impl.BulkProfileInsertProcessor.prepareInsert(BulkProfileInsertProcessor.java:107)
at com.surveyconsole.micropanel.processor.impl.BulkProfileInsertProcessor.initInsert(BulkProfileInsertProcessor.java:98)
at com.surveyconsole.micropanel.processor.impl.BulkProfileInsertProcessor.<init>(BulkProfileInsertProcessor.java:49)
at com.surveyconsole.micropanel.BulkInsertPanelMemberProcessor.bulkProfileInsertProcessingForMembers(BulkInsertPanelMemberProcessor.java:195)
at com.surveyconsole.micropanel.BulkInsertPanelMemberProcessor.postInsertProcessing(BulkInsertPanelMemberProcessor.java:174)
at com.surveyconsole.micropanel.BulkInsertPanelMemberProcessor.bulkInsertPanelMembers(BulkInsertPanelMemberProcessor.java:90)
```

---

### 12. Root Exception :
org.apache.xmlrpc.XmlRpcException: Failed to read ser *(low, 2 hits)*

**dc / side:** us · other
**endpoint:** `(unknown)`
**dates:** 2026-08-08
**affected hosts:** pvweb1
**error ids (sample 2/2):** 2363149, 2363149

**root cause:**
```
Root Exception :
org.apache.xmlrpc.XmlRpcException: Failed to read servers response: pv-data.questionpro.net
	at org.apache.xmlrpc.client.XmlRpcStreamTransport.sendRequest(XmlRpcStreamTransport.java:1
```

**codebase frames:**
```
at com.surveyconsole.batch.KickStartServices.getSurveyResponseCountByDataSource(KickStartServices.java:325)
at com.surveyconsole.builder.ListSurveysAction$1.runLogged(ListSurveysAction.java:370)
at com.bhaskaran.processor.ErrorLoggedThread.run(ErrorLoggedThread.java:66)
at com.surveyconsole.batch.KickStartServices.getSurveyResponseCountByDataSource(KickStartServices.java:328)
at com.surveyconsole.builder.ListSurveysAction$1.runLogged(ListSurveysAction.java:370)
at com.bhaskaran.processor.ErrorLoggedThread.run(ErrorLoggedThread.java:66)
```

---

### 13. java.lang.NullPointerException: Cannot invoke "com.surveyconsole.user. *(low, 2 hits)*

**dc / side:** us · other
**endpoint:** `/a/showPanelHealthDashboard.do`
**dates:** 2026-08-08
**affected hosts:** qpweb2.questionpro.net
**error ids (sample 2/2):** 2363133, 2363133

**request context:**

- referer: `https://www.questionpro.com/a/showPanelHealthDashboard.do?lcfpn=false`

**root cause:**
```
java.lang.NullPointerException: Cannot invoke "com.surveyconsole.user.User.getBuildHeader()" because "<local32>" is null
```

**codebase frames:**
```
at com.surveyconsole.application.logs.filter.MDCFilter.filter(MDCFilter.java:26)
at com.bhaskaran.application.filter.FilterAdapter.doFilter(FilterAdapter.java:14)
at com.surveyconsole.intercom.IntercomAppFilter.filter(IntercomAppFilter.java:28)
at com.bhaskaran.application.filter.FilterAdapter.doFilter(FilterAdapter.java:14)
at com.surveyconsole.infra.XSSPreventionFilter.filter(XSSPreventionFilter.java:131)
at com.bhaskaran.application.filter.FilterAdapter.doFilter(FilterAdapter.java:14)
```

---

## pdm report

```
52 errors logged (2026-08-07 → 2026-08-13)

us dc — 1 panel, 1 portal
eu dc — 3 panel, 1 portal
qa    — 1 panel, 0 portal  (non-production)
```

---

## engineering update

```
52 errors | panel-1, portal-1 (us) | panel-3, portal-1 (eu)

~ 14  : [2026-08-07→2026-08-12] java.util.concurrentmodificationexception — survey-angular.panel.portal.PortalSurveyAJSHandler-GetAllSurveys
~ 8   : [2026-08-09] java.lang.nullpointerexception: cannot invoke "com.surveyconsole.user.globalsettings.domainauthentic — /a/verifyDomainAuthentication.do
```