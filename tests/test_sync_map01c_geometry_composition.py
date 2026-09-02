from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class GeometryLineageCompositionContractTests(unittest.TestCase):
    def test_required_composed_sources_exist(self) -> None:
        required = [
            "wolfram/BASS/Kernel/Geometry/CanonicalizationBackend.wl",
            "wolfram/BASS/Kernel/Geometry/Abstract1Plus3.wl",
            "wolfram/BASS/Kernel/Geometry/Abstract1Plus3Receipt.wl",
            "wolfram/BASS/Kernel/Geometry/ONFConnectionCurvature.wl",
            "wolfram/BASS/Kernel/Geometry/XCobaCurvatureWitnesses.wl",
            "wolfram/BASS/Tests/W2AbstractGeometry.wlt",
            "wolfram/BASS/Tests/W3ONFCurvature.wlt",
            "wolfram/BASS/Tests/SYNCMAP01CGeometryComposition.wlt",
            "wolfram/schemas/abstract-1plus3-model.schema.json",
            "wolfram/schemas/w3-xcoba-curvature-witness.schema.json",
        ]
        missing = [path for path in required if not (ROOT / path).is_file()]
        self.assertEqual(missing, [], f"missing composed geometry paths: {missing}")

    def test_curvature_uses_canonical_connection(self) -> None:
        source = (ROOT / "wolfram/BASS/Kernel/Geometry/ONFConnectionCurvature.wl").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "ConnectionToLockedGammaOrder[LeviCivitaConnection[a, n]]",
            source,
        )
        self.assertNotIn(
            "(c[[gamma, alpha, beta]]\n      - c[[alpha, beta, gamma]]",
            source,
            "curvature composition must not carry a second connection implementation",
        )
        self.assertIn("canonical_connection_formula_id", source)

    def test_loader_orders_connection_before_curvature(self) -> None:
        init = (ROOT / "wolfram/BASS/Kernel/init.wl").read_text(encoding="utf-8")
        connection = init.index('"LeviCivitaConnection.wl"')
        curvature = init.index('"ONFConnectionCurvature.wl"')
        xcoba = init.index('"XCobaCurvatureWitnesses.wl"')
        self.assertLess(connection, curvature)
        self.assertLess(curvature, xcoba)

    def test_dimension_registry_contains_w2_and_curvature_dimensions(self) -> None:
        dimensions = (ROOT / "wolfram/BASS/Kernel/Authority/Dimensions.wl").read_text(
            encoding="utf-8"
        )
        for token in ('"schema_version" -> "1.1.0"', '"A_a"', '"K_ab"', '"R3_scalar"'):
            self.assertIn(token, dimensions)

    def test_public_schemas_parse(self) -> None:
        for relative in (
            "wolfram/schemas/abstract-1plus3-model.schema.json",
            "wolfram/schemas/w3-xcoba-curvature-witness.schema.json",
        ):
            parsed = json.loads((ROOT / relative).read_text(encoding="utf-8"))
            self.assertIsInstance(parsed, dict)

    def test_composition_test_binds_exact_parent_lineages(self) -> None:
        test_source = (ROOT / "wolfram/BASS/Tests/SYNCMAP01CGeometryComposition.wlt").read_text(
            encoding="utf-8"
        )
        self.assertIn("c787e6c51608568fcb60d52f010235f8cb2c1076", test_source)
        self.assertIn("5d3e8ecce2a40a1bc2b43af7daa985e042d9815f", test_source)
        self.assertIn("ConnectionCompositionReceiptQ", test_source)
        self.assertIn("dual_full_riemann_match", test_source)


if __name__ == "__main__":
    unittest.main()
