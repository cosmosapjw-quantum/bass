"""Regression checks for the RF04 v2 public-mapping authority package."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
import shutil


PACKAGE = Path(__file__).resolve().parent


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
            result = subprocess.run(
                [sys.executable, str(copied_package / "validate_mapping.py"), str(copied_package)],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("handoff markdown", result.stderr + result.stdout)


if __name__ == "__main__":
    unittest.main()
