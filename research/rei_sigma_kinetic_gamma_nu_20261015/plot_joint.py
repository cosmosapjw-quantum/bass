"""Source-only quantitative PNGs from actually integrated eight-case CSV."""
from __future__ import annotations
import csv,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent
EV=HERE/"evidence"
T=EV/"JOINT_CAMPAIGN/REI_GAMMANU_MASSIVE_BACKGROUND.csv"
def main():
    groups={}
    with T.open() as f:
        for r in csv.DictReader(f):groups.setdefault(r["case"],[]).append(r)
    fig,ax=plt.subplots(figsize=(9,5))
    for name in ["RADIATION_ONLY","MASSIVE_ONLY","BOTH_PRIMORDIAL",
                 "BOTH_THOMSON_AX08","SIGNED_PLUS","SIGNED_MINUS"]:
        a=groups[name]
        x=np.array([float(v["zbar"]) for v in a])
        y=np.array([float(v["Sigma"]) for v in a])
        ax.plot(x,y,label=name)
    ax.invert_xaxis()
    ax.set(xlabel="Mean scale redshift zbar",ylabel="Sigma=sqrt(3)*abs(s)/H",
           title="Source-locked Einstein + photon, neutrino, massive FD background")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(EV/"JOINT_SIGMA_HISTORIES.png",dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,5))
    for field,label in [("pi_gamma_J_m3","Photon gamma"),
                        ("pi_nu_J_m3","Massless neutrino"),
                        ("pi_massive_J_m3","Massive FD matter"),
                        ("pi_total_J_m3","Total physical LRS Pi")]:
        a=groups["BOTH_PRIMORDIAL"]
        ax.plot([float(v["zbar"]) for v in a],
                [float(v[field]) for v in a],label=label)
    ax.invert_xaxis()
    ax.set(xlabel="Mean redshift zbar",ylabel="Pi [J/m3]",
           title="Independent stress decomposition: Sigma_ref=0, three kinetic sources")
    ax.legend()
    fig.tight_layout()
    fig.savefig(EV/"JOINT_KINETIC_PI_DECOMPOSITION.png",dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,5))
    for name in ["BOTH_PRIMORDIAL","BOTH_THOMSON_AX08"]:
        a=groups[name]
        ax.plot([float(v["zbar"]) for v in a],
                [float(v["Sigma"]) for v in a],label=name)
    ax.invert_xaxis()
    ax.set(xlabel="Mean redshift zbar",ylabel="Sigma",
           title="One-way original AX08 electron Thomson versus collisionless gamma")
    ax.legend()
    fig.tight_layout()
    fig.savefig(EV/"JOINT_AX08_THOMSON_DIFFERENCE.png",dpi=180);plt.close(fig)
    print("SCIENTIFIC_FIGURES",[(p.name,p.stat().st_size) for p in EV.glob("JOINT_*.png")])
if __name__=="__main__":main()
