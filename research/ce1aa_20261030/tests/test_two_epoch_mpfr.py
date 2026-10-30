"""Source/path-locked direct MPFR192 l4 continuum rank2 certificate tests."""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import json
import numpy as np
import pytest
from research.ce1aa_20261030 import two_epoch_mpfr as aa


@pytest.fixture(scope="module")
def actual(tmp_path_factory):
    out=tmp_path_factory.mktemp("ce1aa")/"direct_mpfr.json"
    return aa.run(out)


def test_six_original_source_locked_paths_and_old_h_gate(actual):
    assert len(actual["cases"])==6
    assert actual["source_sha256"]==aa.SOURCE_SHA
    assert actual["whole_python_rust_mpfr_formal_program_proof"]=="NOT_RUN"
    assert actual["original_K12_source_rerun"] is False
    assert "TARGETED_SCOPED" in actual["full_time_residual_when_regenerated_path_sha_differs"]
    for x in actual["cases"].values():
        assert x["MPFR_bits"]==192
        assert x["original_strict_h_target"]==1e-5
        assert 0<x["old_h_certified_upper"]<1e-5
        assert x["E0_MPFR_lower"]>.6 and x["ET_MPFR_lower"]>.6
        assert x["rust_vs_exact_stored_MPFR_midpoint_max_abs"]<2e-12
        assert x["path_time_certificate_binding"] in (
            "DIRECT_BYTE_IDENTICAL_PREDECESSOR_REUSE",
            "NEW_BYTE_PATH_FRESH_WHOLE_PANEL_MPFR192_CERTIFIED")
        if x["path_time_certificate_binding"].startswith("NEW_BYTE_PATH"):
            proof=x["fresh_runner_path_MPFR192_full_time_proof"]
            assert proof is not None and proof["target_met"]
            assert proof["path_sha256"]["coefficients"]==x["path_coefficients_binary_git_sha256"]
            assert proof["physical_source_sha256"]==aa.SOURCE_SHA
            assert len(proof["panels"])==int(x["case"].split("STEPS")[1])
            assert x["active_path_h_certified_upper"]<1e-5
        else:
            assert x["fresh_runner_path_MPFR192_full_time_proof"] is None
        assert x["original_Rust_CSV_SHA256"] == aa.hashlib.sha256(
            (aa.INPUT/(x["case"]+"_BASS_RUST_SKY.csv")).read_bytes()).hexdigest()


def test_new_real_continuum_noncollinearity_for_both_gl_orders(actual):
    for name in ("GL6_STEPS16","GL8_STEPS16"):
        case=actual["cases"][name]
        assert case["continuum_two_time_minor_lower_outward"]>0
        assert case["continuum_two_time_minor_upper_outward"]>case["continuum_two_time_minor_lower_outward"]
        assert case["continuum_two_time_principal_lambda_min_lower_outward"]>0
        assert case["continuum_second_mode_rank_at_least_two_certified_if_parent_claim_valid"]


def test_no_fake_zero_mode_at_looser_panel_certificates(actual):
    # An insufficient prior *bound* is not a physical zero mode or a failed IVP.
    for n in (6,8):
        for s in (4,8):
            case=actual["cases"][f"GL{n}_STEPS{s}"]
            assert case["continuum_two_time_minor_lower_outward"]<0
            assert case["continuum_two_time_principal_lambda_min_lower_outward"] is None


def test_approximate_positive_geometry_broad_scale(actual):
    d=actual["cases"]["GL8_STEPS16"]["continuum_two_time_minor_lower_outward"]
    assert 7e-8<d<9e-8
    d6=actual["cases"]["GL6_STEPS16"]["continuum_two_time_minor_lower_outward"]
    assert 6e-8<d6<9e-8
    assert abs(d-d6)<3e-8


def test_source_and_time_blob_guards():
    t,l,p=aa.source_and_time_locks()
    assert t["rust_source_blob"]==aa.RUST_BLOB
    assert l["source"]==aa.SOURCE_SHA
    assert p["physical_rows"]==10086


def test_invalid_original_path_certificate_rejected():
    t,l,p=aa.source_and_time_locks()
    damaged=deepcopy(l)
    damaged["cases"]["8"]["time_path_cases"]["16"]["parent_path_coefficients_sha256"]="0"*64
    with pytest.raises(ValueError,match="Original predecessor certified path SHA inconsistency"):
        aa.certify_pair(8,16,t,damaged,p)


def test_mismatched_source_fails_closed(monkeypatch):
    t,l,p=aa.source_and_time_locks()
    original=aa.sample_gl_source
    def altered(order):
        s=original(order)
        s.mass=np.asarray(s.mass).copy()
        s.mass[0]=np.nextafter(s.mass[0],np.inf)
        return s
    monkeypatch.setattr(aa,"sample_gl_source",altered)
    with pytest.raises(ValueError,match="ray/mass dyadic identity"):
        aa.certify_pair(8,16,t,l,p)


def test_malformed_pr270_kernel_bound_rejected():
    t,l,p=aa.source_and_time_locks()
    damaged=deepcopy(l)
    damaged["cases"]["8"]["time_path_cases"]["16"]["total_cross_kernel_upper_ceil_27"]="0.250000000000000000000000000"
    with pytest.raises(ValueError,match="positive l4 bound"):
        aa.certify_pair(8,16,t,damaged,p)


def test_false_positive_small_magnitude_rejected():
    t,l,p=aa.source_and_time_locks()
    damaged=deepcopy(t)
    damaged["cases"]["8"]["cases"]["16"]["target_h"]=1e-12
    with pytest.raises(ValueError,match="Original h gate"):
        aa.certify_pair(8,16,damaged,l,p)


def test_exact_mpfr_pi_and_cubic_endpoint():
    pi=aa.exact_pi()
    assert pi.lower<3.1415926535897936
    assert pi.upper>3.141592653589793
    from bianchi.nonperturbative.einstein_interval import BITS
    assert BITS==192


def test_no_unjustified_production_or_ensemble_claims(actual):
    assert actual["upper_dag"]=="9/15"
    assert actual["ce1"]=="PARTIAL"
    assert actual["new_upper_nodes"]==0
    assert actual["original_h_target_unchanged"]==1e-5
    assert not actual["production_ready"] and not actual["merge_ready"]
    assert not actual["auto_next"] and actual["distinct_author_R6_C9"]=="NOT_RUN"
    assert all(not x["ensemble_covariance"] for x in actual["cases"].values())
