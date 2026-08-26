#!/usr/bin/env python3
"""Build the bounded, content-addressed RF-02C native delta.

The wheel is copied byte-for-byte.  A separate normalized content identity
removes only known build-instance data from the wheel's CycloneDX SBOM; it is
never used as a substitute for the exact archive or installed-file identities.
"""
from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import sys
import tempfile
from typing import Any
import zipfile


_SCHEMA_VERSION = "v1"
_PATH_URI = re.compile(r"path\+file://[^#\r\n]*#")
_NATIVE_SUFFIXES = (".so", ".pyd", ".dylib")


class DeltaBuildError(RuntimeError):
    """A fail-closed native-delta construction error."""


def _canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _record_digest(value: bytes) -> str:
    return base64.urlsafe_b64encode(hashlib.sha256(value).digest()).decode("ascii").rstrip("=")


def _safe_member_name(name: str) -> bool:
    path = PurePosixPath(name)
    return bool(name) and not path.is_absolute() and ".." not in path.parts and "\\" not in name


def _read_and_verify_wheel(wheel: Path) -> tuple[dict[str, bytes], str, str, str]:
    try:
        with zipfile.ZipFile(wheel) as archive:
            infos = archive.infolist()
            names = [info.filename for info in infos]
            if len(names) != len(set(names)):
                raise DeltaBuildError("wheel contains duplicate member paths")
            if any(not _safe_member_name(name) for name in names):
                raise DeltaBuildError("wheel contains an unsafe member path")
            files = {
                info.filename: archive.read(info)
                for info in infos
                if not info.is_dir()
            }
    except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
        if isinstance(exc, DeltaBuildError):
            raise
        raise DeltaBuildError(f"wheel unreadable: {type(exc).__name__}") from exc

    record_names = sorted(name for name in files if name.endswith(".dist-info/RECORD"))
    if len(record_names) != 1:
        raise DeltaBuildError("wheel RECORD is missing or ambiguous")
    record_name = record_names[0]
    try:
        rows = list(csv.reader(io.StringIO(files[record_name].decode("utf-8"), newline="")))
    except (UnicodeDecodeError, csv.Error) as exc:
        raise DeltaBuildError(f"wheel RECORD is unreadable: {type(exc).__name__}") from exc

    records: dict[str, tuple[str, str]] = {}
    for row in rows:
        if len(row) != 3 or not row[0]:
            raise DeltaBuildError("wheel RECORD contains a malformed row")
        if row[0] in records:
            raise DeltaBuildError(f"wheel RECORD contains a duplicate row: {row[0]}")
        records[row[0]] = (row[1], row[2])

    if set(records) != set(files):
        missing = sorted(set(files) - set(records))
        extra = sorted(set(records) - set(files))
        detail = f"missing={missing!r} extra={extra!r}"
        raise DeltaBuildError(f"wheel RECORD member set mismatch: {detail}")
    if records[record_name] != ("", ""):
        raise DeltaBuildError("wheel RECORD self-row must have empty hash and size")
    for name, payload in sorted(files.items()):
        if name == record_name:
            continue
        expected = (f"sha256={_record_digest(payload)}", str(len(payload)))
        if records[name] != expected:
            raise DeltaBuildError(f"wheel RECORD mismatch for {name}")

    native_names = sorted(
        name for name in files if PurePosixPath(name).name.endswith(_NATIVE_SUFFIXES)
    )
    if len(native_names) != 1:
        raise DeltaBuildError("wheel shared object is missing or ambiguous")
    sbom_names = sorted(
        name
        for name in files
        if ".dist-info/sboms/" in name and name.lower().endswith(".json")
    )
    if len(sbom_names) != 1:
        raise DeltaBuildError("wheel CycloneDX SBOM is missing or ambiguous")
    return files, record_name, native_names[0], sbom_names[0]


def _normalize_build_path_strings(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _normalize_build_path_strings(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize_build_path_strings(item) for item in value]
    if isinstance(value, str):
        return _PATH_URI.sub("path+file://<BUILD_PATH>#", value)
    return value


def _normalized_sbom(payload: bytes) -> bytes:
    try:
        sbom = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DeltaBuildError(f"wheel SBOM is unreadable: {type(exc).__name__}") from exc
    if not isinstance(sbom, dict):
        raise DeltaBuildError("wheel SBOM root is not an object")
    sbom.pop("serialNumber", None)
    metadata = sbom.get("metadata")
    if isinstance(metadata, dict):
        metadata.pop("timestamp", None)
    return _canonical_json_bytes(_normalize_build_path_strings(sbom))


def _member_description(
    name: str,
    payload: bytes,
    *,
    record_name: str,
    sbom_name: str,
) -> dict[str, Any]:
    normalized = _normalized_sbom(payload) if name == sbom_name else payload
    included = name != record_name
    description: dict[str, Any] = {
        "included_in_normalized_content": included,
        "path": name,
        "sha256": _sha256_bytes(payload),
        "size": len(payload),
    }
    if included:
        description.update(
            {
                "normalization": "cyclonedx-rf02c-v1" if name == sbom_name else "identity",
                "normalized_sha256": _sha256_bytes(normalized),
                "normalized_size": len(normalized),
            }
        )
    return description


def _content_manifest(
    files: dict[str, bytes],
    *,
    record_name: str,
    native_name: str,
    sbom_name: str,
) -> dict[str, Any]:
    members = [
        _member_description(
            name,
            files[name],
            record_name=record_name,
            sbom_name=sbom_name,
        )
        for name in sorted(files)
    ]
    identity_members = [
        {
            "normalized_sha256": item["normalized_sha256"],
            "normalized_size": item["normalized_size"],
            "path": item["path"],
        }
        for item in members
        if item["included_in_normalized_content"]
    ]
    identity_payload = {
        "members": identity_members,
        "schema": f"bass-rf02c-native-normalized-content/{_SCHEMA_VERSION}",
    }
    return {
        "archive_member_count": len(members),
        "members": members,
        "normalization": {
            "record": "excluded from normalized content identity",
            "sbom": {
                "canonical_json": True,
                "normalized_build_path_uri": "path+file://<BUILD_PATH>#",
                "removed_fields": ["metadata.timestamp", "serialNumber"],
            },
        },
        "normalized_content_identity": {
            "algorithm": "sha256",
            "sha256": _sha256_bytes(_canonical_json_bytes(identity_payload)),
        },
        "record_path": record_name,
        "sbom_path": sbom_name,
        "schema": f"bass-rf02c-native-content-manifest/{_SCHEMA_VERSION}",
        "shared_object_path": native_name,
    }


def _exact_member(files: dict[str, bytes], name: str) -> dict[str, Any]:
    payload = files[name]
    return {"path": name, "sha256": _sha256_bytes(payload), "size": len(payload)}


def build_delta(
    *,
    wheel: Path,
    cargo_lock: Path,
    source_head: str,
    source_tree: str,
    output_root: Path,
) -> dict[str, Any]:
    wheel = wheel.resolve()
    cargo_lock = cargo_lock.resolve()
    output_root = output_root.resolve()
    if not wheel.is_file() or wheel.suffix != ".whl":
        raise DeltaBuildError("--wheel must name an existing .whl file")
    if not cargo_lock.is_file():
        raise DeltaBuildError("--cargo-lock must name an existing file")
    for label, value in (("source head", source_head), ("source tree", source_tree)):
        if not re.fullmatch(r"[0-9a-f]{40}", value):
            raise DeltaBuildError(f"{label} must be a lowercase 40-hex Git identity")
    if output_root.exists():
        raise DeltaBuildError("output root already exists; refusing to overwrite it")

    files, record_name, native_name, sbom_name = _read_and_verify_wheel(wheel)
    wheel_sha256 = _sha256_file(wheel)
    wheel_size = wheel.stat().st_size
    cargo_lock_bytes = cargo_lock.read_bytes()
    content_manifest = _content_manifest(
        files,
        record_name=record_name,
        native_name=native_name,
        sbom_name=sbom_name,
    )
    content_bytes = _canonical_json_bytes(content_manifest)
    wheel_relative = f"rf02c-wheel/{wheel.name}"
    cargo_lock_relative = "source/Cargo.lock"
    content_relative = "NATIVE_CONTENT_MANIFEST.json"
    restore_relative = "RF02C_NATIVE_RESTORE.json"

    restore = {
        "cargo_lock": {
            "relative_path": cargo_lock_relative,
            "sha256": _sha256_bytes(cargo_lock_bytes),
            "size": len(cargo_lock_bytes),
        },
        "native_content_manifest": {
            "normalized_content_sha256": content_manifest["normalized_content_identity"]["sha256"],
            "relative_path": content_relative,
            "sha256": _sha256_bytes(content_bytes),
            "size": len(content_bytes),
        },
        "no_index_restore": {
            "commands": [
                [
                    "env",
                    "-u",
                    "BASS_ALLOW_UNVERIFIED_NATIVE_DEV",
                    "python",
                    "-m",
                    "pip",
                    "install",
                    "--no-index",
                    "--no-deps",
                    "--no-cache-dir",
                    "--force-reinstall",
                    wheel_relative,
                ],
                [
                    "env",
                    "-u",
                    "BASS_ALLOW_UNVERIFIED_NATIVE_DEV",
                    "python",
                    "-c",
                    "import bianchi_rustcore; print(bianchi_rustcore.__file__)",
                ],
            ],
            "network": "forbidden",
            "working_directory": "delta_root",
        },
        "record": _exact_member(files, record_name),
        "sbom": _exact_member(files, sbom_name),
        "schema": f"bass-rf02c-native-restore/{_SCHEMA_VERSION}",
        "shared_object": _exact_member(files, native_name),
        "source": {"head": source_head, "tree": source_tree},
        "wheel": {
            "filename": wheel.name,
            "relative_path": wheel_relative,
            "sha256": wheel_sha256,
            "size": wheel_size,
        },
    }
    restore_bytes = _canonical_json_bytes(restore)

    payload_bytes = {
        cargo_lock_relative: cargo_lock_bytes,
        content_relative: content_bytes,
        restore_relative: restore_bytes,
    }
    delta_manifest = {
        "cargo_lock_sha256": _sha256_bytes(cargo_lock_bytes),
        "normalized_content_sha256": content_manifest["normalized_content_identity"]["sha256"],
        "payloads": {
            **{name: _sha256_bytes(payload) for name, payload in sorted(payload_bytes.items())},
            wheel_relative: wheel_sha256,
        },
        "schema": f"bass-rf02c-native-delta/{_SCHEMA_VERSION}",
        "source": {"head": source_head, "tree": source_tree},
        "wheel_sha256": wheel_sha256,
    }
    delta_bytes = _canonical_json_bytes(delta_manifest)

    output_root.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f".{output_root.name}.", dir=output_root.parent) as temporary:
        staging = Path(temporary) / output_root.name
        (staging / "rf02c-wheel").mkdir(parents=True)
        (staging / "source").mkdir()
        shutil.copyfile(wheel, staging / wheel_relative)
        for relative, payload in payload_bytes.items():
            target = staging / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
        (staging / "DELTA_MANIFEST.json").write_bytes(delta_bytes)
        staging.rename(output_root)
    return delta_manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel", required=True, type=Path)
    parser.add_argument("--cargo-lock", required=True, type=Path)
    parser.add_argument("--source-head", required=True)
    parser.add_argument("--source-tree", required=True)
    parser.add_argument("--output-root", required=True, type=Path)
    args = parser.parse_args()
    try:
        manifest = build_delta(
            wheel=args.wheel,
            cargo_lock=args.cargo_lock,
            source_head=args.source_head,
            source_tree=args.source_tree,
            output_root=args.output_root,
        )
    except DeltaBuildError as exc:
        print(f"RF02C_NATIVE_DELTA_ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(manifest, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
