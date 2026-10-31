"""Pure characteristic and Gaussian-bin routines, no BASS imports (independent checks)."""
from __future__ import annotations
import math
import numpy as np
from numpy.polynomial.legendre import leggauss, legvander, Legendre
from scipy.special import ndtr


def partial_gauss_integration(order: int):
    """Nodes, full weights, and exact polynomial partial integrals on [-1,xi]."""
    if not 3 <= int(order) <= 16:
        raise ValueError("bounded quadrature order 3..16")
    nodes, weights = leggauss(order)
    V = legvander(nodes, order-1)
    I = np.stack([Legendre.basis(k).integ()(nodes)
                  - Legendre.basis(k).integ()(-1.) for k in range(order)], axis=1)
    partial = np.linalg.solve(V.T, I.T).T
    if np.max(np.abs(partial @ np.ones(order)-(nodes+1))) > 2e-12:
        raise ArithmeticError("GL partial integration fails constant")
    if np.max(np.abs(partial @ nodes-(nodes**2-1)/2)) > 2e-12:
        raise ArithmeticError("GL partial integration fails linear")
    return nodes, weights, partial


def static_green_energy(h: float, source: float, duration: float):
    if not h>0 or not source>=0 or not duration>=0:
        raise ValueError("bad static Green function")
    return source*(-math.expm1(-4*h*duration))/(4*h)


def summarize_packets(y_centers, sigmas, energy, directions, angular_weights,
                      *, red_cut=-.01):
    """Analytic Doppler Gaussian frequency moments, no histogram discretization."""
    y=np.asarray(y_centers,float)
    sig=np.asarray(sigmas,float).reshape(-1,1)
    p=np.asarray(energy,float)
    n=np.asarray(directions,float)
    w=np.asarray(angular_weights,float)
    if y.shape != p.shape or sig.shape!=(len(p),1) or n.shape!=(p.shape[1],3):
        raise ValueError("packet dimension mismatch")
    if not np.all(np.isfinite(p)) or np.min(p)<0 or np.min(sig)<=0 or np.min(w)<=0:
        raise ValueError("nonphysical packet energy/width/weights")
    ray_energy=p.sum(axis=0)
    total=float(w @ ray_energy)
    if total<=0:raise ArithmeticError("line tracer should contain physical photons")
    weighted=p*w[None,:]
    mean=float(np.sum(weighted*y)/total)
    second=float(np.sum(weighted*(y*y+sig*sig))/total)
    variance=max(0.,second-mean*mean)
    red_raw=float(np.sum(weighted*ndtr((red_cut-y)/sig))/total)
    # A normalized positive weighted probability may exceed 1 by one ulp
    # on different BLAS/reduction schedules. Reject substantive violations.
    if not -2e-13<=red_raw<=1+2e-13:
        raise ArithmeticError("unphysical escaped line red-wing probability")
    red=float(min(1.0,max(0.0,red_raw)))
    momentum=np.einsum("n,ni->i",w*ray_energy,n)
    tensor=np.einsum("n,ni,nj->ij",w*ray_energy,n,n)/total
    quad=tensor-np.eye(3)/3
    return {"rho":total,"q":momentum.tolist(),
            "mean_log_nu":mean,"std_log_nu":math.sqrt(variance),
            "redwing_fraction":red,"quadrupole_frob":float(np.linalg.norm(quad)),
            "quadrupole":quad.tolist(),"ray_energy":ray_energy}


def gaussian_bin_histogram(y_centers,sigmas,energy,directions_weight,
                           edges, *, neighbor=2):
    """Actual Gaussian CDF bin integrals, measuring any lost frequency tail."""
    y=np.asarray(y_centers,float)
    sig=np.asarray(sigmas,float).reshape(-1,1)
    p=np.asarray(energy,float)
    w=np.asarray(directions_weight,float)
    edges=np.asarray(edges,float)
    if y.shape!=p.shape or sig.shape!=(len(p),1) or len(w)!=p.shape[1]:
        raise ValueError("bad histogram packet dimensions")
    if len(edges)<5 or not np.all(np.diff(edges)>0):raise ValueError("bad logfreq edges")
    if np.max(sig)>0.20*np.min(np.diff(edges)):
        raise ValueError("Doppler Gaussian unresolved by bounded bin-neighbor integration")
    yy=y.reshape(-1)
    ss=np.broadcast_to(sig,y.shape).reshape(-1)
    pp=(p*w[None,:]).reshape(-1)
    if not np.all((yy>edges[0]+10*ss)&(yy<edges[-1]-10*ss)):
        raise ValueError("frequency histogram support excludes escaped photons")
    nb=len(edges)-1
    inds=np.searchsorted(edges,yy,side="right")-1
    hist=np.zeros(nb)
    for j in range(-neighbor,neighbor+1):
        pos=inds+j
        mask=(pos>=0)&(pos<nb)
        ix=pos[mask]
        prob=ndtr((edges[ix+1]-yy[mask])/ss[mask])-ndtr((edges[ix]-yy[mask])/ss[mask])
        hist+=np.bincount(ix,weights=pp[mask]*prob,minlength=nb)
    total=float(np.sum(pp))
    residual=float(abs(np.sum(hist)-total)/max(total,1.e-300))
    return hist,residual
