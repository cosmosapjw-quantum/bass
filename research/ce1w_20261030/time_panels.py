"""CE1-W: same exact binary GL6/GL8 source, different RK4/Hermite time panels.

A genuine BASS CE1 numerical-science study. Uses the previously proved
exact-rational angular source bound and the existing MPFR192 fourth-derivative
residual / exact binary Hermite knot jumps. No new source/continuum closure and
no replacement of a rigorous interval by the independent Rust binary64 oracle.

Run: PYTHONPATH=. python research/ce1w_20261030/time_panels.py --output PATH
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
from time import perf_counter

import numpy as np

from bianchi.nonperturbative.einstein_error_budget import rk4_path, HermitePath
from bianchi.nonperturbative.einstein_interval import (
    Interval as I, _iv_fraction as iv, _bernstein_box_binary,
    residual_taylor_mpfr, propagate_interval,
)
from bianchi.nonperturbative.einstein_tabulated_time import _panel_endpoint_jump
from research.ce1u_20261030.certified_gl_source import (
    sample_gl_source, certify_gl_source, SOURCE_SHA, SHEAR, sha,
)
from research.ce1v_20261030.cross_certify import load_donor, evidence_lock

HORIZON = 0.08
STEPS = (4, 8, 16)
ORDERS = (6, 8)
FIXED_TARGET_H = 1e-5
RUST_SOURCE_BLOB = "a29b12b5e7b0d529bddaf9eac53cfdb984ddaa84"


def _blob_array(a) -> str:
    arr = np.asarray(a)
    h = hashlib.sha256()
    h.update(repr((arr.shape, arr.dtype.str)).encode("ascii"))
    h.update(arr.tobytes(order="C"))
    return h.hexdigest()


def _continuum_initial(source, path) -> float:
    sx, sy = (Fraction.from_float(float(x)) for x in SHEAR[:2])
    sig = [iv(sx), iv(sy), iv(-(sx + sy))]
    E = iv(source.continuum_energy)
    root = ((E + sum((x*x for x in sig), I(0))/I(2))/I(3)).sqrt()
    initial = [root+x for x in sig]
    if any(v.lower <= 0 or v.upper >= .8 for v in initial):
        raise ValueError("Nonexpanding original physical initial data")
    if any(not 0 < float(h) < .8 for h in path.states[0,3:]):
        raise ValueError("Stored initial state outside invariant h-box")
    diffs = [initial[k]-I(float(path.states[0,3+k])) for k in range(3)]
    return max(max(abs(v.lower),abs(v.upper)) for v in diffs)


def _certify_same_source(source, donor, order, steps, subcells=1):
    if type(steps) is not int or steps not in STEPS:
        raise ValueError("Fixed CE1-W time-panel counts 4/8/16 only")
    if type(subcells) is not int or subcells not in (1, 2):
        raise ValueError("subcells 1/2 only, no zero-work certificate")
    start = perf_counter()
    eta_fraction = evidence_lock(order, source, donor)
    eta = iv(eta_fraction)
    if eta.lower < 0 or eta.upper >= 1e-8:
        raise ValueError("Original exact-rational pressure source is not admitted")
    path = rk4_path(source, source.initial_state(tuple(SHEAR)), HORIZON,
                    steps, backend="python_oracle")
    time_build = perf_counter()-start
    if not isinstance(path, HermitePath) or len(path.times)!=steps+1:
        raise ValueError("Original RK4/Hermite path contract failed")
    if path.times[0] != 0 or path.times[-1] != HORIZON:
        raise ValueError("Original exact-binary proper-time endpoints changed")
    if not np.array_equal(path.coefficients[:,0,:], path.states[:-1]):
        raise ValueError("Stored Hermite origins differ from original binary state knots")
    if not np.array_equal(path.states[0],source.initial_state(tuple(SHEAR))):
        raise ValueError("Stored initial state mismatch")
    if not np.isfinite(path.coefficients).all():
        raise ValueError("Nonfinite Hermite polynomial")
    for j in range(steps):
        low, high = _bernstein_box_binary(path,j)
        if min(low)<0 or max(high[:3]) >= .07 or min(low[3:]) <= 0:
            raise ValueError("Certified exact whole-panel hull outside original positive box")
    initial_h = _continuum_initial(source,path)
    initial=[I(0),I(initial_h)]
    source_acc=[I(0),I(0)]
    time_acc=[I(0),I(0)]
    start_mpfr=perf_counter()
    rows=[]
    for j in range(steps):
        defect=residual_taylor_mpfr(source,path,j,subcells=subcells)
        d=I(float(path.times[j+1]))-I(float(path.times[j]))
        if d.lower <= 0:
            raise ValueError("Nonpositive exact binary panel duration")
        initial=propagate_interval(initial,d,I(1),I(0),I(0))
        source_acc=propagate_interval(source_acc,d,I(1),I(0),eta)
        time_acc=propagate_interval(
            time_acc,d,I(1),I(float(defect["ell_defect"])),I(float(defect["h_defect"]))
        )
        jump_ell,jump_h=_panel_endpoint_jump(path,j)
        time_acc=[time_acc[0]+I(jump_ell),time_acc[1]+I(jump_h)]
        rows.append({
            "j":j,"u_start":float(path.times[j]),"u_end":float(path.times[j+1]),
            "ell_defect_upper":float(defect["ell_defect"]),
            "h_defect_upper":float(defect["h_defect"]),
            "fourth_derivative_upper":float(defect["fourth_derivative_bound"]),
            "knot_ell_upper":float(jump_ell),"knot_h_upper":float(jump_h),
            "cumulative_h_time_upper":time_acc[1].upper,
            "cumulative_h_source_upper":source_acc[1].upper,
            "cumulative_h_initial_upper":initial[1].upper,
        })
    mpfr_time=perf_counter()-start_mpfr
    final_h=(initial[1]+source_acc[1]+time_acc[1]).upper
    final_ell=(initial[0]+source_acc[0]+time_acc[0]).upper
    if not math.isfinite(final_h) or not 0 < final_h < FIXED_TARGET_H:
        raise ArithmeticError(f"Original fixed CE1 1e-5 h gate not met: {final_h}")
    return {
        "schema":"bass.ce1w.same_gl_source_panel_count_mpfr192.v1",
        "order":order,"rays":len(source.mass),"steps":steps,"subcells":subcells,
        "u_end":HORIZON,"target_h":FIXED_TARGET_H,"target_met":True,
        "physical_source_sha256":SOURCE_SHA,
        "source_ray_sha256":sha(np.asarray(source.n,dtype="<f8").tobytes()),
        "source_mass_sha256":sha(np.asarray(source.mass,dtype="<f8").tobytes()),
        "path_sha256":{
            "times":_blob_array(path.times),
            "states":_blob_array(path.states),
            "coefficients":_blob_array(path.coefficients)
        },
        "epsilon_source_fraction":str(eta_fraction),
        "epsilon_source_outward_upper":eta.upper,
        "initial_h_upper":initial[1].upper,
        "source_h_upper":source_acc[1].upper,
        "time_jump_h_upper":time_acc[1].upper,
        "final_h_upper":final_h,
        "final_ell_upper":final_ell,
        "cost":{
            "rk4_path_build_seconds":time_build,
            "mpfr_residual_and_comparison_seconds":mpfr_time,
            "total_seconds":perf_counter()-start
        },
        "panels":rows,"production_ready":False,"merge_ready":False,
        "upper_dag":"9/15","formal_program_verification":"NOT_RUN",
        "rust_role":"Binary64 independent BASS native E/P/Eprime parity, not MPFR proof",
    }


def experiment(*,output,steps=STEPS,subcells=1):
    orders={}
    for n in ORDERS:
        src=sample_gl_source(n)
        donor=load_donor(n)
        eta_fraction=evidence_lock(n,src,donor)
        old=certify_gl_source(n,src)
        if iv(eta_fraction).upper > old["total_pressure_error_upper"]:
            raise ArithmeticError("Different source hierarchy / original GL epsilon order")
        scenarios={}
        for step in steps:
            row=_certify_same_source(src,donor,n,step,subcells=subcells)
            scenarios[str(step)]=row
            print(
                f"CE1W_GL{n}_STEPS{step}_SCOPED_MPFR_PASS "
                f"h={row['final_h_upper']:.17g} "
                f"time={row['time_jump_h_upper']:.17g} "
                f"source={row['source_h_upper']:.17g} "
                f"wall={row['cost']['total_seconds']:.3f}",
                flush=True,
            )
        times=[scenarios[str(k)]["time_jump_h_upper"] for k in steps]
        orders[str(n)]={
            "source_ray_sha256":scenarios[str(steps[0])]["source_ray_sha256"],
            "source_mass_sha256":scenarios[str(steps[0])]["source_mass_sha256"],
            "source_contract_not_changed":len({v["source_ray_sha256"] for v in scenarios.values()})==1
                                               and len({v["source_mass_sha256"] for v in scenarios.values()})==1,
            "time_bound_monotone_nonincreasing":all(times[i+1]<=times[i] for i in range(len(times)-1)),
            "cases":scenarios,
        }
        if not orders[str(n)]["source_contract_not_changed"]:
            raise RuntimeError("Panel count modified stored source identity")
    payload={
        "unit":"CE1W_FIXED_GL_SOURCE_RK4_TIME_PANELS",
        "date":"2026-10-30",
        "source":"Original frozen six cell GL6/GL8, no smoothing, time panel experiment only",
        "parent_pr":266,
        "parent_head":"2d5076ecb2307cea39c1b608396c34050021ebc3",
        "rust_source_blob":RUST_SOURCE_BLOB,
        "exact_source_proof_pr":264,"source_comparison_pr":265,
        "python":sys.version,"numpy":np.__version__,"platform":platform.platform(),
        "orderno":list(ORDERS),"steps":list(steps),"cases":orders,
        "accepted_scope":"MPFR192 original scalar pressure-source/4th-derivative time comparison; not production",
        "new_top_level_nodes":0,"upper_dag":"9/15","ce1":"PARTIAL",
        "production_ready":False,"merge_ready":False,"auto_next":False
    }
    out=Path(output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    return payload


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",required=True)
    parser.add_argument("--steps",default="4,8,16")
    parser.add_argument("--subcells",type=int,default=1)
    x=parser.parse_args()
    chosen=tuple(int(t) for t in x.steps.split(","))
    if len(chosen)!=len(set(chosen)) or not chosen or any(k not in STEPS for k in chosen):
        raise ValueError("Unique ordered 4,8,16 CE1-W step choices only")
    experiment(output=x.output,steps=chosen,subcells=x.subcells)
