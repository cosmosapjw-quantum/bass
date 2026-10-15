"""Measured CPU and memory scaling, only for source-bounded Einstein-Vlasov.

Compare vectorized angular-entropy moments with individually evaluated
moments and parallel individual ODE cases. No GPU or full AX08 speedup.
"""
from __future__ import annotations
import argparse,json,time,statistics,tracemalloc
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import einstein_vlasov_lrs as e
import produce_stress_tables as tab

def tmed(fn,reps=3):
    fn()
    times=[]
    output=None
    for _ in range(reps):
        t=time.perf_counter();output=fn();times.append(time.perf_counter()-t)
    return statistics.median(times),times,output

def run(reps=3):
    grid=e.Moments(64)
    b=np.linspace(-.02,.02,4096)
    arrayfn=lambda:grid.evaluate(b,.7)
    serialfn=lambda:tuple(np.array(x) for x in zip(*(grid.evaluate(float(v),.7) for v in b)))
    chunkfn=lambda:grid.evaluate_chunked(b,.7,chunk=128)
    ma,ra,A=tmed(arrayfn,reps)
    ms,rs,S=tmed(serialfn,reps)
    component_err=max(float(np.max(abs(x-y))) for x,y in zip(A,S))
    if component_err>2e-14:raise AssertionError("MOMENT_VEC_NUMERICAL_MISMATCH")
    mc,rc,C=tmed(chunkfn,reps)
    chunk_err=max(float(np.max(abs(x-y))) for x,y in zip(A,C))
    if chunk_err>2e-14:raise AssertionError("CHUNK_REDUCTION_PHYSICAL_DISAGREEMENT")
    tracemalloc.start()
    arrayfn();_,peak_array=tracemalloc.get_traced_memory()
    tracemalloc.stop()
    tracemalloc.start()
    chunkfn();_,peak_chunk=tracemalloc.get_traced_memory()
    tracemalloc.stop()
    tracemalloc.start()
    serialfn();_,peak_serial=tracemalloc.get_traced_memory()
    tracemalloc.stop()
    cases=[e.InitialData(*s) for s in tab.CASES]
    def scalar_fn(init):
        a=e.EinsteinVlasovLRS(init,ang_n=64)
        z=a.at_a(a.aend)
        return (z["t_elapsed_proper_s"],z["b"],z["s_over_H"])
    def with_workers(worker):
        if worker==1:
            return list(map(scalar_fn,cases))
        with ThreadPoolExecutor(max_workers=worker) as pool:
            return list(pool.map(scalar_fn,cases))
    valid_ref=with_workers(1)
    parallel=[]
    for n in (1,2,4):
        tm,rep,states=tmed(lambda:with_workers(n),reps)
        err=max(abs(x-y) for old,new in zip(valid_ref,states) for x,y in zip(old,new))
        if err>1e-11:raise AssertionError("THREAD_SOLVER_SOURCE_DISAGREEMENT")
        parallel.append({"threads":n,"median_seconds":tm,"seconds":rep,"max_absolute_ref_disagreement":err})
    return {"schema":"bass.rei.axbi.initial_stress_cpu_bench.v1",
       "host_settings":"real user Ubuntu; warmed per-scope three repeats, original q/A/eta cases",
       "moment_loop":{"n_b_values":len(b),"angular_GL_n":64,"vector_wall_median_s":ma,"scalar_wall_median_s":ms,
         "vector_speedup":ms/ma,"chunked_wall_median_s":mc,
         "chunked_speedup":ms/mc,
         "max_abs_component_difference":component_err,"max_abs_chunk_disagreement":chunk_err,
         "tracemalloc_vector_bytes":peak_array,"tracemalloc_chunked_bytes":peak_chunk,
         "tracemalloc_scalar_bytes":peak_serial},
       "separate_17_case_ODE_solves":parallel,
       "native_AX08_coupled_science_solver_speedup":None,
       "parallelism_conclusion":"Only keep separate-case threads if measured native runtime is faster at fixed physics; no subagent claims"}
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    result=run()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2)[:3300])
