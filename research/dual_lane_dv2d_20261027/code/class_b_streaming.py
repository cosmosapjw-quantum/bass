"""DV2-D instantaneous polarized Bianchi-V/class-B Liouville operator.

Normal proper-time A=c*a_structure (or all rates times T_star for u=t/T_star),
N=0, geodesic/nonrotating normal tetrad, photon propagation direction.
The new operator is grad(A.n).D_spin, with no radial or Doppler A source.
Analytic rank-one Gaunt assembly only: no grid fitting, direct calls or IVPs.
Finite-band input has output through Lin+1 (Lin+2 when shear is included).
"""
from __future__ import annotations
from functools import lru_cache
from math import pi,sqrt
from pathlib import Path
import sys
import numpy as np
from sympy.physics.wigner import wigner_3j
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'vendor'))
from harmonic_streaming import labels,real_transform,coefficient_rhs


def validate_A(A):
    A=np.asarray(A,float)
    if A.shape!=(3,) or not np.isfinite(A).all():
        raise ValueError('A must be a finite three-vector of rates, not acceleration')
    return A


@lru_cache(maxsize=None)
def dipole_gaunt(spin:int,l:int,lp:int)->np.ndarray:
    """Integral conj(spinY_lm)Y_1M spinY_lpmp, BASS CS convention."""
    out=np.zeros((2*l+1,2*lp+1,3))
    if abs(l-lp)>1 or l+lp<1:return out
    pref=sqrt((2*l+1)*3*(2*lp+1)/(4*pi))*float(wigner_3j(l,1,lp,spin,0,-spin))
    if pref:
        for m in range(-l,l+1):
            for mp in range(-lp,lp+1):
                M=m-mp
                if abs(M)<=1:
                    out[l+m,lp+mp,M+1]=(-1)**(m+spin)*pref*float(wigner_3j(l,1,lp,-m,M,mp))
    out.setflags(write=False)
    return out


def _multiplication(spin:int,lin:int,lout:int,A)->np.ndarray:
    if spin not in (0,2) or not isinstance(lin,int) or not isinstance(lout,int) or not abs(spin)<=lin<=lout<=8:
        raise ValueError('Require spin0/2 and |spin|<=Lin<=Lout<=8')
    A=validate_A(A)
    ar=sqrt(4*pi/3)*A[[1,2,0]]
    ac=real_transform(1).T@ar
    out=np.zeros((len(labels(spin,lout)),len(labels(spin,lin))),complex)
    ro=0
    for l in range(abs(spin),lout+1):
        ci=0
        for lp in range(abs(spin),lin+1):
            if abs(l-lp)<=1:
                block=np.einsum('ijm,m->ij',dipole_gaunt(spin,l,lp),ac)
                out[ro:ro+2*l+1,ci:ci+2*lp+1]=real_transform(l).conj()@block@real_transform(lp).T
            ci+=2*lp+1
        ro+=2*l+1
    return out


def class_b_matrix(spin:int,lin:int,lout:int,A)->np.ndarray:
    """C_l,lp=[lp(lp+1)+2-l(l+1)]/2 times the spin-one Gaunt contraction.

    It is not anti-Hermitian: G+G^dagger=2 multiplication_by_(A.n).
    """
    out=_multiplication(spin,lin,lout,A)
    for i,(l,_) in enumerate(labels(spin,lout)):
        for j,(lp,_) in enumerate(labels(spin,lin)):
            out[i,j]*=(lp*(lp+1)+2-l*(l+1))/2
    return out


def class_b_rhs(c:dict,A,*,H:float=0.,S=None,nu:float=0.,lout:int|None=None)->dict:
    """Analytic class-B addition to pinned shear and polarized Thomson RHS."""
    A=validate_A(A)
    for (f,l,m),v in c.items():
        if f not in ('I','E','B','V') or not isinstance(l,int) or not isinstance(m,int) or l<0 or l>6 or abs(m)>l or (f in ('E','B') and l<2) or not np.isfinite(v):
            raise ValueError('Valid finite coefficient with ell<=6 required')
    S=np.zeros((3,3)) if S is None else np.asarray(S,float)
    lin=max([2]+[k[1] for k in c]);lout=(lin+2 if np.any(S) else lin+1) if lout is None else lout
    out=coefficient_rhs(c,H,S,nu,lout=lout)
    K0=class_b_matrix(0,lin,lout,A);K2=class_b_matrix(2,lin,lout,A)
    for f in ('I','V'):
        y=K0@np.array([c.get((f,l,m),0.) for l,m in labels(0,lin)])
        if np.max(abs(y.imag))>2e-11:raise ArithmeticError('Spin0 reality violation')
        for (l,m),v in zip(labels(0,lout),y):out[f,l,m]=out.get((f,l,m),0.)+float(v.real)
    y=K2@np.array([c.get(('E',l,m),0.)+1j*c.get(('B',l,m),0.) for l,m in labels(2,lin)])
    for (l,m),v in zip(labels(2,lout),y):
        out['E',l,m]=out.get(('E',l,m),0.)+float(v.real)
        out['B',l,m]=out.get(('B',l,m),0.)+float(v.imag)
    return out


def geometry_rates(n,H,S,A):
    """(direction, screen skew matrix, angular divergence, log-energy rate)."""
    A=validate_A(A);S=np.asarray(S,float);n=np.asarray(n,float)
    if S.shape!=(3,3) or not np.isfinite(S).all() or not np.isfinite(H) or np.max(abs(S-S.T))>1e-13 or abs(np.trace(S))>1e-13:
        raise ValueError('Finite H and symmetric trace-free S required')
    if n.ndim!=2 or n.shape[1]!=3 or not np.isfinite(n).all() or np.max(abs(np.linalg.norm(n,axis=1)-1))>1e-10:
        raise ValueError('Unit finite directions required')
    sn=np.einsum('ni,ij,nj->n',n,S,n);alpha=n@A
    v=-n@S.T+sn[:,None]*n-A+alpha[:,None]*n
    B=np.einsum('ni,nj->nij',v,n)-np.einsum('ni,nj->nij',n,v)
    return v,B,3*sn+2*alpha,-(H+sn)


def frozen_map(n0,a:float,t:float):
    """Exact canonical-A_z direction map and Jacobian, no Doppler/redshift.

    A vector is [0,0,a], H=S=N=0; reference time/rate units. This closed
    diagnostic is not a finite-time collision solver or an Einstein solution.
    """
    n0=np.asarray(n0,float)
    if n0.ndim!=2 or n0.shape[1]!=3 or not np.isfinite(n0).all() or np.max(abs(np.linalg.norm(n0,axis=1)-1))>1e-10 or not np.isfinite(a*t):
        raise ValueError('Finite unit directions and finite a,t required')
    if abs(a*t)>20:raise ValueError('Bounded frozen diagnostic requires |a*t|<=20')
    ch,sh=np.cosh(a*t),np.sinh(a*t);D=ch-n0[:,2]*sh
    n=np.column_stack([n0[:,0]/D,n0[:,1]/D,(n0[:,2]*ch-sh)/D])
    return n,D**-2


def rate_moments(g,J):
    """rho, q=energy_flux/c, pi, with common carrier normalization."""
    I=np.trace(J,axis1=1,axis2=2)
    rho=float(np.dot(g.w,I));q=np.einsum('n,n,ni->i',g.w,I,g.n)
    pi=np.einsum('n,n,ni,nj->ij',g.w,I,g.n,g.n)-rho*np.eye(3)/3
    return rho,q,pi
