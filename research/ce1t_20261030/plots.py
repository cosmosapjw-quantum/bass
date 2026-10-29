"""CE1-T reproducible figures from source-locked Rust quadrature evidence."""
import argparse,csv,io,json,zipfile
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
p=argparse.ArgumentParser();p.add_argument('--data',required=True);p.add_argument('--old-atlas-zip',default='');p.add_argument('--output',required=True);arg=p.parse_args()
d=json.load(open(arg.data));out=Path(arg.output);out.mkdir(exist_ok=True,parents=True)
res=d['results'];ordr=sorted(int(k) for k in res if int(k)!=40)
fig,ax=plt.subplots(figsize=(9.0,5.2))
ax.loglog([res[str(n)]['rays'] for n in ordr],[res[str(n)]['max_abs_delta_C4prime_vs_GL40'] for n in ordr],'o-',label='Cellwise Gauss–Legendre, 41 epochs')
ax.axhline(1e-9,linestyle='--',color='gray',label='Exploratory absolute threshold 1e-9')
ax.set_xlabel('Number of positive-octant rays (6n²)');ax.set_ylabel(r'Max $|dC_4^U/du - dC_{4,\mathrm{GL40}}^U/du|$')
ax.set_title('BASS Rust Liouville: 6-cell quadrature convergence')
ax.grid(alpha=.25,which='both');ax.legend(loc='best');fig.tight_layout();fig.savefig(out/'CE1T_GL_CONVERGENCE.png',dpi=180);plt.close(fig)
fig,ax=plt.subplots(figsize=(9.0,5.2))
u=np.array([r['u'] for r in res['40']['stats']);
for n in (2,4,6,40):
    x=np.array([r['C4prime'] for r in res[str(n)]['stats']]);ax.plot(u,x,label=f'cellwise GL{n} ({res[str(n)]["rays"]} rays)',linewidth=1.8 if n in (6,40) else 1)
if arg.old_atlas_zip:
 with zipfile.ZipFile(arg.old_atlas_zip) as z:
  olds=list(csv.DictReader(io.StringIO(z.read('stored_ref8_fixed_gl40.csv').decode())))
  vals=[]
  for row in olds:
   a=np.array([complex(float(row[f'a_4_{m}_re']),float(row[f'a_4_{m}_im'])) for m in range(-4,5)])
   da=np.array([complex(float(row[f'da_4_{m}_re']),float(row[f'da_4_{m}_im'])) for m in range(-4,5)])
   vals.append(2*np.vdot(a,da).real/9.)
  assert np.max(np.abs(np.array([float(q['u']) for q in olds])-u))<1e-14
  ax.plot(u,vals,'--',label='Original stored ref8, fixed GL40 geometry',linewidth=1)
ax.set_xlabel('Proper dimensionless time u=t/Tstar')
ax.set_ylabel(r'$dC_4^U/du$ (energy-integrated sky)')
ax.set_title('Angular quadrature vs original midpoint ray source')
ax.grid(alpha=.25);ax.legend(loc='best',fontsize=9);fig.tight_layout();fig.savefig(out/'CE1T_C4PRIME_41_EPOCH.png',dpi=180);plt.close(fig)
