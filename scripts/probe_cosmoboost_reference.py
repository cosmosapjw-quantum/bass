#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import subprocess
from pathlib import Path

EXPECTED_COMMIT = "be29be2e9ba10424314f826a32e79008bdc2d2be"
EXPECTED_BLUEPRINTS_BLOB = "50d4de3261b02fc0118beb5a1799d8fe7729750f"


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout.strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", type=Path)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repository.resolve()
    head = git(repo, "rev-parse", "HEAD")
    if head != EXPECTED_COMMIT:
        raise SystemExit(f"COSMOBOOST_PIN_FAIL: expected {EXPECTED_COMMIT}, got {head}")

    source = repo / "cosmoboost/blueprints.py"
    blob = git(repo, "hash-object", str(source.relative_to(repo)))
    if blob != EXPECTED_BLUEPRINTS_BLOB:
        raise SystemExit(f"COSMOBOOST_BLOB_FAIL: expected {EXPECTED_BLUEPRINTS_BLOB}, got {blob}")

    tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
    default_pars = None
    class_names: set[str] = set()
    method_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "DEFAULT_PARS":
                    default_pars = ast.literal_eval(node.value)
        elif isinstance(node, ast.ClassDef):
            class_names.add(node.name)
        elif isinstance(node, ast.FunctionDef):
            method_names.add(node.name)

    if not isinstance(default_pars, dict):
        raise SystemExit("COSMOBOOST_AST_FAIL: DEFAULT_PARS not found")
    required_defaults = {
        "d": 1,
        "s": 0,
        "beta": 0.00123,
        "lmin": 0,
        "lmax": 1000,
        "method": "ODE",
    }
    for key, expected in required_defaults.items():
        if default_pars.get(key) != expected:
            raise SystemExit(f"COSMOBOOST_AST_FAIL: {key}={default_pars.get(key)!r}, expected {expected!r}")
    if "Kernel" not in class_names or "_get_mLl_d1" not in method_names:
        raise SystemExit("COSMOBOOST_AST_FAIL: expected generalized kernel API missing")

    receipt = {
        "status": "PASS",
        "authority_effect": "NONE_EXTERNAL_REFERENCE_ONLY",
        "repository": "syasini/CosmoBoost",
        "commit": head,
        "blueprints_git_blob": blob,
        "blueprints_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "observed_defaults": required_defaults,
        "observed_kernel_class": True,
        "observed_d1_kernel_method": True,
        "claim_boundary": "SOURCE_AST_AND_IDENTITY_PROBE_ONLY_NOT_BASS_OR_HTT_PARITY",
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
