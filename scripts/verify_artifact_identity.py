#!/usr/bin/env python3
"""Fail-closed artifact identity classification using only the Python stdlib."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any


REQUEST_SCHEMA = "bass-artifact-identity-request-v1"
RESULT_SCHEMA = "bass-artifact-identity-result-v1"
IDENTITY_CLASSES = {"A", "B", "C", "D"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SIDECAR_RE = re.compile(r"^([0-9A-Fa-f]{64})[ \t]+\*?(.+?)\s*$")

EXIT_PASS = 0
EXIT_BLOCKED = 2
EXIT_P0 = 3


class RequestError(ValueError):
    """The request cannot support a deterministic identity decision."""


def _identity(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise RequestError(f"{label} must be an object")
    filename = value.get("filename")
    size_bytes = value.get("size_bytes")
    sha256 = value.get("sha256")
    if not isinstance(filename, str) or not filename or Path(filename).name != filename:
        raise RequestError(f"{label}.filename must be one basename")
    if type(size_bytes) is not int or size_bytes < 0:
        raise RequestError(f"{label}.size_bytes must be a nonnegative integer")
    if not isinstance(sha256, str) or not SHA256_RE.fullmatch(sha256.lower()):
        raise RequestError(f"{label}.sha256 must be 64 hexadecimal characters")
    return {
        "filename": filename,
        "size_bytes": size_bytes,
        "sha256": sha256.lower(),
    }


def _result(
    code: str,
    identity_class: str,
    *,
    blocking: bool,
    severity: str,
    exit_status: int,
    finding_class: str | None = None,
    actual: dict[str, object] | None = None,
    expected: dict[str, object] | None = None,
    details: dict[str, object] | None = None,
) -> tuple[dict[str, object], int]:
    result: dict[str, object] = {
        "blocking": blocking,
        "code": code,
        "finding_class": finding_class or identity_class,
        "identity_class": identity_class,
        "schema": RESULT_SCHEMA,
        "scientific_integrity_failure": False,
        "severity": severity,
    }
    if actual is not None:
        result["actual"] = actual
    if expected is not None:
        result["expected"] = expected
    if details:
        result["details"] = details
    return result, exit_status


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _portable_relative_path(value: str) -> bool:
    if not value or "\\" in value:
        return False
    posix_path = PurePosixPath(value)
    windows_path = PureWindowsPath(value)
    return (
        not posix_path.is_absolute()
        and not windows_path.is_absolute()
        and not windows_path.drive
        and ".." not in posix_path.parts
        and "." not in posix_path.parts
    )


def _check_sidecar(path: Path, identity_class: str) -> tuple[dict[str, object], int] | None:
    if not path.is_file():
        return _result(
            "BLOCKED_INPUT_REQUIRED",
            identity_class,
            blocking=True,
            severity="BLOCKED",
            exit_status=EXIT_BLOCKED,
            finding_class="D",
            details={"missing_sidecar": str(path)},
        )
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as error:
        return _result(
            "INVALID_SIDECAR",
            identity_class,
            blocking=True,
            severity="BLOCKED",
            exit_status=EXIT_BLOCKED,
            finding_class="D",
            details={"error": str(error)},
        )
    entries = 0
    for line_number, line in enumerate(lines, start=1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = SIDECAR_RE.fullmatch(line)
        if match is None:
            return _result(
                "INVALID_SIDECAR",
                identity_class,
                blocking=True,
                severity="BLOCKED",
                exit_status=EXIT_BLOCKED,
                finding_class="D",
                details={"line": line_number},
            )
        entries += 1
        referenced_path = match.group(2)
        if not _portable_relative_path(referenced_path):
            return _result(
                "NON_PORTABLE_SIDECAR",
                identity_class,
                blocking=True,
                severity="P1",
                exit_status=EXIT_BLOCKED,
                finding_class="D",
                details={"line": line_number, "path": referenced_path},
            )
    if entries == 0:
        return _result(
            "INVALID_SIDECAR",
            identity_class,
            blocking=True,
            severity="BLOCKED",
            exit_status=EXIT_BLOCKED,
            finding_class="D",
            details={"reason": "no digest entries"},
        )
    return None


def _manifested_tree_identity(
    root: Path,
    manifest_value: object,
    filename: str,
) -> tuple[dict[str, object] | None, tuple[dict[str, object], int] | None]:
    if not isinstance(manifest_value, dict) or not isinstance(manifest_value.get("paths"), list):
        raise RequestError("class B directory input requires manifest.paths")
    paths = manifest_value["paths"]
    if any(not isinstance(path, str) or not _portable_relative_path(path) for path in paths):
        raise RequestError("manifest paths must be portable relative strings")
    if len(paths) != len(set(paths)):
        raise RequestError("manifest paths must be unique")

    actual_paths: list[str] = []
    for candidate in root.rglob("*"):
        if candidate.is_symlink():
            return None, _result(
                "NON_PORTABLE_MANIFEST",
                "B",
                blocking=True,
                severity="P1",
                exit_status=EXIT_BLOCKED,
                details={"symlink": candidate.relative_to(root).as_posix()},
            )
        if candidate.is_file():
            actual_paths.append(candidate.relative_to(root).as_posix())
    actual_paths.sort()

    cache_paths = [
        path
        for path in actual_paths
        if "__pycache__" in PurePosixPath(path).parts or path.endswith((".pyc", ".pyo"))
    ]
    if cache_paths:
        return None, _result(
            "CACHE_CONTAMINATION",
            "B",
            blocking=True,
            severity="P0",
            exit_status=EXIT_P0,
            details={"paths": cache_paths},
        )

    manifest_paths = sorted(paths)
    missing = sorted(set(manifest_paths) - set(actual_paths))
    unmanifested = sorted(set(actual_paths) - set(manifest_paths))
    if missing:
        return None, _result(
            "BLOCKED_INPUT_REQUIRED",
            "B",
            blocking=True,
            severity="BLOCKED",
            exit_status=EXIT_BLOCKED,
            details={"missing_manifest_paths": missing},
        )
    if unmanifested:
        return None, _result(
            "UNMANIFESTED_DETERMINISTIC_EVIDENCE",
            "B",
            blocking=True,
            severity="P0",
            exit_status=EXIT_BLOCKED,
            details={"paths": unmanifested},
        )

    tree_digest = hashlib.sha256()
    total_size = 0
    for relative_path in manifest_paths:
        member = root / relative_path
        member_size = member.stat().st_size
        total_size += member_size
        record = f"{_sha256(member)} {member_size} {relative_path}\n"
        tree_digest.update(record.encode("utf-8"))
    return (
        {
            "filename": filename,
            "size_bytes": total_size,
            "sha256": tree_digest.hexdigest(),
        },
        None,
    )


def _receipt_is_bound(
    receipt: object,
    actual: dict[str, object],
    expected: dict[str, object],
) -> bool:
    if not isinstance(receipt, dict):
        return False
    try:
        subject = _identity(receipt.get("subject"), "receipt.subject")
        source = _identity(receipt.get("source"), "receipt.source")
    except RequestError:
        return False
    return subject == actual and source == expected


def verify_request(request: object) -> tuple[dict[str, object], int]:
    if not isinstance(request, dict):
        raise RequestError("request must be an object")
    if request.get("schema") != REQUEST_SCHEMA:
        raise RequestError(f"schema must equal {REQUEST_SCHEMA}")
    identity_class = request.get("identity_class")
    if identity_class not in IDENTITY_CLASSES:
        raise RequestError("identity_class must be one of A, B, C, or D")
    relation = request.get("relation")
    if not isinstance(relation, str) or not relation:
        raise RequestError("relation must be a nonempty string")

    artifact = request.get("artifact")
    if not isinstance(artifact, dict):
        raise RequestError("artifact must be an object")
    raw_path = artifact.get("path")
    filename = artifact.get("filename")
    if not isinstance(raw_path, str) or not raw_path:
        raise RequestError("artifact.path must be a nonempty string")
    if not isinstance(filename, str) or not filename or Path(filename).name != filename:
        raise RequestError("artifact.filename must be one basename")
    artifact_path = Path(raw_path)
    if not artifact_path.exists():
        return _result(
            "BLOCKED_INPUT_REQUIRED",
            identity_class,
            blocking=True,
            severity="BLOCKED",
            exit_status=EXIT_BLOCKED,
            details={"missing_artifact": str(artifact_path)},
        )

    expected = _identity(request.get("expected"), "expected")
    if artifact_path.is_dir():
        if identity_class != "B":
            raise RequestError("directory artifacts require identity class B")
        actual, tree_failure = _manifested_tree_identity(
            artifact_path,
            request.get("manifest"),
            filename,
        )
        if tree_failure is not None:
            return tree_failure
        assert actual is not None
    elif artifact_path.is_file():
        actual = {
            "filename": filename,
            "size_bytes": artifact_path.stat().st_size,
            "sha256": _sha256(artifact_path),
        }
    else:
        return _result(
            "BLOCKED_INPUT_REQUIRED",
            identity_class,
            blocking=True,
            severity="BLOCKED",
            exit_status=EXIT_BLOCKED,
            details={"unsupported_artifact": str(artifact_path)},
        )

    sidecar = request.get("sidecar")
    if sidecar is not None:
        if not isinstance(sidecar, dict) or not isinstance(sidecar.get("path"), str):
            raise RequestError("sidecar.path must be a string")
        sidecar_failure = _check_sidecar(Path(sidecar["path"]), identity_class)
        if sidecar_failure is not None:
            return sidecar_failure

    byte_identity_matches = actual == expected
    same_name = actual["filename"] == expected["filename"]
    if identity_class in {"A", "B"} and not byte_identity_matches:
        if same_name:
            return _result(
                "ARTIFACT_IDENTITY_COLLISION",
                identity_class,
                blocking=True,
                severity="P0",
                exit_status=EXIT_P0,
                actual=actual,
                expected=expected,
                details={"failure_domain": "BYTE_IDENTITY"},
            )
        mismatch_code = "BYTE_IDENTITY_MISMATCH" if identity_class == "A" else "DETERMINISTIC_EVIDENCE_MISMATCH"
        return _result(
            mismatch_code,
            identity_class,
            blocking=True,
            severity="P0",
            exit_status=EXIT_P0,
            actual=actual,
            expected=expected,
            details={"failure_domain": "BYTE_IDENTITY"},
        )

    if not _receipt_is_bound(request.get("receipt"), actual, expected):
        return _result(
            "UNBOUND_HISTORICAL_EVIDENCE",
            identity_class,
            blocking=True,
            severity="P0",
            exit_status=EXIT_P0,
            actual=actual,
            expected=expected,
        )

    if identity_class == "A":
        if relation != "EXACT_BYTES":
            raise RequestError("class A requires relation EXACT_BYTES")
        return _result(
            "PASS_EXACT_IDENTITY",
            "A",
            blocking=False,
            severity="PASS",
            exit_status=EXIT_PASS,
            actual=actual,
            expected=expected,
        )
    if identity_class == "B":
        if relation != "DETERMINISTIC_EVIDENCE":
            raise RequestError("class B requires relation DETERMINISTIC_EVIDENCE")
        return _result(
            "PASS_DETERMINISTIC_EVIDENCE",
            "B",
            blocking=False,
            severity="PASS",
            exit_status=EXIT_PASS,
            actual=actual,
            expected=expected,
        )
    if identity_class == "C":
        if relation != "SCIENTIFIC_CONTENT_EQUIVALENCE":
            raise RequestError("class C requires relation SCIENTIFIC_CONTENT_EQUIVALENCE")
        criteria = request.get("content_criteria")
        if (
            not isinstance(criteria, dict)
            or not criteria
            or any(not isinstance(name, str) or not name for name in criteria)
            or any(status != "PASS" for status in criteria.values())
        ):
            return _result(
                "BLOCKED_CONTENT_CRITERIA_REQUIRED",
                "C",
                blocking=True,
                severity="BLOCKED",
                exit_status=EXIT_BLOCKED,
                actual=actual,
                expected=expected,
            )
        return _result(
            "PASS_CONTENT_EQUIVALENCE",
            "C",
            blocking=False,
            severity="PASS",
            exit_status=EXIT_PASS,
            actual=actual,
            expected=expected,
            details={"content_criteria": dict(sorted(criteria.items()))},
        )

    if relation != "PACKAGING_METADATA":
        raise RequestError("class D requires relation PACKAGING_METADATA")
    if byte_identity_matches:
        code = "PASS_PACKAGING_IDENTITY"
        severity = "PASS"
    elif request.get("byte_identity_authoritative") is True:
        return _result(
            "PACKAGING_BYTE_IDENTITY_REQUIRED",
            "D",
            blocking=True,
            severity="P1",
            exit_status=EXIT_BLOCKED,
            actual=actual,
            expected=expected,
        )
    else:
        code = "PACKAGING_METADATA_MISMATCH"
        severity = "NONBLOCKING_FINDING"
    return _result(
        code,
        "D",
        blocking=False,
        severity=severity,
        exit_status=EXIT_PASS,
        actual=actual,
        expected=expected,
    )


def _self_test() -> None:
    with tempfile.TemporaryDirectory() as temporary_directory:
        root = Path(temporary_directory)
        artifact = root / "artifact.bin"
        artifact.write_bytes(b"self-test")
        actual = {
            "filename": "artifact.bin",
            "size_bytes": 9,
            "sha256": _sha256(artifact),
        }
        exact, exact_status = verify_request(
            {
                "schema": REQUEST_SCHEMA,
                "identity_class": "A",
                "relation": "EXACT_BYTES",
                "artifact": {"path": str(artifact), "filename": "artifact.bin"},
                "expected": actual,
                "receipt": {"subject": actual, "source": actual},
            }
        )
        assert exact_status == EXIT_PASS and exact["code"] == "PASS_EXACT_IDENTITY"

        packaging_expected = dict(actual)
        packaging_expected["sha256"] = "0" * 64
        packaging, packaging_status = verify_request(
            {
                "schema": REQUEST_SCHEMA,
                "identity_class": "D",
                "relation": "PACKAGING_METADATA",
                "artifact": {"path": str(artifact), "filename": "artifact.bin"},
                "expected": packaging_expected,
                "receipt": {"subject": actual, "source": packaging_expected},
            }
        )
        assert packaging_status == EXIT_PASS
        assert packaging["code"] == "PACKAGING_METADATA_MISMATCH"
        assert packaging["scientific_integrity_failure"] is False


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--request", type=Path)
    mode.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    if arguments.self_test:
        _self_test()
        print("PASS_AC01_SELF_TEST")
        return EXIT_PASS
    try:
        request = json.loads(arguments.request.read_text(encoding="utf-8"))
        result, exit_status = verify_request(request)
    except (OSError, UnicodeError, json.JSONDecodeError, RequestError) as error:
        result, exit_status = _result(
            "INVALID_REQUEST",
            "UNCLASSIFIED",
            blocking=True,
            severity="BLOCKED",
            exit_status=EXIT_BLOCKED,
            details={"error": str(error)},
        )
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return exit_status


if __name__ == "__main__":
    sys.exit(main())
