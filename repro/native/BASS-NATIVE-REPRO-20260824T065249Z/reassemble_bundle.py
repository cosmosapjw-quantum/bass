#!/usr/bin/env python3
"""Reassemble a BASS archive from the manifest's explicit ordered part list."""

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

    if args.output.exists():
        raise SystemExit(f"ERROR: refusing to overwrite output: {args.output}")
    if not args.output.parent.is_dir():
        raise SystemExit(f"ERROR: output parent does not exist: {args.output.parent}")

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    if manifest.get("schema") != "bass-native-bundle-manifest-v1":
        raise SystemExit("ERROR: unsupported manifest schema")
    parts = manifest.get("parts")
    archive = manifest.get("archive")
    if not isinstance(parts, list) or not parts or not isinstance(archive, dict):
        raise SystemExit("ERROR: malformed parts/archive manifest")
    if len(parts) > int(manifest["limits"]["max_parts"]):
        raise SystemExit("ERROR: manifest exceeds part-count cap")

    expected_orders = list(range(len(parts)))
    actual_orders = [part.get("order") for part in parts]
    if actual_orders != expected_orders:
        raise SystemExit("ERROR: ordered part list is not contiguous from zero")

    temp = args.output.with_name(args.output.name + f".tmp.{os.getpid()}")
    digest = hashlib.sha256()
    total = 0
    try:
        with temp.open("xb") as output:
            for part in parts:
                filename = part.get("filename")
                if not isinstance(filename, str) or Path(filename).name != filename:
                    raise SystemExit("ERROR: unsafe part filename")
                path = args.parts_dir / filename
                if not path.is_file():
                    raise SystemExit(f"ERROR: missing part: {filename}")
                size = path.stat().st_size
                if size != part.get("size_bytes"):
                    raise SystemExit(f"ERROR: size mismatch: {filename}")
                if size > int(manifest["limits"]["max_part_bytes"]):
                    raise SystemExit(f"ERROR: oversized part: {filename}")
                if sha256(path) != part.get("sha256"):
                    raise SystemExit(f"ERROR: SHA-256 mismatch: {filename}")
                with path.open("rb") as source:
                    for block in iter(lambda: source.read(1024 * 1024), b""):
                        output.write(block)
                        digest.update(block)
                        total += len(block)
        if total != archive.get("size_bytes"):
            raise SystemExit("ERROR: reconstructed archive size mismatch")
        if digest.hexdigest() != archive.get("sha256"):
            raise SystemExit("ERROR: reconstructed archive SHA-256 mismatch")
        if total > int(manifest["limits"]["max_artifact_bytes"]):
            raise SystemExit("ERROR: reconstructed archive exceeds artifact cap")
        os.replace(temp, args.output)
    finally:
        if temp.exists():
            temp.unlink()

    print(
        json.dumps(
            {
                "status": "PASS",
                "output": str(args.output),
                "size_bytes": total,
                "sha256": digest.hexdigest(),
                "part_count": len(parts),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
