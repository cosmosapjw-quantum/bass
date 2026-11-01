#!/usr/bin/env python3
"""Two source-derived original S0 science figures; no observational data."""
import csv,gzip
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
with gzip.open(ROOT/"results/CHARACTERISTIC_VS_HAT_CONTINUOUS_MATERIAL_RESPONSE.csv.gz","rt") as f:
    rows=list(csv.DictReader(f))
for y,label,unit in (
    ("delta_xHII","Difference in H II ionization fraction",""),
    ("delta_T_K","Difference in gas temperature","K")
):
    fig,ax=plt.subplots(figsize=(7,4.3))
    for b in ("S0_BI","S0_FLRW"):
        r=sorted((r for r in rows if r["branch"]==b),key=lambda x:int(x["step"]))
        x=[float(v["t_proper_s"])/1e9 for v in r]
        ydata=[float(v[y]) for v in r]
        ax.plot(x,ydata,label=b.replace("S0_",""))
    ax.axhline(0,linewidth=.8)
    ax.set_xlabel("Source proper time (10⁹ s)")
    ax.set_ylabel(label+(" ("+unit+")" if unit else ""))
    ax.set_title("S0 continuous coupled original-Rust: characteristic minus fixed-hat")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(ROOT/"results"/(y+".svg"))
    fig.savefig(ROOT/"results"/(y+".png"),dpi=180)
    plt.close(fig)
print("PLOTS_CREATED",len([*ROOT.glob("results/*.svg")]))
