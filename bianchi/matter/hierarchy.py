"""
H1-a · Lewis-Challinor 운동량적분 다극 계층 — 상태 표현과 초기조건.

출처: A. Lewis & A. Challinor, *Evolution of cosmological dark matter perturbations*,
Phys. Rev. D 66, 023531 (astro-ph/0203507v2).  논문 부호규약은 **(+---)**,
우리 코드는 **(-+++)** — 변환은 PLAN-H §2 및 아래 ★부호 절 참조.

논문 식 (10) (속도가중 n ≡ l + 2i):

    J^(i)_{A_l} ≡ [4π(-2)^l (l!)²/(2l+1)!] ∫₀^∞ dλ λ² E F_{A_l} (λ/E)^n

★ **핵심 단순화 (이 세션에서 확인)**: 위 정규화 인자는 PSTF 역변환 인자와 **정확히
  상쇄**되므로, F_{A_l} 을 거치지 않고 분포함수의 직접 모멘트로 쓸 수 있다:

    J^(i)_{A_l} = ∫ dλ dΩ  λ² E (λ/E)^n  e_{⟨A_l⟩}  f          (계수 정확히 1)

  검증 (freestream.py 정확 구적 대조):
      J^(0)/ρ      = 1.000000000000
      J^(1)/(3p)   = 1.000000000000        (식 11 의 p = ⅓J^(1))
      J^(0)_ab vs π_ab  최대|Δ| = 2.1e-13
      J^(0)_a (비틸트·등방 f) = O(1e-15) ≈ 0
  이것이 논문이 "The numerical factor is introduced so that ... are simply
  ρ=J^(0), q_a=J^(0)_a, π_ab=J^(0)_ab, p=⅓J^(1)" 라고 적은 이유다.

식 (11) 대응:
    ρ = J^(0),   q_a = J^(0)_a,   π_ab = J^(0)_ab,   p = (1/3) J^(1)

★ 무질량 극한: λ=E ⇒ (λ/E)^n=1 ⇒ **J^(i) 가 i 에 무관**.  이 성질이 계층의 l=2
  σ-소스에서 Misner 계수 -8/15 를 만든다 (PLAN-H §0b):
      (2/15)[J^(2) - 5J^(1)] = (2/15)(ρ - 5ρ) = -(8/15)ρ

이 모듈은 H1-a (상태·초기조건) 만 담당한다.  RHS(식 12 의 균질 축약)는 H1-b.
"""
from __future__ import annotations

from itertools import permutations
from math import factorial

import numpy as np

from bianchi.backend_policy import BackendPolicy, select_backend
from bianchi.matter import freestream as fs

#: 계층에서 실제로 쓰는 최대 다극 차수의 안전 상한 (3^l 저장이므로).
L_MAX_SUPPORTED = 6


# ════════════════════════════════════════════════════════ PSTF (trace-free) 사영
def _symmetrize(T):
    """대칭화 — 모든 지표 순열 평균.  l ≤ 6 에서 실용적."""
    T = np.asarray(T, float)
    l = T.ndim
    if l < 2:
        return T
    acc = np.zeros_like(T)
    perms = list(permutations(range(l)))
    for p in perms:
        acc += np.transpose(T, p)
    return acc / len(perms)


def _trace_last_two(T):
    """마지막 두 지표 축약 → rank l-2."""
    return np.trace(T, axis1=-2, axis2=-1)


def _sym_basis(rank):
    """대칭 rank-r 텐서의 기저 (다중지표 조합 i1≤i2≤…)."""
    if rank == 0:
        return [np.ones(())]
    from itertools import combinations_with_replacement
    basis = []
    for idx in combinations_with_replacement(range(3), rank):
        B = np.zeros((3,) * rank)
        B[idx] = 1.0
        basis.append(_symmetrize(B))
    return basis


_TRACE_BASIS_CACHE = {}


def _trace_subspace(l):
    """대칭 rank-l 공간에서 '순수 대각합' 부분공간 span{ sym(δ ⊗ S) } 의 행렬 (3^l, nb).

    ★ 대칭 rank-l 텐서는 PSTF ⊕ sym(δ⊗rank(l-2)) 로 분해되고, 두 부분공간은 완전축약
      내적에 대해 **직교**한다 (PSTF 는 어느 두 지표 대각합도 0 이므로 δ 와의 축약이 0).
      따라서 직교사영으로 대각합 부분을 정확히 제거할 수 있다 — 반복법(계수 1/(2l-1))은
      l≥4 에서 이중 대각합 구조 때문에 수렴하지 않는다 (실측 확인).
    """
    if l not in _TRACE_BASIS_CACHE:
        eye = np.eye(3)
        cols = [_symmetrize(np.multiply.outer(B, eye)).ravel()
                for B in _sym_basis(l - 2)]
        _TRACE_BASIS_CACHE[l] = np.stack(cols, axis=1)
    return _TRACE_BASIS_CACHE[l]


_PSTF_OP_CACHE = {}


def pstf_operator(l):
    """★ R3 · PSTF 사영을 **고정 행렬** Q_l = (I − A·A⁺)·S_l 로 미리 만든다 (3^l, 3^l).

    `pstf` 는 원래 호출마다 (a) l! 개 순열 평균과 (b) `np.linalg.lstsq` 를 돌았다.
    둘 다 **T 에 무관한 선형연산**이라 한 번만 만들면 된다 — 프로파일에서 이 함수가
    tilted 적분 34.3 초 중 18.7 초(호출 87093회)를 먹고 있었다.

    S_l 은 대칭화 행렬, A 는 `_trace_subspace(l)` (순수 대각합 부분공간).
    ★ 수학은 그대로다: 같은 직교사영을 행렬로 굳혔을 뿐이고, 차등시험이 이를 고정한다.
    """
    if l not in _PSTF_OP_CACHE:
        d = 3 ** l
        S = np.empty((d, d))
        for c in range(d):
            e = np.zeros(d)
            e[c] = 1.0
            S[:, c] = _symmetrize(e.reshape((3,) * l)).ravel()
        A = _trace_subspace(l)
        P = np.eye(d) - A @ np.linalg.pinv(A)
        _PSTF_OP_CACHE[l] = P @ S
    return _PSTF_OP_CACHE[l]


def pstf(T, tol=1e-10):
    """대칭 rank-l 텐서의 **PSTF(사영 대칭 무대각합) 부분** — 직교사영.

    ★ 함정 3 규율(trace-free 를 안전하게): 결과의 **모든** 대각합이 tol 이하임을
      런타임 검증하고, 실패 시 조용히 넘기지 않고 예외를 던진다.

    ★ R3: 사영을 `pstf_operator(l)` 로 굳혀 호출당 **행렬-벡터 곱 한 번**이 됐다
      (옛 판은 매번 l! 순열 평균 + lstsq).  값은 그대로다 — `test_r3_*` 가 대조한다.
    """
    T = np.asarray(T, float)
    l = T.ndim
    if l < 2:
        return _symmetrize(T)          # 스칼라·벡터는 이미 trace-free
    if l > L_MAX_SUPPORTED:
        raise ValueError(f"l={l} > L_MAX_SUPPORTED={L_MAX_SUPPORTED}")
    out = (pstf_operator(l) @ T.ravel()).reshape(T.shape)
    scale = max(np.abs(T).max(), 1e-300)
    resid = np.abs(_trace_last_two(out)).max() / scale
    if resid > tol:
        raise RuntimeError(f"PSTF 대각합 제거 실패 (l={l}, 잔여 {resid:.3e})")
    return out


def is_pstf(T, tol=1e-10):
    """진단: 대칭 + 모든 대각합 0 인지."""
    T = np.asarray(T, float)
    if T.ndim < 2:
        return True
    scale = max(np.abs(T).max(), 1e-300)
    sym_err = np.abs(T - _symmetrize(T)).max() / scale
    tr_err = np.abs(_trace_last_two(T)).max() / scale
    return bool(sym_err <= tol and tr_err <= tol)


def n_independent(l):
    """PSTF rank-l 텐서의 독립 성분 수 = 2l+1."""
    return 2 * l + 1


# ════════════════════════════════════════════════════════ 정규화 인자 (문서·검증용)
def J_NORM(l):
    """논문 식 (10) 의 정규화 인자 4π(-2)^l (l!)²/(2l+1)!.

    ★ 실제 계산에는 쓰지 않는다 — PSTF 역변환 인자와 상쇄되기 때문(모듈 docstring).
      이 함수는 상쇄를 문서화·시험하기 위해 남긴다.
    """
    return 4.0 * np.pi * (-2.0) ** l * factorial(l) ** 2 / factorial(2 * l + 1)


# ════════════════════════════════════════════════════════ 초기조건 (구적 모멘트)
def rust_f0_args(f0):
    """★ R5c: 분포가 Rust 구적으로 표현되면 (dipole_eps, dipole_axis), 아니면 None.

    Rust 커널(`kin_j_moment*`)은 f₀ 를 콜백으로 받지 않고 **페르미-디랙(+선택적
    쌍극변조)** 만 안다.  그래서 디스패치는 f₀ 를 **알아볼 수 있을 때만** 간다:
      · `fs.f_fermi_dirac` 그 자체        → (0.0, 2)
      · `f_dipole(eps, axis)` 의 반환값   → (eps, axis)   (base 가 기본일 때만 표식)
    그 밖의 커스텀 f₀ 는 numpy 로 남는다 — 조용히 다른 분포를 적분하는 것보다 느린
    쪽이 낫다.
    """
    if f0 is fs.f_fermi_dirac:
        return 0.0, 2
    return getattr(f0, "_rust_dipole", None)


def J_moment(a_vec, mass, l, i, f0=fs.f_fermi_dirac, *, backend=None):
    """J^(i)_{A_l} = ∫ dλ dΩ λ² E (λ/E)^n e_{⟨A_l⟩} f   (n = l+2i).

    a_vec: 방향 스케일인자 (3,) — freestream 과 동일한 Bianchi I 정확 특성곡선
    (불변기저 운동량 p_i = const, P^i = p_i/a_i).
    반환: l=0 이면 float, 아니면 shape (3,)*l 의 PSTF numpy 배열.

    ★ R5c: 알아볼 수 있는 f₀ 면 Rust 구적(`kin_j_moment`, 같은 격자·7배)으로 간다.
      `backend="python"` 이 numpy 오라클이다.  두 경로는 차등테스트로 1e−12 에 묶여
      있고, v=0 비트-정확 쌍(J ↔ J′)은 **Rust 쌍끼리도** 성립한다 (cargo 게이트).
    """
    args = rust_f0_args(f0)
    policy = BackendPolicy.PYTHON_ORACLE if backend == "python" else backend
    selected = select_backend(
        "hierarchy.J_moment",
        policy=policy,
        l=l,
        i=i,
        f0_supported=args is not None,
    )
    if selected.uses_rust:
        rc = selected.native_module
        assert rc is not None and args is not None
        flat = np.asarray(rc.kin_j_moment(
            np.ascontiguousarray(np.asarray(a_vec, float)), float(mass),
            int(l), int(i), float(args[0]), int(args[1])))
        return float(flat[0]) if l == 0 else flat.reshape((3,) * l)
    a = np.asarray(a_vec, float)
    if a.shape != (3,):
        raise ValueError("a_vec must be shape (3,)")
    if l < 0 or i < -1:
        raise ValueError("l >= 0, i >= -1")
    V = float(np.prod(a))
    Q, DQ, NH, WA = fs._Q, fs._DQ, fs._NHAT, fs._WANG
    P = (Q[:, None, None] * NH[None, :, :]) / a[None, None, :]      # P^i = p_i/a_i
    P2 = np.einsum("rai,rai->ra", P, P)
    lam = np.sqrt(P2)
    E = np.sqrt(mass ** 2 + P2)
    n = l + 2 * i
    # dλ λ² dΩ f  (freestream 과 동일한 측도·부피 정규화)
    # f0 는 등방 f0(q) 또는 방향의존 f0(q, nhat)->(nr,nang) 둘 다 허용.
    # ★ 방향의존이 필요한 이유: 등방 f0 는 f(p)=f(-p) 라서 **홀수 l 다극이 항등적으로 0**
    #   이 되어 (A) 항군과 q_a 섹터를 시험할 수 없다 (실측 확인: |J_a| ~ 3e-15).
    #   Vlasov 는 f = f0(불변기저 p_i) 이면 어떤 방향의존도 허용하므로 정당하다.
    try:
        fv = np.asarray(f0(Q, NH), float)          # (nr, nang)
    except TypeError:
        fv = np.asarray(f0(Q), float)[:, None]     # (nr, 1) 등방
    w = (DQ[:, None] * Q[:, None] ** 2) * WA[None, :] * fv / V
    integ = w * E * (lam / np.maximum(E, 1e-300)) ** n
    if l == 0:
        return float(integ.sum())
    ehat = P / np.maximum(lam, 1e-300)[:, :, None]
    # rank-l 방향 외적 e_{a1}...e_{al} 을 누적 (l ≤ L_MAX_SUPPORTED)
    letters = "ijklmn"[:l]
    subs = ",".join(f"ra{c}" for c in letters)
    T = np.einsum(f"ra,{subs}->{letters}", integ, *([ehat] * l))
    return pstf(T)


def J_grid(a_vec, mass, l_max=4, i_max=2, f0=fs.f_fermi_dirac):
    """(l, i) 격자의 J 를 모두 계산해 dict[(l,i)] 로.  계층 초기조건.

    i = -1 도 포함한다 — 식 (12) 에 J^(i-1) 항이 있으므로 i=0 방정식이 J^(-1) 을 참조한다.
    """
    out = {}
    for l in range(l_max + 1):
        for i in range(-1, i_max + 1):
            out[(l, i)] = J_moment(a_vec, mass, l, i, f0)
    return out


# ════════════════════════════════════════════════════════ 식 (11) 대응 (검증용)
def emt_from_J(J):
    """식 (11): ρ=J^(0), q_a=J^(0)_a, π_ab=J^(0)_ab, p=⅓J^(1).

    J: `J_grid` 의 dict.  반환 dict(rho, p, q, pi).
    """
    return dict(rho=J[(0, 0)], p=J[(0, 1)] / 3.0,
                q=J[(1, 0)], pi=J[(2, 0)])


def massless_i_independence_residual(a_vec, l=2, i_pairs=((0, 1), (1, 2)),
                                     f0=fs.f_fermi_dirac):
    """무질량에서 J^(i)_{A_l} 가 i 에 무관함을 확인 (최대 상대차 반환).

    이 성질이 -8/15 유도의 전제다 (PLAN-H §0b).
    """
    worst = 0.0
    for i1, i2 in i_pairs:
        A = np.atleast_1d(np.asarray(J_moment(a_vec, 0.0, l, i1, f0), float))
        B = np.atleast_1d(np.asarray(J_moment(a_vec, 0.0, l, i2, f0), float))
        scale = max(np.abs(A).max(), 1e-300)
        worst = max(worst, float(np.abs(A - B).max() / scale))
    return worst


def misner_source_coefficient(a_vec, f0=fs.f_fermi_dirac):
    """식 (12) l=2,i=0 의 σ-소스 계수를 J 로부터 직접 계산.

        (l(l-1)/(4l²-1)) [(n-1)J^(2) - (l+n+1)J^(1)] / ρ,   l=2, n=2
      = (2/15) [J^(2) - 5 J^(1)] / ρ

    무질량이면 J^(i)=ρ 이므로 **-8/15** 가 되어야 한다 (Misner 중성미자 점성).
    """
    rho = J_moment(a_vec, 0.0, 0, 0, f0)
    J1 = J_moment(a_vec, 0.0, 0, 1, f0)
    J2 = J_moment(a_vec, 0.0, 0, 2, f0)
    return (2.0 / 15.0) * (J2 - 5.0 * J1) / rho


# ════════════════════════════════════════════════════════ H1-b · 균질 축약 RHS
# 식 (12) 의 균질·법선합동 축약 (PLAN-H §0b).  (S)공간미분 = 0 (Bianchi I),
# (V)vorticity = 0, (A)가속도 = 0 (u = e_0 는 측지·비회전).  남는 것:
#
#   J̇^(i)_{A_l} + H[(3+n)J^(i)_{A_l} + (1-n)J^(i+1)_{A_l}]
#     + (l/(2l+3))[(2n+3)J^(i)_{a<A_{l-1}} + (2-2n)J^(i+1)_{a<A_{l-1}}] σ_{a_l>}{}^a   … (A)
#     + [(l-n)J^(i-1)_{abA_l} + (n-1)J^(i)_{abA_l}] σ^{ab}                              … (B)
#     + (l(l-1)/(4l²-1))[(n-1)J^(i+2)_{<A_{l-2}} - (l+n+1)J^(i+1)_{<A_{l-2}}] σ_{a_{l-1}a_l>}  … (C)
#     = 0                              (충돌항은 H3)
#
# ★ 부호규약: 논문은 (+---), 우리는 (-+++).  σ-결합 세 항군(A,B,C)의 전역부호를
#   `SIGMA_SIGNS` 로 두고 **오라클로 확정**한다 (PLAN-H §4).  audit/h_hierarchy.py 가
#   정확 구적해의 수치 시간미분과 대조해 이 값을 결정·검증한다.

#: σ-결합 항군 (A, B, C) 의 전역부호.  오라클로 확정된 값 (audit/h_hierarchy.py).
SIGMA_SIGNS = dict(A=+1.0, B=-1.0, C=-1.0)


def _contract_one(J, sigma):
    """(J·σ)_{A_{l-1} b} = J_{a A_{l-1}} σ_{b a}   — rank l → rank l (지표 하나 교체)."""
    J = np.asarray(J, float)
    l = J.ndim
    letters = "ijklmn"[:l - 1]
    return np.einsum(f"a{letters},ba->{letters}b", J, sigma)


def _contract_two(J, sigma):
    """J_{ab A_l} σ^{ab}  — rank l+2 → rank l."""
    J = np.asarray(J, float)
    l = J.ndim - 2
    letters = "ijklmn"[:l]
    return np.einsum(f"ab{letters},ab->{letters}", J, sigma)


def _outer_sigma(J, sigma):
    """J_{<A_{l-2}} σ_{a_{l-1}a_l>}  — rank l-2 ⊗ σ → PSTF rank l."""
    return pstf(np.multiply.outer(np.asarray(J, float), sigma))


def hierarchy_rhs(J, H, sigma, l, i, signs=None):
    """식 (12) 균질·법선합동 축약의 dJ^(i)_{A_l}/dt.

    J: dict[(l,i)] → J 값 (스칼라 또는 rank-l 배열).  필요한 이웃 (l±2, i±1, i+2) 이
       모두 들어 있어야 한다 (절단·닫힘은 H2 의 일이며, 여기서는 공급된 값을 그대로 쓴다).
    H: Hubble (= Θ/3),  sigma: (3,3) 차원량 trace-free 대칭 shear.
    반환: dJ/dt (J[(l,i)] 와 같은 모양).
    """
    if signs is None:
        signs = SIGMA_SIGNS
    sigma = np.asarray(sigma, float)
    n = l + 2 * i

    def get(ll, ii):
        v = J.get((ll, ii))
        if v is None:
            raise KeyError(f"J[({ll},{ii})] 없음 — hierarchy_rhs 는 이웃을 요구한다")
        return v

    # --- H 항
    out = -H * ((3.0 + n) * np.asarray(get(l, i), float)
                + (1.0 - n) * np.asarray(get(l, i + 1), float))

    # --- (A) l→l 지표교체 결합 (l ≥ 1)
    if l >= 1:
        cA = l / (2.0 * l + 3.0)
        tA = ((2.0 * n + 3.0) * _contract_one(get(l, i), sigma)
              + (2.0 - 2.0 * n) * _contract_one(get(l, i + 1), sigma))
        out = out - signs["A"] * cA * (pstf(tA) if l >= 2 else tA)

    # --- (B) l+2 → l 이중축약
    # ★ 구조적 사실: (l - n) = l - (l+2i) = **-2i** 이므로 i=0 에서 정확히 0 이다.
    #   즉 i=0 방정식은 J^(-1) 을 참조하지 않으며, 계층은 **i 아래로 닫힌다**
    #   (i_min=0 으로 충분; 아래로 무한 퇴행이 없다).
    cB_prev = l - n                                    # = -2i
    tB = (n - 1.0) * _contract_two(get(l + 2, i), sigma)
    if cB_prev != 0.0:
        tB = tB + cB_prev * _contract_two(get(l + 2, i - 1), sigma)
    out = out - signs["B"] * tB

    # --- (C) l-2 → l 외적 (l ≥ 2)
    if l >= 2:
        cC = l * (l - 1.0) / (4.0 * l * l - 1.0)
        tC = ((n - 1.0) * _outer_sigma(get(l - 2, i + 2), sigma)
              - (l + n + 1.0) * _outer_sigma(get(l - 2, i + 1), sigma))
        out = out - signs["C"] * cC * tC

    return pstf(out) if l >= 2 else out


# ──────────────────────────────────── 정확 구적해의 수치 시간미분 (오라클)
def background_step(a_vec, H, sigma_diag, dt):
    """Bianchi I 배경 한 스텝:  ȧ_i = (H + σ_i) a_i."""
    a = np.asarray(a_vec, float)
    return a * (1.0 + (H + np.asarray(sigma_diag, float)) * dt)


def dJ_dt_exact(a_vec, mass, l, i, H, sigma_diag, dt=1e-5, f0=fs.f_fermi_dirac):
    """정확 구적해의 중심차분 시간미분 — 계층 RHS 검증용 **오라클**."""
    ap = background_step(a_vec, H, sigma_diag, dt)
    am = background_step(a_vec, H, sigma_diag, -dt)
    Jp = np.asarray(J_moment(ap, mass, l, i, f0), float)
    Jm = np.asarray(J_moment(am, mass, l, i, f0), float)
    return (Jp - Jm) / (2.0 * dt)


def rhs_residual(a_vec, mass, H, sigma_diag, l, i, signs=None, dt=1e-5,
                 f0=fs.f_fermi_dirac, i_pad=3):
    """계층 RHS 대 정확 구적 시간미분의 **상대잔차** (부호확정·검증의 핵심 지표).

    이웃 J 는 전부 정확 구적으로 공급하므로 절단 오차가 섞이지 않는다 —
    RHS 자체의 정확성만 시험한다.
    """
    sigma = np.diag(np.asarray(sigma_diag, float))
    J = {}
    for ll in (l - 2, l, l + 2):
        if ll < 0:
            continue
        for ii in range(i - 1, i + i_pad):
            J[(ll, ii)] = J_moment(a_vec, mass, ll, ii, f0)
    pred = np.atleast_1d(np.asarray(hierarchy_rhs(J, H, sigma, l, i, signs), float))
    exact = np.atleast_1d(dJ_dt_exact(a_vec, mass, l, i, H, sigma_diag, dt, f0))
    # ★ 스케일 하한 (물리적 정규화): 등방 f0 의 **홀수 l 은 항등적으로 0** 이므로
    #   |exact| 로만 나누면 0/0 이 되어 무의미하다 (실측: |J_a| ~ 3e-15 인데 잔차 1.0).
    #   방정식의 주도 규모 H·ρ 의 1e-8 을 하한으로 둔다 — 배정밀도+구적에서 이보다
    #   작은 항은 애초에 분해되지 않는다는 정직한 선언.
    rho = abs(float(np.asarray(J[(0, 0)], float))) if (0, 0) in J else \
        abs(float(J_moment(a_vec, mass, 0, 0, f0)))
    floor = 1e-8 * abs(H) * rho
    scale = max(np.abs(exact).max(), floor, 1e-300)
    return float(np.abs(pred - exact).max() / scale)


def f_dipole(eps=0.3, axis=2, base=fs.f_fermi_dirac):
    """방향의존 f₀(q, n̂) = f_base(q)·(1 + ε n̂_axis) — **홀수 l 다극을 켜기 위한** 시험용.

    Vlasov 는 f = f₀(불변기저 p_i) 이면 임의의 방향의존을 허용한다 (특성곡선 보존).
    등방 f₀ 로는 (A) 항군과 q_a 섹터가 항등적으로 0 이라 시험되지 않는다.
    """
    def f(q, nhat=None):
        b = base(q)
        if nhat is None:
            return b
        return b[:, None] * (1.0 + eps * nhat[None, :, axis])
    if base is fs.f_fermi_dirac:            # ★ R5c: Rust 디스패치가 알아보는 표식
        f._rust_dipole = (float(eps), int(axis))
    return f


# ════════════════════════════════════════════════════════ H2 · 절단·닫힘과 적분
# 식 (12) 의 (l,i) 방정식은 이웃 (l±2, i-1 … i+2) 을 참조하므로 두 방향 모두 닫아야 한다.
#
# **l 방향**: 단순절단 J_{A_l} = 0 for l > l_max.  배경에는 k-모드가 없고 결합이 σ 를
#   통해서만 일어나므로 |Σ| ≪ 1 에서 빠르게 수렴한다 (l_max 수렴 시험으로 확인).
#
# **i 방향**: 단순히 0 으로 자르면 **무질량에서 틀린다** — 무질량은 (λ/E)=1 이라
#   J^(i) 가 i 에 무관(=ρ)하기 때문이다.  반대로 유질량은 λ/E<1 이라 J^(i) → 0.
#   두 극한을 모두 맞추려면 **기하 외삽**이 옳다:
#       J^(i_max+1) ≈ J^(i_max) · (J^(i_max)/J^(i_max-1))
#   무질량이면 비가 1 이므로 J 를 그대로 이어주고(정확), 유질량이면 비<1 로 감쇠한다.

def close_i(J, l, i_max, i_min=0):
    """i 방향 닫힘 — 기하 외삽으로 J^(i_max+1), J^(i_max+2) 를 채운다.

    무질량(비=1)에서 정확하고, 유질량(비<1)에서 감쇠를 재현한다.
    단순 0-절단은 무질량을 망가뜨린다 (검증: test_i_closure_matters).
    """
    a = np.atleast_1d(np.asarray(J[(l, i_max)], float))
    b = np.atleast_1d(np.asarray(J[(l, i_max - 1)], float))
    shape = np.asarray(J[(l, i_max)]).shape
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.where(np.abs(b) > 1e-300, a / b, 0.0)
    ratio = np.clip(np.nan_to_num(ratio, nan=0.0), -1.0, 1.0)
    nxt = (a * ratio).reshape(shape)
    J[(l, i_max + 1)] = nxt if shape else float(nxt)
    nxt2 = (np.atleast_1d(nxt) * ratio).reshape(shape)
    J[(l, i_max + 2)] = nxt2 if shape else float(nxt2)
    return J


def _zeros_like_rank(l):
    return 0.0 if l == 0 else np.zeros((3,) * l)


def close_grid(J, l_max, i_max, i_min=0):
    """(l,i) 격자를 RHS 가 요구하는 이웃까지 닫는다 (l 단순절단 + i 기하외삽)."""
    Jc = dict(J)
    for l in range(l_max + 1):
        close_i(Jc, l, i_max, i_min)
    # l 단순절단: l_max+1, l_max+2 를 0 으로
    for l in (l_max + 1, l_max + 2):
        for i in range(i_min, i_max + 3):
            Jc[(l, i)] = _zeros_like_rank(l)
    return Jc


def hierarchy_state_rhs(J, H, sigma, l_max, i_max, i_min=0, signs=None):
    """격자 전체의 dJ/dt (닫힘 적용).  반환 dict[(l,i)] (l ≤ l_max, i_min ≤ i ≤ i_max)."""
    Jc = close_grid(J, l_max, i_max, i_min)
    out = {}
    for l in range(l_max + 1):
        for i in range(i_min, i_max + 1):
            out[(l, i)] = hierarchy_rhs(Jc, H, sigma, l, i, signs)
    return out


def integrate_hierarchy(a0, mass, H, sigma_diag, t_end, nsteps=200,
                        l_max=4, i_max=3, f0=fs.f_fermi_dirac, i_min=0, *,
                        backend=None):
    """계층을 RK4 로 적분 (H, σ 상수 배경).  반환 dict(t, a, J_hist, exact_hist).

    배경: ȧ_i = (H+σ_i)a_i 이므로 a_i(t) = a_i(0) exp((H+σ_i)t) — 정확.
    `exact_hist` 는 같은 시각의 **정확 구적** J (오라클).
    """
    a0 = np.asarray(a0, float)
    sig_d = np.asarray(sigma_diag, float)
    sigma = np.diag(sig_d)
    dt = t_end / nsteps
    keys = [(l, i) for l in range(l_max + 1) for i in range(i_min, i_max + 1)]
    J = {k: J_moment(a0, mass, k[0], k[1], f0, backend=backend) for k in keys}

    def axpy(base, d, c):
        return {k: base[k] + c * np.asarray(d[k]) for k in keys}

    ts, Js, Es = [], [], []
    for s in range(nsteps + 1):
        t = s * dt
        a_t = a0 * np.exp((H + sig_d) * t)
        ts.append(t)
        Js.append({k: (float(J[k]) if np.ndim(J[k]) == 0 else np.array(J[k]))
                   for k in keys})
        Es.append(dict(rho=J_moment(a_t, mass, 0, 0, f0, backend=backend),
                       p=J_moment(a_t, mass, 0, 1, f0, backend=backend) / 3.0,
                       pi=J_moment(a_t, mass, 2, 0, f0, backend=backend)))
        if s == nsteps:
            break
        k1 = hierarchy_state_rhs(J, H, sigma, l_max, i_max, i_min)
        k2 = hierarchy_state_rhs(axpy(J, k1, 0.5 * dt), H, sigma, l_max, i_max, i_min)
        k3 = hierarchy_state_rhs(axpy(J, k2, 0.5 * dt), H, sigma, l_max, i_max, i_min)
        k4 = hierarchy_state_rhs(axpy(J, k3, dt), H, sigma, l_max, i_max, i_min)
        J = {k: J[k] + dt / 6.0 * (np.asarray(k1[k]) + 2 * np.asarray(k2[k])
                                   + 2 * np.asarray(k3[k]) + np.asarray(k4[k]))
             for k in keys}
    return dict(t=np.array(ts), J=Js, exact=Es)


def trajectory_error(res):
    """적분 궤적 대 정확 구적의 최대 상대오차 (ρ, p, π)."""
    e_rho = e_p = e_pi = 0.0
    for J, E in zip(res["J"], res["exact"]):
        e_rho = max(e_rho, abs(float(J[(0, 0)]) - E["rho"]) / abs(E["rho"]))
        e_p = max(e_p, abs(float(J[(0, 1)]) / 3.0 - E["p"]) / abs(E["p"]))
        sc = max(np.abs(E["pi"]).max(), 1e-8 * abs(E["rho"]))
        e_pi = max(e_pi, float(np.abs(np.asarray(J[(2, 0)]) - E["pi"]).max() / sc))
    return dict(rho=e_rho, p=e_p, pi=e_pi)
