from __future__ import annotations

import copy
import unittest

from scripts.verify_sync_map02e_shared_export import (
    EXPECTED_FORMULA_IDS,
    EXPORT_PATH,
    ValidationError,
    load_export,
    validate_export,
)


class SyncMap02ESharedExportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.export = load_export(EXPORT_PATH)

    def assert_rejected(self, candidate: dict, fragment: str) -> None:
        with self.assertRaisesRegex(ValidationError, fragment):
            validate_export(candidate)

    def test_canonical_export_passes(self) -> None:
        report = validate_export(self.export)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["formula_count"], 6)
        self.assertEqual(report["internal_dependency_edges"], 4)
        self.assertEqual(report["external_dependency_edges"], 3)

    def test_exact_union_has_six_formula_ids(self) -> None:
        actual = {item["formula_id"] for item in self.export["formulas"]}
        self.assertEqual(actual, EXPECTED_FORMULA_IDS)

    def test_rejects_stale_htt_pre_repair_pin(self) -> None:
        candidate = copy.deepcopy(self.export)
        candidate["predecessors"]["sync_map_02d"]["commit"] = (
            "06aa29f78c26bcafeb60d85b719a4d3aa5c4c2e8"
        )
        self.assert_rejected(candidate, "stale HTT predecessor")

    def test_rejects_stale_four_formula_union(self) -> None:
        candidate = copy.deepcopy(self.export)
        candidate["formulas"] = candidate["formulas"][:4]
        self.assert_rejected(candidate, "six-formula union")

    def test_rejects_wrong_doppler_sign(self) -> None:
        candidate = copy.deepcopy(self.export)
        formula = next(item for item in candidate["formulas"] if item["formula_id"] == "BASS.FRAME.DOPPLER_FACTOR.001")
        formula["equation_ir"]["terms"][0]["input"] = "gamma*(1-beta_dot_n_sky)"
        self.assert_rejected(candidate, "Doppler signature")

    def test_rejects_wrong_solid_angle_power(self) -> None:
        candidate = copy.deepcopy(self.export)
        formula = next(item for item in candidate["formulas"] if item["formula_id"] == "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001")
        formula["equation_ir"]["terms"][0]["input"] = "doppler_factor^(-1)*dOmega"
        self.assert_rejected(candidate, "solid-angle signature")

    def test_rejects_wrong_blackbody_temperature_weight(self) -> None:
        candidate = copy.deepcopy(self.export)
        formula = next(item for item in candidate["formulas"] if item["formula_id"] == "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001")
        formula["equation_ir"]["terms"][0]["input"] = "doppler_factor^(-1)*temperature(n_sky)"
        self.assert_rejected(candidate, "temperature-pullback signature")

    def test_rejects_wrong_energy_drift_shear_sign(self) -> None:
        candidate = copy.deepcopy(self.export)
        formula = next(item for item in candidate["formulas"] if item["formula_id"] == "BASS.PHOTON.ENERGY_DRIFT.001")
        formula["equation_ir"]["terms"][1]["coefficient"] = {"type": "integer", "value": 1}
        self.assert_rejected(candidate, "energy-drift signature")

    def test_rejects_direction_flow_without_radial_compensator(self) -> None:
        candidate = copy.deepcopy(self.export)
        formula = next(item for item in candidate["formulas"] if item["formula_id"] == "BASS.PHOTON.DIRECTION_FLOW.001")
        formula["equation_ir"]["terms"] = formula["equation_ir"]["terms"][1:]
        self.assert_rejected(candidate, "direction-flow signature")

    def test_rejects_forbidden_scope_injection(self) -> None:
        candidate = copy.deepcopy(self.export)
        candidate["coverage"]["included"].append("finite electron tilt collision")
        self.assert_rejected(candidate, "scope firewall")

    def test_rejects_missing_external_dependency(self) -> None:
        candidate = copy.deepcopy(self.export)
        candidate["external_dependency_edges"] = candidate["external_dependency_edges"][:-1]
        self.assert_rejected(candidate, "external dependency")

    def test_rejects_semantic_hash_drift(self) -> None:
        candidate = copy.deepcopy(self.export)
        candidate["formulas"][0]["semantic_hash"] = "0" * 64
        self.assert_rejected(candidate, "semantic hash")

    def test_dependency_graph_is_acyclic(self) -> None:
        candidate = copy.deepcopy(self.export)
        candidate["internal_dependency_edges"].append({
            "from": "BASS.FRAME.DOPPLER_FACTOR.001",
            "to": "BASS.FRAME.ABERRATED_DIRECTION.001",
            "relation": "depends_on",
        })
        self.assert_rejected(candidate, "cycle")


if __name__ == "__main__":
    unittest.main()
