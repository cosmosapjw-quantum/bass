from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

RED_CONTRACT = (
    ROOT
    / "docs"
    / "bass_master_ssot_v2"
    / "BG_02_IMPLEMENTATION"
    / "BG_02_IMPLEMENTATION_RED_CONTRACT.json"
)
DESIGN_PIN = (
    ROOT
    / "docs"
    / "bass_master_ssot_v2"
    / "BG_02_IMPLEMENTATION"
    / "BG_02_DESIGN_AUTHORITY_PIN.json"
)
PRODUCTION = (
    ROOT
    / "wolfram"
    / "BASS"
    / "Kernel"
    / "Background"
    / "EinsteinProjection.wl"
)
IMPLEMENTATION_REGISTRY = (
    ROOT
    / "docs"
    / "bass_master_ssot_v2"
    / "BG_02_IMPLEMENTATION"
    / "BG_02_IMPLEMENTATION_REGISTRY.json"
)
INIT = ROOT / "wolfram" / "BASS" / "Kernel" / "init.wl"
NATIVE_RUNNER = (
    ROOT
    / "wolfram"
    / "scripts"
    / "run_bg02_einstein_projection_native.wls"
)
NATIVE_WLT = (
    ROOT
    / "wolfram"
    / "BASS"
    / "Tests"
    / "BG02EinsteinProjectionImplementation.wlt"
)

EXPECTED_PARENT = "80d271cc528e1a0ffa813ecd3e3fb7610f3fa755"
EXPECTED_TREE = "3fd8818938eaa0988988c6927cff799455a7a31d"
EXPECTED_DESIGN = "ef6d51aad709555737617e2021ba50c553c90b6c"

EXPECTED_FORMULA_IDS = [
    "BASS.BG.EINSTEIN_RESIDUAL.001",
    "BASS.BG.HAMILTONIAN_PROJECTION.001",
    "BASS.BG.MOMENTUM_PROJECTION.001",
    "BASS.BG.SPATIAL_TRACE_PROJECTION.001",
    "BASS.BG.SPATIAL_PSTF_PROJECTION.001",
    "BASS.BG.HAMILTONIAN_HSIGMA.001",
    "BASS.BG.EXPANSION_RATE_RAW.001",
    "BASS.BG.EXPANSION_RATE_ADM.001",
    "BASS.BG.EXPANSION_RATE_RAYCHAUDHURI.001",
    "BASS.BG.SHEAR_RATE_LIE.001",
    "BASS.BG.SHEAR_RATE_PROJECTED.001",
    "BASS.BG.HOMOGENEOUS_SCALAR_CURVATURE.001",
    "BASS.BG.HOMOGENEOUS_MOMENTUM.001",
    "BASS.BG.EXCEPTIONAL_VI_MOMENTUM_CARRIER.001",
]

PUBLIC_APIS = [
    "EinsteinResidualTensor",
    "EinsteinProjectionRegistry",
    "HamiltonianProjection",
    "MomentumProjection",
    "SpatialTraceProjection",
    "SpatialPSTFProjection",
    "SpatialTraceRate",
    "ADMTraceRate",
    "RaychaudhuriRate",
    "ShearLieRate",
    "ShearProjectedRate",
]


class BG02EinsteinProjectionImplementationTests(unittest.TestCase):
    def production_source(self) -> str:
        self.assertTrue(
            PRODUCTION.is_file(),
            f"BG02 production module missing: {PRODUCTION}",
        )
        return PRODUCTION.read_text(encoding="utf-8")

    def implementation_registry(self) -> dict:
        self.assertTrue(
            IMPLEMENTATION_REGISTRY.is_file(),
            f"BG02 implementation registry missing: {IMPLEMENTATION_REGISTRY}",
        )
        return json.loads(IMPLEMENTATION_REGISTRY.read_text(encoding="utf-8"))

    # These two tests are expected to pass in the RED source.
    def test_exact_scientific_parent_and_design_are_pinned(self) -> None:
        self.assertTrue(RED_CONTRACT.is_file(), RED_CONTRACT)
        self.assertTrue(DESIGN_PIN.is_file(), DESIGN_PIN)
        red = json.loads(RED_CONTRACT.read_text(encoding="utf-8"))
        pin = json.loads(DESIGN_PIN.read_text(encoding="utf-8"))
        self.assertEqual(red["repository_scope"], "BASS_ONLY")
        self.assertEqual(red["scientific_parent"]["commit"], EXPECTED_PARENT)
        self.assertEqual(red["scientific_parent"]["tree"], EXPECTED_TREE)
        self.assertEqual(red["design_authority"]["commit"], EXPECTED_DESIGN)
        self.assertEqual(red["design_authority"]["formula_ids"], EXPECTED_FORMULA_IDS)
        self.assertEqual(pin["scientific_parent_commit"], EXPECTED_PARENT)
        self.assertEqual(
            pin["semantic_federation_reference"]["effect"],
            "DEPENDENCY_REFERENCE_ONLY_NOT_CODE_ANCESTRY",
        )

    def test_pr91_geometry_authority_sources_are_present(self) -> None:
        required = [
            ROOT / "wolfram/BASS/Kernel/Geometry/Abstract1Plus3.wl",
            ROOT / "wolfram/BASS/Kernel/Geometry/LeviCivitaConnection.wl",
            ROOT / "wolfram/BASS/Kernel/Geometry/ONFConnectionCurvature.wl",
            ROOT / "wolfram/BASS/Kernel/Geometry/XCobaCurvatureWitnesses.wl",
            ROOT / "wolfram/BASS/Kernel/IR/EquationIR.wl",
            INIT,
        ]
        for path in required:
            self.assertTrue(path.is_file(), path)
        init_text = INIT.read_text(encoding="utf-8")
        self.assertIn('"Geometry", "ONFConnectionCurvature.wl"', init_text)
        self.assertIn('"Geometry", "XCobaCurvatureWitnesses.wl"', init_text)

    # The following sixteen tests are expected to fail in RED because the
    # production module and implementation registry are deliberately absent.
    def test_production_module_exists(self) -> None:
        source = self.production_source()
        self.assertIn('BeginPackage["BASS`Background`"]', source)

    def test_loader_imports_exactly_one_background_module(self) -> None:
        self.production_source()
        init_text = INIT.read_text(encoding="utf-8")
        self.assertEqual(
            init_text.count('"Background", "EinsteinProjection.wl"'),
            1,
            "loader must import exactly one BG02 production module",
        )

    def test_implementation_registry_has_exact_14_ids(self) -> None:
        registry = self.implementation_registry()
        self.assertEqual(registry["formula_count"], 14)
        self.assertEqual(
            [row["formula_id"] for row in registry["formulas"]],
            EXPECTED_FORMULA_IDS,
        )
        self.assertTrue(
            all(row["dimension"] == "L^-2" for row in registry["formulas"])
        )

    def test_required_public_api_names_are_exposed(self) -> None:
        source = self.production_source()
        for api in PUBLIC_APIS:
            self.assertRegex(
                source,
                rf"\b{re.escape(api)}::usage\b",
                f"missing public API usage: {api}",
            )

    def test_single_off_shell_residual_is_the_only_projection_authority(self) -> None:
        source = self.production_source()
        self.assertIn("EinsteinResidualTensor", source)
        self.assertIn("kappaG", source)
        self.assertNotRegex(source, r"(?<![A-Za-z])kappa(?![A-Za-zG_])")
        self.assertEqual(source.count("G_ab + Lambda g_ab - kappa_G T_ab"), 1)
        for api in (
            "HamiltonianProjection",
            "MomentumProjection",
            "SpatialTraceProjection",
            "SpatialPSTFProjection",
        ):
            block = re.search(
                rf"{api}\[[^\]]*\]\s*:=([\s\S]*?)(?=\n[A-Z]\w*(?:\[[^\]]*\])?\s*:=|\nEnd\[)",
                source,
            )
            self.assertIsNotNone(block, f"definition missing: {api}")
            self.assertIn("EinsteinResidualTensor", block.group(1))

    def test_hamiltonian_projection_contract_is_present(self) -> None:
        source = self.production_source()
        for token in (
            "HamiltonianProjection",
            "R3",
            "K^2",
            "K_ab K^ab",
            "Lambda",
            "kappaG",
            "rho",
        ):
            self.assertIn(token, source)

    def test_momentum_projection_contract_is_present(self) -> None:
        source = self.production_source()
        for token in (
            "MomentumProjection",
            "D^b K_ab",
            "D_a K",
            "kappaG",
            "q_a",
        ):
            self.assertIn(token, source)

    def test_spatial_trace_projection_contract_is_present(self) -> None:
        source = self.production_source()
        for token in (
            "SpatialTraceProjection",
            "R3",
            "Lie",
            "D.A",
            "A2",
            "kappaG",
            "p",
        ):
            self.assertIn(token, source)

    def test_spatial_pstf_projection_contract_is_present(self) -> None:
        source = self.production_source()
        for token in (
            "SpatialPSTFProjection",
            "R3PSTF",
            "DPSTFA",
            "APSTFA",
            "kappaG",
            "pi_ab",
        ):
            self.assertIn(token, source)

    def test_three_expansion_rates_remain_distinct_and_off_shell(self) -> None:
        source = self.production_source()
        for api in ("SpatialTraceRate", "ADMTraceRate", "RaychaudhuriRate"):
            self.assertIn(f"{api}::usage", source)
        self.assertIn("F_ADM - F_trace + Hres/2", source)
        self.assertIn("F_trace - F_Ray + Hres/6", source)
        self.assertIn("F_ADM - F_Ray + 2 Hres/3", source)
        self.assertNotIn("Hres -> 0", source)

    def test_off_shell_rate_identity_metadata_is_registered(self) -> None:
        registry = self.implementation_registry()
        identities = registry["off_shell_identities"]
        self.assertEqual(
            identities,
            [
                "F_ADM - F_trace + Hres/2 = 0",
                "F_trace - F_Ray + Hres/6 = 0",
                "F_ADM - F_Ray + 2 Hres/3 = 0",
            ],
        )
        self.assertFalse(registry["state_projection_policy"]["projects_Hres_to_zero"])

    def test_shear_rate_derivative_kinds_are_explicit(self) -> None:
        registry = self.implementation_registry()
        rates = registry["shear_rate_metadata"]
        self.assertEqual(
            rates["BASS.BG.SHEAR_RATE_LIE.001"]["derivative_kind"],
            "LIE_DERIVATIVE_PSTF",
        )
        self.assertEqual(
            rates["BASS.BG.SHEAR_RATE_PROJECTED.001"]["derivative_kind"],
            "PROJECTED_COVARIANT_NORMAL_DERIVATIVE",
        )

    def test_locked_curvature_route_and_connection_order_guards_exist(self) -> None:
        source = self.production_source()
        self.assertTrue(
            "ONFScalarCurvature" in source
            or "ConnectionToLockedGammaOrder" in source
        )
        self.assertNotIn("Koszul", source)
        registry = self.implementation_registry()
        guards = registry["connection_order_guards"]
        self.assertEqual(guards["Bianchi_V"]["locked"], -6)
        self.assertEqual(guards["Bianchi_V"]["wrong"], 4)
        self.assertEqual(guards["Bianchi_II"]["locked"], -0.5)
        self.assertEqual(guards["Bianchi_II"]["wrong"], 1.5)
        self.assertTrue(guards["I_IX_ONLY_IS_INSUFFICIENT"])

    def test_flat_flrw_de_sitter_and_kasner_limits_are_registered(self) -> None:
        registry = self.implementation_registry()
        limits = registry["known_limits"]
        self.assertEqual(limits["flat_de_sitter"]["rates"], [0, 0, 0])
        self.assertEqual(limits["kasner_vacuum"]["Hres"], 0)
        self.assertEqual(
            limits["kasner_vacuum"]["rates"],
            ["-1/(3 tau^2)", "-1/(3 tau^2)", "-1/(3 tau^2)"],
        )
        self.assertEqual(
            limits["flat_flrw"]["friedmann"],
            "3 H^2 = kappaG rho + Lambda",
        )

    def test_exceptional_vi_minus_one_ninth_carrier_is_retained(self) -> None:
        source = self.production_source()
        self.assertIn(
            "N22 Sigma12 + (N23 - 3 A) Sigma13",
            source,
        )
        self.assertNotIn("N22 Sigma12 + N23 Sigma13", source)

    def test_native_xact_replay_and_claim_firewalls_exist(self) -> None:
        self.production_source()
        self.implementation_registry()
        self.assertTrue(NATIVE_RUNNER.is_file(), NATIVE_RUNNER)
        self.assertTrue(NATIVE_WLT.is_file(), NATIVE_WLT)
        wlt_text = NATIVE_WLT.read_text(encoding="utf-8")
        self.assertEqual(wlt_text.count("VerificationTest["), 26)
        runner_text = NATIVE_RUNNER.read_text(encoding="utf-8")
        for token in (
            "xTensor",
            "xCoba",
            "TestsFailedCount",
            "TestsNotEvaluatedCount",
            "TEMPORARY_FILE_STRICT_JSON_ROUND_TRIP_THEN_RENAME",
        ):
            self.assertIn(token, runner_text)
        registry = self.implementation_registry()
        forbidden = {
            "CONSTRAINT_PROPAGATION_VERIFIED",
            "BACKGROUND_NUMERICAL_EVOLUTION",
            "PROVIDER_ADMISSION",
            "SCIENCE_VALIDITY",
            "PASS_RF04",
        }
        self.assertTrue(forbidden.issubset(set(registry["withheld_claims"])))


if __name__ == "__main__":
    unittest.main()
