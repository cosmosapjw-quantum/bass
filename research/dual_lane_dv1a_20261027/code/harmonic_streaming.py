"""DV1-A exact angular generator on prescribed nonrotating Bianchi I.

Normal proper-time rates (or all rates multiplied by T_star for u=t/T_star).
Bolometric I,V are spin0; Q+iU=sum(E+iB) spin+2 Z in pinned DL2 convention.
No amplitude expansion. Finite bandlimit specifies the input fixture, not a
closure prescription: its full instantaneous output extends through Lin+2.
The Wigner formula constructs the generator without an angular quadrature or
calls to a direct RHS. This module does not evolve a truncated hierarchy.
"""
from __future__ import annotations
from functools import lru_cache
from math import pi,sqrt
from pathlib import Path
import sys
import numpy as np
from sympy.physics.wigner import wigner_3j
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'vendor'))
from polarized_dictionary import stf_basis


def labels(spin: int,lmax: int) -> list[tuple[int,int]]:
    return [(l,m) for l in range(abs(spin),lmax+1) for m in range(-l,l+1)]


@lru_cache(maxsize=None)
def real_transform(l: int) -> np.ndarray:
    """Z_r=sum_j R[r,j]Y_j; coefficient a_Y=R.T a_Z (not R^dagger)."""
    R=np.zeros((2*l+1,2*l+1),complex);R[l,l]=1
    for m in range(1,l+1):
        R[l+m,l+m]=(-1)**m/sqrt(2);R[l+m,l-m]=1/sqrt(2)
        R[l-m,l+m]=(-1)**m/(1j*sqrt(2));R[l-m,l-m]=-1/(1j*sqrt(2))
    R.setflags(write=False);return R


@lru_cache(maxsize=None)
def gaunt_block(spin: int,l: int,lp: int) -> np.ndarray:
    """Integral conj(spinY_lm) Y_2M spinY_lpmp in exact 3j convention."""
    out=np.zeros((2*l+1,2*lp+1,5),float)
    if abs(l-lp)>2 or l+lp<2:return out
    spin3j=float(wigner_3j(l,2,lp,spin,0,-spin))
    pref=sqrt((2*l+1)*5*(2*lp+1)/(4*pi))*spin3j
    if pref==0:return out
    for m in range(-l,l+1):
        for mp in range(-lp,lp+1):
            M=m-mp
            if abs(M)<=2:
                out[m+l,mp+lp,M+2]=(-1)**(m+spin)*pref*float(wigner_3j(l,2,lp,-m,M,mp))
    out.setflags(write=False);return out


def _validate(spin,lin,lout,H,S):
    if spin not in (0,2) or not abs(spin)<=lin<=lout<=8:
        raise ValueError('Require spin 0/2 and |spin|<=Lin<=Lout<=8')
    S=np.asarray(S,float)
    if S.shape!=(3,3) or not np.isfinite(S).all() or not np.isfinite(H):
        raise ValueError('Finite H and 3x3 shear required')
    if np.max(np.abs(S-S.T))>1e-13 or abs(np.trace(S))>1e-13:
        raise ValueError('Shear must be symmetric trace-free; no silent projection')
    return S


def streaming_matrix(spin: int,lin: int,lout: int,H: float,S) -> np.ndarray:
    """Exact bandlimited-input angular projection; Lout>=Lin+2 retains all output.

    C_l,lp=[lp(lp+1)-l(l+1)-10]/4 multiplies the spin Gaunt integral.
    Smaller Lout is an explicit output projection, not a closed exact dynamics.
    """
    S=_validate(spin,lin,lout,H,S)
    sr=np.einsum('mij,ij->m',stf_basis(),S)*sqrt(8*pi/15)
    sc=real_transform(2).T@sr
    out=np.zeros((len(labels(spin,lout)),len(labels(spin,lin))),complex)
    ro=0
    for l in range(abs(spin),lout+1):
        ci=0
        for lp in range(abs(spin),lin+1):
            if abs(l-lp)<=2:
                gc=np.einsum('ijm,m->ij',gaunt_block(spin,l,lp),sc)
                block=real_transform(l).conj()@gc@real_transform(lp).T
                out[ro:ro+2*l+1,ci:ci+2*lp+1]=(lp*(lp+1)-l*(l+1)-10)/4*block
            if l==lp:out[ro:ro+2*l+1,ci:ci+2*lp+1]-=4*H*np.eye(2*l+1)
            ci+=2*lp+1
        ro+=2*l+1
    return out


def collision_rhs(c: dict,nu: float) -> dict:
    """Rest-cold-Thomson same-physics full polarized collision generator."""
    if not np.isfinite(nu) or nu<0:raise ValueError('finite nonnegative nu required')
    out={k:-nu*v for k,v in c.items()}
    out['I',0,0]=0.
    K=np.array([[.1,-sqrt(6)/10],[-sqrt(6)/10,.6]])
    for m in range(-2,3):
        y=np.array([c.get(('I',2,m),0.),c.get(('E',2,m),0.)])
        a=nu*(K-np.eye(2))@y
        out['I',2,m]=float(a[0]);out['E',2,m]=float(a[1])
    for m in range(-1,2):out['V',1,m]=-.5*nu*c.get(('V',1,m),0.)
    return out


def coefficient_rhs(c: dict,H: float,S,nu: float=0.,lout: int|None=None) -> dict:
    """Apply analytic Liouville plus full polarized collision in real all-m basis."""
    for (f,l,m),v in c.items():
        if f not in ('I','E','B','V') or l<0 or abs(m)>l or l>6 or (f in ('E','B') and l<2) or not np.isfinite(v):
            raise ValueError('Invalid finite coefficient')
    lin=max([2]+[k[1] for k in c]);lout=lin+2 if lout is None else lout
    if lout<lin:raise ValueError('lout must retain input modes')
    l0,l2=labels(0,lin),labels(2,lin)
    out={}
    a0=streaming_matrix(0,lin,lout,H,S);a2=streaming_matrix(2,lin,lout,H,S)
    for f in ('I','V'):
        x=np.array([c.get((f,l,m),0.) for l,m in l0]);y=a0@x
        if np.max(np.abs(y.imag))>2e-12:raise ArithmeticError('Scalar real-basis reality violation')
        out.update({(f,l,m):float(v.real) for (l,m),v in zip(labels(0,lout),y)})
    p=np.array([c.get(('E',l,m),0.)+1j*c.get(('B',l,m),0.) for l,m in l2]);p=a2@p
    for (l,m),v in zip(labels(2,lout),p):out['E',l,m]=float(v.real);out['B',l,m]=float(v.imag)
    for k,v in collision_rhs(c,nu).items():out[k]=out.get(k,0.)+v
    return out
