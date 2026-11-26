"""Physical early-to-late linear STF transfer on pinned REC/REI clocks."""
import sys,json,numpy as np
from pathlib import Path
from itertools import combinations
from scipy.integrate import solve_ivp
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'r118c3i_temporal_rank'))
from linear_response import OG,ON,OM,OL,T0,K0,CLOCK,coeff,skew
sys.path.insert(0,str(D.parent/'r118c3j_radial_channels'))
from optimize import construct,evaluate
EARLY=D.parent/'r118c3d_four_tracks/REC_CLOCK.csv'
def solve(nr=64,nt=256):
 e=np.genfromtxt(EARLY,names=True,delimiter=',');l=np.genfromtxt(CLOCK,names=True,delimiter=',')
 start=e['a'][0];a20=1/21;cut=np.log(a20/start);end=np.log(.2/start)
 y,w=leggauss(nr);y=30*(1+y);w=30*w;f=1/(1+np.exp(y));norm=w@(y**3*f);masses=[.001,.006,.05];fac=ON/norm/3
 cold=OM+ON-fac*sum(coeff(y,w,m,1.)[0] for m in masses);n=4;src=np.zeros((3,n));src[:,1:]=np.eye(3);i,j=np.array(list(combinations(range(n),2))).T
 def bg(t):
  a=start*np.exp(t);rr=np.array([coeff(y,w,m,a) for m in masses]);rho,pt,J,G=rr.T
  h2=(cold*a+OG+fac*rho.sum())/a**4+OL;qd=(cold*a+2*OG+fac*(rho+pt).sum())/(2*h2*a**4)-OL/h2
  ne=np.interp(t,e['u'],e['ne_m3']) if t<=cut else np.interp(t-cut,l['u'],l['ne_m3'])
  return a,h2,qd,K0*ne/np.sqrt(h2),J,G
 def rhs(t,z):
  s,b,A,P=z[:16].reshape(4,4);a,h2,qd,k,J,G=bg(t)
  stress=(fac*(J@src-G.sum()*b)+(2/15)*OG*A)/a**4
  return np.r_[(qd-2)*s+3*stress/h2,s,-4*s-k*(.9*A+.4*P),-k*(.15*A+.4*P),s[i]*P[j]-s[j]*P[i]-k*z[16:22],k]
 ic=np.zeros(23);ic[0]=1
 tol=np.r_[np.full(16,2e-15),np.full(6,2e-22),1e-12]
 def integ(a,b,ic,nstep):
  z=solve_ivp(rhs,(a,b),ic,method='DOP853',rtol=2e-11,atol=tol,max_step=(b-a)/nstep,t_eval=np.linspace(a,b,nstep+1));assert z.success;return z
 early=integ(0,cut,ic,nt);v=early.y[:,-1];s,b,A,P=v[:16].reshape(4,4);T=np.vstack([s,src-b,A,P])
 start_l=v.copy();start_l[16:]=0;late=integ(cut,end,start_l,nt);whole=integ(cut,end,v,nt)
 M=skew(late.y[16:22,-1],4);Mw=skew(whole.y[16:22,-1],4)
 ref=json.loads((D.parent/'r118c3k_radiation_channels/R7.json').read_text())['rows'][-1];M0=np.array(ref['M']);Mt=T.T@M0@T
 U,sv,V=np.linalg.svd(T,full_matrices=False);proj=U@U.T
 target=np.array(ref['A']);target_proj=target@proj
 # Fit early coefficient control to late target; norm can be large, report not physical.
 inv=target@np.linalg.pinv(T.T);diff=np.linalg.norm(target-inv@T.T)/np.linalg.norm(target)
 def diag(M):
  ss=np.linalg.svd(M,compute_uv=False);a,_=construct(M);return dict(sv=ss.tolist(),ratio=float(ss[2]/ss[0]),bound=float(np.sqrt(5)*ss[2]),control=a.tolist(),constructed=evaluate(M,a))
 out=dict(nr=nr,nt=nt,start_a=float(start),cut=float(cut),transfer=T.tolist(),transfer_sv=sv.tolist(),target_projection_error=float(diff),target_early_control_norm=float(np.linalg.norm(inv,2)),early_tau=float(v[-1]),late_tau=float(late.y[-1,-1]),pullback_relative=float(np.linalg.norm(M-Mt)/np.linalg.norm(M)),early_memory_check=float(np.linalg.norm(Mw-M-skew(v[16:22],4)*np.exp(-late.y[-1,-1]))/np.linalg.norm(Mw)),late=diag(M),whole=diag(Mw),scope='linear four early controls, A=P=0 at z1600; C3D scalar REC clock, C3I scalar REI clock, no early photon modes beyond this model')
 return out
def main():
 rows=[solve(48,192),solve(96,512)]
 (D/'R7.json').write_text(json.dumps(rows,indent=2)+'\n')
 for q in rows:print({k:v for k,v in q.items() if k not in ['transfer','late','whole']},q['late']['ratio'],q['late']['bound'],q['whole']['ratio'],q['whole']['bound'],flush=True)
if __name__=='__main__':main()
