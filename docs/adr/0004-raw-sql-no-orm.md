# 0004. Parameterised SQL by hand, no ORM

Status: accepted
Recorded: 2026-10. Decided: 2025-11-02 (ff594cf)

All data access lives in `repository/*.py` and uses the stdlib `sqlite3` module through `database/connection.py:8`. Every value is passed through a `?` placeholder. The only SQL built from strings joins column names taken from a hard-coded allowlist (`repository/users_repo.py:57-64`, `repository/reports_repo.py:56-63`); the values in those statements still use `?`. The repository layer was created in ff594cf. No ORM was ever added (`git log -S'sqlalchemy' -i` finds only a TODO added in f9cc72c and removed in 9301c6f).

## Why

The main reason was to show SQL injection defence by hand. Supporting reasons: the data access layer is transparent and easier to audit, and it keeps things simple (KISS). See [project_overview.md](../project_overview.md) (section 2, KISS) and [input_handling.md](../input_handling.md) (section 2, parameterized queries).

## Considered options

SQLAlchemy ORM: the maintainer has experience with it. Not chosen because the goal was to show SQL injection defence by hand. No other alternatives recorded.

## Consequences

- Repository functions are tested in `tests/repository/` (`test_users_repo.py`, `test_reports_repo.py`, `test_comments_repo.py`). No test asserts that a non-allowlisted column is ignored or that injection input is treated as data: not enforced by a test.
- Any SQL a reader audits is plain text in `repository/`.

If reversed: introducing an ORM removes the hand-written SQL injection defence that was the main reason for this choice. Adding an f-string or concatenated value to SQL, or a column name not from the allowlist, reopens SQL injection. Do not replace the repository layer with an ORM or build SQL from request input. Not enforced by a test.
