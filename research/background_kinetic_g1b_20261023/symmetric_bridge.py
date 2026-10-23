"""Six-component evaluation of an analytically symmetric kinetic pressure.

Avoid two separately rounded reductions for P_ab and P_ba near isotropic stress.
This is a representation choice, not tolerance widening, density fitting or a
physical positivity projection. The original G1A source remains unchanged.
"""
import numpy as np
from vendor import kinetic as kn, core as bg


def symmetric_moments(k,w,mass):
    k,w,mass,E=kn.packet_arrays(k,w,mass)
    rho=np.sum(w*E);flux=np.einsum('q,qi->i',w,k);v=w/E
    P=np.empty((3,3))
    for a in range(3):
        for b in range(a,3):
            P[a,b]=P[b,a]=np.sum(v*(k[:,a]*k[:,b]))
    p=np.trace(P)/3
    pi=P-p*np.eye(3);pi[2,2]=-pi[0,0]-pi[1,1]
    if not all(np.all(np.isfinite(x)) for x in (rho,flux,p,pi)):
        raise ValueError('moment arithmetic overflow')
    return rho,flux,p,pi


class SymmetricPackets(kn.CoupledPackets):
    def moment_blocks(self,k,w):
        values=[symmetric_moments(k[self.sectors==i],w[self.sectors==i],
                                  self.mass[self.sectors==i]) for i in range(self.ns)]
        return (np.array([x[0] for x in values]),np.array([x[1] for x in values]),
                bg.Source(np.array([x[2] for x in values]),np.array([x[3] for x in values])))
