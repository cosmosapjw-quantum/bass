#!/usr/bin/env python3
"""Physical source-locked, normal-frame CE1AH response figures."""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'data';F=ROOT/'figures';F.mkdir(exist_ok=True)
with (D/'CE1AH_TANGENT_PHYSICAL.csv').open(newline='') as f:rows=list(csv.DictReader(f))
with (D/'CE1AH_BASELINE_PHYSICAL.csv').open(newline='') as f:base=list(csv.DictReader(f))

for title,k1,k2,name in [
 ('Coupled initial-shear response of fractional angular multipoles','dC2','dC4','CE1AH_GL16_C2_C4_RESPONSES.png'),
 ('Shear-radiation exchange response','dW','dq','CE1AH_GL16_WORK_RESPONSE.png'),
 ('Volume-corrected photon energy response','denergy_ratio','d_cumulative_q','CE1AH_GL16_ENERGY_TRANSFER_RESPONSE.png')]:
    fig,ax=plt.subplots(figsize=(10,5.8),layout='constrained')
    for mode in ('A_xy','B_axial'):
        s=[r for r in rows if int(r['GL'])==16 and r['mode']==mode]
        t=[float(r['u']) for r in s]
        ax.plot(t,[float(r[k1]) for r in s],label=f'{mode}: {k1}',linewidth=2)
        ax.plot(t,[float(r[k2]) for r in s],label=f'{mode}: {k2}',linestyle='--',linewidth=1.7)
    ax.set(title=title,xlabel=r'Original proper time $u=t/T_*$',ylabel='Derivative per unit initial traceless shear parameter')
    ax.grid(alpha=.24);ax.legend(ncol=2,fontsize=9)
    fig.savefig(F/name,dpi=155)
    plt.close(fig)

# Resolve the smaller l=4 response on its own scientifically scaled axes.
fig,ax=plt.subplots(figsize=(9,5.4),layout='constrained')
for mode in ('A_xy','B_axial'):
    s=[r for r in rows if int(r['GL'])==16 and r['mode']==mode]
    ax.plot([float(r['u']) for r in s],[float(r['dC4']) for r in s],linewidth=2,label=mode)
ax.set(title='Self-consistent fractional l=4 response (zoom)',xlabel=r'Proper $u=t/T_*$',ylabel=r'$\partial C_4 / \partial\epsilon_{A,B}$')
ax.grid(alpha=.24);ax.legend()
fig.savefig(F/'CE1AH_GL16_C4_RESPONSES_DETAILED.png',dpi=155);plt.close(fig)

# Baseline physical anchor: no fabricated thermal sky.
fig,ax=plt.subplots(figsize=(9.5,5.5),layout='constrained')
s=[r for r in base if int(r['GL'])==16]
t=np.array([float(r['u']) for r in s]);
for field in ('C2','C4','W'):
    ax.plot(t,[float(r[field]) for r in s],label=f'original physical {field}',linewidth=2)
ax.set(xlabel=r'Proper $u=t/T_*$', ylabel='Dimensionless original Einstein-Vlasov observable',title='Original six-cell baseline (GL16, 401 actual IVP epochs)')
ax.grid(alpha=.24);ax.legend()
fig.savefig(F/'CE1AH_ORIGINAL_BASELINE_PHYSICS.png',dpi=155);plt.close(fig)
print('CE1AH_PLOTS',len(list(F.glob('*.png'))))
