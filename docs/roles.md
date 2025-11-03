# Roles, Authorization, and Admin Area

A compact reference for how roles are represented and enforced, and how the Admin dashboard works. The design is intentionally small and explicit to stay exam‑friendly.

## Roles

Two roles exist in this app:

- user (developer)
- admin

Where they live:

- Database: `users.role` (TEXT CHECK constraint)
- Session: `session['role']` set at login alongside `session['user_id']`

Why in session?

- Keeps authorization checks cheap and centralized in decorators
- During login logout boundaries we call `session.clear()` to avoid fixation and then store minimal identity fields only

## Decorators

We use tiny, self‑made decorators in `security/decorators.py`.

- `@login_required`
  - If not authenticated, flash a hint and redirect to `auth.login`.
- `@require_role('admin')`
  - If unauthenticated → redirect to login (same as `@login_required`).
  - If authenticated but wrong role → `abort(404)` (info‑hiding; don’t leak that an admin page exists).

Notes:

- Returning 404 for unauthorized avoids making role/feature discovery easier.
- Use 404 consistently for private resources even if authenticated.

## Admin Dashboard

Minimal, secure dashboard for changing report status. Implemented in `routes/admin.py` with a separate Blueprint.

Routes:

- `GET /admin` → dashboard list of recent reports.
- `POST /admin/reports/<id>/status` → change to `public | private | closed`.

Security rules:

- All admin routes use `@require_role('admin')`.
- All POST actions include `{{ csrf_token() }}` and are protected by `CSRFProtect`.
- POSTs validate the requested status against a whitelist.
- Successful updates use PRG: redirect 303 back to `/admin`.

Repository helpers:

- `repository/reports_repo.py` exposes `update_status(report_id, status)` that enforces a whitelist and uses parameterized SQL.
- `list_all(limit, offset)` is used by the dashboard to render a compact table including `owner_username`.

Template (`templates/admin_dashboard.html`):

- A simple table with one row per report and three POST buttons (Public, Private, Close), each as a tiny form with CSRF.
- Keeps styling consistent with the rest of the app (`.card`, `.actions`).

## Authorization Matrix (short)

| Resource | user | admin |
|:---------|:-----|:------|
| /reports (list/detail/new) | ✅ | ✅ |
| /reports/<id>/comment (POST) | ✅ (public or own private) | ✅ |
| /admin | ❌ (404) | ✅ |
| /admin/reports/<id>/status (POST) | ❌ (404) | ✅ |

## Status & Visibility

Report `status` values:

- `public` → visible to all authenticated users
- `private` → visible to owner and admins
- `closed` → treated like public/private for visibility, but signals no new work; rendering remains the same (simplicity)

Admin actions only change the `status` field; they do not edit content or ownership.

## Testing Hints

- Use `https` base_url and a Referer header for CSRF‑related tests (consistent with existing tests).
- Non‑admin access to `/admin` and `/admin/.../status` should 404 when logged in, and redirect to login when not.
- Changing status should 303 back to `/admin` and flash Success.

## Trade‑offs

- Decorators are simple and explicit — good for teaching and small projects. Larger apps might use Flask‑Login or a policy engine (e.g., Flask‑Principal) for more complex rules.
- The dashboard is intentionally minimal: no pagination or search (KISS). For larger datasets, extend `list_all` and add filters.
