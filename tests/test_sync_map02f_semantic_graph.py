from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "docs" / "bass_master_ssot_v2" / "SYNC_MAP_02F" / "CROSS_REPOSITORY_SEMANTIC_GRAPH.json"
VERIFIER = ROOT / "scripts" / "verify_sync_map02f_semantic_graph.py"
WOLFRAM_MODULE = ROOT / "wolfram" / "BASS" / "Kernel" / "IR" / "CrossRepositorySemanticGraph.wl"


class SyncMap02FMissingSurfaceTests(unittest.TestCase):
    def test_cross_repository_graph_authority_is_missing_on_exact_parent(self) -> None:
        self.assertTrue(
            GRAPH.is_file(),
            "SYNC-MAP-02F graph authority is absent on the exact 02E parent",
        )

    def test_fail_closed_verifier_is_missing_on_exact_parent(self) -> None:
        self.assertTrue(
            VERIFIER.is_file(),
            "SYNC-MAP-02F fail-closed verifier is absent on the exact 02E parent",
        )

    def test_wolfram_graph_api_is_missing_on_exact_parent(self) -> None:
        self.assertTrue(
            WOLFRAM_MODULE.is_file(),
            "SYNC-MAP-02F Wolfram graph API is absent on the exact 02E parent",
        )


if __name__ == "__main__":
    unittest.main()
