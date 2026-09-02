from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
XCAS = ROOT / "docs/bass_master_ssot_v2/XCAS_01"


REQUIRED = (
    "scripts/external_formula_packages/verify_python_tensor_package.py",
    "scripts/external_formula_packages/cadabra_tensor_probe.py",
    "scripts/external_formula_packages/maxima_weighted_pullback.mac",
    "scripts/external_formula_packages/reduce_aberration.red",
    "scripts/external_formula_packages/aggregate_receipts.py",
    "docs/bass_master_ssot_v2/XCAS_01/PACKAGE_PLAN.json",
    "docs/bass_master_ssot_v2/XCAS_01/README.md",
    "docs/bass_master_ssot_v2/XCAS_01/TDD_RED_RECEIPT.json",
    "docs/bass_master_ssot_v2/XCAS_01/STENSOR_WOLFRAM_RECEIPT.json",
    "docs/bass_master_ssot_v2/XCAS_01/OGRE_WOLFRAM_RECEIPT.json",
    "docs/bass_master_ssot_v2/XCAS_01/GENERAL_RELATIVITY_TENSORS_RECEIPT.json",
    "docs/bass_master_ssot_v2/XCAS_01/HOSTED_RUNNER_BLOCK_RECEIPT.json",
    "docs/bass_master_ssot_v2/XCAS_01/INTERIM_AGGREGATE_RECEIPT.json",
    "docs/bass_master_ssot_v2/XCAS_01/SCISPACE_PACKAGE_LITERATURE_LOCK.md",
)


def _load_json(name: str) -> dict[str, object]:
    value = json.loads((XCAS / name).read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_external_package_verification_surfaces_exist() -> None:
    missing = [path for path in REQUIRED if not (ROOT / path).is_file()]
    assert missing == [], f"missing XCAS-01 surfaces: {missing}"


def test_external_package_stage_is_evidence_only() -> None:
    readme = XCAS / "README.md"
    assert readme.is_file(), "XCAS-01 README is absent"
    text = readme.read_text(encoding="utf-8")
    for required in (
        "authority_effect: NONE",
        "NO_02E_SEMANTIC_PROMOTION",
        "NO_02F_SEMANTIC_CLOSEOUT",
        "NO_CONSUMER_PARITY_PROMOTION",
    ):
        assert required in text


def test_three_executed_wolfram_packages_are_exact_passes() -> None:
    for receipt_name in (
        "STENSOR_WOLFRAM_RECEIPT.json",
        "OGRE_WOLFRAM_RECEIPT.json",
        "GENERAL_RELATIVITY_TENSORS_RECEIPT.json",
    ):
        receipt = _load_json(receipt_name)
        assert receipt["status"] == "PASS"
        assert receipt["pass"] is True
        assert receipt["authority_effect"] == "NONE"
        assert (
            receipt["package_axis"]
            == "INDEPENDENT_TENSOR_PACKAGE_SHARED_WOLFRAM_KERNEL"
        )


def test_hosted_runner_nonexecution_is_not_package_failure() -> None:
    receipt = _load_json("HOSTED_RUNNER_BLOCK_RECEIPT.json")
    assert receipt["status"] == "BLOCKED_HOSTED_RUNNER_INFRASTRUCTURE"
    assert receipt["package_execution_effect"] == "NOT_RUN"
    for observation in receipt["observations"]:
        assert observation.get("all_job_conclusions") == "failure"
        if "all_step_counts" in observation:
            assert observation["all_step_counts"] == 0
        if "all_steps" in observation:
            assert observation["all_steps"] is None


def test_interim_aggregate_does_not_claim_cross_cas_pass() -> None:
    receipt = _load_json("INTERIM_AGGREGATE_RECEIPT.json")
    assert receipt["status"] == "PARTIAL_EXTERNAL_PACKAGE_PASS_INDEPENDENT_CAS_NOT_RUN"
    assert receipt["executed_package_count"] == 3
    assert receipt["executed_package_pass_count"] == 3
    assert receipt["executed_independent_cas_engine_count"] == 0
    assert receipt["independence_assessment"]["strong_cross_CAS_claim"] is False
