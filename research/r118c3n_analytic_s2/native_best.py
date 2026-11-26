"""Native check of selected physically norm-constrained squeeze using same C3M owner."""
import json,numpy as np,subprocess,concurrent.futures as cf
from pathlib import Path
from scipy.interpolate import CubicSpline
from s2 import combine
from joint import load
D=Path(__file__).resolve().parent;ROOT=D.parents[1];OLD=D.parent/'r118c3m_order_resolved';CLOCK=D.parent/'r118c3l_reachable_sky/clock.csv';BIN=ROOT/'_rustcore/target/release/examples'
def run():
 C=np.array(json.loads((D/'DEEP_SQUEEZE.json').read_text())['best']['control']);assert abs(np.linalg.norm(C)-1)<1e-14
 def job(t):
  ep,s=t;lab=f'native_best_{ep:g}_{s}';a=np.r_[[.001,.006,.05],(ep*s*C.T).ravel()];p=D/(lab+'.ctrl');np.savetxt(p,a[None,:],fmt='%.17e')
  with (D/(lab+'.csv')).open('w') as o,(D/(lab+'.geom')).open('w') as e:r=subprocess.run([str(BIN/'r118c3m_shear'),str(CLOCK),str(p),'8192','7'],stdout=o,stderr=e)
  print(lab,r.returncode,flush=True);return r.returncode
 with cf.ThreadPoolExecutor(max_workers=2) as p:r=list(p.map(job,[(ep,s) for ep in [.02,.01] for s in [-1,1]]))
 assert not any(r)
 def geom(p):
  l=p.read_text().splitlines();assert l[-1].startswith('min_screen=')
  return np.genfromtxt(l[:-1],names=True,delimiter=',')
 zero=geom(OLD/'zero_8192_0.01_0.geom');u,h,f,s=load(768);a,b=combine(C,f,s);rows={}
 for ep in [.02,.01]:
  p,q=[geom(D/f'native_best_{ep:g}_{s}.geom') for s in [1,-1]];t=p['u'];assert np.array_equal(t,q['u']) and np.array_equal(t,zero['u'])
  S=lambda z:np.stack([z[f'S{i}'] for i in range(5)],axis=0)
  s1=(S(p)-S(q))/(2*ep);s2=(S(p)+S(q)-2*S(zero))/(2*ep*ep)
  v=CubicSpline(u,a[0],axis=-1)(t);w=CubicSpline(u,b[0],axis=-1)(t);norm=lambda z:np.sqrt(np.trapezoid(np.sum(z*z,axis=0),t))
  zz=[]
  for sign in [1,-1]:
   z=np.genfromtxt(D/f'native_best_{ep:g}_{sign}.csv',names=True,delimiter=',');m=(z['epoch']==1)&(z['ell']==3);zz.append(z['Bre'][m]+1j*z['Bim'][m])
  rows[str(ep)]=dict(S1_error=float(norm(s1-v)/norm(v)),S2_error=float(norm(s2-w)/norm(w)),native_even=float(np.linalg.norm(zz[0]+zz[1])/(2*ep**2)),native_odd=float(np.linalg.norm(zz[0]-zz[1])/(2*ep**3)),max_gauss=float(max(np.max(abs(p['gauss'])),np.max(abs(q['gauss'])))))
 o=dict(rows=rows,scope='actual native signed squeeze cases, finite amplitude; small cubic signal near cancellation floor, analytic coefficient is not exact nonlinear null')
 (D/'NATIVE_BEST.json').write_text(json.dumps(o,indent=2)+'\n');print(o)
if __name__=='__main__':run()
