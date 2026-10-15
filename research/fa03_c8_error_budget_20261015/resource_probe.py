"""C8 real measured peak allocations and deterministic physical ray-reduction survey."""
from __future__ import annotations
import argparse,json,statistics,time,tracemalloc
from pathlib import Path
import numpy as np
import sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/"fa03_c7_polarized_batch_20261015"))
import batch_transport as base
import stokes_vector as s

def traces(fn):
    fn()  # compiled imports/initial NumPy cache warm outside tracemalloc
    tracemalloc.start()
    try:
        out=fn()
        current,peak=tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return peak,out

def wall(fn,n=3):
    fn()
    a=[];last=None
    for _ in range(n):
        s=time.perf_counter()
        last=fn()
        a.append(time.perf_counter()-s)
    return statistics.median(a),a,last

def execute(steps=128):
    grids=[(3,12),(6,24),(10,48)]
    records=[]
    eps=[-.1,0,.1]
    for nr,nphi in grids:
        ell,w=base._prepared_rays(nr,nphi)
        reference=s.solve_energy_real(eps,steps=steps,ell=ell,w=w,ne=8)
        timing=[]
        for ne in (4,5,8):
            fn=lambda ne=ne:s.solve_energy_real(eps,steps=steps,ell=ell,w=w,ne=ne)
            peak,out=traces(fn)
            m,reps,_=wall(fn)
            timing.append({"ne":ne,"tracemalloc_peak_bytes":peak,"median_wall_s":m,
                           "times_s":reps,
                           "max_ref_GL8_trace_delta":max(base.trace_norm(x-y) for x,y in zip(out,reference)),
                           "nominal_stokes_state_bytes":3*len(w)*ne*4*8,
                           "source_bound_status":"energy exact-Ode theorem separate, RK4+float not included"})
        records.append({"rays":len(w),"grid":[nr,nphi],"settings":{"steps":steps,"eps":eps},
                        "measurements":timing})
    ell,w=base._prepared_rays(10,48)
    original=s.solve_energy_real(eps,steps=steps,ell=ell,w=w,ne=4)
    parallel=[]
    for workers in (1,2,4):
        for chunk in (120,):
            fn=lambda:s.solve_energy_real(eps,steps=steps,ell=ell,w=w,ne=4,ray_chunk=chunk,workers=workers)
            t,values,F=wall(fn)
            parallel.append({"workers":workers,"chunk":chunk,
                            "actual_chunk_count":int(np.ceil(len(w)/chunk)),
                            "median_wall_s":t,"times_s":values,
                            "max_difference_vs_unchunked":max(base.trace_norm(x-y) for x,y in zip(F,original))})
    reduction=[]
    for nr,nphi in ((3,12),(6,24)):
        ell,w=base._prepared_rays(nr,nphi)
        original=s.solve_energy_real(eps,steps=steps,ell=ell,w=w,ne=4)
        for chunk in (1,4,12,len(w)):
            out=s.solve_energy_real(eps,steps=steps,ell=ell,w=w,ne=4,ray_chunk=chunk,workers=1)
            reduction.append({"grid":[nr,nphi],"chunk":chunk,"nchunks":int(np.ceil(len(w)/chunk)),
                        "max_trace_difference":max(base.trace_norm(x-y) for x,y in zip(out,original)),
                        "bitwise_equal":bool(np.array_equal(out,original))})
    return {"schema":"bass.fa03.c8.host_memory_parallel_roundoff.v1",
            "scope":"same tested source; 64bit host, 128 RK4, 3 eps; one-host measured allocations and threads",
            "memory_scope":"tracemalloc-traced Python/NumPy allocations, not full process max RSS",
            "timings":records,"parallel":parallel,"roundoff_reduction":reduction,
            "intrinsic_solver_roundoff_certification":None,
            "performance_reproducibility_across_CPU":None}

if __name__=="__main__":
    pa=argparse.ArgumentParser();pa.add_argument("--out",type=Path,required=True)
    a=pa.parse_args()
    if a.out.exists():raise FileExistsError(a.out)
    d=execute()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
    for r in d["timings"]:
        print("RAYS",r["rays"],[(v["ne"],round(v["median_wall_s"],5),v["tracemalloc_peak_bytes"]) for v in r["measurements"]],flush=True)
    print("PARALLEL",[(x["workers"],round(x["median_wall_s"],5)) for x in d["parallel"]],flush=True)
    print("ROUND_OFF",[(x["grid"],x["chunk"],x["max_trace_difference"]) for x in d["roundoff_reduction"]],flush=True)
