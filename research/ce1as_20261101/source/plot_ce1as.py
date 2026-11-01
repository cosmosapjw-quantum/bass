"""Two source-bound physical figures; no source transformations or fitted data."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'figures';OUT.mkdir(exist_ok=True)
with (ROOT/'data'/'CE1AS_BIANCHI_VS_FLRW.csv').open() as f: r=list(csv.DictReader(f))
axes={}
for row in r:
 if row['GL']=='24' and row['eps']=='0.0' and row['direction'] in ('x','y','z'):
  axes[(row['direction'],float(row['z']))]=row
zs=sorted(set(z for _,z in axes))
fig,ax=plt.subplots(figsize=(7.8,4.5))
for direction in ('x','y','z'):
 ax.plot(zs,[float(axes[(direction,z)]['D_A_Bianchi']) for z in zs],marker='o',label='Bianchi '+direction)
ax.plot(zs,[float(axes[('x',z)]['D_A_FLRW_E0_matched']) for z in zs],marker='s',ls='--',label='Independent FLRW')
ax.set(xlabel='Observed redshift z',ylabel=r'$D_A/(cT_*)$',title='Energy-monopole-matched FLRW vs original Bianchi I (GL24)')
ax.legend();ax.grid(alpha=.25);fig.tight_layout()
for ext in ('png','svg'):fig.savefig(OUT/f'CE1AS_distances.{ext}',dpi=170)
plt.close(fig)
fig,ax=plt.subplots(figsize=(7.8,4.5))
for direction in ('x','y','z'):
 ax.plot(zs,[100*float(axes[(direction,z)]['fractional_DA_difference']) for z in zs],marker='o',label='Bianchi '+direction+' / FLRW - 1')
ax.plot(zs,[100*float(axes[('x',z)]['proxy_fractional_error_to_FLRW']) for z in zs],ls='--',label='Old equal-volume proxy / FLRW - 1')
ax.axhline(0,linewidth=.7)
ax.set(xlabel='Observed redshift z',ylabel='Fractional distance difference (%)',title='Geometry/matter contrast vs physical FLRW and old proxy')
ax.legend();ax.grid(alpha=.25);fig.tight_layout()
for ext in ('png','svg'):fig.savefig(OUT/f'CE1AS_distance_contrasts.{ext}',dpi=170)
plt.close(fig)
print('CE1AS_PLOTS=2_PNG_2_SVG')
