"""Independent direct radial FD quadrature and saved high-order coefficient audit."""
import numpy as np,json
from pathlib import Path
from numpy.polynomial.legendre import leggauss
from radial_jets import Moments,table,mat,window,MASS,T0
D=Path(__file__).resolve().parent
def stress():
 rng=np.random.default_rng(321);C=rng.normal(size=(5,7))*.2;ms=Moments(C,12);y,w=leggauss(192);y=30*(1+y);w=30*w;V=window(y)
 J=np.stack([np.einsum('ni,ij,nj->n',ms.n,mat(C[:,j]),ms.n) for j in range(1,7)]).reshape(3,2,-1)
 p0=J[:,1,:,None]+(J[:,0]-J[:,1])[:,:,None]*V
 Ds=np.array([np.eye(3),mat(rng.normal(size=5)*.2),*[rng.normal(size=(3,3))*.1 for _ in range(3)]])
 rows=[]
 for a in [.000625,.02,.2]:
  rr,pp=ms.eval(Ds,table(a,y,w))
  def exact(eps):
   F=np.einsum('k,kij->ij',np.array([eps**k for k in range(5)]),Ds);v=ms.n@F.T
   f=1/(1+np.exp(y*np.exp(-eps*p0)));E=np.hypot(np.linalg.norm(v,axis=1)[None,:,None]*y,a*MASS[:,None,None]/T0)
   assert f.min()>=0 and f.max()<=1
   rho=np.sum((f*E)@(w*y*y)@ms.w);P=sum((v.T*(ms.w*((f[i]/E[i])@(w*y**4))))@v for i in range(3));return rho,P
  r,p=exact(0)
  for ep in [.02,.01,.005]:
   a0,b0=exact(ep);a1,b1=exact(-ep);z=((b0+b1-2*p)/(2*ep*ep)-pp[2])/ep**2
   rows.append(dict(a=a,eps=ep,pressure_rel=float(np.linalg.norm(z-pp[4])/np.linalg.norm(pp[4]))))
 assert max(v['pressure_rel'] for v in rows if v['eps']==.005)<3e-4
 return rows
def run():
 a=json.loads((D/'R7.json').read_text());f=json.loads((D/'RADIAL_FINE.json').read_text());j=json.loads((D/'RADIAL_JETS.json').read_text())
 z,y=[np.load(D/f'radial2_nr192_{n}.npz') for n in [2048,4096]]
 b=z['B'][:,9:16];c=y['B'][:,9:16];rel=[float(np.linalg.norm(b[k]-c[k])/np.linalg.norm(c[k])) for k in [2,3,4]]
 obj=lambda x:float(max(np.linalg.norm(np.array([(s*.01)**k for k in range(1,6)])@x) for s in [-1,1]))
 assert max(rel)<1e-5 and max(j['embedded_reproduction'])<1e-8
 G=np.array(f['G']);C=y['control'];assert abs(np.trace(C@G@C.T)-f['budget'])<1e-10
 v=json.loads((D/'PURE_BAND.json').read_text());leak=max(r['holdout_leak'] for r in v['rows'].values());assert leak<1e-6
 o=dict(direct_fd_stress=stress(),fine_coeff_relative=rel,fine_B3=np.linalg.norm(c,axis=1).tolist(),fine_objective=obj(c),objective_ratio_to_embedded=obj(c)/j['rows'][1]['objective'],metric_budget=float(np.trace(C@G@C.T)),max_holdout_leak=leak,scope='independent direct FD quadrature and saved-array audit; same physical metric, W changes; no native radial promotion')
 (D/'AUDIT.json').write_text(json.dumps(o,indent=2)+'\n');print(o,flush=True)
if __name__=='__main__':run()
