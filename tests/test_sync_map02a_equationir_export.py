from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "wolfram/BASS/Kernel/IR/SemanticFormulaExport.wl"
INIT = ROOT / "wolfram/BASS/Kernel/init.wl"
WLT = ROOT / "wolfram/BASS/Tests/SYNCMAP02AEquationIRExport.wlt"
SCHEMA = ROOT / "wolfram/schemas/bass-formula-semantic-export.schema.json"

EXPECTED_GLOBAL_IDS = {
    "BASS.GEO.STRUCTURE_CONSTANTS.001",
    "BASS.GEO.SPATIAL_PROJECTOR.001",
    "BASS.GEO.SPATIAL_VOLUME_FORM.001",
    "BASS.GEO.NORMAL_ACCELERATION.001",
    "BASS.GEO.EXTRINSIC_CURVATURE.001",
    "BASS.GEO.NORMAL_DERIVATIVE_DECOMPOSITION.001",
    "BASS.GEO.EXTRINSIC_CURVATURE_SHEAR_SPLIT.001",
    "BASS.GEO.GAUSS.001",
    "BASS.GEO.CODAZZI.001",
    "BASS.GEO.CONTRACTED_GAUSS.001",
    "BASS.GEO.LEVI_CIVITA_CONNECTION.001",
    "BASS.GEO.SPATIAL_RIEMANN.001",
    "BASS.GEO.SPATIAL_RICCI.001",
    "BASS.GEO.SPATIAL_SCALAR.001",
}


class SyncMap02AEquationIRExportContractTests(unittest.TestCase):
    def test_semantic_export_module_exists(self) -> None:
        self.assertTrue(MODULE.is_file(), "SemanticFormulaExport.wl is absent")

    def test_loader_registers_export_after_formula_sources(self) -> None:
        init = INIT.read_text(encoding="utf-8")
        export = init.index('"SemanticFormulaExport.wl"')
        self.assertLess(init.index('"Abstract1Plus3.wl"'), export)
        self.assertLess(init.index('"LeviCivitaConnection.wl"'), export)
        self.assertLess(init.index('"ONFConnectionCurvature.wl"'), export)

    def test_public_api_and_semantic_projection_contract(self) -> None:
        source = MODULE.read_text(encoding="utf-8")
        for name in (
            "BASSFormulaGlobalIDMap",
            "BASSFormulaEquationIRRegistry",
            "FormulaSemanticProjection",
            "FormulaSemanticSHA256",
            "BASSFormulaDependencyEdges",
            "BASSFormulaSemanticExport",
            "BASSFormulaSemanticExportQ",
        ):
            self.assertIn(name, source)
        self.assertIn("KeyDrop", source)
        self.assertIn('"formula_id"', source)
        self.assertIn('"provenance"', source)

    def test_all_global_ids_are_declared(self) -> None:
        source = MODULE.read_text(encoding="utf-8")
        missing = sorted(formula_id for formula_id in EXPECTED_GLOBAL_IDS if formula_id not in source)
        self.assertEqual(missing, [])

    def test_test_contract_binds_formula_count_and_hash_invariance(self) -> None:
        source = WLT.read_text(encoding="utf-8")
        self.assertIn("Length[$BASSSyncMap02ARegistry]", source)
        self.assertIn("14", source)
        self.assertIn("hash-excludes-id-and-provenance", source)
        self.assertIn("dependency-closure", source)
        self.assertIn("curvature-connection-edge", source)

    def test_public_schema_parses(self) -> None:
        parsed = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(parsed["$id"], "bass.master-ssot-v2.formula-semantic-export.v1")
        self.assertIn("formulas", parsed["required"])
        self.assertIn("dependency_edges", parsed["required"])
        self.assertIn("registry_semantic_hash", parsed["required"])


if __name__ == "__main__":
    unittest.main()
