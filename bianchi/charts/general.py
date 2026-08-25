"""
PR-11 · Layer 0 일반 직교틀 차트 (Fermi 게이지 R=0 기본).

상태: Sigma_ab (5, trace-free) + N_ab (6, 대칭) + A_a (3)  [+ 물질은 args 로 주입]

  Sigma_ab' = -(2-q) Sigma_ab - ^3S_ab + Pi_ab + [W, Sigma]
  N_ab'     = q N_ab + 2 Sigma_(a^d N_b)d      + [W, N]
  A_a'      = q A_a - Sigma_a^b A_b            + W A
  W_ab      = -eps_abc R_c        (COMMUTATOR 규약; conventions.rotation_matrix)

곡률은 구조상수에서 **직접** 계산한다 (Koszul -> Riemann -> Ricci), 전사 없음.

LIMITATIONS
  - Fermi 게이지에서 N_ab 가 비대각으로 진화하므로 **유형 부호 보존이 근사적**이다.
    Layer 1 (class_a/class_b) 의 곱셈구조 정확 보존을 대체하지 않는다.
  - 구속(Gauss/trace/Codazzi/Jacobi)이 명시적으로 존재하며 지수 증폭될 수 있다.
    -> constraints.project 를 병용할 것.
  - Bianchi IX 재붕괴 (H->0) 는 이 차트로 통과할 수 없다.
"""
from __future__ import annotations

from bianchi.conventions import EPS3_J, rotation_matrix, tracefree_from_5, sym_from_6
from bianchi.charts.base import deceleration
from bianchi.optional_dependencies import require_jax_x64, require_optional

jax, jnp = require_jax_x64(feature=__name__)
eqx = require_optional("equinox", feature=__name__)

name = "general"
LIMITATIONS = __doc__.split("LIMITATIONS")[1].strip()


class StateG(eqx.Module):
    Sigma: jnp.ndarray     # (3,3) trace-free 대칭
    N: jnp.ndarray         # (3,3) 대칭
    A: jnp.ndarray         # (3,)

    @staticmethod
    def of(Sigma, N, A):
        return StateG(jnp.asarray(Sigma, jnp.float64),
                      jnp.asarray(N, jnp.float64),
                      jnp.asarray(A, jnp.float64))

    @staticmethod
    def from_packed(v):
        return StateG(tracefree_from_5(*v[:5]), sym_from_6(*v[5:11]), v[11:14])

    def packed(self):
        S, N = self.Sigma, self.N
        return jnp.concatenate([
            jnp.array([S[0, 0], S[1, 1], S[0, 1], S[0, 2], S[1, 2]]),
            jnp.array([N[0, 0], N[1, 1], N[2, 2], N[0, 1], N[0, 2], N[1, 2]]),
            self.A,
        ])


# ---------------------------------------------------------------- 곡률 (유도 그대로)
def _gamma_struct(N, A):
    """gamma^c_{ab} = eps_{abd} N^{dc} + A_a d^c_b - A_b d^c_a."""
    g = jnp.einsum("abd,dc->cab", EPS3_J, N)
    I = jnp.eye(3)
    g = g + jnp.einsum("a,cb->cab", A, I) - jnp.einsum("b,ca->cab", A, I)
    return g


def _connection(N, A):
    """Koszul (정규직교틀): Gamma^k_{ij} = 1/2 (g^k_ij - g^i_jk + g^j_ki)."""
    g = _gamma_struct(N, A)
    return 0.5 * (g - jnp.einsum("ijk->kij", g) + jnp.einsum("jki->kij", g))


def ricci3(N, A):
    """3D Ricci (성분 상수)."""
    g = _gamma_struct(N, A)
    G = _connection(N, A)
    # R_jk = G^m_jk G^i_im - G^m_ik G^i_jm - g^m_ij G^i_mk
    t1 = jnp.einsum("mjk,iim->jk", G, G)
    t2 = jnp.einsum("mik,ijm->jk", G, G)
    t3 = jnp.einsum("mij,imk->jk", g, G)
    return t1 - t2 - t3


def curvature(N, A):
    """(K, ^3S_ab) — Hubble 정규화 변수 기준."""
    Ric = ricci3(N, A)
    Ric = 0.5 * (Ric + Ric.T)             # Jacobi 면 밖에서의 수치 비대칭 제거
    R3 = jnp.trace(Ric)
    S3 = Ric - R3 * jnp.eye(3) / 3.0
    return -R3 / 6.0, S3


def R3_closed(N, A):
    """검증용 닫힌 형태: ^3R = -tr(N^2) + (1/2)(tr N)^2 - 6 A.A"""
    return -jnp.trace(N @ N) + 0.5 * jnp.trace(N) ** 2 - 6.0 * (A @ A)


def S3_closed(N, A):
    """명시적 닫힌 형태 (외부검토 R2; v1.1 에서 계수 확정·검증):

        ^3S_ab = 2 N_<a^c N_b>c - (tr N) N_<ab> + 2 eps_{cd<a} A^c N_b>^d

    Jacobi (N A = 0) 를 쓰지 않고도 성립하며, ricci3() 의 tracefree 부분과
    1e-14 이내로 일치한다 (audit/r2_curvature.py).  A-항의 계수는 정확히 +2
    이고 (0, +1, -2 는 O(1) 로 실패), 지표 배열은 eps_{cda} A^c N_b^d 이다.
    """
    N = jnp.asarray(N); A = jnp.asarray(A)
    B = 2.0 * (N @ N) - jnp.trace(N) * N
    C = jnp.einsum("cda,c,bd->ab", EPS3_J, A, N)
    M = B + 2.0 * C
    M = 0.5 * (M + M.T)
    return M - jnp.trace(M) * jnp.eye(3) / 3.0


# ---------------------------------------------------------------- RHS
def aux(y: StateG, args):
    gamma = args["gamma"]
    K, S3 = curvature(y.N, y.A)
    Sigma2 = jnp.trace(y.Sigma @ y.Sigma) / 6.0
    Omega = args.get("Omega", None)
    if Omega is None:
        Omega = 1.0 - Sigma2 - K            # Gauss 로 소거 (비틸트 기본)
    # ★ v1.3 (감사 결함 #5): 기본 q 는 **비틸트** 공식이다. tilted/특수 물질을
    #   Pi, q_flux 로 주입할 때는 반드시 args["q"] 로 올바른 q 도 함께 줄 것 —
    #   안 주면 (2-gamma)V^2/G_+ 보정이 빠진 q 로 조용히 틀린다.
    q = args.get("q", None)
    if q is None:
        q = deceleration(Sigma2, Omega, gamma)
    return dict(K=K, S3=S3, Sigma2=Sigma2, Omega=Omega, q=q)


def rhs(tau, y: StateG, args) -> StateG:
    a = aux(y, args)
    q, S3 = a["q"], a["S3"]
    R = args.get("R", jnp.zeros(3))
    W = rotation_matrix(R)
    Pi = args.get("Pi", jnp.zeros((3, 3)))
    S, N, A = y.Sigma, y.N, y.A
    dS = -(2.0 - q) * S - S3 + Pi + (W @ S - S @ W)
    dN = q * N + (S @ N + N @ S) + (W @ N - N @ W)
    dA = q * A - S @ A + W @ A
    # trace-free 사영 (수치 표류 방지)
    dS = dS - jnp.trace(dS) * jnp.eye(3) / 3.0
    return StateG(dS, 0.5 * (dN + dN.T), dA)


# ---------------------------------------------------------------- 구속
def constraint_residuals(y: StateG, args):
    """Gauss / trace / Codazzi / Jacobi / (군 파라미터는 algebra.type_drift)."""
    from bianchi.conventions import codazzi_residual
    a = aux(y, args)
    q_flux = args.get("q_flux", None)
    return dict(
        gauss=a["Sigma2"] + a["K"] + a["Omega"] - 1.0,
        trace=jnp.trace(y.Sigma),
        codazzi=codazzi_residual(y.Sigma, y.N, y.A, q_flux),
        jacobi=y.N @ y.A,
    )


def constraint_vector(y: StateG, args):
    c = constraint_residuals(y, args)
    return jnp.concatenate([
        jnp.atleast_1d(c["gauss"]), jnp.atleast_1d(c["trace"]),
        c["codazzi"], c["jacobi"],
    ])


# ---------------------------------------------------------------- Layer1 변환
def from_class_a(yA):
    """class_a StateA -> StateG (교차검증용)."""
    from bianchi.conventions import SQRT3
    Sp, Sm = yA.Sigma_p, yA.Sigma_m
    S = jnp.diag(jnp.array([-2*Sp, Sp + SQRT3*Sm, Sp - SQRT3*Sm]))
    N = jnp.diag(jnp.array([yA.N1, yA.N2, yA.N3]))
    return StateG(S, N, jnp.zeros(3))


def to_class_a(yG):
    from bianchi.charts.class_a import StateA
    from bianchi.conventions import SQRT3
    S, N = yG.Sigma, yG.N
    Sp = -S[0, 0] / 2.0
    Sm = (S[1, 1] - S[2, 2]) / (2.0 * SQRT3)
    return StateA(Sp, Sm, N[0, 0], N[1, 1], N[2, 2])
