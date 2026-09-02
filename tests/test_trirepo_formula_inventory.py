from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "trirepo_formula_inventory.py"
FIXTURE = ROOT / "fixtures" / "trirepo_formula_inventory_minimal.json"
SOURCE = ROOT / "docs" / "bianchi_program" / "SYNC_MAP_01" / "TRIREPO_PATH_INVENTORY_SOURCE.json"


def load_module():
    spec = importlib.util.spec_from_file_location("trirepo_formula_inventory", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load inventory module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class InventoryContractTests(unittest.TestCase):
    def test_cli_validates_minimal_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "inventory.json"
            completed = subprocess.run(
                [sys.executable, str(SCRIPT), "--input", str(FIXTURE), "--output", str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            document = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(document["status"], "PASS_BOUNDED_PATH_INVENTORY")
            self.assertEqual(document["summary"]["entry_count"], 1)

    def test_inventory_run_id_is_entry_order_invariant(self) -> None:
        module = load_module()
        document = json.loads(FIXTURE.read_text(encoding="utf-8"))
        duplicate = copy.deepcopy(document["entries"][0])
        duplicate["path"] = "wolfram/BASS/Kernel/Authority/Dimensions.wl"
        duplicate["blob_sha"] = "a12808c2cbc3bf6f56f9dc27e01a3d7daec34c9e"
        document["entries"].append(duplicate)
        reversed_document = copy.deepcopy(document)
        reversed_document["entries"].reverse()
        self.assertEqual(
            module.compute_inventory_run_id(document),
            module.compute_inventory_run_id(reversed_document),
        )

    def test_mixed_ownership_requires_split(self) -> None:
        module = load_module()
        document = json.loads(FIXTURE.read_text(encoding="utf-8"))
        entry = document["entries"][0]
        entry["classification"] = "MIXED_OWNERSHIP_REQUIRES_SPLIT"
        entry["authority_effect"] = "NONE"
        entry["mixed_ownership"] = True
        entry["owner_candidates"] = ["bass", "rec_bianchi"]
        entry["split_required"] = False
        with self.assertRaisesRegex(module.InventoryError, "MIXED_PATH_REQUIRES_SPLIT"):
            module.validate_inventory(document)

    def test_independent_oracle_cannot_claim_authority(self) -> None:
        module = load_module()
        document = json.loads(FIXTURE.read_text(encoding="utf-8"))
        entry = document["entries"][0]
        entry["path_role"] = "ORACLE"
        entry["classification"] = "INDEPENDENT_ORACLE"
        entry["authority_effect"] = "AUTHORITATIVE_DERIVATION"
        entry["replay_of_candidates"] = ["BASS.CONVENTION.CORE.001"]
        with self.assertRaisesRegex(module.InventoryError, "ORACLE_AUTHORITY_EFFECT"):
            module.validate_inventory(document)

    def test_independent_oracle_requires_replay_candidate(self) -> None:
        module = load_module()
        document = json.loads(FIXTURE.read_text(encoding="utf-8"))
        entry = document["entries"][0]
        entry["path_role"] = "ORACLE"
        entry["classification"] = "INDEPENDENT_ORACLE"
        entry["authority_effect"] = "NONE"
        entry["replay_of_candidates"] = []
        with self.assertRaisesRegex(module.InventoryError, "ORACLE_REPLAY_CANDIDATE"):
            module.validate_inventory(document)

    def test_active_lineage_set_is_exact(self) -> None:
        module = load_module()
        document = json.loads(FIXTURE.read_text(encoding="utf-8"))
        del document["lineages"]["rei_bianchi"]
        with self.assertRaisesRegex(module.InventoryError, "LINEAGE_SET"):
            module.validate_inventory(document)

    def test_duplicate_repository_path_is_rejected(self) -> None:
        module = load_module()
        document = json.loads(FIXTURE.read_text(encoding="utf-8"))
        document["entries"].append(copy.deepcopy(document["entries"][0]))
        with self.assertRaisesRegex(module.InventoryError, "DUPLICATE_PATH"):
            module.validate_inventory(document)

    def test_authoritative_schema_must_be_owned_locally(self) -> None:
        module = load_module()
        document = json.loads(FIXTURE.read_text(encoding="utf-8"))
        document["entries"][0]["owner_candidates"] = ["rec_bianchi"]
        with self.assertRaisesRegex(module.InventoryError, "AUTHORITATIVE_SCHEMA_OWNER"):
            module.validate_inventory(document)

    def test_full_source_inventory_validates(self) -> None:
        module = load_module()
        source = json.loads(SOURCE.read_text(encoding="utf-8"))
        result = module.validate_inventory(source)
        self.assertEqual(result["status"], "PASS_BOUNDED_PATH_INVENTORY")
        self.assertGreaterEqual(result["summary"]["entry_count"], 50)
        self.assertGreaterEqual(result["summary"]["mixed_ownership_path_count"], 3)
        self.assertEqual(result["summary"]["official_dag_edge_mutation_count"], 0)
        self.assertEqual(result["summary"]["semantic_source_scan"], "NOT_RUN_SYNC_MAP_01")


if __name__ == "__main__":
    unittest.main()
