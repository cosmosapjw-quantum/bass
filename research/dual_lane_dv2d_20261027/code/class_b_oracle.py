"""Independent Cartesian/P8 and coordinate-Hamiltonian instantaneous checks.
No imports from class_b_streaming or analytic Gaunt assembly.
"""
from __future__ import annotations
from pathlib import Path
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'vendor'))
import polarization as P8
from polarized_dictionary import analyze
from direct_oracle import carrier_with_derivatives,components


def direct_rhs(g,c,A,*,H=0.,S=None,nu=0.):
    J,Jt,Jp=carrier_with_derivatives(g,c)
    S=np.zeros((3,3)) if S is None else np.asarray(S,float)
    A=np.asarray(A,float);z=np.zeros(3);Z=np.zeros((3,3))
    v=P8.direction_rate(g.n,H,S,z,Z,A)
    vt=np.einsum('ni,ni->n',v,g.bt);vf=np.einsum('ni,ni->n',v,g.bp)/np.sin(g.theta)
    s=np.einsum('ni,ij,nj->n',g.n,S,g.n)
    out=-4*(H+s)[:,None,None]*J+P8.tensor_rate(J,g.n,H,S,z,Z,A)-vt[:,None,None]*Jt-vf[:,None,None]*Jp
    if nu:
        M=np.einsum('n,nij->ij',g.w,J)
        out+=nu*(3/(8*np.pi)*np.einsum('nia,ab,nbj->nij',g.P,M,g.P)-J)
    return out


def projected_rhs(g,c,A,*,H=0.,S=None,nu=0.,lout=5):
    return analyze(g,direct_rhs(g,c,A,H=H,S=S,nu=nu),lout)


def coordinate_rate(n,scales,rates,b,z):
    """d p_hat/du from canonical H=sqrt(exp(2bz)(Px/ax)^2+...+(Pz/az)^2).

    x/(cT_star) and u=t/T_star; dimensionless b; A_z=b/az. No tetrad
    connection/direction calls. Initial physical |p_hat|=1.
    Metric spatial part ax²e^-2bz dx²+ay²e^-2bz dy²+az² dz².
    """
    n=np.asarray(n,float);a=np.asarray(scales,float);h=np.asarray(rates,float)
    if a.shape!=(3,) or np.any(a<=0) or h.shape!=(3,):raise ValueError('positive scales and3 rates required')
    P=n*a[None,:];P[:,:2]*=np.exp(-b*z)
    trans=np.exp(2*b*z)*((P[:,0]/a[0])**2+(P[:,1]/a[1])**2)
    energy=np.sqrt(trans+(P[:,2]/a[2])**2)
    zdot=P[:,2]/(a[2]**2*energy)
    Pzdot=-b*trans/energy
    out=-h[None,:]*n
    out[:,:2]+=b*zdot[:,None]*n[:,:2]
    out[:,2]+=Pzdot/a[2]
    return out


def spin_coordinate_rhs(g,c,A,*,H=0.,S=None,connection=True):
    """Local spin form evaluated without Gaunt contraction, for gauge tests."""
    S=np.zeros((3,3)) if S is None else np.asarray(S,float);A=np.asarray(A,float)
    comp=components(g,c);s=np.einsum('ni,ij,nj->n',g.n,S,g.n);alpha=g.n@A
    v=-g.n@S.T+s[:,None]*g.n-A+alpha[:,None]*g.n
    vt=np.einsum('ni,ni->n',v,g.bt);vf=np.einsum('ni,ni->n',v,g.bp)/np.sin(g.theta)
    out={}
    for f,spin in [('I',0),('V',0),('P',2)]:
        x,dt,dp=comp[f];out[f]=-4*(H+s)*x-vt*dt-vf*dp
        if connection:out[f]-=1j*spin*np.cos(g.theta)*vf*x
    return out
