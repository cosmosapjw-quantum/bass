#!/usr/bin/env python3
"""2D scientific plots from original source HYREC and BASS TypeII atomic data.

Original HYREC2 recombination kinetics are FLRW-calibrated SWIFT mode,
external TypeII H and proper hydrogen current are conditional inputs.
"""
import csv,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
parent=HERE.parents[1]/"research/typeii_hyrec2_history_20261102"
meta=json.loads((HERE/"R5_SOURCE_ATOMIC_TYPEII_PHOTON_RESULTS.json").read_text())
flrw=np.loadtxt(parent/"HYREC2_FLRW_XE_TM_8000.dat")
type_h=np.loadtxt(HERE/"NATIVE_TYPEII_HUBBLE_HHE_ATOMIC_XE_TM_8000.dat")
both=np.loadtxt(HERE/"NATIVE_TYPEII_H_AND_PROPER_NH_XE_TM_8000.dat")
density=np.loadtxt(HERE/"NATIVE_FLRW_H_AND_TYPEII_PROPER_NH_XE_TM_8000.dat")
hgrid=np.loadtxt(HERE/"TYPEII_H_COMPARE_FLRW_GRID.csv",delimiter=",",skiprows=1)
files=[flrw,type_h,both,density]
if not all(a.shape==(8000,3) for a in files):raise RuntimeError("HYREC_SOURCE_8000_OUTPUT_MISSING")
if not all(np.isfinite(a).all() for a in files):raise RuntimeError("NONFINITE_ORIGINAL_HYREC_KINETIC_OUTPUT")
disclaimer="Original HYREC2 native atomic kinetics; prescribed BASS gamma=1.3 Type-II H and class-A proper nH; not self-consistent cosmology"
def save(fig,filename):
    fig.text(.015,.013,disclaimer,fontsize=7)
    fig.tight_layout(rect=(0,.042,1,1))
    fig.savefig(HERE/filename,dpi=180)
    plt.close(fig)

fig,ax=plt.subplots(figsize=(7.5,4.7))
select=(hgrid[:,0]>=300)&(hgrid[:,0]<=1700)
ax.plot(hgrid[select,0],hgrid[select,3],label=r"$H_{\rm TypeII}/H_{\rm FLRW}$ from original Type-II ODE")
ax.set(xlabel="Mean-scale-factor label z_mean (not observed redshift)",ylabel="Expansion ratio",
       title="Original BASS Type-II mean expansion relative to native FLRW HYREC-2")
ax.set_xlim(1700,300)
ax.set_ylim(.45,1.04)
ax.grid(alpha=.25);ax.legend()
save(fig,"FIG01_ORIGINAL_TYPEII_H_RATIO.png")

fig,ax=plt.subplots(figsize=(7.5,4.7))
mask=(flrw[:,0]>=750)&(flrw[:,0]<=1700)
labels=["Native FLRW H, FLRW nH","Type-II H only","FLRW H, Type-II proper nH","Type-II H + proper nH"]
for x,label in zip([flrw,type_h,density,both],labels):
    ax.plot(x[mask,0],x[mask,1],label=label)
ax.set(xlabel="Mean-scale-factor label z_mean",ylabel=r"Free electron fraction $x_e=n_e/n_H$",
       title="Native HYREC-2 H/He kinetic solutions with BASS source H and nH")
ax.set_xlim(1700,750);ax.grid(alpha=.25);ax.legend(fontsize=8)
save(fig,"FIG02_ORIGINAL_HYREC_ATOMIC_4_LANES.png")

rows=list(csv.DictReader((HERE/"TYPEII_ATOMIC_THOMSON_EXTENDED_26RAY.csv").open(newline="")))
N=1167
if len(rows)!=N*26:raise RuntimeError("BASS_SOURCE_RAYS_MISSING")
tt=np.array([float(rows[k]["tau_H"]) for k in range(N)])
z=np.array([float(rows[k]["z_mean"]) for k in range(N)])
depth=np.array([[float(rows[j*N+k]["depth_native_TypeII_H_plus_proper_nH"])
                  for k in range(N)] for j in range(26)])
p,m=meta["physical_plus_minus_axes"]
fig,ax=plt.subplots(figsize=(7.5,4.7))
for j in range(26):ax.plot(z,depth[j],alpha=.19,linewidth=.9)
ax.plot(z,depth[p],linewidth=2.2,label=r"Axial $+e_y$")
ax.plot(z,depth[m],linewidth=2.2,label=r"Axial $-e_y$")
ax.set(xlabel="Mean-scale-factor label z_mean",
       ylabel="Integrated conditional Thomson optical depth",
       title="Original Type-II 26 geodesics + native HYREC2 H and proper nucleus")
ax.set_xlim(1700,300);ax.grid(alpha=.25);ax.legend()
save(fig,"FIG03_BASS_TYPEII_NATIVE_ATOM_26_DEPTH.png")
print("SCOPED_SCIENCE_FIGURES=3 SOURCE_DATA_VERIFIED")
