"""Pinned private Rust bootstrap for the new S12 NCP manifest.

Only the official, hash-pinned archive is downloadable. No installer script,
global package state, rustup settings or caller PATH is modified.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import shutil
import sys
import tarfile
import time
import urllib.request
import uuid

import resources
from runner import THREAD_ENV, atomic_json, digest_file, utc

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from process_control import run_owned

VERSION = "1.94.1"
TARGET = "x86_64-unknown-linux-gnu"
ARCHIVE_NAME = "rust-1.94.1-x86_64-unknown-linux-gnu.tar.xz"
ARCHIVE_ROOT = ARCHIVE_NAME[:-len(".tar.xz")]
ARCHIVE_URL = "https://static.rust-lang.org/dist/" + ARCHIVE_NAME
ARCHIVE_BYTES = 192287020
ARCHIVE_SHA256 = "294b3d81fa72e62581276290c60c81eb8b58498d333d422ca1dfc432877d0c40"
EXTRACTED_BYTES_CAP = 1 << 30


def remaining(deadline):
    value = deadline - time.monotonic()
    if value <= 0:
        raise TimeoutError("TOOLCHAIN_DEADLINE")
    return value


def disk_admit(root, additional):
    allocated = resources.allocated_bytes(root)
    free = shutil.disk_usage(root).free
    if allocated + additional > resources.DISK_CAP_BYTES or free < additional:
        raise RuntimeError("TOOLCHAIN_DISK_BUDGET_UNAVAILABLE")
    return {"allocated_bytes": allocated, "free_bytes": free,
            "additional_reserved_bytes": additional, "cap_bytes": resources.DISK_CAP_BYTES}


def safe_relative(value):
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or any(part in ("", ".", "..") for part in path.parts):
        raise ValueError("UNSAFE_TOOLCHAIN_ARCHIVE_PATH")
    return path


def selected_path(member):
    path = safe_relative(member.name)
    parts = path.parts
    if parts[0] != ARCHIVE_ROOT:
        raise ValueError("UNEXPECTED_TOOLCHAIN_ARCHIVE_ROOT")
    if len(parts) < 3:
        return None
    component, relative = parts[1], PurePosixPath(*parts[2:])
    selected = ((component == "rustc" and (relative == PurePosixPath("bin/rustc") or relative.parts[0] == "lib"))
                or (component == "rust-std-" + TARGET and relative.parts[0] == "lib")
                or (component == "cargo" and relative == PurePosixPath("bin/cargo")))
    if not selected or member.isdir():
        return None
    if not member.isfile() or member.issym() or member.islnk():
        raise ValueError("SELECTED_TOOLCHAIN_MEMBER_MUST_BE_REGULAR")
    return relative


def verify_archive(path, deadline):
    path = Path(path)
    if path.stat().st_size != ARCHIVE_BYTES:
        raise ValueError("PINNED_TOOLCHAIN_ARCHIVE_SIZE")
    h = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            remaining(deadline); h.update(block)
    if h.hexdigest() != ARCHIVE_SHA256:
        raise ValueError("PINNED_TOOLCHAIN_ARCHIVE_SHA256")


def download_archive(destination, disk_root, deadline):
    disk_admit(disk_root, ARCHIVE_BYTES + EXTRACTED_BYTES_CAP + (16 << 20))
    partial = destination.with_suffix(destination.suffix + ".partial")
    count, h = 0, hashlib.sha256()
    request = urllib.request.Request(ARCHIVE_URL, headers={"User-Agent": "BASS-S12-private-pinned-toolchain"})
    with urllib.request.urlopen(request, timeout=min(30.0, remaining(deadline))) as response, partial.open("xb") as target:
        if response.status != 200:
            raise RuntimeError("TOOLCHAIN_HTTP_STATUS")
        while True:
            remaining(deadline)
            block = response.read(1 << 20)
            if not block:
                break
            count += len(block)
            if count > ARCHIVE_BYTES:
                raise ValueError("TOOLCHAIN_DOWNLOAD_EXCEEDS_PINNED_SIZE")
            target.write(block); h.update(block)
        target.flush(); os.fsync(target.fileno())
    if count != ARCHIVE_BYTES or h.hexdigest() != ARCHIVE_SHA256:
        raise ValueError("TOOLCHAIN_DOWNLOAD_IDENTITY")
    os.link(partial, destination)
    partial.unlink()
    return {"url": ARCHIVE_URL, "bytes": count, "sha256": h.hexdigest(), "method": "one full read-only GET"}


def extract_minimal(archive, destination, disk_root, deadline):
    selected, seen, size = [], set(), 0
    with tarfile.open(archive, "r|xz") as stream:
        for member in stream:
            remaining(deadline)
            relative = selected_path(member)
            if relative is None:
                continue
            if str(relative) in seen or member.size < 0:
                raise ValueError("DUPLICATE_OR_NEGATIVE_TOOLCHAIN_MEMBER")
            seen.add(str(relative)); size += member.size
            if size > EXTRACTED_BYTES_CAP:
                raise ValueError("MINIMAL_TOOLCHAIN_EXTRACTION_BUDGET")
            selected.append({"archive_path": member.name, "path": str(relative), "bytes": member.size,
                             "mode": member.mode & 0o755})
    if not {"bin/rustc", "bin/cargo"} <= seen or not any(p.startswith("lib/rustlib/" + TARGET + "/lib/") for p in seen):
        raise ValueError("MINIMAL_TOOLCHAIN_COMPONENTS_MISSING")
    disk_admit(disk_root, size + (8 << 20))
    destination.mkdir(parents=True, exist_ok=False)
    by_name = {row["archive_path"]: row for row in selected}
    with tarfile.open(archive, "r|xz") as stream:
        for member in stream:
            remaining(deadline)
            if member.name not in by_name:
                continue
            row = by_name[member.name]
            relative = selected_path(member)
            if relative is None or str(relative) != row["path"] or member.size != row["bytes"]:
                raise ValueError("TOOLCHAIN_ARCHIVE_CHANGED")
            target = destination.joinpath(*relative.parts)
            if not target.resolve().is_relative_to(destination.resolve()):
                raise ValueError("TOOLCHAIN_DESTINATION_ESCAPE")
            target.parent.mkdir(parents=True, exist_ok=True)
            h, count = hashlib.sha256(), 0
            source = stream.extractfile(member)
            if source is None:
                raise ValueError("TOOLCHAIN_MEMBER_BYTES_UNAVAILABLE")
            with source, target.open("xb") as output:
                for block in iter(lambda: source.read(1 << 20), b""):
                    remaining(deadline); count += len(block); h.update(block); output.write(block)
            if count != row["bytes"]:
                raise ValueError("TRUNCATED_TOOLCHAIN_MEMBER")
            os.chmod(target, row["mode"])
            row["sha256"] = h.hexdigest()
    if any("sha256" not in row for row in selected):
        raise ValueError("INCOMPLETE_TOOLCHAIN_EXTRACTION")
    return selected


def probe(rustc, cargo, directory, deadline):
    result = {}
    for name, path, argv in (("rustc", rustc, [rustc, "-vV"]), ("cargo", cargo, [cargo, "--version"])):
        path = Path(path).resolve()
        if not path.is_file() or path.name.startswith("rustup"):
            raise ValueError("RUSTUP_SHIM_OR_COMPILER_UNAVAILABLE")
        argv[0] = str(path)
        receipt = run_owned(argv, stdout_path=directory/(name+".stdout"), stderr_path=directory/(name+".stderr"),
                            receipt_path=directory/(name+".json"), timeout_s=min(20.0, remaining(deadline)),
                            env={**os.environ, **THREAD_ENV}, as_bytes=2 << 30, file_bytes=1 << 20)
        text = (directory/(name+".stdout")).read_text()
        if receipt["status"] == "INTERRUPTED":
            raise SystemExit(receipt["exit_code"])
        if receipt["status"] != "EXITED" or receipt["exit_code"] != 0:
            raise RuntimeError("TOOLCHAIN_VERSION_PROBE_FAILED:" + name)
        if name == "rustc" and (not text.startswith("rustc " + VERSION + " ") or "host: " + TARGET not in text):
            raise ValueError("PINNED_RUSTC_VERSION_OR_HOST")
        if name == "cargo" and not text.startswith("cargo " + VERSION + " "):
            raise ValueError("PINNED_CARGO_VERSION")
        result[name] = {"path": str(path), "sha256": digest_file(path), "version_output": text,
                        "probe_receipt": str(directory/(name+".json")), "probe_process": receipt}
    return result


def _cached(cache_root, deadline):
    for directory in sorted(cache_root.glob("rust-" + VERSION + "-*")):
        receipt = directory/"READY.json"
        try:
            record = json.loads(receipt.read_bytes())
            if record["status"] != "PASS_PRIVATE_PINNED_TOOLCHAIN" or record["archive"]["sha256"] != ARCHIVE_SHA256:
                continue
            prefix = directory/"prefix"
            if directory.is_symlink() or prefix.is_symlink() or not prefix.resolve().is_relative_to(cache_root.resolve()):
                raise ValueError("CACHED_TOOLCHAIN_PREFIX_ESCAPE")
            declared = set()
            for row in record["members"]:
                remaining(deadline)
                path = prefix.joinpath(*safe_relative(row["path"]).parts)
                if row["path"] in declared or not path.resolve().is_relative_to(prefix.resolve()) or path.is_symlink() or not path.is_file() or path.stat().st_size != row["bytes"] or digest_file(path) != row["sha256"]:
                    raise ValueError("CACHED_TOOLCHAIN_MEMBER_CHANGED")
                declared.add(row["path"])
            actual = {p.relative_to(prefix).as_posix() for p in prefix.rglob("*") if p.is_file() or p.is_symlink()}
            if actual != declared or not {"bin/rustc", "bin/cargo"} <= declared:
                raise ValueError("CACHED_TOOLCHAIN_FILE_SET_CHANGED")
            for name in ("rustc", "cargo"):
                expected = (prefix/"bin"/name).resolve()
                if Path(record["executables"][name]["path"]).resolve() != expected or digest_file(expected) != record["executables"][name]["sha256"]:
                    raise ValueError("CACHED_TOOLCHAIN_EXECUTABLE_CHANGED")
            return record, receipt
        except TimeoutError:
            raise
        except (OSError, ValueError, KeyError, TypeError):
            continue
    return None


def ensure_toolchain(cache_root, record_root, disk_root, deadline, *, archive_path=None,
                     existing_rustc=None, existing_cargo=None):
    if sys.platform != "linux" or platform.machine() not in ("x86_64", "AMD64"):
        raise RuntimeError("PINNED_TOOLCHAIN_SUPPORTS_LINUX_X86_64_ONLY")
    cache_root, record_root, disk_root = map(lambda p: Path(p).resolve(), (cache_root, record_root, disk_root))
    if not cache_root.is_relative_to(disk_root) or not record_root.is_relative_to(disk_root):
        raise ValueError("TOOLCHAIN_PATH_OUTSIDE_MEASURED_DISK_ROOT")
    cache_root.mkdir(parents=True, exist_ok=True); record_root.mkdir(parents=True, exist_ok=True)
    disk_admit(disk_root, 1 << 20)
    cached = _cached(cache_root, deadline)
    if cached is not None:
        record, receipt = cached
        result = {"status": "PASS_REUSED_EXACT_PRIVATE_TOOLCHAIN", "executables": record["executables"],
                  "ready_receipt": str(receipt), "ready_receipt_sha256": digest_file(receipt),
                  "members_verified": len(record["members"]), "archive_sha256": ARCHIVE_SHA256}
        atomic_json(record_root/"TOOLCHAIN.json", result)
        return result
    rustc = existing_rustc or shutil.which("rustc")
    cargo = existing_cargo or shutil.which("cargo")
    external_failure = None
    if rustc and cargo:
        try:
            executable = probe(rustc, cargo, record_root/"external_probe", deadline)
            result = {"status": "PASS_EXISTING_VERSION_HASH_IDENTIFIED", "executables": executable,
                      "archive_identity_claim": False, "existing_toolchain_modified": False}
            atomic_json(record_root/"TOOLCHAIN.json", result)
            return result
        except TimeoutError:
            raise
        except (OSError, ValueError, RuntimeError) as error:
            external_failure = {"type": type(error).__name__, "message": str(error)}
    directory = cache_root/("rust-" + VERSION + "-" + ARCHIVE_SHA256[:12] + "-" + uuid.uuid4().hex[:8])
    directory.mkdir(exist_ok=False)
    record = {"schema": "BASS_S12_PRIVATE_TOOLCHAIN_V1", "status": "STARTED", "started_utc": utc(),
              "official_archive_url": ARCHIVE_URL, "external_probe_failure": external_failure,
              "global_install_or_settings_changed": False, "scientific_execution": False}
    atomic_json(directory/"STARTED.json", record)
    try:
        if archive_path is None:
            archive = directory/ARCHIVE_NAME
            record["download"] = download_archive(archive, disk_root, deadline)
        else:
            archive = Path(archive_path).resolve()
        verify_archive(archive, deadline)
        record["archive"] = {"path": str(archive), "bytes": ARCHIVE_BYTES, "sha256": ARCHIVE_SHA256}
        record["members"] = extract_minimal(archive, directory/"prefix", disk_root, deadline)
        record["executables"] = probe(directory/"prefix/bin/rustc", directory/"prefix/bin/cargo", directory/"probe", deadline)
        record.update(status="PASS_PRIVATE_PINNED_TOOLCHAIN", finished_utc=utc(),
                      extracted_bytes=sum(row["bytes"] for row in record["members"]))
        atomic_json(directory/"READY.json", record)
        result = {"status": record["status"], "executables": record["executables"], "ready_receipt": str(directory/"READY.json"),
                  "ready_receipt_sha256": digest_file(directory/"READY.json"), "members_verified": len(record["members"]),
                  "archive_sha256": ARCHIVE_SHA256}
        atomic_json(record_root/"TOOLCHAIN.json", result)
        return result
    except Exception as error:
        record.update(status="FAILED", finished_utc=utc(), error={"type": type(error).__name__, "message": str(error)})
        atomic_json(directory/"FAILED.json", record)
        raise
