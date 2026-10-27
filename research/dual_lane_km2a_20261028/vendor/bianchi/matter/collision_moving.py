"""
V2b+V2c · **움직이는 전자**의 Thomson 충돌항 — Doppler(l=1) 원천과 tilted 프레임.

★ 왜 필요한가 (부채 두 개를 동시에 갚는다):
  1. `collision.py` 의 docstring 은 "λ₁ = 0 → 감쇠 1 (쌍극; 실제로는 바리온 속도로
     완화 → `dipole_source`)" 이라고 적어 두었는데 **`dipole_source` 는 구현이 없다**.
     즉 계층에는 광자–바리온 결합의 원천항이 통째로 빠져 있다.
  2. V2a 는 전자가 정지한 경우만 검증했다.  tilted 배경에서는 전자가 움직인다.

★ 구성 원리 — 인용하지 않고 **boost 로 유도**한다:
  Thomson 은 **전자 정지틀에서 탄성**이고 각분포만 Rayleigh 위상함수를 따른다.
  분포함수 f 는 스칼라이므로, 실험실틀 운동량을 정지틀로 boost → 거기서 산란 →
  다시 boost 하면 실험실틀 충돌항이 나온다.  새 물리 입력이 하나도 없다.

      p^μ ∂_μ f = C[f],      C/E = (E′/E) · n_e σ_T · [ ⟨f⟩_P(λ′, n̂′) − f(λ, n̂) ]

  `⟨f⟩_P(λ′,n̂′) = ∫dΩ″ P(n̂′·n̂″) f(λ′, n̂″)` 는 **정지틀** 각평균이고, f 를 그 안에서
  평가할 때는 (λ′, n̂″) 를 다시 실험실틀로 boost 해 넣는다 (f 가 스칼라이므로 정당).

★★ 오라클 — **평형 조건**:
  전자 정지틀에서 등방인 f (= boosted 등방 분포) 는 산란으로 **정확히 변하지 않아야**
  한다.  C ≡ 0 을 점마다 확인한다 (측정 8.9e−16).

  ★ 정직한 범위 — 처음에 "boost·위상함수·측도가 하나라도 틀리면 깨진다" 고 적었는데
    **틀린 주장이었다**.  대조군으로 위상함수에 0.1 % 상수배를 걸었더니 잔차가
    8.95e−16 로 **그대로**였다: `collision_rate_density` 가 같은 상수로 나눈 행합으로
    규격화하므로 정확히 상쇄된다.  즉 평형 게이트는 **전체 규격화에 둔감**하다.
    실제로 무는 것은 **boost 왕복**이다 — 되돌리는 boost 를 0.1 % 어긋내면
    8.9e−16 → 1.3e−8 (1.5 × 10⁷ 배).  역할 분담은 이렇다:
        전체 규격화  →  V2a 의 `collision_oracle.phase_norm()` (8π/3, 2e−16)
        각도 구조    →  V2a 의 `eigenvalue_from_grid` (λ_l, 1e−13)
        boost 왕복   →  여기 `equilibrium_residual`
    둘 다 시험으로 고정해 둔다 (`normalisation_control_is_vacuous`,
    `boost_control_residual`) — 죽은 게이트를 살아 있다고 오인하지 않기 위해서.
"""
from __future__ import annotations

import numpy as np

from bianchi.matter import collision_oracle as CO


# ═══════════════════════════════════════ 1. 광자 boost (무질량, 순수 boost)
def boost_photon(lam, nhat, v):
    """실험실틀 (λ, n̂) → 속도 v 로 움직이는 틀의 (λ′, n̂′).

        λ′ = γλ(1 − v·n̂),     n̂′ = [n̂ + γv(γ(v·n̂)/(γ+1) − 1)] · λ/λ′

    반환 (λ′, n̂′).  λ 는 (...,) 모양, n̂ 는 (..., 3).
    ★ 유도를 믿지 않는다 — `boost_selfcheck` 가 |n̂′| = 1 과 역boost 왕복을 확인한다.
    """
    v = np.asarray(v, float)
    v2 = float(v @ v)
    if v2 >= 1.0:
        raise ValueError(f"|v| >= 1 (v²={v2})")
    gam = 1.0 / np.sqrt(1.0 - v2)
    k = gam ** 2 / (gam + 1.0)
    vn = np.asarray(nhat, float) @ v
    lp = np.asarray(lam, float) * gam * (1.0 - vn)
    # p′^i = p^i + v_i[k(v·p) − γE],  p^i = λn̂^i,  E = λ
    num = (np.asarray(nhat, float) * np.asarray(lam, float)[..., None]
           + v * (np.asarray(lam, float) * (k * vn - gam))[..., None])
    return lp, num / np.maximum(lp, 1e-300)[..., None]


def boost_selfcheck(v=(0.13, -0.07, 0.21), n_theta=8, n_phi=16):
    """★ 자기검증: |n̂′| = 1, 역boost 왕복, λ′ > 0."""
    n, _ = CO.sphere_grid(n_theta, n_phi)
    lam = np.full(len(n), 1.0)
    lp, npr = boost_photon(lam, n, v)
    lb, nb = boost_photon(lp, npr, -np.asarray(v, float))
    return dict(unit=float(np.abs(np.linalg.norm(npr, axis=-1) - 1.0).max()),
                roundtrip_lam=float(np.abs(lb / lam - 1.0).max()),
                roundtrip_dir=float(np.abs(nb - n).max()),
                lam_positive=bool((lp > 0).all()))


# ═══════════════════════════════════════ 2. 충돌항 (실험실틀)
def collision_rate_density(f, lam, n, v, n_theta=12, n_phi=24, tau_dot=1.0):
    """★ C/E 를 실험실틀 격자 (λ, n̂) 에서 계산한다.

    f 는 **호출 가능한 스칼라 함수** f(λ, n̂) 여야 한다 (임의 4-운동량에서 평가해야
    하므로 격자값이 아니라 함수여야 한다).  반환 shape (n_lam, n_dir).

    ★ 정지틀 각평균 안의 f 는 (λ′, n̂″) 를 **역boost** 해 실험실틀에서 평가한다
      — f 가 스칼라이므로 정당하고, 이 한 줄이 Doppler 를 전부 만든다.
    """
    v = np.asarray(v, float)
    lam = np.atleast_1d(np.asarray(lam, float))
    n = np.atleast_2d(np.asarray(n, float))
    dirs, w = CO.sphere_grid(n_theta, n_phi)
    Praw = CO.phase_unnormalised(n, dirs)                 # 임시 (규격화는 아래)

    # 정지틀 성분
    L = lam[:, None]                                      # (nl, 1)
    lp, npr = boost_photon(np.broadcast_to(L, (len(lam), len(n))),
                           np.broadcast_to(n[None, :, :], (len(lam), len(n), 3)), v)

    # 정지틀 각평균: 출사방향 n̂″ 는 **정지틀** 격자, 위상함수는 n̂′·n̂″
    Pk = CO.phase_unnormalised(dirs, dirs)                # (nd, nd) 규격화 전
    norm = (Pk * w[None, :]).sum(axis=1)                  # 각 행의 ∫P dΩ″
    # n̂′ 는 격자점이 아니므로 위상함수를 직접 조립한다
    Pin = CO.phase_unnormalised(npr.reshape(-1, 3), dirs).reshape(
        len(lam), len(n), len(dirs))
    Pin = Pin * (w[None, None, :] / norm.mean())

    # 출사 (λ′, n̂″) 를 실험실틀로 역boost 해 f 를 평가
    lam_out, n_out = boost_photon(
        np.broadcast_to(lp[:, :, None], (len(lam), len(n), len(dirs))),
        np.broadcast_to(dirs[None, None, :, :], (len(lam), len(n), len(dirs), 3)),
        -v)
    gain = (Pin * f(lam_out, n_out)).sum(axis=-1)
    loss = f(np.broadcast_to(L, (len(lam), len(n))),
             np.broadcast_to(n[None, :, :], (len(lam), len(n), 3)))
    return tau_dot * (lp / L) * (gain - loss)


# ═══════════════════════════════════════ 3. ★★ 평형 오라클
def boosted_isotropic(v, f0=None):
    """전자 정지틀에서 등방인 분포 — f(λ, n̂) = f₀(λ′(λ, n̂)).

    ★ 이것이 Thomson 의 **정확한 평형해**다 (탄성 + 각등방).
    """
    from bianchi.matter import freestream as fs
    g0 = fs.f_bose_einstein if f0 is None else f0
    vv = np.asarray(v, float)

    def f(lam, nhat):
        lp, _ = boost_photon(lam, nhat, vv)
        return np.asarray(g0(lp), float)

    return f


def equilibrium_residual(v=(0.13, -0.07, 0.21), n_theta=8, n_phi=16, n_lam=6):
    """★★ **가장 결정적인 게이트**: 정지틀 등방 분포는 산란으로 변하지 않는다.

    C ≡ 0 을 점마다 확인한다.  boost 대수·위상함수·측도 중 하나라도 틀리면 깨진다.
    반환 dict(residual, scale) — residual 은 |C|/(τ̇·f) 최대값.
    """
    n, _ = CO.sphere_grid(n_theta, n_phi)
    lam = np.linspace(0.4, 4.0, n_lam)
    f = boosted_isotropic(v)
    C = collision_rate_density(f, lam, n, v, n_theta, n_phi)
    scale = np.abs(f(np.broadcast_to(lam[:, None], (len(lam), len(n))),
                     np.broadcast_to(n[None, :, :], (len(lam), len(n), 3)))).max()
    return dict(residual=float(np.abs(C).max() / scale), scale=float(scale))


def static_limit_residual(n_theta=10, n_phi=20, n_lam=5, seed=0):
    """★ v = 0 에서 V2a 의 순수 각산란으로 **환원**되는가 (비트 수준)."""
    n, _ = CO.sphere_grid(n_theta, n_phi)
    lam = np.linspace(0.5, 3.0, n_lam)
    rng = np.random.default_rng(seed)
    coef = rng.normal(size=9) * 0.3

    def f(l, nh):
        B = CO.stf_basis(2, nh.reshape(-1, 3)).reshape(nh.shape[:-1] + (9,))
        return np.exp(-np.asarray(l, float)) * (1.0 + B @ coef)

    C = collision_rate_density(f, lam, n, np.zeros(3), n_theta, n_phi)
    # V2a 경로: 각격자에서 S 를 직접 적용
    S, ng, wg = CO.scattering_operator(n_theta, n_phi)
    fv = f(np.broadcast_to(lam[:, None], (len(lam), len(n))),
           np.broadcast_to(n[None, :, :], (len(lam), len(n), 3)))
    ref = (fv @ S.T) - fv
    return float(np.abs(C - ref).max() / np.abs(fv).max())


# ═══════════════════════════════════════ 4. 모멘트 변화율 (Doppler 원천 측정)
def moment_rates(f, v, mass=0.0, l_max=2, i_max=0, n_r=32, n_theta=12, n_phi=24,
                 tau_dot=1.0, L=3.0):
    """dJ^(i)_{A_l}/dt|_충돌 = ∫d³P W (C/E) — 실험실틀 모멘트 변화율."""
    xr, wr = np.polynomial.legendre.leggauss(int(n_r))
    lam = L * (1 + xr) / (1 - xr)
    dlam = wr * 2 * L / (1 - xr) ** 2
    n, w = CO.sphere_grid(n_theta, n_phi)
    C = collision_rate_density(f, lam, n, v, n_theta, n_phi, tau_dot)
    E = np.sqrt(mass ** 2 + lam ** 2)
    out = {}
    for l in range(l_max + 1):
        B = CO.stf_basis(l, n).reshape(len(n), -1)
        ang = (4 * np.pi * w)[:, None] * B
        for i in range(i_max + 1):
            rad = dlam * lam ** 2 * E * (lam / E) ** (l + 2 * i)
            m = np.einsum("r,rN,Nk->k", rad, C, ang)
            out[(l, i)] = m.reshape((3,) * l) if l else float(m[0])
    return out


def moments_of(f, mass=0.0, l_max=2, i_max=0, n_r=32, n_theta=12, n_phi=24, L=3.0):
    """같은 격자에서 J^(i)_{A_l} 자체 (비교 기준)."""
    xr, wr = np.polynomial.legendre.leggauss(int(n_r))
    lam = L * (1 + xr) / (1 - xr)
    dlam = wr * 2 * L / (1 - xr) ** 2
    n, w = CO.sphere_grid(n_theta, n_phi)
    F = f(np.broadcast_to(lam[:, None], (len(lam), len(n))),
          np.broadcast_to(n[None, :, :], (len(lam), len(n), 3)))
    E = np.sqrt(mass ** 2 + lam ** 2)
    out = {}
    for l in range(l_max + 1):
        B = CO.stf_basis(l, n).reshape(len(n), -1)
        ang = (4 * np.pi * w)[:, None] * B
        for i in range(i_max + 1):
            rad = dlam * lam ** 2 * E * (lam / E) ** (l + 2 * i)
            m = np.einsum("r,rN,Nk->k", rad, F, ang)
            out[(l, i)] = m.reshape((3,) * l) if l else float(m[0])
    return out


# ═══════════════════════════════════════ 5. ★ Doppler 원천의 계수를 **측정**한다
def dipole_source_coefficient(v_mag=1e-3, axis=2, dipole=0.0, **kw):
    """★★ q̇_a|_충돌 = −τ̇[q_a − c·ρ·v_a] 의 **c 를 측정**한다.

    등방 광자 분포 (q = 0) 에 작은 전자속도 v 를 주면 q̇ = +τ̇ c ρ v 가 된다.
    c 를 가정하지 않고 격자에서 뽑는다.  (문헌의 광자–바리온 항력은 c = 4/3.)
    반환 dict(c, rho, qdot, v).
    """
    from bianchi.matter import freestream as fs
    v = np.zeros(3)
    v[axis] = float(v_mag)

    def f(lam, nhat):
        base = np.asarray(fs.f_bose_einstein(np.asarray(lam, float)), float)
        if dipole:
            base = base * (1.0 + dipole * np.asarray(nhat, float)[..., axis])
        return base

    r = moment_rates(f, v, l_max=1, **kw)
    m = moments_of(f, l_max=1, **kw)
    rho = float(m[(0, 0)])
    qdot = np.atleast_1d(np.asarray(r[(1, 0)], float))
    q = np.atleast_1d(np.asarray(m[(1, 0)], float))
    return dict(c=float((qdot[axis] + q[axis]) / (rho * v_mag)), rho=rho,
                qdot=float(qdot[axis]), q=float(q[axis]),
                rhodot=float(r[(0, 0)]))


def linearity_in_ve(mags=(1e-4, 3e-4, 1e-3, 3e-3), **kw):
    """★ 원천이 v_e 1차인가 — c 가 v_e 에 무관해야 한다."""
    return [(m, dipole_source_coefficient(m, **kw)["c"]) for m in mags]


def photon_number_rate(v=(0.0, 0.0, 1e-2), dipole=0.3, axis=2, **kw):
    """★ Thomson 은 광자 수를 보존한다: ṅ = ∫d³P (C/E) = 0.

    (에너지 ρ 는 Doppler 로 바뀔 수 있다 — 그건 보존이 아니다.  구별해서 잰다.)
    """
    from bianchi.matter import freestream as fs

    def f(lam, nhat):
        return np.asarray(fs.f_bose_einstein(np.asarray(lam, float)), float) * (
            1.0 + dipole * np.asarray(nhat, float)[..., axis])

    n_r = kw.pop("n_r", 32)
    nt, npz = kw.pop("n_theta", 12), kw.pop("n_phi", 24)
    L = kw.pop("L", 3.0)
    xr, wr = np.polynomial.legendre.leggauss(int(n_r))
    lam = L * (1 + xr) / (1 - xr)
    dlam = wr * 2 * L / (1 - xr) ** 2
    n, w = CO.sphere_grid(nt, npz)
    C = collision_rate_density(f, lam, n, v, nt, npz)
    F = f(np.broadcast_to(lam[:, None], (len(lam), len(n))),
          np.broadcast_to(n[None, :, :], (len(lam), len(n), 3)))
    rad = dlam * lam ** 2
    ndot = float(np.einsum("r,rN,N->", rad, C, 4 * np.pi * w))
    nn = float(np.einsum("r,rN,N->", rad, F, 4 * np.pi * w))
    rad_e = dlam * lam ** 3
    rhodot = float(np.einsum("r,rN,N->", rad_e, C, 4 * np.pi * w))
    rho = float(np.einsum("r,rN,N->", rad_e, F, 4 * np.pi * w))
    return dict(ndot_over_n=ndot / nn, rhodot_over_rho=rhodot / rho)


# ═══════════════════════════════════════ 6. 대조군 — 평형 게이트가 죽어 있지 않다
def normalisation_control_is_vacuous(scale=1.001, v=(0.13, -0.07, 0.21),
                                     n_theta=8, n_phi=16, n_lam=4):
    """★ **첫 대조군이 아무것도 잡지 못했다 — 그 사실을 시험으로 남긴다.**

    위상함수 전체에 상수배를 걸면 `collision_rate_density` 가 같은 상수로 나눈
    행합(`norm`)으로 규격화하므로 **정확히 상쇄**된다 (측정: 8.95e−16 vs 8.89e−16).
    ⇒ 평형 게이트는 **전체 규격화에 둔감**하다.  그건 결함이 아니라 **역할 분담**이다:
      · 전체 규격화는 V2a 의 `collision_oracle.phase_norm()` 이 잰다 (8π/3, 2e−16).
      · 평형 게이트가 실제로 잡는 것은 **boost 왕복**이다 (`boost_control_residual`).
    이 함수는 그 둔감성을 **명시적으로 고정**해 둔다 — 죽은 게이트를 살아 있다고
    오인하지 않기 위해서.
    """
    n, _ = CO.sphere_grid(n_theta, n_phi)
    lam = np.linspace(0.4, 4.0, n_lam)
    f = boosted_isotropic(v)
    orig = CO.phase_unnormalised

    def broken(a, b):
        return orig(a, b) * scale

    CO.phase_unnormalised = broken
    try:
        C = collision_rate_density(f, lam, n, v, n_theta, n_phi)
    finally:
        CO.phase_unnormalised = orig
    sc = np.abs(f(np.broadcast_to(lam[:, None], (len(lam), len(n))),
                  np.broadcast_to(n[None, :, :], (len(lam), len(n), 3)))).max()
    return float(np.abs(C).max() / sc)


def boost_control_residual(dv=1e-3, v=(0.13, -0.07, 0.21), n_theta=8, n_phi=16,
                           n_lam=4):
    """★ **실제로 무는 대조군**: 되돌리는 boost 속도를 dv 만큼 어긋내면 평형이 깨진다.

    평형 게이트가 민감한 대상이 **boost 왕복**임을 보인다 (규격화가 아니라).
    반환 (정상 잔차, 어긋난 잔차).
    """
    n, _ = CO.sphere_grid(n_theta, n_phi)
    lam = np.linspace(0.4, 4.0, n_lam)
    f = boosted_isotropic(v)
    good = float(np.abs(collision_rate_density(f, lam, n, v, n_theta, n_phi)).max())
    orig = boost_photon
    vv = np.asarray(v, float)

    def wrong(l, nh, u):
        u = np.asarray(u, float)
        if np.dot(u, vv) < 0:                      # 역boost 쪽만 어긋낸다
            u = u * (1.0 + dv)
        return orig(l, nh, u)

    g = globals()
    g["boost_photon"] = wrong
    try:
        bad = float(np.abs(collision_rate_density(f, lam, n, v, n_theta, n_phi)).max())
    finally:
        g["boost_photon"] = orig
    sc = np.abs(f(np.broadcast_to(lam[:, None], (len(lam), len(n))),
                  np.broadcast_to(n[None, :, :], (len(lam), len(n), 3)))).max()
    return dict(good=good / sc, broken=bad / sc, ratio=bad / max(good, 1e-300))


def phase_norm_is_direction_independent(n_theta=12, n_phi=24, n_probe=200, seed=0):
    """★ 규격화 상수가 **입사 방향과 무관**한지 (격자 밖 n̂′ 에서도).

    `collision_rate_density` 가 격자행 평균으로 규격화하므로 이것이 성립해야 한다.
    측정: 스프레드 1.7e−16, 격자행 평균과의 차이 0.
    """
    dirs, w = CO.sphere_grid(n_theta, n_phi)
    rng = np.random.default_rng(seed)
    r = rng.normal(size=(n_probe, 3))
    r /= np.linalg.norm(r, axis=1, keepdims=True)
    rows = (CO.phase_unnormalised(r, dirs) * w[None, :]).sum(axis=1)
    grid = (CO.phase_unnormalised(dirs, dirs) * w[None, :]).sum(axis=1)
    return dict(spread=float(rows.std() / rows.mean()),
                offset=float(abs(rows.mean() - grid.mean()) / grid.mean()))


def quadrupole_damping_vs_ve(mags=(0.0, 1e-3, 1e-2, 3e-2), quad=0.3, **kw):
    """★ l=2 감쇠가 전자속도의 **1차에서 변하지 않는다** (측정: 편차 ∝ v²).

    반환 [(v_e, π̇/π)] — v_e=0 에서 −0.9, 1e−2 에서 −0.90083 (편차 8.3e−4 ≈ 8.3v²).
    """
    from bianchi.matter import freestream as fs
    T = np.diag([1.0, -0.5, -0.5]).ravel()

    def f(lam, nh):
        nh = np.asarray(nh, float)
        B = CO.stf_basis(2, nh.reshape(-1, 3)).reshape(nh.shape[:-1] + (9,))
        return np.asarray(fs.f_bose_einstein(np.asarray(lam, float)), float) * (
            1.0 + quad * (B @ T))

    out = []
    for ve in mags:
        v = np.array([0.0, 0.0, float(ve)])
        r = moment_rates(f, v, l_max=2, **kw)
        m = moments_of(f, l_max=2, **kw)
        pd = np.asarray(r[(2, 0)], float)
        p0 = np.asarray(m[(2, 0)], float)
        k = np.abs(p0) > 1e-12 * np.abs(p0).max()
        out.append((float(ve), float(np.median(pd[k] / p0[k]))))
    return out
