#!/usr/bin/env python3
"""Plot source-conditional FIRST scattering event density, not CMB visibility."""
import csv,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent
s=json.loads((HERE/"PHYSICAL_SAHA_THOMSON_SUMMARY.json").read_text())
records=list(csv.DictReader((HERE/"FIRST_SCATTER_401X26.csv").open(newline="")))
if len(records)!=401*26:raise RuntimeError("NOT_401X26_FIRST_SCATTER")
density=np.zeros((26,401))
times=np.zeros(401)
for row in records:
    j=int(row["ray_id"]); k=int(round(float(row["tau_H"])/.0005))
    density[j,k]=float(row["first_scattering_density_per_tau_H"])
    if j==0:times[k]=float(row["tau_H"])
p=int(s["positive_ey_ray_id"]);m=int(s["negative_ey_ray_id"])
fig,ax=plt.subplots(figsize=(7.3,4.6))
for j in range(26):ax.plot(times,density[j],alpha=.2,linewidth=.75)
ax.plot(times,density[p],linewidth=2.0,label=r"first event along $+e_y$")
ax.plot(times,density[m],linewidth=2.0,label=r"first event along $-e_y$")
ax.set_xlim(0,.035)
ax.set(xlabel=r"Source Hubble time $\tau_H$",ylabel=r"First scattering density $g_1=\nu e^{-\mathcal{T}}$",
       title="BASS Type-II: first Thomson event on hydrogen-only Saha source")
ax.legend();ax.grid(alpha=.25)
fig.text(.015,.01,"Conditional early high-z model; not observed CMB last-scattering visibility",fontsize=7)
fig.tight_layout(rect=(0,.035,1,1))
fig.savefig(HERE/"FIG04_FIRST_SCATTER.png",dpi=170)
plt.close(fig)
print("FIRST_SCATTER_PLOT_SOURCE_CONDITIONAL_PASS")
