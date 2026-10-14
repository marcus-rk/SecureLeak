"""PreToolUse hook for the Bash tool: block risky commands before they run.

Enforces, for every simple command in a chain (newline, ;, &&, ||, |, &):
- no reading of secret files (.env, .env.*, .envrc, *.pem, *.key, instance/)
- no force push (git push -f, --force, --force-with-lease)
- no git commit while the current branch is main

Exit codes: 0 allows the command, 2 blocks it with a one-line reason on stderr.
Fails open: malformed input or an internal error exits 0 with a warning on stderr.
This is a guardrail against accidents, not a sandbox against obfuscated commands.
"""

from __future__ import annotations

import json
import shlex
import subprocess
import sys
from pathlib import PurePosixPath

# Commands that print or load a file's contents
READ_COMMANDS = {"cat", "less", "more", "head", "tail", "grep", "sed", "awk", "source", "."}
# For these, the first non-option argument is the pattern or script, not a file, unless one of these options supplies it
PATTERN_OPTIONS = {"grep": {"-e", "-f"}, "sed": {"-e", "-f"}, "awk": {"-f"}}
# File names that hold local secrets
SECRET_NAMES = {".env", ".envrc"}
# Variants such as .env.local and .env.production
SECRET_PREFIX = ".env."
# Local TLS certificates and keys
SECRET_SUFFIXES = (".pem", ".key")
# Local database and uploads; the directory itself counts, for recursive reads
SECRET_DIR = "instance"
# git push flags that force a push (-f exactly, --force* as a prefix)
FORCE_FLAG = "-f"
FORCE_PREFIX = "--force"
# Commits are blocked while this branch is checked out
PROTECTED_BRANCH = "main"


def is_secret_path(arg: str) -> bool:
    path = PurePosixPath(arg)
    name = path.name
    if name in SECRET_NAMES or name.startswith(SECRET_PREFIX):
        return True
    if name.endswith(SECRET_SUFFIXES):
        return True
    return SECRET_DIR in path.parts


def file_args(tokens: list[str]) -> list[str]:
    """Return the arguments that may be files: for grep, sed and awk, minus the pattern or script."""
    args = tokens[1:]
    options = PATTERN_OPTIONS.get(tokens[0])
    if options is None or any(a in options for a in args):
        return args
    for i, arg in enumerate(args):
        if not arg.startswith("-"):
            return args[:i] + args[i + 1 :]
    return args


def segments(command: str) -> list[list[str]]:
    """Split a command line into simple commands at newlines, ;, &&, ||, | and &."""
    # A newline separates commands like ; does
    lexer = shlex.shlex(command.replace("\n", ";"), posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    result: list[list[str]] = [[]]
    for token in lexer:
        if token in {";", "&&", "||", "|", "&"}:
            result.append([])
        else:
            result[-1].append(token)
    return [s for s in result if s]


def git_subcommand(tokens: list[str]) -> tuple[str | None, list[str]]:
    """Return the git subcommand and its arguments, or (None, []) if not a git command."""
    if tokens[0] != "git":
        return None, []
    i = 1
    while i < len(tokens) and tokens[i].startswith("-"):
        # -C <path> and -c <name=value> take a separate argument
        i += 2 if tokens[i] in {"-C", "-c"} else 1
    if i >= len(tokens):
        return None, []
    return tokens[i], tokens[i + 1 :]


def current_branch(cwd: str) -> str:
    result = subprocess.run(["git", "branch", "--show-current"], cwd=cwd, capture_output=True, text=True)
    return result.stdout.strip()


def check(command: str, cwd: str) -> str | None:
    """Return the reason to block `command` run in `cwd`, or None to allow it."""
    for tokens in segments(command):
        # Printing a secret file would put its values in the transcript
        if tokens[0] in READ_COMMANDS and any(is_secret_path(a) for a in file_args(tokens)):
            return "Blocked: reading a secret file. Name the key without printing its value."
        sub, args = git_subcommand(tokens)
        # Force-pushing rewrites remote history
        if sub == "push" and any(a == FORCE_FLAG or a.startswith(FORCE_PREFIX) for a in args):
            return "Blocked: force push. Push without --force, or ask the owner."
        # Work happens on a branch, never directly on main
        if sub == "commit" and current_branch(cwd) == PROTECTED_BRANCH:
            return "Blocked: commit on main. Create a branch first."
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        reason = check(payload["tool_input"]["command"], payload["cwd"])
    except Exception as exc:
        # Fail open: a hook bug must never block every Bash command
        print(f"block_risky_bash warning: could not check command ({exc!r}); allowing it.", file=sys.stderr)
        return 0
    if reason:
        print(reason, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
