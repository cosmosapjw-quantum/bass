#!/usr/bin/env python3
"""Scientific figures only from source-conditioned BASS Saha model output CSV."""
from pathlib import Path
import csv, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
summary=json.loads((HERE/"PHYSICAL_SAHA_THOMSON_SUMMARY.json").read_text())
with (HERE/"HYDROGEN_SAHA_HISTORY_401.csv").open(newline="") as f:
    h=list(csv.DictReader(f))
with (HERE/"SAHA_THOMSON_RAYS_401X26.csv").open(newline="") as f:
    rows=list(csv.DictReader(f))
assert len(h)==401 and len(rows)==401*26
def column(name):return np.array([float(r[name]) for r in h])
tau=column("tau_H"); z=column("z_mean_not_observed")
xe=column("x_e_H_only_source_Saha")
ne=column("n_e_rest_cm_minus3")
nu=column("nu_source_prefactor_Gamma_nu_rest")
ray=np.zeros((26,401))
for r in rows:
    j=int(r["ray_id"])
    k=int(round(float(r["tau_H"])/.0005))
    ray[j,k]=float(r["integrated_thomson_depth"])
axis_p=int(summary["positive_ey_ray_id"])
axis_m=int(summary["negative_ey_ray_id"])
meta="Source-conditioned H-only Saha, mean z=1700 to 1392; not full Bianchi recombination"

fig,ax=plt.subplots(figsize=(7.2,4.6))
ax.plot(z,xe)
ax.set(xlabel="Mean-scale-factor thermal label z_mean (not observed redshift)",
       ylabel="Hydrogen ionization fraction x_e",title="BASS Type-II: original hydrogen Saha equilibrium")
ax.set_xlim(z.max(),z.min());ax.set_ylim(0,1.03); ax.grid(alpha=.25)
fig.text(.01,.01,meta,fontsize=7)
fig.tight_layout(rect=(0,.035,1,1))
fig.savefig(HERE/"FIG01_HYDROGEN_XE.png",dpi=170)
plt.close(fig)
fig,ax=plt.subplots(figsize=(7.2,4.6))
ax.plot(tau,ne,label=r"$n_e^{\rm rest}$ (cm$^{-3}$)")
ax2=ax.twinx()
ax2.plot(tau,nu,linestyle="--",label="Normal-frame scalar Thomson prefactor")
ax.set(xlabel=r"Hubble time $\tau_H$",ylabel=r"Electron-rest proper $n_e$ (cm$^{-3}$)",
       title="BASS Type-II: conserved baryon current + Saha proper electrons")
ax2.set_ylabel(r"$\Gamma\,n_e^{\rm rest}\sigma_T c/H$ (dimensionless)")
ax.grid(alpha=.25); fig.text(.01,.01,meta,fontsize=7)
fig.tight_layout(rect=(0,.035,1,1))
fig.savefig(HERE/"FIG02_ELECTRON_RATE.png",dpi=170)
plt.close(fig)
fig,ax=plt.subplots(figsize=(7.2,4.6))
for k in range(26):
    ax.plot(tau,ray[k,:],alpha=.25,linewidth=.8)
ax.plot(tau,ray[axis_p],linewidth=2.1,label=r"Axial $+e_y$")
ax.plot(tau,ray[axis_m],linewidth=2.1,label=r"Axial $-e_y$")
ax.set(xlabel=r"Hubble time $\tau_H$",ylabel=r"Integrated conditional Thomson depth $\mathcal{T}$",
       title="BASS Type-II: 26 source-ray physical-dimension opacity scenarios")
ax.legend();ax.grid(alpha=.25);fig.text(.01,.01,meta,fontsize=7)
fig.tight_layout(rect=(0,.035,1,1))
fig.savefig(HERE/"FIG03_THOMSON_DEPTH_26.png",dpi=170)
plt.close(fig)
print("SCIENTIFIC_FIGURES_GENERATED 3 SOURCE_CONDITIONAL")
