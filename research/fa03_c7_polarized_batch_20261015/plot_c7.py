"""Reproduce two measured execution plots from saved C7 timing JSON."""
from __future__ import annotations
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE=Path(__file__).resolve().parent
def main():
    dat=json.loads((BASE/"evidence/BENCHMARK_STOKES_64.json").read_text())
    rows=dat["results"]
    xs=[z["rays"] for z in rows]
    for name,label in [("original_separate_Jones","Original Jones, 3 epsilon runs"),
                       ("complex_fused_Jones","Complex Jones batch"),
                       ("real_vector_Stokes","Real Stokes batch"),
                       ("real_stokes_thread2","Real Stokes, 2 threads")]:
        plt.plot(xs,[z["timing"][name]["median_seconds"] for z in rows],"o-",label=label)
    plt.xlabel("Number of cap rays")
    plt.ylabel("Median wall time (s)")
    plt.title("FA03 C7 matched RK4/energy benchmark")
    plt.legend()
    plt.tight_layout()
    out=BASE/"evidence/C7_MATCHED_WALLTIME.png"
    plt.savefig(out,dpi=175)
    plt.close()
    speed=[z["optimization"]["real_vs_original_speedup"] for z in rows]
    plt.plot(xs,speed,"o-")
    plt.xlabel("Number of cap rays")
    plt.ylabel("Original Jones / real Stokes (speedup)")
    plt.title("FA03 C7 4-real-component physical speedup")
    plt.tight_layout()
    out2=BASE/"evidence/C7_REAL_STOKES_SPEEDUP.png"
    plt.savefig(out2,dpi=175)
    plt.close()
    print(out,out2)
if __name__=="__main__":main()
