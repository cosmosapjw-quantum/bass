from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
VERIFIER_PATH = ROOT / "scripts" / "verify_sync_map02d_htt_relations.py"
SPEC = importlib.util.spec_from_file_location("verify_sync_map02d", VERIFIER_PATH)
assert SPEC is not None and SPEC.loader is not None
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


def canonical_data() -> dict[str, object]:
    return VERIFY.load_json(VERIFY.CLASSIFICATION)


def test_sync_map02d_canonical_contract_passes() -> None:
    result = VERIFY.verify(canonical_data())
    assert result["status"] == "PASS"
    assert result["relations"] == 12
    assert result["source_pins"] == 8
    assert result["pending_bass_imports"] == 4
    assert result["new_htt_shared_gaps"] == 2
    assert result["duplicate_authority_count"] == 0
    assert result["dag_nodes"] == 10
    assert result["dag_edges"] == 12


def test_sync_map02d_rejects_missing_htt_prerequisite() -> None:
    data = copy.deepcopy(canonical_data())
    impact = data["impact_dag"]
    assert isinstance(impact, dict)
    impact["edges"] = [
        edge
        for edge in impact["edges"]
        if edge != ["02D_HTT", "02E_SHARED_EXPORT"]
    ]
    with pytest.raises(VERIFY.VerificationError, match="lacks HTT relation prerequisite"):
        VERIFY.verify(data)


def test_sync_map02d_rejects_global_tilt_reclassification() -> None:
    data = copy.deepcopy(canonical_data())
    firewall = data["semantic_firewall"]
    assert isinstance(firewall, dict)
    firewall["global_matter_frame_tilt"] = "IMPLEMENTED"
    with pytest.raises(VERIFY.VerificationError, match="must not own global tilt"):
        VERIFY.verify(data)


def test_sync_map02d_rejects_duplicate_formula_authority() -> None:
    data = copy.deepcopy(canonical_data())
    relations = data["relations"]
    assert isinstance(relations, list)
    relations[1]["formula_id"] = relations[0]["formula_id"]
    with pytest.raises(VERIFY.VerificationError, match="formula IDs are not unique"):
        VERIFY.verify(data)


def test_sync_map02d_rejects_silent_empirical_beta_promotion() -> None:
    data = copy.deepcopy(canonical_data())
    firewall = data["semantic_firewall"]
    assert isinstance(firewall, dict)
    firewall["empirical_beta_fit"] = "IMPLEMENTED"
    with pytest.raises(VERIFY.VerificationError, match="empirical beta was silently promoted"):
        VERIFY.verify(data)
