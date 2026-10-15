"""Real-Stokes 4-component SIMD-friendly equivalent of the frozen FA03 Jones ODE.

For F=1/2[[I+Q,U-iV],[U+iV,I-Q]], Ge=alpha*H+omega*J,
H=[[h0+hz,hx],[hx,h0-hz]], J=[[0,-1],[1,0]]:
 dI=BI-2alpha*(h0*I+hz*Q+hx*U)
 dQ=BQ-2alpha*(h0*Q+hz*I)+2omega*U
 dU=BU-2alpha*(h0*U+hx*I)-2omega*Q
 dV=BV-2alpha*h0*V.
Exact coordinate transform, not a weak-polarization approximation.
"""
from __future__ import annotations
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from numpy.polynomial.legendre import leggauss

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import batch_transport as parent

def _stokes_coefficient(x,data,epsilon,energy):
    P,H,G,k=parent.fa03.fields(x,data)
    ps=np.stack(((P[:,0,0]+P[:,1,1]).real,
                  (P[:,0,0]-P[:,1,1]).real,
                   2*P[:,0,1].real,-2*P[:,0,1].imag),axis=-1)  # [ray,4]
    src=(energy[None,:]**3*(1+.1*k[:,None]*energy[None,:]))[...,None]*ps[:,None,:]
    alpha=1+epsilon[:,None,None]*(energy[None,None,:]*k[None,:,None]-1)
    h0=.5*(H[:,0,0]+H[:,1,1])
    hz=.5*(H[:,0,0]-H[:,1,1])
    hx=H[:,0,1]
    rot=G[:,1,0]-G[:,0,1]  # =2*omega
    return src,2*alpha*h0[None,:,None],2*alpha*hz[None,:,None],2*alpha*hx[None,:,None],rot[None,:,None]

def _rhs(Y,c):
    src,a0,az,ax,rot=c
    I,Q,U,V=Y[...,0],Y[...,1],Y[...,2],Y[...,3]
    return np.stack((src[None,:,:,0]-a0*I-az*Q-ax*U,
                     src[None,:,:,1]-a0*Q-az*I+rot*U,
                     src[None,:,:,2]-a0*U-ax*I-rot*Q,
                     src[None,:,:,3]-a0*V),axis=-1)

def _rays_stokes(eps,ell,w,energy,ew,steps):
    data=parent.fa02.setup(ell,.008,.01)
    Y=np.zeros((len(eps),len(w),len(energy),4),dtype=float)
    h=.5/steps
    c0=_stokes_coefficient(.5,data,eps,energy)
    for i in range(steps):
        x=.5+i*h
        cm=_stokes_coefficient(x+h/2,data,eps,energy)
        c1=_stokes_coefficient(x+h,data,eps,energy)
        a=_rhs(Y,c0)
        b=_rhs(Y+h*a/2,cm)
        c=_rhs(Y+h*b/2,cm)
        d=_rhs(Y+h*c,c1)
        Y=Y+h*(a+2*b+2*c+d)/6
        c0=c1
    # deterministic signed Stokes reduction, same normalized GL energy/angle weights.
    out=np.einsum('n,e,mnek->mk',w,ew,Y,optimize=True)
    return out

def stokes_to_coherency(Y):
    Y=np.asarray(Y,dtype=float)
    if Y.shape[-1]!=4:raise ValueError("Stokes[...,4]")
    F=np.zeros(Y.shape[:-1]+(2,2),dtype=complex)
    F[...,0,0]=.5*(Y[...,0]+Y[...,1])
    F[...,1,1]=.5*(Y[...,0]-Y[...,1])
    F[...,0,1]=.5*(Y[...,2]-1j*Y[...,3])
    F[...,1,0]=F[...,0,1].conj()
    return F

def solve_energy_real(eps=(-.1,0.,.1),*,steps=64,nr=3,nphi=12,ne=8,
                      ell=None,w=None,ray_chunk=None,workers=1,output="matrix"):
    """Bounded-memory real Stokes vector spectral transport, optional ray threads.

    Default is worker=1 and unchunked. For small arrays parallel ray splitting
    is commonly slower and is not a claimed performance optimization.
    """
    parent.verify()
    es=np.atleast_1d(np.asarray(eps,dtype=float))
    if es.ndim!=1 or len(es)==0 or not np.isfinite(es).all() or np.max(abs(es))>.1:
        raise ValueError("physical epsilon out of range")
    if not isinstance(ne,int) or ne<2:
        raise ValueError("ne>=2")
    if not isinstance(workers,int) or workers<1 or workers>8:
        raise ValueError("workers integer 1..8")
    if ell is None or w is None:
        if ell is not None or w is not None:
            raise ValueError("ell and w together")
        ell,w=parent._prepared_rays(nr,nphi)
    ell,w=parent._check_setup(steps,ell,w)
    nodes,ww=leggauss(ne)
    energy=1+.02*nodes
    ew=ww/2
    if ray_chunk is None:ray_chunk=len(w)
    if not isinstance(ray_chunk,int) or ray_chunk<1:
        raise ValueError("ray_chunk>=1")
    cuts=[(i,min(len(w),i+ray_chunk)) for i in range(0,len(w),ray_chunk)]
    def execute(cut):
        l,r=cut
        return _rays_stokes(es,ell[l:r],w[l:r],energy,ew,steps)
    if workers==1 or len(cuts)==1:
        parts=[execute(cut) for cut in cuts]
    else:
        with ThreadPoolExecutor(max_workers=min(workers,len(cuts))) as pool:
            parts=list(pool.map(execute,cuts))
    total=np.zeros((len(es),4),dtype=float)
    for part in parts:total+=part
    if output=="stokes":return total
    if output=="matrix":return stokes_to_coherency(total)
    raise ValueError("output matrix or stokes")

if __name__=="__main__":
    import json
    print(json.dumps({"eps":[-.1,0,.1],
                      "stokes":solve_energy_real(output="stokes").tolist()},indent=2))
