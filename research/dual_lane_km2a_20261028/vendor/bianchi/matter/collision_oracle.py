"""
V2a · **충돌항의 독립 오라클** — 각격자 직접 축약 (discrete ordinates).

★ 왜 몬테카를로가 아닌가 (PLAN-V2 §3 측정):
    MC   광자 10⁶개  →  p₂ 상대오차 **9 %**
    구적 격자 32점   →  **4 × 10⁻¹⁵**
  게다가 강한 감쇠 자체가 분산감소(상관표본)의 전제를 파괴하고 (상관계수 0.10),
  잡음 진폭이 1/(a√N) 이라 우주론적 이방성 a~10⁻⁵ 에서는 N~10¹⁶ 이 필요하다.
  MC 는 `audit/v2_monte_carlo.py` 에 **구조 오라클**(마르코프 커널 확인)로만 남긴다.

★ 무엇을 검증하는가 — H3 은 λ_l **값**을 두 경로로 확인했지만, 그것을
  **계층에 붙인 결과**(PSTF rank-l 텐서를 (1−λ_l) 로 감쇠시키는 것이 실제 각산란
  연산자와 같은가)는 검증된 적이 없다.  그 등식이 여기서 시험하는 대상이다:

        ∫dΩ  n_{⟨A_l⟩}(n̂)  P(n̂·n̂′)   =?   λ_l · n_{⟨A_l⟩}(n̂′)

★ 순환 차단 — **두 가지를 인용하지 않고 재구성**한다:
  1. 위상함수: Thomson 미분단면적을 편광기저에서 조립하고 (∝ Σ_{ij}|ê_i·ê′_j|²),
     규격화 상수까지 **∫P dΩ = 1 로 스스로 정한다** (3/16π 를 넣지 않는다).
  2. PSTF 기저: n_{⟨A_l⟩} 을 고전 항등식
        n_{⟨A_l⟩} = (−1)^l/(2l−1)!! · r^{l+1} ∂_{A_l}(1/r)
     로 **기호미분해서** 만든다 (`hierarchy.pstf` 를 쓰지 않는다).
  ⇒ 이 파일은 `bianchi.matter.collision` 과 `hierarchy.pstf` 를 **전혀 임포트하지 않는다**.
    (교차검증용 비교는 audit/시험 쪽에서 한다.)
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np


# ═══════════════════════════════════════ 1. 구면 격자
@lru_cache(maxsize=32)
def sphere_grid(n_theta=12, n_phi=24):
    """Gauss–Legendre(cosθ) × 균일(φ) 곱격자.  반환 (n[N,3], w[N]) — Σw = 1."""
    x, wx = np.polynomial.legendre.leggauss(int(n_theta))
    ph = (np.arange(int(n_phi)) + 0.5) * 2 * np.pi / int(n_phi)
    X, PH = np.meshgrid(x, ph, indexing="ij")
    W = np.outer(wx, np.full(int(n_phi), 2 * np.pi / int(n_phi))) / (4 * np.pi)
    s = np.sqrt(np.maximum(0.0, 1 - X ** 2))
    n = np.stack([s * np.cos(PH), s * np.sin(PH), X], -1).reshape(-1, 3)
    return n, W.ravel()


# ═══════════════════════════════════════ 2. 위상함수 (재유도)
def _pol_basis(n):
    """n̂ 에 수직인 정규직교 편광쌍 (배열 입력 지원)."""
    n = np.atleast_2d(np.asarray(n, float))
    a = np.zeros_like(n)
    small = np.abs(n[:, 0]) < 0.9
    a[small, 0] = 1.0
    a[~small, 1] = 1.0
    e1 = np.cross(n, a)
    e1 /= np.linalg.norm(e1, axis=1, keepdims=True)
    return e1, np.cross(n, e1)


def phase_unnormalised(n_in, n_out):
    """★ Thomson 미분단면적을 **쌍극복사에서 조립** — (1+μ²) 를 인용하지 않는다.

        dσ/dΩ ∝ ½ Σ_{i,j} |ê_i(n̂) · ê′_j(n̂′)|²      (입사 비편광, 출사 편광 합산)

    반환 (N_in, N_out) 행렬 (규격화 전).
    """
    a1, a2 = _pol_basis(n_in)
    b1, b2 = _pol_basis(n_out)
    tot = np.zeros((len(a1), len(b1)))
    for u in (a1, a2):
        for v in (b1, b2):
            tot += (u @ v.T) ** 2
    return 0.5 * tot


def scattering_operator(n_theta=12, n_phi=24):
    """★ 산란 연산자 S — (S f)(n̂) = ∫dΩ′ P(n̂·n̂′) f(n̂′), 격자 위 행렬.

    규격화는 **측정으로 정한다**: 각 행이 ∫P dΩ′ = 1 이 되도록 나눈다.
    (3/16π 같은 상수를 넣지 않으므로 그 상수도 검증 대상이 된다 — `phase_norm` 참조.)
    """
    n, w = sphere_grid(n_theta, n_phi)
    K = phase_unnormalised(n, n)
    S = K * w[None, :]
    row = S.sum(axis=1)
    return S / row[:, None], n, w


def phase_norm(n_theta=24, n_phi=48):
    """★ 규격화 상수를 **측정**한다: ∫ P_raw dΩ = 8π/3  ⇒  P = (3/8π)P_raw.

    이것이 (3/16π)(1+μ²) 의 3/16π 와 같은지 확인하는 독립 경로.
    반환 dict(measured, expected_8pi_over_3, rel_err).
    """
    n, w = sphere_grid(n_theta, n_phi)
    e = np.array([[0.0, 0.0, 1.0]])
    raw = phase_unnormalised(e, n)[0]
    meas = float(4 * np.pi * np.sum(w * raw))          # ∫ P_raw dΩ
    exp = 8 * np.pi / 3.0
    return dict(measured=meas, expected_8pi_over_3=exp,
                rel_err=abs(meas - exp) / exp)


# ═══════════════════════════════════════ 3. PSTF 기저 (기호미분으로 재구성)
@lru_cache(maxsize=8)
def _stf_lambdified(l):
    """n_{⟨A_l⟩} = (−1)^l/(2l−1)!! · r^{l+1} ∂_{A_l}(1/r) 를 기호미분해 lambdify.

    ★ `hierarchy.pstf` (최소제곱 사영) 와 **완전히 다른 구성**이다.
    """
    import sympy as sp
    x = sp.symbols("x0 x1 x2", real=True)
    r = sp.sqrt(sum(v ** 2 for v in x))
    dfact = 1
    for k in range(1, 2 * l, 2):
        dfact *= k
    expr_cache = {}

    def deriv(idx):
        key = tuple(sorted(idx))
        if key not in expr_cache:
            e = 1 / r
            for i in key:
                e = sp.diff(e, x[i])
            expr_cache[key] = sp.simplify((-1) ** l * r ** (l + 1) * e / dfact)
        return expr_cache[key]

    idxs = np.indices((3,) * l).reshape(l, -1).T if l else np.zeros((1, 0), int)
    exprs = [deriv(tuple(t)) for t in idxs]
    return sp.lambdify(x, exprs, "numpy"), l


def stf_basis(l, n):
    """n_{⟨A_l⟩}(n̂) 를 격자 전점에서 — 반환 shape (N,) + (3,)*l."""
    n = np.atleast_2d(np.asarray(n, float))
    if l == 0:
        return np.ones(len(n))
    fn, _ = _stf_lambdified(l)
    vals = fn(n[:, 0], n[:, 1], n[:, 2])
    out = np.stack([np.broadcast_to(np.asarray(v, float), (len(n),)) for v in vals], -1)
    return out.reshape((len(n),) + (3,) * l)


# ═══════════════════════════════════════ 4. ★ 핵심 게이트 — λ_l 측정
def eigenvalue_from_grid(l, n_theta=12, n_phi=24):
    """★ λ_l 을 **각격자에서 직접** 잰다 — Legendre 도, 다극 대수도 쓰지 않는다.

        S · n_{⟨A_l⟩}  =?  λ_l · n_{⟨A_l⟩}      (격자 위 고유값 문제)

    반환 dict(lam, residual) — residual 은 고유벡터 관계의 상대잔차
    (λ 가 맞아도 잔차가 크면 '고유함수가 아니다' 는 뜻이라 반드시 함께 본다).
    """
    S, n, w = scattering_operator(n_theta, n_phi)
    B = stf_basis(l, n)                                # (N,)+(3,)*l
    flat = B.reshape(len(n), -1)
    out = S @ flat
    num = float(np.sum(w[:, None] * out * flat))
    den = float(np.sum(w[:, None] * flat * flat))
    lam = num / den
    res = float(np.abs(out - lam * flat).max()
                / max(np.abs(flat).max(), 1e-300))
    return dict(lam=lam, residual=res)


def eigenvalue_table(l_max=4, n_theta=12, n_phi=24):
    return [(l, eigenvalue_from_grid(l, n_theta, n_phi)) for l in range(l_max + 1)]


# ═══════════════════════════════════════ 5. 임의 f 에 대한 연산자 시험
def moment_on_grid(l, f, n, w):
    """M_{A_l}[f] = ∫dΩ n_{⟨A_l⟩} f — 격자 축약."""
    B = stf_basis(l, n).reshape(len(n), -1)
    m = np.einsum("N,N,Nk->k", w, np.asarray(f, float), B)
    return m.reshape((3,) * l) if l else float(m[0])


def operator_residual(l, seed=0, n_theta=12, n_phi=24, l_mix=4):
    """★ **순수 l 이 아닌** f 에 대해서도 M_l[S f] = λ_l M_l[f] 인가.

    f 를 l = 0…l_mix 성분의 무작위 혼합으로 만든다 — 다른 l 이 새어 들어오면
    (즉 연산자가 l 을 섞으면) 여기서 깨진다.  `eigenvalue_from_grid` 보다 강한 시험.
    """
    S, n, w = scattering_operator(n_theta, n_phi)
    rng = np.random.default_rng(seed)
    f = np.zeros(len(n))
    for k in range(l_mix + 1):
        B = stf_basis(k, n).reshape(len(n), -1)
        f = f + B @ rng.normal(size=B.shape[1]) * 0.5 ** k
    lam = eigenvalue_from_grid(l, n_theta, n_phi)["lam"]
    m_in = np.atleast_1d(np.asarray(moment_on_grid(l, f, n, w), float))
    m_out = np.atleast_1d(np.asarray(moment_on_grid(l, S @ f, n, w), float))
    sc = max(np.abs(m_in).max(), 1e-300)
    return float(np.abs(m_out - lam * m_in).max() / sc)


def photon_number_residual(seed=0, n_theta=12, n_phi=24):
    """Thomson 은 광자 수를 보존한다 — ∫S f dΩ = ∫f dΩ (l=0 이 안 변한다)."""
    S, n, w = scattering_operator(n_theta, n_phi)
    rng = np.random.default_rng(seed)
    f = 1.0 + 0.3 * rng.normal(size=len(n))
    a, b = float(np.sum(w * f)), float(np.sum(w * (S @ f)))
    return abs(a - b) / abs(a)


# ═══════════════════════════════════════ 6. 대조군 (게이트가 살아 있는지)
def perturbed_eigenvalue(l, delta, n_theta=12, n_phi=24):
    """★ 위상함수에 인위적 P_l 성분을 δ 만큼 더하면 λ_l 이 **움직여야** 한다.

    게이트가 '무엇을 하든 통과' 하는 죽은 시험이 아님을 보이는 대조군.
    (P_l 은 여기서도 Legendre 를 쓰지 않고 n_{⟨A_l⟩}·n′_{⟨A_l⟩} 축약으로 만든다.)
    """
    n, w = sphere_grid(n_theta, n_phi)
    K = phase_unnormalised(n, n)
    B = stf_basis(l, n).reshape(len(n), -1)
    K = K + delta * (B @ B.T)
    S = K * w[None, :]
    S = S / S.sum(axis=1)[:, None]
    flat = B
    out = S @ flat
    num = float(np.sum(w[:, None] * out * flat))
    den = float(np.sum(w[:, None] * flat * flat))
    return num / den


# ═══════════════════════════════════════ 7. 전체 사슬 — 실제 분포에서 모멘트까지
#
# 지금까지는 각도만 봤다.  여기서는 **물리 운동량 공간 (λ, ê)** 위의 실제 Bianchi I
# 분포에 산란 연산자를 걸고, 모멘트 J^(i)_{A_l} 을 재조립해 계층의 예측과 대조한다.
#
# ★ 이것이 검증하는 추가 사실 두 가지:
#   (a) 탄성 산란이므로 **i (속도가중) 를 섞지 않는다** — 계층이 그렇게 가정한다.
#   (b) 지름 가중 E(λ/E)^n 이 각 연산자와 가환이다.
def _phys_grid(n_r=48, n_theta=12, n_phi=24, L=3.0):
    """물리 운동량 격자 (λ, ê) — 지름은 (0,∞) 사상 Gauss-Legendre."""
    xr, wr = np.polynomial.legendre.leggauss(int(n_r))
    lam = L * (1 + xr) / (1 - xr)
    dlam = wr * 2 * L / (1 - xr) ** 2
    n, w = sphere_grid(n_theta, n_phi)
    return lam, dlam, n, w


def moments_from_grid(F, mass, l, i, lam, dlam, n, w):
    """J^(i)_{A_l} = ∫dλ λ² ∫dΩ  E (λ/E)^n ê_{⟨A_l⟩} F(λ, ê)   (n = l+2i)."""
    E = np.sqrt(mass ** 2 + lam ** 2)
    rad = dlam * lam ** 2 * E * (lam / E) ** (l + 2 * i)     # (n_r,)
    B = stf_basis(l, n).reshape(len(n), -1)                  # (N, 3^l)
    ang = np.einsum("N,Nk->Nk", 4 * np.pi * w, B)            # dΩ 무게
    m = np.einsum("r,rN,Nk->k", rad, np.asarray(F, float), ang)
    return m.reshape((3,) * l) if l else float(m[0])


def bianchi_I_distribution(a_vec, lam, n, f0=None, dipole=0.0, axis=2):
    """F(λ, ê) = f₀(q)·(1 + ε ê_axis),  q_i = a_i P^i = a_i λ ê_i.

    ε = 0 이면 Bianchi I 자유흐름 **정확해**다.  다만 그 경우 F(P)=F(−P) 라
    **홀수 l 이 항등적으로 0** 이므로 (측정: |J₁|/ρ = 2.3e−17, |J₃|/ρ = 4.9e−17)
    홀수 l 게이트가 0/0 이 된다.  ε ≠ 0 은 홀수 l 을 켜기 위한 **벌크 운동 성분**이다
    (H1 이 `f_dipole` 로 한 것과 같은 취지 — 여기서는 각도 쪽에 건다).
    """
    from bianchi.matter import freestream as fs
    f0 = fs.f_fermi_dirac if f0 is None else f0
    a = np.asarray(a_vec, float)
    q = lam[:, None] * np.sqrt(((a[None, :] * n) ** 2).sum(-1))[None, :]
    F = np.asarray(f0(q), float)
    if dipole:
        F = F * (1.0 + dipole * n[None, :, axis])
    return F


def collision_chain_residual(a_vec=(1.0, 0.85, 1.18), mass=0.0, l_max=4, i_max=2,
                             n_r=48, n_theta=12, n_phi=24, f0=None, dipole=0.3):
    """★★ **전체 사슬 게이트** — 계층의 C[J] = −(1−λ_l)J 가 실제 산란과 같은가.

    격자에서 F → S·F 를 만들고 두 모멘트를 재조립해
        [M(S·F) − M(F)] + (1 − λ_l)·M(F)
    를 **ρ 로 규격화**해 본다 (n_eσ_T = 1).

    ★ ρ 규격화인 이유: |M(F)| 로 나누면 홀수 l 에서 0/0 이 된다 (등방 f₀ 는
      홀수 l 이 정확히 0).  `dipole` 로 홀수 l 을 켜되 규격화는 ρ 로 고정한다.

    반환 dict[(l,i)] = 상대오차.  **i 에 무관해야** 한다 (탄성).
    """
    S, n, w = scattering_operator(n_theta, n_phi)
    lam, dlam, n2, w2 = _phys_grid(n_r, n_theta, n_phi)
    assert np.allclose(n, n2)
    F = bianchi_I_distribution(a_vec, lam, n, f0, dipole)
    FS = F @ S.T                                             # 각도에만 작용
    rho = abs(float(moments_from_grid(F, mass, 0, 0, lam, dlam, n, w)))
    out = {}
    for l in range(l_max + 1):
        lam_l = eigenvalue_from_grid(l, n_theta, n_phi)["lam"]
        for i in range(i_max + 1):
            m0 = np.atleast_1d(np.asarray(
                moments_from_grid(F, mass, l, i, lam, dlam, n, w), float))
            m1 = np.atleast_1d(np.asarray(
                moments_from_grid(FS, mass, l, i, lam, dlam, n, w), float))
            out[(l, i)] = float(np.abs((m1 - m0) + (1.0 - lam_l) * m0).max() / rho)
    return out


def odd_l_is_switched_on(a_vec=(1.0, 0.85, 1.18), dipole=0.3, mass=0.0,
                         n_r=48, n_theta=12, n_phi=24, l_max=4):
    """★ 정직성 진단: 어떤 l 이 실제로 0 이 아닌지 **먼저 보고**한다.

    0 인 성분에 게이트를 걸어 두고 "통과했다" 고 말하지 않기 위한 장치.
    반환 [(l, |J_l|/ρ (등방), |J_l|/ρ (쌍극))].
    """
    lam, dlam, n, w = _phys_grid(n_r, n_theta, n_phi)
    out = []
    for eps in (0.0, dipole):
        F = bianchi_I_distribution(a_vec, lam, n, None, eps)
        rho = abs(float(moments_from_grid(F, mass, 0, 0, lam, dlam, n, w)))
        col = []
        for l in range(l_max + 1):
            m = np.atleast_1d(np.asarray(
                moments_from_grid(F, mass, l, 0, lam, dlam, n, w), float))
            col.append(float(np.abs(m).max() / rho))
        out.append(col)
    return [(l, out[0][l], out[1][l]) for l in range(l_max + 1)]


def i_mixing_residual(a_vec=(1.0, 0.85, 1.18), mass=1.0, l=2, i_max=3, **kw):
    """★ 탄성 가정의 직접 시험: 감쇠비가 **i 에 무관**한가 (유질량에서도).

    반환 [(i, 측정 감쇠비)] — 전부 같아야 한다.
    """
    n_r = kw.pop("n_r", 48)
    nt, npz = kw.pop("n_theta", 12), kw.pop("n_phi", 24)
    S, n, w = scattering_operator(nt, npz)
    lam, dlam, _, _ = _phys_grid(n_r, nt, npz)
    F = bianchi_I_distribution(a_vec, lam, n, kw.pop("f0", None))
    FS = F @ S.T
    out = []
    for i in range(i_max + 1):
        m0 = np.atleast_1d(np.asarray(moments_from_grid(F, mass, l, i, lam, dlam, n, w), float))
        m1 = np.atleast_1d(np.asarray(moments_from_grid(FS, mass, l, i, lam, dlam, n, w), float))
        k = np.abs(m0) > 1e-12 * np.abs(m0).max()
        out.append((i, float(np.median(m1[k] / m0[k]))))
    return out


# ═══════════════════════════════════════ 8. ★★ 편광 포함 (V2d)
#
# H3 은 광자 전단점성을 `8/27` (Thomson 9/10 포함) 과 `4/15` (미포함) 사이에서
# **정직하게 미결**로 남겼다.  여기서 편광을 포함한 산란 연산자를 **같은 쌍극복사
# 조립에서** 만들어 그 문제를 측정으로 닫는다.
#
# 핵심: `phase_unnormalised` 는 출사 편광을 **합산**해 버렸다.  합산하지 않고 2×2
# 결맞음 행렬 J_{jk} = ⟨E_j E_k*⟩ 를 그대로 나르면 편광이 살아난다:
#
#       J^out_{jk}(n̂) = ∫dΩ′ Σ_{i,m} A_{ji} A_{km} J^in_{im}(n̂′),
#       A_{ji} = ê_j(n̂) · ê_i(n̂′)
#
# (쌍극복사: 전자가 입사 전기장으로 흔들리고, 나가는 방향의 편광성분은 사영뿐이다.)
_SYM = ((0, 0), (1, 1), (0, 1))          # 상태벡터 (J11, J22, J12)


def polarized_scattering_operator(n_theta=12, n_phi=24):
    """★ 편광을 **합산하지 않은** Thomson 산란 연산자 (3N × 3N).

    규격화는 다시 **측정으로** 정한다: 등방·비편광 상태가 불변이어야 한다.
    반환 (M, n, w).
    """
    n, w = sphere_grid(n_theta, n_phi)
    N = len(n)
    e1, e2 = _pol_basis(n)
    E = np.stack([e1, e2], 1)                            # (N, 2, 3)
    A = np.einsum("ajx,bix->abji", E, E)                 # A[out, in, j, i]
    M = np.zeros((N, 3, N, 3))
    for oj, (j, k) in enumerate(_SYM):
        for ii, (i, m) in enumerate(_SYM):
            if i == m:
                M[:, oj, :, ii] = A[:, :, j, i] * A[:, :, k, m]
            else:                                        # J12 는 (i,m)+(m,i) 둘 다
                M[:, oj, :, ii] = (A[:, :, j, i] * A[:, :, k, m]
                                   + A[:, :, j, m] * A[:, :, k, i])
    M = (M * w[None, None, :, None]).reshape(3 * N, 3 * N)

    def total_I(v):
        x = v.reshape(N, 3)
        return float(np.sum(w * (x[:, 0] + x[:, 1])))

    v0 = np.zeros((N, 3))
    v0[:, 0] = v0[:, 1] = 0.5                            # 등방 비편광
    return M * (total_I(v0) / total_I(M @ v0.ravel())), n, w


def l2_reduced_block(n_theta=12, n_phi=24, n_krylov=6):
    """★ l=2 불변 부분공간에서 산란 연산자의 **축소 블록**을 뽑는다.

    비편광 l=2 상태에서 출발해 Krylov 부분공간을 만들고 직교화한다.
    측정: 부분공간 차원 = **2**, 블록 = [[1/10, √6/10], [√6/10, 3/5]]
    (√6/10 = 0.2449 — CMB 편광 계층의 그 √6 이다.)  고유값 {7/10, 0}.
    """
    M, n, w = polarized_scattering_operator(n_theta, n_phi)
    N = len(n)
    # ★ 결맞음 행렬의 자연스러운 내적은 ⟨J,J′⟩ = ∫dΩ Tr(J J′) 이므로 J12 성분의
    #   무게가 **2** 다 (비대각이 두 번 들어간다).  처음에 무게 1 로 썼더니 축소
    #   블록이 비대칭이 되어 (0.24503 vs 0.24486) √6/10 구조가 8.6e−5 어긋났다.
    #   고유값은 기저 무관이라 멀쩡했지만, 블록의 구조를 읽으려면 내적이 맞아야 한다.
    W3 = (w[:, None] * np.array([1.0, 1.0, 2.0])[None, :]).ravel()

    def ip(a, b):
        return float(np.sum(W3 * a * b))

    B2 = stf_basis(2, n).reshape(N, 9)
    T = np.diag([1.0, -0.5, -0.5]).ravel()
    pat = B2 @ T
    v = np.zeros((N, 3))
    v[:, 0] = v[:, 1] = 0.5 * pat                        # 비편광 l=2
    v = v.ravel()
    K = [v / np.sqrt(ip(v, v))]
    for _ in range(n_krylov):
        u = M @ K[-1]
        for q in K:
            u = u - ip(u, q) * q
        nu = np.sqrt(ip(u, u))
        if nu < 1e-9:
            break
        K.append(u / nu)
    K = np.array(K)
    S = np.array([[ip(K[a], M @ K[b]) for b in range(len(K))]
                  for a in range(len(K))])
    return dict(block=S, dim=len(K), eigenvalues=np.sort(np.linalg.eigvals(S).real)[::-1])


def effective_quadrupole_damping(n_theta=12, n_phi=24):
    """★★ **준정적 유효 감쇠** — V2d 의 답.

    팽창·전단 소스는 **강도 채널에만** 들어간다 (편광은 산란으로만 생긴다).
    준정적 균형 (I − S)x = s, s = (1, 0) 를 풀어 강도 사중극의 유효 감쇠 1/x₀ 를 잰다.

    측정:  편광 포함 **0.750000000000 = 3/4**   vs   비편광 0.9 (= 1 − λ₂)
    ⇒ 점성비 (9/10)/(3/4) = **6/5** — Hu 의 강의노트 "편광이 점성을 6/5 배 늘린다"와 일치.
    """
    r = l2_reduced_block(n_theta, n_phi)
    S = r["block"]
    D = np.eye(len(S)) - S
    s = np.zeros(len(S))
    s[0] = 1.0
    x = np.linalg.solve(D, s)
    return dict(effective=1.0 / x[0], unpolarised=0.9, ratio=0.9 * x[0],
                block=S, dim=r["dim"])


def shear_viscosity_coefficient(n_theta=12, n_phi=24):
    """★ η·n_eσ_T/ρ 를 세 판으로 나란히 — H3 의 미결 항목을 **측정으로 닫는다**.

        η = (4/15) ρ / (유효감쇠 · n_eσ_T)

        각구조 무시 (감쇠 1)      → 4/15  = 0.26667   ← H3 이 문헌 관례로 적어둔 값
        비편광    (감쇠 9/10)     → 8/27  = 0.29630   ← 우리 비편광 계층의 자기정합 값
        편광 포함 (감쇠 3/4)      → 16/45 = 0.35556   ← **물리적으로 옳은 값** (측정)
    """
    eff = effective_quadrupole_damping(n_theta, n_phi)["effective"]
    return dict(no_angular_structure=4.0 / 15.0,
                unpolarised=(4.0 / 15.0) / 0.9,
                polarised=(4.0 / 15.0) / eff,
                effective_damping=eff,
                targets=dict(four_fifteenths=4 / 15, eight_27=8 / 27, sixteen_45=16 / 45))
