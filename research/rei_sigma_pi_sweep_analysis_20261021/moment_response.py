"""Fixed-weight massive stress response from supplied quadrature arrays.

No owner, native library, model preparation, or evolution is imported here.
The owner's dimensionless energy/momentum scales and weight normalization
are retained by taking its arrays directly. See THEORY.md for the derivation.
"""
from __future__ import annotations

import math
import numpy as np


def moment_response(qbar2, mu2, weights, mass, x, b):
    """Return J0, J2, J4, G and analytic J2 derivatives as Python floats.

    ``qbar2`` is a radial vector or column; ``mu2`` an angular vector;
    ``weights`` has shape (radial, angular) and includes both quadrature
    measures and the fixed distribution. Mass and qbar are nondimensionalized
    by the same fixed initial owner scale. Weights must be nonnegative.
    Negative x is allowed for local derivative stencils at x=0.
    """
    q2 = np.asarray(qbar2, dtype=np.float64)
    if q2.ndim == 2 and q2.shape[1] == 1:
        q2 = q2[:, 0]
    u = np.asarray(mu2, dtype=np.float64)
    wgt = np.asarray(weights, dtype=np.float64)
    if q2.ndim != 1 or u.ndim != 1 or wgt.shape != (q2.size, u.size):
        raise ValueError('MOMENT_QUADRATURE_SHAPE')
    if not q2.size or not u.size:
        raise ValueError('MOMENT_EMPTY_QUADRATURE')
    if (not all(math.isfinite(v) for v in (mass, x, b)) or mass < 0
            or not all(np.isfinite(a).all() for a in (q2, u, wgt))
            or np.any(q2 < 0) or np.any(u < 0) or np.any(u > 1)
            or np.any(wgt < 0)):
        raise ValueError('MOMENT_QUADRATURE_DOMAIN')
    r = math.exp(-x)
    perpendicular, parallel = math.exp(2*b), math.exp(-4*b)
    radius2 = perpendicular*(1-u) + parallel*u
    t = parallel*u/radius2
    p2phys = .5*(3*t-1)
    momentum2 = (r*r)*q2[:, None]*radius2[None, :]
    energy2 = mass*mass + momentum2
    if np.any(energy2 <= 0) or not np.isfinite(energy2).all():
        raise ValueError('MOMENT_NONPOSITIVE_OR_NONFINITE_ENERGY')
    energy = np.sqrt(energy2)
    v2 = momentum2/energy2
    weighted_energy = (r**3)*wgt*energy
    stress_kernel = weighted_energy*v2*p2phys[None, :]
    j0 = float(np.sum(weighted_energy))
    j2 = float(np.sum(stress_kernel))
    j4 = float(np.sum(stress_kernel*v2))
    g = float(np.sum(weighted_energy*v2*(
        2*(2-v2)*p2phys[None, :]**2 + 9*t[None, :]*(1-t[None, :]))))
    result = {'J0': j0, 'J2': j2, 'J4': j4, 'G': g,
              'J2_x': -5*j2+j4, 'J2_b': -g,
              'absolute_stress_kernel_sum': float(np.sum(np.abs(stress_kernel)))}
    if not all(math.isfinite(value) for value in result.values()):
        raise FloatingPointError('MOMENT_NONFINITE_RESPONSE')
    return result
