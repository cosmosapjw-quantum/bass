from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


REQUIRED = (
    "scripts/external_formula_packages/verify_python_tensor_package.py",
    "scripts/external_formula_packages/cadabra_tensor_probe.py",
    "scripts/external_formula_packages/maxima_weighted_pullback.mac",
    "scripts/external_formula_packages/reduce_aberration.red",
    "scripts/external_formula_packages/aggregate_receipts.py",
    "docs/bass_master_ssot_v2/XCAS_01/PACKAGE_PLAN.json",
    "docs/bass_master_ssot_v2/XCAS_01/README.md",
)


def test_external_package_verification_surfaces_exist() -> None:
    missing = [path for path in REQUIRED if not (ROOT / path).is_file()]
    assert missing == [], f"missing XCAS-01 surfaces: {missing}"


def test_external_package_stage_is_evidence_only() -> None:
    readme = (ROOT / "docs/bass_master_ssot_v2/XCAS_01/README.md")
    assert readme.is_file(), "XCAS-01 README is absent"
    text = readme.read_text(encoding="utf-8")
    for required in (
        "authority_effect: NONE",
        "NO_02E_SEMANTIC_PROMOTION",
        "NO_02F_SEMANTIC_CLOSEOUT",
        "NO_CONSUMER_PARITY_PROMOTION",
    ):
        assert required in text
