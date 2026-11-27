"""Audit actual coefficient arrays, physical controls and native spin convention."""
import numpy as np,json,sys
from pathlib import Path
from scipy.special import sph_harm_y
D=Path(__file__).resolve().parent;P=D.parent/'r118c3p_analytic_s4'
from controls import check
from multi import objective
def run():
 files=sorted(D.glob('*.npz'));assert len(files)==18,len(files)
 rows={}
 for f in files:
  z=np.load(f);B=z['B'];C=z['control'];q=check(C)
  assert np.isfinite(B).all() and abs(q['norm']-1)<1e-14 and q['wedge_ratio']>=.8-1e-8 and q['wedge_direction_error']<1e-5
  rows[f.stem]=dict(**q,B3=np.linalg.norm(B[:,9:16],axis=1).tolist(),objective=float(objective(B[:,9:16])))
 # Independent spin convention check against prior actual native generator.
 z=np.genfromtxt(P/'spin10.csv.gz',names=True,delimiter=',');nr=int(z['ray'].max()+1);mu=z['mu'][:nr];phi=z['phi'][:nr];theta=np.arccos(mu);sn=np.sqrt(1-mu*mu)
 Y=(z['re']+1j*z['im']).reshape(121,nr);err=[]
 for l in range(2,11):
  for m in range(-l,l+1):
   f,g=sph_harm_y(l,m,theta,phi,diff_n=1);ft=g[:,0];ftt=-mu/sn*ft+(m*m/sn**2-l*(l+1))*f
   y=(ftt-(2*m+mu)/sn*ft+(m*m+2*m*mu)/sn**2*f)/np.sqrt((l-1)*l*(l+1)*(l+2))
   v=Y[l*l+l+m];err.append(float(np.linalg.norm(y-v)/np.linalg.norm(v)))
 p=json.loads((D/'PURE_WINDOW.json').read_text());maxleak=max(v['worst_E_leakage'] for k,v in p['rows'].items() if k.endswith('pure'))
 out=dict(rows=rows,native_spin_relative=max(err),pure_leakage=maxleak,scope='independent saved arrays and analytic spin derivative vs native basis; numerical wedge not exact rank')
 (D/'AUDIT.json').write_text(json.dumps(out,indent=2)+'\n');print('cases',len(rows),'spin',max(err),'pure',maxleak,flush=True)
 assert max(err)<1e-9 and maxleak<1e-9
if __name__=='__main__':run()
