"""
Q1 · 11유형 통합 군 캐리어 — Rust 코어의 얇은 Python 면 (76차).

★ 중복 금지: 분류 **규칙**의 단일 진실원은 `bianchi.algebra` 다.  이 모듈은
Rust 포트를 감싸고, 시험이 두 경로의 일치를 왕복으로 잰다.  규칙을 여기서
다시 쓰지 않는다 (53차 GateGuard 교훈).

포장 규약 (docs/Q-CONTRACT.md §2):  n = (n11, n22, n33, n12, n13, n23)
"""
from __future__ import annotations

import numpy as np

from bianchi.algebra import TOL as JACOBI_TOL
from bianchi.backend_policy import require_native
from bianchi.q.geometry_identity import (
    GeometryRouteIdentityError,
    validate_native_geometry_identity,
)

N_ORDER = ((0, 0), (1, 1), (2, 2), (0, 1), (0, 2), (1, 2))


def _coerce_n(N):
    try:
        N = np.asarray(N, float)
    except (TypeError, ValueError) as exc:
        raise ValueError("n must be a finite 3-vector or symmetric (3, 3) array") from exc
    if N.ndim == 1:
        if N.shape != (3,):
            raise ValueError("n must have shape (3,) or (3, 3)")
        N = np.diag(N)
    elif N.shape != (3, 3):
        raise ValueError("n must have shape (3,) or (3, 3)")
    if not np.isfinite(N).all():
        raise ValueError("n must be finite")
    if not np.array_equal(N, N.T):
        raise ValueError("n must be exactly symmetric")
    return N


def _pack_valid_n(N):
    return np.array([N[i, j] for i, j in N_ORDER])


def pack_n(N):
    """대칭 (3,3) → 6성분."""
    return _pack_valid_n(_coerce_n(N))


def unpack_n(n6):
    """6성분 → 대칭 (3,3)."""
    try:
        n6 = np.asarray(n6, float)
    except (TypeError, ValueError) as exc:
        raise ValueError("n6 must be a finite six-component array") from exc
    if n6.shape != (6,):
        raise ValueError("n6 must have shape (6,)")
    if not np.isfinite(n6).all():
        raise ValueError("n6 must be finite")
    N = np.zeros((3, 3))
    for v, (i, j) in zip(n6, N_ORDER):
        N[i, j] = N[j, i] = v
    return N


def _validated_geometry_inputs(n, a):
    N = _coerce_n(n)
    try:
        a3 = np.asarray(a, float)
    except (TypeError, ValueError) as exc:
        raise ValueError("a must be a finite three-component array") from exc
    if a3.shape != (3,):
        raise ValueError("a must have shape (3,)")
    if not np.isfinite(a3).all():
        raise ValueError("a must be finite")
    if np.max(np.abs(N @ a3)) > JACOBI_TOL:
        raise ValueError("Jacobi constraint n^ab a_b must vanish within 1e-10")
    return _pack_valid_n(N), a3


def _native_geometry_route(route_id, n, a):
    n6, a3 = _validated_geometry_inputs(n, a)
    rust = require_native(route_id)
    validate_native_geometry_identity(rust.rf02c_execution_identity())
    return rust, n6, a3


def classify(n, a):
    """(n, a) → dict(name, group_class, kappa, exceptional, signature)."""
    rust, n6, a3 = _native_geometry_route("q.group.classify", n, a)
    name, cls, kap, exc, sig, asgn = rust.qg_classify(n6, a3)
    return dict(name=name, group_class=cls, kappa=kap, exceptional=exc,
                signature=(tuple(sig), asgn))


def jacobi_residual(n, a):
    rust, n6, a3 = _native_geometry_route("q.group.jacobi_residual", n, a)
    return np.asarray(rust.qg_jacobi(n6, a3))


def structure_constants(n, a):
    """C^c_{ab} — (3,3,3), 지표 [c][a][b] (algebra.structure_constants 와 동일)."""
    rust, n6, a3 = _native_geometry_route("q.group.structure_constants", n, a)
    return np.asarray(rust.qg_structure_constants(n6, a3)).reshape(3, 3, 3)


def ricci3(n, a):
    rust, n6, a3 = _native_geometry_route("q.group.ricci3", n, a)
    return np.asarray(rust.qg_ricci3(n6, a3)).reshape(3, 3)


def curvature(n, a):
    """(K, ^3S_ab)."""
    rust, n6, a3 = _native_geometry_route("q.group.curvature", n, a)
    v = np.asarray(rust.qg_curvature(n6, a3))
    return float(v[0]), v[1:].reshape(3, 3)


def kappa(n, a):
    rust, n6, a3 = _native_geometry_route("q.group.kappa", n, a)
    return rust.qg_kappa(n6, a3)


def roundtrip(n, a):
    """차트 상태 → 군 캐리어 → 차트 상태.  포장이 비트 왕복인지 재는 용도."""
    _rust, n6, a3 = _native_geometry_route("q.group.roundtrip", n, a)
    return unpack_n(n6), a3
