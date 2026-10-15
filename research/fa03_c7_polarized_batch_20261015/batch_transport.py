"""FA03 C7: physical matrix transfer with fused six-state & batched spectral RK4.

Exact source contracts from archived fa02/fa03 are reused without modifying them.
Supports deterministic ray chunks / optional threads; no independent certification
of angular-cap, time-truncation or empirical atomic opacity follows from this code.
"""
from __future__ import annotations

import hashlib
import math
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from time import perf_counter

import numpy as np
from numpy.polynomial.legendre import leggauss

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent/"fa03_c5_angular_cap_20261015"/"reference"
sys.path.insert(0,str(ROOT))
import fa02
import fa03

SHA={"fa02.py":"1e89e75f7a08d2eec1851a58e602c2683b1888a37b3e1fe10b1be4234756eee5",
     "fa03.py":"ad865127da7c2f9ea613541571f9b842f9da7630af9bb951a3df5968ad44ecf7"}

def verify():
    for name,sha in SHA.items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=sha:
            raise ValueError(f"FROZEN_SOURCE_CHANGED:{name}")
    return dict(SHA)

def _prepared_rays(nr=3,nphi=12):
    if not (isinstance(nr,int) and nr>0 and isinstance(nphi,int) and nphi>0):
        raise ValueError("nr,nphi positive ints")
    return fa02.cap_nodes(.02,nr,nphi)

def _check_setup(steps,ell,w):
    if not isinstance(steps,int) or steps<=0:raise ValueError("steps positive integer")
    ell=np.asarray(ell,dtype=float);w=np.asarray(w,dtype=float)
    if ell.ndim!=2 or ell.shape[1]!=3 or len(w)!=len(ell) or not len(w):
        raise ValueError("ray/weight shape invalid")
    if not np.isfinite(ell).all() or not np.isfinite(w).all() or (w<0).any():
        raise ValueError("nonfinite rays or negative weights")
    return ell,w

def trace_norm(m):
    return float(np.linalg.svd(m,compute_uv=False).sum())

def _mom_coeff(x,data):
    P,H,G,k=fa03.fields(x,data)
    a=np.asarray([fa03.moment(j+3) for j in range(3)])[:,None]
    b=np.asarray([fa03.moment(j+4) for j in range(3)])[:,None]
    source=(a+.1*b*k[None,:])[...,None,None]*P[None]
    return P,H,G,k,source

def _mom_rhs(Y,op):
    _,H,G,k,source=op
    GT=G.swapaxes(-1,-2)[None]
    # fused batched all six matrix states, avoid six independent Python matmul pairs
    out=-np.matmul(G[None],Y)-np.matmul(Y,GT)
    out[:3]+=source
    weighted=k[None,:,None,None]*Y
    couple=np.stack((weighted[1]-Y[0],
                     weighted[2]-Y[1],
                     2*(weighted[4]-Y[3])))
    out[3:]-=np.matmul(H[None],couple)+np.matmul(couple,H.swapaxes(-1,-2)[None])
    return out

def solve_moments_fused(steps=64,nr=3,nphi=12,ell=None,w=None,chi=.008,psi=.01):
    """Six ε=0 states, each shape [ray,2,2], frozen Fa03 source laws."""
    verify()
    if ell is None or w is None:
        if ell is not None or w is not None:raise ValueError("provide rays and weights together")
        ell,w=_prepared_rays(nr,nphi)
    ell,w=_check_setup(steps,ell,w)
    if not np.isfinite([chi,psi]).all() or max(abs(chi),abs(psi))>.02:
        raise ValueError("frozen observer family bound")
    data=fa02.setup(ell,chi,psi)
    Y=np.zeros((6,len(w),2,2),dtype=complex)
    h=.5/steps
    # 2*steps+1 distinct coefficient evaluations rather than 4*steps
    current=_mom_coeff(.5,data)
    for j in range(steps):
        x=.5+h*j
        middle=_mom_coeff(x+h/2,data)
        end=_mom_coeff(x+h,data)
        k1=_mom_rhs(Y,current)
        k2=_mom_rhs(Y+h*k1/2,middle)
        k3=_mom_rhs(Y+h*k2/2,middle)
        k4=_mom_rhs(Y+h*k3,end)
        Y=Y+h*(k1+2*k2+2*k3+k4)/6
        current=end
    return np.einsum("n,snij->sij",w,Y,optimize=True)

def _spectral_ops(x,data,es,energy):
    P,H,G,k=fa03.fields(x,data)
    source=(energy[None,:]**3*(1+.1*energy[None,:]*k[:,None]))[...,None,None]*P[:,None,:,:]
    Delta=(energy[None,:]*k[:,None]-1)
    Ge=G[None,:,None,:,:]+es[:,None,None,None,None]*Delta[None,:,:,None,None]*H[None,:,None,:,:]
    return source,Ge

def _spectral_rhs(F,op):
    B,Ge=op
    return B[None]-np.matmul(Ge,F)-np.matmul(F,Ge.swapaxes(-1,-2))

def _spectral_chunk(es,ell,w,energy,ew,steps):
    data=fa02.setup(ell,.008,.01)
    Y=np.zeros((len(es),len(w),len(energy),2,2),complex)
    h=.5/steps
    op0=_spectral_ops(.5,data,es,energy)
    for i in range(steps):
        x=.5+h*i
        opm=_spectral_ops(x+h/2,data,es,energy)
        op1=_spectral_ops(x+h,data,es,energy)
        a=_spectral_rhs(Y,op0)
        b=_spectral_rhs(Y+h*a/2,opm)
        c=_spectral_rhs(Y+h*b/2,opm)
        d=_spectral_rhs(Y+h*c,op1)
        Y=Y+h*(a+2*b+2*c+d)/6
        op0=op1
    return np.einsum("n,e,mneij->mij",w,ew,Y,optimize=True)

def solve_energy_batched(eps=(-.1,0.,.1),*,steps=64,nr=3,nphi=12,ne=8,
                         ell=None,w=None,ray_chunk=None,workers=1):
    """Batch ε and energy; ray-chunk parallelism deterministic; source fixed and pure."""
    verify()
    es=np.atleast_1d(np.asarray(eps,dtype=float))
    if es.ndim!=1 or not len(es) or not np.isfinite(es).all() or np.max(abs(es))>.1:
        raise ValueError("epsilon real finite |epsilon|<=0.1")
    if not isinstance(ne,int) or ne<2:raise ValueError("ne>=2 required")
    if not isinstance(workers,int) or workers<1 or workers>8:
        raise ValueError("1<=workers<=8")
    if ell is None or w is None:
        if ell is not None or w is not None:raise ValueError("provide rays and weights together")
        ell,w=_prepared_rays(nr,nphi)
    ell,w=_check_setup(steps,ell,w)
    v,ww=leggauss(ne)
    energy=1+.02*v
    ew=ww/2
    if ray_chunk is None:
        ray_chunk=len(w)
    if not isinstance(ray_chunk,int) or ray_chunk<1:
        raise ValueError("positive ray chunk")
    cuts=[(i,min(i+ray_chunk,len(w))) for i in range(0,len(w),ray_chunk)]
    def eval_chunk(pair):
        a,b=pair
        return _spectral_chunk(es,ell[a:b],w[a:b],energy,ew,steps)
    if workers==1 or len(cuts)==1:
        partial=[eval_chunk(q) for q in cuts]
    else:
        with ThreadPoolExecutor(max_workers=min(workers,len(cuts))) as pool:
            # executor.map returns results in submission order, deterministic sum order
            partial=list(pool.map(eval_chunk,cuts))
    acc=np.zeros((len(es),2,2),complex)
    for part in partial:acc=acc+part
    return acc

def stokes(F):
    return np.array([np.trace(F).real,(F[0,0]-F[1,1]).real,
                  2*F[0,1].real,-2*F[0,1].imag])

def ray_physics_checks(nr=3,nphi=12,at=(.5,.7,1.)):
    verify()
    ell,w=_prepared_rays(nr,nphi)
    data=fa02.setup(ell,.008,.01)
    stats=[]
    P3eig=np.linalg.eigvalsh(fa02.P3)
    for x in at:
        n,kk,C,L,_,_=data
        v=np.sqrt(1-(1-x*x)*n[...,2]**2)
        ray=np.stack([n[...,0]/v,n[...,1]/v,x*n[...,2]/v],axis=-1)
        B=np.stack([kk,np.cross(ray,kk)],axis=-1)
        S=B@C
        P,H,G,k=fa03.fields(x,data)
        eklo=.98*k.min();ekhi=1.02*k.max()
        base_min=min(1+eps*(e*k0-1) for eps in (-.1,.1) for e in (.98,1.02)
                     for k0 in (k.min(),k.max()))
        stats.append({"x":x,"max_screen_orthonormal_error":float(abs(S.swapaxes(-1,-2)@S-np.eye(2)).max()),
        "max_ray_unit_error":float(abs((ray*ray).sum(axis=-1)-1).max()),
        "max_kk_ray_error":float(abs((kk*ray).sum(axis=-1)).max()),
        "min_source_eig":float(np.linalg.eigvalsh(P).min()),
        "min_absorption_eig":float(np.linalg.eigvalsh(H).min()),
        "min_passivity_factor":float(base_min),"k_min":float(k.min()),"k_max":float(k.max())})
    return {"P3_eigenvalues":P3eig.tolist(),"angle_count":len(w),
            "weights_sum":float(w.sum()),"per_x":stats,
            "positive_jones_solution":"dF/dx=B-Ge F-F Ge^transpose has variation-of-constants positive congruence for B>=0, given frozen real Ge",
            "empirical_atomic_accuracy":None}

if __name__=="__main__":
    import json
    print(json.dumps(ray_physics_checks(),indent=2))
