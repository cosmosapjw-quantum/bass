#!/usr/bin/env python3
"""RED/GREEN contract for the independent SYNC-MAP-02D SymPy oracle."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "sync_map02d_crosscheck_sympy.py"
EXPECTED_COMMIT = "7006aaab27834af37d5034f8f1e50943fe85c0f3"


def load_oracle():
    if not SCRIPT.is_file():
        raise AssertionError(f"missing independent SymPy oracle: {SCRIPT.relative_to(ROOT)}")
    spec = importlib.util.spec_from_file_location("sync_map02d_crosscheck_sympy", SCRIPT)
    if spec is None or spec.loader is None:
        raise AssertionError("cannot construct import spec for SymPy oracle")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SyncMap02DSymPyCrosscheckTests(unittest.TestCase):
    def test_oracle_surface_exists(self) -> None:
        self.assertTrue(SCRIPT.is_file(), f"missing {SCRIPT.relative_to(ROOT)}")

    def test_exact_subject_and_claim_boundary_are_locked(self) -> None:
        oracle = load_oracle()
        result = oracle.run_all()
        self.assertEqual(result["tested_subject"]["commit"], EXPECTED_COMMIT)
        self.assertEqual(result["authority_effect"], "NONE")
        self.assertIn("NO_SHARED_EXPORT", result["claim_boundary"])
        self.assertIn("NO_GLOBAL_TILT", result["claim_boundary"])

    def test_all_exact_and_structural_checks_pass(self) -> None:
        oracle = load_oracle()
        result = oracle.run_all()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["failure_count"], 0)
        self.assertGreaterEqual(result["check_count"], 28)

    def test_registered_hostile_mutations_are_detected(self) -> None:
        oracle = load_oracle()
        result = oracle.run_all()
        checks = {row["name"]: row["passed"] for row in result["checks"]}
        required = {
            "wrong_doppler_sign_detected",
            "wrong_jacobian_power_detected",
            "wrong_stf3_trace_coefficient_detected",
            "non_symmetric_stf3_detected",
            "missing_unit_sphere_domain_detected",
            "omitted_dipole_detected",
            "omitted_octupole_detected",
            "missing_02d_dependency_mutation_detected",
            "missing_dependency_mutant_remains_acyclic",
        }
        self.assertTrue(required <= set(checks), sorted(required - set(checks)))
        self.assertTrue(all(checks[name] for name in required))


if __name__ == "__main__":
    unittest.main(verbosity=2)
