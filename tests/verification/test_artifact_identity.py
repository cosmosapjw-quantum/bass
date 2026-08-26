from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
IDENTITY_VERIFIER = REPOSITORY_ROOT / "scripts" / "verify_artifact_identity.py"
DIFF_VERIFIER = REPOSITORY_ROOT / "scripts" / "verify_allowed_diff.py"

SEALED_SHA256 = "c9d0036bed6744bcdf692fc980d8717d7e5f5a4f4e8266b4a84982602fb1cd09"
FRESH_CONTAINER_SHA256 = "57b7b9b5db6eb5db6f0aaaafe0893d60a133742eb42d492a4dabf3080ce437f1"
CONTENT_CAPSULE_SHA256 = "5b4ef18950b8b6a0e6c358519ee91e7c4091833026ce5271e9221c4af69da7cd"


class ArtifactIdentityTests(unittest.TestCase):
    maxDiff = None

    def _run_identity(self, request: dict[str, object]) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
        with tempfile.TemporaryDirectory() as temporary_directory:
            request_path = Path(temporary_directory) / "request.json"
            request_path.write_text(json.dumps(request), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(IDENTITY_VERIFIER), "--request", str(request_path)],
                cwd=REPOSITORY_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertTrue(
            completed.stdout.strip(),
            f"identity verifier emitted no JSON receipt; stderr={completed.stderr!r}",
        )
        try:
            result = json.loads(completed.stdout)
        except json.JSONDecodeError as error:
            self.fail(f"identity verifier output is not JSON: {error}; output={completed.stdout!r}")
        return completed, result

    @staticmethod
    def _identity(filename: str, size_bytes: int, sha256: str) -> dict[str, object]:
        return {
            "filename": filename,
            "size_bytes": size_bytes,
            "sha256": sha256,
        }

    def test_same_name_different_digest_is_p0(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            artifact = Path(temporary_directory) / "sealed.bin"
            artifact.write_bytes(b"sealed")
            expected = self._identity("sealed.bin", 6, "0" * 64)
            completed, result = self._run_identity(
                {
                    "schema": "bass-artifact-identity-request-v1",
                    "identity_class": "A",
                    "relation": "EXACT_BYTES",
                    "artifact": {"path": str(artifact), "filename": "sealed.bin"},
                    "expected": expected,
                    "receipt": {"subject": expected, "source": expected},
                }
            )

        self.assertEqual(completed.returncode, 3)
        self.assertEqual(result["code"], "ARTIFACT_IDENTITY_COLLISION")
        self.assertEqual(result["identity_class"], "A")
        self.assertEqual(result["severity"], "P0")
        self.assertTrue(result["blocking"])
        self.assertFalse(result["scientific_integrity_failure"])

    def test_missing_artifact_is_blocked_input(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            missing = Path(temporary_directory) / "missing.bin"
            expected = self._identity("missing.bin", 6, SEALED_SHA256)
            completed, result = self._run_identity(
                {
                    "schema": "bass-artifact-identity-request-v1",
                    "identity_class": "A",
                    "relation": "EXACT_BYTES",
                    "artifact": {"path": str(missing), "filename": "missing.bin"},
                    "expected": expected,
                    "receipt": {"subject": expected, "source": expected},
                }
            )

        self.assertEqual(completed.returncode, 2)
        self.assertEqual(result["code"], "BLOCKED_INPUT_REQUIRED")
        self.assertEqual(result["identity_class"], "A")
        self.assertTrue(result["blocking"])
        self.assertFalse(result["scientific_integrity_failure"])

    def test_unbound_receipt_cannot_promote(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            artifact = Path(temporary_directory) / "sealed.bin"
            artifact.write_bytes(b"sealed")
            expected = self._identity("sealed.bin", 6, SEALED_SHA256)
            completed, result = self._run_identity(
                {
                    "schema": "bass-artifact-identity-request-v1",
                    "identity_class": "A",
                    "relation": "EXACT_BYTES",
                    "artifact": {"path": str(artifact), "filename": "sealed.bin"},
                    "expected": expected,
                    "receipt": {"subject": expected},
                }
            )

        self.assertEqual(completed.returncode, 3)
        self.assertEqual(result["code"], "UNBOUND_HISTORICAL_EVIDENCE")
        self.assertEqual(result["severity"], "P0")
        self.assertTrue(result["blocking"])

    def test_absolute_sidecar_path_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            artifact = root / "sealed.bin"
            artifact.write_bytes(b"sealed")
            sidecar = root / "artifact.sha256"
            sidecar.write_text(f"{SEALED_SHA256}  /mnt/data/sealed.bin\n", encoding="utf-8")
            expected = self._identity("sealed.bin", 6, SEALED_SHA256)
            completed, result = self._run_identity(
                {
                    "schema": "bass-artifact-identity-request-v1",
                    "identity_class": "A",
                    "relation": "EXACT_BYTES",
                    "artifact": {"path": str(artifact), "filename": "sealed.bin"},
                    "expected": expected,
                    "receipt": {"subject": expected, "source": expected},
                    "sidecar": {"path": str(sidecar)},
                }
            )

        self.assertEqual(completed.returncode, 2)
        self.assertEqual(result["code"], "NON_PORTABLE_SIDECAR")
        self.assertEqual(result["finding_class"], "D")
        self.assertTrue(result["blocking"])
        self.assertFalse(result["scientific_integrity_failure"])

    def test_unmanifested_cache_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            evidence_root = Path(temporary_directory) / "evidence"
            evidence_root.mkdir()
            (evidence_root / "payload.txt").write_bytes(b"manifested")
            cache_directory = evidence_root / "scripts" / "__pycache__"
            cache_directory.mkdir(parents=True)
            (cache_directory / "verify.cpython-312.pyc").write_bytes(b"cache")
            completed, result = self._run_identity(
                {
                    "schema": "bass-artifact-identity-request-v1",
                    "identity_class": "B",
                    "relation": "DETERMINISTIC_EVIDENCE",
                    "artifact": {"path": str(evidence_root), "filename": "evidence"},
                    "expected": self._identity("evidence", 0, "0" * 64),
                    "manifest": {"paths": ["payload.txt"]},
                }
            )

        self.assertEqual(completed.returncode, 3)
        self.assertEqual(result["code"], "CACHE_CONTAMINATION")
        self.assertEqual(result["identity_class"], "B")
        self.assertEqual(result["severity"], "P0")
        self.assertTrue(result["blocking"])
        self.assertFalse(result["scientific_integrity_failure"])

    def test_forbidden_diff_is_p0(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = Path(temporary_directory) / "repository"
            repository.mkdir()
            subprocess.run(["git", "init", "-q"], cwd=repository, check=True)
            subprocess.run(["git", "config", "user.name", "AC01 Test"], cwd=repository, check=True)
            subprocess.run(["git", "config", "user.email", "ac01@example.invalid"], cwd=repository, check=True)
            scientific_source = repository / "source" / "formula.py"
            scientific_source.parent.mkdir()
            scientific_source.write_text("VALUE = 1\n", encoding="utf-8")
            subprocess.run(["git", "add", "source/formula.py"], cwd=repository, check=True)
            subprocess.run(["git", "commit", "-qm", "base"], cwd=repository, check=True)
            base = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repository, text=True).strip()
            scientific_source.write_text("VALUE = 2\n", encoding="utf-8")
            contract = Path(temporary_directory) / "contract.json"
            contract.write_text(
                json.dumps(
                    {
                        "schema": "bass-ac01-nonselfref-successor/v1",
                        "implementation": {
                            "base_sha": base,
                            "allowed_paths": ["scripts/**", "tests/verification/**"],
                        },
                    }
                ),
                encoding="utf-8",
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    str(DIFF_VERIFIER),
                    "--base",
                    base,
                    "--contract",
                    str(contract),
                ],
                cwd=repository,
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertTrue(completed.stdout.strip(), f"diff verifier emitted no result; stderr={completed.stderr!r}")
        self.assertEqual(completed.returncode, 3)
        self.assertIn("FORBIDDEN_REFERENCE_MUTATION", completed.stdout)
        self.assertIn("source/formula.py", completed.stdout)

    def test_distinct_container_can_pass_content_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            artifact = Path(temporary_directory) / "fresh-container.zip"
            artifact.write_bytes(b"fresh-container")
            actual = self._identity("fresh-container.zip", 15, FRESH_CONTAINER_SHA256)
            expected = self._identity("content-capsule.tar.xz", 15, CONTENT_CAPSULE_SHA256)
            base_request = {
                "schema": "bass-artifact-identity-request-v1",
                "identity_class": "C",
                "relation": "SCIENTIFIC_CONTENT_EQUIVALENCE",
                "artifact": {"path": str(artifact), "filename": "fresh-container.zip"},
                "expected": expected,
                "receipt": {"subject": actual, "source": expected},
            }
            blocked, blocked_result = self._run_identity(base_request)
            passing_request = dict(base_request)
            passing_request["content_criteria"] = {
                "member_atlas": "PASS",
                "replay_gates": "PASS",
            }
            passed, passed_result = self._run_identity(passing_request)

        self.assertEqual(blocked.returncode, 2)
        self.assertEqual(blocked_result["code"], "BLOCKED_CONTENT_CRITERIA_REQUIRED")
        self.assertEqual(passed.returncode, 0)
        self.assertEqual(passed_result["code"], "PASS_CONTENT_EQUIVALENCE")
        self.assertEqual(passed_result["identity_class"], "C")
        self.assertFalse(passed_result["blocking"])
        self.assertFalse(passed_result["scientific_integrity_failure"])


if __name__ == "__main__":
    unittest.main()
