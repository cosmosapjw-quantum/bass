"""Exact-current scalar C/E path, integrated spectrally to a bolometric trace.

collision_moving.py is byte-identical to live blob b6ce9740; only sphere_grid
and phase helpers of the archive collision_oracle are used and match live AST.
The scalar oracle is a trace test for initially unpolarized fields, not a
full-polarized finite-time oracle. E is in an arbitrary positive energy scale.
"""
import numpy as np
from bianchi.matter import collision_moving as CM
from bianchi.q import polarization as P8
from . import polarized_dictionary as PD
from .tilted_collision import TiltedThomson, boost_map

def compare(beta, nrad=10):
    beta = np.asarray(beta, float)
    g = PD.Grid(12, 24)
    Amp = 1 + 0.18 * g.n[:, 2] + 0.11 * (g.n[:, 0] ** 2 - g.n[:, 1] ** 2)
    Je = P8.unpolarized(g.n, 6 * Amp)
    S, n, Dinv = boost_map(g.n, -beta)
    w = g.w / Dinv ** 2
    J = Dinv[:, None, None] ** 4 * np.einsum('nik,nkl,njl->nij', S, Je, S)
    op = TiltedThomson(n, w, beta)
    truth = np.trace(op.rhs(J, 1.3), axis1=1, axis2=2)
    x, wx = np.polynomial.laguerre.laggauss(nrad)

    def f(energy, nhat):
        ee, ne = CM.boost_photon(energy, nhat, beta)
        angular = 1 + 0.18 * ne[..., 2] + 0.11 * (ne[..., 0] ** 2 - ne[..., 1] ** 2)
        return np.exp(-ee) * angular
    vals = []
    for j in [0, 19, 75, 151, 231, 287]:
        d = op.D[j]
        C = CM.collision_rate_density(f, x / d, n[j:j + 1], beta, 12, 24, tau_dot=1.3)[:, 0]
        integrated = float(np.sum(wx * x ** 3 * np.exp(x) * C) / d ** 4)
        vals.append({'ray': j, 'D': float(d), 'bolometric_trace': float(truth[j]), 'spectral_integral': integrated, 'error': abs(integrated - truth[j])})
    scale = max(1.0, float(np.max(abs(truth))))
    return {'beta': beta.tolist(), 'nrad': nrad, 'rows': vals, 'scale': scale, 'relative_error': max((v['error'] for v in vals)) / scale}
