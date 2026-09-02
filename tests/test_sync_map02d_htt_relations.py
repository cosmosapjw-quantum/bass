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


def canonical_data() -> dict[str, object]:
    return VERIFY.load_json(VERIFY.CLASSIFICATION)


class SyncMap02DHTTRelationsTests(unittest.TestCase):
    def test_canonical_contract_passes(self) -> None:
        result = VERIFY.verify(canonical_data())
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["relations"], 12)
        self.assertEqual(result["source_pins"], 8)
        self.assertEqual(result["pending_bass_imports"], 4)
        self.assertEqual(result["new_htt_shared_gaps"], 2)
        self.assertEqual(result["duplicate_authority_count"], 0)
        self.assertEqual(result["dag_nodes"], 10)
        self.assertEqual(result["dag_edges"], 12)

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
