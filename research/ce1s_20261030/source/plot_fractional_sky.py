"""Publication figures from CE1-S saved physical data; no new physics solver."""
from pathlib import Path
import csv,sys,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=Path(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
rows=list(csv.DictReader((p/'fractional_angular_power_164rows.csv').open()))
for l in (2,4):
    fig,ax=plt.subplots(figsize=(7,4.1))
    for ch in ('stored_ref8','stored_ref16','gl24','gl40'):
        s=[v for v in rows if v['channel']==ch]
        ax.plot([float(v['u']) for v in s],[float(v[f'Cdelta{l}']) for v in s],label=ch)
    ax.set(xlabel='Proper time u=t/Tstar',ylabel=f'Fractional angular power C{l}_delta',title=f'BASS CE1-S: fractional unpolarized bolometric angular power l={l}')
    ax.grid(alpha=.2);ax.legend();fig.tight_layout();fig.savefig(out/f'fractional_C{l}_history.png',dpi=160);plt.close(fig)
arr=np.load(p/'fractional_sky_maps_3epochs.npz')
fig,ax=plt.subplots(figsize=(9,4))
im=ax.imshow(arr['u_40_delta'],origin='lower',aspect='auto',extent=(0,360,0,180),interpolation='nearest')
ax.set(xlabel='Azimuth (deg)',ylabel='Polar angle (deg)',title='BASS CE1-S: normal-observer fractional energy sky at u=0.08')
fig.colorbar(im,ax=ax,label='fractional energy contrast');fig.tight_layout();fig.savefig(out/'fractional_sky_u008.png',dpi=160);plt.close(fig)
print('PLOTS_DONE')
