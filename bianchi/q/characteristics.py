"""
Q2 · 특성곡선 커널의 Python 면 (76차).

수식·검증은 `audit/q2_characteristics_general.py` (좌표 측지선 대비 ≤2.1e-14).
여기는 Rust 커널의 얇은 래퍼 + 참조 구현 (비트급 대조용).
"""
from __future__ import annotations

import numpy as np

from bianchi.backend_policy import require_native
from bianchi.q.group import pack_n

SYM = ((0, 0), (1, 1), (2, 2), (0, 1), (0, 2), (1, 2))


def pack_sym(M):
    """대칭 (3,3) 또는 대각 (3,) → 6성분 (11,22,33,12,13,23)."""
    return pack_n(M)


def unpack_sym(v6):
    v6 = np.asarray(v6, float)
    M = np.zeros((3, 3))
    for x, (i, j) in zip(v6, SYM):
        M[i, j] = M[j, i] = x
    return M


class Background:
    """(H, sigma, R, N, A) — sigma·N 은 6성분 포장으로 보관."""

    __slots__ = ("h", "sigma", "rot", "n", "a")

    def __init__(self, h=0.0, sigma=None, rot=None, n=None, a=None):
        self.h = float(h)
        self.sigma = np.zeros(6) if sigma is None else pack_sym(sigma)
        self.rot = np.zeros(3) if rot is None else np.asarray(rot, float)
        self.n = np.zeros(6) if n is None else pack_sym(n)
        self.a = np.zeros(3) if a is None else np.asarray(a, float)

    def args(self):
        return self.h, self.sigma, self.rot, self.n, self.a


# ───────────────────────────────────────────────── 참조 구현 (Python)
def rhs_p_ref(phat, mass, bg: Background):
    """dp̂/dt — 참조 (Rust 와 비트급 대조 대상)."""
    P = np.atleast_2d(np.asarray(phat, float))
    S, N, A = unpack_sym(bg.sigma), unpack_sym(bg.n), bg.a
    p2 = np.sum(P * P, axis=1)
    E = np.sqrt(mass * mass + p2)
    term = (np.cross(P @ N.T, P) + (P @ A)[:, None] * P - p2[:, None] * A[None, :])
    out = (-bg.h * P - P @ S.T
           + np.cross(np.broadcast_to(bg.rot, P.shape), P) + term / E[:, None])
    return out[0] if np.asarray(phat).ndim == 1 else out


def rhs_split_ref(ehat, lnp, mass, bg: Background):
    """(dê/dt, dln p/dt) — 참조."""
    e = np.asarray(ehat, float)
    S, N, A = unpack_sym(bg.sigma), unpack_sym(bg.n), bg.a
    p = np.exp(lnp)
    pe = p / np.sqrt(mass * mass + p * p)
    se = S @ e
    ese = float(e @ se)
    de = (-(se - ese * e) + np.cross(bg.rot, e)
          + pe * (np.cross(N @ e, e) - (A - float(A @ e) * e)))
    return de, -(bg.h + ese)


# ───────────────────────────────────────────────── Rust 면
def rhs_p(phat, mass, bg: Background):
    h, s, r, n, a = bg.args()
    rust = require_native("q.characteristics.rhs_p")
    return np.asarray(rust.qc_rhs_p(np.asarray(phat, float), mass, h, s, r, n, a))


def rhs_split(ehat, lnp, mass, bg: Background):
    h, s, r, n, a = bg.args()
    rust = require_native("q.characteristics.rhs_split")
    v = np.asarray(rust.qc_rhs_split(np.asarray(ehat, float), lnp, mass, h, s, r, n, a))
    return v[:3], float(v[3])


def direction_map(ehat, dt, bg0: Background, bg1: Background = None,
                  mass=0.0, lnp=0.0, substeps=4, renormalize=False):
    """방향격자 (M,3) 를 dt 만큼 (역)추적 → (ê_out (M,3), dln p (M,))."""
    if bg1 is None:
        bg1 = bg0
    E = np.ascontiguousarray(np.asarray(ehat, float).reshape(-1, 3)).ravel()
    h0, s0, r0, n0, a0 = bg0.args()
    h1, s1, r1, n1, a1 = bg1.args()
    rust = require_native("q.characteristics.direction_map")
    out = np.asarray(rust.qc_direction_map(
        E, mass, lnp, h0, s0, r0, n0, a0, h1, s1, r1, n1, a1,
        dt, int(substeps), bool(renormalize)))
    m = E.size // 3
    return out[:3 * m].reshape(m, 3), out[3 * m:]
