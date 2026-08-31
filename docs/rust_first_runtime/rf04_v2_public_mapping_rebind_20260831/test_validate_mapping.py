"""Regression checks for the RF04 v2 public-mapping authority package."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
import shutil
import json
import hashlib


PACKAGE = Path(__file__).resolve().parent
MANIFEST_FILES = (
    "AUTHORITY_REBIND.json",
    "LOCAL_CODEX_HANDOFF_CONTRACT.json",
    "LOCAL_CODEX_HANDOFF.md",
    "LOCAL_IMPLEMENTATION_PROMPT_R2.md",
    "README.md",
    "R2_AUTHORITY_AMENDMENT.json",
    "R2_DESIGN.md",
    "R2_IMPLEMENTATION_PLAN.md",
    "V2_PUBLIC_MAPPING.json",
    "test_validate_mapping.py",
    "validate_mapping.py",
)


def rewrite_manifest(root: Path) -> None:
    entries = [
        f"{hashlib.sha256((root / relative).read_bytes()).hexdigest()}  {relative}"
        for relative in MANIFEST_FILES
    ]
    (root / "MANIFEST.sha256").write_text("\n".join(entries) + "\n", encoding="utf-8")


class PublicMappingPackageTests(unittest.TestCase):
    def test_validator_accepts_the_committed_authority_package(self) -> None:
        result = subprocess.run(
            [sys.executable, str(PACKAGE / "validate_mapping.py"), str(PACKAGE)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

    def test_validator_rejects_a_final_donor_identity_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            copied_package = Path(temporary_directory) / "package"
            shutil.copytree(PACKAGE, copied_package)
            mapping = copied_package / "AUTHORITY_REBIND.json"
            mapping.write_text(
                mapping.read_text(encoding="utf-8").replace(
                    "693e9fff0d44f2b8e40966ceb8da3c348d830bd4",
                    "0000000000000000000000000000000000000000",
                ),
                encoding="utf-8",
            )
            rewrite_manifest(copied_package)
            result = subprocess.run(
                [sys.executable, str(copied_package / "validate_mapping.py"), str(copied_package)],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("final donor", result.stderr + result.stdout)

    def test_validator_rejects_handoff_markdown_that_drifts_from_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            copied_package = Path(temporary_directory) / "package"
            shutil.copytree(PACKAGE, copied_package)
            handoff = copied_package / "LOCAL_CODEX_HANDOFF.md"
            handoff.write_text(
                handoff.read_text(encoding="utf-8").replace(
                    "Do not begin LOCAL-02",
                    "LOCAL-02 may begin",
                ),
                encoding="utf-8",
            )
            rewrite_manifest(copied_package)
            result = subprocess.run(
                [sys.executable, str(copied_package / "validate_mapping.py"), str(copied_package)],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("handoff markdown", result.stderr + result.stdout)

    def test_validator_rejects_zero_argument_identity_with_dynamic_context(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            copied_package = Path(temporary_directory) / "package"
            shutil.copytree(PACKAGE, copied_package)
            mapping_path = copied_package / "V2_PUBLIC_MAPPING.json"
            mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
            mapping["symbols"]["identity"]["arguments"] = []
            mapping_path.write_text(
                json.dumps(mapping, indent=2) + "\n",
                encoding="utf-8",
            )
            rewrite_manifest(copied_package)
            result = subprocess.run(
                [sys.executable, str(copied_package / "validate_mapping.py"), str(copied_package)],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("identity arguments", result.stderr + result.stdout)

    def test_validator_rejects_wheel_hash_as_runtime_payload_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            copied_package = Path(temporary_directory) / "package"
            shutil.copytree(PACKAGE, copied_package)
            mapping_path = copied_package / "V2_PUBLIC_MAPPING.json"
            mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
            mapping["execution_identity"]["fixed_values"]["native_payload_identity"] = (
                "wheel-sha256:" + "0" * 64
            )
            mapping_path.write_text(
                json.dumps(mapping, indent=2) + "\n",
                encoding="utf-8",
            )
            rewrite_manifest(copied_package)
            result = subprocess.run(
                [sys.executable, str(copied_package / "validate_mapping.py"), str(copied_package)],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("native payload identity", result.stderr + result.stdout)

    def test_validator_rejects_missing_geometry_receipt_codec(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            copied_package = Path(temporary_directory) / "package"
            shutil.copytree(PACKAGE, copied_package)
            mapping_path = copied_package / "V2_PUBLIC_MAPPING.json"
            mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
            mapping.pop("geometry_receipt_codecs", None)
            mapping_path.write_text(
                json.dumps(mapping, indent=2) + "\n",
                encoding="utf-8",
            )
            rewrite_manifest(copied_package)
            result = subprocess.run(
                [sys.executable, str(copied_package / "validate_mapping.py"), str(copied_package)],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("geometry receipt codecs", result.stderr + result.stdout)

    def test_validator_rejects_missing_batch_status_and_diagnostic_semantics(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            copied_package = Path(temporary_directory) / "package"
            shutil.copytree(PACKAGE, copied_package)
            mapping_path = copied_package / "V2_PUBLIC_MAPPING.json"
            mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
            mapping["batch_result"].pop("member_status_codes", None)
            mapping["trajectory_result"]["fields"]["diagnostics"].pop("v2_semantics", None)
            mapping_path.write_text(
                json.dumps(mapping, indent=2) + "\n",
                encoding="utf-8",
            )
            rewrite_manifest(copied_package)
            result = subprocess.run(
                [sys.executable, str(copied_package / "validate_mapping.py"), str(copied_package)],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(result.returncode, 0)
        combined = result.stderr + result.stdout
        self.assertIn("batch status code table", combined)
        self.assertIn("diagnostic semantics", combined)


if __name__ == "__main__":
    unittest.main()
