"""Direct second-order homogeneous Einstein-Vlasov-Thomson STF coefficients.
No finite-amplitude shear input. All controls at z=1600; scalar REC/REI clock.
"""
import numpy as np,json,sys
from pathlib import Path
from itertools import combinations_with_replacement
from scipy.integrate import solve_ivp
from scipy.linalg import expm
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'r118c3i_temporal_rank'))
from linear_response import OG,ON,OM,OL,T0,K0,CLOCK
sys.path.insert(0,str(D.parent/'r118c3m_order_resolved'))
from symmetry import B as BASIS
PAIRS=np.array(list(combinations_with_replacement(range(4),2)));ii,jj=PAIRS.T
MASS=np.array([.001,.006,.05])
EARLY=D.parent/'r118c3d_four_tracks/REC_CLOCK.csv'
def stf(x):return (x+x.T)/2-np.eye(3)*np.trace(x)/3
def Q(a,b):return stf(a@b)
def product(a,b):return np.where(ii==jj,a[ii]*b[jj],a[ii]*b[jj]+a[jj]*b[ii])
def radial(y,w,m,a):
 f=1/(1+np.exp(y));e=np.hypot(y,a*m/T0);r=(y/e)**2
 f1=y*f*(1-f);f2=.5*(y*y*f*(1-f)*(1-2*f)-f1);v=w*y**4/e
 return np.array([w@(y*y*f*e),w@(y**4*f/e),v@(2*f1/15),v@(f*(2/3-2*r/15)),v@(f*(2/3-2*r/5+4*r*r/35)),v@(f1*(-4/15+8*r/105)),v@(8*f2/105)])
def solve(nr,nt):
 y,w=leggauss(nr);y=30*(1+y);w=30*w;norm=w@(y**3/(1+np.exp(y)));fac=ON/(3*norm)
 cold=OM+ON-fac*sum(radial(y,w,m,1)[0] for m in MASS)
 e=np.genfromtxt(EARLY,names=True,delimiter=',');l=np.genfromtxt(CLOCK,names=True,delimiter=',')
 a0=e['a'][0];cut=np.log(1/(21*a0));end=np.log(.2/a0)
 src=np.eye(4)[1:]
 def bg(t):
  a=a0*np.exp(t);rr=np.array([radial(y,w,m,a) for m in MASS]);rho,pt,A,G,BB,BJ,JJ=rr.T
  h2=(cold*a+OG+fac*rho.sum())/a**4+OL
  qd=(cold*a+2*OG+fac*(rho+pt).sum())/(2*h2*a**4)-OL/h2
  ne=np.interp(t,e['u'],e['ne_m3']) if t<=cut else np.interp(t-cut,l['u'],l['ne_m3'])
  return a,h2,qd,K0*ne/np.sqrt(h2),A,G,BB,BJ,JJ
 def rhs(t,z):
  s,b,A,P=z[:16].reshape(4,4);s2,b2,A2,P2=z[16:].reshape(4,10)
  a,h2,qd,K,j,g,bb,bj,jj=bg(t)
  pi=(fac*(j@src-g.sum()*b)+2/15*OG*A)/a**4
  quad=bb.sum()*product(b,b)+sum(bj[m]*product(b,src[m])+jj[m]*product(src[m],src[m]) for m in range(3))
  pi2=(fac*(quad-g.sum()*b2)+2/15*OG*A2)/a**4
  return np.r_[(qd-2)*s+3*pi/h2,s,-4*s-K*(.9*A+.4*P),-K*(.15*A+.4*P),(qd-2)*s2+3*pi2/h2,s2,-4*s2-K*(.9*A2+.4*P2)-10/7*product(s,A),-K*(.15*A2+.4*P2)+10/7*product(s,P)]
 z=np.zeros(56);z[0]=1
 v=[]
 for lo,hi,n in [(0,cut,nt),(cut,end,nt//4)]:
  sol=solve_ivp(rhs,(lo,hi),z,t_eval=np.linspace(lo,hi,n+1),method='DOP853',rtol=3e-12,atol=2e-16,max_step=(hi-lo)/n);assert sol.success
  v.append(sol);z=sol.y[:,-1]
 u=np.r_[v[0].t,v[1].t[1:]];data=np.c_[v[0].y,v[1].y[:,1:]]
 h=np.array([np.sqrt(bg(t)[1]) for t in u])
 return u,h,data[:16].reshape(4,4,-1),data[16:].reshape(4,10,-1)
def combine(C,first,second):
 # C is 5x4 matrix of STF components
 M=np.einsum('ka,kij->aij',C,BASIS);Qij=np.array([Q(M[i],M[j]) for i,j in PAIRS])
 Qv=np.einsum('aij,kij->ka',Qij,BASIS)
 return np.einsum('ka,bat->bkt',C,first),np.einsum('ka,bat->bkt',Qv,second)
def stress_check():
 y,w=leggauss(96);y=30*(1+y);w=30*w;mu,v=leggauss(12);phi=np.arange(24)*2*np.pi/24
 mm,pp=np.meshgrid(mu,phi,indexing='ij');n=np.stack([np.sqrt(1-mm**2)*np.cos(pp),np.sqrt(1-mm**2)*np.sin(pp),mm],axis=-1).reshape(-1,3);ww=np.repeat(v/48,24)
 rng=np.random.default_rng(19);B,J,B2=[np.einsum('k,kij->ij',rng.normal(size=5),BASIS)/3 for _ in range(3)]
 rows=[]
 for a in [.000625,.01,.2]:
  m=.05;R=radial(y,w,m,a);want=-R[3]*B2+R[4]*Q(B,B)+R[5]*Q(B,J)+R[6]*Q(J,J)
  def exact(ep):
   F=expm(ep*B+ep*ep*B2);p=n@np.linalg.inv(F);j=np.einsum('ni,ij,nj->n',n,J,n)
   f=1/(1+np.exp(y[None,:]*np.exp(-ep*j[:,None])));E=np.hypot(np.linalg.norm(p,axis=1)[:,None]*y[None,:],a*m/T0)
   c=(f/E)@(w*y**4);return stf((p.T*(ww*c))@p)
  for ep in [.002,.001,.0005]:
   got=(exact(ep)+exact(-ep)-2*exact(0))/(2*ep*ep)
   rows.append(dict(a=a,eps=ep,relative=float(np.linalg.norm(got-want)/np.linalg.norm(want))))
 return rows
def main():
 out=stress_check();assert max(x['relative'] for x in out if x['eps']==.0005)<1e-5
 for nr,nt in [(48,384),(96,768)]:
  u,h,f,s=solve(nr,nt);np.savez_compressed(D/f'COEFF_{nt}.npz',u=u,h=h,first=f,second=s)
  print('coeff',nr,nt,flush=True)
 (D/'R7.json').write_text(json.dumps(dict(stress_check=out,scope='direct STF second-order continuum quadrature with scalar opacity, not exact nonlinear trajectory'),indent=2)+'\n')
 print(out)
if __name__=='__main__':main()
