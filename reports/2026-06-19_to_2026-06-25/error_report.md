# weekly error report — 2026-06-19 to 2026-06-25

**date range:** 2026-06-19 → 2026-06-25
**total errors:** 65
**clusters:** 19

---

## summary table

| # | sev | root cause | count | dc | side | dates |
|---|-----|-----------|-------|-----|------|-------|
| 1 | high | Root Exception :
org.apache.xmlrpc.XmlRpcException: Failed to create input strea | 15 | EU | other | 2026-06-22 |
| 2 | high | com.bhaskaran.database.DatabaseError: You have an error in your SQL syntax; chec | 14 | EU+QA | portal | 2026-06-20 → 2026-06-24 |
| 3 | medium | java.util.NoSuchElementException: No value present | 7 | QA+US | other | 2026-06-22 |
| 4 | medium | java.lang.NullPointerException: Cannot invoke "com.surveyconsole.micropanel.Pane | 6 | US | other | 2026-06-24 |
| 5 | medium | java.lang.NullPointerException: Cannot invoke "com.surveyconsole.micropanel.Pane | 4 | EU | panel | 2026-06-24 |
| 6 | low | java.lang.NullPointerException: Cannot invoke "com.surveyconsole.run.RunSurveySh | 4 | QA | other | 2026-06-23 |
| 7 | low | Root Exception : | 2 | EU | other | 2026-06-22 |
| 8 | low | java.lang.IndexOutOfBoundsException: Index 0 out of bounds for length 0 | 2 | US | other | 2026-06-22 |
| 9 | low | You have an error in your SQL syntax; check the manual that corresponds to your  | 1 | EU | other | 2026-06-19 |
| 10 | low | UserPreparedStatement[SpyPreparedStatement[null]] | 1 | QA | other | 2026-06-21 |
| 11 | low | UserPreparedStatement[SpyPreparedStatement[null]] | 1 | US | other | 2026-06-22 |
| 12 | low | java.lang.UnsupportedOperationException | 1 | EU | other | 2026-06-23 |
| 13 | low | You have an error in your SQL syntax; check the manual that corresponds to your  | 1 | EU | other | 2026-06-23 |
| 14 | low | You have an error in your SQL syntax; check the manual that corresponds to your  | 1 | EU | other | 2026-06-23 |
| 15 | low | You have an error in your SQL syntax; check the manual that corresponds to your  | 1 | EU | other | 2026-06-23 |
| 16 | low | You have an error in your SQL syntax; check the manual that corresponds to your  | 1 | EU | other | 2026-06-23 |
| 17 | low | java.net.SocketTimeoutException: Read timed out | 1 | US | other | 2026-06-24 |
| 18 | low | java.lang.NullPointerException: Cannot invoke "com.surveyconsole.user.User.hasSm | 1 | US | other | 2026-06-24 |
| 19 | low | java.lang.NullPointerException: Cannot invoke "com.surveyconsole.micropanel.Pane | 1 | QA | other | 2026-06-24 |

---

## dc & side breakdown

| dc | portal | panel | other |
|----|--------|-------|-------|
| us | 0 | 0 | 6 |
| eu | 1 | 1 | 8 |
| qa | 1 | 0 | 4 |

---

## cluster details

### 1. Root Exception :
org.apache.xmlrpc.XmlRpcException: Failed to create i *(high, 15 hits)*

**dc / side:** eu · other
**endpoint:** `(unknown)`
**dates:** 2026-06-22
**affected hosts:** pveuadminapp1.questionpro.net, pveuqprun4.questionpro.net, pveuqpweb1.questionpro.net, pveuqpweb2.questionpro.net, pveuqpweb3.questionpro.net, pveuqpweb4.questionpro.net
**error ids (sample 5/15):** 519700, 519716, 519740, 519749, 519774

**root cause:**
```
Root Exception :
org.apache.xmlrpc.XmlRpcException: Failed to create input stream: Server returned HTTP response code: 502 for URL: http://eu-data.questionpro.net/a/xmlrpc
	at org.apache.xmlrpc.client
```

**codebase frames:**
```
at com.surveyconsole.batch.KickStartServices.getSurveyResponseCountByDataSource(KickStartServices.java:325)
at com.surveyconsole.builder.ListSurveysAction$1.runLogged(ListSurveysAction.java:369)
at com.bhaskaran.processor.ErrorLoggedThread.run(ErrorLoggedThread.java:66)
at com.surveyconsole.batch.KickStartServices.getSurveyResponseCountByDataSource(KickStartServices.java:328)
at com.surveyconsole.builder.ListSurveysAction$1.runLogged(ListSurveysAction.java:369)
at com.bhaskaran.processor.ErrorLoggedThread.run(ErrorLoggedThread.java:66)
```

---

### 2. com.bhaskaran.database.DatabaseError: You have an error in your SQL sy *(high, 14 hits)*

**dc / side:** eu + qa · portal
**endpoint:** `/a/panel.do`
**dates:** 2026-06-20 → 2026-06-24
**affected hosts:** pveuadminapp1.questionpro.net, pveuqprun1.questionpro.net, pveuqprun3.questionpro.net, pveuqprun4.questionpro.net, qaweb2
**error ids (sample 5/14):** 511277, 519643, 521964, 521976, 533776

**request context:**

- referer: `https://fivebargatefarming.questionpro.eu/a/panel.do?id=1602639204&tabIndex=`
- ip: `185.114.123.240` (GB)

**root cause:**
```
com.bhaskaran.database.DatabaseError: You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near ')  )  )' at line 1
```

**codebase frames:**
```
at com.bhaskaran.database.ConnectionCommand.execute(ConnectionCommand.java:81)
at com.bhaskaran.database.PreparedConnectionCommand.execute(PreparedConnectionCommand.java:117)
at com.bhaskaran.database.CountCommand.executeLong(CountCommand.java:31)
at com.surveyconsole.micropanel.Panel.getPanelMemberCount(Panel.java:4891)
at com.surveyconsole.micropanel.Panel.hydratePanelMember(Panel.java:11543)
at com.surveyconsole.micropanel.Panel.lambda$hydrateMemberForRecruitmentCriteria$10(Panel.java:11414)
```

---

### 3. java.util.NoSuchElementException: No value present *(medium, 7 hits)*

**dc / side:** qa + us · other
**endpoint:** `/a/renameUserFile.do`
**dates:** 2026-06-22
**affected hosts:** pvqpadminapp1.questionpro.net, qaweb2
**error ids (sample 5/7):** 521111, 521116, 521118, 521124, 521129

**request context:**

- referer: `https://qa-priority.questionpro.com/a/showImageLibrary.do?lcfpn=false`
- params: `ajax=true&engine=dojo&mode=update&userFileID=4204224&pageOffset=0&folderID=0&text=drtjkl&type=null`

**root cause:**
```
java.util.NoSuchElementException: No value present
```

**codebase frames:**
```
at com.surveyconsole.user.RenameUserFileAction.updateUserFileNameInCache(RenameUserFileAction.java:72)
at com.surveyconsole.user.RenameUserFileAction.getActionForward(RenameUserFileAction.java:65)
at com.surveyconsole.user.RenameUserFileAction.doPerform(RenameUserFileAction.java:36)
at com.bhaskaran.ui.ActionAdapter.lambda$perform$0(ActionAdapter.java:298)
at com.bhaskaran.performance.iron.PerformanceLogUtil.executeWithLoggingIfPossible(PerformanceLogUtil.java:34)
at com.bhaskaran.ui.ActionAdapter.perform(ActionAdapter.java:297)
```

---

### 4. java.lang.NullPointerException: Cannot invoke "com.surveyconsole.micro *(medium, 6 hits)*

**dc / side:** us · other
**endpoint:** `/a/showQPointInventory.do`
**dates:** 2026-06-24
**affected hosts:** pvqpadminapp1.questionpro.net
**error ids (sample 5/6):** 564124, 564125, 564127, 564128, 564131

**request context:**

- referer: `https://admin.questionpro.com/a/showQPointInventory.do?lcfpn=false`

**root cause:**
```
java.lang.NullPointerException: Cannot invoke "com.surveyconsole.micropanel.PanelMember.getSelectedLanguage()" because "member" is null
```

**codebase frames:**
```
at com.surveyconsole.micropanel.reward.QPointReward.getHTML(QPointReward.java:762)
at com.surveyconsole.micropanel.reward.QPointReward.getHTML(QPointReward.java:750)
at com.surveyconsole.application.logs.filter.MDCFilter.filter(MDCFilter.java:26)
at com.bhaskaran.application.filter.FilterAdapter.doFilter(FilterAdapter.java:14)
at com.surveyconsole.intercom.IntercomAppFilter.filter(IntercomAppFilter.java:28)
at com.bhaskaran.application.filter.FilterAdapter.doFilter(FilterAdapter.java:14)
```

---

### 5. java.lang.NullPointerException: Cannot invoke "com.surveyconsole.micro *(medium, 4 hits)*

**dc / side:** eu · panel
**endpoint:** `survey-angular.panel.PanelDiscussionTopicAJSHandler-GetActiveTopics`
**dates:** 2026-06-24
**affected hosts:** pveuqpweb2.questionpro.net
**error ids (sample 4/4):** 564176, 564177, 564178, 564179

**request context:**

- referer: `https://eu.questionpro.com/a/showDiscussionModeration.do`
- ip: `94.135.161.38` (DE)

**root cause:**
```
java.lang.NullPointerException: Cannot invoke "com.surveyconsole.micropanel.PanelMember.getDisplayName()" because the return value of "com.surveyconsole.micropanel.discussion.DiscussionTopic.getAuthorPanelMember(com.surveyconsole.micropanel.Panel)" is null
```

**codebase frames:**
```
at com.surveyconsole.micropanel.discussion.topic.service.AddEditTopicsService.putMemberDetails(AddEditTopicsService.java:90)
at com.surveyconsole.micropanel.discussion.topic.service.AddEditTopicsService.getUpdatedDiscussionObject(AddEditTopicsService.java:59)
at com.surveyconsole.micropanel.discussion.topic.service.AddEditTopicsService.getDiscussionsJsonArray(AddEditTopicsService.java:50)
at com.surveyconsole.micropanel.discussion.topic.service.AddEditTopicsService.getActiveDiscussionsList(AddEditTopicsService.java:170)
at com.surveyconsole.angular.panel.PanelDiscussionTopicAJSHandler.apiGetActiveTopics(PanelDiscussionTopicAJSHandler.java:460)
```

---

### 6. java.lang.NullPointerException: Cannot invoke "com.surveyconsole.run.R *(low, 4 hits)*

**dc / side:** qa · other
**endpoint:** `/a/takeProfileSurvey.do`
**dates:** 2026-06-23
**affected hosts:** qaweb2
**error ids (sample 4/4):** 544298, 544357, 544369, 544489

**request context:**

- referer: `https://qa-priority.questionpro.com/a/TakeSurvey?tt=YiyJTkNkMQiMuk7Y1EUFpg%3D%3D&lcfpn=false`
- params: `mode=continue&cf_466054_year=-1&segID=0&cf_466054_day=1&cf_466055=&cf_466054_month=1&submit=Continue`

**root cause:**
```
java.lang.NullPointerException: Cannot invoke "com.surveyconsole.run.RunSurveyShell.getPanelMember()" because "shell" is null
```

**codebase frames:**
```
at com.surveyconsole.micropanel.RequiredProfileUpdateAction.performPanel(RequiredProfileUpdateAction.java:39)
at com.surveyconsole.micropanel.portal.PanelAction.doPerform(PanelAction.java:116)
at com.bhaskaran.ui.ActionAdapter.lambda$perform$0(ActionAdapter.java:298)
at com.bhaskaran.performance.iron.PerformanceLogUtil.executeWithLoggingIfPossible(PerformanceLogUtil.java:34)
at com.bhaskaran.ui.ActionAdapter.perform(ActionAdapter.java:297)
at com.surveyconsole.application.logs.filter.MDCFilter.filter(MDCFilter.java:26)
```

---

### 7. Root Exception : *(low, 2 hits)*

**dc / side:** eu · other
**endpoint:** `/a/panelLanguageTranslationImport.do`
**dates:** 2026-06-22
**affected hosts:** pveuadminapp1.questionpro.net
**error ids (sample 2/2):** 523259, 523315

**request context:**

- referer: `https://euadmin.questionpro.com/a/editLanguage.do?mode=importTranslation&lcfln=false`
- params: `ajax=true&engine=dojo&mode=import`

**root cause:**
```
Root Exception :
```

**codebase frames:**
```
at com.surveyconsole.micropanel.language.PanelTranslationProcessor.populateTranslationForSystemFieldsWhenCellValueNotEmpty(PanelTranslationProcessor.java:272)
at com.surveyconsole.micropanel.language.PanelTranslationProcessor.addUpdateTranslationForSystemFields(PanelTranslationProcessor.java:258)
at com.surveyconsole.micropanel.language.PanelTranslationProcessor.populateSheetOneValuesForEachLanguageVersion(PanelTranslationProcessor.java:180)
at com.surveyconsole.micropanel.language.PanelTranslationProcessor.addUpdateTranslationForSystemFieldsForEachLanguage(PanelTranslationProcessor.java:139)
at com.surveyconsole.micropanel.language.PanelTranslationProcessor.importTranslations(PanelTranslationProcessor.java:122)
at com.surveyconsole.micropanel.language.PanelLanguageTranslationImportHandler.processUserFile(PanelLanguageTranslationImportHandler.java:98)
```

---

### 8. java.lang.IndexOutOfBoundsException: Index 0 out of bounds for length  *(low, 2 hits)*

**dc / side:** us · other
**endpoint:** `/a/loadResponse.do`
**dates:** 2026-06-22
**affected hosts:** qpweb1.questionpro.net
**error ids (sample 2/2):** 525151, 525158

**request context:**

- referer: `https://www.questionpro.com/a/frame.do?mode=viewIndividual&surveyID=96MFJ1fhrO1LHktMsTJTtheAMmtUhQRU_NKHxHsqV0Y-&responseSetID=UQtludCvtTAmWwC1AZmuKnIpDCtNsYxZk6SFUpVXSpQ-`
- params: `surveyID=13323446&responseSetID=148363643`

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

### 9. You have an error in your SQL syntax; check the manual that correspond *(low, 1 hits)*

**dc / side:** eu · other
**endpoint:** `/a/updatePanelMemberProfile.do`
**dates:** 2026-06-19
**affected hosts:** pveuqpweb1.questionpro.net
**error ids (sample 1/1):** 494739

**root cause:**
```
You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near ')  )  )' at line 1
```

**codebase frames:**
```
at com.bhaskaran.database.PreparedConnectionCommand.executeWithConnection(PreparedConnectionCommand.java:75)
at com.bhaskaran.database.ConnectionCommand.execute(ConnectionCommand.java:66)
at com.bhaskaran.database.PreparedConnectionCommand.execute(PreparedConnectionCommand.java:117)
at com.bhaskaran.database.CountCommand.executeLong(CountCommand.java:31)
at com.surveyconsole.micropanel.Panel.getPanelMemberCount(Panel.java:4891)
at com.surveyconsole.micropanel.Panel.hydratePanelMember(Panel.java:11543)
```

---

### 10. UserPreparedStatement[SpyPreparedStatement[null]] *(low, 1 hits)*

**dc / side:** qa · other
**endpoint:** `/a/inviteUsers.do`
**dates:** 2026-06-21
**affected hosts:** qa11
**error ids (sample 1/1):** 515188

**request context:**

- referer: `https://auqa.questionpro.com/a/showPanelUserReport.do?lcfpn=false`
- params: `ajax=true&engine=dojo&text=selenium-communities+test+au@questionpro.com,TestTest123,7894561239,TestA,TestB,TestC,Selenium@123&info=-1`

**root cause:**
```
UserPreparedStatement[SpyPreparedStatement[null]]
```

**codebase frames:**
```
at com.bhaskaran.database.PreparedInsertCommand.executeWithConnection(PreparedInsertCommand.java:39)
at com.bhaskaran.database.ConnectionCommand.execute(ConnectionCommand.java:66)
at com.bhaskaran.database.PreparedInsertCommand.execute(PreparedInsertCommand.java:123)
at com.surveyconsole.micropanel.BulkInsertPanelMemberProcessor.executeMultiplePanelMemberInsert(BulkInsertPanelMemberProcessor.java:161)
at com.surveyconsole.micropanel.BulkInsertPanelMemberProcessor.bulkInsertPanelMembers(BulkInsertPanelMemberProcessor.java:88)
at com.surveyconsole.micropanel.PanelMemberImportHandler.createOrUpdatePanelMember(PanelMemberImportHandler.java:34)
```

---

### 11. UserPreparedStatement[SpyPreparedStatement[null]] *(low, 1 hits)*

**dc / side:** us · other
**endpoint:** `/a/editPanelMember.do`
**dates:** 2026-06-22
**affected hosts:** qpweb1.questionpro.net
**error ids (sample 1/1):** 525161

**request context:**

- referer: `https://www.questionpro.com/a/showPanelUserReport.do?lcfpn=false`
- params: `engine=dojo&moderator=0&mobileNumber=2037677354&pageOrigin=&username=Metmadison&ID=83390501&custom1=&custom2=&custom3=&countryCode=+1&lastname=Madison&middlename=&userAction=save&ajax=true&custom4=&cu`

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

### 12. java.lang.UnsupportedOperationException *(low, 1 hits)*

**dc / side:** eu · other
**endpoint:** `/a//stopBroadcastProcess.do`
**dates:** 2026-06-23
**affected hosts:** pveuqpweb3.questionpro.net
**error ids (sample 1/1):** 543290

**request context:**

- referer: `https://eu.questionpro.com/a/showPanelBroadcastEmail.do?lcfpn=false`
- params: `ajax=true&engine=dojo&id=1604333467`

**root cause:**
```
java.lang.UnsupportedOperationException
```

**codebase frames:**
```
at com.surveyconsole.batch.LongProcessHandler.stopProcess(LongProcessHandler.java:44)
at com.surveyconsole.micropanel.broadcast.StopBroadcastProcessAction.doPerform(StopBroadcastProcessAction.java:32)
at com.bhaskaran.ui.ActionAdapter.lambda$perform$0(ActionAdapter.java:298)
at com.bhaskaran.performance.iron.PerformanceLogUtil.executeWithLoggingIfPossible(PerformanceLogUtil.java:34)
at com.bhaskaran.ui.ActionAdapter.perform(ActionAdapter.java:297)
at com.surveyconsole.application.logs.filter.MDCFilter.filter(MDCFilter.java:26)
```

---

### 13. You have an error in your SQL syntax; check the manual that correspond *(low, 1 hits)*

**dc / side:** eu · other
**endpoint:** `/a/updatePanelMemberProfile.do`
**dates:** 2026-06-23
**affected hosts:** pveuqpweb4.questionpro.net
**error ids (sample 1/1):** 544300

**root cause:**
```
You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near ')  )  )' at line 1
```

**codebase frames:**
```
at com.bhaskaran.database.PreparedConnectionCommand.executeWithConnection(PreparedConnectionCommand.java:75)
at com.bhaskaran.database.ConnectionCommand.execute(ConnectionCommand.java:66)
at com.bhaskaran.database.PreparedConnectionCommand.execute(PreparedConnectionCommand.java:117)
at com.bhaskaran.database.CountCommand.executeLong(CountCommand.java:31)
at com.surveyconsole.micropanel.Panel.getPanelMemberCount(Panel.java:4891)
at com.surveyconsole.micropanel.Panel.hydratePanelMember(Panel.java:11543)
```

---

### 14. You have an error in your SQL syntax; check the manual that correspond *(low, 1 hits)*

**dc / side:** eu · other
**endpoint:** `/a/updatePanelMemberProfile.do`
**dates:** 2026-06-23
**affected hosts:** pveuqpweb4.questionpro.net
**error ids (sample 1/1):** 544303

**root cause:**
```
You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near ')  )  and (cr1.user_id = 1602711301 and cr1.panel_id = 1602639204 and pm.id = cr' at line 1
```

**codebase frames:**
```
at com.bhaskaran.database.PreparedConnectionCommand.executeWithConnection(PreparedConnectionCommand.java:75)
at com.bhaskaran.database.ConnectionCommand.execute(ConnectionCommand.java:66)
at com.bhaskaran.database.PreparedConnectionCommand.execute(PreparedConnectionCommand.java:117)
at com.bhaskaran.database.CountCommand.executeLong(CountCommand.java:31)
at com.surveyconsole.micropanel.Panel.getPanelMemberCount(Panel.java:4891)
at com.surveyconsole.micropanel.Panel.hydratePanelMember(Panel.java:11543)
```

---

### 15. You have an error in your SQL syntax; check the manual that correspond *(low, 1 hits)*

**dc / side:** eu · other
**endpoint:** `/a/updatePanelMemberProfile.do`
**dates:** 2026-06-23
**affected hosts:** pveuqpweb4.questionpro.net
**error ids (sample 1/1):** 550694

**root cause:**
```
You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near ')  )  )' at line 1
```

**codebase frames:**
```
at com.bhaskaran.database.PreparedConnectionCommand.executeWithConnection(PreparedConnectionCommand.java:75)
at com.bhaskaran.database.ConnectionCommand.execute(ConnectionCommand.java:66)
at com.bhaskaran.database.PreparedConnectionCommand.execute(PreparedConnectionCommand.java:117)
at com.bhaskaran.database.CountCommand.executeLong(CountCommand.java:31)
at com.surveyconsole.micropanel.Panel.getPanelMemberCount(Panel.java:4891)
at com.surveyconsole.micropanel.Panel.hydratePanelMember(Panel.java:11543)
```

---

### 16. You have an error in your SQL syntax; check the manual that correspond *(low, 1 hits)*

**dc / side:** eu · other
**endpoint:** `/a/updatePanelMemberProfile.do`
**dates:** 2026-06-23
**affected hosts:** pveuqpweb4.questionpro.net
**error ids (sample 1/1):** 550704

**root cause:**
```
You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near ')  )  )' at line 1
```

**codebase frames:**
```
at com.bhaskaran.database.PreparedConnectionCommand.executeWithConnection(PreparedConnectionCommand.java:75)
at com.bhaskaran.database.ConnectionCommand.execute(ConnectionCommand.java:66)
at com.bhaskaran.database.PreparedConnectionCommand.execute(PreparedConnectionCommand.java:117)
at com.bhaskaran.database.CountCommand.executeLong(CountCommand.java:31)
at com.surveyconsole.micropanel.Panel.getPanelMemberCount(Panel.java:4891)
at com.surveyconsole.micropanel.Panel.hydratePanelMember(Panel.java:11543)
```

---

### 17. java.net.SocketTimeoutException: Read timed out *(low, 1 hits)*

**dc / side:** us · other
**endpoint:** `(unknown)`
**dates:** 2026-06-24
**affected hosts:** qpweb2.questionpro.net
**error ids (sample 1/1):** 569482

**root cause:**
```
java.net.SocketTimeoutException: Read timed out
```

**codebase frames:**
```
at com.surveyconsole.httputil.ApacheHttpUtility.sendPost(ApacheHttpUtility.java:78)
at com.surveyconsole.batch.ProcessingItemNotifier.notifyProgress(ProcessingItemNotifier.java:44)
at com.surveyconsole.batch.ProcessingItem.notifyProgress(ProcessingItem.java:586)
at com.surveyconsole.batch.ProcessingItem.updateProgress(ProcessingItem.java:597)
at com.surveyconsole.batch.ProcessingItem.updateProgress(ProcessingItem.java:605)
at com.surveyconsole.campaign.PanelSendSurveyInvitationProcessor.sendInvitationToMembers(PanelSendSurveyInvitationProcessor.java:167)
```

---

### 18. java.lang.NullPointerException: Cannot invoke "com.surveyconsole.user. *(low, 1 hits)*

**dc / side:** us · other
**endpoint:** `(unknown)`
**dates:** 2026-06-24
**affected hosts:** qpweb3.questionpro.net
**error ids (sample 1/1):** 570128

**request context:**

- referer: `null`

**root cause:**
```
java.lang.NullPointerException: Cannot invoke "com.surveyconsole.user.User.hasSmtpSettings()" because "<local40>" is null
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

### 19. java.lang.NullPointerException: Cannot invoke "com.surveyconsole.micro *(low, 1 hits)*

**dc / side:** qa · other
**endpoint:** `/a/inviteUsers.do`
**dates:** 2026-06-24
**affected hosts:** saqaapp1.questionpro.net
**error ids (sample 1/1):** 570964

**request context:**

- referer: `https://qa.surveyanalytics.com/a/showPanelUserReport.do?lcfpn=false`
- params: `ajax=true&engine=dojo&text=selenium-communities+test+sa@questionpro.com,TestTest123,7894561239,TestA,TestB,TestC,Selenium@123&info=-1`

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

## pdm report

```
65 errors logged (2026-06-19 → 2026-06-25)

us dc — 0 panel, 0 portal
eu dc — 1 panel, 1 portal
qa    — 0 panel, 1 portal  (non-production)
```

---

## engineering update

```
65 errors | panel-0, portal-0 (us) | panel-1, portal-1 (eu)

~ 15  : [2026-06-22] root exception :
org.apache.xmlrpc.xmlrpcexception: failed to create input stream: server returned h — unknown endpoint
~ 14  : [2026-06-20→2026-06-24] com.bhaskaran.database.databaseerror: you have an error in your sql syntax; check the manual that co — /a/panel.do
~ 7   : [2026-06-22] java.util.nosuchelementexception: no value present — /a/renameUserFile.do
~ 6   : [2026-06-24] java.lang.nullpointerexception: cannot invoke "com.surveyconsole.micropanel.panelmember.getselectedl — /a/showQPointInventory.do
```