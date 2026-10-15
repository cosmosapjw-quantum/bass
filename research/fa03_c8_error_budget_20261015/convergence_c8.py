"""FA03-C8 source-locked empirical convergence and matched-accuracy CPU budgets.

The rigorous exact-ODE energy GL-n bound is imported from spectral_cert.
RK4 convergence, floating accuracy, angular refinement and measured performance
are *empirical*, not interval-enclosed certificates of the full solver.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import statistics
import sys
import time
import tracemalloc

import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(HERE.parent/"fa03_c7_polarized_batch_20261015"))
import spectral_cert as cert
import batch_transport as orig
import stokes_vector as fast


def _err(Y,Z):
    return max(orig.trace_norm(x-y) for x,y in zip(Y,Z))


def _time(f,reps=3):
    results=[]
    saved=None
    f()  # physical source and all paths warmed outside timing
    for _ in range(reps):
        start=time.perf_counter()
        saved=f()
        results.append(time.perf_counter()-start)
    return {"median_s":statistics.median(results),"seconds":results}, saved


def _same_case(rays,steps,ne,eps):
    nr,nphi=rays
    return fast.solve_energy_real(eps,steps=steps,nr=nr,nphi=nphi,ne=ne)


def convergence_one(rays,steps=(16,32,64,128,256,512),energy_orders=(2,3,4,5,6,8),
                    reference_steps=1024,ref_energy_order=24):
    """Return data, not automatically admitting tolerance from observed differences."""
    nr,nphi=rays
    eps=[-.1,0,.1]
    cert.source_lock()
    if reference_steps <= max(steps):raise ValueError("reference must be strictly finer")
    fixed_energy_order=6
    high_time=_same_case(rays,reference_steps,fixed_energy_order,eps)
    time=[]
    last=None
    for nstep in steps:
        F=_same_case(rays,nstep,fixed_energy_order,eps)
        time.append({"steps":nstep,"max_eps_error_vs_1024_same_GL6":_err(F,high_time),
            "successive_step_difference":_err(F,last) if last is not None else None,
            "max_stokes_psd_eigen_error":float(min(np.linalg.eigvalsh(q).min() for q in F)),
            "source_identity":"unchanged FA03"})
        last=F
    same_step=128
    hi_energy=_same_case(rays,same_step,ref_energy_order,eps)
    es=[]
    for n in energy_orders:
        F=_same_case(rays,same_step,n,eps)
        es.append({"ne":n,"steps":same_step,
             "empirical_trace_difference_vs_GL24":_err(F,hi_energy),
             "exact_ODE_energy_quadrature_bound_trace":float(cert.certificate(n)),
             "exact_ODE_energy_quadrature_bound_fraction":str(cert.certificate(n)),
             "time_RK4_error_certified":False,
             "angular_continuum_error_certified":False})
    return {"grid":[nr,nphi],"rays":nr*nphi,
        "same_source_epoch":"FA03 fixed Kasner observer and energy band",
        "time_reference":{"steps":reference_steps,"energy_GL":fixed_energy_order,
            "status":"fine-discretization comparator, NOT exact ODE"},
        "time_refinements":time,"energy_refinements":es,
        "absolute_time_error_certified":None,
        "absolute_roundoff_error_certified":None,
        "continuous_cap_angular_error_certified":None}


def bench_reduced_energy(rays,steps=128,energy_choices=(4,5,6,8),reps=3):
    if reps<2:raise ValueError(">=2 repeat wall medians")
    eps=[-.1,0,.1]
    nr,nphi=rays
    funcs={}
    for ne in energy_choices:
        funcs[f"real_stokes_GL{ne}"]=(lambda q=ne:_same_case(rays,steps,q,eps))
    funcs["original_separate_Jones_GL8"]=(lambda:np.stack(
        [orig.fa03.solve_energy(.008,.01,e,steps=steps,nr=nr,nphi=nphi,ne=8) for e in eps]))
    measure={}
    baseline=funcs["original_separate_Jones_GL8"]()
    for name,fn in funcs.items():
        time_data,output=_time(fn,reps)
        time_data["max_tracenorm_vs_original_Jones_GL8"]=_err(output,baseline)
        measure[name]=time_data
    old=measure["original_separate_Jones_GL8"]["median_s"]
    reference=measure["real_stokes_GL8"]["median_s"]
    for n in energy_choices:
        d=measure[f"real_stokes_GL{n}"]
        d["measured_speedup_vs_original_Jones_GL8"]=old/d["median_s"]
        d["measured_speedup_vs_real_GL8"]=reference/d["median_s"]
        d["source_locked_certified_spectral_error"]=float(cert.certificate(n))
        d["nominal_state_bytes"]=3*nr*nphi*n*4*8
    measure["original_separate_Jones_GL8"]["nominal_state_bytes"]=3*nr*nphi*8*4*16
    return {"rays":nr*nphi,"steps":steps,
       "epsilon":eps,"reference_Jones_energy_order":8,
       "energy_choices":list(energy_choices),
       "repetitions":reps,
       "measured":measure,
       "memory_scope":"nominal storage for state arrays, not full transient RSS",
       "matched_accuracy_scope":"fixed identical RK4 step count, with separately recorded exact ODE spectral GL bound; no claimed total certified error"}


def run():
    cert.source_lock()
    grids=[(3,12),(6,24),(10,48)]
    conv=[convergence_one(g) for g in grids]
    benchmark=[bench_reduced_energy(g) for g in grids]
    return {"schema":"bass.fa03.c8.empirical_numerics_and_matched_energy.v1",
        "source_sha256":cert.SHA,
        "valid_rigorous_spectral_cert":cert.analytic_claims(),
        "grids":grids,
        "epsilon":[-.1,0,.1],
        "convergence":conv,
        "benchmark":benchmark,
        "replay_limitation":"Timing varies by host/other load; state numerical values/source SHAs can be compared.",
        "numeric_roundoff_admission":None,
        "exact_time_ODE_error_admission":None,
        "continuous_angular_cap_certified_error":None,
        "native_rei_abundance_scientific_admission":None}


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    if a.out.exists():raise FileExistsError(a.out)
    start=time.perf_counter();data=run()
    data["elapsed_s"]=time.perf_counter()-start
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n")
    for c,b in zip(data["convergence"],data["benchmark"]):
        print("GRID",c["rays"],"time step64error",c["time_refinements"][2]["max_eps_error_vs_1024_same_GL6"],
           "GL4cmp",c["energy_refinements"][2]["empirical_trace_difference_vs_GL24"])
        for ne in (4,5,6,8):
            r=b["measured"][f"real_stokes_GL{ne}"]
            print("  ENERGY",ne,"time",round(r["median_s"],5),
               "vs_orig_GL8",round(r["measured_speedup_vs_original_Jones_GL8"],3),
               "vs_real_GL8",round(r["measured_speedup_vs_real_GL8"],3),
               "trace_GL8",r["max_tracenorm_vs_original_Jones_GL8"])
    print("TOTAL_SEC",data["elapsed_s"])
