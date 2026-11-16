"""Electron-rest ground-state photoionization and leading Compton energy moment.
SI units except the explicitly eV-input Verner fit. A prescribed normal Planck
field is Lorentz transformed; this is not a multilevel recombination solver.
Compton: isotropic nonrelativistic thermal electrons, unpolarized photons,
leading recoil/thermal orders including the angular induced-scattering term.
"""
from pathlib import Path
from functools import lru_cache
import math
import numpy as np
from numpy.polynomial.legendre import leggauss,legvander
from scipy.special import zeta,logsumexp

H=6.62607015e-34
HBAR=H/(2*np.pi)
C=299792458.0
KB=1.380649e-23
EV=1.602176634e-19
ME=9.1093837139e-31
SIGMA_T=6.6524587e-29  # inherited BASS source value, m^2
CG=8*np.pi/(H**3*C**3)
U_PLANCK=np.pi**4/15
N_PLANCK=2*zeta(3)
SPECIES={'HI':(1,1),'HeI':(2,2),'HeII':(2,1)}
_table=np.loadtxt(Path(__file__).with_name('sources')/'photo.dat')
PARAMS={}
for key,(Z,Ne) in SPECIES.items():
    rows=_table[(_table[:,0]==Z)&(_table[:,1]==Ne)]
    if len(rows)!=1:raise RuntimeError('source cross-section row not unique: '+key)
    PARAMS[key]=tuple(float(x) for x in rows[0,2:])

def validate(T,beta):
    if not np.isfinite(T) or T<=0:raise ValueError('T must be positive and finite')
    if not np.isfinite(beta) or abs(beta)>.2:raise ValueError('implemented quadrature scope is |beta|<=0.2')
    return float(T),float(beta)

@lru_cache(maxsize=24)
def gauss(n):
    if not isinstance(n,(int,np.integer)) or n<8 or n>256:raise ValueError('quadrature order must be integer 8..256')
    x,w=leggauss(n);x.setflags(write=False);w.setflags(write=False)
    return x,w

def sigma_ev(energy,species):
    if species not in PARAMS:raise ValueError('unsupported ground-state species')
    e=np.asarray(energy,dtype=float)
    if not np.isfinite(e).all() or np.any(e<0):raise ValueError('invalid photon energy')
    eth,emax,e0,s0,ya,p,yw,y0,y1=PARAMS[species]
    if np.any(e>emax):raise ValueError('energy outside source fit validity')
    active=e>=eth
    es=np.maximum(e,eth)
    x=es/e0-y0;y=np.sqrt(x*x+y1*y1)
    sig=s0*((x-1)**2+yw*yw)*y**(.5*p-5.5)*(1+np.sqrt(y/ya))**(-p)*1e-22
    return np.where(active,sig,0.)

def photo_rate(Tn,beta,species,order=64,angular_order=32):
    Tn,beta=validate(Tn,beta)
    if species not in PARAMS:raise ValueError('unsupported species')
    mu,mw=gauss(angular_order);q,qw=gauss(order)
    y=40*(q+1);wy=40*qw
    g=1/np.sqrt(1-beta*beta)
    temp=Tn/(g*(1+beta*mu))
    thot=Tn*np.sqrt((1+abs(beta))/(1-abs(beta)))
    eth=PARAMS[species][0]*EV
    E=eth+KB*thot*y
    sig=sigma_ev(E/EV,species)
    expo=E[:,None]/(KB*temp[None,:])
    shift=eth/(KB*thot)
    # Factor the hottest threshold occupation out of the Wien tail.
    occ=np.exp(shift-expo)/(-np.expm1(-expo))
    monopole=occ@(mw/2)
    measure=wy*(KB*thot)*E*E*sig*monopole
    integral=float(np.sum(measure))
    if not np.isfinite(integral) or integral<=0:raise RuntimeError('photo rate scaled integral invalid')
    lograte=math.log(8*np.pi/(H**3*C**2))+math.log(integral)-shift
    mean=float(np.sum(measure*(E-eth))/integral)
    return {'log_rate_s':lograte,'rate_s':float(np.exp(lograte)),
            'mean_excess_J':mean,'mean_excess_eV':mean/EV,
            'log_photoheat_W':lograte+math.log(mean),'proper_target_frame':True}

def photo_rate_normal(Tn,beta,species,order=64,angular_order=32):
    Tn,beta=validate(Tn,beta)
    mu,w=gauss(angular_order);g=1/np.sqrt(1-beta*beta)
    D=g*(1-beta*mu)
    log_rates=np.array([photo_rate(Tn*d,0.,species,order=order)['log_rate_s'] for d in D])
    logR=float(logsumexp(log_rates+np.log(w/2)-2*np.log(D)))
    return {'log_rate_s':logR,'rate_s':float(np.exp(logR)),
            'frame':'normal integration with energy transform and aberration'}

def occupation(x,beta=0.,eta=0.,angular_order=32):
    validate(1.,beta)
    if not np.isfinite(eta) or eta<0:raise ValueError('eta must be nonnegative')
    x=np.asarray(x,float)
    if not np.isfinite(x).all() or np.any(x<=0):raise ValueError('x must be positive')
    mu,w=gauss(angular_order);g=1/np.sqrt(1-beta*beta)
    a=x[...,None]*g*(1+beta*mu)+eta
    f=np.exp(-a)/(-np.expm1(-a))
    return f,mu,w/2

def induced_multipoles(f,mu,w):
    f=np.asarray(f,float);mu=np.asarray(mu,float);w=np.asarray(w,float)
    if f.shape[-1]!=len(mu) or len(mu)!=len(w):raise ValueError('angular shape mismatch')
    if not np.isfinite(f).all() or np.any(f<0):raise ValueError('occupation must be finite nonnegative')
    pl=legvander(mu,3)
    nl=f@(w[:,None]*pl)
    return np.sum(nl*nl*np.array([1.,-1.2,.5,-.3]),axis=-1)

def induced_pair(f,mu,w):
    f=np.asarray(f,float);mu=np.asarray(mu,float);w=np.asarray(w,float)
    if f.ndim!=1 or f.shape!=mu.shape or w.shape!=mu.shape:raise ValueError('one-frequency angular vector required')
    if not np.isfinite(f).all() or np.any(f<0):raise ValueError('invalid occupation')
    a=mu[:,None]*mu[None,:]
    b=(1-mu[:,None]**2)*(1-mu[None,:]**2)
    kernel=.75*(1-a+a*a+.5*b-a*a*a-1.5*a*b)
    fw=f*w
    return float(fw@kernel@fw)

@lru_cache(maxsize=12)
def frequency_grid(order=28):
    q,w=gauss(order);edges=(0.,.01,.1,1.,4.,12.,30.,60.,100.)
    xs=[];ws=[]
    for a,b in zip(edges[:-1],edges[1:]):
        xs.append(a+.5*(b-a)*(q+1));ws.append(.5*(b-a)*w)
    return np.concatenate(xs),np.concatenate(ws)

def compton_moments(beta,eta=0.,order=28,angular_order=32):
    validate(1.,beta)
    if not np.isfinite(eta) or eta<0:raise ValueError('invalid chemical-potential parameter')
    x0,w0=frequency_grid(order)
    scale=np.sqrt((1+abs(beta))/(1-abs(beta)))
    x=x0*scale;w=w0*scale
    f,mu,mw=occupation(x,beta,eta,angular_order)
    n0=f@mw;B=induced_multipoles(f,mu,mw)
    # Allow only roundoff-sized cancellation in the Legendre representation.
    if np.min(B)<-1e-12*np.max(f*f):raise RuntimeError('negative induced scattering bilinear')
    number=float(np.sum(w*x*x*n0));U=float(np.sum(w*x**3*n0))
    spontaneous=float(np.sum(w*x**4*n0))
    induced=float(np.sum(w*x**4*B));recoil=spontaneous+induced
    monopole_induced=float(np.sum(w*x**4*n0*n0))
    return {'Tc_over_Tn':recoil/(4*U),'Tc_spontaneous_over_Tn':spontaneous/(4*U),
            'Tc_wrong_monopole_over_Tn':(spontaneous+monopole_induced)/(4*U),
            'energy_ratio':U/U_PLANCK,'number_ratio':number/N_PLANCK,
            'U3':U,'J4':recoil,'J4_spontaneous':spontaneous,'J4_induced':induced}

def compton_heating(Tn,beta,Tm,order=28):
    Tn,beta=validate(Tn,beta)
    if not np.isfinite(Tm) or Tm<0:raise ValueError('invalid electron temperature')
    if KB*max(Tn,Tm)/(ME*C*C)>1e-3:raise ValueError('outside declared nonrelativistic energy regime')
    mom=compton_moments(beta,order=order)
    u=CG*(KB*Tn)**4*mom['U3']
    tc=Tn*mom['Tc_over_Tn']
    power=4*SIGMA_T*C*KB*u/(ME*C*C)*(tc-Tm)
    return {'electron_heat_W':power,'T_C_K':tc,'energy_density_J_m3':u,
            'heat_definition':'thermal energy per mean-rest electron proper second; bulk force work excluded'}
