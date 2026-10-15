"""Cancellation-resistant massive FD pressure difference, with original BASS source lock.

This file leaves the source-pinned bianchi/matter/freestream.py and
research/rei_axbi_sigma_matter_20261015/sigma_matter.py unchanged.

For the LRS Bianchi-I metric ds^2=-c^2dt^2+
a^2[e^{-2b}(dx^2+dy^2)+e^{4b}dz^2], one has
DeltaP = P_parallel-P_perp = -(1/2) (partial rho / partial b)_{ln a}.
The exact polynomial angular part is integrated analytically; the remaining
angular denominator difference is evaluated by a rationalized inverse-energy
identity to avoid subtracting almost equal positive pressure integrals.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/"rei_axbi_sigma_matter_20261015"))
from sigma_matter import MassiveMoments


class StableMassiveMoments(MassiveMoments):
    """Source-compatible massive radial/GL quadrature, stabilized DeltaP.

    evaluate_with_delta(x, b, A) returns rho, P_perp, P_parallel, DeltaP.
    Returned rho and principal pressures retain the original FD quadrature;
    DeltaP is separately formed without P_parallel-P_perp subtraction.
    The analytic angular polynomial part is exact for the continuum angular
    integral. The remaining non-polynomial piece uses ORIGINAL GL nodes.
    """

    def evaluate_with_delta(self, x, b, A=0., *, chunk=64):
        xx=np.asarray(x, dtype=float)
        bb=np.asarray(b, dtype=float)
        if (xx.shape != bb.shape or not np.isfinite(xx).all()
                or not np.isfinite(bb).all()
                or np.any(np.abs(bb)>1)
                or not np.isfinite(A) or not -1<=A<=2):
            raise ValueError("finite same-shaped physical chart and positive angular weight")
        if not isinstance(chunk, int) or isinstance(chunk, bool) or not 1<=chunk<=4096:
            raise ValueError("positive bounded chunk")
        shape=xx.shape
        xf=xx.reshape(-1); bf=bb.reshape(-1)
        out=np.empty((4,len(xf)),dtype=float)
        # Angular nodes and radial BASS FD96 remain immutable source inputs.
        z=(self.mu*self.mu)[None,None,:]
        p2=self.p2[None,None,:]
        wz=(self.w*(1+A*self.p2))[None,None,:]
        qr=self.q[None,:,None]
        rw=self.rw[None,:,None]/self.norm
        for lo in range(0,len(xf),chunk):
            hi=min(lo+chunk,len(xf))
            r=np.exp(-xf[lo:hi])[:,None,None]
            beta=bf[lo:hi,None,None]
            q2=(r*qr)**2
            epm1=np.expm1(2*beta)
            ezm1=np.expm1(-4*beta)
            d=epm1*(1-z)+ezm1*z
            E0=np.hypot(self.mass, r*qr)
            E=np.sqrt(E0*E0+q2*d)
            pref=r*r*r
            weights=rw*wz
            out[0,lo:hi]=(pref*weights*E).sum(axis=(1,2))
            # The trace of the pressure is q^2(1+d)/E. Computing
            # Pbar first avoids separate large principal-pressure
            # arrays and permits reconstruction from stable DeltaP.
            pbar=(pref*weights*q2*(1+d)/(3*E)).sum(axis=(1,2))

            # <W P2> = A/5, <W z> = 1/3 + 2A/15:
            # unlike numerical cancellation, zero b, A=0 gives EXACT zero.
            polynomial=(A/5 + ezm1*(1/3+2*A/15)
                        -epm1*(1/3-A/15))
            # Difference of inverse energies via factorization of E^2-E0^2.
            # No subtraction 1/E - 1/E0 occurs.
            inv_diff=-(q2*d)/(E*E0*(E+E0))
            angular_delta=p2+ezm1*z-epm1*(1-z)/2
            tail=(wz*angular_delta*inv_diff).sum(axis=2,keepdims=True)
            # radial integral. Polynomial is independent of angular nodes.
            out[3,lo:hi]=(pref*rw*q2*(polynomial/E0+tail)).sum(axis=(1,2))
            out[1,lo:hi]=pbar-out[3,lo:hi]/3
            out[2,lo:hi]=pbar+2*out[3,lo:hi]/3
        if shape==():
            return tuple(float(t[0]) for t in out)
        return tuple(t.reshape(shape) for t in out)

    def delta_p_stable(self,x,b,A=0.,*,chunk=64):
        return self.evaluate_with_delta(x,b,A,chunk=chunk)[3]

    def initial_linear_susceptibility(self,x):
        """d DeltaP/db at b=0, A=0, exact continuum angular integral."""
        xx=np.asarray(x,dtype=float)
        if not np.isfinite(xx).all():
            raise ValueError("finite logarithmic scale")
        r=np.exp(-xx)[...,None]
        k=(r*self.q)**2
        e0=np.hypot(self.mass,np.sqrt(k))
        val=r[...,0]**3*np.sum((self.rw/self.norm)*k*(
            -2/e0+2*k/(5*e0**3)),axis=-1)
        return float(np.asarray(val).item()) if xx.shape==() else val
