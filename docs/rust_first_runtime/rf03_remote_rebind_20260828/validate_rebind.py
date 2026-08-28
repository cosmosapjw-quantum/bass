#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from typing import NoReturn

ROOT = Path(__file__).resolve().parent
PACKAGE_ID = "BASS-RF03-REMOTE-REBIND-20260828-R3"
AUTH_BRANCH = "agent/plans/rf03-authority-resolution-20260828-r2"
AUTH_HEAD = "55335d3817a82da7e0f9bf24ef7632a2533645d3"
AUTH_TREE = "7c02689430d01abdf998c5b7ab1c5a6eb48859f4"
AUTH_INDEX = "docs/rust_first_runtime/rf03_authority_resolution_20260828/PACKAGE_INDEX.json"
AUTH_PATH = "docs/rust_first_runtime/rf03_authority_resolution_20260828/direct"
BASE_BRANCH = "agent/architecture/rust-first-rf02c-20260826-r1"
BASE_HEAD = "dfa17457d402bd441d3fdf786c2d79c529512ee5"
BASE_TREE = "9fc67fb0ba10e091e25a14d7e1fac88b77a0241e"
LOCAL_FILES = {
    "README.md",
    "PACKAGE.json",
    "CHANGELOG.md",
    "CODEX_HANDOFF.md",
    "GITHUB_ROUNDTRIP_RECEIPT.json",
    "validate_rebind.py",
}
DIRECT_FILES = {"AUTHORITY_CONTRACT.json": "81f2207bcbfa8ee01713c0b099383ab70bd9d929fd3d0a16813c4da3b3906ab5", "CODEX_HANDOFF.md": "e9d36c24dff60ce86856986d67c11083f028821c678530fab3e334d9b7263d66", "MANIFEST.sha256": "0109b164b872411af55b3d66be56315721a314a4b662b742b3b116a9f094b25d", "README.md": "e61a5845de87b80127a3b92155c1e9afab95b9cc8d1c2f6cb9ab07dd08964c4a", "WORK_UNITS.json": "cfd27422c2c9353a97bd257a5de33a4a2a5781e3ad39266c1bc3bd6b65b4fd82", "validate_package.py": "caf503153085c8ad2900dd80ef26aa905b8cb8bf7e8541ebd51a7736466c80f8"}

def fail(message: str) -> NoReturn:
    raise SystemExit("FAIL: " + message)

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=repo, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    if result.returncode:
        fail("git " + " ".join(args) + ": " + result.stderr.strip())
    return result.stdout.strip()

def validate_local() -> dict:
    entries = {}
    for line in (ROOT / "MANIFEST.sha256").read_text(encoding="utf-8").splitlines():
        if line.strip():
            digest, name = line.split(maxsplit=1)
            if name in entries:
                fail("duplicate manifest entry " + name)
            entries[name] = digest
    if set(entries) != LOCAL_FILES:
        fail("local manifest closure mismatch")
    for name, digest in entries.items():
        if sha256(ROOT / name) != digest:
            fail(name + " digest mismatch")

    package = json.loads((ROOT / "PACKAGE.json").read_text(encoding="utf-8"))
    if package.get("package_id") != PACKAGE_ID:
        fail("package_id mismatch")
    auth = package.get("canonical_authority_package", {})
    required = {
        "branch": AUTH_BRANCH,
        "head": AUTH_HEAD,
        "tree": AUTH_TREE,
        "transport": "DIRECT_TEXT_FILES",
        "index_path": AUTH_INDEX,
        "direct_path": AUTH_PATH,
    }
    for key, value in required.items():
        if auth.get(key) != value:
            fail("authority " + key + " mismatch")
    if auth.get("files_sha256") != DIRECT_FILES:
        fail("direct file digest map mismatch")
    if package.get("claim_boundary", {}).get("current") != "NO_PASS_RF03_CLAIM":
        fail("claim boundary mismatch")
    if package.get("implementation", {}).get("exact_next_action") != "RF03-AUTH-01":
        fail("next action mismatch")
    if package.get("superseded_inputs", {}).get("forbidden_transport") != "ZIP_OR_MULTIPART_BINARY":
        fail("deprecated transport guard missing")
    return package

def validate_live(repo_arg: Path) -> None:
    repo = Path(git(repo_arg, "rev-parse", "--show-toplevel"))
    if git(repo, "rev-parse", "--verify", "origin/" + AUTH_BRANCH) != AUTH_HEAD:
        fail("authority branch moved")
    if git(repo, "rev-parse", AUTH_HEAD + "^{tree}") != AUTH_TREE:
        fail("authority tree mismatch")
    if git(repo, "rev-parse", "--verify", "origin/" + BASE_BRANCH) != BASE_HEAD:
        fail("RF-02C base moved")
    if git(repo, "rev-parse", BASE_HEAD + "^{tree}") != BASE_TREE:
        fail("RF-02C base tree mismatch")

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        index_text = git(repo, "show", AUTH_HEAD + ":" + AUTH_INDEX)
        (tmp / "PACKAGE_INDEX.json").write_text(index_text, encoding="utf-8")
        index = json.loads(index_text)
        if index.get("canonical_transport") != "DIRECT_TEXT_FILES":
            fail("remote canonical transport mismatch")
        if index.get("canonical_path") != AUTH_PATH:
            fail("remote canonical path mismatch")
        indexed = {item["name"]: item["sha256"] for item in index["canonical_files"]}
        if indexed != DIRECT_FILES:
            fail("remote package index digest map mismatch")

        for name, digest in DIRECT_FILES.items():
            text = git(repo, "show", AUTH_HEAD + ":" + AUTH_PATH + "/" + name)
            path = tmp / name
            path.write_text(text, encoding="utf-8")
            if sha256(path) != digest:
                fail("remote direct file digest mismatch: " + name)

        result = subprocess.run(
            ["python", "validate_package.py", "--live", "--repo", str(repo)],
            cwd=tmp, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if result.returncode:
            fail("direct package validator: " + result.stderr.strip())

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()

    validate_local()
    if args.live:
        validate_live(Path(args.repo))
    print(json.dumps({
        "status": "PASS",
        "package_id": PACKAGE_ID,
        "authority_head": AUTH_HEAD,
        "authority_tree": AUTH_TREE,
        "transport": "DIRECT_TEXT_FILES",
        "exact_next_action": "RF03-AUTH-01",
        "claim": "NO_PASS_RF03_CLAIM",
        "live": args.live,
    }, sort_keys=True))

if __name__ == "__main__":
    main()
