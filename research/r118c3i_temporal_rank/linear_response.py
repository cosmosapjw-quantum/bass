"""Linearized represented Bianchi-I FD stress, temporal skew and parity."""
from pathlib import Path
import sys,json,numpy as np
from scipy.integrate import solve_ivp
from numpy.polynomial.legendre import leggauss
from itertools import combinations
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'r118c3h_reachability'))
from reachability import memory,vector,skew,projector,construct
OG=5.4437488671046486e-5;ON=3.7562511328953514e-5;OM=.315;OL=.684908;T0=.00016763891604963858;K0=299792458*6.6524587051e-29/2.1842852410855023e-18
CLOCK=D.parent/'r118c2r_multispecies/rei_q256.csv'
def coeff(y,w,m,a):
 f=1/(1+np.exp(y));e=np.hypot(y,a*m/T0)
 rho=np.sum(w*y*y*f*e);pt=np.sum(w*y**4*f/e)
 J=2/15*np.sum(w*y**5*f*(1-f)/e)
 G=np.sum(w*f*(2/3*y**4/e-2/15*y**6/e**3))
 return rho,pt,J,G
def solve(masses,nr=64,nsteps=256,tol=3e-11):
 masses=np.asarray(masses,float);ns=len(masses);n=ns+1;i,j=np.array(list(combinations(range(n),2))).T
 if min(masses)<0 or ns!=3:raise ValueError('species')
 y,w=leggauss(nr);y=30*(1+y);w=30*w;f=1/(1+np.exp(y));norm=w@(y**3*f)
 cold=OM+ON-ON/norm/ns*sum(coeff(y,w,m,1.)[0] for m in masses)
 if cold<=0:raise ValueError('cold density')
 clock=np.genfromtxt(CLOCK,names=True,delimiter=',');end=np.log(21/5);u=np.linspace(0,end,nsteps+1)
 src=np.eye(n)[1:,:];fac=ON/norm/ns;ic=np.zeros(4*n+len(i));ic[0]=1.
 def bg(t):
  a=np.exp(t)/21.;rr=np.array([coeff(y,w,m,a) for m in masses]);r,pt,J,G=rr.T
  h2=(cold*a+OG+fac*r.sum())/a**4+OL;qd=((cold*a+2*OG+fac*(r+pt).sum())/a**4)/(2*h2)-OL/h2
  k=K0*np.interp(t,clock['u'],clock['ne_m3'])/np.sqrt(h2)
  return a,h2,qd,k,J,G
 def rhs(t,z):
  s,b,A,P=z[:4*n].reshape(4,n);a,h2,qd,k,J,G=bg(t)
  stress=(fac*(J@src-G.sum()*b)+(2/15)*OG*A)/a**4
  return np.r_[(qd-2)*s+3*stress/h2,s,-4*s-k*(.9*A+.4*P),-k*(.15*A+.4*P),s[i]*P[j]-s[j]*P[i]-k*z[4*n:]]
 sol=solve_ivp(rhs,(0,end),ic,method='DOP853',rtol=tol,atol=np.r_[np.full(4*n,1e-16),np.full(len(i),1e-26)],max_step=end/nsteps,t_eval=u)
 assert sol.success
 M=skew(sol.y[4*n:,-1],n);s=sol.y[:n].T
 sv=np.linalg.svd(M,compute_uv=False);gram=np.linalg.svd(s,compute_uv=False);norms=np.linalg.norm(s,axis=0)
 normalized=M/np.outer(norms,norms);svnorm=np.linalg.svd(normalized,compute_uv=False)
 pf=M[0,1]*M[2,3]-M[0,2]*M[1,3]+M[0,3]*M[1,2]
 h=np.array([np.sqrt(bg(t)[1]) for t in u])
 out=dict(masses=masses.tolist(),nr=nr,steps=nsteps,sv=sv.tolist(),ratio=float(sv[2]/sv[0]),normalized_ratio=float(svnorm[2]/svnorm[0]),pfaffian=float(pf),temporal_sv=gram.tolist(),mode_norms=norms.tolist(),cold=float(cold),M=M.tolist())
 return out,u,s,h
def radial_check():
 y,w=leggauss(96);y=30*(1+y);w=30*w
 errs=[]
 for m in [0.,.0001,.006,.05,.2]:
  for a in [1/21,1/5,1.]:
   r,p,J,G=coeff(y,w,m,a);errs.append(abs(J-G)/max(J,G))
 return max(errs)
def parity():
 p=D.parent/'r118c3h_reachability';rows={}
 def v(label):
  a=np.genfromtxt(p/(label+'.csv'),names=True,delimiter=',');z=a['ell']==3;return a['re'][z]+1j*a['im'][z]
 for eps,plus,minus in [(0.0125,'orthogonal125_fine','orthogonal125_minus'),(.00625,'orthogonal062_plus','orthogonal062_minus')]:
  E=(v(plus)+v(minus))/(2*eps**2);O=(v(plus)-v(minus))/(2*eps**3)
  z=np.vdot(E,O);r=z.real/(np.linalg.norm(E)*np.linalg.norm(O));res=np.linalg.norm(O-E*z.real/np.vdot(E,E).real)/np.linalg.norm(O)
  rows[str(eps)]=dict(even_norm=float(np.linalg.norm(E)),odd_norm=float(np.linalg.norm(O)),real_cosine=float(r),complex_abs_cosine=float(abs(z)/(np.linalg.norm(E)*np.linalg.norm(O))),orthogonal_fraction=float(res))
 return rows
def main():
 rows=[]
 for masses in [(.001,.006,.05),(.0001,.004,.1),(.0001,.02,.2),(.001,.03,.15),(.0001,.001,.01),(.003,.02,.08)]:
  d,u,s,h=solve(masses,48,128);rows.append(d);print(masses,d['ratio'],d['normalized_ratio'],flush=True)
 best=max(rows,key=lambda q:q['ratio']);fine=[]
 for mass in [rows[0]['masses'],best['masses']]:
  q,u,s,h=solve(mass,96,512,3e-12);fine.append(q);np.savez_compressed(D/('linear_'+('base' if mass==rows[0]['masses'] else 'best')+'.npz'),u=u,s=s,h=h)
 out=dict(status='LINEAR_RESPONSE_ORACLE',radial_ibp_error=radial_check(),scan=rows,refined=fine,parity=parity(),scope='first-order represented FD and C3C Thomson quadrupole closure, not native finite amplitude; rank assessed under refinement')
 (D/'R7.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(radial=out['radial_ibp_error'],refined=fine,parity=out['parity']),indent=2))
if __name__=='__main__':main()
