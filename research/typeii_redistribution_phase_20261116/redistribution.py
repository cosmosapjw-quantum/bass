"""Conservative source-conditioned resonant redistribution primitives.
Exact tetrad/phase-space transformations; declared factorized FP+Rayleigh
scattering approximation. Tagged packet evolution is dilute, not a solved
cosmological radiation/atom population system.
"""
from pathlib import Path
from functools import lru_cache
import ast,json,math,subprocess,sys
import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import PchipInterpolator
from scipy.linalg import eigh
from scipy.special import wofz
from numpy.polynomial.legendre import leggauss
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'research/typeii_lyman_transfer_20261116'))
import line_transfer as lt
H,C,KB,MH,NU0,A=lt.H,lt.C,lt.KB,lt.MH,lt.NU0,lt.ALYA
PARENT='0577ef0a40cf10130a5933eb52c7230d4de1f11b'
def check(ok,msg):
 if not bool(ok):raise RuntimeError(msg)
def bernoulli(x):
 x=np.asarray(x,float)
 if not np.isfinite(x).all():raise ValueError('finite exponential-fitting argument')
 out=np.empty_like(x);small=abs(x)<1e-4;hi=x>50;lo=x<-50;mid=~(small|hi|lo)
 out[small]=1-x[small]/2+x[small]**2/12-x[small]**4/720
 out[hi]=x[hi]*np.exp(-x[hi]);out[lo]=-x[lo];out[mid]=x[mid]/np.expm1(x[mid])
 return float(out) if out.ndim==0 else out
def thermal_flux(f,delta,stimulated=True):
 f=np.asarray(f,float);d=np.asarray(delta,float)
 if f.ndim!=1 or d.shape!=(len(f)-1,) or not np.isfinite(np.r_[f,d]).all() or min(f)<0:raise ValueError('nonnegative finite occupations with edge differences required')
 left,right=f[:-1],f[1:]
 return bernoulli(d)*left*(1+right if stimulated else 1)-bernoulli(-d)*right*(1+left if stimulated else 1)
def sphere(nmu=4,nphi=8):
 if not isinstance(nmu,int) or not isinstance(nphi,int) or nmu<2 or nphi<4:raise ValueError('sphere orders >=2,4')
 mu,w=leggauss(nmu);phi=2*np.pi*np.arange(nphi)/nphi
 yy=np.repeat(mu,nphi);az=np.tile(phi,nmu);rad=np.sqrt(1-yy*yy)
 return np.column_stack((rad*np.cos(az),yy,rad*np.sin(az))),np.repeat(w/2/nphi,nphi)
def valid_dirs(n,b):
 n=np.asarray(n,float)
 if n.ndim!=2 or n.shape[1]!=3 or not np.isfinite(n).all() or not np.isfinite(b) or abs(b)>=1 or max(abs(np.linalg.norm(n,axis=1)-1))>3e-10:raise ValueError('unit directions and subluminal velocity required')
 return n
def to_normal(ne,b):
 ne=valid_dirs(ne,b);G=1/np.sqrt(1-b*b);D=1/(G*(1+b*ne[:,1]));n=ne*D[:,None];n[:,1]=(ne[:,1]+b)/(1+b*ne[:,1]);return n,D
def to_atom(n,b):
 n=valid_dirs(n,b);G=1/np.sqrt(1-b*b);D=G*(1-b*n[:,1]);ne=n/D[:,None];ne[:,1]=(n[:,1]-b)/(1-b*n[:,1]);return ne,D
def angular_generator(ne,we,D):
 ne=valid_dirs(ne,0.);w=np.asarray(we,float);D=np.asarray(D,float)
 if w.shape!=(len(ne),) or D.shape!=w.shape or not np.isfinite(np.r_[w,D]).all() or min(w)<=0 or min(D)<=0:raise ValueError('positive finite quadrature weights/Doppler factors')
 W=.75*(1+(ne@ne.T)**2)
 Q=w[:,None]*W*D[None,:];np.fill_diagonal(Q,0);np.fill_diagonal(Q,-Q.sum(axis=0))
 pi=w/D;pi/=sum(pi)
 return Q,pi
def angular_step(N,Q,pi,exposure):
 N=np.asarray(N,float);s=np.sqrt(pi);x=np.asarray(exposure,float)
 if N.ndim!=2 or N.shape[0]!=len(pi) or x.shape!=(N.shape[1],) or not np.isfinite(N).all() or min(N.ravel())<-1e-14 or not np.isfinite(x).all() or min(x)<0:raise ValueError('invalid angular-step state or exposure')
 S=Q*s[None,:]/s[:,None];check(np.max(abs(S-S.T))<1e-12,'angular detailed-balance symmetry')
 ev,V=eigh((S+S.T)/2);check(ev[-1]<1e-12,'angular positive eigenvalue');ev[-1]=0.
 out=s[:,None]*(V@(np.exp(ev[:,None]*x[None,:])*(V.T@(N/s[:,None]))))
 check(np.min(out)>-1e-12*max(1.,np.max(N)),'angular exponential lost positivity')
 return out

def geometric_rhs(state,n):
 sp,sm,s13,N1,b=state;sr=np.sqrt(3)
 Sigma=np.array([[-2*sp,0,sr*s13],[0,sp+sr*sm,0],[sr*s13,0,sp-sr*sm]])
 Sn=n@Sigma.T;S=np.sum(n*Sn,axis=1);V=-Sn+S[:,None]*n
 V[:,0]+=sr*s13*n[:,2];V[:,2]-=sr*s13*n[:,0]
 V[:,1]-=N1*n[:,0]*n[:,2];V[:,2]+=N1*n[:,0]*n[:,1]
 return V,S,Sigma

@lru_cache(maxsize=1)
def background():
 paths=['compiler/validation/generate_typeii_fixture.py','compiler/validation/typeii_fixture_canonical.json','research/typeii_cascade_effective_20261116/SOURCE_TRACE_STATIONARY.csv','research/typeii_lyman_transfer_20261116/RESONANCE_FATES.csv','research/typeii_native_hyrec_expansion_20261102/R3_TYPEII_HUBBLE_GRID.json']
 locks={}
 for p in paths:
  actual=subprocess.check_output(['git','hash-object',p],cwd=ROOT,text=True).strip();want=subprocess.check_output(['git','rev-parse',PARENT+':'+p],cwd=ROOT,text=True).strip();check(actual==want,'parent source changed '+p);locks[p]=actual
 src=ROOT/paths[0];fn=[n for n in ast.parse(src.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='typeii_rhs'];check(len(fn)==1,'original RHS missing');env={'math':math};exec(compile(ast.Module(body=fn,type_ignores=[]),str(src),'exec'),env);rhs=env['typeii_rhs']
 fixture=json.loads((ROOT/paths[1]).read_text())['trajectory']['samples'];x0=np.asarray(fixture[0]['state']);H0=json.loads((ROOT/paths[4]).read_text())['H_anchor_source_FLRW_s_inverse']
 def ode(t,x):
  r=np.asarray(rhs(list(x[:5]),1.3));q=r[3]/x[3]+4*x[0];return np.r_[r,-1-q]
 end=np.log(1701/301);s=solve_ivp(ode,(0,end),np.r_[x0,np.log(H0)],method='DOP853',rtol=3e-12,atol=5e-14,max_step=.004,dense_output=True);check(s.success,'source geometry solve')
 overlap=np.max(abs(s.sol([x['tau'] for x in fixture])[:5].T-np.array([x['state'] for x in fixture])));check(overlap<2e-11,'original401 background overlap')
 tr=np.genfromtxt(ROOT/paths[2],delimiter=',',names=True);fa=np.genfromtxt(ROOT/paths[3],delimiter=',',names=True)
 tt=tr['tau_H'];tf=np.log(1701/(1+fa['z_mean']))
 data={'sol':s.sol,'rhs':rhs,'end':end,'x0':x0,'locks':locks,'overlap':float(overlap),'Tm':PchipInterpolator(tt,np.log(tr['Tm_K'])),'p1':PchipInterpolator(tt,np.log(tr['p1s'])),'pion':PchipInterpolator(tf,np.log(fa['p_ionization']))}
 return data

class Geometry:
 def __init__(self,t0,tend,nmu=4,nphi=8,normal_initial=None,weights=None):
  self.bg=background();self.t0=float(t0);self.tend=float(tend)
  if not 0<=t0<tend<=self.bg['end']:raise ValueError('interval outside source domain')
  b0=self.bg['sol'](t0)[4]
  if normal_initial is None:
   na,wa=sphere(nmu,nphi);nn,D0=to_normal(na,b0);wn0=wa*D0**2
  else:
   nn=valid_dirs(normal_initial,b0);wn0=np.asarray(weights,float)
   if wn0.shape!=(len(nn),) or not np.isfinite(wn0).all() or min(wn0)<=0:raise ValueError('initial weights')
  self.wn0=wn0;self.nang=len(nn)
  def ode(t,y):
   r=y.reshape(-1,5);V,S,Sigma=geometric_rhs(self.bg['sol'](t)[:5],r[:,:3]);return np.column_stack((V,-1-S,3*S)).ravel()
  initial=np.column_stack((nn,np.zeros((len(nn),2)))).ravel()
  s=solve_ivp(ode,(t0,tend),initial,method='DOP853',rtol=3e-12,atol=5e-14,max_step=.002,dense_output=True);check(s.success,'angular characteristics solve');self.sol=s.sol
 def at(self,t):
  if not self.t0-1e-12<=t<=self.tend+1e-12:raise ValueError('characteristic time outside interval')
  bg=self.bg;ss=bg['sol'](t);state=ss[:5];hn=np.exp(ss[5]);r=self.sol(t).reshape(-1,5);n=r[:,:3];na,D=to_atom(n,state[4]);out=lt.drift(state,bg['rhs'](list(state),1.3),n)
  J=np.exp(r[:,4]);we=self.wn0*J/D**2
  G=1/np.sqrt(1-state[4]**2);G0=1/np.sqrt(1-bg['x0'][4]**2);z=1701*np.exp(-t)-1
  nH=11.223846333047e-6*.0224*(1-.245)*1e6*(1+z)**3*G0/G
  return {'state':state,'H':hn,'n':n,'na':na,'D':D,'J':J,'we':we,'logEn':r[:,3],'kappa':out['kappa'],'L':out['L'],'Sigma':out['Sigma'],'Tm':float(np.exp(bg['Tm'](t))),'nl':float(nH*np.exp(bg['p1'](t))),'pion':float(np.exp(bg['pion'](t))),'z':float(z),'capacity_angle':np.exp(3*(t-self.t0))*self.wn0*J/D**3,'angular_weight_defect':float(abs(sum(we)-1))}

def fixed_grid(Tref,X=20.,cells=160):
 g=lt.line_grid(Tref,halfwidth=float(X),cells=int(cells));g['width']=np.diff(g['nu_edges']);g['cap']=g['width']*(g['nu_edges'][:-1]**2+g['nu_edges'][:-1]*g['nu_edges'][1:]+g['nu_edges'][1:]**2)/3
 return g

def medium_rates(nu,Tm,nl,pion):
 nu=np.asarray(nu,float)
 if not np.isfinite(np.r_[nu,Tm,nl,pion]).all() or min(nu)<=0 or Tm<=0 or nl<0 or not 0<=pion<=1:raise ValueError('invalid source scattering parameters')
 dn=NU0*np.sqrt(2*KB*Tm/(MH*C*C));a=A/(4*np.pi*dn);phi=np.real(wofz((nu-NU0)/dn+1j*a))/(np.sqrt(np.pi)*dn)
 R=3*nl*A*C**3/(8*np.pi*nu**2)*phi
 return R*(1-pion),R*pion*np.exp(H*(nu-NU0)/(KB*Tm))

def frequency_rates(g,Tm,nl,pion,absorbing=True):
 nu=g['nu'];edges=g['nu_edges'];cap=g['cap'];M=len(nu)
 rs,_=medium_rates(edges,Tm,nl,pion);Dnu=KB*Tm/(MH*C*C)*edges**2*rs
 up=np.zeros(M);down=np.zeros(M)
 delta=H*np.diff(nu)/(KB*Tm);K=Dnu[1:-1]*edges[1:-1]**2/np.diff(nu)
 up[:-1]=K*bernoulli(delta)/cap[:-1];down[1:]=K*bernoulli(-delta)/cap[1:]
 if absorbing:
  dl=nu[0]-edges[0];dr=edges[-1]-nu[-1]
  down[0]=Dnu[0]*edges[0]**2/dl*bernoulli(-H*dl/(KB*Tm))/cap[0]
  up[-1]=Dnu[-1]*edges[-1]**2/dr*bernoulli(H*dr/(KB*Tm))/cap[-1]
 return up,down

def backward_birth_death(N,up,down,kill,dt):
 """Positive tridiagonal solve with cancellation-free diagonal recurrence.
 Store r_i=Schur_diagonal_i-dt*up_i, so a stiff conservative diffusion's
 unit storage term is never recovered by subtracting two huge rates.
 """
 N=np.asarray(N,float);up=np.asarray(up,float);down=np.asarray(down,float);kill=np.asarray(kill,float)
 if N.shape!=up.shape or N.shape!=down.shape or N.shape!=kill.shape or N.ndim!=2 or not np.isfinite(np.r_[N.ravel(),up.ravel(),down.ravel(),kill.ravel(),dt]).all() or min(N.ravel())<-1e-13 or min(up.ravel())<0 or min(down.ravel())<0 or min(kill.ravel())<0 or dt<0:raise ValueError('invalid positive birth-death system')
 # Extended precision is used only in the small tridiagonal factorization.
 U=np.asarray(dt*up,dtype=np.longdouble);D=np.asarray(dt*down,dtype=np.longdouble);K=np.asarray(dt*kill,dtype=np.longdouble);b=np.asarray(N,dtype=np.longdouble).copy();diag=np.empty_like(b)
 r=1+D[:,0]+K[:,0];diag[:,0]=r+U[:,0]
 for i in range(1,N.shape[1]):
  denom=diag[:,i-1];b[:,i]+=U[:,i-1]/denom*b[:,i-1]
  r=1+K[:,i]+D[:,i]*r/denom;diag[:,i]=r+U[:,i]
 b[:,-1]/=diag[:,-1]
 for i in range(N.shape[1]-2,-1,-1):b[:,i]=(b[:,i]+D[:,i+1]*b[:,i+1])/diag[:,i]
 out=np.asarray(b,float);check(np.min(out)>-1e-12,'positive solve failed');return out
