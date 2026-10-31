#!/usr/bin/env python3
"""Regenerate six science figures from real CE1AL original source-owned numerical histories."""
import csv,math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
with (ROOT/'data'/'CE1AL_WEYL_CURVATURE_TANGENT.csv').open(newline='') as f: allrows=list(csv.DictReader(f))
OUT=ROOT/'figures';OUT.mkdir(exist_ok=True)
spec=[
 ('CE1AL_DARK_WEYLsq_FULL','dWeylSq','original_horizon',False),
 ('CE1AL_DARK_KRETSCHMANN_FULL','dKretschmann','original_horizon',False),
 ('CE1AL_DARK_ELECTRIC_WEYL1_SHORT','dElectricWeyl1','short_curvature',False),
 ('CE1AL_DARK_WEYLsq_SHORT_OVER_U2','dWeylSq','short_curvature',True),
 ('CE1AL_BASELINE_WEYLsq','WeylSq','original_horizon',False),
 ('CE1AL_NORMALIZED_WEYLsq','dWeylSq_over_E2','original_horizon',False)]
for name,key,window,scaled in spec:
 fig,ax=plt.subplots(figsize=(7.2,4.2))
 for gl in ('6','8','16'):
  rs=[r for r in allrows if r['GL']==gl and r['window']==window]
  u=[float(r['u']) for r in rs];v=[float(r[key]) for r in rs]
  if scaled:u,v=u[1:],[v[i]/(u[i]**2) for i in range(1,len(u))]
  ax.plot(u,v,label=f'GL{gl}',lw=1.3)
 ax.set_xlabel('Original dimensionless proper time u=t/T*');ax.set_ylabel(key+(' /u²' if scaled else ''))
 ax.set_title(name.replace('_',' '));ax.legend();ax.grid(alpha=.2);fig.tight_layout()
 fig.savefig(OUT/(name+'.png'),dpi=165);fig.savefig(OUT/(name+'.svg'));plt.close(fig)
print('CE1AL_REMOTE_SCIENCE_FIGURES',len(spec),flush=True)
