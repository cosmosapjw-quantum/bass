from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from scripts.verify_sync_map02f_r2a_role_graph import verify

ROOT = Path(__file__).resolve().parents[1]
GRAPH = (
    ROOT
    / "docs"
    / "bass_master_ssot_v2"
    / "SYNC_MAP_02F_R2A"
    / "FORMULA_CONSUMER_ROLE_GRAPH.json"
)
VERIFIER = ROOT / "scripts" / "verify_sync_map02f_r2a_role_graph.py"
SHELL_RUNNER = ROOT / "scripts" / "run_sync_map02f_r2a_role_graph_local.sh"
WOLFRAM_MODULE = ROOT / "wolfram" / "BASS" / "Kernel" / "IR" / "FormulaConsumerRoleGraphR2A.wl"
WOLFRAM_TEST = ROOT / "wolfram" / "BASS" / "Tests" / "FormulaConsumerRoleGraphR2A.wlt"
WOLFRAM_RUNNER = ROOT / "wolfram" / "scripts" / "run_formula_consumer_role_graph_r2a.wls"


class FormulaConsumerRoleGraphR2ATests(unittest.TestCase):
    def data(self) -> dict:
        return json.loads(GRAPH.read_text(encoding="utf-8"))

    def test_required_surfaces_exist_and_clean_graph_passes(self) -> None:
        for path in (
            GRAPH,
            VERIFIER,
            SHELL_RUNNER,
            WOLFRAM_MODULE,
            WOLFRAM_TEST,
            WOLFRAM_RUNNER,
        ):
            self.assertTrue(path.is_file(), path)
        result = verify(self.data())
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["formula_consumer_pair_count"], 10)
        self.assertEqual(result["implementation_role_count"], 11)
        self.assertEqual(result["named_source_symbol_count"], 12)
        self.assertEqual(result["absent_implementation_slot_count"], 1)

    def test_pair_role_and_symbol_count_mutations_fail(self) -> None:
        for key in (
            "formula_consumer_pairs",
            "implementation_roles",
        ):
            mutant = self.data()
            mutant[key].pop()
            with self.assertRaises(ValueError):
                verify(mutant)

        # Exact per-role provenance pinning is intentionally checked before the
        # derived global symbol inventory.  Removing a symbol therefore fails
        # at the stronger role contract, rather than relying on diagnostic
        # precedence in a later aggregate-count check.
        mutant = self.data()
        mutant["implementation_roles"][0]["source_symbols"] = []
        with self.assertRaisesRegex(
            ValueError,
            "role contract mismatch for ROLE-REC-ABERRATION",
        ):
            verify(mutant)

        # The global symbol inventory is unchanged, but assigning symbols to
        # the wrong roles must still fail.
        mutant = self.data()
        roles = mutant["implementation_roles"]
        roles[0]["source_symbols"], roles[1]["source_symbols"] = (
            roles[1]["source_symbols"],
            roles[0]["source_symbols"],
        )
        with self.assertRaisesRegex(ValueError, "role contract"):
            verify(mutant)

    def test_absent_rei_direction_flow_cannot_be_promoted(self) -> None:
        mutant = self.data()
        role = next(
            row
            for row in mutant["implementation_roles"]
            if row["role_id"] == "ROLE-REI-DIRECTION-FLOW-ABSENT"
        )
        role["role_type"] = "CONSUMER_IMPLEMENTATION"
        role["source_symbols"] = ["invented_direction_flow"]
        role["implements_full_formula"] = True
        with self.assertRaises(ValueError):
            verify(mutant)

    def test_htt_blackbody_full_and_prepulled_roles_must_remain_split(self) -> None:
        mutant = self.data()
        mutant["implementation_roles"] = [
            row
            for row in mutant["implementation_roles"]
            if row["role_type"] != "PREPULLED_VALUE_PRIMITIVE"
        ]
        with self.assertRaises(ValueError):
            verify(mutant)

        # Promotion changes an exact pinned role field.  The canonical failure
        # is therefore the exact-role contract; the later derived
        # "primitive promoted" guard remains defence in depth but is not the
        # diagnostic authority for this mutation.
        mutant = self.data()
        primitive = next(
            row
            for row in mutant["implementation_roles"]
            if row["role_type"] == "PREPULLED_VALUE_PRIMITIVE"
        )
        primitive["implements_full_formula"] = True
        with self.assertRaisesRegex(
            ValueError,
            "role contract mismatch for ROLE-HTT-BLACKBODY-PREPULLED",
        ):
            verify(mutant)

    def test_rei_energy_residual_must_be_exact_sigmaee(self) -> None:
        mutant = self.data()
        pair = next(
            row
            for row in mutant["formula_consumer_pairs"]
            if row["pair_id"] == "02F-R2A-REI-ENERGY-DRIFT"
        )
        pair["exact_relation_residual"] = "((-H)-(-H-sigmaEE))!=0"
        with self.assertRaisesRegex(ValueError, "residual weakened"):
            verify(mutant)

    def test_legacy_ell_ray_parameter_is_rejected(self) -> None:
        mutant = self.data()
        mutant["convention_contract"]["ray_length_parameter"] = "ell with dimension L"
        with self.assertRaises(ValueError):
            verify(mutant)

    def test_overloaded_relation_class_is_rejected(self) -> None:
        mutant = self.data()
        mutant["formula_consumer_pairs"][0]["relation_class"] = "SEMANTIC_EQUIVALENT"
        with self.assertRaisesRegex(ValueError, "overloaded relation_class"):
            verify(mutant)

    def test_state_surface_and_formula_hash_mutations_fail(self) -> None:
        mutant = self.data()
        mutant["normal_ancestry"]["state_surface_registry_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "state-surface"):
            verify(mutant)

        mutant = self.data()
        mutant["authority_formulas"][0]["semantic_hash"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "semantic hash"):
            verify(mutant)

        mutant = self.data()
        htt_role = next(
            row
            for row in mutant["implementation_roles"]
            if row["role_id"] == "ROLE-HTT-BLACKBODY-FULL"
        )
        htt_role["source_commit"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "role contract"):
            verify(mutant)

    def test_state_registry_must_precede_role_graph(self) -> None:
        mutant = self.data()
        mutant["stage_dag"]["edges"] = [
            edge
            for edge in mutant["stage_dag"]["edges"]
            if edge != ["BASS_STATE_SURFACE_REGISTRY", "FORMULA_CONSUMER_ROLE_GRAPH"]
        ]
        with self.assertRaisesRegex(ValueError, "does not precede"):
            verify(mutant)


if __name__ == "__main__":
    unittest.main()
