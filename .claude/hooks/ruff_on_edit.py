"""PostToolUse hook for Edit and Write: run `ruff check` on the edited Python file.

Ruff lookup: RUFF_ON_EDIT_CMD if set, then the project's .venv/bin/ruff, then ruff on PATH.
Exit codes: 0 when the file is clean, skipped or Ruff is missing, 2 with Ruff's findings on stderr.
Fails open: malformed input exits 0 with a warning on stderr.
"""

from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path


def ruff_command() -> list[str] | None:
    """Return the Ruff command to run, or None if Ruff is not installed."""
    # Explicit override, used by the tests
    override = os.environ.get("RUFF_ON_EDIT_CMD")
    if override:
        return shlex.split(override)
    # The project virtualenv holds the pinned version
    project = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path(__file__).resolve().parents[2])
    venv_ruff = project / ".venv" / "bin" / "ruff"
    if venv_ruff.is_file():
        return [str(venv_ruff)]
    on_path = shutil.which("ruff")
    return [on_path] if on_path else None


def skip_missing_ruff() -> int:
    # A missing tool must not break the session
    print("ruff_on_edit: ruff not found; skipping lint.", file=sys.stderr)
    return 0


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        file_path = payload["tool_input"]["file_path"]
        if not isinstance(file_path, str):
            raise TypeError("file_path is not a string")
    except Exception as exc:
        # Fail open: a hook bug must never break edits
        print(f"ruff_on_edit warning: could not read payload ({exc!r}); skipping.", file=sys.stderr)
        return 0

    # Ruff only lints Python files
    if not file_path.endswith(".py"):
        return 0

    cmd = ruff_command()
    if cmd is None:
        return skip_missing_ruff()
    try:
        # Check only: never --fix and never format, so only the agent changes files
        result = subprocess.run([*cmd, "check", file_path], capture_output=True, text=True)
    except FileNotFoundError:
        return skip_missing_ruff()
    if result.returncode != 0:
        print(result.stdout + result.stderr, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
