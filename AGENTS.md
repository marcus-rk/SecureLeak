# Agent instructions

This file is the single source of instructions for any coding agent working in this repository. `CLAUDE.md` imports it; do not copy its content elsewhere.

## Before doing anything

1. Read [README.md](README.md) and the parts of `docs/` that touch the area you are working in.
2. Understand the existing project before proposing changes: its purpose, structure, tests and the decisions it already made. Start from what the code does now.

## Commands

- Setup: `python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt` (runtime requirements plus pinned pytest and ruff).
- Tests (full suite): `.venv/bin/python -m pytest -o addopts="" -q` (`pytest.ini` sets `addopts = -q`; overriding it shows the pass/fail summary).
- Lint, check-only: `.venv/bin/ruff check .` and `.venv/bin/ruff format --check .`.
- CI runs the same check-only lint commands (`ruff check` with GitHub annotation output) and never rewrites files, so a local pass means a CI pass.
- Run tests and lint before claiming a change works, and quote the output.

## Separate facts, suggestions and decisions

When reporting or proposing, label each point:

- **Fact:** observed in code, command output or Git history. Cite the file, line or command.
- **Suggestion:** your recommendation or an option. Say why and what it costs.
- **Decision:** agreed with the owner. Only the owner makes these; note where and when it was agreed.

Never present a suggestion as if it were decided.

## Scope

- Discuss intended outcomes and scope with the owner before any rework.
- Do not change application code, upgrade dependencies, refactor, or add features unless that specific work has been agreed.
- Keep agreed changes small, and keep the project's original strengths intact.
- The owner must be able to explain every change. Prefer changes they can understand and defend over clever ones.

## Git workflow

- Start from the latest `origin/main`. Fetch and verify it; preserve existing branches and dirty work by using an isolated worktree when a checkout is already in use.
- Work on a branch, never directly on `main`. Open pull requests as drafts; mark them ready only when the owner asks.
- Commit and push only when the owner asks.
- Use the GitHub account `marcus-rk`. The commit name and email (GitHub noreply address) are set in the local Git config; do not change it or the global config.
- Write all commits, pull requests and documentation in English.

## Agent skills

### Issue tracker

Before creating, claiming, implementing, reviewing or updating an issue, PR or Project item, read `docs/agents/issue-tracker.md` for the canonical lifecycle and authorization gates. Use `gh` for `marcus-rk/SecureLeak`.

### Triage labels

Before triage or label changes, read `docs/agents/triage-labels.md` for the label vocabulary and its relationship to Project status.

### Domain docs

Single-context: this repo has one `CONTEXT.md` and `docs/adr/` at its root. See `docs/agents/domain.md`.
