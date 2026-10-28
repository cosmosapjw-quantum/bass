"""Cartesian P8 reference with general N input; no curvature harmonic formula.

Reuses independent Cartesian carrier differentiation, but obtains direction and
screen rates from pinned P8 connection. Not a production Q/Rust execution.
"""
import numpy as np
from .direct_oracle import carrier_with_derivatives
from bianchi.q import polarization as P8

def direct_curved_rhs(g, c, H, S, N, nu=0.0):
    J, Jt, Jp = carrier_with_derivatives(g, c)
    zero = np.zeros(3)
    v = P8.direction_rate(g.n, H, S, zero, N, zero)
    vt = np.einsum('ni,ni->n', v, g.bt)
    vp = np.einsum('ni,ni->n', v, g.bp) / np.sin(g.theta)
    s = np.einsum('ni,ij,nj->n', g.n, S, g.n)
    rhs = -4 * (H + s)[:, None, None] * J + P8.tensor_rate(J, g.n, H, S, zero, N, zero) - vt[:, None, None] * Jt - vp[:, None, None] * Jp
    if nu:
        M = np.einsum('n,nij->ij', g.w, J)
        rhs += nu * (3 / (8 * np.pi) * np.einsum('nia,ab,nbj->nij', g.P, M, g.P) - J)
    return rhs
