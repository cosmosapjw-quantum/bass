"""Direct multiaxis Taylor coefficients and constrained surrogate verification."""
import sys,json,numpy as np
from pathlib import Path
from scipy.optimize import minimize
from concurrent.futures import ProcessPoolExecutor
D=Path(__file__).resolve().parent;P=D.parent/'r118c3p_analytic_s4'
sys.path.insert(0,str(P))
from jets4 import solve
from controls import C0,control,check
# Import solve from the prior module; output folder is current D.
def run(t,nt,label):
 C=control(t);q=check(C)
 assert q['wedge_ratio']>=.8 and q['wedge_direction_error']<1e-5,q
 u,s,m,b=solve(C,nt,48 if nt<=1024 else 96,6 if nt<=1024 else 8)
 np.savez_compressed(D/f'{label}.npz',t=u,S=s,monopole=m,B=b,control=C,param=t)
 print(label,q,np.linalg.norm(b[:,9:16],axis=1).tolist(),flush=True)
 return b[:,9:16]
def job(z):return run(*z)
def objective(v,e=.01):
 return max(np.linalg.norm(np.array([(sg*e)**k for k in range(1,6)])@v) for sg in [-1,1])
def main():
 ref=np.load(P/'opt_verified_2048.npz')['B'][:,9:16]
 h=.15;ts=[(s*h*np.eye(6)[i],1024,f'd{i}_{s}') for i in range(6) for s in [-1,1]]
 # Run baseline on identical coarse discretization to cancel grid error.
 base=run(np.zeros(6),1024,'base_1024')
 with ProcessPoolExecutor(max_workers=3) as p:v=np.array(list(p.map(job,ts))).reshape(6,2,5,7)
 J=(v[:,1]-v[:,0])/(2*h);H=(v[:,1]+v[:,0]-2*base)/(h*h)
 def pred(t):return base+np.einsum('i,ikm->km',t,J)+.5*np.einsum('i,ikm->km',t*t,H)
 # Keep original wedge within 80%, impose bounded total control distance.
 def cons(t):return np.array([check(control(t))['wedge_ratio']-.8,.35**2-t@t])
 baseline=objective(base);q4=np.linalg.norm(base[3])
 def obj(t,mode):
  p=pred(t)
  return objective(p)/baseline if mode=='signed' else np.linalg.norm(p[3])/q4+.02*np.linalg.norm(p[2])/max(np.linalg.norm(base[2]),1e-300)
 fits={};z=[]
 for mode in ['signed','quartic']:
  opt=minimize(lambda t:obj(t,mode),np.zeros(6),method='SLSQP',bounds=[(-.25,.25)]*6,constraints=[{'type':'ineq','fun':cons}],options={'ftol':1e-11,'maxiter':200})
  t=opt.x;q=check(control(t))
  if min(cons(t))< -1e-7:t*=.99
  fits[mode]=dict(t=t.tolist(),predicted=float(obj(t,mode)),predicted_B4=float(np.linalg.norm(pred(t)[3])),opt_success=bool(opt.success),**check(control(t)))
  z.append((t,2048,'opt_'+mode))
 with ProcessPoolExecutor(max_workers=2) as p:actual=list(p.map(job,z))
 for k,a in zip(fits,actual):fits[k].update(actual_objective=float(objective(a)),relative_to_C3P=float(objective(a)/objective(ref)),actual_B4=float(np.linalg.norm(a[3])),quartic_ratio=float(np.linalg.norm(a[3])/np.linalg.norm(ref[3])),B2=float(np.linalg.norm(a[1])),B3=float(np.linalg.norm(a[2])))
 def sv(A):
  return np.linalg.svd(np.c_[A.real,A.imag],compute_uv=False).tolist()
 out=dict(reference_B4=float(np.linalg.norm(ref[3])),reference_objective=float(objective(ref)),coarse_objective=float(baseline),derivative_singular_B4=sv(J[:,3]),derivative_singular_B3=sv(J[:,2]),axis_B4=np.linalg.norm(v[:,:,3],axis=-1).tolist(),fits=fits,scope='bounded six-coordinate SL2 stabilizer, diagonal quadratic surrogate only; actual verification, no global optimum or exact rank')
 (D/'MULTI.json').write_text(json.dumps(out,indent=2)+'\n');print(out,flush=True)
if __name__=='__main__':main()
