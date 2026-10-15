"""Reproducible measured charts: include cached, batch and 2/4-worker timings."""
from __future__ import annotations
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
EV=HERE/"evidence"
def render():
    j=json.loads((EV/"BENCHMARK_VECTOR.json").read_text())
    keys=["naive","hermite","gauss4","gauss4_vector_workers1",
          "gauss4_vector_workers2","gauss4_vector_workers4"]
    labels=["Cumulative subtraction (unsafe)",
            "501-node Hermite",
            "Scalar physical GL4",
            "Vector GL4, 1 worker",
            "Vector GL4, 2 threads",
            "Vector GL4, 4 threads"]
    x=[j["timings"][k]["median_s"]*1000 for k in keys]
    fig,ax=plt.subplots(figsize=(9,4.8))
    ax.barh(labels,x)
    ax.set_xlabel("Median wall milliseconds, 90 matched source intervals")
    ax.set_title("REI AX03 short-step runtime, source-locked inputs")
    fig.tight_layout()
    fig.savefig(EV/"C8_VECTOR_PARALLEL_COST.png",dpi=180)
    plt.close(fig)
    print(EV/"C8_VECTOR_PARALLEL_COST.png")
if __name__=="__main__":render()
