"""
Validator registry (spec 2.3): pluggable functions that judge whether
a task's output counts as valid, beyond plain exit-code success.

To add a new validator: write a function (stdout: str, stderr: str,
exit_code: int, args: dict) -> tuple[bool, str] and add it to
VALIDATOR_REGISTRY below. This mirrors the CLI's
lib.validation_functions auto-discovery in spirit -- the seam is
explicit here since there is no legacy lib/ package to scan.
"""

import re
from typing import Callable


def _exit_zero(stdout: str, stderr: str, exit_code: int, args: dict) -> tuple[bool, str]:
    ok = exit_code == 0
    return ok, "exit code was 0" if ok else f"exit code was {exit_code}"


def _output_contains(stdout: str, stderr: str, exit_code: int, args: dict) -> tuple[bool, str]:
    needle = args.get("value", "")
    ok = needle in stdout
    return ok, f"'{needle}' found in output" if ok else f"'{needle}' not found in output"


def _output_not_contains(stdout: str, stderr: str, exit_code: int, args: dict) -> tuple[bool, str]:
    needle = args.get("value", "")
    ok = needle not in stdout
    return ok, f"'{needle}' correctly absent" if ok else f"'{needle}' unexpectedly present"


def _regex_match(stdout: str, stderr: str, exit_code: int, args: dict) -> tuple[bool, str]:
    pattern = args.get("pattern", "")
    ok = re.search(pattern, stdout) is not None
    return ok, f"pattern '{pattern}' matched" if ok else f"pattern '{pattern}' did not match"


def _no_stderr(stdout: str, stderr: str, exit_code: int, args: dict) -> tuple[bool, str]:
    ok = not stderr.strip()
    return ok, "stderr was empty" if ok else "stderr was non-empty"


VALIDATOR_REGISTRY: dict[str, Callable[[str, str, int, dict], tuple[bool, str]]] = {
    "exit_zero": _exit_zero,
    "output_contains": _output_contains,
    "output_not_contains": _output_not_contains,
    "regex_match": _regex_match,
    "no_stderr": _no_stderr,
}


def run_validator(name: str, stdout: str, stderr: str, exit_code: int, args: dict) -> dict:
    fn = VALIDATOR_REGISTRY.get(name)
    if fn is None:
        return {"passed": False, "message": f"unknown validator '{name}'"}
    passed, message = fn(stdout, stderr, exit_code, args or {})
    return {"passed": passed, "message": message}