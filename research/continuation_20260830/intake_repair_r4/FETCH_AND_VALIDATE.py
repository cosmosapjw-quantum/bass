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
import secrets
import stat
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
    source_layout: RepositoryLayout


@dataclass(frozen=True)
class ProtectedRoot:
    label: str
    path: Path
    identity: tuple[int, int]


@dataclass(frozen=True)
class RepositoryLayout:
    worktree: Path
    git_dir: Path
    common_git_dir: Path
    worktree_identity: tuple[int, int]
    git_dir_identity: tuple[int, int]
    common_git_dir_identity: tuple[int, int]
    protected_roots: tuple[ProtectedRoot, ...]



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


def _git_environment() -> dict[str, str]:
    # No ambient Git routing or injected config may change what ``-C repo``
    # means.  The commands below are local, read-only object queries and need
    # none of the GIT_* variables inherited from a caller.
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env["GIT_NO_REPLACE_OBJECTS"] = "1"
    env["GIT_NO_LAZY_FETCH"] = "1"
    env["GIT_OPTIONAL_LOCKS"] = "0"
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["LC_ALL"] = "C"
    return env


def _git_argv(repo: Path, *args: str) -> list[str]:
    return [
        "git",
        "--no-replace-objects",
        "--no-lazy-fetch",
        "-C",
        str(repo),
        *args,
    ]


def _git(repo: Path, *args: str) -> bytes:
    env = _git_environment()
    proc = subprocess.run(
        _git_argv(repo, *args),
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


def _decode_git_path(data: bytes, label: str) -> str:
    if not data.endswith(b"\n"):
        raise IntakeError(f"unterminated {label}")
    raw = data[:-1]
    if not raw or b"\x00" in raw or b"\n" in raw or b"\r" in raw:
        raise IntakeError(f"ambiguous {label}")
    return os.fsdecode(raw)


def _repository_layout(repo: Path | str) -> RepositoryLayout:
    candidate = Path(repo).expanduser().resolve(strict=True)
    if not candidate.is_dir():
        raise IntakeError(f"repository path is not a directory: {candidate}")
    top = _decode_git_path(
        _git(candidate, "rev-parse", "--show-toplevel"), "repository root"
    )
    root = Path(top).resolve(strict=True)
    if not root.is_dir():
        raise IntakeError(f"invalid repository root: {root}")
    if candidate != root and not candidate.is_relative_to(root):
        raise IntakeError(
            "supplied repository path was redirected outside its resolved worktree"
        )
    git_dir_text = _decode_git_path(
        _git(root, "rev-parse", "--absolute-git-dir"), "Git directory"
    )
    common_dir_text = _decode_git_path(
        _git(
            root,
            "rev-parse",
            "--path-format=absolute",
            "--git-common-dir",
        ),
        "common Git directory",
    )
    git_dir = Path(git_dir_text).resolve(strict=True)
    common_git_dir = Path(common_dir_text).resolve(strict=True)
    if not git_dir.is_dir() or not common_git_dir.is_dir():
        raise IntakeError("invalid Git metadata directory")

    raw_worktrees = _git(root, "worktree", "list", "--porcelain", "-z")
    worktrees: list[Path] = [root]
    for field in raw_worktrees.split(b"\x00"):
        if not field.startswith(b"worktree "):
            continue
        candidate_path = Path(os.fsdecode(field[len(b"worktree ") :]))
        try:
            worktree = candidate_path.resolve(strict=True)
        except FileNotFoundError:
            continue
        if worktree.is_dir() and worktree not in worktrees:
            worktrees.append(worktree)

    protected: list[ProtectedRoot] = []
    seen_identities: set[tuple[int, int]] = set()
    candidates = [("source repository", root)]
    candidates.extend(
        ("registered Git worktree", worktree)
        for worktree in worktrees
        if worktree != root
    )
    candidates.extend(
        (("Git directory", git_dir), ("common Git directory", common_git_dir))
    )
    for label, protected_path in candidates:
        protected_stat = os.stat(protected_path, follow_symlinks=False)
        if not stat.S_ISDIR(protected_stat.st_mode):
            raise IntakeError(f"invalid protected repository path: {protected_path}")
        identity = (protected_stat.st_dev, protected_stat.st_ino)
        if identity in seen_identities:
            continue
        seen_identities.add(identity)
        protected.append(ProtectedRoot(label, protected_path, identity))

    identities = {item.path: item.identity for item in protected}
    return RepositoryLayout(
        root,
        git_dir,
        common_git_dir,
        identities[root],
        identities[git_dir],
        identities[common_git_dir],
        tuple(protected),
    )


def _repository_root(repo: Path | str) -> Path:
    return _repository_layout(repo).worktree


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
    source_layout = _repository_layout(repo)
    source = source_layout.worktree
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

    return ValidatedPayload(
        spec=spec,
        manifest_bytes=manifest_bytes,
        files=files,
        source_layout=source_layout,
    )


def _same_or_beneath(path: Path, root: Path) -> bool:
    return path == root or path.is_relative_to(root)


def _reject_protected_destination(path: Path, layout: RepositoryLayout) -> None:
    for protected in layout.protected_roots:
        if _same_or_beneath(path, protected.path):
            if protected.label == "source repository":
                raise IntakeError("destination must not be inside source repository")
            raise IntakeError(
                "destination must not be inside protected Git path: "
                f"{protected.label}"
            )


def _require_secure_materialization_support() -> None:
    missing: list[str] = []
    if not hasattr(os, "geteuid"):
        missing.append("geteuid")
    if not hasattr(os, "O_DIRECTORY"):
        missing.append("O_DIRECTORY")
    if not hasattr(os, "O_NOFOLLOW"):
        missing.append("O_NOFOLLOW")
    for function in (os.open, os.mkdir, os.stat):
        if function not in os.supports_dir_fd:
            missing.append(f"dir_fd:{function.__name__}")
    if os.stat not in os.supports_follow_symlinks:
        missing.append("follow_symlinks:stat")
    if missing:
        raise IntakeError(
            "secure fd-relative materialization is unsupported: " + ", ".join(missing)
        )


def _directory_flags() -> int:
    _require_secure_materialization_support()
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    return flags


def _open_stable_directory(path: Path) -> tuple[Path, int]:
    """Open a canonical directory and prove the retained fd names that inode."""

    canonical = path.resolve(strict=True)
    before = os.stat(canonical, follow_symlinks=False)
    if not stat.S_ISDIR(before.st_mode):
        raise IntakeError(f"unsafe destination parent: {canonical}")
    descriptor = os.open(canonical, _directory_flags())
    try:
        opened = os.fstat(descriptor)
        after = os.stat(canonical, follow_symlinks=False)
        expected = (before.st_dev, before.st_ino)
        if (opened.st_dev, opened.st_ino) != expected or (
            after.st_dev,
            after.st_ino,
        ) != expected:
            raise IntakeError("destination parent identity changed while opening")
        return canonical, descriptor
    except Exception:
        os.close(descriptor)
        raise


def _assert_fd_outside_protected(
    directory_fd: int, layout: RepositoryLayout
) -> None:
    protected = {
        root.identity: root.label
        for root in layout.protected_roots
    }
    current_fd = os.dup(directory_fd)
    seen: set[tuple[int, int]] = set()
    try:
        for _ in range(4096):
            current_stat = os.fstat(current_fd)
            identity = (current_stat.st_dev, current_stat.st_ino)
            if identity in protected:
                if protected[identity] == "source repository":
                    raise IntakeError(
                        "destination parent is inside source repository "
                        "(protected Git path)"
                    )
                raise IntakeError(
                    "destination parent is inside a protected Git path: "
                    f"{protected[identity]}"
                )
            if identity in seen:
                raise IntakeError("cycle while checking destination parent ancestry")
            seen.add(identity)
            parent_fd = os.open("..", _directory_flags(), dir_fd=current_fd)
            parent_stat = os.fstat(parent_fd)
            parent_identity = (parent_stat.st_dev, parent_stat.st_ino)
            if parent_identity == identity:
                os.close(parent_fd)
                return
            os.close(current_fd)
            current_fd = parent_fd
        raise IntakeError("destination parent ancestry exceeds safety limit")
    finally:
        os.close(current_fd)


def _assert_namespace_stable(directory_fd: int) -> None:
    """Reject namespaces another unprivileged UID can rename during intake."""

    trusted_owners = {0, os.geteuid()}
    current_fd = os.dup(directory_fd)
    seen: set[tuple[int, int]] = set()
    try:
        for _ in range(4096):
            current_stat = os.fstat(current_fd)
            identity = (current_stat.st_dev, current_stat.st_ino)
            if current_stat.st_uid not in trusted_owners:
                raise IntakeError(
                    "insecure destination namespace: untrusted directory owner"
                )
            writable_by_others = stat.S_IMODE(current_stat.st_mode) & 0o022
            sticky = current_stat.st_mode & stat.S_ISVTX
            if writable_by_others and not sticky:
                raise IntakeError(
                    "insecure destination namespace: writable non-sticky directory"
                )
            if identity in seen:
                raise IntakeError("cycle while checking destination namespace")
            seen.add(identity)
            parent_fd = os.open("..", _directory_flags(), dir_fd=current_fd)
            parent_stat = os.fstat(parent_fd)
            parent_identity = (parent_stat.st_dev, parent_stat.st_ino)
            if parent_identity == identity:
                os.close(parent_fd)
                return
            os.close(current_fd)
            current_fd = parent_fd
        raise IntakeError("destination namespace exceeds safety limit")
    finally:
        os.close(current_fd)


def _assert_public_parent_identity(path: Path, parent_fd: int) -> None:
    expected_stat = os.fstat(parent_fd)
    expected = (expected_stat.st_dev, expected_stat.st_ino)
    check_fd: int | None = None
    try:
        _, check_fd = _open_stable_directory(path)
        current_stat = os.fstat(check_fd)
        if (current_stat.st_dev, current_stat.st_ino) != expected:
            raise IntakeError("destination parent identity changed during materialization")
    except (FileNotFoundError, NotADirectoryError, OSError) as exc:
        raise IntakeError(
            "destination parent identity changed during materialization"
        ) from exc
    finally:
        if check_fd is not None:
            os.close(check_fd)


def _named_identity(parent_fd: int, name: str) -> tuple[int, int, int] | None:
    try:
        current = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        return None
    return current.st_dev, current.st_ino, current.st_mode


def _temporary_parent_candidate() -> Path:
    """Select the ambient temporary parent without probing or writing to it."""

    raw: object = tempfile.tempdir
    if raw is None:
        raw = next(
            (
                value
                for key in ("TMPDIR", "TEMP", "TMP")
                if (value := os.environ.get(key))
            ),
            "/tmp",
        )
    try:
        decoded = os.fsdecode(os.fspath(raw))
    except (TypeError, ValueError) as exc:
        raise IntakeError("invalid temporary destination parent") from exc
    if not decoded or "\x00" in decoded:
        raise IntakeError("invalid temporary destination parent")
    return Path(decoded).expanduser()


def _create_destination(
    destination: Path | str | None, layout: RepositoryLayout
) -> tuple[Path, int, int, str, tuple[int, int]]:
    if destination is None:
        # tempfile.gettempdir() probes candidates by creating and deleting a
        # file.  An attacker-controlled TMPDIR could therefore mutate a
        # protected repository before our ancestry checks.  Select the path
        # without probing; the retained directory fd is checked before mkdir.
        raw_parent = _temporary_parent_candidate()
        parent, parent_fd = _open_stable_directory(raw_parent)
        try:
            _assert_fd_outside_protected(parent_fd, layout)
            _assert_namespace_stable(parent_fd)
            for _ in range(128):
                name = f"bass-rf04-intake-{secrets.token_hex(8)}"
                root = parent / name
                _reject_protected_destination(root, layout)
                try:
                    os.mkdir(name, 0o700, dir_fd=parent_fd)
                except FileExistsError:
                    continue
                break
            else:
                raise IntakeError("could not allocate a unique temporary destination")
        except Exception:
            os.close(parent_fd)
            raise
    else:
        raw = Path(destination).expanduser()
        absolute = Path(os.path.abspath(raw))
        if absolute.name in {"", ".", ".."} or absolute == Path(absolute.anchor):
            raise IntakeError(f"unsafe destination: {raw}")
        parent, parent_fd = _open_stable_directory(absolute.parent)
        name = absolute.name
        root = parent / name
        try:
            _assert_fd_outside_protected(parent_fd, layout)
            _assert_namespace_stable(parent_fd)
            _reject_protected_destination(root, layout)
            if _named_identity(parent_fd, name) is not None:
                raise IntakeError(f"destination already exists: {root}")
            os.mkdir(name, 0o700, dir_fd=parent_fd)
        except FileExistsError as exc:
            os.close(parent_fd)
            raise IntakeError(f"destination already exists: {root}") from exc
        except Exception:
            os.close(parent_fd)
            raise

    root_fd: int | None = None
    identity: tuple[int, int] | None = None
    try:
        root_fd = os.open(name, _directory_flags(), dir_fd=parent_fd)
        opened = os.fstat(root_fd)
        identity = (opened.st_dev, opened.st_ino)
        os.fchmod(root_fd, 0o700)
        named = _named_identity(parent_fd, name)
        if (
            not stat.S_ISDIR(opened.st_mode)
            or named is None
            or named[:2] != identity
            or not stat.S_ISDIR(named[2])
        ):
            raise IntakeError("destination identity changed while creating")
        return root, parent_fd, root_fd, name, identity
    except Exception as exc:
        if root_fd is not None:
            os.close(root_fd)
        os.close(parent_fd)
        raise IntakeError(
            "materialization failed after destination creation; do not use any "
            f"partial output; requested path: {root}; cause: {exc}"
        ) from exc


def _open_or_create_child(parent_fd: int, name: str) -> int:
    try:
        os.mkdir(name, 0o700, dir_fd=parent_fd)
    except FileExistsError:
        pass
    child_fd = os.open(name, _directory_flags(), dir_fd=parent_fd)
    child_stat = os.fstat(child_fd)
    if not stat.S_ISDIR(child_stat.st_mode):
        os.close(child_fd)
        raise IntakeError(f"materialized path component is not a directory: {name}")
    os.fchmod(child_fd, 0o700)
    return child_fd


def _open_parent_for_path(root_fd: int, path: str) -> tuple[int, str]:
    parts = path.split("/")
    current_fd = os.dup(root_fd)
    try:
        for component in parts[:-1]:
            next_fd = _open_or_create_child(current_fd, component)
            os.close(current_fd)
            current_fd = next_fd
        return current_fd, parts[-1]
    except Exception:
        os.close(current_fd)
        raise


def _write_exclusive_at(
    root_fd: int, path: str, data: bytes, mode: int, expected_sha256: str
) -> None:
    parent_fd, name = _open_parent_for_path(root_fd, path)
    flags = os.O_RDWR | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    descriptor: int | None = None
    try:
        descriptor = os.open(name, flags, mode, dir_fd=parent_fd)
        view = memoryview(data)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise IntakeError(f"short write while materializing: {path}")
            view = view[written:]
        os.fchmod(descriptor, mode)
        os.fsync(descriptor)
        os.lseek(descriptor, 0, os.SEEK_SET)
        digest = hashlib.sha256()
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
        if digest.hexdigest() != expected_sha256:
            raise IntakeError(f"post-write payload verification failed: {path}")
    finally:
        if descriptor is not None:
            os.close(descriptor)
        os.close(parent_fd)


def _write_materialized_records(
    root_fd: int, validated: ValidatedPayload
) -> None:
    records = [
        (
            validated.spec.manifest_path,
            validated.manifest_bytes,
            0o644,
            validated.spec.manifest_sha256,
        )
    ]
    records.extend(
        (
            payload.path,
            payload.data,
            0o755 if payload.mode == "100755" else 0o644,
            payload.sha256,
        )
        for payload in validated.files.values()
    )
    paths = [record[0] for record in records]
    if len(paths) != len(set(paths)):
        raise IntakeError("materialization path collision")
    for path, data, mode, expected_digest in records:
        _write_exclusive_at(root_fd, path, data, mode, expected_digest)
    os.fsync(root_fd)


def _assert_destination_identity(
    parent_fd: int, name: str, identity: tuple[int, int]
) -> None:
    named = _named_identity(parent_fd, name)
    if named is None or named[:2] != identity or not stat.S_ISDIR(named[2]):
        raise IntakeError("destination identity changed during materialization")


def _bound_materialization_layout(
    validated: ValidatedPayload, source_repo: Path | str
) -> RepositoryLayout:
    expected = validated.source_layout
    current = _repository_layout(source_repo)
    expected_core = (
        expected.worktree_identity,
        expected.git_dir_identity,
        expected.common_git_dir_identity,
    )
    current_core = (
        current.worktree_identity,
        current.git_dir_identity,
        current.common_git_dir_identity,
    )
    if current_core != expected_core:
        raise IntakeError("validated source repository binding mismatch")

    protected: list[ProtectedRoot] = []
    seen: set[tuple[int, int]] = set()
    for item in (*expected.protected_roots, *current.protected_roots):
        if item.identity in seen:
            continue
        seen.add(item.identity)
        protected.append(item)
    return RepositoryLayout(
        current.worktree,
        current.git_dir,
        current.common_git_dir,
        current.worktree_identity,
        current.git_dir_identity,
        current.common_git_dir_identity,
        tuple(protected),
    )


def materialize(
    validated: ValidatedPayload,
    destination: Path | str | None,
    source_repo: Path | str,
) -> dict[str, object]:
    _require_secure_materialization_support()
    layout = _bound_materialization_layout(validated, source_repo)
    root, parent_fd, root_fd, name, identity = _create_destination(
        destination, layout
    )
    try:
        _write_materialized_records(root_fd, validated)
        # The public source path is not retained by fd.  Rebind it after all
        # writes so a repository path swap during materialization cannot
        # produce a PASS receipt naming a different clone.
        final_layout = _bound_materialization_layout(validated, source_repo)
        _assert_fd_outside_protected(parent_fd, final_layout)
        _assert_namespace_stable(parent_fd)
        _assert_public_parent_identity(root.parent, parent_fd)
        _assert_destination_identity(parent_fd, name, identity)
        os.fsync(parent_fd)
        result = receipt(validated, final_layout, root)
        return result
    except Exception as exc:
        raise IntakeError(
            "materialization failed after destination creation; do not use any "
            f"partial output; requested path: {root}; cause: {exc}"
        ) from exc
    finally:
        os.close(root_fd)
        os.close(parent_fd)


def receipt(
    validated: ValidatedPayload, source_layout: RepositoryLayout, output: Path | None
) -> dict[str, object]:
    return {
        "status": "PASS_IMMUTABLE_PAYLOAD_INTAKE_ONLY",
        "repository": validated.spec.repository,
        "source_repo": str(source_layout.worktree),
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
        if args.validate_only:
            layout = _bound_materialization_layout(validated, args.repo)
            result = receipt(validated, layout, None)
        else:
            result = materialize(validated, args.out, args.repo)
    except (IntakeError, OSError) as exc:
        print(f"STOP_INVALID: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
