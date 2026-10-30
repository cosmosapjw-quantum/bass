"""CE1-X hostile/factual scoped gates based on actual executed source/time/Rust."""
from __future__ import annotations
from fractions import Fraction as F
import json
import os
from pathlib import Path
import pytest
from research.ce1x_20261030.certify_l4 import (
    binomial_abs,tail,certify,K,Q,
)

P=Path(os.environ.get("CE1X_RESULT","/tmp/ce1x/l4_source_and_transfer.json"))
R=Path(os.environ.get("CE1X_RUST_RESULT","/tmp/ce1x/rust_l4.json"))


@pytest.fixture(scope="module")
def science():
    assert P.is_file(), "Actual exact-rational K12 run required"
    return json.loads(P.read_text())


@pytest.fixture(scope="module")
def rust():
    assert R.is_file(), "Actual original BASS native Rust run required"
    return json.loads(R.read_text())


@pytest.mark.parametrize("n,rays",[(6,216),(8,384)])
def test_original_locked_cell_source_and_moment_count(science,n,rays):
    v=science["cases"][str(n)]
    assert v["positive_octant_rays"]==rays
    assert v["original_physical_source_sha256"]==(
       "022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035")
    assert v["binomial_K"]==12 and v["maximum_total_monomial_order"]==14
    assert v["monomial_moment_count"]==len([
        (a,b,d-a-b) for d in range(1,15) for a in range(d+1) for b in range(d-a+1)
    ])+1
    assert F(v["offunit_weighted_norm_error_exact"])<F(1,10**12)


def test_actual_exact_binomial_coefficients_and_conservative_tail():
    assert binomial_abs(F(-3,2),0)==1
    assert binomial_abs(F(-3,2),1)==F(3,2)
    assert binomial_abs(F(-3,2),2)==F(15,8)
    assert binomial_abs(F(1,2),2)==F(1,8)
    assert 0<tail(F(1,2))<tail(F(-3,2))<F(1,10**10)
    with pytest.raises(ValueError,match="Unsupported"):
        tail(F(-5,2))


@pytest.mark.parametrize("n", [6,8])
def test_l4_source_lifts_to_two_times_and_exact_decimal_ceil(science,n):
    v=science["cases"][str(n)]
    for key in ("a40","a42","a44"):
        x=v["harmonic_source_errors"][key]
        assert F(0)<F(x["exact"])<=F(x["ceil_27"])
        alpha=v["fractional_harmonic_source_errors"][key]
        assert F(0)<F(alpha["exact"])<=F(alpha["ceil_27"])
    E=v["energy_source_error_upper"]
    assert F(0)<F(E)<=F(v["energy_source_error_ceil_27"])
    assert F(v["source_only_cross_kernel_error"])>0
    assert F(v["source_only_cross_kernel_error"])<=F(v["source_only_cross_kernel_error_ceil_27"])
    for steps in (4,8,16):
        c=v["time_path_cases"][str(steps)]
        source=F(c["source_kernel_upper_exact"])
        geom=F(c["geometry_kernel_upper_exact"])
        total=F(c["total_cross_kernel_upper_exact"])
        assert total==source+geom
        assert total<=F(c["total_cross_kernel_upper_ceil_27"])
        assert 0<source<total<F(1,100)
        assert len(c["parent_path_coefficients_sha256"])==64
        assert c["fresh_time_mpfr_carrier_SHA_BINDING"]=="EXACT_IN_SAME_CI"
        assert c["fresh_time_mpfr_h_upper"]<1e-5


def test_geometry_reduction_at_fixed_gl_source_not_an_accuracy_gate(science):
    for v in science["cases"].values():
        x=[F(v["time_path_cases"][str(j)]["geometry_kernel_upper_exact"]) for j in (4,8,16)]
        assert x[0]>x[1]>x[2]>0
    assert science["upper_dag"]=="9/15" and science["production_ready"] is False


def test_original_bass_rust_six_cases_and_independent_numpy_agree(science,rust):
    assert rust["status"]=="SCOPED_BASS_NATIVE_RUST_L4_PARITY_AND_K4_CROSSCHECK_PASS"
    assert len(rust["cases"])==6
    for order in (6,8):
        for step in (4,8,16):
            key=f"GL{order}_STEPS{step}"
            data=rust["cases"][key]
            source=science["cases"][str(order)]
            assert data["stored_source_ray_sha256"]==source["source_ray_sha256"]
            assert data["stored_source_mass_sha256"]==source["source_mass_sha256"]
            assert data["certified_path_coefficients_sha256"]==(
                source["time_path_cases"][str(step)]["parent_path_coefficients_sha256"])
            assert data["epoch_count"]==41
            assert data["max_abs_native_Rust_vs_NumPy_l4"]<4e-11
            assert abs(data["K4_delta_0_008_native"]-
                       data["K4_delta_0_008_independent_NumPy"])<1e-10
            assert data["formal_MPFR_integral_from_Rust"]=="NOT_RUN"


def test_source_geometry_bounds_compatible_with_GL_cross_source_falsifier(rust):
    for row in rust["GL6_GL8_intercase"].values():
        assert row["observed_bound_pass"] is True
        assert 0<=row["empirical_GL6_vs_GL8_K4_delta"]<=row["sum_of_two_certified_continuum_upper"]


def test_pressure_only_cannot_identify_l4_even_for_positive_measures():
    # Exact Legendre polynomial P4: integrating over z in [-1,1].
    p={4:F(35,8),2:F(-30,8),0:F(3,8)}
    def mean_power(k):
        return F(1,k+1) if k%2==0 else F(0)
    integral_p4=sum((coeff*mean_power(power) for power,coeff in p.items()),F(0))
    integral_z2_p4=sum((coeff*mean_power(power+2) for power,coeff in p.items()),F(0))
    integral_p4_sq=sum((a*b*mean_power(i+j) for i,a in p.items()
                        for j,b in p.items()),F(0))
    assert integral_p4==0 and integral_z2_p4==0
    assert integral_p4_sq==F(1,9)>0
    # 1+/-eta*P4 positive at eta=1/10; both have same E/P
    # but different positive/negative l4 projection.


@pytest.mark.parametrize("wrong", [0,3,True,12])
def test_out_of_scope_gl_certificate_rejected(wrong):
    with pytest.raises(ValueError):
        certify(wrong,{})
