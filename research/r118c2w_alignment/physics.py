"""Self-consistent weak STF Einstein/Thomson + massive memories; early B3 tensor."""
import sys,json,hashlib
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import expm
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent;P=D.parent/'r118c2r_multispecies'
sys.path.insert(0,str(D.parent/'r118c2p_massive_feedback'))
from massive import Species,OG0,ON0,OM,OL,H0,TNU_EV,C,SIG
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
for p,h in json.loads((P/'SOURCES.json').read_text()).items():assert sha(Path(p))==h
E=np.array([np.diag([1.,-1.,0.])/np.sqrt(2),np.diag([-1.,-1.,2.])/np.sqrt(6),[[0,1/np.sqrt(2),0],[1/np.sqrt(2),0,0],[0,0,0]],[[0,0,1/np.sqrt(2)],[0,0,0],[1/np.sqrt(2),0,0]],[[0,0,0],[0,0,1/np.sqrt(2)],[0,1/np.sqrt(2),0]]])
def tensor(x):return np.einsum('...a,aij->...ij',x,E)
eps=np.zeros((3,3,3))
for i in range(3):eps[i,(i+1)%3,(i+2)%3]=1;eps[i,(i+2)%3,(i+1)%3]=-1
def M(s,e):
 r=np.einsum('iab,ja,kb->ijk',eps,tensor(s),tensor(e));r=sum(r.transpose(p) for p in [(0,1,2),(0,2,1),(1,0,2),(1,2,0),(2,0,1),(2,1,0)])/6
 v=np.einsum('ijj->i',r);return r-(np.einsum('ij,k->ijk',np.eye(3),v)+np.einsum('ik,j->ijk',np.eye(3),v)+np.einsum('jk,i->ijk',np.eye(3),v))/5
sp=[Species(m,256) for m in (.001,.05)]
cold=OM+ON0-sum(s.moments(1.)[0]/2 for s in sp)
hist=np.genfromtxt(P/'rei_q256.csv',names=True,delimiter=',');u=hist['u'];ne=hist['ne_m3']
def coeff(t):
 a=np.exp(t)/21;r,p,chi,dc=np.array([s.moments(a) for s in sp]).T/2
 den=cold*a+OG0+r.sum();pt=OG0/3+p.sum();tot=den+OL*a**4
 return OG0/tot,-1.5*(den+pt)/tot,chi/tot,C*SIG*np.interp(t,u,ne)/(H0*np.sqrt(tot/a**4))
S0=np.array([1.,0.,0.,0.,0.]);cases={}
for name,J in [('aligned',np.array([S0,.7*S0])),('diagonal',np.array([[0,1.,0,0,0],S0])),('rotating',np.array([[0,1,0,0,0],[0,0,.6,.8,0]]))]:
 def rhs(t,v):
  s,a,p,b=v[:20].reshape(4,5);og,d,chi,k=coeff(t);force=chi@(J-b)
  return np.r_[-(3+d)*s+.4*og*a+3*force,-4*s-k*(.9*a+.4*p),-k*(.15*a+.4*p),s,(M(s,p)-k*v[20:].reshape(3,3,3)).ravel()]
 y0=np.r_[S0,np.zeros(42)];S1=rhs(0,y0)[:5];k0=coeff(0)[-1];pred=-k0/20*M(S0,S1)
 sol=solve_ivp(rhs,(0,u[-1]),y0,method='DOP853',rtol=1e-12,atol=1e-22,max_step=.001,dense_output=True);assert sol.success
 on=[]
 short=solve_ivp(rhs,(0,.001),y0,method='DOP853',rtol=1e-12,atol=1e-37,max_step=1e-5,dense_output=True);assert short.success
 for t in (.01,.003,.001,.0003,.0001,.00003,.00001):
  y=(short.sol(t) if t<=.001 else sol.sol(t));v=y[20:].reshape(3,3,3);n=np.linalg.norm(pred)
  on.append(dict(u=t,Bnorm=float(np.linalg.norm(v)),coefficient_relative=None if n==0 else float(np.linalg.norm(v/t**4-pred)/n)))
 ts=np.linspace(0,u[-1],2049);vv=sol.sol(ts);norms=np.linalg.norm(vv[20:],axis=0)
 row=dict(name=name,initial_k=float(k0),S1=S1.tolist(),analytic_quartic_norm=float(np.linalg.norm(pred)),onset=on,final_Bnorm=float(norms[-1]),max_Bnorm=float(max(norms)),final_S=vv[:5,-1].tolist())
 cases[name]=row;print(row,flush=True)
 if name=='aligned':assert max(norms)<1e-18
 else:assert on[-1]['coefficient_relative']<.01 and on[-1]['coefficient_relative']<on[0]['coefficient_relative']
# Nonlinear collisionless massless stress for initially isotropic canonical distribution.
x,w=leggauss(64);phi=2*np.pi*np.arange(128)/128;mu,ph=np.meshgrid(x,phi,indexing='ij')
n=np.stack([np.sqrt(1-mu**2)*np.cos(ph),np.sqrt(1-mu**2)*np.sin(ph),mu],axis=-1).reshape(-1,3)
ww=np.repeat(w/2/128,128)
rows=[]
T=E[0];T2=T@T-np.eye(3)*np.trace(T@T)/3
for e in (.1,.05,.025,.0125,.00625):
 p=n@expm(-e*T);v=np.linalg.norm(p,axis=1);P0=np.einsum('a,ai,aj->ij',ww/v,p,p);rho=ww@v;pi=P0-rho*np.eye(3)/3
 pred0=-8/15*e*T+8/21*e*e*T2
 transverse=pi-np.sum(pi*T)*T
 row=dict(epsilon=e,rho=float(rho),stress_error=float(np.linalg.norm(pi-pred0)),transverse_coeff=float(np.sum(transverse*T2)/(np.sum(T2*T2)*e*e)),density_error=float(abs(rho-(1+4/15*e*e*np.trace(T@T)-8/63*e**3*np.trace(T@T@T)))))
 rows.append(row);print(row,flush=True)
assert abs(rows[-1]['transverse_coeff']-8/21)<1e-5
(D/'PHYSICS.json').write_text(json.dumps(dict(status='DERIVED_AND_CHECKED_SCOPED_ALIGNMENT',cases=cases,nonlinear_stress=rows,source_sha=sha(P/'rei_q256.csv'),scope='linear self-consistent Einstein/Thomson/STF matter memory and leading Cartesian B3 response; nonlinear collisionless massless moment expansion separate, no full nonlinear B3 theorem'),indent=2)+'\n')
