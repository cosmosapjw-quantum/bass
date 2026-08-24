"""
Q4/Q5 · 반경층 + 반-라그랑주 수송의 Python 면 (76차).

수식·설계: PLAN-Q §Q4/§Q5.  Rust 가 본체, 여기는 조립·검증 보조.
"""
from __future__ import annotations

import numpy as np

from bianchi.q.characteristics import Background


def radial(lnp_min=-5.0, lnp_max=5.0, n=96):
    import bianchi_rustcore as R
    return R.QRadial(lnp_min, lnp_max, n)


def plan(sph, bg0: Background, bg1: Background = None, dt=0.01, rad=None,
         mass=0.0, lnp_ref=0.0, substeps=4, k_theta=6, k_phi=6, k_rad=8):
    """한 스텝의 수송 계획 (스텝당 1회; 전 반경·전 무질량종 공유)."""
    import bianchi_rustcore as R
    if bg1 is None:
        bg1 = bg0
    h0, s0, r0, n0, a0 = bg0.args()
    h1, s1, r1, n1, a1 = bg1.args()
    return R.qt_plan_step(sph, rad, h0, s0, r0, n0, a0, h1, s1, r1, n1, a1,
                          dt, mass, lnp_ref, int(substeps),
                          int(k_theta), int(k_phi), int(k_rad))


def free_stream_mode_a(sph, G, bg0, bg1=None, dt=0.01, weight_n=4.0, **kw):
    p = plan(sph, bg0, bg1, dt, **kw)
    return np.asarray(p.apply_mode_a(np.ascontiguousarray(G, float), weight_n)), p


def planck_lnf(rad_grid, T=1.0):
    """ln f_BB(p/T) — Mode B 초기조건 (Wien·RJ 양끝 해석 확장과 정합)."""
    p = np.asarray(rad_grid.p())
    return np.log(1.0 / np.expm1(p / T))


def mode_b_state(sph, rad_grid, lnf_of_p, aniso=None):
    """f[i*n_p + j] (방향-주).  aniso(ê) 가 있으면 방향별 배율."""
    e = np.asarray(sph.ehat()).reshape(-1, 3)
    base = np.exp(np.asarray(lnf_of_p, float))
    if aniso is None:
        amp = np.ones(len(e))
    else:
        amp = np.asarray([aniso(ei) for ei in e], float)
    return (amp[:, None] * base[None, :]).ravel()


def mode_b_moments(sph, rad_grid, f):
    """(rho, q, pi) — 반경 적분 후 각 구적 (절단 없음)."""
    import bianchi_rustcore as R  # noqa: F401
    m = int(sph.n)
    n_p = int(rad_grid.n)
    F = np.asarray(f, float).reshape(m, n_p)
    p = np.asarray(rad_grid.p())
    dl = float(rad_grid.dlnp)
    wt = np.ones(n_p); wt[0] = wt[-1] = 0.5
    G = (F * (p ** 4)[None, :] * wt[None, :]).sum(axis=1) * dl
    from bianchi.q import sphere as S
    return S.moments(sph, G)
