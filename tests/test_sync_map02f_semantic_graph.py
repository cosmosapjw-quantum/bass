from __future__ import annotations

import copy
import unittest

from scripts.verify_sync_map02f_semantic_graph import GRAPH_PATH, load_json, validate_graph


class SyncMap02FSemanticGraphTests(unittest.TestCase):
    def setUp(self) -> None:
        self.graph = load_json(GRAPH_PATH)

    def assertRejected(self, graph, fragment: str) -> None:
        errors = validate_graph(graph)
        self.assertTrue(errors, "hostile mutation unexpectedly escaped")
        self.assertTrue(
            any(fragment in error for error in errors),
            f"expected rejection containing {fragment!r}; got {errors!r}",
        )

    def test_exact_graph_passes(self) -> None:
        self.assertEqual(validate_graph(self.graph), [])

    def test_duplicate_formula_id_is_rejected(self) -> None:
        mutant = copy.deepcopy(self.graph)
        mutant["authority_formulas"][1]["formula_id"] = mutant["authority_formulas"][0]["formula_id"]
        self.assertRejected(mutant, "authority formula ID set")

    def test_compound_or_foreign_owner_is_rejected(self) -> None:
        mutant = copy.deepcopy(self.graph)
        mutant["authority_formulas"][0]["owner"] = ["bass", "htt_base"]
        self.assertRejected(mutant, "non-BASS or compound authority owner")

    def test_semantic_hash_drift_is_rejected(self) -> None:
        mutant = copy.deepcopy(self.graph)
        mutant["authority_formulas"][0]["semantic_hash"] = "0" * 64
        self.assertRejected(mutant, "semantic hash mismatch")

    def test_direction_convention_drift_is_rejected(self) -> None:
        mutant = copy.deepcopy(self.graph)
        mutant["convention_contract"]["outward_sky_direction"] = "n_sky=e"
        self.assertRejected(mutant, "convention mismatch")

    def test_receipt_head_cannot_replace_tested_payload(self) -> None:
        mutant = copy.deepcopy(self.graph)
        mutant["exact_inputs"]["sync_map_02e"]["tested_formula_payload_commit"] = mutant["exact_inputs"]["sync_map_02e"]["append_only_receipt_head"]
        self.assertRejected(mutant, "tested formula payload")

    def test_missing_consumer_relation_is_rejected(self) -> None:
        mutant = copy.deepcopy(self.graph)
        mutant["consumer_relations"].pop()
        self.assertRejected(mutant, "ten unique records")

    def test_missing_source_blob_is_rejected(self) -> None:
        mutant = copy.deepcopy(self.graph)
        mutant["consumer_relations"][0]["source_blob"] = "missing"
        self.assertRejected(mutant, "invalid exact source pin")

    def test_independent_oracle_cannot_gain_authority(self) -> None:
        mutant = copy.deepcopy(self.graph)
        relation = next(item for item in mutant["consumer_relations"] if item["relation_class"] == "INDEPENDENT_ORACLE")
        relation["authority_effect"] = "AUTHORITATIVE_DERIVATION"
        self.assertRejected(mutant, "oracle has authority effect")

    def test_rec_rate_adapter_is_required(self) -> None:
        mutant = copy.deepcopy(self.graph)
        relation = next(item for item in mutant["consumer_relations"] if item["relation_id"] == "02F-REC-ENERGY-DRIFT")
        relation["adapter"] = "R_t=R_ell"
        self.assertRejected(mutant, "REC energy-drift rate adapter missing")

    def test_rei_direction_flow_cannot_be_promoted(self) -> None:
        mutant = copy.deepcopy(self.graph)
        relation = next(item for item in mutant["consumer_relations"] if item["relation_id"] == "02F-REI-DIRECTION-FLOW")
        relation["relation_class"] = "SEMANTIC_EQUIVALENT_IDENTITY_CHART"
        relation["source_symbol"] = "invented_direction_flow"
        self.assertRejected(mutant, "REI direction flow must remain absent")

    def test_rei_h_only_redshift_cannot_be_promoted(self) -> None:
        mutant = copy.deepcopy(self.graph)
        relation = next(item for item in mutant["consumer_relations"] if item["relation_id"] == "02F-REI-ENERGY-DRIFT")
        relation["relation_class"] = "SEMANTIC_EQUIVALENT_IDENTITY_CHART"
        self.assertRejected(mutant, "REI H-only redshift was promoted")

    def test_htt_blackbody_domain_must_remain_strict(self) -> None:
        mutant = copy.deepcopy(self.graph)
        relation = next(item for item in mutant["consumer_relations"] if item["relation_id"] == "02F-HTT-BLACKBODY-T")
        relation["adapter"] = "all frequency-dependent observables"
        self.assertRejected(mutant, "HTT blackbody-temperature domain restriction missing")

    def test_missing_02e_to_02f_edge_is_rejected(self) -> None:
        mutant = copy.deepcopy(self.graph)
        mutant["dag"]["edges"].remove(["SYNC_MAP_02E_SHARED_EXPORT", "SYNC_MAP_02F_SEMANTIC_GRAPH"])
        self.assertRejected(mutant, "twelve unique edges")

    def test_cycle_is_rejected(self) -> None:
        mutant = copy.deepcopy(self.graph)
        mutant["dag"]["edges"][-1] = ["SYNC_GATE_01", "SYNC_MAP_02A_BASS"]
        self.assertRejected(mutant, "not closed and acyclic")


if __name__ == "__main__":
    unittest.main()
