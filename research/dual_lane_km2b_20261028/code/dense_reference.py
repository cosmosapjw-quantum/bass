"""Small-grid pairwise screen matrix exponential, separate from moment gain.

Uses four-vector Lorentz/gauge maps from the pinned independent oracle.
Bounded reference only; no full N^2 matrix in the primary solver.
"""
from pathlib import Path
import sys
import numpy as np
from scipy.linalg import expm
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'vendor'))
from covariant_oracle import maps4,screen,lorentz

class DenseScreenExponential:
    def __init__(self,op,J0,nu0):
        if len(op.n)>160:raise ValueError('Dense oracle limited to160 directions')
        self.op=op;S,self.ne,self.D=maps4(op.n,op.beta);self.we=op.w/self.D**2
        self.E=screen(self.ne)
        Ye=self.D[:,None,None]**4*np.einsum('nik,nkl,njl->nij',S,J0,S)
        self.x0=np.einsum('nia,nij,njb->nab',self.E,Ye,self.E).ravel()
        T=np.einsum('nia,mib->nmab',self.E,self.E)
        K=(3/(8*np.pi))*np.einsum('nmab,nmdc,m->nadmbc',T,T,self.we).reshape(len(self.x0),len(self.x0))
        self.L=float(nu0)*np.repeat(self.D,4)[:,None]*(K-np.eye(len(self.x0)))
        self.weight=np.repeat(self.we/self.D,4);r=np.sqrt(self.weight)
        sym=r[:,None]*self.L/r[None,:]
        self.weighted_symmetry_residual=float(np.max(abs(sym-sym.T)))
        self.eigenvalues=np.linalg.eigvalsh((sym+sym.T)/2)
        back=lorentz(-op.beta)
        self.back=back[1:,1:]-op.n[:,:,None]*back[0,1:]

    def carrier(self,t):
        if not np.isfinite(t) or t<0:raise ValueError('Require t>=0')
        X=(expm(self.L*float(t))@self.x0).reshape(-1,2,2)
        Ye=np.einsum('nia,nab,njb->nij',self.E,X,self.E)
        return np.einsum('nik,nkl,njl->nij',self.back,Ye,self.back)/self.D[:,None,None]**4
