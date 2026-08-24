"""
H5-d1 · tilted 관측자의 **정확 구적 모멘트** — l ≥ 2 오라클의 토대.

★ 왜 tilted 에도 정확 오라클이 있는가:
  Bianchi I 무충돌 Vlasov 의 정확해는 법선 프레임에서 f(t,p) = f₀(q_i), q_i = const.
  tilted 관측자는 **같은 분포함수** f 를 보되 4-운동량을 다르게 분해할 뿐이고,
  boost 는 순수 대수다.  따라서 tilted 모멘트도 정확 구적으로 나온다.

측도: d³P/E 가 로런츠 불변이므로 d³P′ = (E′/E) d³P.  기존 격자를 그대로 쓴다:

    J′^(i)_{A_l} = ∫ d³P′ E′ (λ′/E′)^n e′_{⟨A_l⟩} f
                 = ∫ (d³q/V) · (E′/E) · E′ (λ′/E′)^n · e′_{⟨A_l⟩} · f₀(q)

    n = l + 2i,   V = a₁a₂a₃,   P^i = q n̂_i/a_i   (기존 freestream 규약과 동일)

boost 대수 (순수 boost 사틀 E_A = γv_A n + [δ_AB + k v_A v_B] ê_B, k = γ²/(γ+1)):

    E′  = γ (E − v·P)
    P′^A = P^A + v_A [ k (v·P) − γ E ]

★ 이 유도를 **믿지 않는다**: `boost_algebra_residual` 이 격자 전점에서
  λ′² = E′² − m² 를 확인한다.  부호 하나만 틀려도 깨지는 항등식이다.

★ 왜 이게 H1 보다 나은 게이트인가:
  H1 에서는 등방 f₀ 가 f(p)=f(−p) 라 홀수 l 이 항등적으로 0 이어서 (|J_a| ~ 3e−15)
  (A) 항군을 시험하려고 `f_dipole` 을 **인공 도입**해야 했다.  tilted 에서는
  **boost 자체가 물리적 쌍극자원**이다 — 등방 f₀ + 등방 a_vec 에서도 q′_A ≠ 0.
  분포를 왜곡하지 않고 홀수 l 을 시험할 수 있다.
"""
from __future__ import annotations

import numpy as np

from bianchi.matter import freestream as fs
from bianchi.matter.hierarchy import pstf, rust_f0_args

try:                                        # R5c · Rust 보정구적 (없으면 numpy)
    import bianchi_rustcore as _RC
except Exception:                           # pragma: no cover
    _RC = None


# ═══════════════════════════════════════ boost 대수
def boost_factors(v):
    """(γ, k) — k = γ²/(γ+1) = (γ−1)/v² (v→0 특이점을 제거한 형태)."""
    v = np.asarray(v, float)
    v2 = float(v @ v)
    if v2 >= 1.0:
        raise ValueError(f"|v| >= 1 은 물리적이지 않다 (v²={v2})")
    gam = 1.0 / np.sqrt(1.0 - v2)
    return gam, gam ** 2 / (gam + 1.0)


def boost_momentum(P, E, v):
    """법선 프레임 (E, P^A) → tilted 사틀 (E′, P′^A).

    반환 (E′, P′, λ′, e′)  — 배열 모양은 P 와 같은 앞쪽 축을 유지한다.
    """
    v = np.asarray(v, float)
    gam, k = boost_factors(v)
    vdotP = P @ v
    Ep = gam * (E - vdotP)
    Pp = P + v * (k * vdotP - gam * E)[..., None]
    lamp = np.sqrt(np.einsum("...i,...i->...", Pp, Pp))
    ep = Pp / np.maximum(lamp, 1e-300)[..., None]
    return Ep, Pp, lamp, ep


def boost_algebra_residual(a_vec=(1.0, 0.9, 1.2), v=(0.15, -0.1, 0.2), mass=0.7):
    """★ 자기검증: λ′² = E′² − m² 가 격자 **전점**에서 성립하는가.

    유도를 믿지 않고 측정한다 — boost 부호 오타를 한 줄로 잡는 항등식.
    반환 dict(mass_shell, norm_u, energy_positive).
    """
    a = np.asarray(a_vec, float)
    Q, _, NH, _ = fs._Q, fs._DQ, fs._NHAT, fs._WANG
    P = (Q[:, None, None] * NH[None, :, :]) / a[None, None, :]
    P2 = np.einsum("rai,rai->ra", P, P)
    E = np.sqrt(mass ** 2 + P2)
    Ep, _, lamp, _ = boost_momentum(P, E, v)
    shell = np.abs(lamp ** 2 - (Ep ** 2 - mass ** 2))
    scale = np.maximum(Ep ** 2, 1e-300)
    return dict(mass_shell=float((shell / scale).max()),
                energy_positive=bool((Ep > 0).all()),
                gamma=boost_factors(v)[0])


# ═══════════════════════════════════════ tilted 모멘트
def J_moment_tilted(a_vec, v, mass, l, i, f0=fs.f_fermi_dirac, *, backend=None):
    """J′^(i)_{A_l} — tilted 사틀 성분, 정확 구적.

    v = 0 이면 `hierarchy.J_moment` 와 **비트-정확** 일치해야 한다
    (E′=E, P′=P 이므로 피적분함수가 문자 그대로 동일해진다).

    ★ R5c: 알아볼 수 있는 f₀ 면 Rust 구적(`kin_j_moment_tilted`, 7배)으로 간다.
      `backend="python"` 이 numpy 오라클.  두 백엔드 모두 v=0 비트-정확 쌍을 각자
      만족하므로 (numpy 쌍: 이 파일 §2 시험, Rust 쌍: cargo 게이트) **둘을 함께**
      갈아끼워도 위 불변식은 유지된다 — 한쪽만 바꾸면 깨진다.
    """
    if backend != "python" and _RC is not None and 0 <= l <= 5 and i >= -1:
        args = rust_f0_args(f0)
        if args is not None:
            flat = np.asarray(_RC.kin_j_moment_tilted(
                np.ascontiguousarray(np.asarray(a_vec, float)),
                np.ascontiguousarray(np.asarray(v, float)), float(mass),
                int(l), int(i), float(args[0]), int(args[1])))
            return float(flat[0]) if l == 0 else flat.reshape((3,) * l)
    a = np.asarray(a_vec, float)
    if a.shape != (3,):
        raise ValueError("a_vec must be shape (3,)")
    if l < 0 or i < -1:
        raise ValueError("l >= 0, i >= -1")
    V = float(np.prod(a))
    Q, DQ, NH, WA = fs._Q, fs._DQ, fs._NHAT, fs._WANG
    P = (Q[:, None, None] * NH[None, :, :]) / a[None, None, :]
    P2 = np.einsum("rai,rai->ra", P, P)
    E = np.sqrt(mass ** 2 + P2)
    Ep, _, lamp, ep = boost_momentum(P, E, v)

    try:
        fv = np.asarray(f0(Q, NH), float)              # (nr, nang) 방향의존
    except TypeError:
        fv = np.asarray(f0(Q), float)[:, None]         # (nr, 1) 등방
    # ★ 측도: d³P′ = (E′/E) d³P,  d³P = d³q/V  (야코비안이 (E′/E) 하나로 압축된다)
    w = (DQ[:, None] * Q[:, None] ** 2) * WA[None, :] * fv / V * (Ep / E)
    n = l + 2 * i
    integ = w * Ep * (lamp / np.maximum(Ep, 1e-300)) ** n
    if l == 0:
        return float(integ.sum())
    letters = "ijklmn"[:l]
    subs = ",".join(f"ra{c}" for c in letters)
    T = np.einsum(f"ra,{subs}->{letters}", integ, *([ep] * l))
    return pstf(T)


def moments_tilted(a_vec, v, mass, f0=fs.f_fermi_dirac, *, backend=None):
    """tilted 관측자가 보는 (ρ′, p′, q′_A, π′_AB) = (J′^(0), J′^(1)/3, J′^(0)_a, J′^(0)_ab)."""
    rho = J_moment_tilted(a_vec, v, mass, 0, 0, f0, backend=backend)
    p = J_moment_tilted(a_vec, v, mass, 0, 1, f0, backend=backend) / 3.0
    q = np.asarray(J_moment_tilted(a_vec, v, mass, 1, 0, f0, backend=backend), float)
    pi = np.asarray(J_moment_tilted(a_vec, v, mass, 2, 0, f0, backend=backend), float)
    return rho, p, q, pi


# ═══════════════════════════════════════ ★ 게이트: T^{μν} 프레임 무관성
def _tetrad_flat(v):
    """법선 정규직교기저에서 본 (u^μ, u_μ, E_A^μ, E_{Aμ}).  η = diag(−1,1,1,1)."""
    v = np.asarray(v, float)
    gam, k = boost_factors(v)
    uup = np.r_[gam, gam * v]
    udn = np.r_[-gam, gam * v]
    eup = np.zeros((3, 4))
    edn = np.zeros((3, 4))
    for A in range(3):
        eup[A, 0] = gam * v[A]
        edn[A, 0] = -gam * v[A]
        for B in range(3):
            c = (1.0 if A == B else 0.0) + k * v[A] * v[B]
            eup[A, 1 + B] = c
            edn[A, 1 + B] = c
    return uup, udn, eup, edn


def project_stress_to_tilted(rho, p, pi, v):
    """법선 프레임 (ρ, p, π_ab) 로 T^{μν} 를 세우고 tilted 사틀로 사영.

        ρ′ = T^{μν}u_μu_ν,   q′_A = −T^{μν}u_μE_{Aν},
        π′_AB = S_AB − ⅓δ_AB tr S    (S_AB = T^{μν}E_{Aμ}E_{Bν})

    ★ 계층 방정식을 전혀 쓰지 않는다 — 순수 텐서 대수.
    """
    pi = np.asarray(pi, float)
    T = np.zeros((4, 4))
    T[0, 0] = rho
    T[1:, 1:] = p * np.eye(3) + pi                     # 법선 프레임에서 q_a = 0
    _, udn, _, edn = _tetrad_flat(v)
    rho_p = float(udn @ T @ udn)
    q_p = -np.einsum("m,mn,an->a", udn, T, edn)
    S = np.einsum("am,mn,bn->ab", edn, T, edn)
    pi_p = S - np.trace(S) * np.eye(3) / 3.0
    return rho_p, np.trace(S) / 3.0, q_p, pi_p


def frame_independence_residual(a_vec=(1.0, 0.9, 1.2), v=(0.15, -0.1, 0.2), mass=0.7,
                                f0=fs.f_fermi_dirac):
    """★★ 가장 결정적인 게이트 — boost 대수 + 구적을 **한 번에** 검증.

    T^{μν} 는 텐서이므로, 법선 구적의 (ρ, 0, p, π) 를 tilted 사틀로 사영한 값이
    **boosted 구적이 직접 준** (ρ′, q′, π′) 와 같아야 한다.
    여기서 어긋나면 이후 어떤 계층 검증도 의미가 없다.
    """
    from bianchi.matter import hierarchy as H
    rho = H.J_moment(a_vec, mass, 0, 0, f0)
    p = H.J_moment(a_vec, mass, 0, 1, f0) / 3.0
    pi = np.asarray(H.J_moment(a_vec, mass, 2, 0, f0), float)
    q0 = np.asarray(H.J_moment(a_vec, mass, 1, 0, f0), float)

    rho_t, p_t, q_t, pi_t = project_stress_to_tilted(rho, p, pi, v)
    rho_q, p_q, q_q, pi_q = moments_tilted(a_vec, v, mass, f0)
    return dict(
        rho=abs(rho_t - rho_q) / rho,
        p=abs(p_t - p_q) / rho,
        q=float(np.abs(q_t - q_q).max()) / rho,
        pi=float(np.abs(pi_t - pi_q).max()) / rho,
        normal_q_is_zero=float(np.abs(q0).max()) / rho,      # 법선 프레임 q_a = 0 확인
        rho_tilted=rho_q, rho_normal=rho)


# ═══════════════════════════════════════ 구조적 측정
def analytic_dipole_ratio(rho, p, v):
    """등방 배경에서 |q′|/ρ′ 의 **닫힌형** (π=0 이면 정확).

        q′_A = −γ²(ρ+p) v_A,     ρ′ = γ²(ρ + p v²)
        ⇒  |q′|/ρ′ = v (ρ+p) / (ρ + p v²)

    무질량(p=ρ/3) 이면 (4/3)v / (1 + v²/3) — 작은 v 에서 (4/3)v.
    ★ 이 닫힌형은 구적을 전혀 쓰지 않으므로 boosted 구적의 **독립 검산**이 된다.
    """
    v = float(np.linalg.norm(np.asarray(v, float)))
    return v * (rho + p) / (rho + p * v ** 2)


def dipole_from_boost(a_vec=(1.0, 1.0, 1.0), mass=0.0, vs=(0.0, 0.05, 0.1, 0.2, 0.4)):
    """★ 등방 f₀ + **등방 a_vec** 에서도 boost 만으로 q′ 가 켜진다.

    H1 은 홀수 l 을 시험하려고 `f_dipole` 을 인공 도입해야 했다.  여기서는 필요 없다.
    무질량 극한의 기대: 작은 v 에서 |q′|/ρ′ ≈ (4/3)v  (측정으로 확인).
    """
    out = []
    for s in vs:
        v = np.array([0.0, 0.0, float(s)])
        rho, _, q, _ = moments_tilted(a_vec, v, mass)
        out.append((float(s), float(np.abs(q).max() / rho),
                    (float(np.abs(q).max() / rho) / s / (4.0 / 3.0)) if s > 0 else np.nan))
    return out


def odd_l_activation(a_vec=(1.0, 1.0, 1.0), mass=0.0, v=(0.0, 0.0, 0.25), l_max=5):
    """홀수 l 이 boost 로 켜지는지 (등방 f₀·등방 a_vec).  반환 [(l, |J′_l|/ρ′)]."""
    rho = J_moment_tilted(a_vec, v, mass, 0, 0)
    out = []
    for l in range(l_max + 1):
        j = J_moment_tilted(a_vec, v, mass, l, 0)
        w = abs(j) if l == 0 else float(np.abs(np.asarray(j)).max())
        out.append((l, w / rho))
    return out


def grid_adequacy_scan(a_vec=(1.0, 0.9, 1.2), mass=0.3, vmax=0.9, n=10):
    """★ boost 후 E′ 가 방향의존이라 반경격자가 부적합해질 수 있다 — **측정해 보고**한다.

    지표: 프레임 무관성 게이트의 최대 상대잔차 대 |v|.  유효 tilt 범위를 조용히
    쓰지 않기 위한 스캔 (H5-c 의 cond 스캔과 같은 취지).
    """
    out = []
    d = np.array([1.0, -0.5, 1.5])
    d /= np.linalg.norm(d)
    for f in np.linspace(0.0, vmax, n):
        r = frame_independence_residual(a_vec, tuple(d * f), mass)
        out.append((float(f), boost_factors(d * f)[0],
                    max(r["rho"], r["p"], r["q"], r["pi"])))
    return out
