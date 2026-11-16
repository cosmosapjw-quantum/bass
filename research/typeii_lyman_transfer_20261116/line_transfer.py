"""Frozen local Lyman line interface and source directional frequency flow.
Exact local Doppler/frame identities; finite-band, narrow-line transfer model.
No generic cosmological escape or redistribution-accuracy claim.
"""
from pathlib import Path
from functools import lru_cache
import sys,math
import numpy as np
from scipy.special import wofz,erf
from numpy.polynomial.legendre import leggauss
ROOT=Path(__file__).resolve().parent.parents[1]
sys.path.insert(0,str(ROOT/'research/typeii_cascade_effective_20261116'))
import cascade
H,C,KB,EV=cascade.H,cascade.C,cascade.KB,cascade.EV
MH=1.6735575e-27  # specified translational atomic mass, kg; not a new isotope precision claim
E0=cascade.bf.level((1,0))['chi']-cascade.bf.level((2,1))['chi']
NU0=E0/H;ALYA=cascade.einstein_A((2,1),(1,0));GRATIO=3.

def check(ok,msg):
 if not bool(ok):raise RuntimeError(msg)

def planck(x):
 x=np.asarray(x,float)
 if not np.isfinite(x).all() or np.any(x<=0):raise ValueError('positive finite spectral argument')
 return np.exp(-x)/(-np.expm1(-x))

def drift(state,rhs,n):
 s=np.asarray(state,float);d=np.asarray(rhs,float);n=np.asarray(n,float)
 if s.shape!=(5,) or d.shape!=(5,) or n.ndim!=2 or n.shape[1]!=3 or not np.isfinite(np.r_[s,d,n.ravel()]).all() or abs(s[4])>=1 or np.max(abs(np.linalg.norm(n,axis=1)-1))>3e-10:raise ValueError('invalid TypeII drift state/directions')
 sp,sm,s13,N1,b=s;bp=d[4];sr=np.sqrt(3)
 Sigma=np.array([[-2*sp,0,sr*s13],[0,sp+sr*sm,0],[sr*s13,0,sp-sr*sm]])
 snn=np.einsum('ij,jk,ik->i',n,Sigma,n);nx,ny,nz=n.T
 nyp=(snn-Sigma[1,1])*ny-N1*nx*nz
 G=1/np.sqrt(1-b*b);L=b*bp/(1-b*b);q=1-b*ny;D=G*q
 kappa=1+snn-L+(bp*ny+b*nyp)/q
 ev=np.linalg.eigvalsh(Sigma)
 lower=1+ev[0]-abs(L)-(abs(bp)+abs(b)*(ev[-1]-ev[0]+abs(N1)/2))/(1-abs(b))
 return {'D':D,'kappa':kappa,'normal_redshift':1+snn,'L':L,'nyprime':nyp,'all_sky_lower_bound':float(lower),'Sigma':Sigma,'Gamma':G}

def sobolev(tau):
 a=np.asarray(tau,float)
 if not np.isfinite(a).all() or np.any(a<0):raise ValueError('nonnegative finite optical depth required')
 ans=np.ones_like(a);np.divide(-np.expm1(-a),a,out=ans,where=a!=0)
 return float(ans) if ans.ndim==0 else ans

@lru_cache(maxsize=20)
def gauss(n):return leggauss(n)

def profile_masses(edges,a,order=12):
 e=np.asarray(edges,float)
 if e.ndim!=1 or len(e)<2 or not np.isfinite(e).all() or np.any(np.diff(e)<=0) or not np.isfinite(a) or a<0 or not isinstance(order,int) or order<4:raise ValueError('invalid profile support/width')
 if a==0:return .5*np.diff(erf(e))
 q,w=gauss(order);dx=np.diff(e);x=e[:-1,None]+dx[:,None]*(q+1)/2
 return .5*dx*(np.real(wofz(x+1j*a))/np.sqrt(np.pi)@w)

def line_grid(Tm,halfwidth=20.,cells=128,damping=True):
 if not np.isfinite([Tm,halfwidth]).all() or Tm<=0 or halfwidth<=0 or not isinstance(cells,int) or cells<4:raise ValueError('bad line band')
 eps=np.sqrt(2*KB*Tm/(MH*C*C));dn=NU0*eps
 if eps*halfwidth>.05:raise ValueError('band outside 5 percent local narrow-line support')
 edges=np.linspace(-halfwidth,halfwidth,cells+1);x=(edges[:-1]+edges[1:])/2
 nue=NU0+dn*edges;nu=NU0+dn*x;a=ALYA/(4*np.pi*dn) if damping else 0.
 prob=profile_masses(edges,a)
 # Integrated cell mode capacity uses a difference-of-cubes factorization.
 cap=8*np.pi/(3*C**3)*np.diff(nue)*(nue[:-1]**2+nue[:-1]*nue[1:]+nue[1:]**2)
 return {'x':x,'edges':edges,'nu':nu,'nu_edges':nue,'p':prob,'capacity':cap,'epsilon':eps,'dnu':dn,'a':a,'E0':E0,'A':ALYA,'band_mass':float(sum(prob)),'halfwidth':halfwidth}

def coefficients(grid,nl,nu,Tm,thermal=True):
 if not np.isfinite([nl,nu,Tm]).all() or min(nl,nu)<0 or Tm<=0:raise ValueError('invalid population/temperature')
 if np.any(grid['capacity']<=0) or not np.isfinite(grid['capacity']).all():raise ValueError('bad mode capacity')
 det=H*grid['nu']-grid['E0']
 corr=np.exp(det/(KB*Tm)) if thermal else np.ones_like(det)
 j=grid['A']*grid['p']*nu
 k=grid['A']*grid['p']*(GRATIO*nl*corr-nu)/grid['capacity']
 return j,k,corr

def collision(grid,nl,nu,occ,Tm,thermal=True):
 f=np.asarray(occ,float)
 if f.shape!=grid['nu'].shape or not np.isfinite(f).all() or np.any(f<0):raise ValueError('nonnegative finite bin occupations required')
 j,k,corr=coefficients(grid,nl,nu,Tm,thermal)
 fw=grid['A']*grid['p']*nu*(1+f);rv=grid['A']*grid['p']*GRATIO*nl*corr*f
 F=fw-rv;dn=-float(sum(F));ph=float(np.dot(H*grid['nu'],F));at=grid['E0']*dn
 kin=float(np.dot(grid['E0']-H*grid['nu'],F));gross=float(np.dot(H*grid['nu'],fw+rv))
 bal=float(np.max(abs(F)/np.maximum(fw+rv,1e-300)))
 return {'F':F,'dnu':dn,'dnl':-dn,'photon_energy':ph,'bound_energy':at,'kinetic_energy':kin,'energy_residual':ph+at+kin,'gross_energy':gross,'balance_relative':bal}

def singleflight(emission_weights,cell_tau):
 p=np.asarray(emission_weights,float);t=np.asarray(cell_tau,float)
 if p.ndim!=1 or t.shape!=p.shape or not np.isfinite(np.r_[p,t]).all() or np.any(p<0) or np.any(t<0) or sum(p)>1+2e-10:raise ValueError('finite emitted probability weights and nonnegative depth required')
 red=np.r_[0.,np.cumsum(t[:-1])]
 # Within each constant cell emissivity per optical depth is constant.
 return float(np.sum(p*np.exp(-red)*sobolev(t)))

def frozen_steady(grid,nl,nu,Tm,Hray,fblue=0.,thermal=True):
 """Upwind conservative photon count, frozen local narrow-line rest volume.
 Not the full expanding phase-space/angular measure. O(line width/nu0)
 geometric-volume corrections are outside this specific local diagnostic.
 """
 if not np.isfinite([Hray,fblue]).all() or Hray<=0 or fblue<0:raise ValueError('monotonic red drift and nonnegative blue boundary required')
 j,k,c=coefficients(grid,nl,nu,Tm,thermal)
 if np.any(k<0):raise ValueError('population inversion outside passive transport')
 edges=grid['edges'];dx=np.diff(edges);speed=Hray*grid['nu_edges']/grid['dnu']
 a=speed[:-1]/dx
 blue=speed[-1]*(8*np.pi*grid['nu_edges'][-1]**2*grid['dnu']/C**3)*fblue
 N=np.zeros(len(j));incoming=blue
 for i in range(len(j)-1,-1,-1):
  N[i]=(incoming+j[i])/(a[i]+k[i]);incoming=a[i]*N[i]
 flux=a*N;collision_count=j-k*N
 # Conservative transport energy includes resolved redshift work and edge energies.
 energies=H*grid['nu'];Ered=H*grid['nu_edges'][0];Eblue=H*grid['nu_edges'][-1]
 work=float(np.dot(energies[:-1]-energies[1:],flux[1:])+(Ered-energies[0])*flux[0]+(energies[-1]-Eblue)*blue)
 net=float(sum(collision_count));gross=float(sum(j)+sum(k*N)+blue+flux[0])
 return {'N':N,'f':N/grid['capacity'],'red_out':float(flux[0]),'blue_in':float(blue),'net_line_emission':net,'number_residual':float(net+blue-flux[0]),'gross_number':gross,'geometric_redshift_work':work,'energy_residual':float(np.dot(energies,collision_count)+work+Eblue*blue-Ered*flux[0]),'A_eff_net_over_nu':net/nu if nu>0 else 0.,'absorption_depths':k/a}

def attach_cascade(net,p,grid,occupations,Tm,ntrace):
 """Replace exactly one old imposed-bath Ly-alpha edge by line-photon exchange.
 The output atom source is per tracer fraction; photon/energy are proper volume.
 The old line is removed before adding the new one, never multiplied onto a
 cascade-effective rate. No population re-integration is claimed here.
 """
 pp=np.asarray(p,float)
 if pp.shape!=(7,) or not np.isfinite(pp).all() or min(pp)<0 or not np.isfinite(ntrace) or ntrace<=0:raise ValueError('bad tracer/line source')
 old=next(x for x in net['channels'] if x['upper']==(2,1) and x['lower']==(1,0))
 F_old=pp[2]*old['down']-pp[0]*old['up'];dp=net['Q']@pp
 dp=dp.copy();dp[0]-=F_old;dp[2]+=F_old
 out=collision(grid,ntrace*pp[0],ntrace*pp[2],occupations,Tm)
 dp[0]+=out['dnl']/ntrace;dp[2]+=out['dnu']/ntrace
 return {'population_derivative_proper':dp,'line':out,'removed_old_flux_per_atom':float(F_old),'nucleus_residual':float(sum(dp))}
