"""S6c: binary64 replica of the fixed REI owner's two source spectral quadratures.

Owner 0e25846433170d0f420c4cda44a0bedbf02cd177:
  axbi_sources.rs  AxbiSource::new   cell (count, energy) by composite Simpson n=32
  axbi_covariant_transport.rs source_moments  per-cell/per-bin-piece GL8
The native probe reports u_native/(amount*sum pf*E_simpson)-1. Native deposition
uses GL8 ratios, so the probe residual predicted here is the Simpson-32 truncation
of the *reference* cell-mean energy, not a native deposition error. The owner is
read, never modified. Units: eV; shape(E)=E^2/(exp(E/kT)-1), T=50000 K.
"""
from __future__ import annotations
import math
import mpmath as mp

KB_ERG_K = 1.380649e-16
EV_ERG = 1.602176634e-12
EDGES = (13.6, 24.59, 54.42, 100.0)
X8 = (-0.9602898564975363, -0.7966664774136267, -0.5255324099163290, -0.1834346424956498,
      0.1834346424956498, 0.5255324099163290, 0.7966664774136267, 0.9602898564975363)
W8 = (0.1012285362903763, 0.2223810344533745, 0.3137066458778873, 0.3626837833783619,
      0.3626837833783619, 0.3137066458778873, 0.2223810344533745, 0.1012285362903763)
KT = 50000.0*KB_ERG_K/EV_ERG


def shape(e):
    return e*e/math.expm1(e/KT)


def kahan(xs):
    total = corr = 0.0
    for x in xs:
        y = x-corr; nxt = total+y; corr = (nxt-total)-y; total = nxt
    return total


def simpson(lo, hi, n, energy):
    step = (hi-lo)/n; acc = 0.0
    for i in range(n+1):
        e = lo+step*i
        f = shape(e)*(e if energy else 1.0)
        acc += f*(1.0 if i in (0, n) else 2.0 if i % 2 == 0 else 4.0)
    return acc*step/3.0


def gl8(lo, hi):
    c, h = 0.5*(lo+hi), 0.5*(hi-lo)
    n = kahan(W8[i]*h*shape(c+h*X8[i]) for i in range(8))
    u = kahan(W8[i]*h*shape(c+h*X8[i])*(c+h*X8[i]) for i in range(8))
    return n, u


def cells(cps):
    if isinstance(cps, bool) or not isinstance(cps, int) or not 1 <= cps <= 1024:
        raise ValueError('S6C_PANEL_DOMAIN')
    raw = []
    for a, b in zip(EDGES[:-1], EDGES[1:]):
        for j in range(cps):
            lo = a if j == 0 else a*(b/a)**(j/cps)
            hi = b if j+1 == cps else a*(b/a)**((j+1)/cps)
            raw.append((lo, hi, simpson(lo, hi, 32, False), simpson(lo, hi, 32, True)))
    norm = sum(x[2] for x in raw)
    return [(lo, hi, e/c, c/norm) for lo, hi, c, e in raw]


def predicted(cps: int) -> dict:
    """Probe residual predicted from cell quadratures, plus a 40-digit reference."""
    cs = cells(cps)
    simpson_mean = kahan(pf*E for _, _, E, pf in cs)
    gl8_mean = kahan(pf*gl8(lo, hi)[1]/gl8(lo, hi)[0] for lo, hi, _, pf in cs)
    with mp.workdps(40):
        kt = mp.mpf(KT)
        f = lambda e: e*e/mp.expm1(e/kt)
        exact = mp.fsum(mp.mpf(pf)*mp.quad(lambda e: f(e)*e, [lo, hi])/mp.quad(f, [lo, hi])
                        for lo, hi, _, pf in cs)
        return {'cps': cps, 'probe_residual_predicted': gl8_mean/simpson_mean-1,
                'simpson32_vs_exact': float(mp.mpf(simpson_mean)/exact-1),
                'gl8_vs_exact': float(mp.mpf(gl8_mean)/exact-1)}
