"""Independent Cartesian P8 oracle, using preserved finite-sum derivatives.

No Gaunt/coupling construction. All angular weights are raw GL weights. No
renormalization to remove class-B geometric energy/flux divergence terms.
"""
from pathlib import Path
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'vendor'))
import polarization as P8
from direct_oracle import carrier_with_derivatives,components


def direct_rhs(g,c,A,H=0.,S=None,nu=0.):
    S=np.zeros((3,3)) if S is None else np.asarray(S,float)
    A=np.asarray(A,float);J,Jt,Jp=carrier_with_derivatives(g,c)
    z=np.zeros(3);Z=np.zeros((3,3))
    v=P8.direction_rate(g.n,H,S,z,Z,A)
    vt=np.einsum('ni,ni->n',v,g.bt);vp=np.einsum('ni,ni->n',v,g.bp)/np.sin(g.theta)
    shear=np.einsum('ni,ij,nj->n',g.n,S,g.n)
    out=-4*(H+shear)[:,None,None]*J+P8.tensor_rate(J,g.n,H,S,z,Z,A)-vt[:,None,None]*Jt-vp[:,None,None]*Jp
    if nu:
        M=np.einsum('n,nij->ij',g.w,J)
        out+=nu*(3/(8*np.pi)*np.einsum('nia,ab,nbj->nij',g.P,M,g.P)-J)
    return out


def spin_coordinate_rhs(g,c,A,H=0.,S=None,connection=True):
    S=np.zeros((3,3)) if S is None else np.asarray(S,float);A=np.asarray(A,float)
    comp=components(g,c);shear=np.einsum('ni,ij,nj->n',g.n,S,g.n)
    v=-g.n@S.T+shear[:,None]*g.n+(g.n@A)[:,None]*g.n-A
    vt=np.einsum('ni,ni->n',v,g.bt);vp=np.einsum('ni,ni->n',v,g.bp)/np.sin(g.theta)
    out={}
    for f,s in [('I',0),('V',0),('P',2)]:
        x,dt,dp=comp[f];out[f]=-4*(H+shear)*x-vt*dt-vp*dp
        if connection:out[f]-=1j*s*np.cos(g.theta)*vp*x
    return out
