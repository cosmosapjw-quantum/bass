#!/usr/bin/env python3
"""Verify that a Git working tree differs from an exact base only as allowed."""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath


BASE_RE = re.compile(r"^[0-9a-f]{40}$")
EXIT_PASS = 0
EXIT_BLOCKED = 2
EXIT_P0 = 3


class FirewallError(ValueError):
    """The diff cannot be evaluated against the supplied authority."""


def _git(repository: Path, *arguments: str, text: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *arguments],
        cwd=repository,
        check=False,
        capture_output=True,
        text=text,
    )


def _match(path: str, pattern: str) -> bool:
    if pattern.endswith("/**"):
        prefix = pattern[:-3].rstrip("/")
        return path == prefix or path.startswith(prefix + "/")
    if fnmatch.fnmatchcase(path, pattern) or PurePosixPath(path).match(pattern):
        return True
    if pattern.startswith("**/"):
        return fnmatch.fnmatchcase(path, pattern[3:])
    return False


def _policy(contract: object) -> tuple[str | None, list[str], list[str]]:
    if not isinstance(contract, dict):
        raise FirewallError("contract must be an object")
    if contract.get("schema") == "bass-ac01-nonselfref-successor/v1":
        implementation = contract.get("implementation")
        if not isinstance(implementation, dict):
            raise FirewallError("contract.implementation must be an object")
        allowed = implementation.get("allowed_paths")
        declared_base = implementation.get("base_sha")
        forbidden: object = []
        prefix = "contract.implementation"
    else:
        scope = contract.get("scope")
        if not isinstance(scope, dict):
            raise FirewallError("contract.scope must be an object")
        allowed = scope.get("allowed_paths")
        forbidden = scope.get("forbidden_paths")
        declared_base = contract.get("authority", {}).get("base", {}).get("sha")
        prefix = "contract.scope"
    if not isinstance(allowed, list) or not allowed or any(not isinstance(item, str) or not item for item in allowed):
        raise FirewallError(f"{prefix}.allowed_paths must be a nonempty string list")
    if not isinstance(forbidden, list) or any(not isinstance(item, str) or not item for item in forbidden):
        raise FirewallError(f"{prefix}.forbidden_paths must be a string list")
    if declared_base is not None and (not isinstance(declared_base, str) or not BASE_RE.fullmatch(declared_base)):
        raise FirewallError("contract base SHA must be a lowercase 40-character SHA")
    return declared_base, allowed, forbidden


def _changed_paths(repository: Path, base: str) -> list[tuple[str, str]]:
    diff = _git(repository, "diff", "--name-status", "-z", "--no-renames", base, "--", text=False)
    if diff.returncode != 0:
        raise FirewallError(diff.stderr.decode("utf-8", "replace").strip() or "git diff failed")
    fields = diff.stdout.decode("utf-8", "surrogateescape").split("\0")
    if fields and fields[-1] == "":
        fields.pop()
    if len(fields) % 2:
        raise FirewallError("unexpected git diff --name-status output")
    changes = [(fields[index], fields[index + 1]) for index in range(0, len(fields), 2)]

    untracked = _git(repository, "ls-files", "--others", "--exclude-standard", "-z", text=False)
    if untracked.returncode != 0:
        raise FirewallError(untracked.stderr.decode("utf-8", "replace").strip() or "git ls-files failed")
    for path in untracked.stdout.decode("utf-8", "surrogateescape").split("\0"):
        if path:
            changes.append(("??", path))
    return sorted(set(changes), key=lambda item: (item[1], item[0]))


def verify(repository: Path, base: str, contract_path: Path) -> tuple[str, int]:
    if not BASE_RE.fullmatch(base):
        raise FirewallError("--base must be a lowercase 40-character SHA")
    repository_result = _git(repository, "rev-parse", "--show-toplevel")
    if repository_result.returncode != 0:
        raise FirewallError(repository_result.stderr.strip() or "not inside a Git repository")
    repository = Path(repository_result.stdout.strip())
    commit_check = _git(repository, "cat-file", "-e", f"{base}^{{commit}}")
    if commit_check.returncode != 0:
        raise FirewallError(f"base commit is unavailable: {base}")

    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    declared_base, allowed, forbidden = _policy(contract)
    if declared_base is not None and declared_base != base:
        return (
            f"BASE_AUTHORITY_MISMATCH\nexpected={declared_base}\nactual={base}",
            EXIT_P0,
        )

    ancestor = _git(repository, "merge-base", "--is-ancestor", base, "HEAD")
    if ancestor.returncode != 0:
        return (f"BASE_AUTHORITY_MISMATCH\nbase={base}\nhead_is_not_descendant=true", EXIT_P0)

    changes = _changed_paths(repository, base)
    violations: list[tuple[str, str, str]] = []
    for status, path in changes:
        if any(_match(path, pattern) for pattern in forbidden):
            violations.append((status, path, "forbidden_path"))
        elif not any(_match(path, pattern) for pattern in allowed):
            violations.append((status, path, "not_allowlisted"))

    if violations:
        lines = ["FORBIDDEN_REFERENCE_MUTATION", f"base={base}"]
        lines.extend(
            f"status={status} path={path} reason={reason}"
            for status, path, reason in violations
        )
        return "\n".join(lines), EXIT_P0

    lines = [f"PASS_ALLOWED_DIFF base={base} paths={len(changes)}"]
    lines.extend(f"status={status} path={path}" for status, path in changes)
    return "\n".join(lines), EXIT_PASS


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--contract", required=True, type=Path)
    arguments = parser.parse_args()
    try:
        output, exit_status = verify(Path.cwd(), arguments.base, arguments.contract.resolve())
    except (OSError, UnicodeError, json.JSONDecodeError, FirewallError) as error:
        print(f"BLOCKED_DIFF_FIREWALL\nerror={error}")
        return EXIT_BLOCKED
    print(output)
    return exit_status


if __name__ == "__main__":
    sys.exit(main())
