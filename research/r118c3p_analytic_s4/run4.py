"""Order4 geometry and order5 magnetic jets; native even S4 and previous jet comparison."""
import json,numpy as np,sys
from pathlib import Path
from scipy.interpolate import CubicSpline
from jets4 import solve
D=Path(__file__).resolve().parent;P=D.parent/'r118c3o_analytic_s3';Q=D.parent/'r118c3n_analytic_s2';C3M=D.parent/'r118c3m_order_resolved';C3L=D.parent/'r118c3l_reachable_sky'
def ctrl(k):
 if k=='best':return np.array(json.loads((Q/'DEEP_SQUEEZE.json').read_text())['best']['control'])
 return np.loadtxt(C3L/f'{k}_1.ctrl')[3:].reshape(4,5).T/.0025
def run(k,nt,C=None):
 C=ctrl(k) if C is None else C
 t,s,q,b=solve(C,nt,48 if nt<=1024 else 96,6 if nt<=1024 else 8)
 np.savez_compressed(D/f'{k}_{nt}.npz',t=t,S=s,monopole=q,B=b,control=C)
 o=dict(k=k,nt=nt,B3=np.linalg.norm(b[:,9:16],axis=1).tolist(),B5=np.linalg.norm(b[:,25:36],axis=1).tolist(),S4_norm=float(np.sqrt(np.trapezoid(np.sum(s[:,3]**2,axis=1),t))))
 pp=P/f'{k}_2048.npz'
 if pp.exists():
  z=np.load(pp);v=CubicSpline(z['t'],z['S'],axis=0)(t);norm=lambda x:np.sqrt(np.trapezoid(np.sum(x*x,axis=2),t,axis=0))
  o['old_S123_rel']=(norm(s[:,:3]-v)/norm(v)).tolist()
  o['old_B4_rel']=float(np.linalg.norm(b[3,9:16]-z['B'][3,9:16])/np.linalg.norm(b[3,9:16]))
  if k=='best':dir=Q;prefix='native_best';e1,e2=.02,.01;zero=C3M/'zero_8192_0.01_0.geom'
  else:dir=C3M;prefix=f'{k}_4096';e1,e2=.01,.005;zero=C3M/'zero_4096_0.01_0.geom'
  def load(p):return np.genfromtxt(p.read_text().splitlines()[:-1],names=True,delimiter=',')
  def ss(p):return np.stack([p[f'S{i}'] for i in range(5)],axis=1)
  try:
   z=load(zero)
   def even(e):
    a,b=[load(dir/f'{prefix}_{e:g}_{sg}.geom') for sg in [-1,1]]
    assert np.array_equal(a['u'],b['u']) and np.array_equal(a['u'],z['u'])
    return (ss(a)+ss(b)-2*ss(z))/(2*e**2)
   g=(even(e1)-even(e2))/(e1*e1-e2*e2);v=CubicSpline(t,s[:,3],axis=0)(z['u'])
   norm=lambda x:np.sqrt(np.trapezoid(np.sum(x*x,axis=1),z['u']))
   o['native_S4_rel']=float(norm(v-g)/norm(g));o['native_S4_norm']=float(norm(g))
  except FileNotFoundError as e:o['native_missing']=str(e)
 (D/f'{k}_{nt}.json').write_text(json.dumps(o,indent=2)+'\n');print(o,flush=True);return o
if __name__=='__main__':run(sys.argv[1],int(sys.argv[2]))
