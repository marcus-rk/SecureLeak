import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

import pytest

HOOK = Path(__file__).resolve().parents[2] / ".claude" / "hooks" / "pytest_on_stop.py"

FAILING_OUTPUT = """\
F.
=================================== FAILURES ===================================
___________________________________ test_x ____________________________________
    def test_x():
>       assert 1 == 2
E       assert 1 == 2
tests/test_x.py:2: AssertionError
=========================== short test summary info ============================
FAILED tests/test_x.py::test_x - assert 1 == 2
1 failed, 1 passed in 0.01s
"""


def test_failing_suite_blocks_stop_with_trimmed_summary(tmp_path):
    # Why: An agent must not end its turn while the suite is red, and needs to know what failed.
    fake = _fake_suite(tmp_path, exit_code=1, output=FAILING_OUTPUT)

    result = _run_hook({"stop_hook_active": False}, fake)

    assert result.returncode == 2
    assert "FAILED tests/test_x.py::test_x - assert 1 == 2" in result.stderr
    assert "1 failed, 1 passed in 0.01s" in result.stderr
    assert "AssertionError" not in result.stderr


def test_passing_suite_ends_turn_silently(tmp_path):
    # Why: Clean work must not be slowed down by noise.
    fake = _fake_suite(tmp_path, exit_code=0, output="2 passed in 0.01s\n")

    result = _run_hook({"stop_hook_active": False}, fake)

    assert result.returncode == 0
    assert result.stderr == ""


def test_second_stop_in_chain_is_allowed_without_running_suite(tmp_path):
    # Why: Blocking at most once per stop chain means a test the agent cannot fix never traps it in a loop.
    fake = _fake_suite(tmp_path, exit_code=1, output=FAILING_OUTPUT)

    result = _run_hook({"stop_hook_active": True}, fake)

    assert result.returncode == 0
    assert not (tmp_path / "suite_ran").exists()


def test_hung_suite_times_out_and_lets_turn_end(tmp_path):
    # Why: A hung test must not freeze the session.
    fake = _fake_suite(tmp_path, exit_code=1, output=FAILING_OUTPUT, sleep=10)

    result = _run_hook({"stop_hook_active": False}, fake, PYTEST_ON_STOP_TIMEOUT="0.5")

    assert result.returncode == 0
    assert "timed out" in result.stderr.lower()


def test_default_command_runs_documented_suite_with_project_venv(tmp_path):
    # Why: Results must match the AGENTS.md command and CI, using the project's virtualenv.
    venv_bin = tmp_path / ".venv" / "bin"
    venv_bin.mkdir(parents=True)
    log = tmp_path / "python_args.log"
    python = venv_bin / "python"
    python.write_text(f"#!{sys.executable}\nimport sys\nopen({str(log)!r}, 'w').write(' '.join(sys.argv[1:]))\n")
    python.chmod(0o755)

    result = _run_without_override({"stop_hook_active": False}, tmp_path)

    assert result.returncode == 0
    assert log.read_text() == "-m pytest -o addopts= -q"


def test_missing_venv_skips_with_note(tmp_path):
    # Why: A contributor without a virtualenv must not have every turn blocked.
    result = _run_without_override({"stop_hook_active": False}, tmp_path)

    assert result.returncode == 0
    assert "virtualenv not found" in result.stderr.lower()


@pytest.mark.parametrize("stdin", ["not json", "[]"], ids=["not-json", "not-an-object"])
def test_malformed_input_fails_open_with_warning(tmp_path, stdin):
    # Why: A hook bug or odd payload must never stop the agent from ending its turn.
    result = _run_raw(stdin, _fake_suite(tmp_path, exit_code=1, output=FAILING_OUTPUT))

    assert result.returncode == 0
    assert "warning" in result.stderr.lower()


def test_runs_under_system_python(tmp_path, legacy_python):
    # Why: Claude Code runs bare python3, and a crash on old Pythons would silently disable the hook.
    result = subprocess.run(
        [legacy_python, str(HOOK)], input='{"stop_hook_active": true}', capture_output=True, text=True, timeout=30
    )
    assert result.returncode == 0
    assert result.stderr == ""


# --- helpers ---


def _fake_suite(tmp_path: Path, exit_code: int, output: str = "", sleep: float = 0) -> str:
    """Write a stand-in for the test command that records each run and prints `output`."""
    script = tmp_path / "fake_suite.py"
    marker = tmp_path / "suite_ran"
    script.write_text(
        "import sys, time\n"
        f"open({str(marker)!r}, 'a').write('ran\\n')\n"
        f"time.sleep({sleep})\n"
        f"print({output!r}, end='')\n"
        f"sys.exit({exit_code})\n"
    )
    return shlex.join([sys.executable, str(script)])


def _run_without_override(payload: dict, project: Path) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k != "PYTEST_ON_STOP_CMD"}
    env["CLAUDE_PROJECT_DIR"] = str(project)
    return subprocess.run(
        [sys.executable, str(HOOK)], input=json.dumps(payload), capture_output=True, text=True, env=env, timeout=60
    )


def _run_hook(payload: dict, test_cmd: str, **env: str) -> subprocess.CompletedProcess:
    return _run_raw(json.dumps(payload), test_cmd, **env)


def _run_raw(stdin: str, test_cmd: str, **env: str) -> subprocess.CompletedProcess:
    full_env = {**os.environ, "PYTEST_ON_STOP_CMD": test_cmd, **env}
    return subprocess.run(
        [sys.executable, str(HOOK)], input=stdin, capture_output=True, text=True, env=full_env, timeout=60
    )
