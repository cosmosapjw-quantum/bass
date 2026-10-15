"""Plot the actual 501-point source-frozen Einstein–Vlasov histories."""
from __future__ import annotations
import csv
from collections import defaultdict
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
ev=HERE/"evidence"
rows=defaultdict(list)
with (ev/"TABLES/AXBI_INITIAL_STRESS_BACKGROUND.csv").open() as f:
    for row in csv.DictReader(f):
        rows[(float(row["q_ref"]),float(row["kappa"]))].append(row)

def series(q,k,field):
    return [float(x[field]) for x in rows[(q,k)]]

def render():
    keep=[(0,0),(0,.2),(0,-.2),(.005,0),(.005,.2),(.005,-.2),(.01,0),(.01,.2)]
    for ykey,filename,ylabel,title in [
      ("b","B_VS_Z.png","b(a)","Bianchi I shear and initial photon quadrupole"),
      ("s_over_h","SHEAR_OVER_H.png","s/H","Stress-supported shear evolution"),
      ("pi_s_J_m3","PI_S_J_M3.png","pi_s [J/m³]","Collisionless angular anisotropic pressure"),
      ("radiation_M","RADIATION_ENERGY_M.png","M(b,kappa)","Radiation energy conservation correction")]:
        fig,ax=plt.subplots(figsize=(8.7,5.0))
        for q,k in keep:
            ax.plot(series(q,k,"zbar"),series(q,k,ykey),label=f"q={q:+.3f}, kappa={k:+.2f}")
        ax.invert_xaxis()
        ax.set(xlabel="Mean redshift (zbar=1/a-1)",ylabel=ylabel,title=title)
        ax.legend(fontsize=8);fig.tight_layout()
        fig.savefig(ev/filename,dpi=175);plt.close(fig)
if __name__=="__main__":
    render()
    print("PLOTS",[p.name for p in ev.glob("*.png")])
