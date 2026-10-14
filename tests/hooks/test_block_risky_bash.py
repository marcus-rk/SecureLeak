import json
import subprocess
import sys
from pathlib import Path

import pytest

HOOK = Path(__file__).resolve().parents[2] / ".claude" / "hooks" / "block_risky_bash.py"


def test_cat_env_is_blocked(tmp_path):
    # Why: A Bash read of .env would print secrets into the agent transcript.
    result = _run_hook("cat .env", tmp_path)
    assert result.returncode == 2
    assert "secret" in result.stderr.lower()


@pytest.mark.parametrize(
    "command",
    [
        "less .env.local",
        "more .envrc",
        "head -n 5 config/.env.production",
        "tail certs/server.pem",
        "grep -r KEY tls.key",
        "sed -n 1p .env",
        "awk '{print}' .env",
        "source .env",
        ". .env",
        "cat instance/secureleak.sqlite",
        "cat ./instance/uploads/1/a.png",
        "grep -r KEY instance",
        "cat instance/",
    ],
)
def test_secret_reads_are_blocked(tmp_path, command):
    # Why: Swapping the read command or the secret file type must not bypass the block.
    result = _run_hook(command, tmp_path)
    assert result.returncode == 2
    assert "secret" in result.stderr.lower()


@pytest.mark.parametrize(
    "command",
    [
        "ls -la",
        "git check-ignore .env",
        "cat README.md",
        "pytest -q",
        "ruff check .",
        "git status",
        "git push -u origin feat/x",
    ],
)
def test_ordinary_commands_are_allowed(tmp_path, command):
    # Why: The hook must not get in the way of normal work or of naming a secret file without reading it.
    result = _run_hook(command, tmp_path)
    assert result.returncode == 0
    assert result.stderr == ""


@pytest.mark.parametrize(
    "command",
    [
        "git push --force",
        "git push -f origin feat/x",
        "git push --force-with-lease",
        "git push --force-with-lease=main:abc123 origin main",
    ],
)
def test_force_push_is_blocked(tmp_path, command):
    # Why: An agent must never rewrite remote history.
    result = _run_hook(command, tmp_path)
    assert result.returncode == 2
    assert "force" in result.stderr.lower()


def test_commit_on_main_is_blocked(tmp_path):
    # Why: AGENTS.md requires agents to work on a branch, never directly on main.
    _init_repo(tmp_path, "main")
    result = _run_hook('git commit -m "x"', tmp_path)
    assert result.returncode == 2
    assert "main" in result.stderr


def test_commit_on_feature_branch_is_allowed(tmp_path):
    # Why: Committing on a feature branch is the normal, allowed workflow.
    _init_repo(tmp_path, "feat/x")
    result = _run_hook('git commit -m "x"', tmp_path)
    assert result.returncode == 0


@pytest.mark.parametrize(
    "command",
    [
        "ls && cat .env",
        "echo hi; tail .env",
        "git status || head instance/db.sqlite",
        "echo x | grep KEY .env.local",
        "ls\ncat .env",
    ],
)
def test_risky_command_hidden_in_a_chain_is_blocked(tmp_path, command):
    # Why: Putting a harmless command first must not bypass the block.
    result = _run_hook(command, tmp_path)
    assert result.returncode == 2


@pytest.mark.parametrize(
    "command",
    [
        "grep -rn instance .",
        'grep -n "instance" app.py',
        "sed -n instance README.md",
        "awk instance README.md",
    ],
)
def test_pattern_that_only_mentions_a_secret_name_is_allowed(tmp_path, command):
    # Why: Searching for a word like "instance" names a secret location without reading one.
    result = _run_hook(command, tmp_path)
    assert result.returncode == 0
    assert result.stderr == ""


@pytest.mark.parametrize(
    "command",
    [
        "grep KEY .env",
        "grep -r x instance/",
        "grep -e foo .env",
        "sed -n 1p .env",
        "awk '{print}' .env",
        "awk -f prog.awk .env",
    ],
)
def test_files_after_the_pattern_are_still_checked(tmp_path, command):
    # Why: Skipping the pattern argument must not open a way to read a secret file.
    result = _run_hook(command, tmp_path)
    assert result.returncode == 2
    assert "secret" in result.stderr.lower()


@pytest.mark.parametrize(
    "stdin",
    ["not json", "{}", '{"tool_input": {"command": "cat \\".env"}, "cwd": "."}'],
    ids=["not-json", "missing-keys", "unbalanced-quote"],
)
def test_malformed_input_fails_open_with_warning(tmp_path, stdin):
    # Why: A hook bug or odd payload must never lock the agent out of all Bash commands.
    result = _run_raw(stdin, tmp_path)
    assert result.returncode == 0
    assert "warning" in result.stderr.lower()


def test_runs_under_system_python(tmp_path, legacy_python):
    # Why: Claude Code runs bare python3, and a crash on old Pythons would silently disable the hook.
    payload = {"tool_input": {"command": "cat .env"}, "cwd": str(tmp_path)}
    result = subprocess.run(
        [legacy_python, str(HOOK)], input=json.dumps(payload), capture_output=True, text=True, timeout=30
    )
    assert result.returncode == 2
    assert "secret" in result.stderr.lower()


# --- helpers ---


def _run_hook(command: str, cwd: Path) -> subprocess.CompletedProcess:
    payload = {"tool_name": "Bash", "tool_input": {"command": command}, "cwd": str(cwd)}
    return _run_raw(json.dumps(payload), cwd)


def _init_repo(path: Path, branch: str) -> None:
    subprocess.run(["git", "init", "-q", "-b", branch, str(path)], check=True)


def _run_raw(stdin: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(HOOK)], input=stdin, capture_output=True, text=True, cwd=cwd, timeout=30)
