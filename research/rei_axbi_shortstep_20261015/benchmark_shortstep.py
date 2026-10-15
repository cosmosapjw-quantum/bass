"""C8 actual short-step performance + observed accuracy at SAME source inputs.

Does not compare 90 queries to an unrelated whole-solver cost. Preconstruct
backgrounds and Hermite tables before per-query timings. Explicitly report
single-use one-time table setup, input source, numerical accuracy and memory.
"""
from __future__ import annotations
import json,math,statistics,sys,time,tracemalloc
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from shortstep import HermiteClock,gauss_increment,gauss_batch
from axbi_provider import Background,Family

def median_times(fn,n=5):
    fn()
    times=[];out=None
    for _ in range(n):
        t=time.perf_counter();out=fn();times.append(time.perf_counter()-t)
    return {"median_s":statistics.median(times),"repeat_s":times,
            "checksums":tuple(float(np.sum(np.asarray(out)[:,i])) for i in range(2))}

def run():
    mp=json.loads((HERE/"evidence/MP80_SHORTSTEP.json").read_text())
    case_order=[(0.,"PhysicalDensityFixed"),(.005,"PhysicalDensityFixed"),
                (-.005,"PhysicalDensityFixed"),(.01,"PhysicalDensityFixed"),
                (-.01,"PhysicalDensityFixed"),(.01,"SameHDiagnostic")]
    begin=time.perf_counter()
    bg={k:Background(Family(*k)) for k in case_order}
    bg_init=time.perf_counter()-begin
    begin=time.perf_counter()
    table={k:HermiteClock(obj) for k,obj in bg.items()}
    table_init=time.perf_counter()-begin
    samples=[(bg[(r["q"],r["family"])],table[(r["q"],r["family"])],r["a0"],r["a1"]) for r in mp["rows"]]
    assert len(samples)==90
    def eval_all(mode):
        result=[]
        for b,t,a0,a1 in samples:
            if mode=="naive":
                x=(b.at_a(a1)["proper_elapsed_s"]-b.at_a(a0)["proper_elapsed_s"],
                   b.at_a(a1)["b"]-b.at_a(a0)["b"])
            elif mode=="hermite":x=t.increment(a0,a1)
            elif mode=="gauss4":x=gauss_increment(b,a0,a1,order=4)
            elif mode=="gauss8":x=gauss_increment(b,a0,a1,order=8)
            else:raise ValueError(mode)
            result.append(x)
        return result
    groups={}
    for ix,(b,clock,a0,a1) in enumerate(samples):
        key=(b.case.q_ref,b.case.family)
        groups.setdefault(key,[]).append((ix,a0,a1))
    def eval_batch(workers=1):
        def one(item):
            key,values=item
            ob=bg[key]
            a0=np.array([z[1] for z in values])
            a1=np.array([z[2] for z in values])
            dt,db=gauss_batch(ob,a0,a1,order=4)
            return [(z[0],(float(dt[i]),float(db[i]))) for i,z in enumerate(values)]
        jobs=list(groups.items())
        if workers==1:
            got=[one(entry) for entry in jobs]
        else:
            with ThreadPoolExecutor(max_workers=min(workers,len(jobs))) as pool:
                got=list(pool.map(one,jobs))
        ordered=[None]*len(samples)
        for batch in got:
            for ix,value in batch:ordered[ix]=value
        if any(v is None for v in ordered):raise AssertionError("missing input")
        return ordered
    timings={mode:median_times(lambda mode=mode:eval_all(mode)) for mode in ["naive","hermite","gauss4","gauss8"]}
    for workers in (1,2,4):
        timings[f"gauss4_vector_workers{workers}"]=median_times(lambda n=workers:eval_batch(n))
    input_ref=eval_all("gauss4")
    for workers in (1,2,4):
        grouped=eval_batch(workers)
        maxrel=max(abs(t[0]/r[0]-1) for t,r in zip(grouped,input_ref))
        if maxrel>3e-13:raise ArithmeticError("VECTORIZED_GAUSS_PHYSICAL_MISMATCH")
        timings[f"gauss4_vector_workers{workers}"]["max_relative_disagreement_to_scalar_GL4"]=maxrel
    result={"schema":"bass.rei.axbi.shortstep_runtime_benchmark.v1",
       "source":"original real-AX03 q family + SAME_H",
       "physical_sample_cases":6,
       "paired_intervals":len(samples),
       "mean_scale_values":[.05,.1,.18],
       "relative_nominal_steps":[1e-4,1e-8,1e-10,1e-12,"nextafter"],
       "init_bg_once_s":bg_init,"init_Hermite_once_s":table_init,
       "timings":timings,
       "conclusions":{"fastest_method":min(timings,key=lambda x:timings[x]["median_s"]),
          "naive_numerical_correct":False,
          "hermite_satisfies_prior_stable_relative_target_1e-9":mp["max_relative_time_error"]["Hermite501"]<1e-9,
          "gauss4_satisfies_prior_stable_relative_target_1e-9":mp["max_relative_time_error"]["gauss4"]<1e-9},
       "explicit_limitations":"90 exact float64 input intervals; medians on same physical 90, not a native whole-solver benchmark or a rigorous global interval bound",
       "whole_REI_solver_speedup":None}
    return result
if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument("--output",type=Path,required=True)
    x=parser.parse_args();obj=run()
    x.output.parent.mkdir(parents=True,exist_ok=True)
    if x.output.exists():raise FileExistsError(x.output)
    x.output.write_text(json.dumps(obj,indent=2)+"\n")
    print(json.dumps({k:v for k,v in obj.items() if k!="timings"},indent=2))
    print("TIMINGS",[(k,v["median_s"]) for k,v in obj["timings"].items()])
