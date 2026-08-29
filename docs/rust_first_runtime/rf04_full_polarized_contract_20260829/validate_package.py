#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
BASE_HEAD = "50b6e9f7a6741b7e4807396b94845e0b8b4c1e8"
# The implementation commit above is ancestry evidence; the terminal source is below.
TERMINAL_HEAD = "50b6e9f7a6741b7fd25b0421d2a674b9eb92cdda"
TERMINAL_TREE = "b32fcc26ca51dcaca9e9225d48b03fe9e02988ed"
SOURCE_BLOBS = {
    "_rustcore/src/kinetic/rf04_typeii.rs": "71508ebb9b3a5abd3bc403d6a24502ad9de09d39",
    "runtime/rust/typeii/typeii_polarized_runtime.rs": "a852431274c206cc81b063f9501e46a524bd3765",
    "runtime/rust/typeii/typeii_polarized_runtime_physical.rs": "03684d7a9ef76be3bb06841af86bb5822574bab3",
    "runtime/rust/typeii/typeii_polarized_remap.rs": "5f7a1e580df3855f07f567fb3baa0e339d52c82e",
    "runtime/rust/typeii/typeii_polarized_liouville.rs": "da6fade06f717ab938b0ec4c712ab239e78c998a",
    "runtime/rust/typeii/tests/typeii_pre_liouville_safety.rs": "6936d2a7116bc9b431c884c7f53b68681983d483",
    "docs/rust_first_runtime/rf04_external_review_resume_20260829/CONTRACT.json": "a6cdf5c3c0b32fa09083f13439ddd16743d19e3a",
}


def fail(message: str) -> None:
    raise SystemExit("FAIL: " + message)


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "--no-replace-objects", *args],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=45,
    )
    if result.returncode:
        fail("git " + " ".join(args) + ": " + result.stderr.strip())
    return result.stdout.removesuffix("\n")


def validate_local() -> None:
    package = json.loads((ROOT / "PACKAGE.json").read_text())
    source_map = json.loads((ROOT / "SOURCE_MAP.json").read_text())
    units = json.loads((ROOT / "WORK_UNITS.json").read_text())
    acceptance = json.loads((ROOT / "ACCEPTANCE_MATRIX.json").read_text())
    if package["package_id"] != "BASS-RF04-FULL-POLARIZED-CONTRACT-20260829-R1":
        fail("package id")
    if package["base"]["head"] != TERMINAL_HEAD or package["base"]["tree"] != TERMINAL_TREE:
        fail("terminal source identity")
    if package["execution"]["exact_next_action"] != "RF04-POL-AUTH-00_SOURCE_DERIVATION":
        fail("next action")
    if len(package["open_contracts"]) != 5:
        fail("open-contract closure")
    if source_map["source_head"] != TERMINAL_HEAD or source_map["source_tree"] != TERMINAL_TREE:
        fail("source-map identity")
    if units["exact_next_action"] != "RF04-POL-AUTH-00_SOURCE_DERIVATION":
        fail("work-unit next action")
    if acceptance["terminal_claim"] != "PASS_RF04":
        fail("terminal claim")


def validate_live(repo_arg: Path) -> None:
    repo = Path(git(repo_arg, "rev-parse", "--show-toplevel"))
    if git(repo, "rev-parse", TERMINAL_HEAD + "^{commit}") != TERMINAL_HEAD:
        fail("terminal commit absent")
    if git(repo, "rev-parse", TERMINAL_HEAD + "^{tree}") != TERMINAL_TREE:
        fail("terminal tree")
    if git(repo, "merge-base", "--is-ancestor", BASE_HEAD, TERMINAL_HEAD) != "":
        pass
    for path, blob in SOURCE_BLOBS.items():
        if git(repo, "rev-parse", TERMINAL_HEAD + ":" + path) != blob:
            fail("source blob " + path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    validate_local()
    if args.live:
        validate_live(Path(args.repo))
    print(json.dumps({
        "status": "PASS",
        "package_id": "BASS-RF04-FULL-POLARIZED-CONTRACT-20260829-R1",
        "terminal_head": TERMINAL_HEAD,
        "terminal_tree": TERMINAL_TREE,
        "source_blobs": len(SOURCE_BLOBS),
        "exact_next_action": "RF04-POL-AUTH-00_SOURCE_DERIVATION",
        "claim": "NO_PASS_RF04",
        "live": args.live,
    }, sort_keys=True))
