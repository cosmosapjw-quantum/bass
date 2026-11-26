"""Compare analytic coefficients with native signed histories and bounded joint-null scan."""
import numpy as np,json,sys,subprocess
from pathlib import Path
from scipy.interpolate import CubicSpline
from scipy.linalg import schur
import concurrent.futures as cf
D=Path(__file__).resolve().parent;ROOT=D.parents[1];OLD=D.parent/'r118c3m_order_resolved';CTRL=D.parent/'r118c3l_reachable_sky'
from s2 import combine
BIN=ROOT/'_rustcore/target/release/examples/r118c3m_orders'
def control(k):return np.loadtxt(CTRL/f'{k}_1.ctrl')[3:].reshape(4,5).T/.0025
def interp(u,v,t):
 return CubicSpline(u,v,axis=-1)(t)
def load(n):
 z=np.load(D/f'COEFF_{n}.npz');return z['u'],z['h'],z['first'],z['second']
def measured(k,n,eps):
 p=OLD/f'{k}_{n}_{eps:g}_orders_input.csv';g=np.genfromtxt(p,names=True,delimiter=',')
 return g['u'],np.stack([g[f'S1{i}'] for i in range(5)]),np.stack([g[f'S2{i}'] for i in range(5)])
def compare():
 rows={}
 u,h,f,s=load(768)
 for k in ['generic','whole']:
  a,b=combine(control(k),f,s)
  for n in [4096,8192]:
   t,v,w=measured(k,n,.01);x=interp(u,a[0],t);y=interp(u,b[0],t)
   norm=lambda z:np.sqrt(np.trapezoid(np.sum(z*z,axis=0),t))
   rows[f'{k}_{n}']=dict(S1_rel=float(norm(x-v)/norm(v)),S2_rel=float(norm(y-w)/norm(w)),S2_max=float(np.max(abs(y-w))),S2_norm=float(norm(y)),native_S2_norm=float(norm(w)))
 (D/'S2_COMPARE.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows,flush=True)
def run_case(k,C,n,steps):
 u,h,f,s=load(n);a,b=combine(C,f,s)
 inp=D/f'{k}_{n}_input.csv';np.savetxt(inp,np.c_[u,h,a[0].T,b[0].T],delimiter=',',header='u,h,S10,S11,S12,S13,S14,S20,S21,S22,S23,S24',comments='',fmt='%.17e')
 p=D/f'{k}_{n}_B.csv'
 with p.open('w') as f:proc=subprocess.run([str(BIN),str(inp),str(CTRL/'clock.csv'),str(steps)],stdout=f)
 if proc.returncode:raise RuntimeError('order solver')
 z=np.genfromtxt(p,names=True,delimiter=',')
 get=lambda j,l:z['re'][(z['order']==j)&(z['ell']==l)]+1j*z['im'][(z['order']==j)&(z['ell']==l)]
 b2=get(2,3);b3=get(3,3)+get(5,3);b5=get(3,5)+get(5,5)
 return dict(label=k,n=n,steps=steps,norm=float(np.linalg.norm(C)),B2=float(np.linalg.norm(b2)),B3=float(np.linalg.norm(b3)),B5=float(np.linalg.norm(b5)),control=C.tolist())
def scan():
 M=np.array(json.loads((CTRL/'R7.json').read_text())[-1]['whole']['M']) if 'M' in json.loads((CTRL/'R7.json').read_text())[-1]['whole'] else None
 # C3L diag omits M; recover skew of first-order S,P histories directly on analytic clock.
 u,h,f,s=load(768);from scipy.integrate import cumulative_trapezoid, trapezoid
 from s2 import EARLY,CLOCK,K0
 e=np.genfromtxt(EARLY,names=True,delimiter=',');l=np.genfromtxt(CLOCK,names=True,delimiter=',');cut=e['u'][-1]
 ne=np.where(u<=cut,np.interp(u,e['u'],e['ne_m3']),np.interp(u-cut,l['u'],l['ne_m3']))
 tau=cumulative_trapezoid(K0*ne/h,u,initial=0)
 S,P=f[0],f[3];M=trapezoid((S[:,None,:]*P[None,:,:]-P[:,None,:]*S[None,:,:])*np.exp(tau-tau[-1]),u,axis=-1)
 # Use higher-accuracy integrated M by directly solving linear-memory ODE on cubic spline.
 from scipy.integrate import solve_ivp
 splS=CubicSpline(u,S,axis=-1);splP=CubicSpline(u,P,axis=-1);splK=CubicSpline(u,K0*ne/h)
 def rhs(t,z):
  a,b=splS(t),splP(t);return (np.outer(a,b)-np.outer(b,a)).ravel()-splK(t)*z
 v=solve_ivp(rhs,(u[0],u[-1]),np.zeros(16),method='DOP853',rtol=3e-12,atol=1e-19,max_step=.002);assert v.success
 M=v.y[:,-1].reshape(4,4);M=(M-M.T)/2
 U,V=schur(M,output='real');base=control('whole')
 def rot(t,p):
  def R(t):return np.array([[np.cos(t),-np.sin(t)],[np.sin(t),np.cos(t)]])
  O=np.zeros((4,4));O[:2,:2]=R(t);O[2:,2:]=R(p)
  Q=V@O@V.T;assert np.linalg.norm(Q@M@Q.T-M)<1e-14
  return base@Q
 cases=[('generic',control('generic')),('whole',base)]+[(f'r{i}{j}',rot(i*np.pi/4,j*np.pi/4)) for i,j in [(0,1),(1,0),(1,1),(2,1),(1,2),(2,2)]]
 with cf.ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(lambda p:run_case(*p,768,8192),cases))
 g=rows[0];for_score=lambda r:max(r['B2']/g['B2'],r['B3']/g['B3'])
 for r in rows:r['score']=for_score(r)
 best=min(rows[1:],key=for_score);print('best',best,flush=True)
 extra=[run_case(k,np.array(r['control']),384,8192) for k,r in [('whole',rows[1]),('best',best)]]
 # keep output of best fine mesh without overwriting base
 extra.append(run_case('best_fine',np.array(best['control']),768,16384))
 (D/'JOINT.json').write_text(json.dumps(dict(rows=rows,refinement=extra,best=best['label'],M=M.tolist(),scope='finite congruence rotation scan; approximate M from interpolated coefficients, fixed Frobenius norm; not global minimization or proof of null'),indent=2)+'\n')
 print([(r['label'],r['B2'],r['B3'],r['score']) for r in rows])
if __name__=='__main__':compare();scan()
