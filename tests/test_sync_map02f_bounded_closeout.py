from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from scripts.verify_sync_map02f_bounded_closeout import verify

ROOT = Path(__file__).resolve().parents[1]
GRAPH = (
    ROOT
    / "docs"
    / "bass_master_ssot_v2"
    / "SYNC_MAP_02F_CLOSEOUT"
    / "BOUNDED_SEMANTIC_CLOSEOUT.json"
)
VERIFIER = ROOT / "scripts" / "verify_sync_map02f_bounded_closeout.py"
SHELL_RUNNER = ROOT / "scripts" / "run_sync_map02f_bounded_closeout_local.sh"
WOLFRAM_MODULE = (
    ROOT / "wolfram" / "BASS" / "Kernel" / "IR" / "BoundedSemanticCloseout.wl"
)
WOLFRAM_TEST = (
    ROOT / "wolfram" / "BASS" / "Tests" / "BoundedSemanticCloseout.wlt"
)
WOLFRAM_RUNNER = ROOT / "wolfram" / "scripts" / "run_bounded_semantic_closeout.wls"


class SyncMap02FBoundedCloseoutTests(unittest.TestCase):
    def data(self) -> dict:
        return json.loads(GRAPH.read_text(encoding="utf-8"))

    def test_required_surfaces_and_clean_closeout_pass(self) -> None:
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
        self.assertEqual(result["upstream_stage_count"], 4)
        self.assertEqual(result["formula_count"], 6)
        self.assertEqual(result["state_surface_count"], 6)
        self.assertEqual(result["formula_consumer_pair_count"], 10)
        self.assertEqual(result["implementation_role_count"], 11)
        self.assertEqual(result["certificate_family_count"], 4)
        self.assertEqual(result["relation_certificate_count"], 6)
        self.assertEqual(result["blocked_promotion_count"], 13)

        wlt_text = WOLFRAM_TEST.read_text(encoding="utf-8")
        self.assertEqual(wlt_text.count("VerificationTest["), 17)
        self.assertNotIn("$InputFileName", wlt_text)
        self.assertNotIn("Get[", wlt_text)
        self.assertNotIn("Import[", wlt_text)

        runner_text = WOLFRAM_RUNNER.read_text(encoding="utf-8")
        self.assertIn("AssociationThread[Keys[value], jsonSafe /@ Values[value]]", runner_text)
        self.assertIn('receiptTemporaryPath = receiptPath <> ".tmp"', runner_text)
        self.assertIn('ExportString[receipt, "RawJSON"]', runner_text)
        self.assertIn('Import[receiptTemporaryPath, "RawJSON"]', runner_text)
        self.assertIn('"FAIL_RECEIPT_JSON_EXPORT"', runner_text)

    def test_parent_commit_is_exact_pinned(self) -> None:
        mutant = self.data()
        mutant["normal_ancestry"]["parent_commit"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "parent commit"):
            verify(mutant)

    def test_upstream_stage_identity_mutations_fail(self) -> None:
        mutant = self.data()
        mutant["normal_ancestry"]["stages"][0]["primary_identity"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "upstream stage identity"):
            verify(mutant)

        mutant = self.data()
        mutant["normal_ancestry"]["stages"][3]["native_gate"] = "PASS_UNVERIFIED"
        with self.assertRaisesRegex(ValueError, "upstream stage identity"):
            verify(mutant)

    def test_count_contract_mutations_fail(self) -> None:
        for key in (
            "authority_formulas",
            "state_surfaces",
            "formula_consumer_pairs",
            "implementation_role_rows",
            "named_source_symbols",
            "explicit_absent_implementation_slots",
            "certificate_families",
            "relation_certificate_rows",
            "exact_witnesses",
            "blocked_promotions",
        ):
            mutant = self.data()
            mutant["count_contract"][key] += 1
            with self.assertRaisesRegex(ValueError, "count contract"):
                verify(mutant)

    def test_stage_dag_mutations_fail(self) -> None:
        mutant = self.data()
        mutant["stage_dag"]["edges"].pop()
        with self.assertRaisesRegex(ValueError, "DAG edge"):
            verify(mutant)

        mutant = self.data()
        mutant["stage_dag"]["edges"][-1] = [
            "BOUNDED_SEMANTIC_CLOSEOUT",
            "OWNER_FORMULA_HARDENING",
        ]
        with self.assertRaises(ValueError):
            verify(mutant)

    def test_bounded_claims_cannot_be_promoted_to_runtime(self) -> None:
        mutant = self.data()
        mutant["bounded_claims"]["formula_consumer_role_semantics"] = "PASS_RUNTIME"
        with self.assertRaisesRegex(ValueError, "bounded claim"):
            verify(mutant)

    def test_promotion_firewall_cannot_be_weakened(self) -> None:
        mutant = self.data()
        mutant["promotion_firewall"].remove("SCREEN_BASIS_TRANSPORT_IMPLEMENTED")
        mutant["count_contract"]["blocked_promotions"] -= 1
        with self.assertRaises(ValueError):
            verify(mutant)

        mutant = self.data()
        mutant["promotion_status"] = "PARTIAL_RELEASE"
        with self.assertRaisesRegex(ValueError, "promotion status"):
            verify(mutant)

    def test_consumer_binding_is_not_part_of_bounded_closeout(self) -> None:
        mutant = self.data()
        mutant["consumer_bindings"] = [{"consumer": "rec_bianchi"}]
        with self.assertRaisesRegex(ValueError, "consumer bindings"):
            verify(mutant)

        mutant = self.data()
        mutant["consumer_binding_policy"][
            "runtime_parity_inferred_from_formula_occurrence"
        ] = True
        with self.assertRaisesRegex(ValueError, "runtime parity"):
            verify(mutant)

    def test_cross_repository_source_mutation_remains_forbidden(self) -> None:
        mutant = self.data()
        mutant["consumer_binding_policy"]["consumer_source_mutation_authorized"] = True
        with self.assertRaisesRegex(ValueError, "cross-repository"):
            verify(mutant)

    def test_literature_has_no_project_authority(self) -> None:
        mutant = self.data()
        mutant["literature_regression"]["authority_effect"] = "FORMULA_OWNER"
        with self.assertRaisesRegex(ValueError, "literature authority"):
            verify(mutant)


if __name__ == "__main__":
    unittest.main()
