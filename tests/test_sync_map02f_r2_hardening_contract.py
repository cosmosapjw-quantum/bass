from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GRAPH_PATH = ROOT / "docs/bass_master_ssot_v2/SYNC_MAP_02F/CROSS_REPOSITORY_SEMANTIC_GRAPH.json"
RUNNER_PATH = ROOT / "wolfram/scripts/run_sync_map02f_source_packet.wls"
WLT_PATH = ROOT / "wolfram/BASS/Tests/SYNCMAP02FCrossRepositorySemanticGraph.wlt"
RECEIPT_FIX_PATH = ROOT / "wolfram/BASS/Kernel/IR/CrossRepositorySemanticGraphReceiptFix1.wl"


class SyncMap02FR2HardeningContractTests(unittest.TestCase):
    """Fail-closed RED contract for the post-audit SYNC-MAP-02F R2 graph.

    The tests intentionally separate formula-consumer pairs, implementation
    roles, and source symbols. They also require exact residual coefficients
    and a source-packet runner that cannot report PASS when zero tests were
    discovered.
    """

    def setUp(self) -> None:
        self.graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
        self.relations = self.graph["consumer_relations"]
        self.runner = RUNNER_PATH.read_text(encoding="utf-8")
        self.wlt = WLT_PATH.read_text(encoding="utf-8")
        self.receipt_fix = RECEIPT_FIX_PATH.read_text(encoding="utf-8")

    def test_ray_parameter_is_s_and_ell_is_reserved_for_multipoles(self) -> None:
        convention = self.graph["convention_contract"]
        self.assertEqual(convention.get("ray_length_parameter"), "s=ct")
        self.assertEqual(convention.get("time_adapter"), "s=c*t")
        self.assertEqual(
            convention.get("rec_rate_adapter"),
            "R_t=c*R_s and V_t=c*V_s",
        )
        joined = json.dumps(convention, sort_keys=True)
        self.assertNotRegex(joined, r"R_ell|V_ell|ell=c\*t")

    def test_pair_role_and_symbol_layers_have_exact_counts(self) -> None:
        pair_keys = {
            (row["formula_id"], row["consumer_repository"])
            for row in self.relations
        }
        role_keys = {
            (
                row["formula_id"],
                row["consumer_repository"],
                row.get("implementation_role"),
            )
            for row in self.relations
        }
        symbols: list[str] = []
        absent = 0
        for row in self.relations:
            source_symbols = row.get("source_symbols")
            if isinstance(source_symbols, list):
                symbols.extend(str(item) for item in source_symbols)
            elif row.get("source_symbol"):
                symbols.extend(
                    part.strip()
                    for part in str(row["source_symbol"]).split(";")
                    if part.strip()
                )
            else:
                absent += 1
        self.assertEqual(len(pair_keys), 10)
        self.assertEqual(len(role_keys), 11)
        self.assertEqual(len(symbols), 12)
        self.assertEqual(absent, 1)

    def test_htt_blackbody_full_pullback_and_prepulled_primitive_are_split(self) -> None:
        rows = [
            row
            for row in self.relations
            if row["formula_id"]
            == "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001"
            and row["consumer_repository"] == "htt_base"
        ]
        self.assertEqual(len(rows), 2)
        by_role = {row["implementation_role"]: row for row in rows}
        self.assertEqual(
            set(by_role),
            {"FULL_FIELD_PULLBACK", "PREPULLED_VALUE_PRIMITIVE"},
        )
        self.assertEqual(
            by_role["FULL_FIELD_PULLBACK"]["source_symbols"],
            ["pullback_thermodynamic_temperature_field"],
        )
        self.assertEqual(
            by_role["PREPULLED_VALUE_PRIMITIVE"]["source_symbols"],
            ["thermodynamic_temperature_pullback"],
        )
        self.assertNotEqual(
            by_role["FULL_FIELD_PULLBACK"]["parity_status"],
            by_role["PREPULLED_VALUE_PRIMITIVE"]["parity_status"],
        )

    def test_relation_records_use_orthogonal_semantic_fields(self) -> None:
        required = {
            "formula_id",
            "consumer_repository",
            "source_path",
            "git_blob_sha1",
            "algebraic_relation",
            "domain_relation",
            "implementation_role",
            "convention_adapter",
            "unit_parameter_adapter",
            "input_policy",
            "numerical_policy",
            "validity_subspace",
            "authority_effect",
            "parity_status",
        }
        for row in self.relations:
            with self.subTest(relation_id=row.get("relation_id")):
                self.assertEqual(required - set(row), set())

    def test_rei_h_only_energy_residual_has_exact_sign_and_coefficient(self) -> None:
        self.assertIn("REIHOnlyMinusGenericEnergyDrift", self.receipt_fix)
        self.assertRegex(
            self.receipt_fix,
            r"Expand\[\s*reiDifference\s*-\s*sigmaEE\s*\]\s*===\s*0",
        )
        self.assertNotIn("!TrueQ[reiDifference === 0]", self.receipt_fix)

    def test_source_packet_status_requires_exact_discovered_test_count(self) -> None:
        self.assertRegex(
            self.runner,
            r'"status"\s*->\s*If\[[\s\S]*TestsSucceededCount[\s\S]*expectedTestCount',
        )
        self.assertRegex(self.runner, r"expectedTestCount\s*=\s*12")
        self.assertNotRegex(
            self.runner,
            r'"status"\s*->\s*If\[\s*report\["TestsFailedCount"\]\s*===\s*0\s*&&\s*report\["TestsNotEvaluatedCount"\]\s*===\s*0\s*,\s*"PASS"',
        )

    def test_wlt_is_not_hidden_inside_one_module_expression(self) -> None:
        body = re.sub(r"\(\*[\s\S]*?\*\)", "", self.wlt).lstrip()
        self.assertFalse(
            body.startswith("Module["),
            "TestReport[file] discovers zero tests when all VerificationTest expressions are hidden inside one Module result",
        )


if __name__ == "__main__":
    unittest.main()
