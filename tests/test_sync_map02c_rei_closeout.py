from __future__ import annotations

import csv
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
DOCS = REPO / "docs" / "bass_master_ssot_v2" / "SYNC_MAP_02C"
CLASSIFICATION = DOCS / "REI_RELATION_CLASSIFICATION_R3.json"
COVERAGE = DOCS / "REI_SOURCE_COVERAGE_MATRIX.csv"
VERIFIER = REPO / "scripts" / "verify_sync_map02c_rei_relations.py"

EXPECTED_SOURCE_BLOBS = {
    "src/rei_bianchi/absorption_decomposition.py": "5f797469eaa67847fa3c5f3701a5b8416a55d98e",
    "src/rei_bianchi/b2b_physical_model.py": "b3cc5e45988687b76d5be04c6335009b4c9bd17f",
    "src/rei_bianchi/bass_integration_substrate.py": "3c0f68cb0e40e3826a3d80dfce2fcdd5065fd826",
    "src/rei_bianchi/certificate_graph.py": "afe9c5afc6b2d2b75283f50e4223c371b90746d0",
    "src/rei_bianchi/gamma_conditioned_reconciliation.py": "1328e49baa0f4bb5d4e1d5a5ca0940c10e8852d5",
    "src/rei_bianchi/global_moment_constrained_macro_sink.py": "389753d94a291fffbfb2b09092029d61afb3ea19",
    "src/rei_bianchi/hi_transmission_kernel_b2c1a.py": "7ec9bd5548db4c024c075b70d0affc81eccfe0d7",
    "src/rei_bianchi/hierarchical_two_scale_closure.py": "ecb55acd39aba9d609f2eb704ef282018d6666b2",
    "src/rei_bianchi/joint_implicit_remainder.py": "cdd24e2e17897bf2bfe102814b123668d884c456",
    "src/rei_bianchi/joint_sink_reservoir_history.py": "604697415f4de9363951653165f90273f297e0b0",
    "src/rei_bianchi/matched_history_feasibility_gate.py": "3d80474e7ba1ecba4f102c5dd85b6efa2bfb0ec3",
    "src/rei_bianchi/monolithic_model_b2a.py": "3d806e1c1d3bb523bb3c339d1a141f67d7f10069",
    "src/rei_bianchi/multigroup_hhe_transmission.py": "5b74a4036c8cb21a2cb772dd3d373c5f96d5a36c",
    "src/rei_bianchi/node_lift_operator.py": "6f5c13f02d0e549e581a02d3c4d8b8313b209bbf",
    "src/rei_bianchi/node_resolved_joint_history.py": "69e671769d70804be6f7debc4b9ba1f11519bbfc",
    "src/rei_bianchi/phase_space_kernel_b2c0.py": "026a22b1843ab3a3336b210317727e216202fc75",
    "src/rei_bianchi/primary_exact_zero_model.py": "ea2a10a60114622fd1215b692be3dd0d04ef0c6d",
    "src/rei_bianchi/reiaff1.py": "80a7627baf5981375de10ae55d862b09b0071432",
    "src/rei_bianchi/run_first_interval_refinement.py": "5d39fef633662178a71685dac90e4ffe9a0a788d",
    "src/rei_bianchi/run_node_lift.py": "83abebd1a4f7e7a6f5fba83d4a20e1b23063fa02",
    "src/rei_bianchi/run_primary_diagnostics.py": "1c295b27d692618fffef442182d1595feac56d7d",
    "src/rei_bianchi/source_bound_mprk_sdirk_operator.py": "fba94e59d20d640237290911abd774ede3fe5360",
}

EXPECTED_SHARED_UNION = {
    "BASS.FRAME.ABERRATED_DIRECTION.001",
    "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001",
    "BASS.FRAME.DOPPLER_FACTOR.001",
    "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001",
    "BASS.PHOTON.DIRECTION_FLOW.001",
    "BASS.PHOTON.ENERGY_DRIFT.001",
}


def run_verifier(classification: Path, coverage: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(VERIFIER),
            "--classification",
            str(classification),
            "--coverage",
            str(coverage),
            "--json",
        ],
        cwd=REPO,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


class SyncMap02CLOSEOUTTests(unittest.TestCase):
    def test_canonical_candidate_passes_fail_closed_verifier(self) -> None:
        result = run_verifier(CLASSIFICATION, COVERAGE)
        self.assertEqual(result.returncode, 0, result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "PASS")
        self.assertEqual(payload["source_rows"], 22)
        self.assertEqual(set(payload["shared_union"]), EXPECTED_SHARED_UNION)

    def test_coverage_matrix_is_exact_complete_source_tree(self) -> None:
        with COVERAGE.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        observed = {row["source_path"]: row["git_blob_sha1"] for row in rows}
        self.assertEqual(observed, EXPECTED_SOURCE_BLOBS)
        self.assertEqual(len(rows), 22)
        self.assertTrue(all(row["semantic_disposition"] for row in rows))
        self.assertTrue(all(row["shared_owner_gap_effect"] for row in rows))

    def test_relation_owners_are_atomic(self) -> None:
        data = json.loads(CLASSIFICATION.read_text(encoding="utf-8"))
        allowed = {"bass", "rec_bianchi", "rei_bianchi", "htt_base"}
        owners = [relation["owner"] for relation in data["relations"]]
        self.assertTrue(owners)
        self.assertTrue(all(owner in allowed for owner in owners), owners)
        self.assertNotIn("bass_and_rec", owners)

    def test_shared_export_union_contains_rec_and_htt_gaps(self) -> None:
        data = json.loads(CLASSIFICATION.read_text(encoding="utf-8"))
        self.assertEqual(set(data["shared_formula_consumer_union"]), EXPECTED_SHARED_UNION)
        self.assertEqual(
            set(data["shared_formula_consumer_union"]["BASS.FRAME.SOLID_ANGLE_JACOBIAN.001"]),
            {"htt_base"},
        )
        self.assertEqual(
            set(data["shared_formula_consumer_union"]["BASS.PHOTON.ENERGY_DRIFT.001"]),
            {"rec_bianchi", "rei_bianchi"},
        )

    def test_02e_remains_held_by_both_relation_map_gates(self) -> None:
        data = json.loads(CLASSIFICATION.read_text(encoding="utf-8"))
        gate = data["next_stage_gate"]
        self.assertEqual(gate["node"], "SYNC_MAP_02E_SHARED_FRAME_PHOTON_EXPORT")
        self.assertEqual(gate["status"], "HELD_UNTIL_02C_AND_02D_FROZEN_READBACK")
        self.assertEqual(set(gate["required_predecessors"]), {"SYNC_MAP_02C_REI", "SYNC_MAP_02D_HTT"})

    def _mutated_run(self, *, json_mutator=None, row_mutator=None) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            data = json.loads(CLASSIFICATION.read_text(encoding="utf-8"))
            with COVERAGE.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
                fieldnames = list(rows[0])
            if json_mutator is not None:
                json_mutator(data)
            if row_mutator is not None:
                row_mutator(rows)
            classification = tmp_path / CLASSIFICATION.name
            coverage = tmp_path / COVERAGE.name
            classification.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
            with coverage.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            return run_verifier(classification, coverage)

    def test_multi_owner_mutation_is_rejected(self) -> None:
        result = self._mutated_run(
            json_mutator=lambda data: data["relations"][0].__setitem__("owner", "bass_and_rec")
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FAIL_MULTI_OWNER", result.stdout)

    def test_stale_four_formula_union_is_rejected(self) -> None:
        def mutate(data: dict) -> None:
            del data["shared_formula_consumer_union"]["BASS.FRAME.SOLID_ANGLE_JACOBIAN.001"]
            del data["shared_formula_consumer_union"]["BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001"]

        result = self._mutated_run(json_mutator=mutate)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FAIL_SHARED_UNION", result.stdout)

    def test_missing_source_row_is_rejected(self) -> None:
        result = self._mutated_run(row_mutator=lambda rows: rows.pop())
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FAIL_COVERAGE_COUNT", result.stdout)

    def test_source_blob_mutation_is_rejected(self) -> None:
        def mutate(rows: list[dict[str, str]]) -> None:
            rows[0]["git_blob_sha1"] = "0" * 40

        result = self._mutated_run(row_mutator=mutate)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FAIL_COVERAGE_BLOB", result.stdout)

    def test_02e_gate_bypass_is_rejected(self) -> None:
        result = self._mutated_run(
            json_mutator=lambda data: data["next_stage_gate"].__setitem__("status", "READY")
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FAIL_02E_GATE", result.stdout)


if __name__ == "__main__":
    unittest.main()
