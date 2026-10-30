#!/usr/bin/env python3
"""Generate source-qualified BASS CE1-AF original-physics figures, no CMB interpretation."""
import csv,math,gzip,hashlib
from pathlib import Path
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'figures';OUT.mkdir(exist_ok=True,parents=True)
with (ROOT/'data'/'CE1AF_PHYSICAL_TIMELINE.csv').open(newline='') as f:
    rows=list(csv.DictReader(f))
rows=[r for r in rows if int(r['GL'])==64]
u=np.array([float(r['u']) for r in rows]);C2=np.array([float(r['C2_fractional']) for r in rows]);W=np.array([float(r['shear_work']) for r in rows]);E_ratio=np.array([float(r['volume_compensated_E_ratio']) for r in rows]);S2=np.array([float(r['shear_energy']) for r in rows]);I=np.array([float(r['cum_shear_work_over_E']) for r in rows]);
parent_gz=ROOT/'input'/'CE1AE_PARENT_C4_DENSE.csv.gz'
assert hashlib.sha256(parent_gz.read_bytes()).hexdigest()=='45b4fbae270d55fe75b62650f54572c863d98d7a10a2707d189533d3a4745e54'
with gzip.open(parent_gz,'rt',newline='') as f:
    prior=list(csv.DictReader(f))
prior=[r for r in prior if int(r['GL'])==64]
assert len(prior)==len(rows)==401
C4=np.array([float(r['C4_fractional']) for r in prior]);assert np.max(np.abs(u-np.array([float(r['u']) for r in prior])))<1e-15
fig,ax=plt.subplots(figsize=(8.8,5.1));ax.plot(u,C2,label=r'$C_2$ (fractional quadrupole)');ax.plot(u,C4,label=r'$C_4$ (fractional hexadecapole)');ax.set(xlabel=r'Proper time $u=t/T_\star$',ylabel=r'Normalized bolometric angular power',title='Original six-cell collisionless sky: quadrupole vs hexadecapole');ax.legend();ax.grid(alpha=.22);fig.tight_layout();fig.savefig(OUT/'CE1AF_GL64_C2_VS_C4_REAL_PHYSICS.png',dpi=185);plt.close(fig)
fig,ax=plt.subplots(figsize=(8.8,5.1));ax.plot(u,W,label=r'$W=\sigma_i\Pi_i$');ax.plot(u,S2,label=r'$S_\sigma=\frac{1}{2}\sum_i\sigma_i^2$');ax.set(xlabel=r'Proper time $u=t/T_\star$',ylabel='Dimensionless Einstein-normalized quantities',title='Anisotropic radiation-shear energy exchange');ax.legend();ax.grid(alpha=.22);fig.tight_layout();fig.savefig(OUT/'CE1AF_GL64_SHEAR_RADIATION_WORK.png',dpi=185);plt.close(fig)
fig,ax=plt.subplots(figsize=(8.8,5.1));ax.plot(u,1e4*(E_ratio-1),label=r'$10^4(Ee^{4\bar\ell}/E_0-1)$');ax.plot(u,-1e4*I,label=r'$-10^4\int_0^u W/E\,du$ (linearized)');ax.set(xlabel=r'Proper time $u=t/T_\star$',ylabel='Parts in $10^4$',title='Radiation energy beyond mean-volume dilution');ax.legend();ax.grid(alpha=.22);fig.tight_layout();fig.savefig(OUT/'CE1AF_GL64_VOLUME_COMPENSATED_ENERGY.png',dpi=185);plt.close(fig)
for f in OUT.glob('CE1AF*.png'):print(f.name,f.stat().st_size)
