#!/usr/bin/env python3
"""Fail-closed verifier for a content-addressed native delta package."""
from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import json
from pathlib import Path
import sys
import zipfile


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _record_digest(value: bytes) -> str:
    return base64.urlsafe_b64encode(hashlib.sha256(value).digest()).decode().rstrip("=")


def _fail(message: str) -> int:
    print(message, file=sys.stderr)
    return 2


def _verify_wheel_record(wheel: Path, shared_object: dict[str, str]) -> str | None:
    try:
        with zipfile.ZipFile(wheel) as archive:
            names = set(archive.namelist())
            record_names = [name for name in names if name.endswith(".dist-info/RECORD")]
            if len(record_names) != 1:
                return "RECORD missing or ambiguous"
            rows = list(csv.reader(archive.read(record_names[0]).decode("utf-8").splitlines()))
            records = {row[0]: row[1:] for row in rows if len(row) == 3}
            for name in names - {record_names[0]}:
                row = records.get(name)
                payload = archive.read(name)
                expected = [f"sha256={_record_digest(payload)}", str(len(payload))]
                if row != expected:
                    return f"RECORD mismatch for {name}"
            shared_path = shared_object.get("path")
            if not isinstance(shared_path, str) or shared_path not in names:
                return "shared object missing from wheel"
            expected_shared_sha = shared_object.get("sha256")
            if _sha256_bytes(archive.read(shared_path)) != expected_shared_sha:
                return "shared object SHA-256 mismatch"
    except (OSError, UnicodeDecodeError, zipfile.BadZipFile, csv.Error) as exc:
        return f"wheel or RECORD unreadable: {type(exc).__name__}"
    return None


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--delta-root", type=Path, required=True)
    parser.add_argument("--restore", type=Path)
    parser.add_argument("--wheel", type=Path)
    parser.add_argument("--format", choices=("json",), default="json")
    args = parser.parse_args()
    root = args.delta_root.resolve()
    manifest_path = root / "DELTA_MANIFEST.json"
    if args.restore is not None:
        restore_path = args.restore.resolve()
    else:
        restore_candidates = (
            root / "RF02C_NATIVE_RESTORE.json",
            root / "RF02B_R4_DELTA_RESTORE.json",
        )
        restore_path = next((path for path in restore_candidates if path.is_file()), restore_candidates[-1])
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        restore = json.loads(restore_path.read_text(encoding="utf-8"))
        payloads = manifest["payloads"]
    except (KeyError, OSError, json.JSONDecodeError) as exc:
        return _fail(f"delta manifest or restore receipt unreadable: {type(exc).__name__}")
    if not isinstance(payloads, dict):
        return _fail("delta payload manifest is not an object")
    for relative, expected in sorted(payloads.items()):
        path = root / relative
        if not path.is_file():
            return _fail(f"delta payload missing: {relative}")
        if _sha256(path) != expected:
            return _fail(f"delta payload SHA-256 mismatch: {relative}")
    wheel_info = restore.get("wheel", {})
    wheel_relative = wheel_info.get("relative_path")
    if not isinstance(wheel_relative, str):
        filename = str(wheel_info.get("filename", ""))
        matching_payloads = [relative for relative in payloads if Path(relative).name == filename]
        wheel_relative = matching_payloads[0] if len(matching_payloads) == 1 else f"rf02b-wheel/{filename}"
    wheel = args.wheel or root / wheel_relative
    if not wheel.is_file():
        return _fail("wheel missing")
    if _sha256(wheel) != wheel_info.get("sha256"):
        return _fail("wheel SHA-256 mismatch")
    record_error = _verify_wheel_record(wheel, restore.get("shared_object", {}))
    if record_error is not None:
        return _fail(record_error)
    print(
        json.dumps(
            {
                "schema": "bass-content-addressed-native-delta-verification/v1",
                "status": "PASS",
                "delta_root": str(root),
                "restore_receipt": restore_path.name,
                "wheel_sha256": wheel_info["sha256"],
                "shared_object_sha256": restore["shared_object"]["sha256"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
