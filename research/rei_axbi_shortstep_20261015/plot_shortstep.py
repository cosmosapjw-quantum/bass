"""Plots from actual binary64 endpoint, mp80, and Rust/source-bounded evidence."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
EV=HERE/"evidence"
def render():
    d=json.loads((EV/"MP80_SHORTSTEP.json").read_text())
    xs=np.array([x["actual_delta_ln_a"] for x in d["rows"]])
    fig,ax=plt.subplots(figsize=(8.2,5.0))
    methods=[("relative_t_gauss4_to_mp","Physical local GL4"),
        ("relative_t_hermite_to_mp","501-node Hermite increment"),
        ("relative_t_naive_to_mp","Accumulated t difference")]
    for key,label in methods:
        yy=np.array([max(x[key],1e-18) for x in d["rows"]])
        ax.scatter(xs,yy,label=label,alpha=.7,s=15)
    ax.set_xscale("log");ax.set_yscale("log")
    ax.axhline(1e-9,ls="--",label="Prior stable-increment target 1e-9")
    ax.set(xlabel="Actual delta ln(a) from float64 endpoints",
           ylabel="Relative error to independent mpmath80",
           title="REI AX03 background short-step accuracy (90 physical intervals)")
    ax.legend(fontsize=8);fig.tight_layout()
    fig.savefig(EV/"C8_SHORTSTEP_RELATIVE_ERRORS.png",dpi=175)
    plt.close(fig)
    run=json.loads((EV/"BENCHMARK_CACHED.json").read_text())
    labels=["Cumulative subtraction","501-node Hermite","Physical GL4","Physical GL8"]
    vals=[run["timings"][k]["median_s"]*1000 for k in ["naive","hermite","gauss4","gauss8"]]
    fig,ax=plt.subplots(figsize=(8.2,4.5))
    ax.barh(labels,vals)
    ax.set(xlabel="Median wall time for all 90 intervals (ms)",
           title="Same AX03 physical input, source-matched Python benchmark")
    fig.tight_layout()
    fig.savefig(EV/"C8_SHORTSTEP_CPU_COST.png",dpi=175)
    plt.close(fig)
    print("SAVED",EV/"C8_SHORTSTEP_RELATIVE_ERRORS.png",EV/"C8_SHORTSTEP_CPU_COST.png")

if __name__=="__main__":render()
