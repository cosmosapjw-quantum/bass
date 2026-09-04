#!/usr/bin/env python3
"""Run the named BG-02 native-bridge adversarial RED contract.

This is an expected-RED wrapper: it succeeds only when the exact named set of
publication-blocking tests fails, with no errors, skips, or unexpected passes.
It is superseded incrementally as the native bridge is implemented.
"""

from __future__ import annotations

import io
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = (
    Path(sys.argv[1]).resolve()
    if len(sys.argv) >= 2
    else ROOT / "artifacts/bg02_native_bridge_adversarial_red"
)
LOG = ARTIFACT_DIR / "BG_02_NATIVE_BRIDGE_ADVERSARIAL_RED.log"
RECEIPT = ARTIFACT_DIR / "BG_02_NATIVE_BRIDGE_ADVERSARIAL_RED_RECEIPT.json"

EXPECTED_FAILURES = {
    "test_claim_surface_is_component_oracle_only",
    "test_component_oracle_and_native_bridge_are_separate_modules",
    "test_tensor_api_is_not_an_association_lookup",
    "test_positive_native_gates_are_computed_not_literal",
    "test_exceptional_vi_witness_is_derived_not_x_minus_x",
    "test_wrong_order_curvature_is_test_only",
    "test_state_and_missing_components_fail_closed",
    "test_native_bridge_uses_exact_w2_sign_registry",
    "test_native_runner_activates_xact_before_full_init",
    "test_every_native_exit_publishes_an_atomic_receipt",
    "test_failure_round_trip_preserves_observed_counts",
    "test_native_admission_uses_exact_named_test_set",
    "test_auxiliary_cas_cannot_prevent_native_receipt",
}


def method_name(test: unittest.case.TestCase) -> str:
    return test.id().rsplit(".", 1)[-1]


def main() -> int:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(ROOT))

    suite = unittest.defaultTestLoader.loadTestsFromName(
        "tests.test_bg02_native_bridge_adversarial"
    )
    stream = io.StringIO()
    result = unittest.TextTestRunner(
        stream=stream,
        verbosity=2,
        buffer=True,
    ).run(suite)
    text = stream.getvalue()
    LOG.write_text(text, encoding="utf-8")
    print(text, end="")

    failures = {method_name(test) for test, _ in result.failures}
    errors = {method_name(test) for test, _ in result.errors}
    skipped = {method_name(test) for test, _ in result.skipped}
    unexpected_successes = {
        method_name(test) for test in result.unexpectedSuccesses
    }
    observed = failures | errors | skipped | unexpected_successes
    loaded = result.testsRun
    passed = loaded - len(observed)

    exact_red = (
        loaded == len(EXPECTED_FAILURES)
        and failures == EXPECTED_FAILURES
        and not errors
        and not skipped
        and not unexpected_successes
        and passed == 0
    )

    payload = {
        "schema_version": "1.0.0",
        "stage_id": "BG_02_NATIVE_GAUSS_CODAZZI_BRIDGE_ADVERSARIAL_RED",
        "repository_scope": "BASS_ONLY",
        "expected_failure_ids": sorted(EXPECTED_FAILURES),
        "observed_failure_ids": sorted(failures),
        "error_ids": sorted(errors),
        "skipped_ids": sorted(skipped),
        "unexpected_success_ids": sorted(unexpected_successes),
        "tests_run": loaded,
        "tests_passed": passed,
        "tests_failed": len(failures),
        "tests_errored": len(errors),
        "claim_effect": "COMPONENT_ORACLE_ONLY_NATIVE_BRIDGE_STILL_RED",
        "status": "PASS_EXPECTED_RED" if exact_red else "FAIL_RED_CONTRACT_DRIFT",
    }
    RECEIPT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, sort_keys=True))
    return 0 if exact_red else 1


if __name__ == "__main__":
    raise SystemExit(main())
