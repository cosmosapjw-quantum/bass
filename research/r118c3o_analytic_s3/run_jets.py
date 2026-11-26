"""Actual third-order geometry and normalized B4 runs, compare C3N and native."""
import numpy as np,json,sys
from pathlib import Path
from scipy.interpolate import CubicSpline
from jets import solve
D=Path(__file__).resolve().parent;OLD=D.parent/'r118c3n_analytic_s2';CTRL=D.parent/'r118c3l_reachable_sky';NAT=D.parent/'r118c3m_order_resolved'
sys.path.insert(0,str(OLD))
from s2 import combine
def control(name):
 if name=='best':return np.array(json.loads((OLD/'DEEP_SQUEEZE.json').read_text())['best']['control'])
 return np.loadtxt(CTRL/f'{name}_1.ctrl')[3:].reshape(4,5).T/.0025
def run_case(name,nt):
 p=D/f'{name}_{nt}.npz'
 C=control(name)
 if not p.exists():
  t,s,q,b=solve(C,nt,48 if nt==1024 else 96,6 if nt==1024 else 8)
  np.savez_compressed(p,t=t,S=s,monopole=q,B=b)
 else:
  z=np.load(p);t,s,q,b=[z[k] for k in ['t','S','monopole','B']]
 old=np.load(OLD/'COEFF_768.npz');a,v=combine(C,old['first'],old['second'])
 v1=CubicSpline(old['u'],a[0],axis=-1)(t).T;v2=CubicSpline(old['u'],v[0],axis=-1)(t).T
 norm=lambda x:np.sqrt(np.trapezoid(np.sum(abs(x)**2,axis=1),t))
 out=dict(case=name,steps=nt,S1_rel=float(norm(s[:,0]-v1)/norm(v1)),S2_rel=float(norm(s[:,1]-v2)/norm(v2)),S3_norm=float(norm(s[:,2])),B3_norms=np.linalg.norm(b[:,9:16],axis=1).tolist(),B5_norms=np.linalg.norm(b[:,25:36],axis=1).tolist(),monopole2=float(q[-1,1]/np.sqrt(4*np.pi)))
 if name in ['generic','whole','best']:
  # S3 via odd response at two amplitudes: cancel linear native discretization.
  if name=='best':
   def data(ep,sign):return np.genfromtxt((OLD/f'native_best_{ep:g}_{sign}.geom').read_text().splitlines()[:-1],names=True,delimiter=',')
   eps=[.02,.01]
  else:
   def data(ep,sign):
    p=NAT/f'{name}_4096_{ep:g}_{sign}.geom'
    return np.genfromtxt(p.read_text().splitlines()[:-1],names=True,delimiter=',')
   eps=[.01,.005]
  try:
   def odd(ep):
    a,b=[data(ep,i) for i in [1,-1]];return a['u'],np.stack([(a[f'S{i}']-b[f'S{i}'])/(2*ep) for i in range(5)],axis=1)
   u,a=odd(eps[0]);v,b=odd(eps[1]);assert np.array_equal(u,v)
   S3=(a-b)/(eps[0]**2-eps[1]**2)
   s3=CubicSpline(t,s[:,2],axis=0)(u)
   norm3=lambda x:np.sqrt(np.trapezoid(np.sum(abs(x)**2,axis=1),u))
   out['native_S3_rel']=float(norm3(s3-S3)/norm3(S3));out['native_S3_norm']=float(norm3(S3))
  except FileNotFoundError as e:out['native_S3_compare_missing']=str(e)
 print(out,flush=True);return out
if __name__=='__main__':
 name=sys.argv[1];nt=int(sys.argv[2]);out=run_case(name,nt)
 (D/f'{name}_{nt}.json').write_text(json.dumps(out,indent=2)+'\n')
