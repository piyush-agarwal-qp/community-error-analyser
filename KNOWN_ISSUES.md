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
- **Count trend:** 438 (week of May 29–Jun 4)
- **Affected:** All US qprun nodes (1–11), all Communities tenants
- **Exception:** `java.lang.reflect.InvocationTargetException` in `PortalDashBoardAJSHandler-GetTaskDetails`
- **Status:** Open — root cause (wrapped exception) not yet retrieved from Resin logs
- **Notes:** Accounts for 87% of all weekly errors. Needs `.getCause()` pulled from full Resin log.

---

### KI-002 · GetSurveyDetails AJS Failure — EU Production
- **Severity:** High
- **First seen:** 2026-06-04 (`error_report_2026-06-04.md`, cluster 2)
- **Last seen:** 2026-06-04
- **Count trend:** 15 (week of May 29–Jun 4)
- **Affected:** pveuqprun2, pveuqprun4 — onepoll EU tenants
- **Exception:** `java.lang.reflect.InvocationTargetException` in `PortalDashBoardAJSHandler-GetSurveyDetails`
- **Status:** Open — may share root cause with KI-001 or be independent
- **Notes:** Investigate alongside KI-001; use QA (qa11) to reproduce.

---

### KI-003 · Panel Language Translation Import Failure — EU
- **Severity:** Medium
- **First seen:** 2026-06-04 (`error_report_2026-06-04.md`, cluster 6)
- **Last seen:** 2026-06-04
- **Count trend:** 3 (week of May 29–Jun 4)
- **Affected:** pveuqpweb3, pveuqpweb4 — customer `trpresearch.com`
- **Exception:** `ArrayIndexOutOfBoundsException` (off-by-one) + `NullPointerException` on `PanelDetail.getID()` in `com.surveyconsole.micropanel.language.PanelTranslation`
- **Status:** Open
- **Notes:** Same customer, same endpoint, two different failure paths — both in PanelTranslation import loop.

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
