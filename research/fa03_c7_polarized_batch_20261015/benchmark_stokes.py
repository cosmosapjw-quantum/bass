"""Side-by-side original, complex batched and real Stokes, actual threads benchmark."""
from __future__ import annotations
import argparse
import json
import statistics
import time
from pathlib import Path

import numpy as np
import batch_transport as c
import stokes_vector as s

def measured(reps=3,steps=64):
    if not isinstance(reps,int) or reps<2:raise ValueError("repetitions>=2")
    eps=(-.1,0.,.1)
    result=[]
    for nr,nphi in [(3,12),(6,24),(10,48)]:
        ell,w=c._prepared_rays(nr,nphi)
        chunk=max(1,len(w)//4)
        jobs={
          "original_separate_Jones":lambda:np.stack([c.fa03.solve_energy(.008,.01,e,steps=steps,nr=nr,nphi=nphi,ne=8) for e in eps]),
          "complex_fused_Jones":lambda:c.solve_energy_batched(eps,steps=steps,ell=ell,w=w,ne=8),
          "real_vector_Stokes":lambda:s.solve_energy_real(eps,steps=steps,ell=ell,w=w,ne=8),
          "real_stokes_chunked_serial":lambda:s.solve_energy_real(eps,steps=steps,ell=ell,w=w,ne=8,ray_chunk=chunk,workers=1),
          "real_stokes_thread2":lambda:s.solve_energy_real(eps,steps=steps,ell=ell,w=w,ne=8,ray_chunk=chunk,workers=2),
          "real_stokes_thread4":lambda:s.solve_energy_real(eps,steps=steps,ell=ell,w=w,ne=8,ray_chunk=chunk,workers=4)
        }
        for name,fn in jobs.items():fn()
        tests={}
        original=None
        for name,fn in jobs.items():
            times=[]
            res=None
            for _ in range(reps):
                t0=time.perf_counter()
                res=fn()
                times.append(time.perf_counter()-t0)
            if name=="original_separate_Jones":
                original=res
            err=None if original is res else max(c.trace_norm(a-b) for a,b in zip(original,res))
            if err is not None and err>3e-12:
                raise AssertionError("MATCHED_PHYSICS_MISMATCH:"+name+":"+str(err))
            tests[name]={"median_seconds":statistics.median(times),
                         "individual_seconds":times,
                         "max_matrix_trace_norm_vs_original":err}
        orig=tests["original_separate_Jones"]["median_seconds"]
        fastest=tests["real_vector_Stokes"]["median_seconds"]
        result.append({"rays":len(w),"resolution":[nr,nphi],"steps":steps,
             "repetitions":reps,"exact_real_state_elements":3*len(w)*8*4,
             "state_bytes_real":3*len(w)*8*4*8,
             "state_bytes_complex":3*len(w)*8*2*2*16,
             "optimization":{"real_vs_original_speedup":orig/fastest,
                "real_vs_complex_batch_speedup":tests["complex_fused_Jones"]["median_seconds"]/fastest,
                "real_thread2_vs_real_single":fastest/tests["real_stokes_thread2"]["median_seconds"],
                "real_thread4_vs_real_single":fastest/tests["real_stokes_thread4"]["median_seconds"]},
             "timing":tests})
    return {"schema":"bass.fa03.c7.actual_scoped_benchmark.v2",
        "scope":"all modes same frozen source, eps=-.1,0,.1, ne8, RK4 64, fixed GL angular detector; local warmed wall medians; time excludes testing+external startup",
        "run_parallelism":"ThreadPoolExecutor actual 2/4 disjoint ray jobs, verified physical equivalence, no assertion of parallel speedup",
        "memory":"nominal state array bytes only, not RSS incl NumPy temporaries",
        "whole_REI_speedup":None,
        "results":result}

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--repetitions",type=int,default=3)
    args=parser.parse_args()
    if args.out.exists():raise FileExistsError(args.out)
    dat=measured(args.repetitions)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(dat,indent=2,ensure_ascii=False)+"\n")
    for row in dat["results"]:
        print(row["rays"],row["optimization"],
              {k:round(v["median_seconds"],5) for k,v in row["timing"].items()},flush=True)
