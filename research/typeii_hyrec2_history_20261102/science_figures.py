#!/usr/bin/env python3
"""Source-scoped visualizations of native HyRec-2 and actual extended TypeII rays."""
from pathlib import Path
import csv,json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent
native=np.loadtxt(HERE/"HYREC2_FLRW_XE_TM_8000.dat")
original_Saha=list(csv.DictReader(
    (HERE.parents[1]/"research/typeii_conserved_saha_20261102/HYDROGEN_SAHA_HISTORY_401.csv").open(newline="")))
old_z=np.array([float(r["z_mean_not_observed"]) for r in original_Saha])
old_xe=np.array([float(r["x_e_H_only_source_Saha"]) for r in original_Saha])
summary=json.loads((HERE/"EXTENDED_RECOMB_WINDOW_RESULT.json").read_text())
rows=list(csv.DictReader((HERE/"EXTENDED_TYPEII_HYREC2_RAY_26.csv").open(newline="")))
step=int(summary["extended_time_samples"])
if len(rows)!=26*step:raise RuntimeError("ORIGINAL_EXTENDED_26_RAY_INPUT_MISSING")
tau=np.array([float(r["tau_H"]) for r in rows[:step]])
z=np.array([float(r["z_mean_not_observed"]) for r in rows[:step]])
depth=np.array([[float(rows[j*step+k]["cumulative_depth"]) for k in range(step)]
                for j in range(26)])
g=np.array([[float(rows[j*step+k]["last_event_kernel_to_z300"]) for k in range(step)]
            for j in range(26)])
initial_directions=np.array([[float(rows[j*step][f]) for f in ("n_x","n_y","n_z")]
                             for j in range(26)])
plus=next(j for j in range(26) if np.max(abs(initial_directions[j]-[0,1,0]))<1e-12)
minus=next(j for j in range(26) if np.max(abs(initial_directions[j]-[0,-1,0]))<1e-12)
label="FLRW HyRec-2 H/He x_e on prescribed Type-II geometry; not self-consistent Bianchi recombination"
def save(fig,name):
    fig.text(.01,.012,label,fontsize=7)
    fig.tight_layout(rect=(0,.045,1,1))
    fig.savefig(HERE/name,dpi=170)
    plt.close(fig)

fig,ax=plt.subplots(figsize=(7.5,4.6))
good=(native[:,0]>=300)&(native[:,0]<=1700)
ax.plot(native[good,0],native[good,1],label="Native FLRW HYREC-2 H/He non-equilibrium")
ax.plot(old_z,old_xe,"--",label="Former BASS hydrogen-only Saha, z=1392..1700")
ax.set(xlabel="Mean thermal label z_mean (not observed ray redshift)",
       ylabel="Free-electron fraction x_e=n_e/n_H",
       title="Source HYREC-2 recombination versus previous equilibrium Saha")
ax.set_xlim(1800,300);ax.legend();ax.grid(alpha=.25)
save(fig,"FIG_HYREC2_VS_SAHA_XE.png")

fig,ax=plt.subplots(figsize=(7.5,4.6))
for j in range(26):
    ax.plot(z,depth[j],alpha=.25,linewidth=.9)
ax.plot(z,depth[plus],linewidth=2,label=r"Axial $+e_y$")
ax.plot(z,depth[minus],linewidth=2,label=r"Axial $-e_y$")
ax.set(xlabel="Mean thermal label z_mean",
       ylabel="Cumulative Thomson optical depth from zmean=1700",
       title="Actual 26 extended Type-II rays + native FLRW HyRec-2 source")
ax.set_xlim(1700,300);ax.legend();ax.grid(alpha=.25)
save(fig,"FIG_TYPEII_EXTENDED_DEPTH_26.png")

fig,ax=plt.subplots(figsize=(7.5,4.6))
for j in range(26):
    ax.plot(z,g[j],alpha=.2,linewidth=.75)
ax.plot(z,g[plus],linewidth=2.1,label=r"Conditional $+e_y$")
ax.plot(z,g[minus],linewidth=2.1,label=r"Conditional $-e_y$")
ax.set(xlabel="Mean thermal label z_mean",
       ylabel=r"$g_{\rm last} = \nu(\tau_H)e^{-\int_{\tau_H}^{\tau_{\rm obs}}\nu dt}$",
       title="Finite-observer zmean=300 attenuation kernel (not z=0 CMB visibility)")
ax.set_xlim(1400,700);ax.legend();ax.grid(alpha=.25)
save(fig,"FIG_FINITE_OBSERVER_ATTENUATION_KERNEL_26.png")
print("FIGURES_SOURCE_CONDITIONAL_3_PASS")
