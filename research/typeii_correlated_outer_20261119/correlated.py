"""Type-II source-conditioned coherent-atom joint angle/frequency kernel.

Thermal Maxwell atom motion, Lorentz absorption, electric-dipole angular phase,
leading recoil; pairwise thermal-reversibility symmetrization on the finite grid.
Not the exact correlated, polarized, full quantum Hummer RII redistribution.
"""
from functools import lru_cache
from pathlib import Path
import math,sys
import numpy as np
from scipy.integrate import quad_vec,quad
from scipy.special import ndtr,wofz
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/"research/typeii_redistribution_phase_20261116"))
import redistribution as prev
from numpy.polynomial.hermite import hermgauss
NU0,H,C,KB,MH,A=prev.NU0,prev.H,prev.C,prev.KB,prev.MH,prev.A
def check(p,msg):
 if not bool(p):raise RuntimeError(msg)
def sphere6():
 n=np.array([[1.,0,0],[-1.,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]])
 return n,np.full(6,1/6)
def sphere14(invalid=False):
 if invalid:raise ValueError('invalid sky option')
 n6,w6=sphere6()
 diag=np.array([[x,y,z] for x in (-1.,1.) for y in (-1.,1.) for z in (-1.,1.)])/np.sqrt(3)
 n=np.vstack((n6,diag))
 w=np.r_[np.full(6,1/15),np.full(8,3/40)]
 check(abs(sum(w)-1)<1e-14,'sky integral')
 return n,w

def edges_for(X):
 if not np.isfinite(X) or X<20 or X>120:raise ValueError('outer support must be 20..120 Doppler widths')
 pos=np.r_[np.arange(0,4.001,.5),np.array([5.,6.,8.,10.,12.,16.,20.,25.,30.,40.,60.,80.,120.])]
 pos=np.unique(np.r_[pos[pos<X],X])
 return np.r_[-pos[::-1],pos[1:]]
def _quad_mass_interval(x,a,lo,hi):
 lo=max(lo,-11.);hi=min(hi,11.)
 if hi<=lo:return 0.
 def f(u):return np.exp(-u*u)*a/(np.pi*((x-u)**2+a*a))
 knots=[lo]+[v for v in (x-.1,x-10*a,x,x+10*a,x+.1) if lo<v<hi]+[hi]
 return sum(quad(f,l,r,epsabs=1e-12,epsrel=1e-9,limit=70)[0] for l,r in zip(knots[:-1],knots[1:]))
@lru_cache(maxsize=600)
def _cached(x,mu,a,edges):
 e=np.asarray(edges,float)
 if mu==1.:
  out=np.zeros(len(e)-1)
  j=int(np.searchsorted(e,x,'right')-1)
  if 0<=j<len(out):out[j]=1.
  return tuple(out)
 recoil=H*NU0/(MH*C*C*np.sqrt(2*KB*3000./(MH*C*C)))  # overwritten below by caller T-dependent scale
 # User-level kernel uses recoil argument to override; cached pair receives this tiny number in a custom encoding.
 return tuple(_integrated_conditional(x,mu,a,e,recoil))
def _integrated_conditional(x,mu,a,e,recoil):
 # Emitter velocity reduced by thermal speed sqrt(2kT/m); Maxwell density exp(-u^2).
 # After conditioning on Lorentzian absorption, outgoing frequency has
 # mean x+(mu-1)u - recoil*(1-mu) and transverse Gaussian variance (1-mu^2)/2.
 def f(u):return np.exp(-u*u)*a/(np.pi*((x-u)**2+a*a))
 norm=float(np.real(wofz(x+1j*a)))
 check(norm>0,'positive Voigt conditional normalization')
 if mu <= -1.+1e-13:
  out=np.empty(len(e)-1)
  for k,(lo,hi) in enumerate(zip(e[:-1],e[1:])):
   # x_out=x-2u-2 recoil, so u intervals are reversed.
   u0=(x-2*recoil-hi)/2;u1=(x-2*recoil-lo)/2
   out[k]=_quad_mass_interval(x,a,u0,u1)/norm
 else:
  sig=np.sqrt(max((1-mu*mu)/2,0))
  if sig<1e-12:
   out=np.zeros(len(e)-1);j=int(np.searchsorted(e,x,'right')-1)
   if 0<=j<len(out):out[j]=1.
  elif abs(x)>7.5:
   u,w=hermgauss(96)
   prob=w*a/(np.pi*((x-u)**2+a*a))
   means=x+(mu-1)*u-recoil*(1-mu)
   out=((ndtr((e[1:,None]-means[None,:])/sig)-ndtr((e[:-1,None]-means[None,:])/sig))*prob[None,:]).sum(axis=1)/sum(prob)
  else:
   def integrand(u):
    mean=x+(mu-1)*u-recoil*(1-mu)
    cdf=ndtr((e[1:]-mean)/sig)-ndtr((e[:-1]-mean)/sig)
    return f(u)*cdf
   vals,err=quad_vec(integrand,-11,11,points=[x] if -11<x<11 else None,epsabs=3e-10,epsrel=1e-7,limit=130)
   out=vals/norm
 out=np.maximum(out,0.)
 if np.sum(out)>1+2e-5:raise RuntimeError('conditional probability normalization exceeded')
 return out

def conditional_bins(x,mu,a,edges,recoil=0.):
 e=np.asarray(edges,float)
 if e.ndim!=1 or len(e)<2 or not np.isfinite(np.r_[x,mu,a,recoil,e]).all() or np.any(np.diff(e)<=0) or a<=0 or abs(mu)>1:raise ValueError('invalid conditional coherent scattering parameters')
 if mu>=1-1e-13:
  out=np.zeros(len(e)-1);j=int(np.searchsorted(e,x,'right')-1)
  if 0<=j<len(out):out[j]=1
  return out
 return _integrated_conditional(float(x),float(mu),float(a),e,float(recoil))

def raw_kernel(x,e,T,na,wa,idealized_factorized=False):
 """Conditional jump probability raw[dest_freq, dest_angle, src_freq, src_angle].
 Finite support may lose probability through unresolved true far edges; that
 probability is tracked separately, not silently renormalized to one.
 """
 x=np.asarray(x,float);e=np.asarray(e,float);na=np.asarray(na,float);wa=np.asarray(wa,float)
 NF=len(x);NA=len(wa)
 a=A/(4*np.pi*NU0*np.sqrt(2*KB*T/(MH*C*C)))
 recoil=H*NU0/(MH*C*C*np.sqrt(2*KB*T/(MH*C*C)))
 mu=na@na.T
 mu=np.clip(mu,-1,1)
 phase=.75*(1+mu*mu)
 ang=wa[:,None]*phase
 check(max(abs(ang.sum(axis=0)-1))<3e-13,'angular dipole normalization')
 # Exact finite list of pair-angle cosines for 6/14-direction quadratures.
 values={}
 for j in range(NF):
  for m in np.unique(np.round(mu,12)):
   if m>=1-1e-12:
    P=np.zeros(NF);P[j]=1
   else:
    P=conditional_bins(float(x[j]),float(m),float(a),e,float(recoil))
   values[(j,float(m))]=P
 raw=np.empty((NA,NF,NA,NF))
 for srca in range(NA):
  for dest in range(NA):
   mm=float(np.round(mu[dest,srca],12))
   for j in range(NF):
    raw[dest,:,srca,j]=ang[dest,srca]*values[(j,mm)]
 if idealized_factorized:
  # Preserve per-incoming-frequency marginal and per-incoming-angle dipole law,
  # eliminate the correlation between outgoing angle and outgoing frequency.
  for srca in range(NA):
   marg=raw[:,:,srca,:].sum(axis=0) # (NFdest,NFsrc)
   for dest in range(NA):
    raw[dest,:,srca,:]=ang[dest,srca]*marg
 return raw,{'a':float(a),'recoil':float(recoil),'distinct_mu':len(np.unique(np.round(mu,12))),
  'min_resolved_probability':float(raw.sum(axis=(0,1)).min()),
  'max_resolved_probability':float(raw.sum(axis=(0,1)).max())}

def matrix_kernel(z=1100.,X=40.,T=3000.,nl=2.5e8,angle_order=6,factorized=False):
 if angle_order==6:na,wa=sphere6()
 elif angle_order==14:na,wa=sphere14()
 else:raise ValueError('allowed six or fourteen positive sky nodes')
 e=edges_for(X);x=(e[:-1]+e[1:])/2;nf=len(x);na_count=len(wa)
 raw,meta=raw_kernel(x,e,T,na,wa,factorized)
 N=na_count*nf
 # Source-scoped original line cross-section rate, in atom local proper seconds.
 dn=NU0*np.sqrt(2*KB*T/(MH*C*C));nu=NU0+dn*x
 check(min(nu)>0,'positive physical frequency')
 rate,_=prev.medium_rates(nu,T,nl,0.)
 # Wien equilibrium weights integrate exact positive atomic mode density.
 dnu=np.diff(e)*dn
 cap=wa[:,None]*dnu[None,:]*nu[None,:]**2
 pi=cap*np.exp(-H*(nu[None,:]-NU0)/(KB*T))
 pi=pi.reshape(-1);pi/=sum(pi)
 Q=np.zeros((N,N))
 P=raw.reshape(N,N)
 for src in range(N):
  Q[:,src]=rate[src%nf]*P[:,src]
 np.fill_diagonal(Q,0.)
 # Raw source-weighted equilibrium flux requires a physical reversible correction
 # to include thermodynamic occupation and recoil; do not mislabel this exact RII.
 flow=(Q*pi[None,:]+Q.T*pi[:,None])/2
 Q=flow/pi[None,:]
 np.fill_diagonal(Q,-np.sum(Q,axis=0))
 db=0.
 for i in range(N):
  for j in range(i):
   db=max(db,abs(Q[i,j]*pi[j]-Q[j,i]*pi[i])/max(1e-200,Q[i,j]*pi[j]+Q[j,i]*pi[i]))
 # Factorization diagnostic: raw conditional exit probability changes with mu.
 rawfull,_=raw_kernel(x,e,T,na,wa,False)
 rawfact,_=raw_kernel(x,e,T,na,wa,True)
 discrepancy=float(np.max(np.sum(abs(rawfull-rawfact),axis=(0,1))))
 outer=abs(x)>20.;inner=~outer
 core=np.tile(inner,na_count)
 return dict(Q=Q,pi=pi,x=x,edges=e,na=na,wa=wa,rate=rate,
             cap=cap.reshape(-1),kernel_meta=meta,
             wien_detailed_balance_defect=db,
             column_defect=float(np.max(abs(Q.sum(axis=0)))/max(1.,max(abs(Q).sum(axis=0)))),
             factorization_gap=discrepancy,
             core_outward_rate=float(Q[np.ix_(~core,core)].sum()),
             core_return_rate=float(Q[np.ix_(core,~core)].sum()),
             core_mask=core,
             source_z=z,factorized=factorized,T=T)
def small_generator(z=1100.,xouter=40.,angle_order=6):
 return matrix_kernel(z=z,X=xouter,angle_order=angle_order)
