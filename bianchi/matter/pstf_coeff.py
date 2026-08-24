"""
J1 · **계수공간 PSTF** — 3^l 텐서 표현의 폐기 (PLAN-NEXT-v5 §3, 구조 전환 1절편).

상태를 rank-l PSTF 텐서(3^l 성분) 대신 **정준 실구면조화 기저의 2l+1 실계수**로
저장하고, 계층의 σ-연산 3종을 (2l'+1)×(2l+1)×5 블록으로 만든다:

    _outer_sigma   : l−2 → l     (J_{<A}σ_{ab>})
    _contract_one  : l   → l     (J_{aA}σ_{ba} 의 PSTF 부분)
    _contract_two  : l+2 → l     (J_{abA}σ^{ab})

두 경로 (게이트: l≤6 에서 성분별 합치):
  · 경로 A (dense): 정준 기저 U_lm 으로 기존 dense 연산을 사영 — l ≤ 6 전용
    (pstf_operator 가 3^l — 이 한계가 J1 이 없애는 대상).
  · 경로 B (닫힌형): 실 Gaunt 계수 m-구조 × 환원원소.  **임의 l, 3^l 무생성.**
      outer  : G[m',m,k] = √(D_l/(D_{l−2}D₂)) · rg(l, l−2, 2; m', m, k)
               — 함수사전 (f_T(n)=T·n^l, 조화 곱-사영 ≡ PSTF 외적) 으로
               사전인자까지 완전 닫힌형 (자유 상수 없음).
      c1/c2  : Wigner–Eckart 유일성 (Hom(V_l⊗V₂→V_{l'}) 1차원) ⇒
               G = R_op(l) · rg(...).  R_op(l) 은 **널벡터 최고웨이트**로 결정:
               M=(x̂+iŷ)/√2, M·M=0 ⇒ M^{⊗l} 이 대칭·무대각합·단위 Frobenius —
               3^l 객체 없이 O(1) 산술로 임의 l 의 스칼라를 준다 (audit/j1).

사전 (수치검증되는 닫힌형):
    D_l ≡ <T_lm, T_lm>_frob = (2l+1)!!/(4π·l!)   (m-무관; T_lm ↔ Z_lm 사전)
    ∫ f_T f_T' dΩ/(4π) = l!/(2l+1)!! · <T,T'>_frob

규약: 실 SH Z_lm 은 sympy `real_gaunt` 과 **수치 잠금** (∫ZZZ 대조 3.3e−15,
audit/j1).  기존 `tilted_mass.pstf_basis` (SVD) 는 임의 방향이라 연산자 표에
못 쓴다 — 정준 기저는 여기서만.  SVD↔정준 좌표변환은 직교행렬 (round-trip 시험).

LIMITATIONS
  - 경로 A (dense 게이트·정준 dense 기저) 는 l ≤ 6 (hierarchy.L_MAX_SUPPORTED).
    경로 B 는 임의 l — l>6 은 내부 일관성 (선택규칙·수반성) 게이트가 감시.
  - real_gaunt 최초 비용 (실측): c1_block(10) 337/2205 호출 2.2s, l=15 6.5s
    — lru 는 프로세스 수명.  J2 는 표를 디스크 영속화하거나 3j 점화식으로
    옮길 것 (표는 정확·규약고정 상수라 영속화 안전).
  - ★ J2 이월 명시 (리뷰): 이 3블록은 비틸트 hierarchy_rhs 를 전담하지만
    tilted equation_lhs 는 추가로 (i) 소용돌이 ω 의 반대칭 l→l 회전 블록
    (3-계수 — σ 5-슬롯으로 표현 불가), (ii) u̇ 의 Δl=±1 블록이 필요하다.
"""
from __future__ import annotations

from functools import lru_cache
from itertools import permutations

import numpy as np

from bianchi.matter.hierarchy import L_MAX_SUPPORTED
from bianchi.optional_dependencies import require_optional

sp = require_optional("sympy", feature=__name__)
_wigner = require_optional("sympy.physics.wigner", feature=__name__, dependency="sympy")
_cx_gaunt = _wigner.gaunt
_real_gaunt = _wigner.real_gaunt

_x, _y, _z, _w = sp.symbols("x y z w", real=True)


# ═══════════════════════════════════════ 정준 실 solid harmonic → 텐서 (l ≤ 6)
@lru_cache(maxsize=None)
def solid_expr(l, m):
    """실 solid harmonic  r^l Z_lm  (동차 l차 조화다항식, sympy 규약 잠금)."""
    am = abs(m)
    Q = sp.simplify(sp.assoc_legendre(l, am, _w) / (1 - _w**2)**sp.Rational(am, 2))
    Qp = sp.Poly(sp.expand(Q), _w)
    r2 = _x**2 + _y**2 + _z**2
    homog = sum(c * _z**k * r2**(sp.Rational(l - am - k, 2))
                for (k,), c in Qp.terms())
    N = sp.sqrt(sp.Rational(2*l + 1, 4) / sp.pi
                * sp.Rational(sp.factorial(l - am), sp.factorial(l + am)))
    if m > 0:
        return sp.expand(sp.sqrt(2)*(-1)**m * N
                         * sp.re(sp.expand((_x + sp.I*_y)**am)) * homog)
    if m < 0:
        return sp.expand(sp.sqrt(2)*(-1)**m * N
                         * sp.im(sp.expand((_x + sp.I*_y)**am)) * homog)
    return sp.expand(N * homog)


def D_norm(l):
    """사전 노름 D_l = <T_lm, T_lm>_frob = (2l+1)!!/(4π l!)  (닫힌형)."""
    return float(sp.factorial2(2*l + 1)) / (4.0 * np.pi * float(sp.factorial(l)))


@lru_cache(maxsize=None)
def canonical_tensor(l, m):
    """T_lm : (3,)*l dense — f_T(n) = Z_lm(n) 사전의 계수텐서.  l ≤ 6 전용."""
    if l > L_MAX_SUPPORTED:
        raise ValueError(f"dense 정준 텐서는 l ≤ {L_MAX_SUPPORTED} (경로 B 를 쓸 것)")
    if l == 0:
        return np.array(float(solid_expr(0, 0)))
    poly = sp.Poly(solid_expr(l, m), _x, _y, _z)
    T = np.zeros((3,) * l)
    fl = float(sp.factorial(l))
    for (a, b, c), coef in poly.terms():
        # 단항 x^a y^b z^c → 대칭텐서 성분 coef·a!b!c!/l! (모든 지표 배치 동일)
        val = (float(coef)
               * float(sp.factorial(a)*sp.factorial(b)*sp.factorial(c)) / fl)
        idx = (0,)*a + (1,)*b + (2,)*c
        for p in set(permutations(idx)):
            T[p] = val
    T.setflags(write=False)
    return T


@lru_cache(maxsize=None)
def U_basis(l):
    """Frobenius-정규직교 정준 기저 (3^l, 2l+1) — 열 m = −l..l.  l ≤ 6."""
    cols = [canonical_tensor(l, m).ravel() / np.sqrt(D_norm(l))
            for m in range(-l, l + 1)]
    B = np.stack(cols, axis=1)
    if np.abs(B.T @ B - np.eye(2*l + 1)).max() > 1e-10:
        raise AssertionError(f"l={l}: 정준 기저 직교정규 실패 (사전 D_l 반증?)")
    B.setflags(write=False)          # ★ 리뷰 MAJOR: lru 캐시 변이 오염 차단
    return B


def to_ccoef(T, l):
    """rank-l PSTF 텐서 → 정준 2l+1 계수 (l ≤ 6).  비대칭 입력은 PSTF 사영 겸함."""
    return U_basis(l).T @ np.asarray(T, float).ravel()


def from_ccoef(c, l):
    """정준 계수 → rank-l PSTF 텐서 (l ≤ 6)."""
    v = U_basis(l) @ np.asarray(c, float)
    return v.reshape((3,) * l) if l else float(v[0])


def sigma_to_c5(sigma):
    """(3,3) trace-free 대칭 σ → 정준 5-계수."""
    return to_ccoef(np.asarray(sigma, float), 2)


# ═══════════════════════════════════════ 경로 B — 닫힌형 블록 (임의 l)
@lru_cache(maxsize=None)
def _rg_table(l_out, l_in, l3=2):
    """실 Gaunt 표 rg(l_out, l_in, l3; m', m, k) → (2l_out+1, 2l_in+1, 2l3+1).

    J2 일반화: l3=2 (σ) 와 l3=1 (u̇ 벡터).  패리티 (합 짝수)·삼각 가드."""
    if (l_out + l_in + l3) % 2 or abs(l_out - l_in) > l3 or min(l_out, l_in) < 0:
        raise ValueError(f"rg 표 패리티·삼각 위반: ({l_out},{l_in},{l3})")
    hit = _DISK.get((l_out, l_in, l3))
    if hit is not None:
        return hit                                 # 디스크 사전계산 (규약 스탬프 검증됨)
    G = np.zeros((2*l_out + 1, 2*l_in + 1, 2*l3 + 1))
    for i, mp in enumerate(range(-l_out, l_out + 1)):
        for j, m in enumerate(range(-l_in, l_in + 1)):
            for k, mk in enumerate(range(-l3, l3 + 1)):
                if abs(mp) not in (abs(m + mk), abs(m - mk)):
                    continue                      # 실기저 m-선택규칙 (희소 지름길)
                G[i, j, k] = float(_real_gaunt(l_out, l_in, l3, mp, m, mk))
    G.setflags(write=False)          # ★ 리뷰 MAJOR: lru 캐시 변이 오염 차단
    return G


@lru_cache(maxsize=None)
def _R_op(op, l):
    """Wigner–Eckart 환원원소 (널벡터 최고웨이트 유도 — audit/j1 기록).

    복소 Frobenius-정규직교 최고웨이트의 정확 스칼라 (M·M=0 산술):
        outer: +1,   c2: +1,   c1: −1/√6
    을 사전인자·복소 Gaunt 최고웨이트 값으로 나눠 환원원소로 만든다.
    outer 는 곱-사영 사전으로 자유상수 없이 닫힌다 (Gaunt 불필요).
    """
    fpi = 4 * sp.pi
    D = lambda ll: sp.factorial2(2*ll + 1) / (fpi * sp.factorial(ll))
    if op == "outer":
        # 함수사전 곱-사영: 자유상수 없음 (l=2..5 dense 대조 2.2e−16 합치)
        val = sp.sqrt(D(l) / (D(l - 2) * D(2)))
    elif op == "c2":                               # l+2 → l
        # ★ 수반항등 (정확, 상수 1): <pstf(J⊗σ), K>_l = J_Aσ_{ab}K_{Aab}
        #   = <J, _contract_two(K,σ)>_{l−2}  (K 대칭이라 지표순서 무관)
        #   + rg 의 완전대칭성  ⇒  R_c2(l) = R_out(l+2).
        #   (1차 시도는 복소 Gaunt 최고웨이트 위상 처리를 틀려 l-의존 비율로
        #    반증됐다 — dense 비율이 인수분해 자체는 기계정밀로 증명했었다.)
        val = sp.sqrt(D(l + 2) / (D(l) * D(2)))
    elif op == "c1":                               # l → l
        # 널벡터 최고웨이트: c1(M^{⊗l}, U₂₀) = −M^{⊗l}/√6 (σ·M = −M/√6).
        #   1차 시도의 잉여인자 √D₂/(4π) (= 관측비율 0.061477) 를 리뷰 전
        #   자체반증으로 제거 — 옳은 형태는 R = (−1)^l·(−1/√6)/(4π·g_hw)
        #   가 아니라 아래 (dense 비율로 확정, audit/j1 이 기록).
        # ★ 리뷰가 정리로 승격: g_hw = (−1)^{l+1}√(5/4π)·l/(2l+3) (Racah 형)
        #   ⇒ R_c1(l) = 2(2l+3)/l·√(π/30) 이 기호적으로 증명됨 (audit/j1).
        g_hw = _cx_gaunt(l, l, 2, -l, l, 0)
        val = (-1)**l * (-1 / sp.sqrt(6)) / g_hw
    elif op == "ov":                               # l−1 → l (u̇ 외적, pstf)
        # 곱-사영 사전 정리의 벡터판 — 자유상수 없음
        val = sp.sqrt(D(l) / (D(l - 1) * D(1)))
    elif op == "cv":                               # l+1 → l (u̇ 첫지표 축약)
        # ★ 수반항등 (c2 증명과 동형): <pstf(J⊗w),K>_l = J_A w_a K^{Aa}
        #   = <J, _contract_vec_first(K,w)>_{l−1}  ⇒  R_cv(l) = R_ov(l+1)
        val = sp.sqrt(D(l + 1) / (D(l) * D(1)))
    else:
        raise ValueError(op)
    return float(sp.simplify(val))


def outer_block(l):
    """l−2 → l 블록 (2l+1, 2(l−2)+1, 5) — 임의 l ≥ 2, 3^l 무생성."""
    if l < 2:
        raise ValueError("outer 블록은 l ≥ 2")
    return _R_op("outer", l) * _rg_table(l, l - 2)


def c2_block(l):
    """l+2 → l 블록 (2l+1, 2(l+2)+1, 5)."""
    return _R_op("c2", l) * _rg_table(l, l + 2)


def c1_block(l):
    """l → l 블록 (2l+1, 2l+1, 5) — dense _contract_one 의 PSTF 부분."""
    return _R_op("c1", l) * _rg_table(l, l)


def apply_block(G, c, s5):
    """블록 적용: out[m'] = Σ_{m,k} G[m',m,k]·c[m]·s5[k]  — O((2l+1)²)."""
    return np.einsum("pmk,m,k->p", G, np.asarray(c, float),
                     np.asarray(s5, float))


# ═══════════════════════════════════════ 경로 A — dense 사영 (l ≤ 6, 게이트 전용)
def dense_block(op, l):
    """기존 dense 연산을 정준 기저로 사영한 블록 — 경로 B 의 심판."""
    from bianchi.matter.hierarchy import (_contract_one, _contract_two,
                                          _outer_sigma)
    l_in = {"outer": l - 2, "c1": l, "c2": l + 2}[op]
    fn = {"outer": _outer_sigma, "c1": _contract_one, "c2": _contract_two}[op]
    G = np.zeros((2*l + 1, 2*l_in + 1, 5))
    for k in range(5):
        e5 = np.zeros(5)
        e5[k] = 1.0
        sig = from_ccoef(e5, 2)
        for j in range(2*l_in + 1):
            ej = np.zeros(2*l_in + 1)
            ej[j] = 1.0
            J = from_ccoef(ej, l_in)
            out = fn(np.asarray(J, float), sig)
            G[:, j, k] = to_ccoef(out, l)          # to_ccoef 가 PSTF 사영 겸함
    return G


def vec_to_c3(w):
    """(3,) 벡터 → 정준 3-계수 (l=1).  ★ 정준 순서 (Z₁₋₁,Z₁₀,Z₁₁) ∝ (y,z,x)
    — rot_block 3번째 축 (카르테시안 x,y,z) 과 다르다.  J2b 조립기는 벡터를
    전부 vec_to_c3 로 통일하거나 전부 카르테시안으로 — 혼용 금지."""
    return to_ccoef(np.asarray(w, float), 1)


def outer_vec_block(l):
    """l−1 → l 블록 (2l+1, 2l−1, 3) — pstf(J⊗w).  임의 l ≥ 1."""
    if l < 1:
        raise ValueError("outer_vec 블록은 l ≥ 1")
    return _R_op("ov", l) * _rg_table(l, l - 1, 1)


def contract_vec_block(l):
    """l+1 → l 블록 (2l+1, 2l+3, 3) — J_{aA}w^a 의 PSTF 부분.  임의 l ≥ 0."""
    return _R_op("cv", l) * _rg_table(l, l + 1, 1)


# ═══════════════════════════════════════ ω-회전 블록 (Gaunt 형 아님 — 생성자)
@lru_cache(maxsize=None)
def _real_unitary(l):
    """복소 Y_lm → 실 Z_lm 유니터리 V (2l+1, 2l+1) — CS 규약 (scipy 핀과 동일).

    Z_m>0 = √2(−1)^m Re Y_m = ((−1)^m Y_m + Y_{−m})/√2 · … 표준 조합."""
    n = 2*l + 1
    V = np.zeros((n, n), complex)                  # 행: 실 m_r, 열: 복소 m_c
    idx = lambda m: m + l
    V[idx(0), idx(0)] = 1.0
    s2 = 1.0/np.sqrt(2.0)
    for m in range(1, l + 1):
        V[idx(m),  idx(m)]  = (-1)**m * s2         # Re 조합
        V[idx(m),  idx(-m)] = s2
        V[idx(-m), idx(m)]  = (-1)**m * s2 / 1j    # Im 조합
        V[idx(-m), idx(-m)] = -s2 / 1j
    return V


@lru_cache(maxsize=None)
def rotation_generators(l):
    """실기저 SO(3) 생성자 (A_x, A_y, A_z) — 실 반대칭, 임의 l.

    복소 사다리 (L_z=diag(m), L_± 표준) 를 실기저로 유니터리 변환:
    A_a = V·(−i L_a)·V† 는 실 반대칭이어야 한다 (허수부 잔차는 조립 검증).
    [A_x, A_y] = −A_z 순환 교환관계가 임의 l 내부게이트."""
    n = 2*l + 1
    m = np.arange(-l, l + 1)
    Lz = np.diag(m).astype(complex)
    Lp = np.zeros((n, n), complex)                 # L₊|l,m> = c|l,m+1>
    for k in range(n - 1):
        mm = k - l
        Lp[k + 1, k] = np.sqrt(l*(l + 1) - mm*(mm + 1))
    Lm = Lp.conj().T
    Lx, Ly = 0.5*(Lp + Lm), -0.5j*(Lp - Lm)
    V = _real_unitary(l)
    out = []
    # ★ 변환식 정정 (리뷰 진단): 실계수는 c_re = conj(V)·c_cx 로 변환되므로
    #   연산자는 conj(V)·O·Vᵀ 다 — 1차 조립 V·(−iL)·V† 는 (i) 켤레 누락이
    #   실행렬 축(x,z)만 뒤집고 (ii) 전역 부호가 셋 다 뒤집어, 두 오류가
    #   상쇄되며 "y만 반전"으로 보였다 (dense 심판으로 결과는 옳았음 —
    #   원인 오진을 리뷰가 정정; 같은 틀로 새 연산자를 추가할 때의 함정 봉쇄).
    for L in (Lx, Ly, Lz):
        A = np.conj(V) @ (1j*L) @ V.T
        if np.abs(A.imag).max() > 1e-12:
            raise AssertionError(f"l={l}: 실기저 생성자에 허수 잔차")
        Ar = A.real.copy()
        Ar.setflags(write=False)
        out.append(Ar)
    return tuple(out)


@lru_cache(maxsize=None)
def rot_block(l):
    """l → l 블록 (2l+1, 2l+1, 3) — pstf(_contract_one(J, W(ω))) 의 계수 작용.

    W(ω)_{ba} = ε_{bac}ω_c (반대칭).  Wigner–Eckart (벡터연산자, l→l 유일)
    ⇒ 생성자 A_a 의 배수: rot = R_rot(l)·A_a.  R_rot 은 dense (l≤6) 로
    측정·인식하고 임의 l 로 확장한다 (시험이 l≤6 대조 + l>6 교환관계 감시)."""
    A = rotation_generators(l)
    R = 1.0 / l          # ★ R_rot(l) = 1/l — **정리** (슬롯평균): 대칭텐서의
    #   단일슬롯 회전을 대칭화하면 전체 생성자의 1/l 배 (PSTF 보존).
    #   dense l=1..6 정확 확인 (3.9e−16).
    G = np.stack([R * A[0], R * A[1], R * A[2]], axis=2)
    G.setflags(write=False)
    return G


# ═══════════════════════════════════════ rg 표 디스크 영속화 (리뷰 권고)
_TABLES_PATH = None
_DISK = {}


def _default_tables_path():
    import os
    return os.path.join(os.path.dirname(__file__), "gaunt_tables.npz")


def load_tables(path=None):
    """사전계산 rg 표 로드 — 프로세스 시작비용 제거 (표는 정확·규약고정 상수)."""
    global _TABLES_PATH, _DISK
    import os
    path = path or _default_tables_path()
    if not os.path.exists(path):
        return 0
    data = np.load(path)
    if str(data.get("convention")) != "sympy_real_gaunt_CS_v1":
        raise ValueError("gaunt_tables.npz 규약 스탬프 불일치 — 재생성 필요")
    n = 0
    for key in data.files:
        if key.startswith("rg_"):
            _, lo, li, l3 = key.split("_")
            arr = data[key]
            arr.setflags(write=False)
            _DISK[(int(lo), int(li), int(l3))] = arr
            n += 1
    _TABLES_PATH = path
    return n


def export_tables(path=None, l_max=12):
    """rg 표 (l3∈{1,2}, l ≤ l_max) 를 npz 로 영속화 + 규약 스탬프."""
    path = path or _default_tables_path()
    out = {"convention": np.array("sympy_real_gaunt_CS_v1")}
    for l3 in (1, 2):
        for lo in range(0, l_max + 1):
            for li in range(max(0, lo - l3), min(l_max, lo + l3) + 1):
                if (lo + li + l3) % 2:
                    continue
                out[f"rg_{lo}_{li}_{l3}"] = np.asarray(_rg_table(lo, li, l3))
    np.savez_compressed(path, **out)
    return path


# 모듈 로드 시 사전계산 표 자동 탑재 (7ms; 없으면 0 — sympy 폴백)
load_tables()


# 모듈 로드 시 사전계산 표 자동 탑재 (~7ms; 없으면 0 — sympy 폴백)
load_tables()
