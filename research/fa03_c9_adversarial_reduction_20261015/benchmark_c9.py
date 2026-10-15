"""C9 physically matched tensor-reduction benchmark, no invented acceleration.

Separates live FA03 physical RK4 and final reduction costs. The C7 reference
is the same fixed observer/energies/non-grey 3-case model.
"""
from __future__ import annotations
import argparse,json,statistics,time,tracemalloc,sys
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import deterministic_reducer as d
import stokes_vector as old
import batch_transport as b

def timed(fn,reps=5):
    fn()
    samples=[];state=None
    for _ in range(reps):
        st=time.perf_counter()
        state=fn()
        samples.append(time.perf_counter()-st)
    return statistics.median(samples),samples,state

def tracked(fn):
    fn()
    tracemalloc.start()
    try:
        fn()
        active,peak=tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return peak

def run(reps=5,steps=128):
    if reps<2 or steps<16:raise ValueError("at least 2 repetition, >=16 RK4 steps")
    data=[]
    for nr,nphi in ((3,12),(6,24),(10,48)):
        es=np.array([-.1,0,.1],np.float64)
        ell,w=b._prepared_rays(nr,nphi)
        ne=4
        x,ew= np.polynomial.legendre.leggauss(ne)
        energy=1+.02*x;ew=ew/2
        Y=d._solve_per_ray(es,ell,energy,steps)
        truth=d.exact_dyadic_tensor_sum(Y,w,ew)
        variants={
          "numpy_einsum":lambda:np.einsum("n,e,mnek->mk",w,ew,Y,optimize=True),
          "pairwise_numpy":lambda:d.pairwise_tensor_sum(Y,w,ew),
          "math_fsum":lambda:np.array([[__import__('math').fsum(((Y*ew[None,None,:,None])*w[None,:,None,None]).reshape(3,len(w)*len(ew),4)[i,:,k]) for k in range(4)] for i in range(3)])
        }
        red=[]
        for key,fn in variants.items():
            med,samples,S=timed(fn,reps)
            maxgap=max((abs(__import__('fractions').Fraction.from_float(float(S[i,k]))-truth[i][k]) for i in range(3) for k in range(4)))
            red.append({"method":key,"median_seconds":med,"samples_seconds":samples,
                 "max_exact_dyadic_scalar_error":float(maxgap)})
        cond=d.scalar_bounds(Y,w,ew)
        assert max(z["max_exact_dyadic_scalar_error"] for z in red)<=float(__import__('fractions').Fraction(cond["each_stokes_absolute_error_bound"]))
        full={}
        for method,fun in (
         ("legacy_C7_real",lambda:old.solve_energy_real(es,steps=steps,nr=nr,nphi=nphi,ne=ne,output="stokes")),
         ("C9_pairwise",lambda:d.actual_fa03_reduction(es,steps=steps,nr=nr,nphi=nphi,ne=ne,mode="pairwise")),
         ("C9_math_fsum",lambda:d.actual_fa03_reduction(es,steps=steps,nr=nr,nphi=nphi,ne=ne,mode="math_fsum"))):
            med,samples,S=timed(fun,reps)
            maxdiff=float(np.max(abs(S-red[0]["max_exact_dyadic_scalar_error"]))) if False else \
                  float(np.max(abs(S-variants["numpy_einsum"]())))
            full[method]={"median_seconds":med,"samples_seconds":samples,
                "max_abs_diff_vs_given_same_source_state":maxdiff}
        data.append({"rays":nr*nphi,"steps":steps,"nenergy":ne,"epsilon":[-.1,0,.1],
           "reducer_roundoff_conditional":cond,
           "reducer_bench":red,
           "full_source_bench":full,
           "output_match_tol":"binary64 physical source state to original finite source, not validated full angular/time error"})
    return {"schema":"bass.fa03.c9.reduction_host_benchmark.v1","repetitions":reps,
       "settings":"same real source GL4, 128 RK4, three eps; warmed medians on Ubuntu, no local Codex",
       "source_sha256":b.SHA,
       "results":data,
       "whole_solver_roundoff_certified":None,
       "whole_rei_solver_speedup":None,
       "parallel_C7_past_result":"2/4 ray threads slower on this CPU and same source; not enabled as default"}

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--reps",type=int,default=5)
    a=ap.parse_args()
    if a.out.exists():raise FileExistsError(a.out)
    start=time.perf_counter()
    j=run(a.reps)
    j["total_elapsed_seconds"]=time.perf_counter()-start
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(j,indent=2)+"\n")
    for r in j["results"]:
        print("RAYS",r["rays"],"REDUCTION",[(z["method"],round(z["median_seconds"],7),z["max_exact_dyadic_scalar_error"]) for z in r["reducer_bench"]],
          "FULL",[(n,round(v["median_seconds"],5)) for n,v in r["full_source_bench"].items()],flush=True)
    print("ELAPSED",j["total_elapsed_seconds"])
