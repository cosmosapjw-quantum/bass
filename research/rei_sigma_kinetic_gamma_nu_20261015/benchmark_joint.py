"""Same physics empirical performance: 12 independent background IVPs and FD batches.

Python ProcessPoolExecutor workers are REAL local processes, not ChatGPT native
subagents. Reports wall medians and source output parity. No universal scaleup.
"""
from __future__ import annotations
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context
from pathlib import Path
import argparse,json,math,statistics,time,tracemalloc
import numpy as np
from joint_kinetic import KineticGammaNuMassive,source_lock,verify_original_sources
from sigma_matter import MassiveMoments

def _one_run(cfg):
    m=KineticGammaNuMassive(source_lock(),**cfg)
    z,fields,wall=m.integrate(n=151,rtol=1e-11,atol=6e-14)
    return (fields[-1]["Sigma"],float(z.y[1,-1]),fields[-1]["H"],
            fields[-1]["pi_total_J_m3"])

def median(fn,reps=3):
    fn()
    times=[];res=None
    for _ in range(reps):
        t=time.perf_counter();res=fn();times.append(time.perf_counter()-t)
    return statistics.median(times),times,res

def run():
    verify_original_sources()
    q=[0.,.005,-.005,.01,-.01]
    C=[]
    for i in range(12):
        qq=q[i%len(q)]
        sig=math.sqrt(3)*abs(qq)/math.hypot(1.,qq)
        ori=0 if qq==0 else (1 if qq>0 else -1)
        C.append({"Sigma_ref":sig,"orientation":ori,
                  "kappa_gamma":.2 if i%3!=0 else 0.,
                  "kappa_nu":.2 if i%4!=0 else -.1,
                  "massive_fraction":.1 if i%2 else .2,
                  "massive_A":.5 if i%3!=1 else -.25,
                  "m_over_Tref":30.,"ellmax":8})
    tserial,stimes,baseline=median(lambda:list(map(_one_run,C)))
    processes=[]
    for workers in (2,4):
        def calc():
            # One host Linux fork pool per call, no original owner edits.
            with ProcessPoolExecutor(max_workers=workers,mp_context=get_context("fork")) as pool:
                return list(pool.map(_one_run,C))
        m,samples,out=median(calc)
        mismatch=max(abs(x-y) for a,b in zip(out,baseline) for x,y in zip(a,b))
        if mismatch>4e-13:raise AssertionError(f"NON_IDENTICAL_PHYSICAL_PARALLEL:{mismatch}")
        processes.append({"workers":workers,"wall_median_s":m,"samples_s":samples,
                          "max_abs_endpoint_disagreement_vs_single":mismatch,
                          "speedup_vs_serial":tserial/m})
    massive=MassiveMoments(30.,angular_n=32)
    xs=np.linspace(0,math.log(4.2),1024)
    bb=.01*np.sin(xs)
    funcs={
     "scalar_1024":lambda:tuple(np.array(v) for v in zip(*(massive.evaluate(float(x),float(b),.5)
                            for x,b in zip(xs,bb)))),
     "full_array_1024":lambda:massive.evaluate(xs,bb,.5),
     "chunked128_1024":lambda:massive.batch_chunked(xs,bb,.5,chunk=128),
     "chunked64_1024":lambda:massive.batch_chunked(xs,bb,.5,chunk=64)}
    values={}
    orig=massive.batch_chunked(xs,bb,.5,chunk=128)
    for name,f in funcs.items():
        # scalar zip trick: 3 x N shape, and numpy full/chunk 3 tuples x N
        med,rep,out=median(f)
        temp=np.asarray(out)
        oracle=np.asarray(orig)
        if temp.shape !=oracle.shape:
            raise RuntimeError(f"shape mismatch {name} {temp.shape}, {oracle.shape}")
        maxdiff=float(np.max(np.abs(temp-oracle)))
        if maxdiff>3e-12:raise AssertionError("FD_MOMENT_VECTOR_PARITY")
        tracemalloc.start()
        try:
            f();_,peak=tracemalloc.get_traced_memory()
        finally:tracemalloc.stop()
        values[name]={"median_s":med,"repeats_s":rep,
            "max_abs_vs_chunked128":maxdiff,"tracemalloc_peak_bytes":peak}
    return {"schema":"bass.rei.axbi.gamma_nu_massive_actual_parallel_bench.v1",
     "n_cases":len(C),"case_params":C,
     "serial":{"wall_median_s":tserial,"repeat_s":stimes},
     "process":processes,
     "moment_1024":{"n":1024,"BASS_FD_radial":len(massive.q),
                     "GL_angular":len(massive.w),"comparisons":values},
     "actual_scope":"same BASS FD96 and REI gamma/nu source, real DOP853 12 independent cases or only massive moments, no coupled HHe native solver speedup",
     "hardware_claim":"one observed authorized Ubuntu CPU, timing includes per-call process-pool lifecycle",
     "native_chatgpt_subagents":"NOT_RUN_UNEXPOSED"}

if __name__=="__main__":
    pa=argparse.ArgumentParser();pa.add_argument("--out",type=Path,required=True)
    a=pa.parse_args()
    if a.out.exists():raise FileExistsError(a.out)
    t=time.perf_counter();v=run()
    v["total_wall_s"]=time.perf_counter()-t
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(v,indent=2,ensure_ascii=False)+"\n")
    print("serial",v["serial"]["wall_median_s"],"process",v["process"],flush=True)
    print("massive",[(k,x["median_s"],x["tracemalloc_peak_bytes"]) for k,x in v["moment_1024"]["comparisons"].items()],flush=True)
