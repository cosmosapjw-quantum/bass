from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "validate_sync_map01.py"
SPEC = importlib.util.spec_from_file_location("validate_sync_map01", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class SyncMap01Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = MODULE.validate(ROOT)
        docs = ROOT / "docs" / "bianchi_program"
        cls.inventory = json.loads((docs / "SYNC_MAP_01_FORMULA_PATH_INVENTORY.json").read_text())
        cls.overlaps = json.loads((docs / "SYNC_MAP_01_OVERLAP_LEDGER.json").read_text())
        cls.dag = json.loads((docs / "SYNC_MAP_01_DAG_UPDATE.json").read_text())
        cls.wolfram = json.loads((docs / "SYNC_MAP_01_WOLFRAM_RECEIPT.json").read_text())

    def test_packet_validates(self) -> None:
        self.assertEqual(self.result["status"], "PASS")

    def test_unique_formula_family_ids(self) -> None:
        ids = [entry["formula_family_id"] for entry in self.inventory["formula_families"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_active_control_is_pr86(self) -> None:
        self.assertEqual(self.inventory["active_control_line"]["pr"], 86)

    def test_pr87_is_not_auto_selected(self) -> None:
        donor = self.inventory["parallel_control_donor"]
        self.assertEqual(donor["classification"], "TECHNICAL_DONOR_PARALLEL_NOT_ACTIVE_PARENT")
        self.assertEqual(donor["automatic_disposition"], "NONE")

    def test_geometry_lineage_composition_is_required(self) -> None:
        item = next(entry for entry in self.overlaps["overlaps"] if entry["id"] == "OVL-001")
        self.assertEqual(item["required_action"], "SYNC-MAP-01C_GEOMETRY_LINEAGE_COMPOSITION")

    def test_shared_interface_is_provisional_only(self) -> None:
        item = next(entry for entry in self.overlaps["overlaps"] if entry["id"] == "OVL-003")
        self.assertEqual(item["automatic_action_taken"], "PROVISIONAL_WOLFRAM_EQUIVALENCE_ONLY")

    def test_no_official_edge_mutation(self) -> None:
        self.assertEqual(self.dag["proposed_official_edge_mutations"], [])

    def test_no_scientific_claim_mutation(self) -> None:
        self.assertEqual(self.dag["automatic_scientific_claim_changes"], [])

    def test_wolfram_residuals_are_exact_zero(self) -> None:
        self.assertEqual(set(self.wolfram["verified_residuals"].values()), {"0"})

    def test_rec_provider_remains_blocked(self) -> None:
        item = next(entry for entry in self.inventory["formula_families"] if entry["formula_family_id"] == "REC.PROVIDER_EXPORT")
        self.assertEqual(item["status"], "BLOCKED")

    def test_rei_interval_remains_stopped(self) -> None:
        item = next(entry for entry in self.inventory["formula_families"] if entry["formula_family_id"] == "REI.FIRST_CANONICAL_INTERVAL")
        self.assertEqual(item["status"], "STOP_INVALID_RUNTIME_BRIDGE")


if __name__ == "__main__":
    unittest.main()
