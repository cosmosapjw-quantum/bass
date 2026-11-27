"""Rank-one temporal-null family: fit phase-aware high-order response, validate actual fine jets."""
import sys,json,numpy as np
from pathlib import Path
from scipy.optimize import minimize
from concurrent.futures import ProcessPoolExecutor
D=Path(__file__).resolve().parent;P=D.parent/'r118c3s_radial_envelope'
sys.path.insert(0,str(P));from radial_jets import solve,window
z=np.load(D/'FAMILY.npz');A,M,G,H,dirs,W=[z[k] for k in ['A','M','G','H','dirs','W']];B=float(np.sum(A*A))
def ctrl(t):
 x=A+np.einsum('i,ijk->jk',t,dirs);x*=np.sqrt(B)/np.linalg.norm(x);w=x@M@x.T
 assert np.linalg.norm(w)/np.linalg.norm(W)>.9-1e-12
 target=W*B/np.sum((A+np.einsum('i,ijk->jk',t,dirs))**2)
 assert np.linalg.norm(w-target)/np.linalg.norm(W)<1e-5
 return x@H
def objective(b,ep=.01,skip2=False):
 p=np.arange(1,6);c=np.array([ep**k for k in p]);v=b.copy()
 if skip2:v[1]=0
 return float(max(np.linalg.norm((sg**p*c)@v) for sg in [-1,1]))
def run(job):
 name,t,nt,nr=job;C=ctrl(t);u,s,q,b=solve(C,nt,nr,6 if nt<=1024 else 8)
 np.savez_compressed(D/f'{name}.npz',t=u,S=s,monopole=q,B=b,control=C,param=t)
 v=b[:,9:16];peak=max(np.linalg.norm(C[:,1+2*s:3+2*s]@np.array([window(np.linspace(0,60,400)),1-window(np.linspace(0,60,400))]),axis=0).max() for s in range(3))
 print(name,'norm',np.linalg.norm(v,axis=1).tolist(),'obj',objective(v),flush=True)
 return v
def main():
 h=.12;ts=np.eye(6)*h
 jobs=[('base_1024',np.zeros(6),1024,192)]+[(f'axis{i}_{s}',s*ts[i],1024,192) for i in range(6) for s in [-1,1]]
 with ProcessPoolExecutor(max_workers=3) as p:res=list(p.map(run,jobs))
 base=res[0];v=np.array(res[1:]).reshape(6,2,5,7);J=(v[:,1]-v[:,0])/(2*h);Q=(v[:,1]+v[:,0]-2*base)/(h*h)
 pred=lambda t:base+np.einsum('i,ikm->km',t,J)+.5*np.einsum('i,ikm->km',t*t,Q)
 # optimize only within one v-null direction (two output vectors)
 # ignore B2 in surrogate since numerical low-order cancellation floor
 # is sensitive to the integration grid; actual admission checks full B2.
 fits=[]
 for k in range(3):
  def param(s):
   t=np.zeros(6);t[2*k:2*k+2]=s;return t
  ans=minimize(lambda s:objective(pred(param(s)),skip2=True)/objective(base,skip2=True),[0.,0.],method='SLSQP',bounds=[(-.18,.18)]*2,constraints=[dict(type='ineq',fun=lambda s:.18**2-s@s)],options={'maxiter':150,'ftol':1e-10})
  t=param(ans.x);assert np.linalg.norm(t)<=.180001
  fits.append(dict(family=k,t=t.tolist(),predicted=objective(pred(t),skip2=True),opt_success=bool(ans.success)))
 # verify each fitted point on same 2048 mesh and independent baseline.
 with ProcessPoolExecutor(max_workers=3) as p:vals=list(p.map(run,[('base_2048',np.zeros(6),2048,192)]+[(f'fit{k}_2048',np.array(f['t']),2048,192) for k,f in enumerate(fits)]))
 b0=vals[0]
 for f,x in zip(fits,vals[1:]):
  f.update(actual=objective(x),actual_high=objective(x,skip2=True),ratio=objective(x)/objective(b0),B3_norms=np.linalg.norm(x,axis=1).tolist())
 best=min(range(3),key=lambda k:fits[k]['actual'])
 t=np.array(fits[best]['t'])
 with ProcessPoolExecutor(max_workers=2) as p:fine=list(p.map(run,[('base_4096',np.zeros(6),4096,192),('best_4096',t,4096,192)]))
 cf=ctrl(t);af=cf@np.linalg.inv(H);wf=af@M@af.T
 rel=[float(np.linalg.norm(fine[1][k]-vals[best+1][k])/max(np.linalg.norm(fine[1][k]),1e-300)) for k in range(2,5)]
 out=dict(fits=fits,best=best,coarse_base=objective(base),fine_base=objective(fine[0]),fine_best=objective(fine[1]),fine_ratio=objective(fine[1])/objective(fine[0]),fine_high_ratio=objective(fine[1],skip2=True)/objective(fine[0],skip2=True),fine_B3=np.linalg.norm(fine[1],axis=1).tolist(),fine_base_B3=np.linalg.norm(fine[0],axis=1).tolist(),fine_coeff_relative=rel,wedge_ratio=float(np.linalg.norm(wf)/np.linalg.norm(W)),metric=float(np.trace(cf@G@cf.T)),scope='three separate bounded rank-one radial families, diagonal quadratic surrogate, actual fine verification at 192 radial; not global optimum or certified null')
 (D/'OPT.json').write_text(json.dumps(out,indent=2)+'\n');print(out,flush=True)
if __name__=='__main__':main()
