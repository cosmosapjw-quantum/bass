from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "docs" / "bass_master_ssot_v2" / "SYNC_MAP_02F"


class ExternalOracleTriangulationContract(unittest.TestCase):
    def test_required_independent_oracle_surfaces_exist(self) -> None:
        required = [
            ROOT / "scripts" / "verify_sync_map02f_symengine.py",
            ROOT / "scripts" / "verify_sync_map02f_pylorentz.py",
            ROOT / "scripts" / "verify_sync_map02f_cosmoboost_runtime.py",
            STAGE / "EXTERNAL_ORACLE_MATRIX_R1.json",
        ]
        missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
        self.assertEqual(missing, [], f"external-oracle surfaces are absent: {missing}")

    def test_matrix_keeps_all_external_packages_non_authoritative(self) -> None:
        matrix_path = STAGE / "EXTERNAL_ORACLE_MATRIX_R1.json"
        self.assertTrue(matrix_path.is_file(), "external-oracle matrix is absent")
        matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
        rows = matrix["oracles"]
        self.assertEqual({row["package"] for row in rows}, {"symengine", "pylorentz", "cosmoboost"})
        self.assertTrue(all(row["authority_effect"] == "NONE_EXTERNAL_ORACLE" for row in rows))
        self.assertTrue(all(row["claim_scope"] != "CONSUMER_IMPLEMENTATION_PARITY" for row in rows))

    def test_matrix_uses_exact_package_pins(self) -> None:
        matrix_path = STAGE / "EXTERNAL_ORACLE_MATRIX_R1.json"
        self.assertTrue(matrix_path.is_file(), "external-oracle matrix is absent")
        matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
        pins = {row["package"]: row["version"] for row in matrix["oracles"]}
        self.assertEqual(
            pins,
            {"symengine": "0.14.1", "pylorentz": "0.3.3", "cosmoboost": "1.1.6"},
        )

    def test_matrix_preserves_physics_firewalls(self) -> None:
        matrix_path = STAGE / "EXTERNAL_ORACLE_MATRIX_R1.json"
        self.assertTrue(matrix_path.is_file(), "external-oracle matrix is absent")
        matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
        forbidden = set(matrix["forbidden_promotions"])
        self.assertTrue(
            {
                "GLOBAL_MATTER_TILT",
                "FINITE_ELECTRON_TILT_COLLISION",
                "CONSUMER_IMPLEMENTATION_PARITY",
                "BACKGROUND_PROVIDER_ADMISSION",
                "SCIENCE_VALIDITY",
            }.issubset(forbidden)
        )


if __name__ == "__main__":
    unittest.main()
