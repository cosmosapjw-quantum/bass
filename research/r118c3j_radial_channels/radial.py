"""Momentum-dependent bounded STF initial distributions and temporal skew."""
from pathlib import Path
import sys,json,numpy as np
from scipy.integrate import solve_ivp
from numpy.polynomial.legendre import leggauss
from itertools import combinations
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'r118c3i_temporal_rank'))
from linear_response import OG,ON,OM,OL,T0,K0,CLOCK,coeff,skew,projector
def windows(y,n):
 if n==1:return np.ones((1,len(y)))
 c=np.linspace(.7,8,n);q=np.exp(-.5*((y[None,:]-c[:,None])/1.4)**2-np.max(-.5*((y[None,:]-c[:,None])/1.4)**2,axis=0))
 return q/q.sum(axis=0)
def solve(masses,nw,nr,nt):
 y,w=leggauss(nr);y=30*(1+y);w=30*w;f=1/(1+np.exp(y));norm=w@(y**3*f);win=windows(y,nw);ns=len(masses);n=1+ns*nw;i,j=np.array(list(combinations(range(n),2))).T
 fac=ON/norm/ns;cold=OM+ON-fac*sum(coeff(y,w,m,1)[0] for m in masses);assert cold>0
 clock=np.genfromtxt(CLOCK,names=True,delimiter=',');end=np.log(21/5);u=np.linspace(0,end,nt+1);ic=np.zeros(4*n+len(i));ic[0]=1
 def bg(t):
  a=np.exp(t)/21.;rr=np.array([coeff(y,w,m,a) for m in masses]);rho,pt,J,G=rr.T
  A=np.array([win@(2/15*w*y**5*f*(1-f)/np.hypot(y,a*m/T0)) for m in masses]);h2=(cold*a+OG+fac*rho.sum())/a**4+OL
  q=(cold*a+2*OG+fac*(rho+pt).sum())/(2*h2*a**4)-OL/h2;K=K0*np.interp(t,clock['u'],clock['ne_m3'])/np.sqrt(h2)
  return a,h2,q,K,A,G
 def rhs(t,z):
  s,b,A,P=z[:4*n].reshape(4,n);a,h2,q,K,J,G=bg(t)
  stress=(fac*(np.r_[0.,J.ravel()]-G.sum()*b)+(2/15)*OG*A)/a**4
  return np.r_[(q-2)*s+3*stress/h2,s,-4*s-K*(.9*A+.4*P),-K*(.15*A+.4*P),s[i]*P[j]-s[j]*P[i]-K*z[4*n:]]
 sol=solve_ivp(rhs,(0,end),ic,t_eval=u,method='DOP853',rtol=3e-12,atol=np.r_[np.full(4*n,1e-16),np.full(len(i),1e-27)],max_step=end/nt);assert sol.success
 M=skew(sol.y[4*n:,-1],n);sv=np.linalg.svd(M,compute_uv=False);gs=np.linalg.svd(sol.y[:n].T,compute_uv=False)
 err=max(abs(bg(t)[4].sum(axis=1)-bg(t)[5]).max()/max(bg(t)[5]) for t in u[::max(1,nt//8)])
 out=dict(masses=masses,nw=nw,nr=nr,nt=nt,sv=sv.tolist(),ratio=float(sv[2]/sv[0]),pure_spin1_wedge_bound_unit_control=float(np.sqrt(5)*sv[2]),temporal_sv=gs.tolist(),partition_ibp_error=float(err),M=M.tolist())
 return out
def finite_check():
 # exact angular FD population at perturbed exponent; compare derivative in one STF direction
 y,w=leggauss(96);y=30*(1+y);w=30*w;mu,v=leggauss(64);q=(3*mu**2-1)/np.sqrt(6);win=windows(y,3)[1];f=1/(1+np.exp(y));E=np.hypot(y,.1*.006/T0)
 want=2/15*np.sum(w*y**5*f*(1-f)*win/E)
 out={}
 for eps in [1e-2,1e-3,1e-4]:
  def P(eps):
   g=1/(1+np.exp(y[:,None]*np.exp(-eps*win[:,None]*q[None,:])))
   assert np.min(g)>0 and np.max(g)<1
   return (w*y**4/E)@(g@(v*q/2))
  got=(P(eps)-P(-eps))/(2*eps);out[str(eps)]=float(abs(got/want-1))
 return out
def main():
 cases=[]
 for n in [1,3,5]:
  a=solve([.001,.006,.05],n,48,128);cases.append(a);print(n,a['ratio'],a['pure_spin1_wedge_bound_unit_control'],flush=True)
 for n in [1,3,5]:
  a=solve([.001,.006,.05],n,96,256);cases.append(a);print(n,a['ratio'],a['pure_spin1_wedge_bound_unit_control'],flush=True)
 o=dict(cases=cases,finite_fd=finite_check(),scope='linear source-owned momentum profiles, not native finite dynamics; no exact rank certification')
 (D/'RADIAL.json').write_text(json.dumps(o,indent=2)+'\n')
if __name__=='__main__':main()
