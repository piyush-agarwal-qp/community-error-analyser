# weekly error report — 2026-06-19 to 2026-06-25

**date range:** 2026-06-19 → 2026-06-25
**total errors:** 65
**clusters:** 19

---

## summary table

| # | severity | error type | count | dc | side |
|---|----------|-----------|-------|-----|------|
| 1 | high | Root Exception : | 15 | EU | other |
| 2 | high | java.lang.reflect.InvocationTargetException | 14 | EU+QA | portal |
| 3 | medium | java.util.NoSuchElementException: No value present | 7 | QA+US | other |
| 4 | medium | java.lang.NullPointerException: Cannot invoke "com.surveyconsole.micropanel.Pane | 6 | US | other |
| 5 | medium | java.lang.reflect.InvocationTargetException | 4 | EU | panel |
| 6 | low | java.lang.NullPointerException: Cannot invoke "com.surveyconsole.run.RunSurveySh | 4 | QA | other |
| 7 | low | Root Exception : | 2 | EU | other |
| 8 | low | java.lang.IndexOutOfBoundsException: Index 0 out of bounds for length 0 | 2 | US | other |
| 9 | low | You have an error in your SQL syntax; check the manual that corresponds to your  | 1 | EU | other |
| 10 | low | UserPreparedStatement[SpyPreparedStatement[null]] | 1 | QA | other |
| 11 | low | UserPreparedStatement[SpyPreparedStatement[null]] | 1 | US | other |
| 12 | low | java.lang.UnsupportedOperationException | 1 | EU | other |
| 13 | low | You have an error in your SQL syntax; check the manual that corresponds to your  | 1 | EU | other |
| 14 | low | You have an error in your SQL syntax; check the manual that corresponds to your  | 1 | EU | other |
| 15 | low | You have an error in your SQL syntax; check the manual that corresponds to your  | 1 | EU | other |
| 16 | low | You have an error in your SQL syntax; check the manual that corresponds to your  | 1 | EU | other |
| 17 | low | java.net.SocketTimeoutException: Read timed out | 1 | US | other |
| 18 | low | java.lang.NullPointerException: Cannot invoke "com.surveyconsole.user.User.hasSm | 1 | US | other |
| 19 | low | java.lang.NullPointerException: Cannot invoke "com.surveyconsole.micropanel.Pane | 1 | QA | other |

---

## dc & side breakdown

| dc | portal | panel | other |
|----|--------|-------|-------|
| us | 0 | 0 | 6 |
| eu | 1 | 1 | 8 |
| qa | 1 | 0 | 4 |

---

## cluster details

### 1. Root Exception : *(high, 15 errors)*

**dc / side:** eu · other
**endpoint:** (unknown)
**affected hosts:** pveuadminapp1.questionpro.net, pveuqprun4.questionpro.net, pveuqpweb1.questionpro.net, pveuqpweb2.questionpro.net, pveuqpweb3.questionpro.net, pveuqpweb4.questionpro.net
**error ids (sample):** 519700, 519716, 519740 *(15 total)*

**stack trace:**
```
Error Logged Thread : com.surveyconsole.builder.ListSurveysAction<BR><BR>Root Exception :
org.apache.xmlrpc.XmlRpcException: Failed to create input stream: Server returned HTTP response code: 502 for URL: http://eu-data.questionpro.net/a/xmlrpc
	at org.apache.xmlrpc.client.XmlRpcSunHttpTransport.getInputStream(XmlRpcSunHttpTransport.java:65)
	at org.apache.xmlrpc.client.XmlRpcStreamTransport.sendRequest(XmlRpcStreamTransport.java:141)
	at org.apache.xmlrpc.client.XmlRpcHttpTransport.sendRequest(XmlRpcHttpTransport.java:94)
	at org.apache.xmlrpc.client.XmlRpcSunHttpTransport.sendRequest(XmlRpcS
```

---

### 2. java.lang.reflect.InvocationTargetException *(high, 14 errors)*

**dc / side:** eu + qa · portal
**endpoint:** (unknown)
**affected hosts:** pveuadminapp1.questionpro.net, pveuqprun1.questionpro.net, pveuqprun3.questionpro.net, pveuqprun4.questionpro.net, qaweb2
**error ids (sample):** 511277, 519643, 521964 *(14 total)*

**stack trace:**
```
AJSServlet : {"headers":{"referer":"https://fivebargatefarming.questionpro.eu/a/panel.do?id=1602639204&tabIndex=","cf-ipcountry":"GB","sec-fetch-site":"same-origin","origin":"https://fivebargatefarming.questionpro.eu","sec-ch-ua-mobile":"?0","cf-visitor":"{\"scheme\":\"https\"}","content-type":"application/json; charset=UTF-8","cf-connecting-ip":"185.114.123.240","Content-Length":"1462","X-Real-IP":"fivebargatefarming.questionpro.eu","sec-fetch-mode":"cors","cdn-loop":"cloudflare; loops=1","cf-<BR><BR>java.lang.reflect.InvocationTargetException
	at java.base/jdk.internal.reflect.DirectMethodHa
```

---

### 3. java.util.NoSuchElementException: No value present *(medium, 7 errors)*

**dc / side:** qa + us · other
**endpoint:** /a/renameUserFile.do
**affected hosts:** pvqpadminapp1.questionpro.net, qaweb2
**error ids (sample):** 521111, 521116, 521118 *(7 total)*

**stack trace:**
```
[/a/renameUserFile.do][ajax=true&engine=dojo&mode=update&userFileID=4204224&pageOffset=0&folderID=0&text=drtjkl&type=null][ Active Index = 5 Current Survey = ID = 13608952 Num Surveys : 1104 Email : payal.pandey@questionpro.com] Referrer [https://qa-priority.questionpro.com/a/showImageLibrary.do?lcfpn=false] User-Agent [Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36] Remote Address [123.201.33.202] HTTP Method [POST] <BR><BR>java.util.NoSuchElementException: No value present
	at java.base/java.util.Optional.get(Optional.java:143)
```

---

### 4. java.lang.NullPointerException: Cannot invoke "com.surveycon *(medium, 6 errors)*

**dc / side:** us · other
**endpoint:** /a/jsp/includes/error.jsp
**affected hosts:** pvqpadminapp1.questionpro.net
**error ids (sample):** 564124, 564125, 564127 *(6 total)*

**stack trace:**
```
JSP Error: [/a/jsp/includes/error.jsp][ajax=true&engine=dojo][ Active Index = 0 Current Survey = ID = 13648022 Num Surveys : 1105 Email : payal.pandey@questionpro.com] Referrer [https://admin.questionpro.com/a/showQPointInventory.do?lcfpn=false] User-Agent [Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36] Remote Address [103.249.243.80] HTTP Method [GET] <BR><BR>java.lang.NullPointerException: Cannot invoke "com.surveyconsole.micropanel.PanelMember.getSelectedLanguage()" because "member" is null
	at com.surveyconsole.micropanel.re
```

---

### 5. java.lang.reflect.InvocationTargetException *(medium, 4 errors)*

**dc / side:** eu · panel
**endpoint:** survey-angular.panel.PanelDiscussionTopicAJSHandler-GetActiveTopics
**affected hosts:** pveuqpweb2.questionpro.net
**error ids (sample):** 564176, 564177, 564178 *(4 total)*

**stack trace:**
```
AJSServlet : {"headers":{"referer":"https://eu.questionpro.com/a/showDiscussionModeration.do","cf-ipcountry":"DE","sec-fetch-site":"same-origin","origin":"https://eu.questionpro.com","sec-ch-ua-full-version-list":"\"Microsoft Edge\";v=\"149.0.4022.80\", \"Chromium\";v=\"149.0.7827.156\", \"Not)A;Brand\";v=\"24.0.0.0\"","sec-ch-ua-mobile":"?0","cf-visitor":"{\"scheme\":\"https\"}","content-type":"application/json; charset=UTF-8","cf-connecting-ip":"94.135.161.38","Content-Length":"33","X-Real-IP<BR><BR>java.lang.reflect.InvocationTargetException
	at java.base/jdk.internal.reflect.DirectMethodHa
```

---

### 6. java.lang.NullPointerException: Cannot invoke "com.surveycon *(low, 4 errors)*

**dc / side:** qa · other
**endpoint:** /a/takeProfileSurvey.do
**affected hosts:** qaweb2
**error ids (sample):** 544298, 544357, 544369 *(4 total)*

**stack trace:**
```
[/a/takeProfileSurvey.do][mode=continue&cf_466054_year=-1&segID=0&cf_466054_day=1&cf_466055=&cf_466054_month=1&submit=Continue][ Active Index = 0 Current Survey = ID = 13648022 Num Surveys : 1105 Email : payal.pandey@questionpro.com] Referrer [https://qa-priority.questionpro.com/a/TakeSurvey?tt=YiyJTkNkMQiMuk7Y1EUFpg%3D%3D&lcfpn=false] User-Agent [Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0] Remote Address [123.20<BR><BR>java.lang.NullPointerException: Cannot invoke "com.surveyconsole.run.RunSurveyShell.getPanelM
```

---

### 7. Root Exception : *(low, 2 errors)*

**dc / side:** eu · other
**endpoint:** /a/panelLanguageTranslationImport.do
**affected hosts:** pveuadminapp1.questionpro.net
**error ids (sample):** 523259, 523315 *(2 total)*

**stack trace:**
```
[/a/panelLanguageTranslationImport.do][ajax=true&engine=dojo&mode=import][ Active Index = 0 Current Survey = ID = 1603066038 Num Surveys : 318 Email : muzaffar.quraishi+eu@questionpro.com] Referrer [https://euadmin.questionpro.com/a/editLanguage.do?mode=importTranslation&lcfln=false] User-Agent [Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36] Remote Address [123.201.33.202] HTTP Method [POST] <BR><BR>Root Exception :
java.lang.ArrayIndexOutOfBoundsException: Index 164 out of bounds for length 164
	at com.surveyconsole.micropanel.
```

---

### 8. java.lang.IndexOutOfBoundsException: Index 0 out of bounds f *(low, 2 errors)*

**dc / side:** us · other
**endpoint:** /a/loadResponse.do
**affected hosts:** qpweb1.questionpro.net
**error ids (sample):** 525151, 525158 *(2 total)*

**stack trace:**
```
[/a/loadResponse.do][surveyID=13323446&responseSetID=148363643][ Active Index = 158 Current Survey = ID = 13323446 Num Surveys : 279 Email : thomas.conrad@salesfactory.com] Referrer [https://www.questionpro.com/a/frame.do?mode=viewIndividual&surveyID=96MFJ1fhrO1LHktMsTJTtheAMmtUhQRU_NKHxHsqV0Y-&responseSetID=UQtludCvtTAmWwC1AZmuKnIpDCtNsYxZk6SFUpVXSpQ-] User-Agent [Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36] Remote Addre<BR><BR>java.lang.IndexOutOfBoundsException: Index 0 out of bounds for length 0
	at java.base/jdk.int
```

---

### 9. You have an error in your SQL syntax; check the manual that  *(low, 1 errors)*

**dc / side:** eu · other
**endpoint:** /a/updatePanelMemberProfile.do
**affected hosts:** pveuqpweb1.questionpro.net
**error ids (sample):** 494739 *(1 total)*

**stack trace:**
```
[/a/updatePanelMemberProfile.do][cf_25638_year=-1&pageOffset=0&cf_28584=569560&cf_25635=-1&id=8391011&cf_25639=525360&cf_25638_month=-1&cf_25617_month=1&ajax=true&cf_25638_hour=-1&cf_25638_min=-1&cf_27585=&cf_25617_day=31&engine=dojo&cf_27471=-1&cf_25610=An&cf_25611=Cade&cf_25612=7769976968&cf_25613=a.cade63@btinternet.com&cf_25614=&cf_25615=525054&cf_25616=525252&cf_25618=525261&cf_25617_year=1963&cf_25619=525267&cf_25620=525281&cf_25621=525288&cf_25622=344&cf_25623=525289&cf_25638_day=Day&cf_<BR><BR>You have an error in your SQL syntax; check the manual that corresponds to your MySQL server
```

---

### 10. UserPreparedStatement[SpyPreparedStatement[null]] *(low, 1 errors)*

**dc / side:** qa · other
**endpoint:** /a/inviteUsers.do
**affected hosts:** qa11
**error ids (sample):** 515188 *(1 total)*

**stack trace:**
```
[/a/inviteUsers.do][ajax=true&engine=dojo&text=selenium-communities+test+au@questionpro.com,TestTest123,7894561239,TestA,TestB,TestC,Selenium@123&info=-1][ Active Index = -1 Current Survey = Null Num Surveys : 0 Email : selenium+au+cctest+communities+sanityparalleltest@questionpro.com] Referrer [https://auqa.questionpro.com/a/showPanelUserReport.do?lcfpn=false] User-Agent [Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/145.0.0.0 Safari/537.36] Remote Addre<BR><BR>UserPreparedStatement[SpyPreparedStatement[null]]
Duplicate entry '4007366-selenium-communit
```

---

### 11. UserPreparedStatement[SpyPreparedStatement[null]] *(low, 1 errors)*

**dc / side:** us · other
**endpoint:** /a/editPanelMember.do
**affected hosts:** qpweb1.questionpro.net
**error ids (sample):** 525161 *(1 total)*

**stack trace:**
```
[/a/editPanelMember.do][engine=dojo&moderator=0&mobileNumber=2037677354&pageOrigin=&username=Metmadison&ID=83390501&custom1=&custom2=&custom3=&countryCode=+1&lastname=Madison&middlename=&userAction=save&ajax=true&custom4=&custom5=&status=2&emailAddress=metmadison752@outlook.com&defaultLanguage=0&firstname=Met][ Active Index = 126 Current Survey = ID = 13431280 Num Surveys : 279 Email : thomas.conrad@salesfactory.com] Referrer [https://www.questionpro.com/a/showPanelUserReport.do?lcfpn=false] Us<BR><BR>UserPreparedStatement[SpyPreparedStatement[null]]
Duplicate entry '149770-80439514-80439514-
```

---

### 12. java.lang.UnsupportedOperationException *(low, 1 errors)*

**dc / side:** eu · other
**endpoint:** /a//stopBroadcastProcess.do
**affected hosts:** pveuqpweb3.questionpro.net
**error ids (sample):** 543290 *(1 total)*

**stack trace:**
```
[/a//stopBroadcastProcess.do][ajax=true&engine=dojo&id=1604333467][ Active Index = 2 Current Survey = ID = 1603036405 Num Surveys : 31 Email : llrccgs.beinvolved@nhs.net] Referrer [https://eu.questionpro.com/a/showPanelBroadcastEmail.do?lcfpn=false] User-Agent [Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36] Remote Address [145.40.133.35] HTTP Method [GET] <BR><BR>java.lang.UnsupportedOperationException
	at java.base/java.lang.Thread.stop(Thread.java:1667)
	at com.surveyconsole.batch.LongProcessHandler.stopProcess(LongProcessHand
```

---

### 13. You have an error in your SQL syntax; check the manual that  *(low, 1 errors)*

**dc / side:** eu · other
**endpoint:** /a/updatePanelMemberProfile.do
**affected hosts:** pveuqpweb4.questionpro.net
**error ids (sample):** 544300 *(1 total)*

**stack trace:**
```
[/a/updatePanelMemberProfile.do][cf_25638_year=-1&pageOffset=0&cf_28584=569561&cf_25635=525349&id=23176188&cf_25639=-1&cf_25638_month=-1&cf_25617_month=9&ajax=true&cf_25638_hour=-1&cf_25638_min=-1&cf_27585=&cf_25617_day=29&engine=dojo&cf_27471=-1&cf_25610=Mark&cf_25611=Palmer&cf_25612=&cf_25613=&cf_25614=&cf_25615=525054&cf_25616=525260&cf_25618=525261&cf_25617_year=1963&cf_25619=-1&cf_25620=525282&cf_25621=-1&cf_25622=&cf_25623=-1&cf_25638_day=Day&cf_25625=-1&cf_25626=-1&cf_25627=-1&cf_25624=-<BR><BR>You have an error in your SQL syntax; check the manual that corresponds to your MySQL server
```

---

### 14. You have an error in your SQL syntax; check the manual that  *(low, 1 errors)*

**dc / side:** eu · other
**endpoint:** /a/updatePanelMemberProfile.do
**affected hosts:** pveuqpweb4.questionpro.net
**error ids (sample):** 544303 *(1 total)*

**stack trace:**
```
[/a/updatePanelMemberProfile.do][cf_25638_year=-1&pageOffset=0&cf_28584=569561&cf_25635=525349&id=23176188&cf_25639=-1&cf_25638_month=-1&cf_25617_month=9&ajax=true&cf_25638_hour=-1&cf_25638_min=-1&cf_27585=&cf_25617_day=29&engine=dojo&cf_27471=-1&cf_25610=Mark&cf_25611=Palmer&cf_25612=&cf_25613=mark@systems4food.co.uk&cf_25614=&cf_25615=525054&cf_25616=525260&cf_25618=525261&cf_25617_year=1963&cf_25619=-1&cf_25620=525282&cf_25621=-1&cf_25622=&cf_25623=-1&cf_25638_day=Day&cf_25625=-1&cf_25626=-1<BR><BR>You have an error in your SQL syntax; check the manual that corresponds to your MySQL server
```

---

### 15. You have an error in your SQL syntax; check the manual that  *(low, 1 errors)*

**dc / side:** eu · other
**endpoint:** /a/updatePanelMemberProfile.do
**affected hosts:** pveuqpweb4.questionpro.net
**error ids (sample):** 550694 *(1 total)*

**stack trace:**
```
[/a/updatePanelMemberProfile.do][cf_25638_year=2024&pageOffset=0&cf_28584=569557&cf_25635=-1&id=8396342&cf_25639=525359&cf_25638_month=9&cf_25617_month=6&ajax=true&cf_25638_hour=14&cf_25638_min=37&cf_27585=&cf_25617_day=18&engine=dojo&cf_27471=-1&cf_25610=claire&cf_25611=matthews&cf_25612=7778703010&cf_25613=claire@timmatthews.co.uk&cf_25614=&cf_25615=525054&cf_25616=525252&cf_25618=525262&cf_25617_year=1966&cf_25619=525267&cf_25620=525281&cf_25621=525287&cf_25622=45&cf_25623=525291&cf_25638_da<BR><BR>You have an error in your SQL syntax; check the manual that corresponds to your MySQL server
```

---

### 16. You have an error in your SQL syntax; check the manual that  *(low, 1 errors)*

**dc / side:** eu · other
**endpoint:** /a/updatePanelMemberProfile.do
**affected hosts:** pveuqpweb4.questionpro.net
**error ids (sample):** 550704 *(1 total)*

**stack trace:**
```
[/a/updatePanelMemberProfile.do][cf_25638_year=2024&pageOffset=0&cf_28584=569557&cf_25635=-1&id=8396342&cf_25639=525359&cf_25638_month=9&cf_25617_month=6&ajax=true&cf_25638_hour=14&cf_25638_min=37&cf_27585=&cf_25617_day=18&engine=dojo&cf_27471=-1&cf_25610=claire&cf_25611=matthews&cf_25612=7778703010&cf_25613=claire@timmatthews.co.uk&cf_25614=&cf_25615=525054&cf_25616=525252&cf_25618=525262&cf_25617_year=1966&cf_25619=525267&cf_25620=525281&cf_25621=525287&cf_25622=45&cf_25623=525291&cf_25638_da<BR><BR>You have an error in your SQL syntax; check the manual that corresponds to your MySQL server
```

---

### 17. java.net.SocketTimeoutException: Read timed out *(low, 1 errors)*

**dc / side:** us · other
**endpoint:** (unknown)
**affected hosts:** qpweb2.questionpro.net
**error ids (sample):** 569482 *(1 total)*

**stack trace:**
```
Error In Processing Item While_Notifying Progress<BR><BR>java.net.SocketTimeoutException: Read timed out
	at java.base/sun.nio.ch.NioSocketImpl.timedRead(NioSocketImpl.java:278)
	at java.base/sun.nio.ch.NioSocketImpl.implRead(NioSocketImpl.java:304)
	at java.base/sun.nio.ch.NioSocketImpl.read(NioSocketImpl.java:346)
	at java.base/sun.nio.ch.NioSocketImpl$1.read(NioSocketImpl.java:796)
	at java.base/java.net.Socket$SocketInputStream.read(Socket.java:1099)
	at java.base/sun.security.ssl.SSLSocketInputRecord.read(SSLSocketInputRecord.java:489)
	at java.base/sun.security.ssl.SSLSocketInputRecord.r
```

---

### 18. java.lang.NullPointerException: Cannot invoke "com.surveycon *(low, 1 errors)*

**dc / side:** us · other
**endpoint:** /a/jsp/includes/error.jsp
**affected hosts:** qpweb3.questionpro.net
**error ids (sample):** 570128 *(1 total)*

**stack trace:**
```
JSP Error: [/a/jsp/includes/error.jsp][ajax=true&engine=dojo] No User Object in Session Referrer [null] User-Agent [Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.6998.35/36 Safari/537.36] Remote Address [152.163.120.210] HTTP Method [GET] <BR><BR>java.lang.NullPointerException: Cannot invoke "com.surveyconsole.user.User.hasSmtpSettings()" because "<local40>" is null
	at _jsp._jsp._survey._sendsurvey._compose._email._fromEmailDropDown__jsp._jspService(_fromEmailDropDown__jsp.java:1748)
	at _jsp._jsp._survey._sendsurvey._compose._email._fromEmailDr
```

---

### 19. java.lang.NullPointerException: Cannot invoke "com.surveycon *(low, 1 errors)*

**dc / side:** qa · other
**endpoint:** /a/inviteUsers.do
**affected hosts:** saqaapp1.questionpro.net
**error ids (sample):** 570964 *(1 total)*

**stack trace:**
```
[/a/inviteUsers.do][ajax=true&engine=dojo&text=selenium-communities+test+sa@questionpro.com,TestTest123,7894561239,TestA,TestB,TestC,Selenium@123&info=-1][ Active Index = 0 Current Survey = ID = 3334149 Num Surveys : 2 Email : selenium+sa+cctest+communities+samplingtest@questionpro.com] Referrer [https://qa.surveyanalytics.com/a/showPanelUserReport.do?lcfpn=false] User-Agent [Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/145.0.0.0 Safari/537.36] Remote Ad<BR><BR>java.lang.NullPointerException: Cannot invoke "com.surveyconsole.micropanel.PanelMemberFieldV
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

~ 15  : root exception : — unknown endpoint
~ 14  : java.lang.reflect.invocationtargetexception — unknown endpoint
~ 7   : java.util.nosuchelementexception: no value present — /a/renameUserFile.do
~ 6   : java.lang.nullpointerexception: cannot invoke "com.surveyconsole.micropanel.pane — /a/jsp/includes/error.jsp
```