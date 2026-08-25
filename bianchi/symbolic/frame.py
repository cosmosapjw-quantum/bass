"""
PR-02 · 유도 엔진 (SymPy). 구조상수 -> 3D Ricci -> Einstein -> Hubble 정규화.

검증 사다리 (tests/test_frame_engine.py 가 강제):
  L0  Koszul/Riemann 기계가 단위 둥근 S^3 재현        Ric = 2g, R = 6
  L1  ^3R = -tr(n^2) + (1/2)(tr n)^2 - 6 a.a
  L2  WE 의 K (1/12) 와 ^3S_alpha 재현, Wainwright-Hsu 계 완전 재현
  L3  vEU 의 n,a 진화식 -> N_i' = (q + 2 Sigma_i) N_i
  L4  Codazzi 를 D_b(K^ab - K h^ab) 에서 직접 유도 -> +eps 유일

이 모듈은 **전사하지 않는다**. 모든 RHS 는 여기서 나온다.
"""
from __future__ import annotations

from functools import lru_cache
from itertools import product

from bianchi.optional_dependencies import require_optional

sp = require_optional("sympy", feature=__name__)

I3 = range(3)
I4 = range(4)
ETA = sp.diag(-1, 1, 1, 1)


def eps(i, j, k):
    return sp.LeviCivita(i, j, k)


# ---------------------------------------------------------------- 3D
def gamma_of(n, a):
    """공간 commutation function gamma^c_{ab}."""
    g = [[[sp.S(0)] * 3 for _ in I3] for _ in I3]
    for c, i, j in product(I3, I3, I3):
        s = sum(eps(i, j, d) * n[d][c] for d in I3)
        s += a[i] * (1 if c == j else 0) - a[j] * (1 if c == i else 0)
        g[c][i][j] = sp.expand(s)
    return g


def connection3(n, a):
    """Koszul: Gamma^k_{ij} = 1/2 (g^k_ij - g^i_jk + g^j_ki)  (정규직교틀)."""
    g = gamma_of(n, a)
    G = [[[sp.S(0)] * 3 for _ in I3] for _ in I3]
    for k, i, j in product(I3, I3, I3):
        G[k][i][j] = sp.expand(
            sp.Rational(1, 2) * (g[k][i][j] - g[i][j][k] + g[j][k][i])
        )
    return G, g


def ricci3(n, a):
    """3D Ricci (성분 상수 정규직교틀)."""
    G, g = connection3(n, a)
    R = [[sp.S(0)] * 3 for _ in I3]
    for j, k in product(I3, I3):
        s = 0
        for i, m in product(I3, I3):
            s += G[m][j][k] * G[i][i][m] - G[m][i][k] * G[i][j][m] - g[m][i][j] * G[i][m][k]
        R[j][k] = sp.expand(s)
    return sp.Matrix(R)


def curvature_pieces(n, a):
    """(^3R, ^3S_ab, K)  — K 는 Hubble 정규화 변수로 부를 때 -^3R/6."""
    Ric = ricci3(n, a)
    R3 = sp.expand(sp.trace(Ric))
    S3 = sp.expand(Ric - sp.Rational(1, 3) * R3 * sp.eye(3))
    return R3, S3, sp.expand(-R3 / 6)


def R3_closed_form(n, a):
    """유도로 확인된 닫힌 형태."""
    n = sp.Matrix(n); a = sp.Matrix(a)
    return sp.expand(
        -sp.trace(n * n) + sp.Rational(1, 2) * sp.trace(n) ** 2 - 6 * (a.T * a)[0, 0]
    )


# ---------------------------------------------------------------- Codazzi
def codazzi_from_connection(n, a, sg, H):
    """운동량 구속을 D_b(K^{ab} - K h^{ab}) 에서 직접 계산."""
    G, _ = connection3(n, a)
    Kt = -(H * sp.eye(3) + sg)
    Kmix = Kt - sp.trace(Kt) * sp.eye(3)
    out = []
    for al in I3:
        s = 0
        for b, c in product(I3, I3):
            s += G[al][b][c] * Kmix[c, b] + G[b][b][c] * Kmix[al, c]
        out.append(sp.expand(s))
    return out


def codazzi_standard(n, a, sg, eps_sign=+1):
    """표준형 3 a_b sigma^ab + s * eps^abc n_bd sigma_c^d."""
    return [
        sp.expand(
            3 * sum(a[b] * sg[al, b] for b in I3)
            + eps_sign * sum(
                eps(al, b, c) * n[b, d] * sg[c, d]
                for b in I3 for c in I3 for d in I3
            )
        )
        for al in I3
    ]


# ---------------------------------------------------------------- Hubble 정규화 진화
def evolution_normalized(Sigma, N, A, q, R=None, Pi=None):
    """Hubble 정규화 진화식 (COMMUTATOR 규약).

      Sigma_ab' = -(2-q) Sigma_ab - ^3S_ab/H^2 + Pi_ab + [W, Sigma]
      N_ab'     = q N_ab + 2 Sigma_(a^d N_b)d  + [W, N]
      A_a'      = q A_a - Sigma_a^b A_b        + W A

    W_ab = -eps_abc R_c  (conventions.RotationConvention.COMMUTATOR)
    """
    Sigma = sp.Matrix(Sigma); N = sp.Matrix(N); A = sp.Matrix(A)
    _, S3, _ = curvature_pieces(
        [[N[i, j] for j in I3] for i in I3], [A[i] for i in I3]
    )
    W = sp.zeros(3, 3)
    if R is not None:
        for i, j in product(I3, I3):
            W[i, j] = -sum(eps(i, j, k) * R[k] for k in I3)
    dS = sp.expand(-(2 - q) * Sigma - S3 + (W * Sigma - Sigma * W))
    if Pi is not None:
        dS = sp.expand(dS + sp.Matrix(Pi))
    dN = sp.expand(q * N + (Sigma * N + N * Sigma) + (W * N - N * W))
    dA = sp.expand(q * A - Sigma * A + W * A)
    return dS, dN, dA


# ---------------------------------------------------------------- 4D (물질용)
def frame_structure_4d(H, sg, n, a, R):
    """4D 구조함수 C^C_{AB} (COMMUTATOR 규약)."""
    Cup = {}
    for al in I3:
        vec = [sp.S(0)] * 4
        for be in I3:
            vec[be + 1] = -(
                H * (1 if al == be else 0) + sg[al, be]
                + sum(eps(al, be, g) * R[g] for g in I3)
            )
        Cup[(0, al + 1)] = vec
        Cup[(al + 1, 0)] = [-x for x in vec]
    for al, be in product(I3, I3):
        vec = [sp.S(0)] * 4
        for g in I3:
            vec[g + 1] = (
                sum(eps(al, be, d) * n[d, g] for d in I3)
                + a[al] * (1 if g == be else 0) - a[be] * (1 if g == al else 0)
            )
        Cup[(al + 1, be + 1)] = vec
    for A in I4:
        Cup[(A, A)] = [sp.S(0)] * 4
    return Cup


def connection_4d(Cup):
    """4D Koszul (프레임 계량 상수)."""
    def Cdn(a, b, c):
        return sp.expand(ETA[c, c] * Cup[(a, b)][c])

    Gam = [[[sp.S(0)] * 4 for _ in I4] for _ in I4]
    for a, b, c in product(I4, I4, I4):
        Gam[c][a][b] = sp.expand(
            sp.Rational(1, 2) * (Cdn(a, b, c) - Cdn(b, c, a) + Cdn(c, a, b)) / ETA[c, c]
        )
    return Gam


def divergence_4d(Gam, T, d0):
    """nabla_A T^{AB}. d0 는 e_0 미분 연산자 (공간동차 -> e_alpha(T)=0)."""
    out = []
    for b in I4:
        s = d0(T[0, b])
        for a, dd in product(I4, I4):
            s += Gam[a][a][dd] * T[dd, b] + Gam[b][a][dd] * T[a, dd]
        out.append(sp.expand(s))
    return out


# ---------------------------------------------------------------- 편의: WE class A
@lru_cache(maxsize=1)
def wainwright_hsu():
    """class A (WE 규약) RHS 를 유도로 생성. (state, rhs, aux) 심볼릭."""
    g = sp.Symbol("gamma")
    Sp, Sm, N1, N2, N3 = sp.symbols("Sigma_p Sigma_m N_1 N_2 N_3")
    r3 = sp.sqrt(3)
    Sig = sp.diag(-2 * Sp, Sp + r3 * Sm, Sp - r3 * Sm)
    N = sp.diag(N1, N2, N3)
    R3, S3, K = curvature_pieces(
        [[N[i, j] for j in I3] for i in I3], [0, 0, 0]
    )
    Om = sp.expand(1 - (Sp ** 2 + Sm ** 2) - K)
    q = sp.expand(2 * (Sp ** 2 + Sm ** 2) + sp.Rational(1, 2) * (3 * g - 2) * Om)
    dS = sp.expand(-(2 - q) * Sig - S3)
    dSp = sp.expand(-dS[0, 0] / 2)
    dSm = sp.expand((dS[1, 1] - dS[2, 2]) / (2 * r3))
    dN = [sp.expand((q + 2 * Sig[i, i]) * [N1, N2, N3][i]) for i in I3]
    return (
        (Sp, Sm, N1, N2, N3, g),
        (dSp, dSm, dN[0], dN[1], dN[2]),
        {"Omega": Om, "q": q, "K": K},
    )
