#!/usr/bin/env python3
"""RF-03 R4 intake: immutable raw bytes, historical R1 object, unchanged R2 semantics.

This replaces R3's byte-destroying reader and R2's obsolete moving-R1-tip
check. It is package/source-identity validation, NOT PASS_RF03_AUTHORITY.
Only --materialize writes, to a new explicitly requested directory.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import NoReturn

ROOT = Path(__file__).resolve().parent
PACKAGE_ID = "BASS-RF03-REMOTE-REBIND-20260828-R4"
AUTH_PACKAGE_ID = "BASS-RF03-AUTHORITY-DIRECT-HANDOFF-20260828-R2"
AUTH_BRANCH = "agent/plans/rf03-authority-resolution-20260828-r2"
AUTH_HEAD = "55335d3817a82da7e0f9bf24ef7632a2533645d3"
AUTH_TREE = "7c02689430d01abdf998c5b7ab1c5a6eb48859f4"
AUTH_INDEX = "docs/rust_first_runtime/rf03_authority_resolution_20260828/PACKAGE_INDEX.json"
AUTH_INDEX_BLOB = "5b358d41d7023e71a4e60fd9bff4f643f9827e4a"
AUTH_PATH = "docs/rust_first_runtime/rf03_authority_resolution_20260828/direct"
BASE_BRANCH = "agent/architecture/rust-first-rf02c-20260826-r1"
BASE_HEAD = "dfa17457d402bd441d3fdf786c2d79c529512ee5"
BASE_TREE = "9fc67fb0ba10e091e25a14d7e1fac88b77a0241e"
R1_BRANCH = "agent/plans/rf03-matter-thermo-tilt-closure-20260828-r1"
R1_HEAD = "b7cda09d337906c17821a2b815032c985ff86bdf"
R1_TREE = "1eba9fc7f4ba8832545c403ca4ce92d81bcb8915"
LOCAL_FILES = {
    "README.md", "PACKAGE.json", "CHANGELOG.md", "CODEX_HANDOFF.md",
    "GITHUB_ROUNDTRIP_RECEIPT.json", "VERIFICATION.json", "validate_rebind.py",
    "tests/test_validate_rebind.py", "tests/fixtures/validate_package_r2.py",
    "evidence/RED_raw_bytes.log", "evidence/RED_nested_legacy_pin.log", "evidence/GREEN_regressions.log",
}
# Original R2 raw-file hashes, intentionally unchanged. No EOL normalization.
DIRECT_FILES = {
    "AUTHORITY_CONTRACT.json": "81f2207bcbfa8ee01713c0b099383ab70bd9d929fd3d0a16813c4da3b3906ab5",
    "CODEX_HANDOFF.md": "e9d36c24dff60ce86856986d67c11083f028821c678530fab3e334d9b7263d66",
    "MANIFEST.sha256": "0109b164b872411af55b3d66be56315721a314a4b662b742b3b116a9f094b25d",
    "README.md": "e61a5845de87b80127a3b92155c1e9afab95b9cc8d1c2f6cb9ab07dd08964c4a",
    "WORK_UNITS.json": "cfd27422c2c9353a97bd257a5de33a4a2a5781e3ad39266c1bc3bd6b65b4fd82",
    "validate_package.py": "caf503153085c8ad2900dd80ef26aa905b8cb8bf7e8541ebd51a7736466c80f8",
}
SOURCE_BLOBS = {
    "bianchi/matter/fluid.py": "41905ff26914b2a7931ce2281d67b25fbde273b5",
    "bianchi/matter/species.py": "60a683fcdc639ae790cf6f3c723182d26940d21f",
    "bianchi/matter/tilt_admissibility.py": "c384a87c1722bd3c6b9b7e02ea71efe7ec88b676",
    "bianchi/thermo/temperature.py": "4b792b04df072446a5d046524ea5323e4237d7e4",
    "compiler/validation/typeii_fixture_authority.json": "b71372faa7dde85e928802c08c831299ebe99bcd",
    "runtime/rust/typeii/tests/FIXTURE_PROVENANCE.json": "dfee51903025b4c9d3f62f63581271bd3b6a98cb",
}

def fail(message: str) -> NoReturn:
    raise SystemExit("FAIL: " + message)

def git_bytes(repo: Path, *args: str) -> bytes:
    """Return stdout verbatim: no decoding, universal-newline conversion, or strip."""
    result = subprocess.run(
        ["git", "--no-replace-objects", *args], cwd=repo,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30,
    )
    if result.returncode:
        fail("git " + " ".join(args) + ": " + result.stderr.decode("utf-8", errors="replace").strip())
    return result.stdout

def git_line(repo: Path, *args: str) -> str:
    """Metadata only. Remove the Git protocol's final LF, not path whitespace."""
    line = git_bytes(repo, *args).decode("utf-8").removesuffix("\n")
    if "\n" in line or "\0" in line:
        fail("expected one Git metadata line")
    return line

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def require_equal(actual, expected, label: str) -> None:
    if actual != expected:
        fail(f"{label}: expected {expected!r}, observed {actual!r}")

def validate_local() -> dict:
    entries = {}
    for line in (ROOT / "MANIFEST.sha256").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, name = line.split(maxsplit=1)
        if name in entries:
            fail("duplicate manifest entry " + name)
        entries[name] = expected
    require_equal(set(entries), LOCAL_FILES, "local manifest closure")
    for name, expected in entries.items():
        require_equal(digest((ROOT / name).read_bytes()), expected, name + " digest mismatch")
    package = json.loads((ROOT / "PACKAGE.json").read_bytes())
    require_equal(package["package_id"], PACKAGE_ID, "package id")
    auth = package["canonical_authority_package"]
    for key, value in {
        "branch": AUTH_BRANCH, "head": AUTH_HEAD, "tree": AUTH_TREE,
        "transport": "DIRECT_TEXT_FILES", "index_path": AUTH_INDEX,
        "index_blob": AUTH_INDEX_BLOB, "direct_path": AUTH_PATH,
        "files_sha256": DIRECT_FILES,
    }.items():
        require_equal(auth[key], value, "authority " + key)
    impl = package["implementation"]
    for key, value in {"base_branch": BASE_BRANCH, "base_head": BASE_HEAD,
                       "base_tree": BASE_TREE, "exact_next_action": "RF03-AUTH-01"}.items():
        require_equal(impl[key], value, "implementation " + key)
    repair = package["validator_repair"]
    require_equal(repair["historical_r1_head"], R1_HEAD, "historical R1 head")
    require_equal(repair["historical_r1_tree"], R1_TREE, "historical R1 tree")
    require_equal(repair["source_blobs"], SOURCE_BLOBS, "source pins")
    require_equal(repair["r2_live_replacement"], "R4_EQUIVALENT_IDENTITY_CHECKS_WITH_HISTORICAL_R1_PIN",
                  "explicit R2 live-check replacement")
    require_equal(package["claim_boundary"]["current"], "NO_PASS_RF03_CLAIM", "claim boundary")
    return package

def validate_source_pins(repo: Path) -> None:
    # R1 is a historical input, not the current tip of the bootstrap branch.
    require_equal(git_line(repo, "rev-parse", "--verify", R1_HEAD + "^{commit}"), R1_HEAD,
                  "historical R1 commit")
    require_equal(git_line(repo, "rev-parse", R1_HEAD + "^{tree}"), R1_TREE, "historical R1 tree")
    for path, expected in SOURCE_BLOBS.items():
        require_equal(git_line(repo, "rev-parse", BASE_HEAD + ":" + path), expected,
                      "source blob " + path)

def validate_live(repo_arg: Path, materialize: Path | None = None) -> dict:
    if materialize is not None and (materialize.exists() or materialize.is_symlink()):
        fail("materialization target already exists; preserving it")
    repo = Path(git_line(repo_arg, "rev-parse", "--show-toplevel"))
    for branch, head, tree, label in (
        (AUTH_BRANCH, AUTH_HEAD, AUTH_TREE, "authority"),
        (BASE_BRANCH, BASE_HEAD, BASE_TREE, "RF-02C base"),
    ):
        require_equal(git_line(repo, "rev-parse", "--verify", "refs/remotes/origin/" + branch), head,
                      label + (" branch moved" if label == "authority" else " moved"))
        require_equal(git_line(repo, "rev-parse", head + "^{tree}"), tree, label + " tree")
    require_equal(git_line(repo, "rev-parse", AUTH_HEAD + ":" + AUTH_INDEX), AUTH_INDEX_BLOB,
                  "authority index blob")

    with tempfile.TemporaryDirectory(prefix="bass-rf03-validate-") as td:
        tmp = Path(td)
        index_bytes = git_bytes(repo, "cat-file", "blob", AUTH_HEAD + ":" + AUTH_INDEX)
        (tmp / "PACKAGE_INDEX.json").write_bytes(index_bytes)
        index = json.loads(index_bytes)
        require_equal(index["canonical_transport"], "DIRECT_TEXT_FILES", "remote transport")
        require_equal(index["canonical_path"], AUTH_PATH, "remote direct path")
        indexed = {}
        for item in index["canonical_files"]:
            name = item["name"]
            if name in indexed:
                fail("duplicate canonical index entry " + name)
            indexed[name] = item["sha256"]
        require_equal(indexed, DIRECT_FILES, "remote package digest map")
        for name, expected in DIRECT_FILES.items():
            data = git_bytes(repo, "cat-file", "blob", AUTH_HEAD + ":" + AUTH_PATH + "/" + name)
            require_equal(digest(data), expected, "remote direct file digest mismatch: " + name)
            (tmp / name).write_bytes(data)

        # Execute the ORIGINAL R2 offline semantic/manifest checker, unchanged.
        # Its --live entry is explicitly superseded, not silently bypassed:
        # all source identities are checked here, with R1 fixed to its historical object.
        result = subprocess.run(
            [sys.executable, str(tmp / "validate_package.py")], cwd=tmp,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30,
        )
        if result.returncode:
            fail("R2 offline checker: " + (result.stdout + result.stderr).decode("utf-8", errors="replace"))
        child = json.loads(result.stdout)
        for key, value in {"status": "PASS", "package_id": AUTH_PACKAGE_ID,
                           "base_head": BASE_HEAD, "base_tree": BASE_TREE, "live": False,
                           "exact_next_action": "RF03-AUTH-01"}.items():
            require_equal(child[key], value, "R2 offline result " + key)
        validate_source_pins(repo)
        if materialize is not None:
            shutil.copytree(tmp, materialize)
    return {"direct_files": len(DIRECT_FILES), "source_blobs": len(SOURCE_BLOBS),
            "r2_offline_semantics": "PASS", "historical_r1_commit_tree": "PASS",
            "r2_live_replacement": "PASS_R4_HISTORICAL_PIN_CHECKS",
            "materialized": str(materialize) if materialize is not None else None}

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--materialize", type=Path)
    args = parser.parse_args()
    if args.materialize is not None and not args.live:
        parser.error("--materialize requires --live")
    try:
        validate_local()
        detail = validate_live(args.repo, args.materialize) if args.live else {}
    except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as exc:
        fail(type(exc).__name__ + ": " + str(exc))
    print(json.dumps({"status": "PASS", "package_id": PACKAGE_ID,
        "validation_scope": "BOOTSTRAP_AND_SOURCE_IDENTITY_ONLY",
        "authority_head": AUTH_HEAD, "authority_tree": AUTH_TREE,
        "transport": "DIRECT_TEXT_FILES", "exact_next_action": "RF03-AUTH-01",
        "claim": "NO_PASS_RF03_CLAIM", "live": args.live, "detail": detail}, sort_keys=True))

if __name__ == "__main__":
    main()
