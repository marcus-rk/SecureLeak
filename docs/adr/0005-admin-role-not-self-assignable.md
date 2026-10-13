# 0005. The admin role is assigned outside the website

Status: accepted
Recorded: 2026-10. Decided: 2025-11-02 (fbdb5c9) for part 1, 2025-11-09 (ba83f8a) for part 2

Registration always creates the role `user` and ignores any client-supplied role (`routes/auth.py:76-77`). Admins exist only through seed data, via the `role` column of `seed/users.csv` read at `seed/seed_runner.py:125`. No route promotes or demotes an account: the only `update_user` call in `routes/` is the password hash upgrade (`routes/auth.py:52`). Separately, every request to an admin route re-reads the role from the database (`security/decorators.py:51-59`), added in ba83f8a.

## Why

Part 1: promotion to admin needs a manual step outside the website, which lowers risk. The maintainer's words: "I think it was to enforce someone had to do it non-through the website for lower risk. Meaning manual behind the scene was needed".

Part 2: the maintainer does not recall the reason. [docs/roles.md](../roles.md):30-31, written later in 42c3e9b (2025-12-05), states the aim "to ensure a demoted admin loses access immediately".

## Considered options

An admin-promotion UI or CLI command was also thought about. It was not chosen because promotion should need a manual step outside the website. No other alternatives recorded.

## Consequences

- The admin override in the visibility policy reads the role from the session (`routes/reports.py:104`, then `security/reports_access.py:14-16`), not the database. Whether the database re-check should also cover it was not decided. See [ADR 0002](./0002-single-visibility-policy.md).
- Tests: `tests/seed/test_seed_runner.py::test_valid_seed_password_seeds_admin_that_can_authenticate` asserts that seeding creates `admin1@mail.com` with role `admin` and that it can authenticate. Forcing role `user` at registration is not enforced by a test. The admin-route database re-check is enforced by `tests/security/test_permissions.py::test_demoted_admin_gets_404_on_admin_dashboard_despite_admin_session`.

If reversed: accepting a role field at registration, or adding a promotion route, lets anyone become admin through the website; trusting only the session role keeps a demoted admin's access until the session ends. Do not add a role field to registration or a web promotion flow.
