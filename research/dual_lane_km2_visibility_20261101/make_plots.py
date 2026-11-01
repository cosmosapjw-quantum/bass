from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'figures';OUT.mkdir(exist_ok=True)
R=ROOT/'results'
with (R/'KM2_ORIGINAL_SKY_VISIBILITY_TIME.csv').open(newline='') as f:
 rows=list(csv.DictReader(f))
fig,ax=plt.subplots(figsize=(7.5,4.7))
for grid in ('GL12','GL16'):
 sub=[x for x in rows if x['grid']==grid]
 u=[float(x['u']) for x in sub]
 y=[float(x['weighted_mean_visibility_conditional_du']) for x in sub]
 ax.plot(u,y,label=grid)
ax.set_xlabel('Normal-frame dimensionless time u = t/T*')
ax.set_ylabel('Conditional Thomson visibility density per u')
ax.set_title('Source-owned P8/Peebles ray visibility (not CMB)')
ax.grid(alpha=.25);ax.legend();fig.tight_layout()
for ext in ['png','svg']:fig.savefig(OUT/f'conditional_visibility_time.{ext}',dpi=170)
plt.close(fig)
with (R/'KM2_ORIGINAL_SKY_VISIBILITY_RAYS.csv').open(newline='') as f:
 rows=list(csv.DictReader(f))
fig,ax=plt.subplots(figsize=(7.5,4.7))
for grid in ('GL12','GL16'):
 sub=[x for x in rows if x['grid']==grid]
 nz=np.array([float(x['nobs_z']) for x in sub]);z50=np.array([float(x['event_q50_redshift']) for x in sub])
 ax.scatter(nz,z50,s=8,alpha=.45,label=grid)
ax.set_xlabel('Observed photon sky direction n_z')
ax.set_ylabel('Source-owned event median redshift z50')
ax.set_title('Same-source redshift of Thomson-kernel median')
ax.grid(alpha=.25);ax.legend(markerscale=2);fig.tight_layout()
for ext in ['png','svg']:fig.savefig(OUT/f'event_redshift_sky.{ext}',dpi=170)
plt.close(fig)
print('SCIENCE_FIGURES',[(x.name,x.stat().st_size) for x in OUT.iterdir()])