# SecureLeak

A small tracker where accounts submit vulnerability reports and admins review them. This file fixes the project's vocabulary and the rules that must always hold. Threats and defences are described in [docs/security_model.md](docs/security_model.md); decisions are in [docs/adr/](docs/adr/).

## Language

### People

**User**:
A registered account with the role `user`. Can submit reports and comment on reports that are viewable to them (`database/migrations/init.sql:10`, `docs/roles.md`).
_Avoid_: Developer, reporter, member

**Admin**:
An account with the role `admin`. Every report is viewable by an admin (`security/reports_access.py:15-16`), and only an admin changes a report's status (`routes/admin.py:18-21`).
_Avoid_: Moderator, superuser

**Role**:
The single access level of an account: `user` or `admin` (`database/migrations/init.sql:10`).
_Avoid_: Permission, group

### Reports

**Report**:
A vulnerability report: title, description, severity, status and at most one image, owned by the account that submitted it (`database/migrations/init.sql:14-24`).
_Avoid_: Bug, leak, ticket, issue

**Owner**:
The account (user or admin) that submitted a report (`database/migrations/init.sql:16`).
_Avoid_: Author (for reports), submitter, creator

**Status**:
The one field that says both who can see a report and whether it is still open: `public`, `private` or `closed` (`database/migrations/init.sql:21`).
_Avoid_: Visibility (as a field name), state

**Public report**:
A report with status `public`; viewable by every signed-in account (`security/reports_access.py:19-20`, `routes/reports.py:96,112,137`).

**Private report**:
A report with status `private`; viewable only by its owner and admins (`security/reports_access.py:21-22`).

**Closed report**:
A report with status `closed`; viewable by admins (`security/reports_access.py:15-16`). A non-admin owner currently cannot view it (`security/reports_access.py:23-24`), but that was not decided: see [ADR 0002](docs/adr/0002-single-visibility-policy.md).
_Avoid_: Resolved, archived

**Severity**:
How serious the reported vulnerability is: `low`, `medium` or `high` (`routes/reports.py:60`).
_Avoid_: Priority, criticality

**Viewable**:
Whether a given account may see a given report, as decided by the visibility policy.
_Avoid_: Accessible, visible, authorized

**Visibility policy**:
The single rule that decides whether a report is viewable, implemented as `is_report_viewable` (`security/reports_access.py:6-24`). See [ADR 0002](docs/adr/0002-single-visibility-policy.md).
_Avoid_: Access check, permission check

### Report content

**Comment**:
A text an account adds to a report it can view (`database/migrations/init.sql:26-34`, `routes/reports.py:120-124`).
_Avoid_: Reply, note, message

**Image**:
The optional picture belonging to a report, stored under a random name (`database/migrations/init.sql:19`, `security/uploads.py:47`, [docs/image_sanitization.md](docs/image_sanitization.md)).
_Avoid_: Attachment, upload, file, PoC, screenshot

## Invariants

1. A public report is viewable by any signed-in account, a private report only by its owner and admins, a closed report by admins. Any other status is not viewable by a non-admin (`security/reports_access.py:15-24`). Whether a non-admin owner may view their own closed report is not decided ([ADR 0002](docs/adr/0002-single-visibility-policy.md)). Test: `tests/reports/test_uploads.py::test_upload_public_and_private_access` covers the image route for public and private reports only; `tests/security/test_permissions.py` covers a non-owner on a private report page and comment. Closed reports and admins viewing private reports are not enforced by a test.
2. For a signed-in account, access that is denied answers 404, never 403; a signed-out request is redirected to sign in (`security/decorators.py:20-22` for report routes, `:42-44` for admin routes) (`routes/reports.py:106,122,147`, `security/decorators.py:49,59`). Tests: `tests/reports/test_uploads.py::test_upload_public_and_private_access` (image route), `tests/security/test_permissions.py` (non-owner on a private report page and comment, regular user on the admin dashboard and status-change POST, demoted admin on the admin dashboard only, signed-out redirect). See [ADR 0001](docs/adr/0001-404-instead-of-403.md).
3. Only an admin changes a report's status, and only to `public`, `private` or `closed` (`routes/admin.py:18-21`). Partly enforced by a test: `tests/security/test_permissions.py::test_regular_user_gets_404_on_admin_dashboard_and_status_change` shows a regular user's status-change POST is refused and the status is unchanged. The allowed status values are not enforced by a test.
4. A report created through the website starts as `public` or `private`, never `closed` (`routes/reports.py:64`). Seed data can create `closed` reports directly (`seed/seed_runner.py:135-147`). Not enforced by a test.
5. Registration always creates the role `user`; admins come only from seed data (`routes/auth.py:76-77`, `seed/seed_runner.py:125`). Not enforced by a test. See [ADR 0005](docs/adr/0005-admin-role-not-self-assignable.md).
6. Every request to an admin route that passes the session role check re-reads the role from the database (`security/decorators.py:51-59`). Test: `tests/security/test_permissions.py::test_demoted_admin_gets_404_on_admin_dashboard_despite_admin_session` covers the admin dashboard only; the status-change route is not exercised with a stale admin session.
7. A comment needs a viewable report and 1 to 2000 characters (`routes/reports.py:120-126`). Partly enforced by a test: `tests/security/test_permissions.py::test_non_owner_comment_on_private_report_gets_404_and_stores_nothing` covers the viewable-report requirement; the 1 to 2000 character bounds are not enforced by a test.
8. An image is served only if the report is viewable and the requested name equals the stored name (`routes/reports.py:146-150`). Test: `tests/reports/test_uploads.py::test_upload_public_and_private_access` covers viewability only; the name check is not enforced by a test.
9. An image is accepted only with an allowed extension, is re-encoded before it is stored, and is stored under `UPLOADS_DIR`, which defaults to `uploads/`, outside `static/` (`routes/reports.py:68-73`, `security/uploads.py:12,50-67`, `app.py:43`). The extension and MIME checks live in the route, not in `store_report_image`. Test: `tests/reports/test_uploads.py::test_upload_disallowed_extension_returns_400` rejects a `.txt` file sent as `text/plain`, which the MIME check alone would also reject; the extension allowlist, re-encode and storage location are not enforced by a test on their own. See [ADR 0003](docs/adr/0003-image-re-encoding-and-private-storage.md).
10. Outside debug mode the app does not start without a `SECRET_KEY` (`app.py:29-41`). Test: `tests/security/test_secret_key.py`.
