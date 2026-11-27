"""Near-fixed wedge comparison, independent fine verification."""
import numpy as np,json,sys
from pathlib import Path
from scipy.optimize import minimize
from concurrent.futures import ProcessPoolExecutor
from controls import control,check
from multi import run,objective,job
D=Path(__file__).resolve().parent
base=np.load(D/'base_1024.npz')['B'][:,9:16];h=.15
v=np.array([[np.load(D/f'd{i}_{s}.npz')['B'][:,9:16] for s in [-1,1]] for i in range(6)])
J=(v[:,1]-v[:,0])/(2*h);H=(v[:,1]+v[:,0]-2*base)/(h*h)
def pred(t):return base+np.einsum('i,ikm->km',t,J)+.5*np.einsum('i,ikm->km',t*t,H)
def con(t):return [check(control(t))['wedge_ratio']-.99,.35**2-t@t]
def obj(t,mode):
 a=pred(t)
 return objective(a)/objective(base) if mode=='signed' else np.linalg.norm(a[3])/np.linalg.norm(base[3])
def main():
 fits={};jobs=[]
 for mode in ['signed','quartic']:
  p=minimize(lambda t:obj(t,mode),np.zeros(6),method='SLSQP',bounds=[(-.25,.25)]*6,constraints=[{'type':'ineq','fun':con}],options={'ftol':1e-11,'maxiter':200})
  t=p.x
  if min(con(t))< -1e-8:t*=.99
  assert min(con(t))>=-1e-8
  fits[mode]=dict(t=t.tolist(),optimizer_success=bool(p.success),predicted=float(obj(t,mode)),**check(control(t)))
  jobs.append((t,2048,'near_'+mode))
 q=json.loads((D/'MULTI.json').read_text());jobs.append((np.array(q['fits']['signed']['t']),4096,'opt_signed_fine'))
 with ProcessPoolExecutor(max_workers=3) as pool:r=list(pool.map(job,jobs))
 ref=np.load(D.parent/'r118c3p_analytic_s4/opt_verified_2048.npz')['B'][:,9:16]
 for name,a in zip(fits,r):
  f=fits[name];w=f['wedge_ratio'];ratio=float(np.linalg.norm(a[3])/np.linalg.norm(ref[3]))
  f.update(B4_ratio=ratio,B4_over_wedge2=ratio/w**2,objective_ratio=float(objective(a)/objective(ref)),B2=float(np.linalg.norm(a[1])),B3=float(np.linalg.norm(a[2])))
 old=np.load(D/'opt_signed.npz')['B'][:,9:16];fine=r[-1]
 out=dict(fits=fits,original_wedge_normalized={k:a['quartic_ratio']/a['wedge_ratio']**2 for k,a in q['fits'].items()},fine_signed=dict(objective=float(objective(fine)),coefficient_relative=[float(np.linalg.norm(fine[k]-old[k])/max(np.linalg.norm(fine[k]),1e-300)) for k in [2,3,4]]),scope='same bounded six-coordinate family, wedge>=.99; quartic/wedge² separates amplitude suppression, not exact invariants or global optimizer')
 (D/'NEAR_FIXED.json').write_text(json.dumps(out,indent=2)+'\n');print(out,flush=True)
if __name__=='__main__':main()
