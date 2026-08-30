#!/usr/bin/env python3
"""Fetch an RF-04 continuation payload from pinned raw Git objects.

This intake tool never reads payload bytes from the working tree.  It validates
the exact commit/tree chain, reads regular-file blobs with ``git cat-file``,
checks the manifest and contract closure, and only then materializes into a new
directory outside the source repository.

A successful run proves delivery intake only.  It does not apply the telemetry
patch and does not promote the scientific claim beyond ``NO_PASS_RF04``.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Iterable


class IntakeError(RuntimeError):
    """Fail-closed intake error."""


@dataclass(frozen=True)
class ObjectPin:
    label: str
    commit: str
    tree: str


@dataclass(frozen=True)
class IntakeSpec:
    repository: str
    objects: tuple[ObjectPin, ...]
    parent_edges: tuple[tuple[str, str], ...]
    payload_commit: str
    payload_tree: str
    manifest_path: str
    manifest_blob_sha1: str
    manifest_sha256: str
    expected_entries: int
    allowed_prefix: str
    scientific_claim: str
    next_action: str


@dataclass(frozen=True)
class ManifestEntry:
    sha256: str
    path: str


@dataclass(frozen=True)
class PayloadFile:
    path: str
    sha256: str
    blob_sha1: str
    mode: str
    data: bytes


@dataclass(frozen=True)
class ValidatedPayload:
    spec: IntakeSpec
    manifest_bytes: bytes
    files: dict[str, PayloadFile]


SPEC = IntakeSpec(
    repository="cosmosapjw-quantum/bass",
    objects=(
        ObjectPin(
            "base",
            "2aaad1d72064ddeb60b27a0ec15536d0a2ec6a28",
            "5b9a15c4a378a28e9592ede5a208e8cafc45c482",
        ),
        ObjectPin(
            "invalid_payload",
            "4538ac92fcf5cf70a4d73e2cb3e53125a49590ba",
            "982173d6e3fa1760c58cd547545c2b17f37c7a11",
        ),
        ObjectPin(
            "publication",
            "70e12b8ac18151071d3ecbd1bd78dfd581ee4270",
            "eff0f95c9124e642279d841e68c6e07fdb9b6ce8",
        ),
        ObjectPin(
            "prior_terminal",
            "989f9c38ba625f1de74941fd3e5f51bdd753d1bd",
            "f101c0560fa9b719892365561d7b2d0f2a1054ed",
        ),
        ObjectPin(
            "payload",
            "16f5811beb7d73fae800ff90caf30f69deebc9fd",
            "85a9164e01ea77d312b185809b3698363c750526",
        ),
    ),
    parent_edges=(
        (
            "4538ac92fcf5cf70a4d73e2cb3e53125a49590ba",
            "2aaad1d72064ddeb60b27a0ec15536d0a2ec6a28",
        ),
        (
            "70e12b8ac18151071d3ecbd1bd78dfd581ee4270",
            "4538ac92fcf5cf70a4d73e2cb3e53125a49590ba",
        ),
        (
            "989f9c38ba625f1de74941fd3e5f51bdd753d1bd",
            "70e12b8ac18151071d3ecbd1bd78dfd581ee4270",
        ),
        (
            "16f5811beb7d73fae800ff90caf30f69deebc9fd",
            "989f9c38ba625f1de74941fd3e5f51bdd753d1bd",
        ),
    ),
    payload_commit="16f5811beb7d73fae800ff90caf30f69deebc9fd",
    payload_tree="85a9164e01ea77d312b185809b3698363c750526",
    manifest_path="research/continuation_20260830/MANIFEST.sha256",
    manifest_blob_sha1="32473fb754c9b6b84e5e5980c551860297f1054a",
    manifest_sha256="af2ed1220c76d36bd82e5362b1f4a5fb0bb8061eb6470129458333c533b320de",
    expected_entries=18,
    allowed_prefix="research/continuation_20260830/",
    scientific_claim="NO_PASS_RF04",
    next_action="BASS-LOCAL-01_NATIVE_TELEMETRY_PARITY",
)


def _git(repo: Path, *args: str) -> bytes:
    env = os.environ.copy()
    env["GIT_NO_REPLACE_OBJECTS"] = "1"
    proc = subprocess.run(
        ["git", "--no-replace-objects", "-C", str(repo), *args],
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode:
        detail = proc.stderr.decode("utf-8", errors="replace").strip()
        raise IntakeError(f"git command failed ({args[0]}): {detail}")
    return proc.stdout


def _decode_ascii(data: bytes, label: str) -> str:
    try:
        return data.decode("ascii")
    except UnicodeDecodeError as exc:
        raise IntakeError(f"non-ASCII {label}") from exc


def _repository_root(repo: Path | str) -> Path:
    candidate = Path(repo).expanduser().resolve(strict=True)
    if not candidate.is_dir():
        raise IntakeError(f"repository path is not a directory: {candidate}")
    top = _decode_ascii(
        _git(candidate, "rev-parse", "--show-toplevel"), "repository root"
    ).strip()
    root = Path(top).resolve(strict=True)
    if not root.is_dir():
        raise IntakeError(f"invalid repository root: {root}")
    return root


def _canonical_payload_path(path: str, allowed_prefix: str) -> None:
    if not path or "\\" in path or "\x00" in path or path.startswith("/"):
        raise IntakeError(f"unsafe manifest path: {path!r}")
    parts = path.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise IntakeError(f"non-canonical manifest path: {path!r}")
    if str(PurePosixPath(path)) != path:
        raise IntakeError(f"non-canonical manifest path: {path!r}")
    if allowed_prefix and not path.startswith(allowed_prefix):
        raise IntakeError(f"manifest path outside payload prefix: {path!r}")


def parse_manifest(
    data: bytes, *, expected_entries: int, allowed_prefix: str
) -> tuple[ManifestEntry, ...]:
    if not data.endswith(b"\n"):
        raise IntakeError("manifest must end with one LF-delimited record")
    text = _decode_ascii(data, "manifest")
    entries: list[ManifestEntry] = []
    seen: set[str] = set()
    pattern = re.compile(r"([0-9a-f]{64})  ([^\r\n]+)")
    for line_number, line in enumerate(text.splitlines(), start=1):
        match = pattern.fullmatch(line)
        if match is None:
            raise IntakeError(f"malformed manifest line {line_number}")
        digest, path = match.groups()
        _canonical_payload_path(path, allowed_prefix)
        if path in seen:
            raise IntakeError(f"duplicate manifest path: {path}")
        seen.add(path)
        entries.append(ManifestEntry(digest, path))
    if len(entries) != expected_entries:
        raise IntakeError(
            f"manifest entry count mismatch: {len(entries)} != {expected_entries}"
        )
    return tuple(entries)


def _resolve_tree(repo: Path, commit: str) -> str:
    return _decode_ascii(
        _git(repo, "rev-parse", "--verify", f"{commit}^{{tree}}"), "tree"
    ).strip()


def _resolve_commit(repo: Path, commit: str) -> str:
    return _decode_ascii(
        _git(repo, "rev-parse", "--verify", f"{commit}^{{commit}}"), "commit"
    ).strip()


def _parents(repo: Path, commit: str) -> tuple[str, ...]:
    raw_commit = _git(repo, "cat-file", "commit", commit)
    parents: list[str] = []
    for line in raw_commit.split(b"\n"):
        if not line:
            break
        if line.startswith(b"parent "):
            parent = _decode_ascii(line[7:], "raw commit parent")
            if re.fullmatch(r"[0-9a-f]{40}", parent) is None:
                raise IntakeError(f"malformed raw parent in commit: {commit}")
            parents.append(parent)
    return tuple(parents)


def _blob_at_path(repo: Path, commit: str, path: str) -> tuple[str, str, bytes]:
    _canonical_payload_path(path, "")
    rows = [
        row
        for row in _git(repo, "ls-tree", "-z", "--full-tree", commit, "--", path).split(
            b"\x00"
        )
        if row
    ]
    if len(rows) != 1 or b"\t" not in rows[0]:
        raise IntakeError(f"missing or ambiguous payload path: {path}")
    metadata, raw_path = rows[0].split(b"\t", 1)
    fields = metadata.split()
    if len(fields) != 3:
        raise IntakeError(f"malformed Git tree row: {path}")
    mode, object_type, blob_sha1 = (_decode_ascii(field, "tree row") for field in fields)
    got_path = raw_path.decode("utf-8", errors="strict")
    if got_path != path:
        raise IntakeError(f"Git path mismatch: {got_path!r} != {path!r}")
    if object_type != "blob" or mode not in {"100644", "100755"}:
        raise IntakeError(f"non-regular payload object at {path}: {mode} {object_type}")
    data = _git(repo, "cat-file", "blob", blob_sha1)
    return mode, blob_sha1, data


def _validate_contract(
    contract: object, covered_paths: set[str], spec: IntakeSpec
) -> None:
    if not isinstance(contract, dict):
        raise IntakeError("CONTRACT.json must be an object")
    if contract.get("repository") != spec.repository:
        raise IntakeError("CONTRACT.json repository mismatch")
    base_pins = [pin for pin in spec.objects if pin.label == "base"]
    if len(base_pins) != 1:
        raise IntakeError("intake specification must contain one base pin")
    base = contract.get("base")
    if not isinstance(base, dict):
        raise IntakeError("invalid CONTRACT.json base")
    if base.get("commit") != base_pins[0].commit or base.get("tree") != base_pins[0].tree:
        raise IntakeError("CONTRACT.json base mismatch")
    if contract.get("current_scientific_claim") != spec.scientific_claim:
        raise IntakeError("CONTRACT.json scientific claim mismatch")
    if contract.get("exact_next_action") != spec.next_action:
        raise IntakeError("CONTRACT.json next action mismatch")
    if contract.get("scientific_promotion") is not False:
        raise IntakeError("CONTRACT.json scientific promotion must be false")
    delivery_paths = contract.get("delivery_paths")
    if not isinstance(delivery_paths, list) or not all(
        isinstance(path, str) for path in delivery_paths
    ):
        raise IntakeError("invalid CONTRACT.json delivery_paths")
    if len(delivery_paths) != len(set(delivery_paths)):
        raise IntakeError("duplicate CONTRACT.json delivery_paths")
    if set(delivery_paths) != covered_paths:
        raise IntakeError("manifest/CONTRACT.json delivery closure mismatch")


def validate_payload(repo: Path | str, spec: IntakeSpec = SPEC) -> ValidatedPayload:
    source = _repository_root(repo)
    _git(source, "rev-parse", "--git-dir")

    for pin in spec.objects:
        if _resolve_commit(source, pin.commit) != pin.commit:
            raise IntakeError(f"commit mismatch for {pin.label}")
        actual_tree = _resolve_tree(source, pin.commit)
        if actual_tree != pin.tree:
            raise IntakeError(
                f"tree mismatch for {pin.label}: {actual_tree} != {pin.tree}"
            )
    if _resolve_tree(source, spec.payload_commit) != spec.payload_tree:
        raise IntakeError("payload tree mismatch")
    for child, expected_parent in spec.parent_edges:
        actual_parents = _parents(source, child)
        if actual_parents != (expected_parent,):
            raise IntakeError(
                f"parent mismatch for {child}: {actual_parents} != {(expected_parent,)}"
            )

    manifest_mode, manifest_blob, manifest_bytes = _blob_at_path(
        source, spec.payload_commit, spec.manifest_path
    )
    if manifest_mode != "100644":
        raise IntakeError(f"manifest mode mismatch: {manifest_mode}")
    if manifest_blob != spec.manifest_blob_sha1:
        raise IntakeError(
            f"manifest blob mismatch: {manifest_blob} != {spec.manifest_blob_sha1}"
        )
    manifest_digest = hashlib.sha256(manifest_bytes).hexdigest()
    if manifest_digest != spec.manifest_sha256:
        raise IntakeError(
            f"manifest SHA-256 mismatch: {manifest_digest} != {spec.manifest_sha256}"
        )
    entries = parse_manifest(
        manifest_bytes,
        expected_entries=spec.expected_entries,
        allowed_prefix=spec.allowed_prefix,
    )

    files: dict[str, PayloadFile] = {}
    for entry in entries:
        mode, blob_sha1, data = _blob_at_path(source, spec.payload_commit, entry.path)
        actual = hashlib.sha256(data).hexdigest()
        if actual != entry.sha256:
            raise IntakeError(
                f"payload byte mismatch: {entry.path}: {actual} != {entry.sha256}"
            )
        files[entry.path] = PayloadFile(
            path=entry.path,
            sha256=entry.sha256,
            blob_sha1=blob_sha1,
            mode=mode,
            data=data,
        )

    contract_path = f"{spec.allowed_prefix}CONTRACT.json"
    contract_file = files.get(contract_path)
    if contract_file is None:
        raise IntakeError("CONTRACT.json is not covered by the manifest")
    try:
        contract = json.loads(contract_file.data)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise IntakeError("invalid CONTRACT.json") from exc
    _validate_contract(contract, set(files), spec)

    return ValidatedPayload(spec=spec, manifest_bytes=manifest_bytes, files=files)


def _safe_destination(destination: Path | str, source_repo: Path) -> Path:
    raw = Path(destination).expanduser()
    if not raw.name or raw == Path(raw.anchor):
        raise IntakeError(f"unsafe destination: {raw}")
    absolute = Path(os.path.abspath(raw))
    if absolute.exists() or absolute.is_symlink():
        raise IntakeError(f"destination already exists: {absolute}")
    unresolved_parent = absolute.parent
    if unresolved_parent.is_symlink():
        raise IntakeError(f"unsafe destination parent symlink: {unresolved_parent}")
    parent = unresolved_parent.resolve(strict=True)
    if not parent.is_dir():
        raise IntakeError(f"unsafe destination parent: {parent}")
    resolved_destination = parent / absolute.name
    if resolved_destination.exists() or resolved_destination.is_symlink():
        raise IntakeError(f"destination already exists: {resolved_destination}")
    source = source_repo.resolve(strict=True)
    if resolved_destination == source or resolved_destination.is_relative_to(source):
        raise IntakeError("destination must not be inside source repository")
    return resolved_destination


def _write_exclusive(path: Path, data: bytes, mode: int) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags, mode)
    try:
        with os.fdopen(descriptor, "wb", closefd=False) as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
            os.fchmod(stream.fileno(), mode)
    finally:
        os.close(descriptor)


def _cleanup_owned_directory(path: Path, identity: tuple[int, int]) -> None:
    try:
        stat = path.lstat()
    except FileNotFoundError:
        return
    if path.is_symlink() or not path.is_dir() or (stat.st_dev, stat.st_ino) != identity:
        return
    shutil.rmtree(path)


def materialize(
    validated: ValidatedPayload,
    destination: Path | str | None,
    source_repo: Path | str,
) -> dict[str, object]:
    source = _repository_root(source_repo)
    if destination is None:
        root = Path(tempfile.mkdtemp(prefix="bass-rf04-intake-")).resolve(strict=True)
        if root == source or root.is_relative_to(source):
            identity = (root.lstat().st_dev, root.lstat().st_ino)
            _cleanup_owned_directory(root, identity)
            raise IntakeError("temporary destination resolved inside source repository")
    else:
        root = _safe_destination(destination, source)
        try:
            root.mkdir(mode=0o700)
        except FileExistsError as exc:
            raise IntakeError(f"destination already exists: {root}") from exc
    stat = root.lstat()
    identity = (stat.st_dev, stat.st_ino)
    try:
        manifest_target = root / validated.spec.manifest_path
        manifest_target.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
        _write_exclusive(manifest_target, validated.manifest_bytes, 0o644)
        for payload in validated.files.values():
            target = root / payload.path
            target.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
            _write_exclusive(
                target,
                payload.data,
                0o755 if payload.mode == "100755" else 0o644,
            )
        if hashlib.sha256(manifest_target.read_bytes()).hexdigest() != validated.spec.manifest_sha256:
            raise IntakeError("post-write manifest verification failed")
        for payload in validated.files.values():
            actual = hashlib.sha256((root / payload.path).read_bytes()).hexdigest()
            if actual != payload.sha256:
                raise IntakeError(f"post-write payload verification failed: {payload.path}")
    except Exception:
        _cleanup_owned_directory(root, identity)
        raise

    return receipt(validated, source, root)


def receipt(
    validated: ValidatedPayload, source_repo: Path, output: Path | None
) -> dict[str, object]:
    return {
        "status": "PASS_IMMUTABLE_PAYLOAD_INTAKE_ONLY",
        "repository": validated.spec.repository,
        "source_repo": str(source_repo),
        "payload_commit": validated.spec.payload_commit,
        "payload_tree": validated.spec.payload_tree,
        "manifest_blob_sha1": validated.spec.manifest_blob_sha1,
        "manifest_sha256": validated.spec.manifest_sha256,
        "manifest_entries": len(validated.files),
        "materialized_root": None if output is None else str(output),
        "historical_invalid_payload": "4538ac92fcf5cf70a4d73e2cb3e53125a49590ba",
        "historical_failure": "BLOCKED_IMMUTABLE_PAYLOAD_MANIFEST_MISMATCH",
        "scientific_claim": validated.spec.scientific_claim,
        "next_action": validated.spec.next_action,
        "production_source_changed": False,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", type=Path, help="existing authenticated BASS clone")
    parser.add_argument(
        "--out",
        type=Path,
        help="new, nonexistent destination outside the source clone",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="validate raw Git objects without materializing files",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    if args.validate_only and args.out is not None:
        parser.error("--validate-only and --out are mutually exclusive")
    try:
        validated = validate_payload(args.repo, SPEC)
        source = _repository_root(args.repo)
        if args.validate_only:
            result = receipt(validated, source, None)
        else:
            result = materialize(validated, args.out, source)
    except (IntakeError, OSError) as exc:
        print(f"STOP_INVALID: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
