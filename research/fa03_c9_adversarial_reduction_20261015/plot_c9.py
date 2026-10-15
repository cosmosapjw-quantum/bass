"""Plots measured C9 matched source reduction correctness and performance."""
from __future__ import annotations
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
EV=ROOT/"evidence"

def main():
    z=json.loads((EV/"BENCHMARK_C9.json").read_text())
    rays=[x["rays"] for x in z["results"]]
    k=["numpy_einsum","pairwise_numpy","math_fsum"]
    fig,ax=plt.subplots(figsize=(8,5))
    for s in k:
        vals=[next(q for q in row["reducer_bench"] if q["method"]==s)["max_exact_dyadic_scalar_error"] for row in z["results"]]
        ax.plot(rays,vals,"o-",label=s)
    ax.set_xlabel("Physical rays")
    ax.set_ylabel("Maximum Stokes component dyadic error")
    ax.set_yscale("log")
    ax.set_title("C9 exact Fraction reference, same FA03 state")
    ax.legend()
    fig.tight_layout()
    fig.savefig(EV/"C9_EXACT_REDUCTION_ERRORS.png",dpi=175)
    plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,5))
    for s in ["legacy_C7_real","C9_pairwise","C9_math_fsum"]:
        vals=[row["full_source_bench"][s]["median_seconds"] for row in z["results"]]
        ax.plot(rays,vals,"o-",label=s)
    ax.set_xlabel("Physical rays")
    ax.set_ylabel("Median wall seconds (128 RK4 steps)")
    ax.set_title("C9 same-physics audit cost")
    ax.legend()
    fig.tight_layout()
    fig.savefig(EV/"C9_FULL_SOLVER_COST.png",dpi=175)
    plt.close(fig)
    print("SAVED",str(EV/"C9_EXACT_REDUCTION_ERRORS.png"),str(EV/"C9_FULL_SOLVER_COST.png"))

if __name__=="__main__":
    main()
