"""Matched source/accuracy/memory benchmark of original vs stable BASS FD moments.

Explicitly component-only, not native REI H/He or full-solver acceleration.
"""
from __future__ import annotations
import argparse,hashlib,json,statistics,time,tracemalloc
from pathlib import Path
import numpy as np
from stable_moments import StableMassiveMoments


def _timer(fn,reps=7):
    fn()
    ts=[]
    for _ in range(reps):
        start=time.perf_counter();fn();ts.append(time.perf_counter()-start)
    tracemalloc.start()
    try:
        fn();_,peak=tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return dict(median_s=float(statistics.median(ts)),minimum_s=float(min(ts)),
                peak_python_trace_bytes=int(peak),repeats=reps)


def run(n=1024,angular_n=32):
    m=StableMassiveMoments(30.,angular_n=angular_n)
    x=np.linspace(0,1.55,n)
    b=.007*np.sin(np.linspace(0,9*np.pi,n))+.001
    A=.5
    source=m.batch_chunked(x,b,A,chunk=128)
    stable=m.evaluate_with_delta(x,b,A,chunk=64)
    parity=max(float(np.max(np.abs(source[i]-stable[i]))) for i in range(3))
    source_delta=source[2]-source[1]
    delta_abs=max(abs(stable[3]-source_delta))
    methods={
      "legacy_chunk32":lambda:m.batch_chunked(x,b,A,chunk=32),
      "legacy_chunk128":lambda:m.batch_chunked(x,b,A,chunk=128),
      "stable_chunk16":lambda:m.evaluate_with_delta(x,b,A,chunk=16),
      "stable_chunk32":lambda:m.evaluate_with_delta(x,b,A,chunk=32),
      "stable_chunk64":lambda:m.evaluate_with_delta(x,b,A,chunk=64),
      "stable_chunk128":lambda:m.evaluate_with_delta(x,b,A,chunk=128),
      "stable_chunk256":lambda:m.evaluate_with_delta(x,b,A,chunk=256),
    }
    perf={name:_timer(fn) for name,fn in methods.items()}
    tiny=[]
    for beta in (0.,1e-16,1e-14,1e-12,1e-10):
        orig=m.evaluate(.5,beta,0.)
        new=m.delta_p_stable(.5,beta,0.)
        tiny.append(dict(b=beta,legacy=orig[2]-orig[1],stable=new))
    return {
      "schema":"bass.rei.stable_pi.matched_component_benchmark.v1",
      "n":n,"angular_nodes":angular_n,"radial_nodes":len(m.q),
      "mass_over_Tref":30.,"angular_initial_A":A,
      "max_abs_energy_pressure_parity":parity,
      "max_abs_delta_pi_legacy_vs_stable_on_finite_b":float(delta_abs),
      "tiny_b_sign_control":tiny,
      "methods":perf,
      "scope":"FD96 source vectorized component only; benchmark deliberately excludes native HHe chemistry and data IO",
    }


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--n",type=int,default=1024)
    args=p.parse_args()
    if args.out.exists():
        raise FileExistsError(args.out)
    result=run(args.n)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k in
       ("n","max_abs_energy_pressure_parity","max_abs_delta_pi_legacy_vs_stable_on_finite_b","methods")},indent=2))
