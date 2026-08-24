"""
H2-Rust · PSTF 사영자의 Rust 코드생성.

`bianchi.matter.hierarchy` 의 직교사영을 Rust 로 옮기기 위해, 대각합 부분공간 기저
A_l (3^l × n_b) 와 그 최소자승 해 연산자 `S_l = (AᵀA)⁻¹Aᵀ` (n_b × 3^l) 를 미리 계산해
`_rustcore/src/kinetic/pstf_gen.rs` 로 내보낸다.  Rust 는 `P T = T − A (S T)` 만 하면 된다.

**l ≤ 4 로 제한하는 근거 (측정)**: 계층 궤적의 l_max 수렴이
    l_max=2 → π 오차 4.9e−5,  l_max=4 → 8.2e−9,  l_max=6 → 6.9e−9
이므로 l_max=4 에서 이미 수렴했다.  l=6 까지 내보내면 데이터가 2·729·15 ≈ 22k 개로
커지는데, 수렴 측정이 그 필요를 부정한다 (Python 쪽은 l≤6 유지).

사용:  python -m scripts.codegen_pstf
"""
from __future__ import annotations

import os

import numpy as np
import sympy as sp

from bianchi.matter import hierarchy as H

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_OUT = os.path.join(_ROOT, "_rustcore", "src", "kinetic", "pstf_gen.rs")

L_MAX_RUST = 5


def fmt(vals):
    return ", ".join(repr(float(v)) for v in vals)


def _rational_trace_basis(A: np.ndarray) -> sp.Matrix:
    """Recover the exact permutation-average entries behind a float basis."""
    return sp.Matrix(
        [
            [sp.Rational(float(value)).limit_denominator(720) for value in row]
            for row in np.asarray(A, dtype=np.float64)
        ]
    )


def canonical_trace_basis(A: np.ndarray) -> np.ndarray:
    """Round the permutation-average basis back to its exact rational values."""
    exact = _rational_trace_basis(A)
    canonical = np.asarray(exact.tolist(), dtype=np.float64)
    error = float(np.max(np.abs(canonical - np.asarray(A, dtype=np.float64))))
    if error > 2.0 * np.finfo(np.float64).eps:
        raise ValueError(f"trace-subspace rational reconstruction error {error}")
    return canonical


def exact_left_inverse(A: np.ndarray) -> np.ndarray:
    """Return ``(A.T A)^-1 A.T`` from exact rational trace-basis entries.

    The trace-subspace basis is built only from permutation averages, so every
    entry is rational.  Reconstructing those small denominators before the
    solve removes the SVD/LAPACK backend from the generated-byte contract while
    preserving the unique orthogonal projector and its normalization.
    """
    exact = _rational_trace_basis(A)
    if exact.rank() != exact.cols:
        raise ValueError("trace-subspace basis is not full column rank")
    left_inverse = (exact.T * exact).inv() * exact.T
    if left_inverse * exact != sp.eye(exact.cols):
        raise AssertionError("exact PSTF left-inverse identity failed")
    return np.asarray(left_inverse.tolist(), dtype=np.float64)


def generate() -> str:
    lines = [
        "//! H2 · PSTF 사영자 데이터 — **자동생성** (수정 금지).",
        "//!",
        "//! 생성기: `scripts/codegen_pstf.py`",
        "//! 소스:   `bianchi.matter.hierarchy` 의 직교사영",
        "//!",
        "//! 대칭 rank-l 텐서는 PSTF ⊕ sym(δ⊗rank(l-2)) 로 직교분해된다.",
        "//! A_l: 대각합 부분공간 기저 (3^l × nb),  S_l = (AᵀA)⁻¹Aᵀ (nb × 3^l).",
        "//! 사영:  P T = T - A (S T).",
        "//!",
        f"//! l ≤ {L_MAX_RUST} 만 내보낸다 — 궤적 l_max 수렴 측정(l_max=4 에서 8.2e-9)이 근거.",
        "",
        "#![allow(clippy::all)]",
        "",
        f"pub const L_MAX: usize = {L_MAX_RUST};",
        "",
    ]
    for l in range(2, L_MAX_RUST + 1):
        A = canonical_trace_basis(H._trace_subspace(l))  # (3^l, nb), exact rational
        S = exact_left_inverse(A)                      # (nb, 3^l), BLAS-independent
        nb = A.shape[1]
        dim = A.shape[0]
        # 정확성 자체검증: P 가 실제로 대각합을 없애는지
        rng = np.random.default_rng(l)
        T = H._symmetrize(rng.normal(size=(3,) * l)).ravel()
        P = T - A @ (S @ T)
        resid = np.abs(np.trace(P.reshape((3,) * l), axis1=-2, axis2=-1)).max()
        assert resid < 1e-10, (l, resid)
        lines += [
            f"/// l={l}: 기저 차원 nb={nb}, 텐서 차원 3^{l}={dim}  (정확 유리수 좌역 검증)",
            f"pub const NB_{l}: usize = {nb};",
            f"pub const A_{l}: [f64; {dim * nb}] = [{fmt(A.ravel(order='C'))}];",
            f"pub const S_{l}: [f64; {nb * dim}] = [{fmt(S.ravel(order='C'))}];",
            "",
        ]
    return "\n".join(lines)


def main():
    src = generate()
    os.makedirs(os.path.dirname(_OUT), exist_ok=True)
    with open(_OUT, "w") as f:
        f.write(src)
    n = sum(3 ** l * H._trace_subspace(l).shape[1] * 2 for l in range(2, L_MAX_RUST + 1))
    print(f"wrote {_OUT}  (l=2..{L_MAX_RUST}, {n} floats, {len(src)} bytes)")


if __name__ == "__main__":
    main()
