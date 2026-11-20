"""Original Hummer RII0 static gas-frame finite transition matrix and wing tails.

Source joint redistribution is evaluated by independent analytic Voigt-Hummer
kernel. Recoil/thermal pair symmetrization is a separately labelled option,
not a claim about the exact recoil quantum scattering amplitude.
"""
import sys,math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'research/typeii_correlated_outer_20261119'))
import correlated as src
import hummer_rii as h

def check(ok,msg):
 if not bool(ok):raise RuntimeError(msg)
def extended_edges(X):
 if not np.isfinite(X) or not 20<=X<=480:raise ValueError('outer wing 20..480')
 pts=np.r_[np.arange(0.,4.001,.5),[5.,6.,8.,10.,12.,16.,20.,25.,30.,40.,60.,80.,120.,160.,240.,320.,480.]]
 pts=np.unique(np.r_[pts[pts<X],X])
 return np.r_[-pts[::-1],pts[1:]]
def raw_hummer(x,edges,T,na,wa,factorized=False):
 x=np.asarray(x,float);edges=np.asarray(edges,float)
 if len(edges)!=len(x)+1 or np.any(np.diff(edges)<=0) or T<=0:raise ValueError('bad frequency support')
 a=src.A/(4*np.pi*src.NU0*np.sqrt(2*src.KB*T/(src.MH*src.C**2)))
 mu=np.round(np.clip(na@na.T,-1,1),12)
 ang=wa[:,None]*.75*(1+mu**2)
 na_count=len(wa);nf=len(x)
 raw=np.empty((na_count,nf,na_count,nf))
 cache={}
 for j,xin in enumerate(x):
  for mm in np.unique(mu):
   cache[j,float(mm)]=h.conditional_bins(float(xin),float(mm),float(a),edges)
 for ai in range(na_count):
  for ao in range(na_count):
   m=float(mu[ao,ai])
   for j in range(nf):
    raw[ao,:,ai,j]=ang[ao,ai]*cache[j,m]
 if factorized:
  for ai in range(na_count):
   marg=raw[:,:,ai,:].sum(axis=0)
   for ao in range(na_count):raw[ao,:,ai,:]=ang[ao,ai]*marg
 sums=raw.sum(axis=(0,1))
 check(np.isfinite(raw).all() and raw.min()>=0 and np.max(sums)<=1+2e-4,'raw Hummer positive normalized')
 return raw,{'a':float(a),'recoil':0.0,'angular_nodes':na_count,'frequency_nodes':nf,'finite_mass_min':float(np.min(sums)),
             'finite_mass_max':float(np.max(sums)),'model':'HUMMER_II_CLASSICAL_NO_RECOIL'}
def matrix_kernel(z=1100.,X=40.,T=3000.,nl=2.5e8,angle_order=6,
                  factorized=False,thermo_sym=True):
 if angle_order==6:na,wa=src.sphere6()
 elif angle_order==14:na,wa=src.sphere14()
 else:raise ValueError('allowed 6 or 14 nodes')
 if not np.isfinite(nl) or nl<0:raise ValueError('positive source density')
 e=extended_edges(X);x=(e[:-1]+e[1:])/2;nf=len(x);aa=len(wa)
 raw,meta=raw_hummer(x,e,T,na,wa,factorized)
 nu=src.NU0+src.NU0*np.sqrt(2*src.KB*T/(src.MH*src.C*src.C))*x
 rate,_=src.prev.medium_rates(nu,T,nl,0.)
 dnu=np.diff(e)*src.NU0*np.sqrt(2*src.KB*T/(src.MH*src.C*src.C))
 cap=wa[:,None]*dnu[None,:]*nu[None,:]**2
 pi=(cap*np.exp(-src.H*(nu[None,:]-src.NU0)/(src.KB*T))).reshape(-1)
 pi/=sum(pi)
 NN=aa*nf;P=raw.reshape(NN,NN)
 Q=P*rate[np.arange(NN)%nf][None,:]
 np.fill_diagonal(Q,0)
 if thermo_sym:
  flux=(Q*pi[None,:]+Q.T*pi[:,None])/2
  Q=flux/pi[None,:]
 np.fill_diagonal(Q,-np.sum(Q,axis=0))
 db=float(np.max(abs(Q*pi[None,:]-(Q*pi[None,:]).T))/max(1e-300,np.max(abs(Q*pi[None,:]))))
 rawfull,_=raw_hummer(x,e,T,na,wa,False)
 rawfact,_=raw_hummer(x,e,T,na,wa,True)
 gap=float(np.max(np.sum(abs(rawfull-rawfact),axis=(0,1))))
 inside=np.tile(abs(x)<=20,aa)
 return dict(Q=Q,pi=pi,x=x,edges=e,na=na,wa=wa,rate=rate,
  cap=cap.reshape(-1),kernel_meta=meta,wien_detailed_balance_defect=db,
  column_defect=float(np.max(abs(Q.sum(axis=0)))/max(1.,np.max(abs(Q).sum(axis=0)))),
  factorization_gap=gap,core_outward_rate=float(Q[np.ix_(~inside,inside)].sum()),
  core_return_rate=float(Q[np.ix_(inside,~inside)].sum()),core_mask=inside,
  source_z=z,factorized=factorized,T=T,thermo_sym=thermo_sym)
def scattering_tails(g):
 # True finite-domain terminal mass from the original exact no-recoil conditional.
 x=g['x'];edges=g['edges'];na=g['na'];wa=g['wa'];T=g['T']
 a=src.A/(4*np.pi*src.NU0*np.sqrt(2*src.KB*T/(src.MH*src.C**2)))
 mm=np.round(np.clip(na@na.T,-1,1),12)
 nr=len(wa);nf=len(x)
 red=np.zeros((nr,nf));blue=np.zeros((nr,nf))
 tail_edges=np.array([-1.e5,edges[0],edges[-1],1.e5])
 cache={}
 for j,xx in enumerate(x):
  for mu in np.unique(mm):
   b=h.conditional_bins(float(xx),float(mu),float(a),tail_edges)
   cache[j,float(mu)]=(b[0],b[-1])
 for srca in range(nr):
  for desta in range(nr):
   weight=wa[desta]*.75*(1+mm[desta,srca]**2)
   for j in range(nf):
    r,b=cache[j,float(mm[desta,srca])]
    red[srca,j]+=weight*r
    blue[srca,j]+=weight*b
 if np.any(red+blue>1+1e-6) or np.min(red)<0 or np.min(blue)<0:raise RuntimeError('unphysical finite tails')
 return red.reshape(-1),blue.reshape(-1)
