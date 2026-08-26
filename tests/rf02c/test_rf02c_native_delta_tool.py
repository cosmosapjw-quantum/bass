"""Focused tests for the bounded RF-02C native-delta builder."""
from __future__ import annotations

import base64
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import zipfile

import pytest


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "tools/native/build_rf02c_native_delta.py"
VERIFIER = ROOT / "tools/native/verify_content_addressed_delta.py"
HEAD = "1" * 40
TREE = "2" * 40


def _record_digest(payload: bytes) -> str:
    return base64.urlsafe_b64encode(hashlib.sha256(payload).digest()).decode().rstrip("=")


def _sbom(*, serial: str, timestamp: str, build_root: str) -> bytes:
    value = {
        "bomFormat": "CycloneDX",
        "components": [{"name": "num-traits", "version": "0.2.19"}],
        "dependencies": [{"dependsOn": [], "ref": f"path+file://{build_root}#native@0.1.0"}],
        "metadata": {
            "component": {
                "bom-ref": f"path+file://{build_root}#native@0.1.0",
                "name": "native",
            },
            "timestamp": timestamp,
        },
        "serialNumber": serial,
        "specVersion": "1.6",
        "version": 1,
    }
    return json.dumps(value, sort_keys=True).encode()


def _write_wheel(
    path: Path,
    *,
    serial: str = "urn:uuid:one",
    timestamp: str = "2026-08-26T00:00:00Z",
    build_root: str = "/tmp/build-one",
    corrupt_record_for: str | None = None,
    record_mode: str = "valid",
) -> None:
    dist = "bianchi_rustcore-0.1.0.dist-info"
    files = {
        "bianchi_rustcore/__init__.py": b"from .bianchi_rustcore import *\n",
        "bianchi_rustcore/bianchi_rustcore.so": b"native-rf02c-payload",
        f"{dist}/METADATA": b"Name: bianchi-rustcore\nVersion: 0.1.0\n",
        f"{dist}/WHEEL": b"Wheel-Version: 1.0\nRoot-Is-Purelib: false\n",
        f"{dist}/sboms/bianchi_rustcore.cyclonedx.json": _sbom(
            serial=serial,
            timestamp=timestamp,
            build_root=build_root,
        ),
    }
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    for name, payload in sorted(files.items()):
        digest_payload = b"wrong" if name == corrupt_record_for else payload
        writer.writerow((name, f"sha256={_record_digest(digest_payload)}", len(payload)))
    record_name = f"{dist}/RECORD"
    writer.writerow((record_name, "", ""))
    record = output.getvalue().encode()
    if record_mode == "missing":
        record = b""
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, payload in sorted(files.items()):
            archive.writestr(name, payload)
        if record_mode != "missing":
            archive.writestr(record_name, record)
            if record_mode == "ambiguous":
                archive.writestr("other-0.1.0.dist-info/RECORD", b"other-0.1.0.dist-info/RECORD,,\n")


def _run_builder(wheel: Path, cargo_lock: Path, output: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(BUILDER),
            "--wheel",
            str(wheel),
            "--cargo-lock",
            str(cargo_lock),
            "--source-head",
            HEAD,
            "--source-tree",
            TREE,
            "--output-root",
            str(output),
        ],
        text=True,
        capture_output=True,
        check=False,
    )


def test_builder_is_deterministic_and_generated_delta_verifies(tmp_path: Path) -> None:
    wheel = tmp_path / "bianchi_rustcore-0.1.0-cp312-test.whl"
    lock = tmp_path / "Cargo.lock"
    lock.write_text("version = 4\n", encoding="utf-8")
    _write_wheel(wheel)

    first = tmp_path / "first"
    second = tmp_path / "second"
    first_result = _run_builder(wheel, lock, first)
    second_result = _run_builder(wheel, lock, second)

    assert first_result.returncode == 0, first_result.stderr
    assert second_result.returncode == 0, second_result.stderr
    for name in (
        "DELTA_MANIFEST.json",
        "NATIVE_CONTENT_MANIFEST.json",
        "RF02C_NATIVE_RESTORE.json",
    ):
        assert (first / name).read_bytes() == (second / name).read_bytes()
    assert (first / "rf02c-wheel" / wheel.name).read_bytes() == wheel.read_bytes()
    restore = json.loads((first / "RF02C_NATIVE_RESTORE.json").read_text())
    assert restore["source"] == {"head": HEAD, "tree": TREE}
    assert restore["no_index_restore"]["network"] == "forbidden"
    assert "BASS_ALLOW_UNVERIFIED_NATIVE_DEV" in restore["no_index_restore"]["commands"][0]

    verified = subprocess.run(
        [sys.executable, str(VERIFIER), "--delta-root", str(first)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert verified.returncode == 0, verified.stderr


def test_normalized_identity_ignores_only_frozen_sbom_build_variability(tmp_path: Path) -> None:
    lock = tmp_path / "Cargo.lock"
    lock.write_text("version = 4\n", encoding="utf-8")
    wheel_a = tmp_path / "a" / "bianchi_rustcore-0.1.0-cp312-test.whl"
    wheel_b = tmp_path / "b" / wheel_a.name
    wheel_a.parent.mkdir()
    wheel_b.parent.mkdir()
    _write_wheel(wheel_a)
    _write_wheel(
        wheel_b,
        serial="urn:uuid:two",
        timestamp="2026-08-26T01:02:03Z",
        build_root="/home/runner/work/a-different-root",
    )

    out_a = tmp_path / "delta-a"
    out_b = tmp_path / "delta-b"
    assert _run_builder(wheel_a, lock, out_a).returncode == 0
    assert _run_builder(wheel_b, lock, out_b).returncode == 0
    manifest_a = json.loads((out_a / "NATIVE_CONTENT_MANIFEST.json").read_text())
    manifest_b = json.loads((out_b / "NATIVE_CONTENT_MANIFEST.json").read_text())

    assert hashlib.sha256(wheel_a.read_bytes()).hexdigest() != hashlib.sha256(wheel_b.read_bytes()).hexdigest()
    assert manifest_a["normalized_content_identity"] == manifest_b["normalized_content_identity"]
    assert [item["path"] for item in manifest_a["members"]] == sorted(
        item["path"] for item in manifest_a["members"]
    )
    record = next(item for item in manifest_a["members"] if item["path"].endswith("/RECORD"))
    assert record["included_in_normalized_content"] is False


def test_builder_rejects_member_tamper_against_record(tmp_path: Path) -> None:
    wheel = tmp_path / "bianchi_rustcore-0.1.0-cp312-test.whl"
    lock = tmp_path / "Cargo.lock"
    lock.write_text("version = 4\n", encoding="utf-8")
    _write_wheel(wheel, corrupt_record_for="bianchi_rustcore/bianchi_rustcore.so")

    result = _run_builder(wheel, lock, tmp_path / "delta")

    assert result.returncode == 2
    assert "RECORD mismatch" in result.stderr
    assert not (tmp_path / "delta").exists()


@pytest.mark.parametrize("record_mode", ("missing", "ambiguous"))
def test_builder_rejects_missing_or_ambiguous_record(tmp_path: Path, record_mode: str) -> None:
    wheel = tmp_path / "bianchi_rustcore-0.1.0-cp312-test.whl"
    lock = tmp_path / "Cargo.lock"
    lock.write_text("version = 4\n", encoding="utf-8")
    _write_wheel(wheel, record_mode=record_mode)

    result = _run_builder(wheel, lock, tmp_path / "delta")

    assert result.returncode == 2
    assert "RECORD" in result.stderr
    assert not (tmp_path / "delta").exists()
