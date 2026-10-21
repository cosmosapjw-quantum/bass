#!/usr/bin/env python3
"""Create-only S12 bundles and exact-byte verification of downloaded copies.

This utility has no provider credentials or network/write endpoints. It preserves
failed and interrupted attempts and never calls a scientific executable.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import stat
import shutil
import sys
import zipfile

import resources
from runner import atomic_json, digest_file, load_manifest, relative, under, utc


def verify(archive, expected_sha256, expected_bytes):
    archive = Path(archive)
    if archive.stat().st_size != expected_bytes or digest_file(archive) != expected_sha256:
        raise ValueError("whole archive byte identity mismatch")
    with zipfile.ZipFile(archive) as z:
        names = z.namelist()
        if len(names) != len(set(names)) or "MANIFEST.json" not in names:
            raise ValueError("duplicate ZIP names or missing manifest")
        if z.getinfo("MANIFEST.json").file_size > 16 << 20:
            raise ValueError("manifest exceeds bounded metadata size")
        manifest = json.loads(z.read("MANIFEST.json"))
        if manifest.get("schema") != "BASS_S12_RETURN_BUNDLE_V1":
            raise ValueError("unexpected bundle schema")
        rows = manifest["files"]
        if len({row["path"] for row in rows}) != len(rows) or set(names) != {row["path"] for row in rows} | {"MANIFEST.json"}:
            raise ValueError("manifest/ZIP path set mismatch")
        if sum(row["bytes"] for row in rows) > resources.DISK_CAP_BYTES:
            raise ValueError("declared payload exceeds disk cap")
        for row in rows:
            relative(row["path"])
            info = z.getinfo(row["path"])
            if info.is_dir() or stat.S_ISLNK(info.external_attr >> 16) or info.file_size != row["bytes"]:
                raise ValueError("unsafe member type or member size mismatch")
            h, size = hashlib.sha256(), 0
            with z.open(info) as stream:
                for block in iter(lambda: stream.read(1 << 20), b""):
                    size += len(block); h.update(block)
            # Reading every member through EOF also verifies its ZIP CRC.
            if size != row["bytes"] or h.hexdigest() != row["sha256"]:
                raise ValueError("payload SHA256 mismatch: " + row["path"])
    return {"schema": "BASS_S12_BUNDLE_READBACK_V1", "verified_at_utc": utc(),
            "archive": str(archive), "bytes": expected_bytes, "sha256": expected_sha256,
            "payload_count": len(rows), "payload_bytes": sum(row["bytes"] for row in rows),
            "CRC_all_entries": True, "manifest_all_payloads": True,
            "status": "PASS_EXACT_ARCHIVE_BYTES_CRC_MANIFEST",
            "scientific_status": "Not inferred from packaging; consult each immutable job receipt."}


def create(manifest_path, repo, runs, output, disk_root):
    manifest, manifest_sha = load_manifest(manifest_path, repo)
    sources = dict(manifest["source_files"])
    for job in manifest["jobs"]:
        for name, sha in job["input_files"].items():
            if name in sources and sources[name] != sha:
                raise ValueError("conflicting source/input byte identities")
            sources[name] = sha
    selected = {"job_manifest.json": Path(manifest_path)}
    for name in sorted(sources):
        selected["source/" + name] = under(repo, name)
    if runs.exists():
        for p in sorted(runs.rglob("*")):
            if p.is_symlink():
                raise ValueError("symlink in run tree")
            if p.is_file() and p.name != ".launcher.lock" and ".tmp-" not in p.name:
                if p.resolve() == output.resolve():
                    raise ValueError("output archive cannot be an existing run payload")
                selected["runs/" + p.relative_to(runs).as_posix()] = p
    rows = [{"path": name, "bytes": p.stat().st_size, "sha256": digest_file(p),
             "executable": bool(p.stat().st_mode & stat.S_IXUSR)} for name, p in selected.items()]
    payload_bytes = sum(row["bytes"] for row in rows)
    # Conservative uncompressed upper budget; never depend on compression to fit.
    estimate = payload_bytes + (len(rows) + 1) * 1024 + 16384
    if resources.allocated_bytes(disk_root) + estimate > resources.DISK_CAP_BYTES or shutil.disk_usage(disk_root).free < estimate:
        raise RuntimeError("new bundle would exceed the4GiB allocated disk budget")
    incomplete = [name for name in selected if name.endswith("/STARTED.json")
                  and name[:-len("STARTED.json")] + "receipt.json" not in selected]
    metadata = {"schema": "BASS_S12_RETURN_BUNDLE_V1", "job_manifest_sha256": manifest_sha,
                "payload_count": len(rows), "payload_bytes": payload_bytes, "files": rows,
                "incomplete_attempt_started_records": incomplete,
                "scientific_status": "Per-job receipt only; packaging includes failures and interruptions.",
                "source_snapshot": "Exact declared source/input bytes; no automatic rebuild or scientific replay."}
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for row in rows:
            info = zipfile.ZipInfo(row["path"], date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o100755 if row["executable"] else 0o100644) << 16
            h, count = hashlib.sha256(), 0
            with selected[row["path"]].open("rb") as source, z.open(info, "w", force_zip64=True) as target:
                for block in iter(lambda: source.read(1 << 20), b""):
                    target.write(block); h.update(block); count += len(block)
            if count != row["bytes"] or h.hexdigest() != row["sha256"]:
                raise RuntimeError("payload changed during snapshot; archive is incomplete")
        info = zipfile.ZipInfo("MANIFEST.json", date_time=(1980, 1, 1, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        z.writestr(info, json.dumps(metadata, ensure_ascii=False, indent=2).encode() + b"\n")
    result = verify(output, digest_file(output), output.stat().st_size)
    result["job_manifest_sha256"] = manifest_sha
    result["incomplete_attempt_count"] = len(incomplete)
    atomic_json(output.with_name(output.name + ".receipt.json"), result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    pack = sub.add_parser("create")
    for name in ("manifest", "repo", "runs", "output", "disk-root"):
        pack.add_argument("--" + name, type=Path, required=True)
    check = sub.add_parser("verify")
    check.add_argument("--archive", type=Path, required=True)
    check.add_argument("--sha256", required=True)
    check.add_argument("--bytes", type=int, required=True)
    args = parser.parse_args()
    if args.action == "verify":
        result = verify(args.archive, args.sha256, args.bytes)
    else:
        repo, runs, disk_root, output = (getattr(args, key).resolve() for key in ("repo", "runs", "disk_root", "output"))
        if not all(p.is_relative_to(disk_root) for p in (repo, runs, output)):
            raise ValueError("source, runs and new archive must lie under the measured disk root")
        result = create(args.manifest.resolve(), repo, runs, output, disk_root)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, zipfile.BadZipFile) as error:
        print(json.dumps({"status": "FAIL", "error": str(error)}), file=sys.stderr)
        sys.exit(2)
