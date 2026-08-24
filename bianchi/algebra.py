"""
PR-04 · Lie 대수 구조와 Bianchi 유형 분류기.

  * 대각 게이지 경로:  (n1,n2,n3,A) -> (class, type, kappa)
  * 기저 독립 경로  :  (N_ab, A_a)  -> 같은 결과
      kappa = (1/2)[(tr N)^2 - tr(N^2)] / (A.A)
    Layer 0 (Fermi 게이지) 에서는 n2,n3 가 개별 변수로 존재하지 않으므로
    반드시 기저 독립형을 써야 한다.

  * 예외형 판정은 kappa == -9 를 상수로 박지 않고 **구속 퇴화**로 한다:
      det L = 3 (9 A^2 + n2 n3)   (L: off-diagonal shear 에 대한 Codazzi 행렬)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import jax.numpy as jnp
import numpy as np

from bianchi.conventions import EPS3

TOL = 1e-10


@dataclass(frozen=True)
class BianchiType:
    name: str
    group_class: str          # "A" | "B"
    kappa: Optional[float]    # class B 만 유한; class A 는 None
    exceptional: bool = False
    signature: tuple = ()     # (n 고윳값 부호들, sign(A))

    def __str__(self) -> str:
        k = "" if self.kappa is None else f", kappa={self.kappa:+.6g}"
        e = " [예외형]" if self.exceptional else ""
        return f"Bianchi {self.name} (class {self.group_class}{k}){e}"


def _sgn(x, tol=TOL):
    return 0 if abs(x) < tol else (1 if x > 0 else -1)


# ---------------------------------------------------------------- 구조상수
def structure_constants(n, a):
    """C^k_{ij} = eps_{ijd} n^{dk} + a_i delta^k_j - a_j delta^k_i."""
    n = np.asarray(n, float); a = np.asarray(a, float)
    if n.ndim == 1:
        n = np.diag(n)
    C = np.zeros((3, 3, 3))
    for k in range(3):
        for i in range(3):
            for j in range(3):
                C[k, i, j] = (
                    sum(EPS3[i, j, d] * n[d, k] for d in range(3))
                    + a[i] * (k == j) - a[j] * (k == i)
                )
    return C


def decompose(C):
    """구조상수 -> (n_ab, a_a). structure_constants 의 역."""
    C = np.asarray(C, float)
    a = np.array([0.5 * sum(C[b, al, b] for b in range(3)) for al in range(3)])
    n = np.zeros((3, 3))
    for e in range(3):
        for al in range(3):
            n[e, al] = (
                0.5 * sum(C[al, b, c] * EPS3[b, c, e] for b in range(3) for c in range(3))
                - sum(a[b] * EPS3[b, al, e] for b in range(3))
            )
    return 0.5 * (n + n.T), a


def jacobi_residual(n, a):
    """Jacobi 항등식 n^{ab} a_b = 0 의 잔차."""
    n = np.asarray(n, float); a = np.asarray(a, float)
    if n.ndim == 1:
        n = np.diag(n)
    return n @ a


# ---------------------------------------------------------------- kappa
def kappa_from_diagonal(n2, n3, A):
    """kappa = n2 n3 / A^2. A=0 (class A) 이면 None."""
    if abs(A) < TOL:
        return None
    return float(n2 * n3) / float(A) ** 2


def kappa_basis_independent(N, A):
    """kappa = (1/2)[(tr N)^2 - tr(N^2)] / (A.A).

    Jacobi (N^{ab}A_b = 0) 가 A-방향 고윳값을 죽이므로 N 의 제2 불변량이
    곧 n2 n3 다. 대각 게이지에서 n2*n3 로 환원됨을 테스트로 확인한다.
    """
    N = np.asarray(N, float); A = np.asarray(A, float)
    if N.ndim == 1:
        N = np.diag(N)
    a2 = float(A @ A)
    if a2 < TOL ** 2:
        return None
    second = 0.5 * (np.trace(N) ** 2 - np.trace(N @ N))
    return float(second) / a2


def det_L(n2, n3, A):
    """Codazzi 의 off-diagonal shear 행렬 행렬식. det L = 3(9A^2 + n2 n3).

    0 이면 예외형 (구속 rank 저하). kappa = -9 와 동치이나, 이쪽이 1차 원리.
    """
    return 3.0 * (9.0 * float(A) ** 2 + float(n2) * float(n3))


# ---------------------------------------------------------------- 분류
_CLASS_A = {
    (0, 0, 0): "I",
    (1, 0, 0): "II",
    (1, -1, 0): "VI_0",
    (1, 1, 0): "VII_0",
    (1, 1, -1): "VIII",
    (1, 1, 1): "IX",
}


def classify(n, a) -> BianchiType:
    """(n, a) -> BianchiType. n 은 (3,) 대각 또는 (3,3) 대칭."""
    n_arr = np.asarray(n, float); a_arr = np.asarray(a, float)
    if n_arr.ndim == 1:
        n_mat = np.diag(n_arr)
    else:
        n_mat = 0.5 * (n_arr + n_arr.T)

    if not (np.isfinite(n_mat).all() and np.isfinite(a_arr).all()):
        return BianchiType("non-finite", "?", None, False, ((), 0))
    if np.abs(jacobi_residual(n_mat, a_arr)).max() > 1e-8:
        raise ValueError(
            f"Jacobi 항등식 위반: n^ab a_b = {jacobi_residual(n_mat, a_arr)}"
        )

    eig = np.linalg.eigvalsh(n_mat)
    signs = sorted(_sgn(x) for x in eig)
    a_norm = float(np.linalg.norm(a_arr))

    # ---- class A ----
    if a_norm < TOL:
        key = tuple(sorted((abs(s) for s in signs), reverse=True))
        # 부호 패턴으로 식별 (전체 부호 반전은 같은 유형)
        pos = sum(1 for s in signs if s > 0)
        neg = sum(1 for s in signs if s < 0)
        zero = sum(1 for s in signs if s == 0)
        if zero == 3:
            name = "I"
        elif zero == 2:
            name = "II"
        elif zero == 1:
            name = "VI_0" if (pos == 1 and neg == 1) else "VII_0"
        else:
            name = "IX" if (pos == 3 or neg == 3) else "VIII"
        return BianchiType(name, "A", None, False, (tuple(signs), 0))

    # ---- class B ----
    # A 방향을 e1 로: n 의 A-방향 성분은 Jacobi 로 0
    ahat = a_arr / a_norm
    # A 에 직교하는 2x2 블록의 고윳값 = (n2, n3)
    P = np.eye(3) - np.outer(ahat, ahat)
    sub = P @ n_mat @ P
    ev = np.linalg.eigvalsh(sub)
    # A 방향 고윳값(=0)을 제거: |고윳값| 최소인 것 하나를 뺀다
    order = np.argsort(np.abs(ev))
    n2, n3 = float(ev[order[1]]), float(ev[order[2]])

    kap = kappa_basis_independent(n_mat, a_arr)
    s2, s3 = _sgn(n2), _sgn(n3)
    exceptional = abs(det_L(n2, n3, a_norm)) < 1e-8 * max(1.0, 9 * a_norm ** 2)

    if s2 == 0 and s3 == 0:
        name = "V"
    elif s2 == 0 or s3 == 0:
        name = "IV"
    elif s2 * s3 < 0:
        name = "III" if abs(kap + 1.0) < 1e-8 else "VI_h"
    else:
        name = "VII_h"
    if exceptional:
        name = "VI*_-1/9"
    return BianchiType(name, "B", kap, exceptional, (tuple(sorted([s2, s3])), 1))


# ---------------------------------------------------------------- 진단
def type_drift(N, A, kappa0=None):
    """Layer 0 런타임 진단: 유형 표류를 감지한다.

    반환: dict(n 고윳값 부호, |A|, kappa, Jacobi 잔차, kappa 상대오차)
    """
    N = np.asarray(N, float); A = np.asarray(A, float)
    if N.ndim == 1:
        N = np.diag(N)
    kap = kappa_basis_independent(N, A)
    out = {
        "n_eig_signs": tuple(_sgn(x) for x in np.linalg.eigvalsh(N)),
        "A_norm": float(np.linalg.norm(A)),
        "kappa": kap,
        "jacobi_res": float(np.abs(jacobi_residual(N, A)).max()),
    }
    if kappa0 is not None and kap is not None and abs(kappa0) > TOL:
        out["kappa_rel_err"] = abs(kap / kappa0 - 1.0)
    return out


#: 11개 유형 + 예외형의 표준 대표점 (테스트/스캔 시드용)
CANONICAL = {
    "I":         (np.array([0.0, 0.0, 0.0]), np.zeros(3)),
    "II":        (np.array([1.0, 0.0, 0.0]), np.zeros(3)),
    "VI_0":      (np.array([0.0, 1.0, -1.0]), np.zeros(3)),
    "VII_0":     (np.array([0.0, 1.0, 1.0]), np.zeros(3)),
    "VIII":      (np.array([-1.0, 1.0, 1.0]), np.zeros(3)),
    "IX":        (np.array([1.0, 1.0, 1.0]), np.zeros(3)),
    "V":         (np.array([0.0, 0.0, 0.0]), np.array([1.0, 0.0, 0.0])),
    "IV":        (np.array([0.0, 0.0, 1.0]), np.array([1.0, 0.0, 0.0])),
    "III":       (np.array([0.0, 1.0, -1.0]), np.array([1.0, 0.0, 0.0])),
    "VI_h":      (np.array([0.0, 1.0, -1.0]), np.array([0.5, 0.0, 0.0])),   # kappa=-4
    "VII_h":     (np.array([0.0, 1.0, 1.0]), np.array([0.5, 0.0, 0.0])),    # kappa=+4
    "VI*_-1/9":  (np.array([0.0, 3.0, -3.0]), np.array([1.0, 0.0, 0.0])),   # kappa=-9
}
