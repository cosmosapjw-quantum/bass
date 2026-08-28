from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "tools" / "authority" / "verify_formula_scope.py"
CANONICAL = (
    REPO
    / "provenance"
    / "authority"
    / "sci_auth_04"
    / "FORMULA_SCOPE_AUTHORITY.json"
)
FIXTURE = CANONICAL


def _run(manifest: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--repo",
            str(REPO),
            "--manifest",
            str(manifest),
        ],
        cwd=REPO,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def _mutated_manifest(tmp_path: Path, mutate) -> Path:
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    mutate(payload)
    path = tmp_path / "authority.json"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def _assert_rejected(result: subprocess.CompletedProcess[str], code: str) -> None:
    assert result.returncode != 0
    assert code in result.stderr
    assert "PASS_SCI_AUTH_04_VALIDATOR" not in result.stdout


def test_repository_authority_manifest_passes() -> None:
    result = _run(CANONICAL)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["terminal"] == "PASS_SCI_AUTH_04_VALIDATOR"
    assert payload["formula_authority"] == "TYPED_BUT_NOT_AUTO_PROMOTED"
    assert payload["scientific_equivalence"] == "UNCHANGED"


def test_overclaim_is_rejected(tmp_path: Path) -> None:
    def mutate(payload: dict[str, object]) -> None:
        payload["domains"]["collision"]["included_scope"].append(
            "ALL_MICROPHYSICS_EXACT"
        )

    _assert_rejected(_run(_mutated_manifest(tmp_path, mutate)), "OVERBROAD_SCOPE")


def test_overclaim_top_level_promotion_is_rejected(tmp_path: Path) -> None:
    def mutate(payload: dict[str, object]) -> None:
        payload["scientific_promotion"] = True

    _assert_rejected(_run(_mutated_manifest(tmp_path, mutate)), "OVERBROAD_SCOPE")


def test_surrogate_promotion_is_rejected(tmp_path: Path) -> None:
    def mutate(payload: dict[str, object]) -> None:
        surrogate = payload["domains"]["thermodynamics"]["authorities"][0]
        surrogate["classification"] = "FRESH_FORMULA_AUTHORITY"
        surrogate["fresh"] = True
        surrogate["production_runtime_authority"] = True

    _assert_rejected(_run(_mutated_manifest(tmp_path, mutate)), "SURROGATE_PROMOTION")


def test_missing_domain_authority_is_rejected(tmp_path: Path) -> None:
    def mutate(payload: dict[str, object]) -> None:
        del payload["domains"]["projector"]

    _assert_rejected(
        _run(_mutated_manifest(tmp_path, mutate)), "MISSING_DOMAIN_AUTHORITY"
    )


def test_missing_claim_policy_match_is_rejected(tmp_path: Path) -> None:
    def mutate(payload: dict[str, object]) -> None:
        payload["domains"]["collision"]["claim_policy_refs"] = ["HC01"]

    _assert_rejected(
        _run(_mutated_manifest(tmp_path, mutate)), "MANIFEST_CLAIM_MISMATCH"
    )
