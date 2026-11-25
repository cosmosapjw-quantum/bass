"""Positive piecewise frequency hats and equilibrium-consistent activity."""
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.constants import h,k as k_B
def project(b,n,nu0,dnu,z0):
    # Separate per-owner-cell piecewise hat volumes and quadrature nodes.
    q,w=leggauss(48);q=(q+1)/2;w=w/2
    x=b[:,0,None]+(b[:,1]-b[:,0])[:,None]*np.arange(n+1)[None,:]/n
    xx=(x[:,:-1,None]+np.diff(x,axis=1)[:,:,None]*q).reshape(35,-1)
    nu=nu0+dnu*xx;zr=np.exp(-h*nu/(k_B*3000.))/z0
    d=(np.diff(x,axis=1)[:,:,None]*w).reshape(35,-1)*(nu/nu0)**2
    H=np.zeros((35,n+1,n*len(q)))
    for j in range(n):
        H[:,j,j*len(q):(j+1)*len(q)]=d[:,j*len(q):(j+1)*len(q)]*(1-q)
        H[:,j+1,j*len(q):(j+1)*len(q)]=d[:,j*len(q):(j+1)*len(q)]*q
    g=H.sum(axis=2);W=H/g[:,:,None];z=np.einsum('inq,iq->in',W,zr)
    return x,xx,zr,W,g,z
def inverse_be(f,zr,W,z):
    # Normalize activity by z0, avoid 1e17 large alpha in iteration.
    # Solve exact finite-occupancy hat-mean, not f/(1+f)/mean(z).
    alpha=f/(1+f)/z[...,None]
    for _ in range(12):
        u=zr[:,None,:,None]*alpha[:,:,None,:]
        # quadrature nodes outside each hat support may exceed pole;
        # only supported nodes enter this integral.
        mask=W[:,:,:,None]>0
        assert np.all(u[mask.repeat(f.shape[-1],axis=-1)]<1)
        u=np.where(mask,u,0.)
        value=np.sum(W[:,:,:,None]*u/(1-u),axis=2)
        deriv=np.sum(W[:,:,:,None]*zr[:,None,:,None]/(1-u)**2,axis=2)
        delta=(value-f)/deriv
        alpha-=delta
        if np.max(abs(delta)/np.maximum(abs(alpha),1e-300))<4e-16:break
    return alpha
