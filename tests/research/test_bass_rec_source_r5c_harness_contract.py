from __future__ import annotations

from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/research/run_bass_rec_source_r5c_dev_behavior.sh"
TEXT = SCRIPT.read_text(encoding="utf-8")


def test_shell_syntax_is_valid() -> None:
    completed = subprocess.run(
        ["bash", "-n", str(SCRIPT)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr


def test_exact_source_and_wheel_identities_are_pinned() -> None:
    required = {
        "d81ad12f795b6ac6d57293502e75426ed1dbbb1a",
        "fc4d21b92a1abd1e9b35178f7d666831fc5c827d",
        "bf5a59534ffc9d6f9c3410aa19319f18a4a8a7a9761bcd61c5da8c8627ddf609",
        "ca3807fa4ef49b5292bd65fd80b6fe9947c1cef7f835979122bff572900eb906",
    }
    for token in required:
        assert token in TEXT


def test_default_fail_closed_control_precedes_development_override_runs() -> None:
    fail_closed = TEXT.index("DEFAULT FAIL-CLOSED CONTROL")
    base_override = TEXT.index("BASE INTEGRATION WITH EXPLICIT DEVELOPMENT OVERRIDE")
    candidate_override = TEXT.index(
        "CANDIDATE INTEGRATION WITH EXPLICIT DEVELOPMENT OVERRIDE"
    )
    assert fail_closed < base_override < candidate_override
    assert "env -u \"$OVERRIDE\"" in TEXT
    assert 'env "$OVERRIDE=1"' in TEXT


def test_policy_and_packaging_are_not_run_under_global_override() -> None:
    start = TEXT.index("POLICY AND PACKAGING WITHOUT OVERRIDE")
    end = TEXT.index("BASE INTEGRATION WITH EXPLICIT DEVELOPMENT OVERRIDE")
    block = TEXT[start:end]
    assert "env -u \"$OVERRIDE\"" in block
    assert '"$OVERRIDE=1"' not in block


def test_success_classification_is_explicitly_development_only() -> None:
    assert (
        "PASS_R5C_DEV_BEHAVIOR_ONLY_NO_PRODUCTION_PROVENANCE" in TEXT
    )
    assert '"production_native_provenance":False' in TEXT
    assert '"trusted_registry_modified":False' in TEXT


def test_harness_does_not_rewrite_backend_policy_or_trusted_receipts() -> None:
    forbidden_patterns = (
        r"sed\s+-i[^\n]*backend_policy",
        r">\s*[^\n]*backend_policy\.py",
        r"update_file",
        r"RF04_SCALAR_RAW_NATIVE_PAYLOAD\s*=",
        r"_TRUSTED_NATIVE_PAYLOADS\s*=",
    )
    for pattern in forbidden_patterns:
        assert re.search(pattern, TEXT) is None, pattern


def test_caller_checkout_is_never_switched() -> None:
    forbidden = (
        "git checkout",
        "git switch",
        "git reset --hard",
        "git clean -",
    )
    for token in forbidden:
        assert token not in TEXT
    assert "worktree add --detach" in TEXT
    assert "worktree remove --force" in TEXT


def test_base_and_candidate_use_the_same_local_wheel_and_test_file() -> None:
    assert TEXT.count("tests/test_backend_integration.py") == 2
    assert "base_integration.xml" in TEXT
    assert "candidate_integration.xml" in TEXT
    assert "same_counts" in TEXT


def test_receipt_retains_claim_firewalls() -> None:
    for field in (
        '"behavioral_regression_only":True',
        '"production_native_provenance":False',
        '"source_integration":False',
        '"grid_pstf_parity":False',
        '"physical_face":False',
        '"provider_export":False',
        '"pass_rf04":False',
    ):
        assert field in TEXT
