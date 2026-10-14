"""Stop hook: run the full test suite before the agent ends its turn.

Runs the AGENTS.md command with the project's virtualenv Python (PYTEST_ON_STOP_CMD overrides it).
Blocks at most once per stop chain: when stop_hook_active is true the turn ends without a run.
Exit codes: 0 lets the turn end, 2 blocks it with the failure summary on stderr.
Fails open: malformed input, a missing virtualenv or a timeout exits 0 with a note on stderr.
"""

from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

# Seconds before a hung suite is abandoned; below the hook timeout in .claude/settings.json
DEFAULT_TIMEOUT = 120


def suite_command(project: Path) -> list[str] | None:
    """Return the test command, or None if the project virtualenv is missing."""
    # Explicit override, used by the tests
    override = os.environ.get("PYTEST_ON_STOP_CMD")
    if override:
        return shlex.split(override)
    python = project / ".venv" / "bin" / "python"
    if not python.is_file():
        return None
    return [str(python), "-m", "pytest", "-o", "addopts=", "-q"]


def summary(output: str) -> str:
    """Keep the FAILED and ERROR lines plus the final summary line."""
    lines = [line for line in output.splitlines() if line.strip()]
    failed = [line for line in lines if line.startswith(("FAILED ", "ERROR "))]
    return "\n".join(failed + lines[-1:])


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        stop_hook_active = payload.get("stop_hook_active")
    except Exception as exc:
        # Fail open: a hook bug must never stop the turn from ending
        print(f"pytest_on_stop warning: could not read payload ({exc!r}); skipping tests.", file=sys.stderr)
        return 0

    # Loop guard: this stop already follows a block, so let the turn end
    if stop_hook_active:
        return 0

    project = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path(__file__).resolve().parents[2])
    cmd = suite_command(project)
    if cmd is None:
        print("pytest_on_stop: project virtualenv not found; skipping tests.", file=sys.stderr)
        return 0

    timeout = float(os.environ.get("PYTEST_ON_STOP_TIMEOUT") or DEFAULT_TIMEOUT)
    try:
        result = subprocess.run(cmd, cwd=project, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        print(f"pytest_on_stop: test suite timed out after {timeout:g}s; not blocking.", file=sys.stderr)
        return 0
    if result.returncode != 0:
        print("Test suite failed; fix it before ending the turn.\n" + summary(result.stdout), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
