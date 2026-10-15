"""Measured same-physics FA03 C7 benchmark (no solver warmup in timings).

Medians of repeated wall-clock timing on user Ubuntu workstation. One CPU sample
and optional ThreadPool ray chunks are actual execution, not theoretical speedups.
"""
from __future__ import annotations
import argparse
import json
import math
import platform
import sys
import time
import statistics
from pathlib import Path

import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import batch_transport as batch

def _median(fn,reps):
    vals=[]
    value=None
    for _ in range(reps):
        t=time.perf_counter()
        value=fn()
        vals.append(time.perf_counter()-t)
    return statistics.median(vals), value, vals

def bench(reps=3,grids=((3,12),(6,24),(10,48)),steps=64,ne=8):
    if reps<1:raise ValueError("repetitions positive")
    batch.verify()
    e=(-.1,0.,.1)
    cases=[]
    for nr,nphi in grids:
        ell,w=batch._prepared_rays(nr,nphi)
        rays=len(w)
        chunk=max(1,rays//4)
        def ref():
            return np.stack([batch.fa03.solve_energy(.008,.01,eps,steps=steps,nr=nr,nphi=nphi,ne=ne) for eps in e])
        def opt():
            return batch.solve_energy_batched(e,steps=steps,ell=ell,w=w,ne=ne)
        def serial_chunks():
            return batch.solve_energy_batched(e,steps=steps,ell=ell,w=w,ne=ne,ray_chunk=chunk,workers=1)
        def parallel2():
            return batch.solve_energy_batched(e,steps=steps,ell=ell,w=w,ne=ne,ray_chunk=chunk,workers=2)
        def parallel4():
            return batch.solve_energy_batched(e,steps=steps,ell=ell,w=w,ne=ne,ray_chunk=chunk,workers=4)
        funcs={"original_separate_eps":ref,"fused_batched_eps":opt,
               "fused_chunked_serial":serial_chunks,
               "fused_thread2":parallel2,"fused_thread4":parallel4}
        for f in funcs.values():f()  # full warm-up outside timing
        measurements={}
        orig=None
        for name,fn in funcs.items():
            median,out,individual=_median(fn,reps)
            measurements[name]={"median_s":median,"repeat_s":individual,
                "max_disagreement_vs_source":None}
            if name=="original_separate_eps":
                orig=out
            else:
                err=max(batch.trace_norm(u-v) for u,v in zip(out,orig))
                if err>2e-12:raise AssertionError(f"NUMERICAL_DISCREPANCY:{name}:{err}")
                measurements[name]["max_disagreement_vs_source"]=err
        measurements["fused_batched_eps"]["speedup_vs_original"]=measurements["original_separate_eps"]["median_s"]/measurements["fused_batched_eps"]["median_s"]
        for k in ["fused_chunked_serial","fused_thread2","fused_thread4"]:
            measurements[k]["speedup_vs_single_batch"]=measurements["fused_batched_eps"]["median_s"]/measurements[k]["median_s"]
        cases.append({"nr":nr,"nphi":nphi,"rays":rays,"steps":steps,"ne":ne,"eps":list(e),
            "parallel_ray_chunks":math.ceil(rays/chunk),
            "chunk_max_rays":chunk,
            "state_bytes_batch_unpartitioned":len(e)*rays*ne*4*16,
            "state_bytes_per_ray_chunk":len(e)*chunk*ne*4*16,
            "time":measurements})
    return {"schema":"bass.fa03.c7.real_benchmark.v1",
            "python":platform.python_version(),
            "numpy":np.__version__,
            "original_source_sha256":batch.SHA,
            "repetitions":reps,"cases":cases,
            "performance_scope":"actual warmed per-case median wall time, same source and checked physical output; excludes setup external Git and comparison test costs",
            "parallel_scope":"ThreadPoolExecutor actual disjoint deterministic ray partitions, NumPy memory buffers, not multiprocessing native solver",
            "memory_scope":"state-array nominal bytes only, not peak RSS",
            "claim_gate":{"native_REI_speedup":None,"whole_BASS_solver_speedup":None,
                          "rigorous_error_bound":None}}

def main():
    pa=argparse.ArgumentParser()
    pa.add_argument("--repetitions",type=int,default=3)
    pa.add_argument("--steps",type=int,default=64)
    pa.add_argument("--out",type=Path,required=True)
    a=pa.parse_args()
    if a.out.exists():raise FileExistsError(a.out)
    r=bench(a.repetitions,steps=a.steps)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({"path":str(a.out),"summaries":[{"rays":c["rays"],
        "reference_s":c["time"]["original_separate_eps"]["median_s"],
        "fused_s":c["time"]["fused_batched_eps"]["median_s"],
        "fused_speedup":c["time"]["fused_batched_eps"]["speedup_vs_original"],
        "serial_chunks_s":c["time"]["fused_chunked_serial"]["median_s"],
        "parallel2_s":c["time"]["fused_thread2"]["median_s"],
        "parallel4_s":c["time"]["fused_thread4"]["median_s"],
        "max_ref_disagreement":c["time"]["fused_batched_eps"]["max_disagreement_vs_source"]} for c in r["cases"]]},indent=2))
if __name__=="__main__":
    main()
