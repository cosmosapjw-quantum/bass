"""Independent saved-array admission, scope and reproducibility audit."""
import numpy as np,json
from pathlib import Path
D=Path(__file__).resolve().parent
def main():
 f=np.load(D/'FAMILY.npz');A,M,G,H,W=[f[k] for k in ['A','M','G','H','W']];B=np.sum(A*A)
 rows={};files=[x for x in D.glob('*.npz') if x.name!='FAMILY.npz'];assert len(files)==19
 for p in files:
  z=np.load(p);C=z['control'];aw=C@np.linalg.inv(H);norm=float(np.trace(C@G@C.T));w=aw@M@aw.T
  assert abs(norm-B)<1e-12 and np.linalg.norm(w)/np.linalg.norm(W)>.9-1e-10 and np.isfinite(z['B']).all()
  target=W*(np.linalg.norm(w)/np.linalg.norm(W));err=float(np.linalg.norm(w-target)/np.linalg.norm(W));assert err<1e-5
  y=np.linspace(0,60,1001);a=-.5*((y-.7)/1.4)**2;b=-.5*((y-8.)/1.4)**2;win=1/(1+np.exp(np.clip(b-a,-700,700)))
  peak=max(np.linalg.norm(C[:,1+2*s:3+2*s]@np.array([win,1-win]),axis=0).max() for s in range(3))
  v=z['B'][:,9:16];eps=.01;obj=float(max(np.linalg.norm(np.array([(sg*eps)**k for k in range(1,6)])@v) for sg in [-1,1]))
  rows[p.stem]=dict(budget=norm,wedge_ratio=float(np.linalg.norm(w)/np.linalg.norm(W)),wedge_direction_error=err,peak_stf=float(peak),eps_peak=float(eps*peak),objective=obj,B3=np.linalg.norm(v,axis=1).tolist())
 a=rows['base_4096'];b=rows['best_4096'];q=json.loads((D/'OPT.json').read_text());assert abs(b['objective']-q['fine_best'])<1e-26
 out=dict(cases=len(rows),rows=rows,ratio=b['objective']/a['objective'],quartic_ratio=b['B3'][3]/a['B3'][3],wedge_normalized_quartic_ratio=b['B3'][3]/a['B3'][3]/b['wedge_ratio']**2,scope='saved coefficient and actual control audit, FD occupation valid by construction; finite bounded rank-one search, not global null')
 (D/'AUDIT.json').write_text(json.dumps(out,indent=2)+'\n');print({k:v for k,v in out.items() if k!='rows'},flush=True)
if __name__=='__main__':main()
