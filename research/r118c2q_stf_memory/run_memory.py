"""Conditional z20->4 visibility and prescribed homogeneous shear response.
Physical input histories are full-resolution, not plotting thins."""
import json,hashlib
from pathlib import Path
import numpy as np
from scipy.integrate import cumulative_trapezoid,solve_ivp
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent.parent/'r118c2n_visibility'
I=Path('/home/cosmosapjw/worktrees/rei-htt-thomson-20261124'); H=Path('/home/cosmosapjw/Downloads')
K=I/'research/r118c2k_segment'; M=I/'research/r118c2m_energy_budget'; L=I/'research/r118c2l_tight_continuation'
fhe=.2454/(4*(1-.2454)); c=299792458.;st=6.6524587051e-29; a0=1/21
H20=67.4e3/3.0856775814913673e22*np.sqrt(.315*21**3+9.2e-5*21**4+1-.315-9.2e-5)
C=np.array([[-.9,-.4],[-.15,-.4]])
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def j(p):return json.loads(p.read_text())
sources={}
def read(p,hash_,bass=False):
    assert sha(p)==hash_;sources[str(p)]=hash_
    keys=['eta','time_s','nH_m3','x_HII','x_HeII','x_HeIII','xe'] if bass else ['a','time_s','nH_proper_cm3','x_HII','x_HeII','x_HeIII','ne_proper_cm3']
    x=np.genfromtxt(p,names=True,delimiter='\t' if bass else ',',usecols=keys)
    v=np.stack([x[k] for k in keys],axis=1)
    if bass:
        v[:,0]=np.exp(v[:,0])*a0;v[:,6]*=v[:,2]
    else:v[:,2]*=1e6;v[:,6]*=1e6
    assert np.all(np.isfinite(v)) and np.all(v[:,2]>0) and np.all(v[:,6]>=0)
    assert np.max(abs(v[:,6]/v[:,2]-v[:,3]-fhe*(v[:,4]+2*v[:,5])))<2e-14
    return v
runs={r['case']:r for r in j(K/'RUNS.json')}
old={r['case']:r for r in j(I/'research/r118c2j_error_control/RUNS.json') if r['variant']=='reduced'}
def row(r):return read(Path(r['raw_path'])/'history.csv',r['hashes']['history.csv'])
def chain(*arr):
    a=arr[0]
    for b in arr[1:]:
        assert np.allclose(a[-1],b[0],rtol=3e-14,atol=1e-30)
        a=np.concatenate((a,b[1:]))
    return a
hist={'q16':chain(row(old['long16']),row(runs['resume16']),row(runs['extend16'])),
      'q32':chain(row(old['long32']),row(runs['resume32'])),
      'q64':row(runs['fresh64']),
      'tight32':chain(row(runs['fresh32tight']),row(j(L/'ACCEPTANCE.json')),row(j(M/'CONTINUATION.json')),row(j(M/'EXTENSION.json')),row(j(M/'FINAL_HISTORY.json')))}
hist['q128']=row(j(I/'research/r118c2n_spectral/Q128.json'))
q256=j(I/'research/r118c2n_spectral/Q256.json');assert q256['status']=='PASS_SCOPED_COMPLETE'
hist['q256']=chain(*(row(r) for r in q256['segments']))
bass=j(D.parent/'r118c2m_energy_budget/RESULTS.json')
for r in bass['results']:
    if r['name'] in ('base','time2','cross','time2_strict'):
        hist['bass_'+r['name']]=read(Path(bass['raw'])/r['name']/'history.tsv',r['hashes']['history.tsv'],True)



import sys
from scipy.linalg import expm
from scipy.integrate import solve_ivp
from scipy.interpolate import PchipInterpolator
from numpy.polynomial.legendre import leggauss
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(OUT.parent/'r118c2p_massive_feedback'))
from massive import Background,Species,OG0,ON0,TNU_EV,C,SIG,A0
native=np.genfromtxt(OUT/'native.csv',delimiter=',',names=True)
# Use exact native normalization in native/Python comparison, then physical C2P Tnu for ODE.
T_native=.00016763891604963858
BETA=np.array([.2,-.1,.3,.05,-.2]);masses=[0.,.001,.01,.05,.1,.3]
basis=np.array([np.diag([1.,-1.,0.])/np.sqrt(2),np.diag([-1.,-1.,2.])/np.sqrt(6),
 [[0,1/np.sqrt(2),0],[1/np.sqrt(2),0,0],[0,0,0]],
 [[0,0,1/np.sqrt(2)],[0,0,0],[1/np.sqrt(2),0,0]],
 [[0,0,0],[0,0,1/np.sqrt(2)],[0,1/np.sqrt(2),0]]])
assert np.max(abs(np.einsum('aij,bij->ab',basis,basis)-np.eye(5)))<1e-15
def memory(y):
 w=y*y/(y*y+9.)
 return np.stack([1-w,.2*w,w,.1*w,-.3*(1-w)],axis=-1)
def radial(m,a,n=128,temp=TNU_EV,beta=BETA):
 x,w=leggauss(n);y=30*(1+x);w=30*w
 f=1/(1+np.exp(y));norm=ON0/(w@(f*y**3));e=np.hypot(y,a*m/temp)
 chi=2/15*norm*w*y**5*f*(1-f)/e;dc=-chi*(a*m/temp/e)**2
 J=memory(y);d=beta-J
 return np.array([norm*(w@(y*y*e*f)),norm/3*(w@(y**4*f/e)),chi.sum(),dc.sum()]),chi@J/chi.sum(),-chi@d,chi@np.sum(d*d,axis=1),-dc@np.sum(d*d,axis=1)
# native comparison at 774 represented a/m combinations; independent GL256
# precompute nodes to avoid repeated expensive leggauss
from functools import lru_cache
leggauss=lru_cache(None)(leggauss)
native_err=[]
for r in native:
 vals,jj,st,mem,los=radial(r['mass'],r['a'],256,T_native)
 actual=np.r_[r['rho'],r['p'],r['chi'],r['dchi'],[r[f'J{k}'] for k in range(5)],[r[f'stress{k}'] for k in range(5)],r['mem'],r['loss']]
 ref=np.r_[vals,jj,st,mem,los];err=np.max(abs(actual-ref)/np.maximum(abs(ref),1e-20))
 assert err<1e-9,(r['mass'],r['a'],err)
 native_err.append(float(err))
# Exact angular integration of a positive initial deformed FD distribution.
mu,w=leggauss(24);phi=np.arange(48)*2*np.pi/48
n=np.stack([np.sqrt(1-mu[:,None]**2)*np.cos(phi),np.sqrt(1-mu[:,None]**2)*np.sin(phi),np.broadcast_to(mu[:,None],(24,48))],axis=-1).reshape(-1,3)
wa=np.repeat(w/2/48,48);yb,wy=leggauss(96);y=30*(yb+1);wy*=30
J=memory(y);jm=np.einsum('qa,aij->qij',J,basis);Bmat=np.einsum('a,aij->ij',BETA,basis)
f0=1/(np.exp(y)+1);norm=ON0/(wy@(y**3*f0))
def exact(m,a,h,rot=np.eye(3)):
 nn=n@rot.T;bm=rot@Bmat@rot.T;jrot=np.einsum('ij,qjk,lk->qil',rot,jm,rot)
 ph=nn@expm(-h*bm).T
 p=y[:,None,None]*ph[None,:,:]
 e=np.sqrt(np.sum(p*p,axis=-1)+(a*m/TNU_EV)**2)
 jproj=np.einsum('ai,qij,aj->qa',nn,jrot,nn)
 f=1/(np.exp(y[:,None]*np.exp(-h*jproj))+1)
 stress=norm*np.einsum('q,a,qa,qai,qaj->ij',wy*y*y,wa,f/e,p,p)
 return stress-np.eye(3)*np.trace(stress)/3
checks=[]
for m in masses:
 for a in (A0,.1,.2):
  vals,jj,st,mem,los=radial(m,a,256)
  want=np.einsum('a,aij->ij',st,basis)
  h=1e-5;num=(exact(m,a,h)-exact(m,a,-h))/(2*h)
  rel=float(np.linalg.norm(num-want)/np.linalg.norm(want));assert rel<2e-8
  checks.append(dict(m=m,a=a,relative=rel))
# Native radial response is independent of chosen frame; check transformed exact tensor.
rot=expm(np.array([[0.,-.4,.2],[.4,0.,-.3],[-.2,.3,0.]]))
r=(exact(.05,.2,1e-5,rot)-exact(.05,.2,-1e-5,rot))/(2e-5)
w=(exact(.05,.2,1e-5)-exact(.05,.2,-1e-5))/(2e-5)
rotation_gap=float(np.linalg.norm(r-rot@w@rot.T)/np.linalg.norm(w));assert rotation_gap<2e-8
def integrate(m,u,ne,method='DOP853',order=128,initial_s=True):
 bg=Background(m,order);x,w=leggauss(order);y=30*(1+x);w=30*w;f=1/(1+np.exp(y));norm=ON0/(w@(y**3*f));J=memory(y);nf=PchipInterpolator(u,ne)
 def weights(a):
  e=np.hypot(y,a*m/TNU_EV);chi=2/15*norm*w*y**5*f*(1-f)/e
  return chi,-chi*(a*m/TNU_EV/e)**2
 def energy(a,v):
  S,A,B,b=v.reshape(4,5);_,og,_,_,_=bg.coeff(a);chi,dc=weights(a)
  return 10*(S@S)/og+A@A+8/3*(B@B)+30*(chi@np.sum((b-J)**2,axis=1))/OG0
 def fun(t,y):
  a=A0*np.exp(t);H,og,oc,d,_=bg.coeff(a);k=C*SIG*float(nf(t))/H;chi,dc=weights(a)
  S,A,B,b=y[:20].reshape(4,5);pi=-chi@(b-J)
  R=np.stack([-(3+d)*S+.4*og*A+3*pi/(OG0/og),-4*S-k*(.9*A+.4*B),-k*(.15*A+.4*B),S])
  loss=20*(S@S)/og+k*(1.8*(A@A)+1.6*(A@B)+32/15*(B@B))-30*(dc@np.sum((b-J)**2,axis=1))/OG0
  return np.r_[R.ravel(),loss]
 initial=np.zeros(21);initial[1]=1. if initial_s else 0.
 sol=solve_ivp(fun,(u[0],u[-1]),initial,method=method,rtol=2e-10,atol=2e-12,max_step=.006,dense_output=True);assert sol.success
 t=np.linspace(u[0],u[-1],1025);v=sol.sol(t);ll=np.array([energy(A0*np.exp(z),x[:20]) for z,x in zip(t,v.T)])
 bal=float(abs(ll[-1]+v[-1,-1]-ll[0])/ll[0]);assert bal<2e-8 and max(np.diff(ll))/ll[0]<1e-11
 return dict(end=v[:20,-1].reshape(4,5).tolist(),balance=bal,initial_s=initial_s,series=np.vstack([t,v[:20],ll]))
results={};series={}
for name in ('q256','bass_cross'):
 a=hist[name][:,0];u=np.log(a/A0);u[0]=0.;u[-1]=np.log(21/5);ne=hist[name][:,6]
 rows=[]
 for m in masses:
  v=integrate(m,u,ne);series[name+'_'+str(m)]=v.pop('series')
  p0=radial(m,A0)[1];p1=radial(m,.2)[1]
  angle=float(np.degrees(np.arccos(np.clip(p0@p1/(np.linalg.norm(p0)*np.linalg.norm(p1)),-1,1))))
  row=dict(m=m,preferred_start=p0.tolist(),preferred_end=p1.tolist(),stf_angle_deg=angle,**v)
  rows.append(row);print(name,m,'angle',angle,'S',v['end'][0],'B',v['end'][2],flush=True)
 results[name]=rows
# separate zero-initial-shear source test and independent solver
a=hist['q256'][:,0];u=np.log(a/A0);u[0]=0.;u[-1]=np.log(21/5);ne=hist['q256'][:,6]
z=integrate(.05,u,ne,initial_s=False);series['zero_shear']=z.pop('series');assert np.linalg.norm(z['end'][0])>1e-6
r=integrate(.05,u,ne,method='Radau',order=256);r.pop('series')
ref=next(v for v in results['q256'] if v['m']==.05)
gap=float(np.max(abs(np.array(r['end'])-ref['end'])));assert gap<2e-8
np.savez_compressed(OUT/'SERIES.npz',**series)
out=dict(status='PASS_SCOPED_STF_MEMORY',native_rows=len(native),max_native_relative=max(native_err),angular_checks=checks,rotation_gap=rotation_gap,results=results,zero_initial_shear=z,independent_ode_gap=gap,source_hashes=sources,scope='linear homogeneous Bianchi I, conditional smooth FD initial STF memory, fixed actual ne histories, not observed CMB or nonlinear evolution')
(OUT/'RESULTS.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
