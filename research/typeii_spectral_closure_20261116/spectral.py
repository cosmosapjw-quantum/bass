"""Electron-frame collision integrals for a prescribed boosted Planck field.
Exact local bulk boost; leading nonrelativistic Compton energy exchange.
Ground-state Verner photo cross sections are not HYREC effective n=2 rates.
Units: SI unless a name explicitly ends in eV. Photons are unpolarized.
"""
from pathlib import Path
from functools import lru_cache
import math,json,hashlib
import numpy as np
from numpy.polynomial.legendre import leggauss,legvander
from scipy.special import roots_laguerre,zeta
HERE=Path(__file__).resolve().parent
HPLANCK=6.62607015e-34;HBAR=HPLANCK/(2*np.pi);C=299792458.
KB=1.380649e-23;EV=1.602176634e-19;ME=9.1093837139e-31;SIGMAT=6.6524587051e-29
COEFF=np.array([1.,-6/5,1/2,-3/10])
def check(ok,msg):
 if not bool(ok):raise RuntimeError(msg)
def scalar_beta(b):
 b=float(b)
 if not np.isfinite(b) or abs(b)>=1:raise ValueError('finite |beta|<1 required')
 return b
def positive(x,name):
 a=np.asarray(x,float)
 if not np.isfinite(a).all() or np.any(a<=0):raise ValueError('positive finite '+name+' required')
 return a
@lru_cache(None)
def gauss(n):
 if not isinstance(n,int) or n<4 or n>512:raise ValueError('quadrature order outside 4..512')
 return leggauss(n)
@lru_cache(None)
def laguerre(n):
 if not isinstance(n,int) or n<8 or n>256:raise ValueError('Laguerre order outside 8..256')
 return roots_laguerre(n)
def bose(x):
 x=positive(x,'Planck exponent');return np.exp(-x)/(-np.expm1(-x))
def occupation(x,beta,mu):
 b=scalar_beta(beta);x=positive(x,'dimensionless energy');mu=np.asarray(mu,float)
 if not np.isfinite(mu).all() or np.any(abs(mu)>1):raise ValueError('direction outside sphere')
 return bose(x*(1+b*mu)/np.sqrt(1-b*b))
def multipoles(x,beta,nmu=48):
 b=scalar_beta(beta);x=np.atleast_1d(positive(x,'dimensionless energy'));mu,w=gauss(nmu)
 n=occupation(x[:,None],b,mu[None,:]);return n@(w[:,None]*legvander(mu,3)/2)
def log1mexp(x):
 x=positive(x,'log exponent')
 with np.errstate(divide='ignore',invalid='ignore'):
  return np.where(x<np.log(2),np.log(-np.expm1(-x)),np.log1p(-np.exp(-x)))
def monopole(x,beta):
 b=abs(scalar_beta(beta));a=positive(x,'dimensionless energy')
 if b<1e-5:
  result=multipoles(np.ravel(a),b,48)[:,0].reshape(a.shape)
 else:
  g=1/np.sqrt(1-b*b);result=(log1mexp(a*g*(1+b))-log1mexp(a*g*(1-b)))/(2*a*g*b)
 return result
def induced(bl):
 a=np.asarray(bl,float)
 if a.shape[-1]!=4 or not np.isfinite(a).all():raise ValueError('four finite occupation multipoles required')
 return np.sum(COEFF*a*a,axis=-1)
def direct_pair(x,beta,nmu=20,nphi=32,recoil_eta=None):
 """Independent pair-direction integral, optional exact cold-electron KN recoil.
 recoil_eta=E/(m_ec^2): return heating normalized by E*eta, per photon density factor.
 At eta->0 the result is b0+S; with None return only induced S.
 """
 b=scalar_beta(beta);x=float(positive(x,'energy'));mu,w=gauss(nmu);w=w/2
 ph=np.arange(nphi)*2*np.pi/nphi
 q=mu[:,None,None]*mu[None,:,None]+np.sqrt(1-mu[:,None,None]**2)*np.sqrt(1-mu[None,:,None]**2)*np.cos(ph)[None,None,:]
 ni=occupation(x,b,mu)[:,None,None]
 weight=w[:,None,None]*w[None,:,None]/nphi
 if recoil_eta is None:
  nj=occupation(x,b,mu)[None,:,None]
  val=.75*(1+q*q)*(1-q)*ni*nj
 else:
  e=float(positive(recoil_eta,'recoil energy'));ratio=1/(1+e*(1-q))
  kn=.75*ratio**2*(ratio+1/ratio-1+q*q)
  nj=occupation(x*ratio,b,mu[None,:,None])
  val=kn*ni*(1+nj)*(1-q)*ratio
 return float(np.sum(weight*val))
def compton(beta,nmu=48,nx=160):
 b=scalar_beta(beta);g=1/np.sqrt(1-b*b)
 a,w=gauss(nx);cut=60/(g*(1-abs(b)));x=.5*cut*(a+1);wx=.5*cut*w
 bl=multipoles(x,b,nmu);S=induced(bl)
 if min(S)<-1e-12:raise RuntimeError('stimulated recoil positivity violated')
 # Analytic single-spectrum moments; independent numeric moments in unit tests.
 ur=g*g*(1+b*b/3);I3=np.pi**4/15*ur
 Isp=24*zeta(5)*g**3*(1+b*b)
 Iind=float(np.sum(wx*x**4*S));Iind_mono=float(np.sum(wx*x**4*bl[:,0]**2))
 return {'energy_ratio':float(ur),'number_ratio':float(g),
         'Tc_ratio':float((Isp+Iind)/(4*I3)),
         'spontaneous_Tc_ratio':float(Isp/(4*I3)),
         'monopole_squared_Tc_ratio':float((Isp+Iind_mono)/(4*I3)),
         'I3':float(I3),'I4_spontaneous':float(Isp),'I4_induced':Iind,
         'I4_wrong_monopole_induced':Iind_mono}
def heating_per_electron(Tm,Tn,beta):
 tm=float(positive(Tm,'electron temperature'));tn=float(positive(Tn,'radiation temperature'))
 if KB*max(tm,tn)/(ME*C*C)>1e-3:raise ValueError('nonrelativistic thermal domain exceeded')
 r=compton(beta);U=8*np.pi*(KB*tn)**4/(HPLANCK**3*C**3)*r['I3']
 return 4*SIGMAT*C*KB*U/(ME*C*C)*(tn*r['Tc_ratio']-tm)

def load_parameters():
 source=json.loads((HERE/'SOURCES.json').read_text())
 row=next(x for x in source['photo_cross_sections'] if x['file']=='photo.dat')
 check(hashlib.sha256((HERE/'sources/photo.dat').read_bytes()).hexdigest()==row['sha256'],'photo table identity')
 table=np.loadtxt(HERE/'sources/photo.dat');mapping={}
 for name,Z,N in [('HI',1,1),('HeI',2,2),('HeII',2,1)]:
  a=table[(table[:,0]==Z)&(table[:,1]==N)];check(a.shape==(1,11),'missing Verner species')
  keys=['threshold_eV','Emax_eV','E0_eV','sigma0_Mb','ya','P','yw','y0','y1']
  mapping[name]=dict(zip(keys,map(float,a[0,2:])));mapping[name].update(Z=Z,N=N)
 return mapping
PARAMS=load_parameters()
def cross_section(species,energy_eV):
 if species not in PARAMS:raise ValueError('unsupported ground-state species')
 E=positive(energy_eV,'photon energy eV');p=PARAMS[species]
 if np.any(E>p['Emax_eV']):raise ValueError('outside tabulated fit validity')
 x=E/p['E0_eV']-p['y0'];y=np.sqrt(x*x+p['y1']**2)
 # Evaluation below threshold is masked, not extrapolated as a physical cross section.
 with np.errstate(invalid='ignore',divide='ignore',over='ignore'):
  val=p['sigma0_Mb']*1e-22*((x-1)**2+p['yw']**2)*y**(.5*p['P']-5.5)/(1+np.sqrt(y/p['ya']))**p['P']
 return np.where(E>=p['threshold_eV'],val,0.)
def photo_rate(species,Tn,beta,ne=64,nmu=64):
 if species not in PARAMS:raise ValueError('unsupported ground-state species')
 T=float(positive(Tn,'radiation temperature'));b=scalar_beta(beta)
 kt=KB*T/EV;chi=PARAMS[species]['threshold_eV'];g=1/np.sqrt(1-b*b)
 amin=g*(1-abs(b));x0=chi/kt;t,w=laguerre(ne);mu,wm=gauss(nmu)
 E=chi+kt/amin*t
 if max(E)>PARAMS[species]['Emax_eV']:raise ValueError('photo quadrature outside cross-section fit')
 angular_a=g*(1+b*mu)
 exponent=-(angular_a[None,:]-amin)*x0-(angular_a[None,:]/amin-1)*t[:,None]
 den=-np.expm1(-angular_a[None,:]*(x0+t[:,None]/amin))
 scaled=(np.exp(exponent)/den)@(wm/2)
 values=E**2*cross_section(species,E)*scaled
 integral=float(np.dot(w,values));heat_integral=float(np.dot(w,values*(E-chi)))
 check(integral>0 and heat_integral>0,'scaled photo integral nonpositive')
 logpref=np.log(8*np.pi*EV**3/(HPLANCK**3*C*C)*kt/amin)-amin*x0
 lr=logpref+np.log(integral);lh=logpref+np.log(heat_integral*EV)
 return {'rate_s':float(np.exp(lr)),'log_rate_s':float(lr),'heating_W':float(np.exp(lh)),
         'log_heating_W':float(lh),'mean_excess_eV':float(heat_integral/integral),
         'threshold_eV':chi,'scaled_integral':integral}
