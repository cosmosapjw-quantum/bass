from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools/authority/verify_thermodynamics_authority.py"
AUTHORITY = ROOT / "provenance/authority/rf03/RF03_AUTHORITY.json"


def _run(*args: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--repo",
            str(ROOT),
            "--authority",
            str(AUTHORITY),
            *(str(arg) for arg in args),
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def _mutated_authority(tmp_path: Path, mutate) -> Path:
    payload = json.loads(AUTHORITY.read_text(encoding="utf-8"))
    mutate(payload)
    path = tmp_path / "RF03_AUTHORITY.json"
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def test_exact_source_bound_authority_passes_real_verifier() -> None:
    result = _run()

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["terminal"] == "PASS_RF03_AUTHORITY"
    assert payload["claim"] == "NO_PASS_RF03"
    assert payload["checks"] == {
        "authority_semantics": "PASS",
        "explicit_gamma_and_state": "PASS",
        "historical_typeii_surrogate_only": "PASS",
        "source_blob_identity": "PASS",
        "t_gamma_force_invariance": "PASS",
        "t_gamma_jvp_invariance": "PASS",
    }


def test_source_blob_mutation_is_rejected_before_authority_pass(tmp_path: Path) -> None:
    path = _mutated_authority(
        tmp_path,
        lambda payload: payload["source_blobs"].__setitem__(
            "bianchi/matter/fluid.py", "0" * 40
        ),
    )

    result = _run("--authority", path)

    assert result.returncode == 1
    assert "SOURCE_BLOB_IDENTITY_MISMATCH" in result.stderr


def test_hidden_model_or_temperature_coupling_authority_is_rejected(
    tmp_path: Path,
) -> None:
    def mutate(payload: dict) -> None:
        payload["production_matter_authority"]["model_id"] = "constant_w_default"
        payload["thermodynamics_boundary"]["T_gamma_force_role"] = "COUPLED"

    path = _mutated_authority(tmp_path, mutate)

    result = _run("--authority", path)

    assert result.returncode == 1
    assert "AUTHORITY_SEMANTICS_MISMATCH" in result.stderr


def test_receipt_embeds_hash_bound_prior_freeze_without_claim_inflation(
    tmp_path: Path,
) -> None:
    prior_payload = {
        "schema": "bass-rf03-schema-and-route-freeze/v1",
        "status": "BLOCKED_UNRESOLVED_EOS_OR_MODEL_AUTHORITY",
    }
    prior = tmp_path / "SCHEMA_AND_ROUTE_FREEZE.json"
    prior.write_text(
        json.dumps(prior_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    receipt = tmp_path / "AUTHORITY_VERIFICATION.json"

    result = _run("--prior-freeze", prior, "--receipt", receipt)

    assert result.returncode == 0, result.stderr
    stored = json.loads(receipt.read_text(encoding="utf-8"))
    assert stored["terminal"] == "PASS_RF03_AUTHORITY"
    assert stored["claim"] == "NO_PASS_RF03"
    assert stored["prior_blocker_freeze"]["availability"] == "AVAILABLE"
    assert stored["prior_blocker_freeze"]["sha256"] == hashlib.sha256(
        prior.read_bytes()
    ).hexdigest()
    assert stored["prior_blocker_freeze"]["content"] == prior_payload
