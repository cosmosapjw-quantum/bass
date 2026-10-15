"""Plots of actual FA03 C8 matched source experiments, no extrapolated certificate."""
from __future__ import annotations
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
EV=ROOT/"evidence"

def render():
    data=json.loads((EV/"C8_CONVERGENCE_AND_BENCHMARK.json").read_text())
    d=data["convergence"][0]
    xs=[r["steps"] for r in d["time_refinements"]]
    ys=[r["max_eps_error_vs_1024_same_GL6"] for r in d["time_refinements"]]
    fig,ax=plt.subplots(figsize=(8,5))
    ax.loglog(xs,ys,"o-",label="Observed vs 1024 RK4 steps, 36 rays, GL6")
    ax.loglog(xs,[ys[1]*(xs[1]/x)**4 for x in xs],"--",label="Fourth-order reference slope")
    ax.set(xlabel="RK4 steps",ylabel="Trace-norm difference",title="FA03 C8 empirical time discretization")
    ax.legend()
    fig.tight_layout()
    fig.savefig(EV/"C8_RK4_REFINEMENT.png",dpi=175)
    plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,5))
    for n,label in [(4,"GL4"),(5,"GL5"),(6,"GL6"),(8,"GL8")]:
        grids=[k["rays"] for k in data["benchmark"]]
        tim=[k["measured"][f"real_stokes_GL{n}"]["median_s"] for k in data["benchmark"]]
        ax.plot(grids,tim,"o-",label=label)
    ax.set(xlabel="Cap rays",ylabel="Median CPU wall seconds (128 RK4)",
           title="FA03 C8 measured energy-order performance")
    ax.legend()
    fig.tight_layout()
    fig.savefig(EV/"C8_ENERGY_SPEED.png",dpi=175)
    plt.close(fig)
    return [str(EV/"C8_RK4_REFINEMENT.png"),str(EV/"C8_ENERGY_SPEED.png")]

if __name__=="__main__":print(render())
