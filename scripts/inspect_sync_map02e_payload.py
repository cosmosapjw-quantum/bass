#!/usr/bin/env python3
"""Inspect the concurrent .sync_payload without applying or deleting it."""
from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD_DIR = ROOT / ".sync_payload"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--extract-to", type=Path)
    args = parser.parse_args()

    parts = sorted(PAYLOAD_DIR.glob("part*"))
    if not parts:
        print(json.dumps({"status": "NO_PAYLOAD"}, sort_keys=True))
        return 0
    if [part.name for part in parts] != [f"part{i:02d}" for i in range(len(parts))]:
        raise SystemExit("FAIL: payload part sequence is not contiguous")

    encoded = b"".join(part.read_bytes().strip() for part in parts)
    try:
        compressed = base64.b64decode(encoded, validate=True)
        decoded = gzip.decompress(compressed)
    except Exception as exc:
        raise SystemExit(f"FAIL: staged payload is not canonical base64+gzip: {exc}") from exc

    kind = "raw"
    members: list[str] = []
    if zipfile.is_zipfile(io.BytesIO(decoded)):
        kind = "zip"
        with zipfile.ZipFile(io.BytesIO(decoded)) as archive:
            members = archive.namelist()
            if args.extract_to is not None:
                args.extract_to.mkdir(parents=True, exist_ok=True)
                archive.extractall(args.extract_to)
    else:
        try:
            with tarfile.open(fileobj=io.BytesIO(decoded), mode="r:*") as archive:
                kind = "tar"
                members = archive.getnames()
                if args.extract_to is not None:
                    args.extract_to.mkdir(parents=True, exist_ok=True)
                    archive.extractall(args.extract_to)
        except tarfile.TarError:
            try:
                value = json.loads(decoded.decode("utf-8"))
                kind = "json"
                members = sorted(value) if isinstance(value, dict) else []
                if args.extract_to is not None:
                    args.extract_to.mkdir(parents=True, exist_ok=True)
                    (args.extract_to / "payload.json").write_bytes(decoded)
            except (UnicodeDecodeError, json.JSONDecodeError):
                if args.extract_to is not None:
                    args.extract_to.mkdir(parents=True, exist_ok=True)
                    (args.extract_to / "payload.bin").write_bytes(decoded)

    report = {
        "status": "PASS_INSPECTED_NOT_APPLIED",
        "part_count": len(parts),
        "part_names": [part.name for part in parts],
        "encoded_size": len(encoded),
        "compressed_size": len(compressed),
        "decoded_size": len(decoded),
        "decoded_sha256": hashlib.sha256(decoded).hexdigest(),
        "kind": kind,
        "member_count": len(members),
        "members": members,
        "claim_effect": "NONE",
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
