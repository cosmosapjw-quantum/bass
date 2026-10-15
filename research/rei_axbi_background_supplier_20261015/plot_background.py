"""Visual, reproducible plots from the *actual* AX03 source locked background."""
from __future__ import annotations
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from axbi_provider import Background,Family

ROOT=Path(__file__).resolve().parent
PLOTS=ROOT/"evidence"
def plot():
    curves={}
    for q in [0.,.005,-.005,.01,-.01]:
        bg=Background(Family(q))
        curves[q]=bg.table(501)
    same=Background(Family(.01,"SameHDiagnostic")).table(501)
    fig,ax=plt.subplots(figsize=(8,5))
    for q,z in curves.items():
        ax.plot(z["zbar"],z["b"],label=f"q_ref={q:+.3f}")
    ax.plot(same["zbar"],same["b"],"--",label="SAME_H +0.010 diagnostic")
    ax.invert_xaxis()
    ax.set(xlabel="Mean redshift zbar=1/a-1",ylabel="Anisotropy b(a)",
           title="Source-locked REI AX03 shear-integrated Bianchi-I geometry")
    ax.legend(loc="best",fontsize=8)
    fig.tight_layout()
    fig.savefig(PLOTS/"AX03_B_Z20_TO_Z4.png",dpi=170);plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,5))
    for q,z in curves.items():
        ax.plot(z["zbar"],z["H_mean_per_s"]/z["H_flrw_per_s"]-1,label=f"q_ref={q:+.3f}")
    ax.plot(same["zbar"],same["H_mean_per_s"]/same["H_flrw_per_s"]-1,"--",label="SAME_H +0.010")
    ax.invert_xaxis()
    ax.set(xlabel="Mean redshift zbar",ylabel="H/H_FLRW -1",
           title="Density-fixed shear energy vs SAME_H counterfactual")
    ax.legend(loc="best",fontsize=8)
    fig.tight_layout()
    fig.savefig(PLOTS/"AX03_H_SHEAR_VS_FLRW.png",dpi=170);plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,5))
    for q,z in curves.items():
        ax.plot(z["zbar"],z["proper_elapsed_s"]/(365.25*86400*1e9),label=f"q_ref={q:+.3f}")
    ax.invert_xaxis()
    ax.set(xlabel="Mean redshift zbar",ylabel="Elapsed proper time from zbar=20 (Gyr)",
           title="REI AX03 proper-time clock: six signed physical backgrounds")
    ax.legend(loc="best",fontsize=8)
    fig.tight_layout()
    fig.savefig(PLOTS/"AX03_PROPER_TIME_GYR.png",dpi=170);plt.close(fig)
    print([str(p) for p in PLOTS.glob("AX03_*.png")])
if __name__=="__main__":plot()
