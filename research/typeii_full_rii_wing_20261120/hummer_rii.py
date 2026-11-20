"""Classical Hummer 1962 Type II angle/frequency Voigt closed kernel.

Exact within sharp lower level, radiation damping, Doppler Maxwell gas and atom
frame coherent scattering, *without recoil*. Not microscopic full quantum RII.
Finite frequency-bin mass computed without renormalizing omitted outer wings.
"""
from pathlib import Path
import math,sys
import numpy as np
from scipy.integrate import quad
from scipy.special import wofz
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'research/typeii_correlated_outer_20261119'))
import correlated as prior
MODEL_SCOPE="COHERENT_NO_RECOIL_EXACT_HUMMER_II"
def check(cond,msg):
    if not bool(cond):raise RuntimeError(msg)
def phi(x,a):
    if not np.isfinite(np.r_[x,a]).all() or a<=0:
        raise ValueError('positive Voigt damping and finite frequency required')
    return np.real(wofz(np.asarray(x)+1j*a))/np.sqrt(np.pi)
def joint(x,xout,mu,a):
    if not np.isfinite([x,xout,mu,a]).all() or a<=0 or not -1<=mu<=1:
        raise ValueError('finite, physical input x, xout, mu, a required')
    if mu==1.:
        raise ValueError('forward delta distribution has no ordinary pointwise density')
    if mu==-1.:
        s=(x+xout)/2
        return math.exp(-((x-xout)/2)**2)*a/(2*math.pi**1.5*(s*s+a*a))
    s=math.sqrt((1-mu)/2);q=math.sqrt((1+mu)/2)
    X=(x+xout)/(2*q);Y=(x-xout)/(2*s)
    return math.exp(-Y*Y)*float(np.real(wofz(X+1j*a/q)))/(2*math.pi*s*q)
def conditional(x,xout,mu,a):
    return joint(x,xout,mu,a)/float(phi(x,a))
def _splitintegral(f,low,high,points):
    relevant=sorted(set([low,high]+[t for t in points if low<t<high]))
    return sum(quad(f,a,b,epsabs=1e-12,epsrel=3e-9,limit=100)[0]
               for a,b in zip(relevant[:-1],relevant[1:]))
def conditional_bins(x,mu,a,edges):
    e=np.asarray(edges,float)
    if e.ndim!=1 or len(e)<2 or not np.isfinite(np.r_[x,mu,a,e]).all() or a<=0 or abs(mu)>1 or np.min(np.diff(e))<=0:
        raise ValueError('strict ascending edges, finite x, physical mu, positive damping')
    out=np.zeros(len(e)-1)
    if mu==1.:
        j=int(np.searchsorted(e,x,side='right')-1)
        if 0<=j<len(out):out[j]=1.
        return out
    norm=float(phi(x,a))
    if mu==-1.:
        # Exact u=(x-xout)/2 under backscattering, with incoming
        # Maxwell/Lorentz conditional density and Jacobian cancelling in du.
        def fu(u):return math.exp(-u*u)*a/(math.pi*((x-u)**2+a*a))/(norm*math.sqrt(math.pi)/math.sqrt(math.pi)) # norm=H/sqrt(pi)
        # Integral of fu is H(a,x); divide by sqrt(pi)*phi=H.
        for i,(left,right) in enumerate(zip(e[:-1],e[1:])):
            u0=(x-right)/2;u1=(x-left)/2
            out[i]=_splitintegral(fu,u0,u1,[0.,x-5*a,x,x+5*a,x-1.,x+1.])/(math.sqrt(math.pi))
    else:
        for i,(left,right) in enumerate(zip(e[:-1],e[1:])):
            out[i]=_splitintegral(lambda t:joint(float(x),float(t),float(mu),float(a))/norm,
               left,right,[x-8,x-4,x,x+4,x+8,-x])
    if not np.isfinite(out).all() or np.min(out)<-1e-12 or np.sum(out)>1+2e-4:
        raise RuntimeError('Hummer finite-bin conditional normalization failure')
    return np.maximum(out,0.)
def directions(order=6):
    if order==6:return prior.sphere6()
    if order==14:return prior.sphere14()
    raise ValueError('only source six/fourteen sky positive quadrature supported')

def leading_recoil_bins(x,mu,a,edges,recoil):
    """Leading atom recoil shifts emitted Doppler frequency by -recoil*(1-mu).

    Uses exact recoil-free Hummer conditional with shifted outgoing integration
    edges. This is a first-order frequency-shift model, NOT the full quantum
    redistribution/recoil operator or exact detailed-balance correction.
    """
    if not np.isfinite(recoil) or recoil<0:raise ValueError('finite nonnegative recoil')
    return conditional_bins(x,mu,a,np.asarray(edges,float)+recoil*(1-mu))
