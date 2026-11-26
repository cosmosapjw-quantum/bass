"""C3H STF exact gap law and temporal congruence candidate."""
from pathlib import Path
import sys,json,hashlib,numpy as np
from itertools import combinations
from scipy.linalg import schur
from scipy.integrate import solve_ivp
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'r118c3g_memory_controls'))
from memory_controls import basis,projector,principal_bound,initial_span
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def gap_spectrum(n):
 n=np.asarray(n,float);n=n/np.linalg.norm(n);e=np.linalg.eigvalsh(np.einsum('i,ijk->jk',n,basis()))
 return np.sort(np.r_[np.ones(3),np.sqrt(2/5)*np.array([e[1]-e[0],e[2]-e[0],e[2]-e[1]])])
def skew(v,n):
 a=np.zeros((n,n));i,j=np.array(list(combinations(range(n),2))).T;a[i,j]=v;a[j,i]=-v;return a
def vector(a):
 i,j=np.array(list(combinations(range(len(a)),2))).T;return a[i,j]
def memory(u,S,h,clock,max_steps=1024):
 S=np.asarray(S);n=S.shape[1];i,j=np.array(list(combinations(range(n),2))).T
 def rhs(t,y):
  s=np.array([np.interp(t,u,S[:,k]) for k in range(n)])
  K=299792458*6.6524587051e-29/2.1842852410855023e-18*np.interp(t,clock['u'],clock['ne_m3'])/np.interp(t,u,h)
  a,p,w=y[:n],y[n:2*n],y[2*n:]
  return np.r_[-4*s-K*(.9*a+.4*p),-K*(.15*a+.4*p),s[i]*p[j]-s[j]*p[i]-K*w]
 sol=solve_ivp(rhs,(u[0],u[-1]),np.zeros(2*n+len(i)),method='DOP853',rtol=2e-11,atol=2e-18,max_step=(u[-1]-u[0])/max_steps)
 if not sol.success:raise RuntimeError(sol.message)
 return skew(sol.y[2*n:,-1],n)
def construct(M,Q):
 # Q is orthonormal 5x4 axial hyperplane basis. Find target skew spin1 via null of P3 on wedge^2 W.
 P,_=projector();i,j=np.array(list(combinations(range(5),2))).T
 B=np.array([Q[i,k]*Q[j,l]-Q[i,l]*Q[j,k] for k,l in combinations(range(4),2)]).T
 _,s,V=np.linalg.svd(P@B,full_matrices=False);assert s[-1]<1e-10
 target=skew(V[-1],4)
 def blocks(K):
  T,U=schur(K,output='real');assert abs(T[0,1])>0 and abs(T[2,3])>0
  return U,np.array([T[0,1],T[2,3]])
 U,m=blocks(M);V,t=blocks(target)
 # Sign and magnitude handled by first diagonal coordinate in each block.
 a=np.sqrt(abs(t/m));L=np.diag(np.ravel(np.c_[a*np.sign(t/m),a]))
 A=Q@V@L@U.T
 # Norm 1 for largest control column; common scale preserves direction.
 A/=max(np.linalg.norm(A,axis=0))
 W=A@M@A.T
 return A,W,dict(mode_singular_values=np.linalg.svd(M,compute_uv=False).tolist(),condition=float(np.linalg.cond(M)),control_singular_values=np.linalg.svd(A,compute_uv=False).tolist(),target_spin3=float(np.linalg.norm(P@vector(W))/np.linalg.norm(vector(W))),wedge_norm=float(np.linalg.norm(vector(W))),pfaffian=float(M[0,1]*M[2,3]-M[0,2]*M[1,3]+M[0,3]*M[1,2]))
def proxy():
 gpath=D.parent/'r118c3g_memory_controls/axialfine.geom';clockpath=D.parent/'r118c2r_multispecies/rei_q256.csv'
 g=np.genfromtxt(gpath.read_text().splitlines()[:-1],names=True,delimiter=',');clock=np.genfromtxt(clockpath,names=True,delimiter=',')
 S=np.stack([g[f'S{i}'] for i in range(5)],axis=1)/.025
 A=initial_span(1.,0,1/(3*np.sqrt(2)),0);Q=np.linalg.svd(A,full_matrices=False)[0];modes=S@np.linalg.pinv(A).T
 M=memory(g['u'],modes,g['h'],clock)
 Z,W,diag=construct(M,Q)
 P,_=projector()
 ref=vector(A@M@A.T);diag.update(reference_fraction=float(np.linalg.norm(P@ref)/np.linalg.norm(ref)),proxy_reconstruction_error=float(np.linalg.norm(S-modes@A.T)/np.linalg.norm(S)),input_sha=sha(gpath),clock_sha=sha(clockpath),matrix=M.tolist(),candidate=Z.tolist())
 # Check covariance identity independently with integrated transformed history.
 Wcheck=memory(g['u'],modes@Z.T,g['h'],clock)
 diag['congruence_check_relative']=float(np.linalg.norm(Wcheck-W)/np.linalg.norm(W));diag['reintegrated_fraction']=float(np.linalg.norm(P@vector(Wcheck))/np.linalg.norm(vector(Wcheck)))
 return diag
def check_gaps():
 rng=np.random.default_rng(20261126);errs=[]
 for _ in range(128):
  n=rng.normal(size=5);n/=np.linalg.norm(n);Q=np.linalg.svd(n[None,:],full_matrices=True)[2][1:].T
  got=np.sort(principal_bound(Q)['singular_values']);errs.append(float(np.max(abs(got-gap_spectrum(n)))))
 assert max(errs)<1e-12
 return max(errs)
if __name__=='__main__':
 d=proxy();d['gap_random_max_error']=check_gaps();(D/'PROXY.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d,indent=2))
