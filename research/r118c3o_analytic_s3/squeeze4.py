"""Weak-plane squeeze refinement using B2..B4 and two explicit amplitude metrics."""
import numpy as np,json,sys
from scipy.linalg import schur
from pathlib import Path
from jets import solve
D=Path(__file__).resolve().parent;P=D.parent/'r118c3n_analytic_s2';L=D.parent/'r118c3l_reachable_sky'
def run():
 M=np.array(json.loads((P/'JOINT.json').read_text())['M']);base=np.loadtxt(L/'whole_1.ctrl')[3:].reshape(4,5).T/.0025
 _,V=schur(M,output='real');ref=np.linalg.norm(base@M@base.T)
 z=np.load(D/'whole_2048.npz');sn=np.sqrt(np.trapezoid(np.sum(z['S'][:,0]**2,axis=1),z['t']))
 rows=[]
 for d in [3.25,3.5,3.75,4.25,4.5]:
  C=base@V@np.diag(np.exp([-d,d,0.,0.]))@V.T;C/=np.linalg.norm(C);wedge=np.linalg.norm(C@M@C.T)/ref
  t,s,q,b=solve(C,1024,48,6);v=b[:,9:16];scale=sn/np.sqrt(np.trapezoid(np.sum(s[:,0]**2,axis=1),t))
  vals={}
  for name,f in [('frobenius',1.),('integrated_shear',scale)]:
   vals[name]={str(e):float(max(np.linalg.norm(sum((sg*e*f)**(j+1)*v[j] for j in range(4))) for sg in [-1,1])) for e in [.0025,.005,.01,.02]}
  rows.append(dict(s=-d,control=C.tolist(),wedge_ratio=float(wedge),shear_rescale=float(scale),coeff_norms=np.linalg.norm(v,axis=1).tolist(),max_signed_B3=vals))
  print(d,wedge,scale,rows[-1]['coeff_norms'],flush=True)
 for k in ['whole','best']:
  z=np.load(D/f'{k}_2048.npz');v=z['B'][:,9:16];t=z['t'];s=z['S'];scale=sn/np.sqrt(np.trapezoid(np.sum(s[:,0]**2,axis=1),t));vals={}
  for name,f in [('frobenius',1.),('integrated_shear',scale)]:
   vals[name]={str(e):float(max(np.linalg.norm(sum((sg*e*f)**(j+1)*v[j] for j in range(4))) for sg in [-1,1])) for e in [.0025,.005,.01,.02]}
  rows.append(dict(case=k,s=0 if k=='whole' else -4.,shear_rescale=float(scale),coeff_norms=np.linalg.norm(v,axis=1).tolist(),max_signed_B3=vals))
 best={metric:{str(e):min(rows,key=lambda r:r['max_signed_B3'][metric][str(e)])['s'] for e in [.0025,.005,.01,.02]} for metric in ['frobenius','integrated_shear']}
 o=dict(rows=rows,best_s=best,scope='bounded squeeze scan and truncated B2+B3+B4 signed maximum at fixed initial norm or fixed integrated linear shear; no S4 owner or higher-order null')
 (D/'SQUEEZE4.json').write_text(json.dumps(o,indent=2)+'\n');print(best)
if __name__=='__main__':run()
