"""Actual Einstein--Vlasov source trajectories: publishable exploratory plots."""
from __future__ import annotations
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from einstein_vlasov_lrs import EinsteinVlasovLRS,InitialData

HERE=Path(__file__).resolve().parent
OUT=HERE/"evidence"
CASES=[(0,0,0),(0,1,1),(0,-1,1),(.01,0,0),(.01,0,1),(.01,1,1),(.01,-1,1)]

def run():
    data={}
    for q,A,eta in CASES:
        model=EinsteinVlasovLRS(InitialData(q,A,eta))
        data[(q,A,eta)]=model.table(501)
    for key,title,ylabel,out in [
     ("s_over_H","Dynamical shear sourced by independent initial radiation quadrupole","s/H",
       "INITIAL_Q_A_SHEAR.png"),
     ("b","Anisotropic metric background from independent initial stress","b(a)",
       "INITIAL_Q_A_METRIC.png"),
     ("delta_Pparallel_minus_Pperp_J_m3",
       "Collisionless anisotropic radiation pressure difference","P_parallel - P_perp (J/m^3)",
       "INITIAL_Q_A_PRESSURE.png")]:
        fig,ax=plt.subplots(figsize=(8.5,5.4))
        for (q,A,eta),d in data.items():
            label=f"q={q:+.3f}, A={A:+.1f}, eta={eta:g}"
            ax.plot(d["zbar"],d[key],label=label)
        ax.invert_xaxis()
        ax.set_xlabel("Mean-scale redshift zbar = 1/a - 1")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.legend(fontsize=7)
        fig.tight_layout()
        fig.savefig(OUT/out,dpi=170)
        plt.close(fig)
    print("SOURCE_PLOTS",[(p.name,p.stat().st_size) for p in sorted(OUT.glob("INITIAL_Q_A_*.png"))])
if __name__=="__main__":run()
