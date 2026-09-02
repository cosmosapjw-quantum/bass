from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class XCAS04ContractTests(unittest.TestCase):
    def test_required_engine_scripts_exist(self) -> None:
        required = [
            ROOT / "external_cas/octave/check_sync_map02f_xcas04.m",
            ROOT / "external_cas/jas/CheckSyncMap02fXcas04.java",
            ROOT / "external_cas/julia/Project.toml",
            ROOT / "external_cas/julia/Manifest.toml",
            ROOT / "external_cas/julia/check_sync_map02f_xcas04.jl",
        ]
        missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
        self.assertEqual([], missing, f"missing XCAS-04 surfaces: {missing}")

    def test_machine_manifest_exists_and_is_complete(self) -> None:
        path = ROOT / "docs/bass_master_ssot_v2/SYNC_MAP_02F/XCAS04_OCTAVE_JAS_JULIA_MATRIX.json"
        self.assertTrue(path.is_file(), f"missing {path.relative_to(ROOT)}")
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual("XCAS04_OCTAVE_JAS_JULIA", data["matrix_id"])
        self.assertEqual(3, len(data["engines"]))
        by_name = {entry["engine"]: entry for entry in data["engines"]}
        self.assertEqual(
            {"GNU Octave", "Java Algebra System", "Julia/Nemo"},
            set(by_name),
        )
        self.assertEqual(
            "INDEPENDENT_NUMERICAL_AND_MATRIX_ORACLE_NOT_SYMBOLIC_CAS",
            by_name["GNU Octave"]["engine_role"],
        )
        self.assertEqual(
            "INDEPENDENT_EXACT_POLYNOMIAL_CAS",
            by_name["Java Algebra System"]["engine_role"],
        )
        self.assertEqual(
            "INDEPENDENT_EXACT_CAS_JULIA_FRONTEND_FLINT_BACKEND",
            by_name["Julia/Nemo"]["engine_role"],
        )
        self.assertEqual("NONE_EXTERNAL_ORACLE", data["authority_effect"])

    def test_aggregate_verifier_exists(self) -> None:
        self.assertTrue(
            (ROOT / "scripts/verify_xcas04_octave_jas_julia_receipts.py").is_file()
        )


if __name__ == "__main__":
    unittest.main()
