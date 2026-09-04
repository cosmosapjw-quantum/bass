from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path
from types import ModuleType
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
GRAPH = (
    ROOT
    / "docs"
    / "bass_master_ssot_v2"
    / "SYNC_MAP_02F_R3"
    / "CONSUMER_BINDING_CONTRACTS.json"
)
VERIFIER = ROOT / "scripts" / "verify_sync_map02f_r3_consumer_bindings.py"
SHELL_RUNNER = ROOT / "scripts" / "run_sync_map02f_r3_consumer_bindings_local.sh"
WOLFRAM_MODULE = (
    ROOT / "wolfram" / "BASS" / "Kernel" / "IR" / "ConsumerBindingContractsR3.wl"
)
WOLFRAM_TEST = ROOT / "wolfram" / "BASS" / "Tests" / "ConsumerBindingContractsR3.wlt"
WOLFRAM_RUNNER = ROOT / "wolfram" / "scripts" / "run_consumer_binding_contracts_r3.wls"

EXPECTED_PAIR_IDS = [
    "02F-R2A-REC-ABERRATION",
    "02F-R2A-REC-DOPPLER",
    "02F-R2A-REC-DIRECTION-FLOW",
    "02F-R2A-REC-ENERGY-DRIFT",
    "02F-R2A-REI-DIRECTION-FLOW",
    "02F-R2A-REI-ENERGY-DRIFT",
    "02F-R2A-HTT-ABERRATION",
    "02F-R2A-HTT-DOPPLER",
    "02F-R2A-HTT-SOLID-ANGLE",
    "02F-R2A-HTT-BLACKBODY-T",
]
EXPECTED_ROLE_IDS = [
    "ROLE-REC-ABERRATION",
    "ROLE-REC-DOPPLER",
    "ROLE-REC-DIRECTION-FLOW",
    "ROLE-REC-ENERGY-DRIFT",
    "ROLE-REI-DIRECTION-FLOW-ABSENT",
    "ROLE-REI-ENERGY-DRIFT-CONTROL",
    "ROLE-HTT-ABERRATION-BIDIRECTIONAL",
    "ROLE-HTT-DOPPLER-BIDIRECTIONAL",
    "ROLE-HTT-SOLID-ANGLE-ORACLE",
    "ROLE-HTT-BLACKBODY-FULL",
    "ROLE-HTT-BLACKBODY-PREPULLED",
]


def load_verify() -> Callable[[dict[str, Any]], dict[str, Any]]:
    if not VERIFIER.is_file():
        raise AssertionError(f"consumer-binding verifier missing: {VERIFIER}")
    spec = importlib.util.spec_from_file_location("consumer_binding_verifier", VERIFIER)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load consumer-binding verifier")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    verify = getattr(module, "verify", None)
    if not callable(verify):
        raise AssertionError("consumer-binding verify function missing")
    return verify


class SyncMap02FR3ConsumerBindingTests(unittest.TestCase):
    def data(self) -> dict[str, Any]:
        self.assertTrue(GRAPH.is_file(), f"consumer-binding graph missing: {GRAPH}")
        return json.loads(GRAPH.read_text(encoding="utf-8"))

    def verify(self, data: dict[str, Any]) -> dict[str, Any]:
        return load_verify()(data)

    def test_required_surfaces_and_clean_contract_pass(self) -> None:
        for path in (
            GRAPH,
            VERIFIER,
            SHELL_RUNNER,
            WOLFRAM_MODULE,
            WOLFRAM_TEST,
            WOLFRAM_RUNNER,
        ):
            self.assertTrue(path.is_file(), path)

        result = self.verify(self.data())
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["consumer_count"], 3)
        self.assertEqual(result["binding_request_count"], 10)
        self.assertEqual(result["source_role_pin_count"], 11)
        self.assertEqual(result["named_source_symbol_count"], 12)
        self.assertEqual(result["absent_implementation_slot_count"], 1)
        self.assertEqual(result["formula_count"], 6)
        self.assertEqual(result["state_surface_count"], 6)
        self.assertEqual(result["certificate_family_count"], 4)
        self.assertEqual(result["blocked_promotion_count"], 13)

        wlt_text = WOLFRAM_TEST.read_text(encoding="utf-8")
        self.assertEqual(wlt_text.count("VerificationTest["), 18)
        self.assertNotIn("$InputFileName", wlt_text)
        self.assertNotIn("Get[", wlt_text)
        self.assertNotIn("Import[", wlt_text)

        runner_text = WOLFRAM_RUNNER.read_text(encoding="utf-8")
        self.assertIn("AssociationThread[Keys[value], jsonSafe /@ Values[value]]", runner_text)
        self.assertIn('receiptTemporaryPath = receiptPath <> ".tmp"', runner_text)
        self.assertIn('ExportString[receipt, "RawJSON"]', runner_text)
        self.assertIn('Import[receiptTemporaryPath, "RawJSON"]', runner_text)
        self.assertIn('"FAIL_RECEIPT_JSON_EXPORT"', runner_text)

    def test_parent_closeout_identity_is_exact_pinned(self) -> None:
        mutant = self.data()
        mutant["normal_ancestry"]["parent_commit"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "parent commit"):
            self.verify(mutant)

    def test_count_contract_mutations_fail(self) -> None:
        for key in (
            "consumers",
            "binding_requests",
            "source_role_pins",
            "named_source_symbols",
            "absent_implementation_slots",
            "owner_formulas",
            "state_surfaces",
            "certificate_families",
            "blocked_promotions",
        ):
            mutant = self.data()
            mutant["count_contract"][key] += 1
            with self.assertRaisesRegex(ValueError, "count contract"):
                self.verify(mutant)

    def test_binding_ids_and_pair_coverage_are_exact(self) -> None:
        data = self.data()
        self.assertEqual(
            [row["pair_id"] for row in data["binding_requests"]],
            EXPECTED_PAIR_IDS,
        )

        mutant = copy.deepcopy(data)
        mutant["binding_requests"].pop()
        with self.assertRaisesRegex(ValueError, "binding request"):
            self.verify(mutant)

        mutant = copy.deepcopy(data)
        mutant["binding_requests"][1]["pair_id"] = mutant["binding_requests"][0]["pair_id"]
        with self.assertRaisesRegex(ValueError, "binding request"):
            self.verify(mutant)

    def test_formula_semantic_hash_mutation_fails(self) -> None:
        mutant = self.data()
        mutant["formula_authority"]["formulas"][0]["semantic_hash"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "formula authority"):
            self.verify(mutant)

    def test_source_role_pin_mutation_fails(self) -> None:
        data = self.data()
        self.assertEqual(
            [row["role_id"] for row in data["source_role_pins"]],
            EXPECTED_ROLE_IDS,
        )

        mutant = copy.deepcopy(data)
        mutant["source_role_pins"][0]["source_commit"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "source role"):
            self.verify(mutant)

    def test_rei_absent_direction_flow_cannot_be_promoted(self) -> None:
        mutant = self.data()
        role = next(
            row
            for row in mutant["source_role_pins"]
            if row["role_id"] == "ROLE-REI-DIRECTION-FLOW-ABSENT"
        )
        role["role_type"] = "CONSUMER_IMPLEMENTATION"
        role["implements_full_formula"] = True
        role["source_symbols"] = ["generic_direction_flow"]
        with self.assertRaisesRegex(ValueError, "REI absent"):
            self.verify(mutant)

    def test_htt_full_and_prepulled_blackbody_roles_remain_distinct(self) -> None:
        mutant = self.data()
        prepulled = next(
            row
            for row in mutant["source_role_pins"]
            if row["role_id"] == "ROLE-HTT-BLACKBODY-PREPULLED"
        )
        prepulled["implements_full_formula"] = True
        prepulled["role_type"] = "FULL_FIELD_PULLBACK"
        with self.assertRaisesRegex(ValueError, "HTT blackbody"):
            self.verify(mutant)

    def test_state_surface_and_certificate_requirements_cannot_be_weakened(self) -> None:
        mutant = self.data()
        rec_direction = next(
            row
            for row in mutant["binding_requests"]
            if row["pair_id"] == "02F-R2A-REC-DIRECTION-FLOW"
        )
        rec_direction["conditional_certificate_families"] = []
        with self.assertRaisesRegex(ValueError, "binding request"):
            self.verify(mutant)

        mutant = self.data()
        mutant["state_surface_policy"]["j_and_g_generic_binding"] = "ADMITTED"
        with self.assertRaisesRegex(ValueError, "state-surface"):
            self.verify(mutant)

    def test_cross_repository_runtime_provider_science_firewalls(self) -> None:
        for key in (
            "consumer_source_mutation_authorized",
            "runtime_parity_admitted",
            "provider_promotion_authorized",
            "science_promotion_authorized",
            "merge_or_ready_transition_authorized",
            "formula_occurrence_implies_runtime_parity",
            "source_role_pin_implies_runtime_parity",
            "certificate_schema_implies_runtime_certificate",
        ):
            mutant = self.data()
            mutant["authorization_firewall"][key] = True
            with self.assertRaisesRegex(ValueError, "authorization firewall"):
                self.verify(mutant)

    def test_stage_dag_mutations_fail(self) -> None:
        mutant = self.data()
        mutant["stage_dag"]["edges"].pop()
        with self.assertRaisesRegex(ValueError, "DAG"):
            self.verify(mutant)

        mutant = self.data()
        mutant["stage_dag"]["edges"].append(
            ["CROSS_REPOSITORY_PARITY_FEDERATION", "BOUNDED_SEMANTIC_CLOSEOUT"]
        )
        with self.assertRaises(ValueError):
            self.verify(mutant)

    def test_literature_has_no_project_authority(self) -> None:
        mutant = self.data()
        mutant["literature_regression"][0]["authority_effect"] = "FORMULA_OWNER"
        with self.assertRaisesRegex(ValueError, "literature authority"):
            self.verify(mutant)


if __name__ == "__main__":
    unittest.main()
