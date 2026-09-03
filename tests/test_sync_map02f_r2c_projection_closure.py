from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from scripts.verify_sync_map02f_r2c_projection_closure import verify

ROOT = Path(__file__).resolve().parents[1]
GRAPH = (
    ROOT
    / "docs"
    / "bass_master_ssot_v2"
    / "SYNC_MAP_02F_R2C"
    / "PROJECTION_CLOSURE_CERTIFICATE_GRAPH.json"
)
VERIFIER = ROOT / "scripts" / "verify_sync_map02f_r2c_projection_closure.py"
SHELL_RUNNER = ROOT / "scripts" / "run_sync_map02f_r2c_projection_closure_local.sh"
WOLFRAM_MODULE = (
    ROOT / "wolfram" / "BASS" / "Kernel" / "IR" / "ProjectionClosureCertificateGraphR2C.wl"
)
WOLFRAM_TEST = ROOT / "wolfram" / "BASS" / "Tests" / "ProjectionClosureCertificateGraphR2C.wlt"
WOLFRAM_RUNNER = ROOT / "wolfram" / "scripts" / "run_projection_closure_certificate_graph_r2c.wls"


class ProjectionClosureCertificateGraphR2CTests(unittest.TestCase):
    def data(self) -> dict:
        return json.loads(GRAPH.read_text(encoding="utf-8"))

    def test_required_surfaces_and_clean_graph_pass(self) -> None:
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
        self.assertEqual(result["certificate_family_count"], 4)
        self.assertEqual(result["relation_certificate_count"], 6)
        self.assertEqual(result["exact_witness_count"], 6)
        self.assertEqual(result["blocked_promotion_count"], 3)

        runner_text = WOLFRAM_RUNNER.read_text(encoding="utf-8")
        self.assertIn('receiptTemporaryPath = receiptPath <> ".tmp"', runner_text)
        self.assertIn('ExportString[receipt, "RawJSON"]', runner_text)
        self.assertIn('Import[receiptTemporaryPath, "RawJSON"]', runner_text)
        self.assertIn('"FAIL_RECEIPT_JSON_EXPORT"', runner_text)

    def test_normal_ancestry_is_exact_pinned(self) -> None:
        for key in (
            "parent_commit",
            "native_role_graph_source_head",
            "role_graph_sha256",
            "role_graph_wolfram_receipt_sha256",
            "state_surface_registry_sha256",
            "hardened_formula_registry_semantic_hash",
        ):
            mutant = self.data()
            mutant["normal_ancestry"][key] = "0" * 64
            with self.assertRaises(ValueError):
                verify(mutant)

    def test_count_family_and_obligation_mutations_fail(self) -> None:
        mutant = self.data()
        mutant["count_contract"]["certificate_families"] = 3
        with self.assertRaisesRegex(ValueError, "count contract"):
            verify(mutant)

        mutant = self.data()
        mutant["certificate_families"].pop()
        with self.assertRaisesRegex(ValueError, "family inventory"):
            verify(mutant)

        mutant = self.data()
        mutant["certificate_families"][0]["required_fields"] = []
        with self.assertRaisesRegex(ValueError, "empty obligations"):
            verify(mutant)

    def test_noninvertible_relations_cannot_be_promoted(self) -> None:
        for relation_id in ("PSTF_TO_J", "GRID_TO_G"):
            mutant = self.data()
            row = next(
                item
                for item in mutant["relation_certificates"]
                if item["relation_id"] == relation_id
            )
            row["invertibility_claim"] = "EXACT_EQUIVALENCE"
            with self.assertRaises(ValueError):
                verify(mutant)

        mutant = self.data()
        row = next(
            item
            for item in mutant["relation_certificates"]
            if item["relation_id"] == "SCALAR_TO_POLARIZED_PROHIBITED"
        )
        row["direction"] = "IMPLICIT_PROMOTION"
        with self.assertRaisesRegex(ValueError, "relation contract"):
            verify(mutant)

    def test_rank_and_aliasing_policy_cannot_be_weakened(self) -> None:
        mutant = self.data()
        mutant["rank_and_aliasing_policy"][
            "radial_polynomial_product_sufficient_condition"
        ] = "radial_work_order >= radial_output_order"
        with self.assertRaisesRegex(ValueError, "radial anti-aliasing"):
            verify(mutant)

        mutant = self.data()
        mutant["rank_and_aliasing_policy"][
            "angular_harmonic_product_sufficient_condition"
        ] = "angular_work_rank >= angular_output_rank"
        with self.assertRaisesRegex(ValueError, "angular anti-aliasing"):
            verify(mutant)

        mutant = self.data()
        mutant["rank_and_aliasing_policy"]["hardcoded_numeric_ell_cutoff_forbidden"] = False
        with self.assertRaisesRegex(ValueError, "ell hardcode"):
            verify(mutant)

    def test_roundtrip_and_radial_witnesses_are_exact_pinned(self) -> None:
        mutant = self.data()
        row = next(
            item
            for item in mutant["exact_witnesses"]
            if item["witness_id"] == "GAUSS_LEGENDRE_L2_ROUNDTRIP"
        )
        row["expected_analysis_residuals"] = [0, 0, 1]
        with self.assertRaisesRegex(ValueError, "analysis residual"):
            verify(mutant)

        mutant = self.data()
        row = next(
            item
            for item in mutant["exact_witnesses"]
            if item["witness_id"] == "RADIAL_MULTIPLICATION_WORK_ORDER"
        )
        row["minimum_radial_work_order"] = 1
        with self.assertRaisesRegex(ValueError, "radial work order"):
            verify(mutant)

    def test_g_closure_and_four_force_witnesses_are_pinned(self) -> None:
        mutant = self.data()
        row = next(
            item
            for item in mutant["exact_witnesses"]
            if item["witness_id"] == "G_TWO_BIN_FREQUENCY_CLOSURE_NOGO"
        )
        row["generic_scalar_closure"] = True
        with self.assertRaisesRegex(ValueError, "G closure"):
            verify(mutant)

        mutant = self.data()
        row = next(
            item
            for item in mutant["exact_witnesses"]
            if item["witness_id"] == "RADIATION_MATTER_FOUR_FORCE_CANCELLATION"
        )
        row["expected_total_residual"] = [1, 0, 0, 0]
        with self.assertRaisesRegex(ValueError, "four-force"):
            verify(mutant)

    def test_screen_and_polarization_witnesses_are_pinned(self) -> None:
        mutant = self.data()
        row = next(
            item
            for item in mutant["exact_witnesses"]
            if item["witness_id"] == "SCREEN_PROJECTOR_RATIONAL_DIRECTION"
        )
        row["expected_trace"] = 3
        with self.assertRaisesRegex(ValueError, "screen trace"):
            verify(mutant)

        mutant = self.data()
        row = next(
            item
            for item in mutant["exact_witnesses"]
            if item["witness_id"] == "SCALAR_INTENSITY_DOES_NOT_FIX_POLARIZATION"
        )
        row["frobenius_difference_squared"] = 0
        with self.assertRaisesRegex(ValueError, "polarization witness"):
            verify(mutant)

    def test_dag_and_literature_authority_firewalls(self) -> None:
        mutant = self.data()
        mutant["stage_dag"]["edges"] = [
            edge
            for edge in mutant["stage_dag"]["edges"]
            if edge
            != [
                "FORMULA_CONSUMER_ROLE_GRAPH",
                "PROJECTION_CLOSURE_CERTIFICATE_GRAPH",
            ]
        ]
        with self.assertRaisesRegex(ValueError, "R2A does not precede"):
            verify(mutant)

        mutant = self.data()
        mutant["literature_regression"][0]["authority_effect"] = "OVERRIDE"
        with self.assertRaisesRegex(ValueError, "literature"):
            verify(mutant)


if __name__ == "__main__":
    unittest.main()
