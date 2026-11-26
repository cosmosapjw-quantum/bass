"""Scoped C3G controls: leading STF hyperplane and native physical wedge."""
import numpy as np, json, hashlib, sys
from pathlib import Path
from itertools import combinations
from scipy.integrate import solve_ivp
D=Path(__file__).resolve().parent
def basis():
 E=np.zeros((5,3,3));E[0]=np.diag([1,-1,0])/np.sqrt(2);E[1]=np.diag([-1,-1,2])/np.sqrt(6)
 for k,(a,b) in enumerate(((0,1),(0,2),(1,2)),2):E[k,a,b]=E[k,b,a]=1/np.sqrt(2)
 return E
def projector():
 q=json.loads((D.parent/'r118c3c_memory_kernel/WEDGE.json').read_text())
 return 2*np.array(q['gram']),np.array(q['pairs'])
def principal_bound(A,P=None):
 if P is None:P,pairs=projector()
 else:pairs=np.array(list(combinations(range(5),2)))
 A=np.asarray(A,float)
 if A.shape!=(5,4) or not np.all(np.isfinite(A)):raise ValueError('span')
 if P.shape!=(10,10) or not np.allclose(P@P,P,atol=1e-12,rtol=0) or not np.allclose(P,P.T,atol=1e-12,rtol=0) or abs(np.trace(P)-7)>1e-12:raise ValueError('projector')
 Q,s,_=np.linalg.svd(A,full_matrices=True)
 if s[-1]<1e-12*s[0]:raise ValueError('rank')
 W=Q[:,:4];n=Q[:,4];i,j=pairs.T
 B=np.array([W[i,k]*W[j,l]-W[i,l]*W[j,k] for k,l in combinations(range(4),2)]).T
 ev=np.linalg.eigvalsh(np.einsum('i,ijk->jk',n,basis()))
 sig=np.linalg.svd(P@B,compute_uv=False)
 return dict(normal=n.tolist(),normal_eigenvalues=ev.tolist(),sigma_min=float(sig[-1]),singular_values=sig.tolist())
def initial_span(amp,angle,s4,orientation):
 return np.array([[amp*np.cos(angle)/3,0,0,amp*np.sin(orientation)],
 [amp*np.sin(angle)/3,amp,0,0],[0,0,.6*amp,0],[0,0,.8*amp,amp*np.cos(orientation)],[amp*s4,0,0,0]])
def analyze(label,amp,angle,s4,orientation):
 p=D/(label+'.geom');lines=p.read_text().splitlines()
 if not lines[-1].startswith('gauss='):raise ValueError('native output incomplete')
 g=np.genfromtxt(lines[:-1],names=True,delimiter=',');u=g['u'];S=np.stack([g[f'S{i}'] for i in range(5)],axis=1)/amp
 ne=np.genfromtxt(D.parent/'r118c2r_multispecies/rei_q256.csv',names=True,delimiter=',')
 P,pairs=projector();i,j=pairs.T
 A=initial_span(amp,angle,s4,orientation)
 Q,_,_=np.linalg.svd(A,full_matrices=False);proj=Q@Q.T
 def solve(projection):
  def rhs(t,y):
   ss=projection@np.array([np.interp(t,u,S[:,k]) for k in range(5)])
   k=299792458*6.6524587051e-29/2.1842852410855023e-18*np.interp(t,ne['u'],ne['ne_m3'])/np.interp(t,u,g['h'])
   a,b,w=y[:5],y[5:10],y[10:]
   return np.r_[-4*ss-k*(.9*a+.4*b),-k*(.15*a+.4*b),ss[i]*b[j]-ss[j]*b[i]-k*w]
  z=solve_ivp(rhs,(u[0],u[-1]),np.zeros(20),method='DOP853',rtol=1e-10,atol=1e-17,max_step=(u[-1]-u[0])/512)
  if not z.success:raise RuntimeError(z.message)
  return z.y[10:,-1]
 w=solve(np.eye(5));v=solve(proj)
 ratio=lambda z:float(np.linalg.norm(P@z)/np.linalg.norm(z)) if np.linalg.norm(z)>0 else None
 bound=principal_bound(A,P)
 if ratio(v)+1e-11<bound['sigma_min']:raise AssertionError('projection bound violated')
 y=np.genfromtxt(D/(label+'.csv'),names=True,delimiter=',');m=y['ell']==3
 return dict(label=label,amp=amp,angle=angle,s4=s4,orientation=orientation,bound=bound,
    physical_projected_fraction=ratio(w),leading_projected_fraction=ratio(v),
    out_of_span=float(np.linalg.norm(S-S@proj)/np.linalg.norm(S)),
    wedge_norm=float(np.linalg.norm(w)),native_B3=float(np.linalg.norm(y['re'][m]+1j*y['im'][m])),
    gauss=float(lines[-1].split('=')[1]),geometry_sha=hashlib.sha256(p.read_bytes()).hexdigest())
if __name__=='__main__':
 label=sys.argv[1];row=analyze(label,*map(float,sys.argv[2:]))
 (D/(label+'.json')).write_text(json.dumps(row,indent=2)+'\n');print(row,flush=True)
