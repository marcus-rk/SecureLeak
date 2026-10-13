# 0002. One visibility policy, default deny

Status: accepted
Recorded: 2026-10. Decided: 2025-11-03 (66b3e03)

One function, `is_report_viewable` (`security/reports_access.py:6-24`), decides whether a report is viewable. The report page, comment and image routes all call it (`routes/reports.py:105`, `:120`, `:146`). For non-admins, any status it does not recognise is denied (`security/reports_access.py:23-24`). The admin override was added later in 0b71b9a (2025-12-05) (`security/reports_access.py:14-16`).

## Why

One function decides whether a report is viewable for the report page, comment and image routes, so one fix covers all three and the routes cannot drift apart. It can also be tested on its own. Any status the function does not recognise is denied, so a new or misspelled status can never expose a report.

## Considered options

- Filtering in SQL only, with no policy function: "considered, but not for this PoC" (maintainer's words).
- A permission or ACL table per report: "considered, but not for this PoC" (maintainer's words).
- A library such as Flask-Principal: "considered, but not for this PoC" (maintainer's words).

## Consequences

- A closed report is not viewable by a non-admin owner only as a side effect of default deny (`security/reports_access.py:19-24`). This was not decided. That owner's list still includes their closed reports (`repository/reports_repo.py:40`), so opening one gives 404. Treat this as undecided, not as intended.
- The admin override reads the role from the session (`routes/reports.py:104`), not the database. Whether it should was not decided (see [ADR 0005](0005-admin-role-not-self-assignable.md)).
- No unit test of `is_report_viewable` exists. Partial enforcement: `tests/reports/test_uploads.py::test_upload_public_and_private_access` (non-owner on a private image gets 404) and `tests/security/test_permissions.py` (non-owner on a private report page and comment gets 404).

If reversed: inlining the check per route, or adding a status without updating the policy, lets the routes drift. Do not make a new status viewable by default, and do not change closed-report behaviour until the maintainer decides it. Only partly enforced by a test (see above).
