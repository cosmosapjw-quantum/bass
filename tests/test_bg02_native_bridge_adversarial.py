from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRODUCTION = ROOT / "wolfram/BASS/Kernel/Background/EinsteinProjection.wl"
COMPONENT_ORACLE = (
    ROOT
    / "wolfram/BASS/Kernel/Background/EinsteinProjectionComponentOracle.wl"
)
XTENSOR_BRIDGE = (
    ROOT
    / "wolfram/BASS/Kernel/Background/EinsteinProjectionXTensorBridge.wl"
)
GEOMETRY_RULES = (
    ROOT / "wolfram/BASS/Kernel/Geometry/GaussCodazziProjectionRules.wl"
)
REGISTRY = (
    ROOT
    / "docs/bass_master_ssot_v2/BG_02_IMPLEMENTATION/"
    "BG_02_IMPLEMENTATION_REGISTRY.json"
)
RUNNER = ROOT / "wolfram/scripts/run_bg02_einstein_projection_native.wls"


class BG02NativeBridgeAdversarialTests(unittest.TestCase):
    def source(self, path: Path) -> str:
        self.assertTrue(path.is_file(), f"required source missing: {path}")
        return path.read_text(encoding="utf-8")

    def registry(self) -> dict:
        return json.loads(self.source(REGISTRY))

    def test_claim_surface_is_component_oracle_only(self) -> None:
        registry = self.registry()
        self.assertEqual(
            registry.get("status"),
            "COMPONENT_ORACLE_ONLY_NATIVE_XTENSOR_BRIDGE_REQUIRED",
        )
        self.assertEqual(
            registry.get("implementation_layer"),
            "COMPONENT_FORMULA_ORACLE",
        )
        self.assertIs(registry.get("native_tensor_api_admitted"), False)

    def test_component_oracle_and_native_bridge_are_separate_modules(self) -> None:
        self.assertTrue(COMPONENT_ORACLE.is_file(), COMPONENT_ORACLE)
        self.assertTrue(XTENSOR_BRIDGE.is_file(), XTENSOR_BRIDGE)
        component = self.source(COMPONENT_ORACLE)
        bridge = self.source(XTENSOR_BRIDGE)
        self.assertIn("COMPONENT_FORMULA_ORACLE", component)
        self.assertIn("EinsteinResidualTensor", bridge)
        self.assertIn("EinsteinBASSW2CD", bridge)
        self.assertNotIn("residualComponents", bridge)

    def test_tensor_api_is_not_an_association_lookup(self) -> None:
        source = self.source(PRODUCTION)
        self.assertNotIn(
            "EinsteinResidualTensor[vars_:Automatic] := "
            "residualComponents[state[vars]]",
            source,
        )
        self.assertNotRegex(
            source,
            r"HamiltonianProjection\[[^\]]*\]\s*:=\s*Module\["
            r"\{r=EinsteinResidualTensor\[[^\]]*\]\},\s*Lookup\[r,",
        )

    def test_positive_native_gates_are_computed_not_literal(self) -> None:
        source = self.source(PRODUCTION)
        forbidden = (
            '"dependency_graph_closed"->True',
            '"single_off_shell_residual_authority"->True',
            '"I_IX_only_witness_set_rejected"->True',
            '"second_koszul_implementation_absent"->True',
            "TrueQ[A_normal=!=a_B]",
        )
        for marker in forbidden:
            self.assertNotIn(marker, source, marker)

    def test_exceptional_vi_witness_is_derived_not_x_minus_x(self) -> None:
        source = self.source(PRODUCTION)
        self.assertNotIn(
            "(N22 Sigma12+(N23-3 A)Sigma13)-"
            "(N22 Sigma12+(N23-3 A)Sigma13)",
            source,
        )
        self.assertIn("exceptional_VI_minus_one_ninth_residual", source)
        self.assertRegex(
            source,
            r"exceptional_VI_minus_one_ninth_residual[\s\S]*"
            r"MomentumProjection",
        )

    def test_wrong_order_curvature_is_test_only(self) -> None:
        source = self.source(PRODUCTION)
        self.assertNotIn("wrongOrderScalarCurvature", source)
        self.assertNotRegex(source, r"R\s*=\s*Array\[Function")
        self.assertNotRegex(source, r"Ric\s*=\s*Array\[Function")

    def test_state_and_missing_components_fail_closed(self) -> None:
        source = self.source(PRODUCTION)
        self.assertNotIn("state[_] := <||>", source)
        self.assertIn('Failure["InvalidBG02State"', source)
        self.assertIn('Failure["MissingBG02Component"', source)
        self.assertNotRegex(
            source,
            r'Lookup\[r,"(?:Hamiltonian|Momentum|SpatialTrace|SpatialPSTF)'
            r'Projection",r\]',
        )

    def test_native_bridge_uses_exact_w2_sign_registry(self) -> None:
        rules = self.source(GEOMETRY_RULES)
        for formula_id in (
            "W2-CURV-001",
            "W2-CURV-002",
            "W2-CURV-003",
        ):
            self.assertIn(formula_id, rules)
        self.assertIn("GaussCodazziSignRegistryQ", rules)
        self.assertIn("DeltaHamiltonian", rules)
        self.assertIn("DeltaMomentum", rules)
        self.assertIn("DeltaSpatialTrace", rules)
        self.assertIn("DeltaSpatialPSTF", rules)

    def test_native_runner_activates_xact_before_full_init(self) -> None:
        runner = self.source(RUNNER)
        activate = runner.find("ActivatePinnedXAct")
        full_init = runner.find("Get[initPath]")
        self.assertGreaterEqual(activate, 0)
        self.assertGreater(full_init, activate)
        self.assertIn('MemberQ[$Packages, "xAct`xTensor`"]', runner)
        self.assertIn('MemberQ[$Packages, "xAct`xCoba`"]', runner)
        self.assertIn("DownValues[xAct`xTensor`DefTensor]", runner)
        self.assertIn("DownValues[xAct`xCoba`DefChart]", runner)

    def test_every_native_exit_publishes_an_atomic_receipt(self) -> None:
        runner = self.source(RUNNER)
        self.assertIn(
            "writeReceiptAndExit[payload_Association, code_Integer]",
            runner,
        )
        self.assertIn(
            "TEMPORARY_FILE_STRICT_JSON_ROUND_TRIP_THEN_RENAME",
            runner,
        )
        early_exit_positions = [m.start() for m in re.finditer(r"\bExit\[", runner)]
        writer_position = runner.find(
            "writeReceiptAndExit[payload_Association, code_Integer]"
        )
        self.assertTrue(early_exit_positions)
        self.assertGreaterEqual(writer_position, 0)
        for position in early_exit_positions:
            surrounding = runner[max(0, position - 160) : position + 40]
            self.assertIn("writeReceiptAndExit", surrounding)

    def test_failure_round_trip_preserves_observed_counts(self) -> None:
        runner = self.source(RUNNER)
        for key in (
            "tests_succeeded",
            "tests_failed",
            "tests_not_evaluated",
        ):
            expected = (
                f'Lookup[roundTrip, "{key}", -1] ===\n'
                f'      Lookup[safeReceipt, "{key}", -2]'
            )
            self.assertIn(expected, runner)
        self.assertNotIn(
            'Lookup[roundTrip, "tests_succeeded", -1] === '
            "expectedTestCount",
            runner,
        )

    def test_native_admission_uses_exact_named_test_set(self) -> None:
        runner = self.source(RUNNER)
        for key in (
            "required_test_ids",
            "observed_test_ids",
            "failed_test_ids",
            "not_evaluated_test_ids",
            "required_test_id_hash",
        ):
            self.assertIn(key, runner)
        self.assertIn("BG02-XTENSOR-PROJECTION-DERIVATION", runner)

    def test_auxiliary_cas_cannot_prevent_native_receipt(self) -> None:
        native_shell = ROOT / "scripts/run_bg02_native_xact_diagnostic_local.sh"
        auxiliary_shell = ROOT / "scripts/run_bg02_auxiliary_cas_audit_local.sh"
        self.assertTrue(native_shell.is_file(), native_shell)
        self.assertTrue(auxiliary_shell.is_file(), auxiliary_shell)
        native = self.source(native_shell)
        for token in ("sage", "Singular", "octave", "lean", "lake"):
            self.assertNotIn(token, native)
        self.assertIn("BG_02_EINSTEIN_PROJECTION_WOLFRAM_RECEIPT.json", native)


if __name__ == "__main__":
    unittest.main()
