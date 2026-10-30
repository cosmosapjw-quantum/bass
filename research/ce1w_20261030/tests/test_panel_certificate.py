"""Read-back science-contract tests against *executed*, never invented, CE1-W CI data."""
from __future__ import annotations
from copy import deepcopy
from fractions import Fraction
import json
import math
import os
from pathlib import Path

import pytest

from research.ce1u_20261030.certified_gl_source import sample_gl_source
from research.ce1v_20261030.cross_certify import evidence_lock, load_donor

TARGET = 1e-5
DATA = Path(os.getenv("CE1W_RESULT","/tmp/ce1w/science.json"))
RUST = Path(os.getenv("CE1W_RUST_RESULT","/tmp/ce1w/rust_parity.json"))


@pytest.fixture(scope="module")
def result():
    assert DATA.is_file(), f"Execute actual MPFR before running tests: {DATA}"
    return json.loads(DATA.read_text())


@pytest.mark.parametrize("order", [6,8])
def test_original_source_stays_identical_across_every_time_resolution(result,order):
    c=result["cases"][str(order)]
    assert c["source_contract_not_changed"]
    assert set(c["cases"])=={"4","8","16"}
    n={v["source_ray_sha256"] for v in c["cases"].values()}
    m={v["source_mass_sha256"] for v in c["cases"].values()}
    assert len(n)==len(m)==1
    source=sample_gl_source(order)
    proof=load_donor(order)
    assert evidence_lock(order,source,proof)==Fraction(proof["maximum_epsilon_source_exact"])


@pytest.mark.parametrize("order", [6,8])
def test_all_original_fourth_derivative_and_binary_knot_panels_included(result,order):
    data=result["cases"][str(order)]["cases"]
    for st in (4,8,16):
        x=data[str(st)]
        assert len(x["panels"])==st
        assert x["steps"]==st and x["subcells"]==1
        assert x["panels"][0]["u_start"]==0
        assert x["panels"][-1]["u_end"]==.08
        assert all(math.isfinite(v["h_defect_upper"]) and v["h_defect_upper"]>=0
                   and math.isfinite(v["fourth_derivative_upper"]) and v["fourth_derivative_upper"]>=0
                   and v["knot_h_upper"]>=0 for v in x["panels"])
        assert x["time_jump_h_upper"]>0 and x["source_h_upper"]>0
        assert x["final_h_upper"]<TARGET and x["target_met"]
        assert not x["production_ready"] and not x["merge_ready"]
        assert x["cost"]["mpfr_residual_and_comparison_seconds"]>0


def test_step_changes_are_real_new_rk4_trajectories(result):
    for c in result["cases"].values():
        h={case["path_sha256"]["coefficients"] for case in c["cases"].values()}
        assert len(h)==3, "Same interpolant reused across different step counts"


def test_fixed_geometry_target_is_not_sky_target(result):
    assert result["upper_dag"]=="9/15" and result["ce1"]=="PARTIAL"
    assert result["production_ready"] is False
    for c in result["cases"].values():
        for v in c["cases"].values():
            assert v["target_h"]==TARGET and v["u_end"]==.08
            assert v["source_ray_sha256"]==c["source_ray_sha256"]


def test_parent_bound_recomputed_without_guessing_prior_byte_identity(result):
    # The exact roundoff can vary across NumPy/BLAS platforms. This only
    # matches the scientific numerical scale, not the path exact byte identity.
    for c in result["cases"].values():
        x=c["cases"]["4"]
        assert 0 < x["final_h_upper"] < 1.2e-6
        assert len(x["path_sha256"]["coefficients"])==64


@pytest.mark.parametrize("order", [6,8])
def test_donor_source_sha_rebinding_is_rejected(order):
    s=sample_gl_source(order)
    cert=load_donor(order)
    invalid=deepcopy(cert)
    invalid["stored_gl_hashes"]["ray_sha256"]="0"*64
    with pytest.raises(ValueError,match="binary source"):
        evidence_lock(order,s,invalid)
    invalid=deepcopy(cert)
    invalid["K"]=11
    with pytest.raises(ValueError,match="Donor polynomial"):
        evidence_lock(order,s,invalid)


def test_original_bass_native_rust_result_is_six_scoped_paths(result):
    assert RUST.is_file(), f"Execute true original BASS Rust: {RUST}"
    obj=json.loads(RUST.read_text())
    assert obj["upper_dag"]=="9/15"
    assert set(obj["checks"])=={f"GL{n}_STEPS{k}" for n in (6,8) for k in (4,8,16)}
    for data in obj["checks"].values():
        assert data["time_samples"]==41 and data["binary_source_SHA_match"]
        assert max(data["max_abs_gaps"].values())<8e-12
        assert data["native_elapsed_seconds"]>0
    assert obj["native_b64_is_rigorous_mpfr"] is False
