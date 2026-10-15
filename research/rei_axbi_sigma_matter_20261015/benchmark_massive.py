"""Matched source-physical massive Vlasov vector, chunk, and worker benchmarks."""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
import argparse,json,statistics,time,tracemalloc
from pathlib import Path
import numpy as np
from sigma_matter import MassiveMoments,EinsteinVlasovSigmaMatter
from export_sigma_histories import cases

def timed(fn,reps=3):
    fn()
    t=[];last=None
    for _ in range(reps):
        start=time.perf_counter();last=fn();t.append(time.perf_counter()-start)
    return statistics.median(t),t,last

def peak(fn):
    fn()
    tracemalloc.start()
    try:
        fn()
        now,m=tracemalloc.get_traced_memory()
    finally:tracemalloc.stop()
    return m

def solve_all(jobs,workers):
    if workers==1:return [EinsteinVlasovSigmaMatter(initial,angular_n=32) for _,initial in jobs]
    with ThreadPoolExecutor(max_workers=workers) as p:
        return list(p.map(lambda job:EinsteinVlasovSigmaMatter(job[1],angular_n=32),jobs))

def run():
    obj=MassiveMoments(30.,angular_n=32)
    x=np.linspace(0,1.42,1024)
    b=.04*np.sin(1.3*x)
    A=.5
    def one():
        z=[obj.evaluate(float(xi),float(bi),A) for xi,bi in zip(x,b)]
        return np.array(z).T
    def full():return np.stack(obj.evaluate(x,b,A))
    def chunk():return np.stack(obj.batch_chunked(x,b,A,chunk=128))
    def group(workers):
        if workers==1:return chunk()
        cuts=[(i,min(i+128,len(x))) for i in range(0,len(x),128)]
        with ThreadPoolExecutor(max_workers=workers) as ex:
            out=list(ex.map(lambda ab:np.stack(obj.evaluate(x[ab[0]:ab[1]],b[ab[0]:ab[1]],A)),cuts))
        return np.concatenate(out,axis=1)
    reference=one()
    moment=[]
    for label,fun in [("scalar_1024",one),("full_vector_1024",full),
                      ("chunk128_vector",chunk),("chunk128_two_threads",lambda:group(2)),
                      ("chunk128_four_threads",lambda:group(4))]:
        med,tm,z=timed(fun)
        error=float(np.max(abs(z-reference)))
        if error>6e-14:raise AssertionError("ORIGINAL_MOMENT_DIFFERENCE_OUTSIDE_ROUNDOFF")
        moment.append({"method":label,"median_seconds":med,"repeat_seconds":tm,
          "tracemalloc_peak_bytes":peak(fun),"maximum_absolute_difference_vs_scalar":error})
    jobs=cases()
    ode=[]
    original=solve_all(jobs,1)
    ref=np.array([[m.at_x(m.xmax)["b"],m.at_x(m.xmax)["Sigma"]] for m in original])
    for w in (1,2,4):
        med,t,sol=timed(lambda w=w:solve_all(jobs,w))
        e=float(np.max(abs(np.array([[m.at_x(m.xmax)["b"],m.at_x(m.xmax)["Sigma"]] for m in sol])-ref)))
        if e>1e-13:raise AssertionError("SCIENCE_DIFFERED_THREAD_REDUCTION")
        ode.append({"workers":w,"median_seconds":med,"repeat_seconds":t,"max_source_endpoint_error":e})
    return {"schema":"bass.rei.axbi.initial_sigma_massive_pi_real_benchmark.v1",
      "source":"original BASS FD radial Q,DQ and original AX03 cosmology, positive GL32 angular",
      "moments_input":{"n":len(x),"mass_over_Tref":30,"A":A,"chunk":128},
      "moments":moment,"ode_case_count":len(jobs),"ode":ode,
      "native_REI_ion_history_speedup":None,
      "memory_scope":"tracemalloc Python NumPy temporary peaks, not process peak RSS or owner Rust",
      "parallel_scope":"actual Python ThreadPoolExecutor two/four workers; labels do not imply faster"}
if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--out",type=Path,required=True)
    z=ap.parse_args();result=run()
    if z.out.exists():raise FileExistsError(z.out)
    z.out.parent.mkdir(parents=True,exist_ok=True)
    z.out.write_text(json.dumps(result,indent=2)+"\n")
    for r in result["moments"]:print("MOMENT",r["method"],round(r["median_seconds"],5),r["tracemalloc_peak_bytes"],r["maximum_absolute_difference_vs_scalar"])
    for r in result["ode"]:print("ODE",r["workers"],round(r["median_seconds"],5),r["max_source_endpoint_error"])
