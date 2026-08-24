"""
K2b · **tilt 의 허용조건** — 어떤 Bianchi 유형이 tilt 를 담을 수 있는가.

K2 에서 에너지틀 v(t) 를 물질에서 풀어냈다.  그런데 그것을 기하와 결합하려면
**운동량 구속(Codazzi)** 을 만족해야 한다:

    C^a = 3 A_b Σ^{ab} + ε^{abc} N_{bd} Σ_c{}^d − q^a = 0

★ **결과 (측정)**:  Bianchi I 은 N = A = 0 이므로  C^a = −q^a.
  구속이 **q^a = 0 을 강제**한다 — 즉 **Bianchi I 은 tilt 를 담을 수 없다.**
  대각계량에서 G_{0i} ≡ 0 인 것과 같은 말이다 (기하가 운동량밀도를 받을 자리가 없다).

  ⇒ K2 에서 구한 tilt 는 **운동학적으로 옳은 test-field 구성**이지만
    **type I 의 Einstein 해는 아니다**.  이 사실을 명시하지 않으면 K1+K2 통합을
    존재하지 않는 대상 위에 짓게 된다.

★ 더 뾰족한 사실: 대각 N·대각 Σ 이면 **type II 도 담지 못한다** —
  ε^{abc}N_{bd}Σ_c{}^d 가 둘 다 대각일 때 0 이 되기 때문이다.
  담으려면 **A ≠ 0 (class B, 최소는 type V)** 이거나 **비대각 Σ/N** 이 필요하다.

★ 구성적 귀결: 주어진 q 에 대해 type V 에서 A 를 풀 수 있다 (`solve_type_V_A`).
  즉 tilt 를 담는 일관된 구성이 **존재한다** — 다만 type I 이 아닐 뿐이다.
"""
from __future__ import annotations

import numpy as np

from bianchi.conventions import CODAZZI_EPS_SIGN


def _eps():
    e = np.zeros((3, 3, 3))
    for a, b, c in ((0, 1, 2), (1, 2, 0), (2, 0, 1)):
        e[a, b, c] = 1.0
        e[a, c, b] = -1.0
    return e


EPS = _eps()


def constraint_capacity(Sigma, N=None, A=None):
    """기하가 담을 수 있는 운동량밀도:  3A_bΣ^{ab} + ε^{abc}N_{bd}Σ_c{}^d.

    ★ 이 값이 0 이면 그 배경은 q^a ≠ 0 을 **담을 수 없다**.
    """
    S = np.asarray(Sigma, float)
    N = np.zeros((3, 3)) if N is None else np.asarray(N, float)
    A = np.zeros(3) if A is None else np.asarray(A, float)
    term_a = 3.0 * (S @ A)
    term_e = CODAZZI_EPS_SIGN * np.einsum("abc,bd,cd->a", EPS, N, S)
    return term_a + term_e


def codazzi_residual_np(Sigma, N=None, A=None, q=None):
    """C^a = (기하 용량) − q^a.  구속은 C = 0."""
    cap = constraint_capacity(Sigma, N, A)
    return cap if q is None else cap - np.asarray(q, float)


def bianchi_I_capacity(Sigma):
    """★ Bianchi I (N = A = 0) 의 용량 — **항등적으로 0**."""
    return constraint_capacity(Sigma, None, None)


def tilt_is_admissible(Sigma, N=None, A=None, tol=1e-12):
    """이 배경이 0 이 아닌 q 를 담을 수 있는가 (용량이 비자명한가)."""
    return bool(np.abs(constraint_capacity(Sigma, N, A)).max() > tol)


def violation_for_flux(q, Sigma, N=None, A=None):
    """주어진 q 에 대한 구속 위반 크기 |C^a| (정규화된 q 를 넣을 것)."""
    return float(np.abs(codazzi_residual_np(Sigma, N, A, q)).max())


# ═══════════════════════════════════════ 구성적: type V 에서 A 를 푼다
def solve_type_V_A(q, Sigma, rcond=1e-12):
    """★ type V (N = 0, A ≠ 0) 에서 3 Σ^{ab} A_b = q^a 를 A 에 대해 푼다.

    Σ 가 무대각합·대칭이라 특이할 수 있으므로 최소제곱(의사역행렬)으로 푼다.
    반환 dict(A, residual, rank, exact).
    ★ 이것이 "tilt 를 담는 일관된 구성이 존재한다" 는 **구성적 증거**다.
    """
    S = np.asarray(Sigma, float)
    qq = np.asarray(q, float)
    M = 3.0 * S
    A, *_ = np.linalg.lstsq(M, qq, rcond=rcond)
    res = float(np.abs(M @ A - qq).max())
    return dict(A=A, residual=res, rank=int(np.linalg.matrix_rank(M, tol=1e-10)),
                exact=bool(res < 1e-10 * max(np.abs(qq).max(), 1e-300)))


def type_V_consistent_configuration(q, Sigma):
    """주어진 q, Σ 로 type V 구성을 만들고 **Codazzi 잔차를 확인**해 돌려준다."""
    r = solve_type_V_A(q, Sigma)
    C = codazzi_residual_np(Sigma, None, r["A"], q)
    return dict(A=r["A"], codazzi=float(np.abs(C).max()), exact=r["exact"],
                rank=r["rank"])


# ═══════════════════════════════════════ 진단 보고
def admissibility_table(Sigma=None):
    """유형별 용량 표 — **대각 Σ** 에서 무엇이 tilt 를 담는가."""
    S = np.diag([0.06, -0.02, -0.04]) if Sigma is None else np.asarray(Sigma, float)
    rows = [
        ("Bianchi I  (N=0, A=0)", None, None),
        ("Bianchi II (N=diag)", np.diag([1.0, 0.0, 0.0]), None),
        ("Bianchi VII0 (N=diag)", np.diag([1.0, 1.0, 0.0]), None),
        ("Bianchi IX (N=diag)", np.diag([1.0, 1.0, 1.0]), None),
        ("Bianchi V  (A≠0)", None, np.array([0.0, 0.0, 0.7])),
        ("Bianchi II (N 비대각)", np.array([[0.0, 1.0, 0.0],
                                            [1.0, 0.0, 0.0],
                                            [0.0, 0.0, 0.0]]), None),
    ]
    out = []
    for name, N, A in rows:
        cap = constraint_capacity(S, N, A)
        out.append((name, cap, float(np.abs(cap).max())))
    return out
