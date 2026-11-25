"""Independent NumPy evaluation of final per-absorber Verner moments.
No extra angular weights: packet counts already include them.
Actual terminal spectrum, not a bound on all preceding steps.
"""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--rei',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
C=2.99792458e10
pars=np.array([(13.60,.4298,5.475e4,32.88,2.963,0.,0.,0.),(24.59,13.61,949.2,1.469,3.188,2.039,.4434,2.136),(54.42,1.720,1.369e4,32.88,2.963,0.,0.,0.)])
bind=np.array([13.598434599702,24.587389011,54.41776])
def sig(E):
 out=[]
 for eth,e0,s0,ya,p,yw,y0,y1 in pars:
  x=E/e0-y0;y=np.sqrt(x*x+y1*y1)
  out.append(np.where(E>=eth,s0*((x-1)**2+yw*yw)*y**(p/2-5.5)*(1+np.sqrt(y/ya))**(-p)*1e-18,0.))
 return np.array(out)
def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
rows=[];J=json.loads((a.root/'RESULTS.json').read_text())
for r in J['cases']:
 root=a.root/r['case'];q=np.genfromtxt(root/'packets.tsv',names=True,delimiter='\t');h=np.genfromtxt(root/'history.tsv',names=True,delimiter='\t')
 E=q['energy_eV'];N=q['N_per_H'];s=sig(E);nh=h['nH_m3'][-1]*1e-6
 gamma=C*nh*(s@N);heat=C*nh*((s*(E[None,:]-bind[:,None]))@N)
 assert np.all(gamma>=0) and np.all(heat>=0)
 rows.append(dict(case=r['case'],end=r['end'],gamma_s=gamma.tolist(),heat_eV_per_absorber_s=heat.tolist(),packets_sha256=sha(root/'packets.tsv')))
base=next(x for x in rows if x['case']=='z4_q+0_n8192_s16_w0.04_tNone')
for r in rows:
 if r['end']==4:
  r['rel_to_w004_8192']={k:(np.asarray(r[k])/np.asarray(base[k])-1).tolist() for k in ('gamma_s','heat_eV_per_absorber_s')}
r=next(c for c in J['cases'] if c['steps']==32768)
h=np.genfromtxt(a.root/r['case']/'history.tsv',names=True,delimiter='\t');q=np.genfromtxt(a.rei,names=True,delimiter=',')
z=21*np.exp(-h['eta'])-1;zz=np.linspace(4.,20.,20001)
dif={};shared=[]
for k,l in [('x_HII','x_HII'),('x_HeII','x_HeII'),('x_HeIII','x_HeIII'),('temperature_K','Tm_K')]:
 u=np.interp(zz,q['zbar'][::-1],q[k][::-1]);v=np.interp(zz,z[::-1],h[l][::-1])
 dif[k]=dict(max_abs=float(np.max(abs(u-v))),max_relative_to_rei64=float(np.max(abs(u-v)/np.maximum(abs(u),1e-8))),terminal_rei64=float(u[0]),terminal_bass=float(v[0]))
a.out.write_text(json.dumps(dict(scope='independent terminal Verner formula and matched-redshift distinct-scheme comparison',cases=rows,rei64_vs_guarded_bass=dif,rei64_history_sha256=sha(a.rei)),indent=2)+'\n')
print('TERMINAL COMPARISON',json.dumps(dif,indent=2))
for r in rows:
 if r['end']==4:print(r['case'],r['gamma_s'],r['heat_eV_per_absorber_s'],r.get('rel_to_w004_8192'))
