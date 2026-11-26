"""Phase-aware order-five objective; bounded local interpolation in the weak skew plane."""
import numpy as np,json,sys
from pathlib import Path
from scipy.linalg import schur
from scipy.optimize import minimize_scalar
from jets4 import solve
from run4 import ctrl,run
D=Path(__file__).resolve().parent;P=D.parent/'r118c3n_analytic_s2'
def main():
 M=np.array(json.loads((P/'JOINT.json').read_text())['M']);_,V=schur(M,output='real');base=ctrl('whole');W=np.linalg.norm(base@M@base.T)
 def C(s):
  x=base@V@np.diag(np.exp([s,-s,0.,0.]))@V.T;return x/np.linalg.norm(x)
 # The Taylor response is a homogeneous polynomial of degree k in the
 # control. Before normalization each is a Laurent polynomial in exp(s).
 # Local interpolation of complex coefficients provides a bounded surrogate
 # for the signed objective; directly validate its chosen point.
 xx=np.array([-4.5,-4.25,-4.,-3.75,-3.5]);rows=[];vectors=[]
 for s in xx:
  if s==-4.:z=np.load(D/'best_1024.npz');b=z['B']
  else:
   t,y,q,b=solve(C(s),1024,48,6)
   np.savez_compressed(D/f'squeeze_{abs(s):g}.npz',t=t,S=y,monopole=q,B=b,control=C(s))
  v=b[:,9:16];vectors.append(v);rows.append(dict(s=float(s),wedge=float(np.linalg.norm(C(s)@M@C(s).T)/W),norms=np.linalg.norm(v,axis=1).tolist()))
  print('squeeze',s,rows[-1],flush=True)
 Vv=np.array(vectors);from scipy.interpolate import CubicSpline
 spl=CubicSpline(xx,Vv,axis=0)
 def objective(v,e):
  return max(np.linalg.norm(np.einsum('k,km->m',np.array([(sign*e)**k for k in range(1,6)]),v)) for sign in [-1,1])
 fits={}
 for e in [.0025,.005,.01,.02]:
  opt=minimize_scalar(lambda x:objective(spl(x),e),bounds=(xx[0],xx[-1]),method='bounded',options={'xatol':1e-5})
  fits[str(e)]=dict(s=float(opt.x),predicted=float(opt.fun),sampled_best=float(min(objective(v,e) for v in Vv)),at_original=float(objective(Vv[2],e)))
 ep=.01;opt=fits[str(ep)]['s'];t,y,q,b=solve(C(opt),2048,96,8)
 np.savez_compressed(D/'opt_verified_2048.npz',t=t,S=y,monopole=q,B=b,control=C(opt))
 val=objective(b[:,9:16],ep);fits[str(ep)].update(verified=float(val),relative_prediction=float(abs(val-fits[str(ep)]['predicted'])/val),wedge=float(np.linalg.norm(C(opt)@M@C(opt).T)/W))
 o=dict(rows=rows,fit=fits,scope='bounded local cubic-spline interpolation of complex fifth-order response in one squeeze coordinate; actual 2048 verification at eps .01; no invariant global optimizer')
 (D/'OPT5.json').write_text(json.dumps(o,indent=2)+'\n');print(o,flush=True)
if __name__=='__main__':main()
