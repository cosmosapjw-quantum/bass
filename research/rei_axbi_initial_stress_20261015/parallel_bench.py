"""Measure serial vs 2/4-thread same-input Einstein–Vlasov case solve.

NumPy vector RK4 is separate and already measured. Threading is a genuine
workload experiment, NOT a native subagent dispatch or claimed speedup.
"""
from __future__ import annotations
import argparse,json,time,statistics
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np
from einstein_vlasov import KineticStressBackground,Initial
from vector_batch import CASES,solve_many

def one(pair):
    q,k=pair
    p=KineticStressBackground(Initial(q,k)).at_a(.2)
    return np.array([p["b"],p["s_per_s"]/p["h_per_s"],p["elapsed_proper_s"]/4.279e16],dtype=float)

def profile(reps=4):
    results={}
    reference=np.stack([one(q) for q in CASES])
    for workers in (1,2,4):
        vals=[]
        for j in range(reps):
            t=time.perf_counter()
            if workers==1:
                result=np.stack([one(q) for q in CASES])
            else:
                with ThreadPoolExecutor(max_workers=workers) as pool:
                    result=np.stack(list(pool.map(one,CASES)))
            vals.append(time.perf_counter()-t)
            if not np.array_equal(result,reference):
                raise AssertionError("THREAD_CASE_ORDER_NONDETERMINISM")
        results[str(workers)]={"median_s":statistics.median(vals),
                               "repeats_s":vals,
                               "exact_output_identity":True}
    vals=[]
    for _ in range(reps):
        t=time.perf_counter()
        f=solve_many(steps=128,order=16)
        vals.append(time.perf_counter()-t)
        err=max(abs(f["b_end"][i]-reference[i,0]) for i in range(len(CASES)))
        if err>2e-9:raise AssertionError("VECTORIZED_CONVERGENCE_FALSE_PASS")
    return {"schema":"bass.rei.axbi.initial_stress.parallel_and_vector_cpu.v1",
        "source_cases":CASES,"n_cases":len(CASES),
        "DOP853_parallel_workers":results,
        "vectorized_RK4_128_GL16":{"median_s":statistics.median(vals),
           "repetitions_s":vals,"max_delta_b_requirement":2e-9},
        "performance_scope":"actual CPU same q+kappa cases, source locked, no native coupled REI trial","native_subagent":"NOT_RUN"}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    if a.out.exists():raise FileExistsError(a.out)
    z=profile()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(z,indent=2)+"\n")
    print({k:v for k,v in z.items() if k not in ("source_cases","DOP853_parallel_workers")})
    print([(k,v["median_s"]) for k,v in z["DOP853_parallel_workers"].items()])
