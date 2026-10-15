"""Render original actual physical Sigma and radiation/massive stresses."""
from __future__ import annotations
import csv,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent
DATA=HERE/"evidence/SIGMA_MATTER_TABLES"
def plot():
    meta=json.loads((DATA/"AX03_SIGMA_MATTER_CONTRACT.json").read_text())
    by={}
    with (DATA/"AX03_SIGMA_MASSIVE_HISTORIES.csv").open() as f:
        for row in csv.DictReader(f):
            by.setdefault(row["case_id"],[]).append(row)
    fig,ax=plt.subplots(figsize=(8.2,5.2))
    names=["SHEAR_PLUS_SIGMA","SHEAR_PLUS_RAD_PLUS","SHEAR_PLUS_MATTER_PLUS",
       "SHEAR_PLUS_BOTH_PLUS","SHEAR_PLUS_BOTH_MINUS","SHEAR_PLUS_COLD_MATTER"]
    for name in names:
        r=by[name]
        z=np.array([float(t["zbar"]) for t in r])
        y=np.array([float(t["Sigma"]) for t in r])
        ax.plot(z,y,label=name.replace("_"," ").title())
    ax.invert_xaxis();ax.set(xlabel="Mean redshift zbar",ylabel=r"$\Sigma=\sqrt{\sigma_{ab}\sigma^{ab}/2}/H$",
        title="Bianchi I: coupled radiation and massive collisionless shear")
    ax.legend(fontsize=7)
    fig.tight_layout();fig.savefig(HERE/"evidence/AXBI_SIGMA_STRESS_HISTORY.png",dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(8.2,5.0))
    names=["RADIATION_ONLY_SEED","MASSIVE_MATTER_ONLY_SEED","RADIATION_AND_MATTER_SEED"]
    for name in names:
        r=by[name];z=[float(t["zbar"]) for t in r]
        s=[float(t["Sigma"]) for t in r]
        ax.plot(z,s,label=name.replace("_"," "))
    ax.invert_xaxis();ax.set(xlabel="Mean redshift zbar",ylabel="Sigma",
        title="Zero initial shear, separate kinetic anisotropic-stress seeds")
    ax.legend(fontsize=8);fig.tight_layout();fig.savefig(HERE/"evidence/AXBI_ZERO_SHEAR_GENERATION.png",dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(8.2,5.0))
    r=by["SHEAR_PLUS_BOTH_PLUS"]
    z=np.array([float(t["zbar"]) for t in r])
    rad=np.array([float(t["Pi_r_J_m3"]) for t in r])
    mat=np.array([float(t["Pi_m_J_m3"]) for t in r])
    ax.plot(z,rad,label="Radiation Pi")
    ax.plot(z,mat,label="Massive collisionless matter Pi")
    ax.invert_xaxis()
    ax.set(xlabel="Mean redshift zbar",ylabel="LRS anisotropic stress Pi (J/m^3)",
        title="Kinetic quadrupole sources (not hydrodynamic viscosity)")
    ax.legend();fig.tight_layout();fig.savefig(HERE/"evidence/AXBI_PI_COMPONENTS.png",dpi=180);plt.close(fig)
    print("PLOTTED",len(meta["cases"]),"PHYSICAL_SOURCE_CASES")
if __name__=="__main__":plot()
