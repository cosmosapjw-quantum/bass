#!/usr/bin/env python3
"""Audit ZIP/TAR metadata without extracting or executing archive contents."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import tarfile
import zipfile


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def path_issues(name: str) -> list[str]:
    issues: list[str] = []
    if not name:
        return ["empty_name"]
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in name):
        issues.append("control_character")
    if "\\" in name:
        issues.append("backslash_path")
    if name.startswith("/") or PurePosixPath(name).is_absolute():
        issues.append("absolute_path")
    parts = PurePosixPath(name).parts
    if ".." in parts:
        issues.append("parent_traversal")
    if parts and len(parts[0]) >= 2 and parts[0][1] == ":":
        issues.append("drive_path")
    return issues


def _base_report(path: Path) -> dict:
    return {
        "schema_version": 1,
        "archive": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "entries": 0,
        "expanded_bytes": 0,
        "issues": [],
    }


def inspect_zip(path: Path, max_entries: int, max_bytes: int, max_ratio: float) -> dict:
    report = _base_report(path)
    seen: set[str] = set()
    with zipfile.ZipFile(path) as archive:
        for info in archive.infolist():
            report["entries"] += 1
            report["expanded_bytes"] += info.file_size
            for issue in path_issues(info.filename):
                report["issues"].append({"entry": info.filename, "issue": issue})
            if info.filename in seen:
                report["issues"].append({"entry": info.filename, "issue": "duplicate_name"})
            seen.add(info.filename)
            mode = (info.external_attr >> 16) & 0xFFFF
            file_type = stat.S_IFMT(mode) if mode else 0
            if file_type == stat.S_IFLNK:
                report["issues"].append({"entry": info.filename, "issue": "symlink"})
            elif file_type not in (0, stat.S_IFREG, stat.S_IFDIR):
                report["issues"].append({"entry": info.filename, "issue": "special_file"})
            if info.compress_size == 0:
                ratio = float("inf") if info.file_size else 1.0
            else:
                ratio = info.file_size / info.compress_size
            if info.file_size >= 1024 * 1024 and ratio > max_ratio:
                report["issues"].append({"entry": info.filename, "issue": "expansion_ratio", "ratio": ratio})
    if report["entries"] > max_entries:
        report["issues"].append({"entry": None, "issue": "entry_limit"})
    if report["expanded_bytes"] > max_bytes:
        report["issues"].append({"entry": None, "issue": "expanded_size_limit"})
    return report


def inspect_tar(path: Path, max_entries: int, max_bytes: int, _max_ratio: float) -> dict:
    report = _base_report(path)
    seen: set[str] = set()
    with tarfile.open(path, mode="r:*") as archive:
        for info in archive:
            report["entries"] += 1
            if info.isfile():
                report["expanded_bytes"] += info.size
            for issue in path_issues(info.name):
                report["issues"].append({"entry": info.name, "issue": issue})
            if info.name in seen:
                report["issues"].append({"entry": info.name, "issue": "duplicate_name"})
            seen.add(info.name)
            if info.issym() or info.islnk():
                report["issues"].append({"entry": info.name, "issue": "link"})
            elif not (info.isfile() or info.isdir()):
                report["issues"].append({"entry": info.name, "issue": "special_file"})
            if info.mode & (stat.S_ISUID | stat.S_ISGID | stat.S_ISVTX):
                report["issues"].append({"entry": info.name, "issue": "special_mode"})
    if report["entries"] > max_entries:
        report["issues"].append({"entry": None, "issue": "entry_limit"})
    if report["expanded_bytes"] > max_bytes:
        report["issues"].append({"entry": None, "issue": "expanded_size_limit"})
    return report


def inspect_archive(path: Path, max_entries: int = 100_000,
                    max_bytes: int = 4 * 1024**3, max_ratio: float = 200.0) -> dict:
    if not path.is_file():
        raise FileNotFoundError(path)
    if zipfile.is_zipfile(path):
        report = inspect_zip(path, max_entries, max_bytes, max_ratio)
        report["format"] = "zip"
    elif tarfile.is_tarfile(path):
        report = inspect_tar(path, max_entries, max_bytes, max_ratio)
        report["format"] = "tar"
    else:
        raise ValueError(f"unsupported archive format: {path}")
    report["status"] = "PASS" if not report["issues"] else "REJECT"
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--max-entries", type=int, default=100_000)
    parser.add_argument("--max-expanded-bytes", type=int, default=4 * 1024**3)
    parser.add_argument("--max-entry-ratio", type=float, default=200.0)
    args = parser.parse_args()
    report = inspect_archive(args.archive, args.max_entries,
                             args.max_expanded_bytes, args.max_entry_ratio)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
