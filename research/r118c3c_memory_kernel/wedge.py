import numpy as np,json,hashlib
from pathlib import Path
from scipy.integrate import solve_ivp,cumulative_trapezoid
from numpy.polynomial.legendre import leggauss
from itertools import combinations
D=Path(__file__).resolve().parent;P=D.parent/'r118c3b_multistf';src=P/'a0125_history.csv';ne=D.parent/'r118c2r_multispecies/rei_q256.csv'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
r=np.genfromtxt(src,names=True,delimiter=',');n=np.genfromtxt(ne,names=True,delimiter=',');u=r['u'];end=u[-1];S=np.stack([r[f'S{k}'] for k in range(5)],axis=1)/.0125
def K(t):return 299792458*6.6524587051e-29/2.1842852410855023e-18*np.interp(t,n['u'],n['ne_m3'])/np.interp(t,u,r['h'])
def actual(t):return np.stack([np.interp(t,u,S[:,i]) for i in range(5)],axis=-1)
E=np.zeros((5,3,3));E[0]=np.diag([1,-1,0])/np.sqrt(2);E[1]=np.diag([-1,-1,2])/np.sqrt(6)
for k,(i,j) in enumerate(((0,1),(0,2),(1,2)),2):E[k,i,j]=E[k,j,i]=1/np.sqrt(2)
eps=np.zeros((3,3,3));eps[0,1,2]=eps[1,2,0]=eps[2,0,1]=1;eps[0,2,1]=eps[2,1,0]=eps[1,0,2]=-1
def M(A,B):
 t=np.einsum('iab,ja,kb->ijk',eps,A,B);t=sum(t.transpose(p) for p in ((0,1,2),(0,2,1),(1,0,2),(1,2,0),(2,0,1),(2,1,0)))/6
 v=np.einsum('ijj->i',t);return t-(np.einsum('ij,k->ijk',np.eye(3),v)+np.einsum('ik,j->ijk',np.eye(3),v)+np.einsum('jk,i->ijk',np.eye(3),v))/5
pairs=list(combinations(range(5),2));T=np.array([M(E[i],E[j]) for i,j in pairs]).reshape(10,27);G=T@T.T;ev=np.linalg.eigvalsh(G)
assert sum(ev>1e-12)==7 and np.max(abs(ev[-7:]-ev[-1]))<1e-14
ii,jj=np.array(pairs).T
def solve(fn):
 def rhs(t,y):
  a,p,w=y[:5],y[5:10],y[10:];s=fn(t);k=K(t)
  return np.r_[-4*s-k*(.9*a+.4*p),-k*(.15*a+.4*p),s[ii]*p[jj]-s[jj]*p[ii]-k*w]
 sol=solve_ivp(rhs,(0,end),np.zeros(20),rtol=2e-12,atol=1e-16,method='DOP853',max_step=end/1024);assert sol.success
 return sol.y[10:,-1]
tt=np.linspace(0,end,65537);tau=cumulative_trapezoid(K(tt),tt,initial=0)
def tri(fn,nn):
 x,w=leggauss(nn);t=(x+1)*end/2;v=t[:,None]*(x+1)/2;wt=w[:,None]*end/2*t[:,None]*w/2
 dt=np.interp(t,tt,tau)[:,None]-np.interp(v,tt,tau);f=wt*(6/7)*(np.exp(-.3*dt)-np.exp(-dt))*np.exp(-(tau[-1]-np.interp(t,tt,tau)))[:,None]
 s=fn(t)[:,None,:];p=fn(v);return np.sum(f[:,:,None]*(s[:,:,ii]*p[:,:,jj]-s[:,:,jj]*p[:,:,ii]),axis=(0,1))
def fixed(t):return np.asarray(actual(t))[...,0,None]*np.array([1.,0.,0.,0.,.75])
def shape(t,k,rev=False):
 t=np.asarray(t);a=np.zeros(t.shape+(5,));a[...,0]=1.;a[...,k]=1-t/end if rev else t/end;return a
cases={}
for name,fn in [('actual',actual),('fixed',fixed),('commuting',lambda t:shape(t,1)),('noncommuting',lambda t:shape(t,2)),('reverse',lambda t:shape(t,1,True))]:
 w=solve(fn);q=tri(fn,256);q2=tri(fn,512);v=w@T;norm=np.linalg.norm(v);den=abs(w)@np.linalg.norm(T,axis=1)
 row=dict(wedge=w.tolist(),quad256=q.tolist(),quad512=q2.tolist(),quad_abs=float(np.linalg.norm(w-q2)),tensor_norm=float(norm),normalized_B3=float(16/np.sqrt(189)*norm),cancellation_ratio=float(norm/den) if den else None,channels=(w[:,None]*T).tolist())
 cases[name]=row;print(name,{k:row[k] for k in ('tensor_norm','normalized_B3','cancellation_ratio','quad_abs')})
assert abs(cases['commuting']['tensor_norm']/cases['noncommuting']['tensor_norm']-np.sqrt(5))<1e-8
assert np.linalg.norm(np.array(cases['commuting']['wedge'])+cases['reverse']['wedge'])<1e-8*np.linalg.norm(cases['commuting']['wedge'])
assert np.linalg.norm(np.array(cases['commuting']['quad512'])+cases['reverse']['quad512'])<1e-15
p=np.genfromtxt(P/'p12ref.csv',names=True,delimiter=',');m=(p['ell']==3)&(p['order']==2);ref=np.linalg.norm(p['re'][m]+1j*p['im'][m])
out=dict(status='DERIVED_AND_CHECKED_WEDGE',inputs={str(p):sha(p) for p in (src,ne,P/'p12ref.csv')},pairs=pairs,gram=G.tolist(),eigenvalues=ev.tolist(),cases=cases,reference_norm=float(ref),relative=float(abs(cases['actual']['normalized_B3']/ref-1)))
print('eigenvalues',ev,'actual native relative',out['relative'])
(D/'WEDGE.json').write_text(json.dumps(out,indent=2)+'\n')
