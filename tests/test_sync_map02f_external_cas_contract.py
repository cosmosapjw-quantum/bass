from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_SURFACES = (
    "docs/bass_master_ssot_v2/SYNC_MAP_02F/EXTERNAL_CAS_MATRIX.json",
    "scripts/verify_sync_map02f_external_cas_receipts.py",
    "external_cas/maxima/check_sync_map02f.mac",
    "external_cas/form/check_sync_map02f.frm",
    "external_cas/ginac/check_sync_map02f.cpp",
    "external_cas/symengine/check_sync_map02f.py",
    "external_cas/z3/check_sync_map02f.py",
    "external_cas/symbolica/check_sync_map02f.py",
    "external_cas/cadabra2/check_sync_map02f.cdb",
    "external_cas/reduce/check_sync_map02f.red",
)

MANDATORY_ENGINES = {"maxima", "form", "ginac", "symengine", "z3", "symbolica"}
EXPLORATORY_ENGINES = {"cadabra2", "reduce"}


class ExternalCASMatrixContractTests(unittest.TestCase):
    def test_required_surfaces_exist(self) -> None:
        missing = [path for path in REQUIRED_SURFACES if not (ROOT / path).is_file()]
        self.assertEqual([], missing, f"missing external-CAS surfaces: {missing}")

    def test_manifest_declares_independent_mandatory_and_exploratory_axes(self) -> None:
        path = ROOT / "docs/bass_master_ssot_v2/SYNC_MAP_02F/EXTERNAL_CAS_MATRIX.json"
        self.assertTrue(path.is_file(), "external CAS matrix is absent")
        matrix = json.loads(path.read_text(encoding="utf-8"))
        engines = matrix.get("engines", [])
        mandatory = {row.get("engine") for row in engines if row.get("required_for_axis_closeout")}
        exploratory = {row.get("engine") for row in engines if not row.get("required_for_axis_closeout")}
        self.assertEqual(MANDATORY_ENGINES, mandatory)
        self.assertEqual(EXPLORATORY_ENGINES, exploratory)
        self.assertEqual("NONE", matrix.get("authority_effect"))
        self.assertIn("NO_02F_SEMANTIC_CLOSEOUT", matrix.get("withheld_claims", []))

    def test_verifier_is_fail_closed_on_missing_receipts(self) -> None:
        path = ROOT / "scripts/verify_sync_map02f_external_cas_receipts.py"
        self.assertTrue(path.is_file(), "receipt verifier is absent")
        source = path.read_text(encoding="utf-8")
        for token in (
            "MANDATORY_ENGINES",
            "expected_identity_ids",
            "hostile_mutations",
            "download_sha256",
            "PASS_EXTERNAL_CAS_MATRIX",
        ):
            self.assertIn(token, source)


if __name__ == "__main__":
    unittest.main()
