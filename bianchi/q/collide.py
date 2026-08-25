"""
Q7 · 정확 충돌 지수의 Python 면 + 참조 구현 (76차).

    exp(x C) f = P₀f + e^{−x}(f − P₀f − P₂f) + e^{−0.9x} P₂f,  x = νΔτ

★ k_l 하드코딩 금지: `kernel_eigenvalues` 가 수치 구적으로 재계산한다.
"""
from __future__ import annotations

import numpy as np

from bianchi.backend_policy import require_native

KERNELS = ("thomson", "bgk", "bgk_cons")
ACTIVE = {"thomson": ((0, 1.0), (2, 0.1)),
          "bgk": ((0, 1.0),),
          "bgk_cons": ((0, 1.0), (1, 1.0))}


def kernel_eigenvalues(l_max=6):
    rust = require_native("q.collide.kernel_eigenvalues")
    return np.asarray(rust.qx_kernel_eigenvalues(l_max))


def kernel_eigenvalues_ref(l_max=6):
    """참조: k_l = 2π ∫ K(x) P_l(x) dx,  K = (3/16π)(1+x²)."""
    from numpy.polynomial.legendre import leggauss, legval
    x, w = leggauss(64)
    K = (3.0 / (16.0 * np.pi)) * (1.0 + x ** 2)
    out = []
    for l in range(l_max + 1):
        c = np.zeros(l + 1); c[l] = 1.0
        out.append(2.0 * np.pi * float((w * K * legval(x, c)).sum()))
    return np.asarray(out)


def collide(sph, f, nu_dt, kernel="thomson"):
    rust = require_native("q.collide.collide")
    return np.asarray(rust.qx_collide(sph, np.ascontiguousarray(f, float),
                                      float(nu_dt), kernel))


def collide_modeb(sph, f, n_p, nu_dt, kernel="thomson"):
    rust = require_native("q.collide.collide_modeb")
    return np.asarray(rust.qx_collide_modeb(sph, np.ascontiguousarray(f, float),
                                            int(n_p), float(nu_dt), kernel))


def collide_ref(sph, f, nu_dt, kernel="thomson"):
    """참조 3항 구현 (Rust 대조용)."""
    f = np.asarray(f, float)
    if nu_dt <= 0:
        return f.copy()
    em = np.exp(-nu_dt)
    out = em * f
    for l, kl in ACTIVE[kernel]:
        pl = np.asarray(sph.project_l(np.ascontiguousarray(f), l))
        out = out + (np.exp(nu_dt * (kl - 1.0)) - em) * pl
    return out


def dense_operator(sph):
    """dense M_ij = w_j K(ê_i·ê_j) — 심판용 (O(M²), 작은 격자에서만)."""
    from bianchi.q import sphere as S
    e, w = S.nodes(sph)
    c = e @ e.T
    return (3.0 / (16.0 * np.pi)) * (1.0 + c ** 2) * w[None, :]


def dense_expm_apply(M, f, x, tol=1e-18, max_terms=400):
    """e^{x(M−I)} f = e^{−x} Σ xᵏMᵏf/k! — Taylor 심판."""
    term = np.asarray(f, float).copy()
    acc = term.copy()
    for k in range(1, max_terms):
        term = (M @ term) * (x / k)
        acc = acc + term
        if np.abs(term).max() < tol:
            break
    return np.exp(-x) * acc
