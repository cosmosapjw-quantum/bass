"""
Q1 · 11유형 통합 군 캐리어 — Rust 코어의 얇은 Python 면 (76차).

★ 중복 금지: 분류 **규칙**의 단일 진실원은 `bianchi.algebra` 다.  이 모듈은
Rust 포트를 감싸고, 시험이 두 경로의 일치를 왕복으로 잰다.  규칙을 여기서
다시 쓰지 않는다 (53차 GateGuard 교훈).

포장 규약 (docs/Q-CONTRACT.md §2):  n = (n11, n22, n33, n12, n13, n23)
"""
from __future__ import annotations

import numpy as np

from bianchi.backend_policy import require_native

N_ORDER = ((0, 0), (1, 1), (2, 2), (0, 1), (0, 2), (1, 2))


def pack_n(N):
    """대칭 (3,3) → 6성분."""
    N = np.asarray(N, float)
    if N.ndim == 1:
        N = np.diag(N)
    return np.array([N[i, j] for i, j in N_ORDER])


def unpack_n(n6):
    """6성분 → 대칭 (3,3)."""
    n6 = np.asarray(n6, float)
    N = np.zeros((3, 3))
    for v, (i, j) in zip(n6, N_ORDER):
        N[i, j] = N[j, i] = v
    return N


def classify(n, a):
    """(n, a) → dict(name, group_class, kappa, exceptional, signature)."""
    n6 = pack_n(n)
    a3 = np.asarray(a, float)
    rust = require_native("q.group.classify")
    name, cls, kap, exc, sig, asgn = rust.qg_classify(n6, a3)
    return dict(name=name, group_class=cls, kappa=kap, exceptional=exc,
                signature=(tuple(sig), asgn))


def jacobi_residual(n, a):
    rust = require_native("q.group.jacobi_residual")
    return np.asarray(rust.qg_jacobi(pack_n(n), np.asarray(a, float)))


def structure_constants(n, a):
    """C^c_{ab} — (3,3,3), 지표 [c][a][b] (algebra.structure_constants 와 동일)."""
    rust = require_native("q.group.structure_constants")
    return np.asarray(rust.qg_structure_constants(
        pack_n(n), np.asarray(a, float))).reshape(3, 3, 3)


def ricci3(n, a):
    rust = require_native("q.group.ricci3")
    return np.asarray(rust.qg_ricci3(pack_n(n), np.asarray(a, float))).reshape(3, 3)


def curvature(n, a):
    """(K, ^3S_ab)."""
    rust = require_native("q.group.curvature")
    v = np.asarray(rust.qg_curvature(pack_n(n), np.asarray(a, float)))
    return float(v[0]), v[1:].reshape(3, 3)


def kappa(n, a):
    rust = require_native("q.group.kappa")
    return rust.qg_kappa(pack_n(n), np.asarray(a, float))


def roundtrip(n, a):
    """차트 상태 → 군 캐리어 → 차트 상태.  포장이 비트 왕복인지 재는 용도."""
    n6 = pack_n(n)
    return unpack_n(n6), np.asarray(a, float)
