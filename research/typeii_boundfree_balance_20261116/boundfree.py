"""State-resolved finite-support photoionization/Milne capture bridge.
SI rates. Source photon/excess energies are in Ry; sigma in Mb. The original
finite table is never extrapolated. No effective HYREC rate is overwritten.
Maxwellian relative electrons, infinitely heavy hydrogen nucleus, unaligned nl
levels, unpolarized photon bath. The angular monopole is exact for the prescribed
boosted normal Planck/BE distribution; recoil/thermal Doppler and alignment are
outside the bound-free approximation used here.
"""
from pathlib import Path
from functools import lru_cache
import hashlib,json,math,re
import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.special import logsumexp
from numpy.polynomial.legendre import leggauss
H=6.62607015e-34
C=299792458.
KB=1.380649e-23
EV=1.602176634e-19
ME=9.1093837139e-31
RY_EV=13.605693122994
RY=RY_EV*EV
A=8*np.pi/(H**3*C**2)
ROOT=Path(__file__).resolve().parent
SOURCE_HASH='4150287531cc642ecf837fa253b22f5158bd189b3f2c9ce634010b2e4b5ee44c'

def check(ok,msg):
    if not bool(ok):raise RuntimeError(msg)

def load_source():
    p=ROOT/'sources/h1.px.txt';check(hashlib.sha256(p.read_bytes()).hexdigest()==SOURCE_HASH,'raw author table identity drift')
    lines=p.read_text().splitlines();out={}
    for i,line in enumerate(lines):
        hit=re.match(r'^\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*:',line)
        if not hit:continue
        spin,l,par,n=map(int,hit.groups());be,count=lines[i+1].split()
        arr=np.array([list(map(float,v.split())) for v in lines[i+2:i+2+int(count)]])
        check(arr.shape==(int(count),3) and np.isfinite(arr).all(),'invalid source block')
        check(n>=1 and 0<=l<n and spin==2 and par==l%2,'source state identity')
        chi=-float(be)*RY;k=arr[:,1]*RY;sig=arr[:,2]*1e-22
        check(k[0]==0 and np.all(np.diff(k)>0) and min(sig)>0,'source grid/cross section')
        check((n,l) not in out,'duplicate state')
        # The binding line and excess-energy column are authoritative. Photon
        # energies are separately rounded in the original table and not mixed.
        x=np.log1p(k/chi);y=np.log(sig)
        out[n,l]={'n':n,'l':l,'g':2*(2*l+1),'gplus':1,'chi':chi,'K':k,'sigma':sig,
            'Kmax':float(k[-1]),'logx':x,'logsigma':y,'interp':PchipInterpolator(x,y,extrapolate=False),
            'photon_column_rounding_max_J':float(max(abs(arr[:,0]*RY-chi-k)))}
    check(len(out)==55 and set(out)=={(n,l) for n in range(1,11) for l in range(n)},'source level completeness')
    return out
LEVELS=load_source()

def level(key):
    if key not in LEVELS:raise ValueError('unsupported resolved hydrogen level')
    return LEVELS[key]

def validate(Tn,Tm,beta,eta=0):
    vals=np.asarray([Tn,Tm,beta,eta],float)
    if not np.isfinite(vals).all() or min(Tn,Tm)<=0 or max(Tn,Tm)>10000 or min(Tn,Tm)<300 or abs(beta)>.2 or eta<0:
        raise ValueError('scope: 300<=T<=10000 K, |beta|<=0.2, eta>=0, finite scalars')

def sigma(E,key,method='pchip'):
    q=level(key);e=np.asarray(E,float)
    if not np.isfinite(e).all() or np.any(e<0):raise ValueError('invalid photon energy')
    limit=q['chi']+q['Kmax']
    if np.any(e>limit*(1+4e-15)):raise ValueError('outside finite author cross-section support')
    k=np.clip(e-q['chi'],0,q['Kmax']);x=np.log1p(k/q['chi'])
    if method=='pchip':s=np.exp(q['interp'](x))
    elif method=='linear':s=np.exp(np.interp(x,q['logx'],q['logsigma']))
    else:raise ValueError('unknown interpolation')
    return np.where(e>=q['chi'],s,0.)

def capture_sigma(K,key,method='pchip'):
    q=level(key);k=np.asarray(K,float)
    if not np.isfinite(k).all() or np.any(k<=0):raise ValueError('capture cross section needs K>0; v sigma Maxwell measure is regular')
    E=q['chi']+k
    return q['g']/q['gplus']*E*E/(2*ME*C*C*k)*sigma(E,key,method)

def log_nbar(E,Tn,beta=0,eta=0):
    e=np.asarray(E,float)
    if not np.isfinite(e).all() or np.any(e<=0) or not np.isfinite(Tn) or Tn<=0 or not np.isfinite(beta) or abs(beta)>.2 or not np.isfinite(eta) or eta<0:
        raise ValueError('invalid spectral arguments')
    b=abs(float(beta));u=e/(KB*Tn)/np.sqrt(1-b*b)
    if b==0:
        a=u+eta;return -a-np.log(-np.expm1(-a))
    # Exact analytic angular integral, written without subtracting two nearly
    # equal logarithms; the deep-Wien asymptote differs below 5e-14 relatively.
    amin=u*(1-b)+eta;delta=2*u*b
    logY=-amin+np.log(-np.expm1(-delta))-np.log(-np.expm1(-amin))
    ans=logY.copy() if np.ndim(logY)>0 else np.asarray(logY)
    regular=logY>=-30
    ans=np.where(regular,np.log(np.log1p(np.exp(np.maximum(logY,-745)))),logY)
    return ans-np.log(delta)

@lru_cache(maxsize=64)
def quadrature(key,order=4):
    if not isinstance(order,int) or not 2<=order<=24:raise ValueError('segment order must be 2..24')
    q=level(key);k=q['K'];a,w=leggauss(order)
    nodes=(k[:-1,None]+.5*np.diff(k)[:,None]*(a+1)).ravel()
    weights=(.5*np.diff(k)[:,None]*w).ravel()
    return nodes,weights

def log_saha(T,key,eta=0):
    q=level(key)
    if not np.isfinite(T) or T<=0 or not np.isfinite(eta):raise ValueError('invalid equilibrium inputs')
    return np.log(q['g']/(2*q['gplus']))+1.5*np.log(H*H/(2*np.pi*ME*KB*T))+q['chi']/(KB*T)+eta

def rates(Tn,Tm,beta,key,eta=0,order=8,method='pchip'):
    validate(Tn,Tm,beta,eta);q=level(key)
    K,w=quadrature(key,order);E=q['chi']+K
    logs=np.log(sigma(E,key,method));lnn=log_nbar(E,Tn,beta,eta)
    base=np.log(w)+2*np.log(E)+logs
    lp=base+lnn
    cap=base-K/(KB*Tm)
    ls0=np.log(q['g']/(2*q['gplus']))+1.5*np.log(H*H/(2*np.pi*ME*KB*Tm))
    logP=math.log(A)+float(logsumexp(lp))
    logSp=math.log(A)+ls0+float(logsumexp(cap))
    logSt=math.log(A)+ls0+float(logsumexp(cap+lnn))
    lc=cap+np.logaddexp(0,lnn);logAl=math.log(A)+ls0+float(logsumexp(lc))
    kp=float(np.sum(np.exp(lp-logsumexp(lp))*K))
    kc=float(np.sum(np.exp(lc-logsumexp(lc))*K))
    return {'level':list(key),'g':q['g'],'chi_J':q['chi'],'log_photo':logP,'log_alpha':logAl,
            'photo_s':float(np.exp(logP)),'alpha_m3_s':float(np.exp(logAl)),
            'alpha_spontaneous_m3_s':float(np.exp(logSp)),'alpha_stimulated_m3_s':float(np.exp(logSt)),
            'stimulated_fraction':float(np.exp(logSt-logAl)),
            'photo_excess_J':kp,'capture_kinetic_J':kc,
            'log_stationary_ratio_m3':logAl-logP,
            'log_departure_from_Tm_Saha':logAl-logP-log_saha(Tm,key),
            'support_Kmax_eV':q['Kmax']/EV,
            'support_over_kT_hot':q['Kmax']/(KB*max(Tm,Tn*np.sqrt((1+abs(beta))/(1-abs(beta))))),
            'rate_scope':'finite original table support, no extrapolation',
            'Tm_K':Tm,'Tn_K':Tn,'beta':beta,'eta':eta,'segment_order':order,'interpolation':method}

def velocity_alpha(Tn,Tm,beta,key,eta=0,order=8):
    validate(Tn,Tm,beta,eta);q=level(key)
    # Independent integration variable, Maxwell speed PDF and Milne cross section.
    edges=np.sqrt(2*q['K']/ME);a,w=leggauss(order)
    v=(edges[:-1,None]+.5*np.diff(edges)[:,None]*(a+1)).ravel()
    dv=(.5*np.diff(edges)[:,None]*w).ravel()
    K=.5*ME*v*v;E=q['chi']+K
    fv=4*np.pi*(ME/(2*np.pi*KB*Tm))**1.5*v*v*np.exp(-K/(KB*Tm))
    n=np.exp(log_nbar(E,Tn,beta,eta))
    return float(np.sum(dv*v*fv*capture_sigma(K,key)*(1+n)))

def net_sources(r,ni,ne,nplus):
    if not np.isfinite([ni,ne,nplus]).all() or min(ni,ne,nplus)<0:raise ValueError('invalid density')
    forward=ni*r['photo_s'];reverse=ne*nplus*r['alpha_m3_s'];F=forward-reverse
    chi=r['chi_J'];Qk=forward*r['photo_excess_J']-reverse*r['capture_kinetic_J']
    Qi=chi*F
    Qg=-forward*(chi+r['photo_excess_J'])+reverse*(chi+r['capture_kinetic_J'])
    return {'F_ion_m3_s':F,'dni_proper_s':-F,'dnplus_proper_s':F,'dne_proper_s':F,
            'nucleus_residual':-F+F,'charge_residual':F-F,
            'Q_photon':Qg,'Q_kinetic':Qk,'Q_ionization':Qi,'energy_residual':Qg+Qk+Qi}

def proper_to_normal_fraction(sources,nH,Gamma,Hn):
    if not np.isfinite([nH,Gamma,Hn]).all() or nH<=0 or Gamma<1 or Hn<=0:raise ValueError('invalid clock/density')
    return np.asarray(sources,float)/(nH*Gamma*Hn)
