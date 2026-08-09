#!/usr/bin/env python3
"""Canonical, shell-free H0/H1 static-audit command plans.

This module is intentionally independent of the harness validator so the runner and
validator can share one immutable command plan without an import cycle.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


SOURCE_NAMES = (
    "01-physmath-research-harness-gpt56.zip",
    "02-physmath-coding-harness-gpt56.zip",
    "03-Low-ell-Bianchi-Einstein-Boltzmann-Solver.txt",
    "04-rust-1.94.1-x86_64-unknown-linux-gnu.tar.xz.asc",
    "05-rust_1_94_1_env.sh",
    "06-Adaptive-CMB-Code-Development-Protocol.txt",
    "07-Adaptive-CMB-Code-Research-Executor-DAG-Governed-Development-Mandatory-Dual-Audit-Plot-Driven-Adversarial-Loop.txt",
    "08-rust-1.94.1-x86_64-unknown-linux-gnu.tar.xz",
    "09-Figure-Residual-Error-Pass.txt",
    "10-Figure-Hostile-Audit.txt",
    "11-bootstrap.sh",
    "12-bianchirustcoreRDAGcomplete.tar.gz",
    "13-lowell_bianchi_codex_automation_kit.zip",
)

ARCHIVE_SOURCE_NAMES = (
    "01-physmath-research-harness-gpt56.zip",
    "02-physmath-coding-harness-gpt56.zip",
    "12-bianchirustcoreRDAGcomplete.tar.gz",
    "13-lowell_bianchi_codex_automation_kit.zip",
)

H1_TESTS = (
    "tests.test_harness_tools.HarnessTests.test_bundle_is_deterministic_and_archive_safe",
    "tests.test_harness_tools.HarnessTests.test_bootstrap_contracts_have_only_expected_preseal_errors",
    "tests.test_harness_tools.HarnessTests.test_code_read_without_od0_pass_is_rejected",
    "tests.test_harness_tools.HarnessTests.test_code_read_authorization_must_bind_owner_receipt",
    "tests.test_harness_tools.HarnessTests.test_all_in_scope_aggregate_state_is_derived",
    "tests.test_harness_tools.HarnessTests.test_applied_invalidation_produces_an_honest_remediation_state",
    "tests.test_harness_tools.HarnessTests.test_activity_receipt_rejects_minimal_nested_evidence",
    "tests.test_harness_tools.HarnessTests.test_coordinated_family_criterion_weakening_is_rejected",
    "tests.test_harness_tools.HarnessTests.test_coordinated_sector_binding_weakening_is_rejected",
    "tests.test_harness_tools.HarnessTests.test_disabled_sector_claim_must_be_locked_out",
    "tests.test_harness_tools.HarnessTests.test_exact_precode_allowlist_rejects_solver_and_binary_injections",
    "tests.test_harness_tools.HarnessTests.test_executable_mode_is_rejected_even_on_allowed_path",
    "tests.test_harness_tools.HarnessTests.test_family_leaf_criterion_isolation_is_enforced",
    "tests.test_harness_tools.HarnessTests.test_input_inventory_hashes_are_well_formed",
    "tests.test_harness_tools.HarnessTests.test_high_ell_row_semantics_are_immutable",
    "tests.test_harness_tools.HarnessTests.test_governing_contract_change_makes_pass_receipt_stale",
    "tests.test_harness_tools.HarnessTests.test_governing_profile_weakening_is_rejected",
    "tests.test_harness_tools.HarnessTests.test_generic_claim_cannot_be_dynamically_locked_out",
    "tests.test_harness_tools.HarnessTests.test_instruction_mutations_stale_h1_and_block_old_log_reuse",
    "tests.test_harness_tools.HarnessTests.test_live_file_immutable_projection_mutations_stale_h1",
    "tests.test_harness_tools.HarnessTests.test_massless_neutrino_scope_is_exact",
    "tests.test_harness_tools.HarnessTests.test_od003_upstream_role_and_wrong_pin_are_rejected",
    "tests.test_harness_tools.HarnessTests.test_owner_resolution_requires_typed_non_null_values",
    "tests.test_harness_tools.HarnessTests.test_pass_gate_rejects_minimal_receipt",
    "tests.test_harness_tools.HarnessTests.test_pending_owner_state_rejects_reserved_od0_receipt",
    "tests.test_harness_tools.HarnessTests.test_post_od0_invalidation_preserves_historical_authorization_evidence",
    "tests.test_harness_tools.HarnessTests.test_precode_rejects_undeclared_solver_file_even_after_manifest_rebuild",
    "tests.test_harness_tools.HarnessTests.test_safe_zip_passes",
    "tests.test_harness_tools.HarnessTests.test_supported_claim_requires_pass_gate_and_receipt_evidence",
    "tests.test_harness_tools.HarnessTests.test_transitive_invalidation_set_is_complete",
    "tests.test_harness_tools.HarnessTests.test_valid_od0_to_c0_phase_transition_is_accepted",
    "tests.test_harness_tools.HarnessTests.test_resolved_owner_decisions_require_snapshot_receipt",
    "tests.test_harness_tools.HarnessTests.test_resolved_owner_receipt_is_valid_before_code_authorization",
    "tests.test_harness_tools.HarnessTests.test_run_state_rejects_free_form_instruction_values",
    "tests.test_harness_tools.HarnessTests.test_run_state_rejects_generic_evidence_as_activity_proof",
    "tests.test_harness_tools.HarnessTests.test_static_log_rejects_forged_command_plan",
    "tests.test_harness_tools.HarnessTests.test_zip_traversal_is_rejected",
)

PY_SOURCE_FILES = (
    "tools/__init__.py",
    "tools/audit_archive.py",
    "tools/build_file_manifest.py",
    "tools/create_bundle.py",
    "tools/invalidate_state.py",
    "tools/issue_harness_evidence.py",
    "tools/run_static_checks.py",
    "tools/static_plan.py",
    "tools/validate_harness.py",
    "tests/__init__.py",
    "tests/test_harness_tools.py",
)


def execution_context(mode: str, root: Path, python_executable: str,
                      temporary: Path | None = None) -> dict:
    root = root.resolve()
    if mode == "H0" and temporary is None:
        raise ValueError("H0 requires an isolated temporary root")
    if mode == "H1" and temporary is not None:
        raise ValueError("H1 must not declare a temporary root")
    return {
        "harness_root": str(root),
        "workspace_root": str(root.parent),
        "temporary_root": str(temporary.resolve()) if temporary is not None else None,
        "python_executable": python_executable,
    }


def expected_command_plan(mode: str, context: dict) -> list[dict]:
    root = Path(context["harness_root"])
    workspace = Path(context["workspace_root"])
    python = context["python_executable"]
    sources = workspace / "project_sources"
    repo = workspace / "references/bianchi_phase_r"
    if mode == "H0":
        temporary = Path(context["temporary_root"])
        source_files = [str(sources / name) for name in SOURCE_NAMES]
        plan: list[dict] = [{
            "id":"CMD-H0-001", "argv":["sha256sum", *source_files], "cwd":str(root),
        }]
        for index, name in enumerate(ARCHIVE_SOURCE_NAMES, 2):
            plan.append({
                "id":f"CMD-H0-{index:03d}",
                "argv":[python, "tools/audit_archive.py", str(sources / name)],
                "cwd":str(root),
            })
        plan.extend([
            {"id":"CMD-H0-006","argv":["xz","--test",str(sources / SOURCE_NAMES[7])],"cwd":str(root)},
            {"id":"CMD-H0-007","argv":["gzip","--test",str(sources / SOURCE_NAMES[11])],"cwd":str(root)},
            {"id":"CMD-H0-008","argv":["git","-C",str(repo),"rev-parse","HEAD"],"cwd":str(root)},
            {"id":"CMD-H0-009","argv":["git","-C",str(repo),"status","--porcelain"],"cwd":str(root)},
            {"id":"CMD-H0-010","argv":["curl","-fsSL","https://static.rust-lang.org/dist/rust-1.94.1-x86_64-unknown-linux-gnu.tar.xz.sha256"],"cwd":str(root)},
            {"id":"CMD-H0-011","argv":["curl","-fsSL","https://static.rust-lang.org/dist/rust-1.94.1-x86_64-unknown-linux-gnu.tar.xz.asc","-o",str(temporary / "official.asc")],"cwd":str(root)},
            {"id":"CMD-H0-012","argv":["cmp","-s",str(temporary / "official.asc"),str(sources / SOURCE_NAMES[3])],"cwd":str(root)},
            {"id":"CMD-H0-013","argv":["curl","-fsSL","https://static.rust-lang.org/rust-key.gpg.ascii","-o",str(temporary / "rust-key.gpg.ascii")],"cwd":str(root)},
            {"id":"CMD-H0-014","argv":["gpg","--batch","--dearmor","--yes","--output",str(temporary / "rust-key.gpg"),str(temporary / "rust-key.gpg.ascii")],"cwd":str(root)},
            {"id":"CMD-H0-015","argv":["gpg","--homedir",str(temporary / "gnupg"),"--batch","--no-autostart","--with-colons","--show-keys","--fingerprint",str(temporary / "rust-key.gpg.ascii")],"cwd":str(root)},
            {"id":"CMD-H0-016","argv":["gpgv","--keyring",str(temporary / "rust-key.gpg"),str(sources / SOURCE_NAMES[3]),str(sources / SOURCE_NAMES[7])],"cwd":str(root)},
            {"id":"CMD-H0-017","argv":["git","-C",str(repo),"remote","get-url","origin"],"cwd":str(root)},
            {"id":"CMD-H0-018","argv":["git","-C",str(repo),"rev-parse","HEAD^{tree}"],"cwd":str(root)},
            {"id":"CMD-H0-019","argv":["git","-C",str(repo),"ls-remote","origin","HEAD","refs/heads/main"],"cwd":str(root)},
        ])
        return plan
    if mode != "H1":
        raise ValueError(f"unknown static-plan mode: {mode}")
    parent_probe = (
        "import runpy; "
        f"runpy.run_path({str(root / 'tests/test_harness_tools.py')!r}, run_name='bass_portability_probe')"
    )
    return [
        {"id":"CMD-H1-001","argv":[python,"-m","py_compile",*PY_SOURCE_FILES],"cwd":str(root)},
        {"id":"CMD-H1-002","argv":[python,"-m","unittest","-v",*H1_TESTS],"cwd":str(root)},
        {"id":"CMD-H1-003","argv":[python,"-c",parent_probe],"cwd":str(workspace)},
    ]


def command_plan_fingerprint(plan: list[dict]) -> str:
    payload = json.dumps(plan, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False, allow_nan=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
