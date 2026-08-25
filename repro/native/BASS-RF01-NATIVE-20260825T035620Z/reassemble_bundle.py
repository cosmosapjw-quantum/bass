#!/usr/bin/env python3
"""Reassemble an RF-01 R4 archive from its explicit ordered part manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--parts-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists() or not args.output.parent.is_dir():
        raise SystemExit("ERROR: output must be absent and its parent must exist")
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    if manifest.get("schema") != "bass-rf01-native-bundle-manifest-v1":
        raise SystemExit("ERROR: unsupported R4 manifest schema")
    parts = manifest.get("parts")
    archive = manifest.get("archive")
    limits = manifest.get("limits")
    if not isinstance(parts, list) or not parts or not isinstance(archive, dict) or not isinstance(limits, dict):
        raise SystemExit("ERROR: malformed R4 bundle manifest")
    if len(parts) > limits["max_parts"] or [item.get("order") for item in parts] != list(range(len(parts))):
        raise SystemExit("ERROR: invalid ordered part contract")
    expected_names = {item.get("filename") for item in parts}
    actual_names = {path.name for path in args.parts_dir.iterdir() if path.is_file()}
    if expected_names != actual_names:
        raise SystemExit("ERROR: parts directory differs from manifest")
    temporary = args.output.with_name(args.output.name + f".tmp.{os.getpid()}")
    digest = hashlib.sha256()
    total = 0
    try:
        with temporary.open("xb") as output:
            for item in parts:
                filename = item.get("filename")
                if not isinstance(filename, str) or Path(filename).name != filename:
                    raise SystemExit("ERROR: unsafe part filename")
                path = args.parts_dir / filename
                size = path.stat().st_size
                if size != item.get("size_bytes") or size > limits["max_part_bytes"] or sha256(path) != item.get("sha256"):
                    raise SystemExit(f"ERROR: part size/hash mismatch: {filename}")
                with path.open("rb") as source:
                    for block in iter(lambda: source.read(1024 * 1024), b""):
                        output.write(block)
                        digest.update(block)
                        total += len(block)
        if total != archive.get("size_bytes") or total > limits["max_artifact_bytes"] or digest.hexdigest() != archive.get("sha256"):
            raise SystemExit("ERROR: reconstructed archive differs from manifest")
        os.replace(temporary, args.output)
    finally:
        if temporary.exists():
            temporary.unlink()
    print(json.dumps({"status": "PASS", "output": str(args.output), "size_bytes": total, "sha256": digest.hexdigest(), "part_count": len(parts)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
