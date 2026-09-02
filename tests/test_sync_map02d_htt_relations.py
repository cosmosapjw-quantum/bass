from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
VERIFIER_PATH = ROOT / "scripts" / "verify_sync_map02d_htt_relations.py"
SPEC = importlib.util.spec_from_file_location("verify_sync_map02d", VERIFIER_PATH)
assert SPEC is not None and SPEC.loader is not None
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)

HISTORICAL_ORACLE_PATH = "htt/obsstat/boost_biposh_residual.py"
REQUIRED_STF3_CHECKS = {
    "stf3_symmetric",
    "stf3_trace_free",
    "stf3_ambient_factor_matches",
    "stf3_unit_sphere_residual",
    "stf3_unit_sphere_domain_required",
}
REQUIRED_STF3_MUTATIONS = {
    "wrong_stf3_trace_coefficient_detected",
    "non_symmetric_stf3_detected",
    "missing_unit_sphere_domain_detected",
}


def canonical_data() -> dict[str, object]:
    return VERIFY.load_json(VERIFY.CLASSIFICATION)


class SyncMap02DHTTRelationsTests(unittest.TestCase):
    def test_canonical_contract_passes(self) -> None:
        result = VERIFY.verify(canonical_data())
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["relations"], 12)
        self.assertEqual(result["source_pins"], 9)
        self.assertEqual(result["pending_bass_imports"], 4)
        self.assertEqual(result["new_htt_shared_gaps"], 2)
        self.assertEqual(result["duplicate_authority_count"], 0)
        self.assertEqual(result["dag_nodes"], 10)
        self.assertEqual(result["dag_edges"], 12)

    def test_canonical_contract_exact_pins_historical_oracle(self) -> None:
        data = canonical_data()
        sources = data["exact_htt_sources"]
        self.assertIsInstance(sources, list)
        paths = {source["path"] for source in sources}
        self.assertIn(HISTORICAL_ORACLE_PATH, paths)

        relations = data["relations"]
        self.assertIsInstance(relations, list)
        parity = next(row for row in relations if row["relation_id"] == "HTT-R11")
        oracle_paths = parity.get("oracle_source_paths")
        self.assertEqual(
            oracle_paths,
            [
                "htt/obsstat/processed_boost_parity.py",
                HISTORICAL_ORACLE_PATH,
            ],
        )

    def test_rejects_missing_historical_oracle_pin(self) -> None:
        data = copy.deepcopy(canonical_data())
        sources = data["exact_htt_sources"]
        self.assertIsInstance(sources, list)
        data["exact_htt_sources"] = [
            source for source in sources if source["path"] != HISTORICAL_ORACLE_PATH
        ]
        with self.assertRaisesRegex(
            VERIFY.VerificationError,
            "historical fixed-axis oracle pin is missing",
        ):
            VERIFY.verify(data)

    def test_rejects_mutated_historical_oracle_digest(self) -> None:
        data = copy.deepcopy(canonical_data())
        sources = data["exact_htt_sources"]
        self.assertIsInstance(sources, list)
        historical = next(
            source for source in sources if source["path"] == HISTORICAL_ORACLE_PATH
        )
        historical["git_blob_sha1"] = "0" * 40
        with self.assertRaisesRegex(
            VERIFY.VerificationError,
            "historical fixed-axis oracle digest drifted",
        ):
            VERIFY.verify(data)

    def test_canonical_contract_contains_explicit_stf3_obligations(self) -> None:
        data = canonical_data()
        corrected = data["wolfram_exact_checks"]["corrected_run"]
        structural = corrected["structural_checks"]
        mutations = data["wolfram_exact_checks"]["hostile_mutations"]
        self.assertLessEqual(REQUIRED_STF3_CHECKS, set(structural))
        self.assertLessEqual(REQUIRED_STF3_MUTATIONS, set(mutations))

    def test_rejects_failed_stf3_trace_proof(self) -> None:
        data = copy.deepcopy(canonical_data())
        corrected = data["wolfram_exact_checks"]["corrected_run"]
        corrected["structural_checks"]["stf3_trace_free"] = False
        with self.assertRaisesRegex(
            VERIFY.VerificationError,
            "explicit STF3 proof failed",
        ):
            VERIFY.verify(data)

    def test_rejects_missing_unit_sphere_domain_guard(self) -> None:
        data = copy.deepcopy(canonical_data())
        mutations = data["wolfram_exact_checks"]["hostile_mutations"]
        mutations["missing_unit_sphere_domain_detected"] = False
        with self.assertRaisesRegex(
            VERIFY.VerificationError,
            "STF3 hostile mutation escaped detection",
        ):
            VERIFY.verify(data)

    def test_rejects_missing_htt_prerequisite(self) -> None:
        data = copy.deepcopy(canonical_data())
        impact = data["impact_dag"]
        self.assertIsInstance(impact, dict)
        impact["edges"] = [
            edge
            for edge in impact["edges"]
            if edge != ["02D_HTT", "02E_SHARED_EXPORT"]
        ]
        with self.assertRaisesRegex(
            VERIFY.VerificationError,
            "lacks HTT relation prerequisite",
        ):
            VERIFY.verify(data)

    def test_rejects_global_tilt_reclassification(self) -> None:
        data = copy.deepcopy(canonical_data())
        firewall = data["semantic_firewall"]
        self.assertIsInstance(firewall, dict)
        firewall["global_matter_frame_tilt"] = "IMPLEMENTED"
        with self.assertRaisesRegex(
            VERIFY.VerificationError,
            "must not own global tilt",
        ):
            VERIFY.verify(data)

    def test_rejects_duplicate_formula_authority(self) -> None:
        data = copy.deepcopy(canonical_data())
        relations = data["relations"]
        self.assertIsInstance(relations, list)
        relations[1]["formula_id"] = relations[0]["formula_id"]
        with self.assertRaisesRegex(
            VERIFY.VerificationError,
            "formula IDs are not unique",
        ):
            VERIFY.verify(data)

    def test_rejects_silent_empirical_beta_promotion(self) -> None:
        data = copy.deepcopy(canonical_data())
        firewall = data["semantic_firewall"]
        self.assertIsInstance(firewall, dict)
        firewall["empirical_beta_fit"] = "IMPLEMENTED"
        with self.assertRaisesRegex(
            VERIFY.VerificationError,
            "empirical beta was silently promoted",
        ):
            VERIFY.verify(data)


if __name__ == "__main__":
    unittest.main()
