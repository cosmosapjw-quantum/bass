"""Early-to-late radial source reachability, fixed FD-number weighted budget."""
import sys,json,numpy as np
from pathlib import Path
from scipy.linalg import block_diag
from scipy.integrate import solve_ivp
from numpy.polynomial.legendre import leggauss
from itertools import combinations
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'r118c3j_radial_channels'))
from radial import windows,coeff,OG,ON,OM,OL,T0,K0,CLOCK,skew
from optimize import construct,evaluate
EARLY=D.parent/'r118c3d_four_tracks/REC_CLOCK.csv'
BUDGET=json.loads((D.parent/'r118c3r_fixed_wedge/R7.json').read_text())['metric_norm']
def solve(nw,nr,nt):
 e=np.genfromtxt(EARLY,names=True,delimiter=',');l=np.genfromtxt(CLOCK,names=True,delimiter=',')
 start=e['a'][0];cut=np.log(1/(21*start));end=np.log(.2/start)
 y,w=leggauss(nr);y=30*(1+y);w=30*w;f=1/(1+np.exp(y));V=windows(y,nw)
 n=1+3*nw;i,j=np.array(list(combinations(range(n),2))).T
 wt=w*y*y*f;wt/=wt.sum();g=(V*wt)@V.T/3;G=block_diag(np.ones((1,1)),g,g,g)
 ge,gu=np.linalg.eigh(G);assert min(ge)>0
 H=(gu/np.sqrt(ge))@gu.T;fac=ON/(w@(y**3*f))/3;masses=[.001,.006,.05]
 cold=OM+ON-fac*sum(coeff(y,w,m,1.)[0] for m in masses)
 def bg(t):
  a=start*np.exp(t);rr=np.array([coeff(y,w,m,a) for m in masses]);rho,pt,J,G0=rr.T
  A=np.array([V@(2/15*w*y**5*f*(1-f)/np.hypot(y,a*m/T0)) for m in masses])
  h2=(cold*a+OG+fac*rho.sum())/a**4+OL;q=(cold*a+2*OG+fac*(rho+pt).sum())/(2*h2*a**4)-OL/h2
  ne=np.interp(t,e['u'],e['ne_m3']) if t<=cut else np.interp(t-cut,l['u'],l['ne_m3'])
  return a,h2,q,K0*ne/np.sqrt(h2),A,G0
 # Direct integration in whitened controls: response to basis columns H.
 ic=np.zeros(4*n+len(i));ic[:n]=H[0]
 def rhs(t,z):
  s,b,A,P=z[:4*n].reshape(4,n);a,h,q,k,J,G0=bg(t)
  stress=(fac*(np.r_[0.,J.ravel()]@H-G0.sum()*b)+(2/15)*OG*A)/a**4
  return np.r_[(q-2)*s+3*stress/h,s,-4*s-k*(.9*A+.4*P),-k*(.15*A+.4*P),s[i]*P[j]-s[j]*P[i]-k*z[4*n:]]
 atol=np.r_[np.full(4*n,1e-15),np.full(len(i),2e-24)]
 a=solve_ivp(rhs,(0,cut),ic,method='DOP853',rtol=3e-12,atol=atol,max_step=cut/nt);assert a.success
 b=solve_ivp(rhs,(cut,end),a.y[:,-1],method='DOP853',rtol=3e-12,atol=atol,max_step=(end-cut)/nt);assert b.success
 M=skew(b.y[4*n:,-1],n);sv=np.linalg.svd(M,compute_uv=False)
 A,_=construct(M);A*=np.sqrt(BUDGET)/np.linalg.norm(A);C=A@H
 assert abs(np.trace(C@G@C.T)-BUDGET)<1e-10
 q=evaluate(M,A);test=max(np.max(abs(bg(t)[4].sum(axis=1)-bg(t)[5]))/max(bg(t)[5]) for t in np.linspace(0,end,20))
 peak=max(np.linalg.norm(C[:,1+s*nw:1+(s+1)*nw]@windows(np.linspace(0,60,400),nw),axis=0).max() for s in range(3))
 return dict(nw=nw,nr=nr,nt=nt,metric_condition=float(ge[-1]/ge[0]),whitened_sv=sv.tolist(),bound=float(BUDGET*sv[2]/2),control=C.tolist(),budget=float(np.trace(C@G@C.T)),constructed=q,peak=peak,partition_error=test,M=M.tolist(),G=G.tolist(),H=H.tolist())
def run():
 rows=[]
 for nw in [1,2,3,5]:
  for nr,nt in [(48,192),(96,512)]:
   r=solve(nw,nr,nt);rows.append(r);print(nw,nr,r['whitened_sv'][:6],r['constructed'],r['peak'],flush=True)
 for a,b in zip(rows[::2],rows[1::2]):
  C=np.array(a['control']);G=np.array(b['G']);H=np.array(b['H']);A=C@np.linalg.inv(H);M=np.array(b['M'])
  b['coarse_control_fine']=evaluate(M,A);b['coarse_budget_fine']=float(np.trace(C@G@C.T))
 out=dict(rows=rows,scope='same early/late scalar clocks, FD window control space, direct whitened linear transfer; weighted budget from C3R, not fixed W or nonlinear null; actual radial jets separate')
 (D/'R7.json').write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':run()
