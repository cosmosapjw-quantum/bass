from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = (
    ROOT
    / "docs"
    / "bass_master_ssot_v2"
    / "SYNC_MAP_02F_R2"
    / "BASS_STATE_SURFACE_REGISTRY.json"
)
VERIFIER = ROOT / "scripts" / "verify_bass_state_surface_registry.py"
WOLFRAM_MODULE = (
    ROOT / "wolfram" / "BASS" / "Kernel" / "IR" / "BASSStateSurfaceRegistry.wl"
)
WOLFRAM_TEST = (
    ROOT / "wolfram" / "BASS" / "Tests" / "BASSStateSurfaceRegistry.wlt"
)
LOCAL_RUNNER = ROOT / "scripts" / "run_bass_state_surface_registry_local.sh"


def load_verifier():
    spec = importlib.util.spec_from_file_location("bass_state_surface_verifier", VERIFIER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load verifier")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


class BASSStateSurfaceRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.verifier = load_verifier()

    def test_required_surfaces_exist(self) -> None:
        for path in (REGISTRY, VERIFIER, WOLFRAM_MODULE, WOLFRAM_TEST, LOCAL_RUNNER):
            self.assertTrue(path.is_file(), path)

    def test_clean_registry_passes(self) -> None:
        result = self.verifier.verify(load_registry())
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["state_count"], 6)
        self.assertEqual(result["relation_count"], 6)

    def test_j_projection_cannot_be_promoted_to_state_equivalence(self) -> None:
        data = load_registry()
        relation = next(row for row in data["relations"] if row["relation_id"] == "PSTF_TO_J")
        relation["runtime_parity"] = "EXACT_CONSUMER_IMPLEMENTATION"
        with self.assertRaisesRegex(ValueError, "state parity"):
            self.verifier.verify(data)

    def test_g_projection_requires_spectral_closure(self) -> None:
        data = load_registry()
        relation = next(row for row in data["relations"] if row["relation_id"] == "GRID_TO_G")
        relation["required_certificates"] = [
            item
            for item in relation["required_certificates"]
            if item != "SOURCE_GRID_QUADRATURE_OR_SPECTRAL_CLOSURE"
        ]
        with self.assertRaisesRegex(ValueError, "G projection closure"):
            self.verifier.verify(data)

    def test_polarized_surface_requires_screen_transport(self) -> None:
        data = load_registry()
        relation = next(
            row
            for row in data["relations"]
            if row["relation_id"] == "SCALAR_TO_POLARIZED_PROHIBITED"
        )
        relation["required_certificates"].remove("SCREEN_BASIS_TRANSPORT")
        with self.assertRaisesRegex(ValueError, "screen transport"):
            self.verifier.verify(data)

    def test_hardcoded_ell_cutoff_is_forbidden(self) -> None:
        data = load_registry()
        data["ell_policy"]["target_cutoff"] = 12
        with self.assertRaisesRegex(ValueError, "target cutoff"):
            self.verifier.verify(data)

    def test_normal_ancestry_is_exact_pinned(self) -> None:
        data = load_registry()
        data["normal_ancestry"]["parent_commit"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "normal ancestry"):
            self.verifier.verify(data)


if __name__ == "__main__":
    unittest.main()
