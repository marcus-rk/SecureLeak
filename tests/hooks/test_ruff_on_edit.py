import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

import pytest

HOOK = Path(__file__).resolve().parents[2] / ".claude" / "hooks" / "ruff_on_edit.py"


def test_findings_in_edited_python_file_are_reported(tmp_path):
    # Why: The agent must see lint findings right after editing a file, not after CI fails.
    target = tmp_path / "bad.py"
    target.write_text("import os\n")
    fake = _fake_ruff(tmp_path, exit_code=1, output="bad.py:1:8: F401 `os` imported but unused")

    result = _run_hook({"tool_input": {"file_path": str(target)}}, fake)

    assert result.returncode == 2
    assert "F401" in result.stderr


def test_clean_python_file_is_silent_and_check_only(tmp_path):
    # Why: Clean edits stay quiet, and the hook never rewrites files (no --fix, no format).
    target = tmp_path / "good.py"
    target.write_text("x = 1\n")
    fake = _fake_ruff(tmp_path, exit_code=0)

    result = _run_hook({"tool_input": {"file_path": str(target)}}, fake)

    assert result.returncode == 0
    assert result.stderr == ""
    assert _ruff_calls(tmp_path) == [f"check {target}"]


@pytest.mark.parametrize("name", ["README.md", "templates/base.html", ".github/workflows/ci.yml"])
def test_non_python_file_is_skipped(tmp_path, name):
    # Why: Ruff only lints Python, so other files must not produce noise.
    fake = _fake_ruff(tmp_path, exit_code=1, output="should not run")

    result = _run_hook({"tool_input": {"file_path": str(tmp_path / name)}}, fake)

    assert result.returncode == 0
    assert _ruff_calls(tmp_path) == []


def test_missing_ruff_skips_with_note(tmp_path):
    # Why: A contributor without Ruff installed must not have every edit fail.
    target = tmp_path / "good.py"
    target.write_text("x = 1\n")

    result = _run_hook({"tool_input": {"file_path": str(target)}}, str(tmp_path / "no-such-ruff"))

    assert result.returncode == 0
    assert "ruff not found" in result.stderr.lower()


def test_no_ruff_in_venv_or_on_path_skips_with_note(tmp_path):
    # Why: Without any Ruff installed, edits must still succeed with a short note.
    project = tmp_path / "project"
    project.mkdir()
    target = project / "good.py"
    target.write_text("x = 1\n")
    empty_bin = tmp_path / "empty_bin"
    empty_bin.mkdir()

    result = _run_without_override(target, project, empty_bin)

    assert result.returncode == 0
    assert "ruff not found" in result.stderr.lower()


@pytest.mark.parametrize(
    "stdin",
    ["not json", "{}", '{"tool_input": {"file_path": null}}'],
    ids=["not-json", "missing-keys", "null-path"],
)
def test_malformed_input_fails_open_with_warning(tmp_path, stdin):
    # Why: A hook bug or odd payload must never break the agent's edits.
    result = _run_raw(stdin, _fake_ruff(tmp_path, exit_code=1))
    assert result.returncode == 0
    assert "warning" in result.stderr.lower()


def test_project_venv_ruff_is_preferred_over_path(tmp_path):
    # Why: The pinned Ruff in the project virtualenv gives the same results as CI.
    project = tmp_path / "project"
    target = project / "good.py"
    _executable_ruff(project / ".venv" / "bin", tmp_path, "venv")
    _executable_ruff(tmp_path / "path_bin", tmp_path, "path")
    project.mkdir(exist_ok=True)
    target.write_text("x = 1\n")

    result = _run_without_override(target, project, tmp_path / "path_bin")

    assert result.returncode == 0
    assert _ruff_calls(tmp_path) == [f"venv check {target}"]


def test_ruff_on_path_is_used_without_project_venv(tmp_path):
    # Why: Contributors without a virtualenv still get lint feedback from a Ruff on PATH.
    project = tmp_path / "project"
    project.mkdir()
    target = project / "good.py"
    target.write_text("x = 1\n")
    _executable_ruff(tmp_path / "path_bin", tmp_path, "path")

    result = _run_without_override(target, project, tmp_path / "path_bin")

    assert result.returncode == 0
    assert _ruff_calls(tmp_path) == [f"path check {target}"]


def test_runs_under_system_python(tmp_path, legacy_python):
    # Why: Claude Code runs bare python3, and a crash on old Pythons would silently disable the hook.
    result = subprocess.run([legacy_python, str(HOOK)], input="{}", capture_output=True, text=True, timeout=30)
    assert result.returncode == 0
    assert "warning" in result.stderr.lower()


# --- helpers ---


def _fake_ruff(tmp_path: Path, exit_code: int, output: str = "") -> str:
    """Write a stand-in for Ruff that logs its arguments and prints `output`."""
    script = tmp_path / "fake_ruff.py"
    log = tmp_path / "ruff_calls.log"
    script.write_text(
        "import sys\n"
        f"open({str(log)!r}, 'a').write(' '.join(sys.argv[1:]) + '\\n')\n"
        f"print({output!r})\n"
        f"sys.exit({exit_code})\n"
    )
    return shlex.join([sys.executable, str(script)])


def _executable_ruff(bin_dir: Path, tmp_path: Path, tag: str) -> None:
    """Write an executable named `ruff` that logs `tag` and its arguments."""
    bin_dir.mkdir(parents=True, exist_ok=True)
    ruff = bin_dir / "ruff"
    log = tmp_path / "ruff_calls.log"
    ruff.write_text(
        f"#!{sys.executable}\n"
        "import sys\n"
        f"open({str(log)!r}, 'a').write({tag!r} + ' ' + ' '.join(sys.argv[1:]) + '\\n')\n"
    )
    ruff.chmod(0o755)


def _run_without_override(target: Path, project: Path, path_dir: Path) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k != "RUFF_ON_EDIT_CMD"}
    env.update(CLAUDE_PROJECT_DIR=str(project), PATH=str(path_dir))
    payload = json.dumps({"tool_input": {"file_path": str(target)}})
    return subprocess.run(
        [sys.executable, str(HOOK)], input=payload, capture_output=True, text=True, env=env, timeout=30
    )


def _ruff_calls(tmp_path: Path) -> list[str]:
    log = tmp_path / "ruff_calls.log"
    return log.read_text().splitlines() if log.exists() else []


def _run_hook(payload: dict, ruff_cmd: str) -> subprocess.CompletedProcess:
    return _run_raw(json.dumps(payload), ruff_cmd)


def _run_raw(stdin: str, ruff_cmd: str) -> subprocess.CompletedProcess:
    env = {**os.environ, "RUFF_ON_EDIT_CMD": ruff_cmd}
    return subprocess.run([sys.executable, str(HOOK)], input=stdin, capture_output=True, text=True, env=env, timeout=30)
