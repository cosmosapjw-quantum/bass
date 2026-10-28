"""Declared bounded inputs, not observational fits or cosmological solutions."""
import numpy as np
from . import polarized_dictionary as PD
from .tilted_collision import TiltedThomson, boost_map

def mixed_coefficients():
    return {('I', 0, 0): 2 * np.sqrt(4 * np.pi), ('I', 1, 1): 0.12, ('I', 2, -1): 0.08, ('I', 3, 0): 0.05, ('I', 4, 2): 0.04, ('E', 2, 0): 0.09, ('B', 3, 1): 0.06, ('V', 1, -1): 0.07}

def electron_fixture(beta, n=12, coefficients=None):
    """Fixed GL electron directions mapped to normal; raw transformed weights."""
    g = PD.Grid(n, 2 * n)
    b = np.asarray(beta, float)
    S, nlab, De = boost_map(g.n, -b)
    op = TiltedThomson(nlab, g.w / De ** 2, b)
    Je = PD.synthesize(g, mixed_coefficients() if coefficients is None else coefficients)
    J = De[:, None, None] ** 4 * np.einsum('nik,nkl,njl->nij', S, Je, S)
    return (g, op, J)

def normal_fixture(beta, n=16, coefficients=None):
    """Independent uniform normal grid, common physical electron-frame field."""
    g = PD.Grid(n, 2 * n)
    op = TiltedThomson(g.n, g.w, beta)
    eg = PD.Grid(n, 2 * n)
    eg.n = op.ne.copy()
    eg.theta = np.arccos(np.clip(eg.n[:, 2], -1, 1))
    eg.phi = np.arctan2(eg.n[:, 1], eg.n[:, 0])
    st, ct = (np.sin(eg.theta), np.cos(eg.theta))
    sp, cp = (np.sin(eg.phi), np.cos(eg.phi))
    eg.bt = np.stack([ct * cp, ct * sp, -st], axis=1)
    eg.bp = np.stack([-sp, cp, np.zeros_like(sp)], axis=1)
    eg.P = op.Pe.copy()
    eg._cache = {}
    Je = PD.synthesize(eg, mixed_coefficients() if coefficients is None else coefficients)
    J = np.einsum('nki,nkl,nlj->nij', op.S, Je, op.S) / op.D[:, None, None] ** 4
    return (g, op, J)
