"""Radiative initial-condition controls; homogeneous linear STF model."""
import sys,json,numpy as np
from pathlib import Path
from scipy.integrate import solve_ivp
from numpy.polynomial.legendre import leggauss
from itertools import combinations
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'r118c3i_temporal_rank'))
from linear_response import OG,ON,OM,OL,T0,K0,CLOCK,coeff,skew
sys.path.insert(0,str(D.parent/'r118c3j_radial_channels'))
from optimize import construct,evaluate
def solve(nr=96,nt=256,mode='both'):
 masses=[.001,.006,.05];ns=3;nc=4+int(mode in ['I','both'])+int(mode in ['P','both']);i,j=np.array(list(combinations(range(nc),2))).T
 y,w=leggauss(nr);y=30*(1+y);w=30*w;f=1/(1+np.exp(y));norm=w@(y**3*f);fac=ON/norm/ns
 cold=OM+ON-fac*sum(coeff(y,w,m,1.)[0] for m in masses)
 clock=np.genfromtxt(CLOCK,names=True,delimiter=',');end=np.log(21/5);u=np.linspace(0,end,nt+1)
 src=np.zeros((3,nc));src[:,1:4]=np.eye(3);ic=np.zeros(4*nc+len(i));ic[0]=1
 if mode in ['I','both']:ic[2*nc+4]=1
 if mode in ['P','both']:ic[3*nc+nc-1]=1
 def bg(t):
  a=np.exp(t)/21.;rr=np.array([coeff(y,w,m,a) for m in masses]);rho,pt,J,G=rr.T
  h2=(cold*a+OG+fac*rho.sum())/a**4+OL;qd=(cold*a+2*OG+fac*(rho+pt).sum())/(2*h2*a**4)-OL/h2
  k=K0*np.interp(t,clock['u'],clock['ne_m3'])/np.sqrt(h2)
  return a,h2,qd,k,J,G
 def rhs(t,z):
  s,b,A,P=z[:4*nc].reshape(4,nc);a,h2,qd,k,J,G=bg(t)
  stress=(fac*(J@src-G.sum()*b)+(2/15)*OG*A)/a**4
  return np.r_[(qd-2)*s+3*stress/h2,s,-4*s-k*(.9*A+.4*P),-k*(.15*A+.4*P),s[i]*P[j]-s[j]*P[i]-k*z[4*nc:]]
 sol=solve_ivp(rhs,(0,end),ic,t_eval=u,method='DOP853',rtol=3e-12,atol=np.r_[np.full(4*nc,1e-16),np.full(len(i),1e-26)],max_step=end/nt);assert sol.success
 M=skew(sol.y[4*nc:,-1],nc);sv=np.linalg.svd(M,compute_uv=False);A,scale=construct(M);v=evaluate(M,A)
 return dict(mode=mode,nr=nr,steps=nt,sv=sv.tolist(),ratio=float(sv[2]/sv[0]),wedge_bound=float(np.sqrt(5)*sv[2]),constructed=v,M=M.tolist(),A=A.tolist()),u,sol.y[:4*nc].reshape(4,nc,-1)
def main():
 rows=[]
 for n in [128,512]:
  for mode in ['none','I','P','both']:
   o,u,v=solve(96 if n==512 else 48,n,mode);rows.append(o);print(mode,n,o['ratio'],o['wedge_bound'],o['constructed'],flush=True)
   if n==512:np.savez_compressed(D/f'response_{mode}.npz',u=u,values=v)
 (D/'R7.json').write_text(json.dumps(dict(rows=rows,scope='C3I linear quadrupole closure, initial radiative data independently varied; W is only a component of native B3 when seed nonzero'),indent=2)+'\n')
if __name__=='__main__':main()
