"""
PR-47 · 우주론적 거리와 이방 BAO.

BAO 표준자:  음향지평 r_s(z_drag) 를 각(횡단)·시선(방사) 두 방향으로 재어
  D_M/r_s (횡단),  D_H/r_s (방사),  D_V/r_s (부피평균) 를 얻는다.

이방(Bianchi) 배경의 핵심:  시선 팽창률이 방향에 의존한다.

    H_∥(n̂) = θ/3 + σ_ab n̂^a n̂^b = H (1 + Σ_ab n̂^a n̂^b)      (Σ = σ/H)

  → D_H(n̂) = c/H_∥(n̂) 가 방향마다 달라지고, BAO 의 Alcock-Paczynski 비
    D_M/D_H 에 사중극(ℓ=2) 이방성이 생긴다.  이것이 이방 BAO 신호다.

r_s 는 drag 시기(z~1060, 복사·물질기 깊숙이)에서 굳으므로 그때의 **평균** 팽창률로
계산한다 (이방성은 후기 거리에 각인).  c_s = c/√(3(1+R)),  R = 3ρ_b/4ρ_γ.

FLRW 극한(Σ→0): 표준 ΛCDM 값 (r_s≈147 Mpc, D_V(0.5)/r_s 등) 재현.
"""
from __future__ import annotations

import numpy as np
from scipy.integrate import quad

from bianchi.physical import units as U


# ---------------------------------------------------------------- 배경 H(z)
def flrw_hubble(z, H0=67.4, Om=0.315, Or=9.24e-5, OL=None):
    """평탄 ΛCDM H(z) [km/s/Mpc].  Or 은 광자+무질량ν (Ω_r h²≈4.15e-5 → Ω_r≈9.2e-5)."""
    z = np.asarray(z, float)
    if OL is None:
        OL = 1.0 - Om - Or
    return H0 * np.sqrt(Or * (1 + z) ** 4 + Om * (1 + z) ** 3 + OL)


def directional_hubble(H, Sigma, nhat):
    """시선 방향 팽창률 H_∥(n̂) = H(1 + Σ_ab n̂^a n̂^b)  (차원 H 단위)."""
    Sigma = np.asarray(Sigma, float); nhat = np.asarray(nhat, float)
    nhat = nhat / np.linalg.norm(nhat)
    return H * (1.0 + nhat @ Sigma @ nhat)


# ---------------------------------------------------------------- 음향지평
def _R_baryon(z, Omega_b_h2=0.0224, Omega_g_h2=None):
    """R = 3ρ_b/4ρ_γ = (3 Ω_b)/(4 Ω_γ) /(1+z)."""
    if Omega_g_h2 is None:
        Omega_g_h2 = U.photon_omega_h2()
    return (3.0 * Omega_b_h2) / (4.0 * Omega_g_h2) / (1.0 + z)


def sound_horizon(z_drag=None, H0=67.4, Om=0.315, Ob_h2=0.0224,
                  Or=9.24e-5, h=None, z_max=1e5, include_tail=True):
    """음향지평 r_s(z_d) = ∫_{z_d}^∞ c_s/H dz  [Mpc].  표준 ≈ 147 Mpc.

    c_s = c/√(3(1+R)),  R = 3ρ_b/4ρ_γ.

    ★ v3.0 (A3) — **절단 오차 수정**.  이전 판은 z_max=1e5 에서 자르고 끝냈는데,
      복사기 꼬리가 2.7 Mpc (≈2%) 나 된다:  z>z_max 에서 R→0, H→H₀√Ω_r(1+z)² 이므로

          ∫_{z_max}^∞ c_s/H dz  →  (c/√3) / (H₀√Ω_r) / (1+z_max)

      이 해석 꼬리를 더하면 수치적분과 1% 내로 일치하고(확인함), r_s 가 Planck 대비
      -2% → **-0.15%** 로 개선된다.

    ★ 함정 (v3.0 에서 발견): 이전 default 인 Eisenstein-Hu `drag_redshift`(≈1021)는
      **빠진 꼬리를 우연히 벌충**해 147.8 (0.5% 오차) 처럼 보이게 했다 — 두 오차의
      상쇄였다.  꼬리를 고친 지금 그 조합은 +2.3% 로 어긋난다.  따라서 기본 z_drag 을
      자기일관 값(`drag_redshift_tau`)으로 바꾼다.

    include_tail=False 면 구(舊) 동작(절단)을 재현한다 — 회귀 비교용.
    """
    if z_drag is None:
        z_drag = drag_redshift_tau(Ob_h2=Ob_h2, H0=H0, Om=Om, Or=Or)
    if h is None:
        h = H0 / 100.0

    def integrand(z):
        R = _R_baryon(z, Ob_h2)
        cs = U.C_LIGHT_KM_S / np.sqrt(3.0 * (1.0 + R))          # km/s
        Hz = flrw_hubble(z, H0, Om, Or)                          # km/s/Mpc
        return cs / Hz                                           # Mpc
    val, _ = quad(integrand, z_drag, z_max, limit=200)
    if include_tail:
        val += sound_horizon_tail(z_max, H0, Or)
    return float(val)


def sound_horizon_tail(z_max, H0=67.4, Or=9.24e-5):
    """복사기 해석 꼬리 ∫_{z_max}^∞ c_s/H dz = (c/√3)/(H₀√Ω_r)/(1+z_max)  [Mpc].

    z ≫ z_eq 에서 R ∝ 1/(1+z) → 0 이므로 c_s → c/√3, H → H₀√Ω_r (1+z)².
    ★ 한계: 아주 이른 시기 g_*(T) 증가로 실제 H 는 더 크므로 참 꼬리는 이보다 약간
      작다.  z_max=1e5 에서 이 보정은 전체의 <0.2% 수준이다.
    """
    return (U.C_LIGHT_KM_S / np.sqrt(3.0)) / (H0 * np.sqrt(Or)) / (1.0 + z_max)


def drag_redshift_tau(Ob_h2=0.0224, H0=67.4, Om=0.315, Or=9.24e-5,
                      z_lo=800.0, z_hi=1400.0, n_grid=600):
    """자기일관 바리온 drag 적색이동:  τ_drag(z_d) = 1.

        τ_drag(z) = ∫_0^z σ_T n_e c / [R(z') H(z') (1+z')] dz'
      1/R 인자는 광자→바리온 운동량 전달 효율.  x_e 는 Peebles 해(모듈 자체)를 쓴다.

    ★ Eisenstein-Hu 적합식(`recombination.drag_redshift`)과 달리 이 값은 우리 자신의
      재결합사(史)와 일관된다 — A3 에서 r_s 꼬리를 고친 뒤에는 이쪽을 기본으로 쓴다.
    """
    from bianchi.thermo.recombination import peebles_xe, _NB0_PER_OBH2
    h = H0 / 100.0
    zg = np.linspace(z_hi, 10.0, n_grid)                 # 내림차순 (peebles_xe 규약)
    xe = peebles_xe(zg, Ob_h2, Om * h * h, h)
    sigma_T = 6.6524587e-25          # cm²
    c_cm = 2.99792458e10             # cm/s
    n_H = _NB0_PER_OBH2 * Ob_h2 * (1.0 + zg) ** 3        # cm^-3
    Hz_s = flrw_hubble(zg, H0, Om, Or) / U.MPC_KM        # s^-1
    R = _R_baryon(zg, Ob_h2)
    dtau_dz = sigma_T * xe * n_H * c_cm / (R * Hz_s * (1.0 + zg))
    # 오름차순 정렬 후 0→z 누적
    order = np.argsort(zg)
    zs = zg[order]; dt = dtau_dz[order]
    tau = np.concatenate([[0.0], np.cumsum(0.5 * (dt[1:] + dt[:-1]) * np.diff(zs))])
    # τ=1 교차점 (선형보간)
    i = int(np.searchsorted(tau, 1.0))
    if i <= 0 or i >= len(zs):
        return float(np.clip(zs[np.argmin(np.abs(tau - 1.0))], z_lo, z_hi))
    z0, z1 = zs[i - 1], zs[i]; t0, t1 = tau[i - 1], tau[i]
    return float(z0 + (1.0 - t0) * (z1 - z0) / (t1 - t0))


# ---------------------------------------------------------------- 거리들
def sound_horizon_fit(Om_h2=0.1430, Ob_h2=0.02237, Onu_h2=6.4e-4):
    """음향지평 r_drag [Mpc] — Aubourg et al. 2015 (BOSS) eq.16 보정식.

        r_d = 55.154 exp[-72.3(Ω_ν h²+0.0006)²] / [(Ω_cb h²)^0.25351 (Ω_b h²)^0.12807]
      Ω_cb = Ω_c+Ω_b (중성미자 제외).  Planck 우주론에서 CAMB 대비 ~0.1%.
    물리적분(sound_horizon) 이 반해석적 ~2% 오차를 갖는 반면, 이 보정식은 정밀 오라클.
    """
    Ocb_h2 = Om_h2 - Onu_h2
    return float(55.154 * np.exp(-72.3 * (Onu_h2 + 0.0006) ** 2)
                 / (Ocb_h2 ** 0.25351 * Ob_h2 ** 0.12807))


def comoving_distance(z, H0=67.4, Om=0.315, Or=9.24e-5, H_of_z=None):
    """시선 공변거리 D_C(z) = ∫_0^z c/H dz'  [Mpc]  (등방 배경)."""
    def Hz(zz):
        return H_of_z(zz) if H_of_z is not None else flrw_hubble(zz, H0, Om, Or)
    val, _ = quad(lambda zz: U.C_LIGHT_KM_S / Hz(zz), 0.0, float(z), limit=200)
    return float(val)


def transverse_distance(z, **kw):
    """횡단 공변거리 D_M.  평탄우주에서 D_M = D_C."""
    return comoving_distance(z, **kw)


def hubble_distance(z, H0=67.4, Om=0.315, Or=9.24e-5, H_of_z=None):
    """방사 Hubble 거리 D_H(z) = c/H(z)  [Mpc]."""
    Hz = H_of_z(z) if H_of_z is not None else flrw_hubble(z, H0, Om, Or)
    return float(U.C_LIGHT_KM_S / Hz)


def volume_distance(z, **kw):
    """부피평균 거리 D_V = [D_M² · c z/H(z)]^{1/3} = [D_M² · z D_H]^{1/3}  [Mpc]."""
    DM = transverse_distance(z, **kw)
    DH = hubble_distance(z, **kw)
    return float((DM ** 2 * z * DH) ** (1.0 / 3.0))


def bao_observables(z, r_s=None, **kw):
    """BAO 비율 D_M/r_s, D_H/r_s, D_V/r_s 와 Alcock-Paczynski F_AP = D_M/D_H."""
    if r_s is None:
        r_s = sound_horizon(H0=kw.get("H0", 67.4), Om=kw.get("Om", 0.315),
                            Or=kw.get("Or", 9.24e-5))
    DM = transverse_distance(z, **kw); DH = hubble_distance(z, **kw)
    DV = volume_distance(z, **kw)
    return dict(z=float(z), r_s=float(r_s),
                DM_over_rs=DM / r_s, DH_over_rs=DH / r_s, DV_over_rs=DV / r_s,
                F_AP=DM / DH)


# ---------------------------------------------------------------- 이방 BAO
def anisotropic_bao(z, Sigma, nhats=None, r_s=None, H0=67.4, Om=0.315,
                    Or=9.24e-5):
    """방향별 방사 거리 D_H(n̂) 의 이방성.  Σ 사영으로 시선 팽창률이 방향 의존.

    반환: dict(nhats, DH_over_rs(n̂), F_AP(n̂), anisotropy = (max-min)/mean).
    (횡단 D_M 은 시선적분 평균이라 이방성 억제 — 방사 D_H 가 주된 신호.)
    """
    if nhats is None:
        nhats = np.array([[1., 0, 0], [0, 1., 0], [0, 0, 1.]])
    nhats = np.atleast_2d(np.asarray(nhats, float))
    if r_s is None:
        r_s = sound_horizon(H0=H0, Om=Om, Or=Or)
    Hz_iso = flrw_hubble(z, H0, Om, Or)
    DM = transverse_distance(z, H0=H0, Om=Om, Or=Or)
    DH_dir, FAP = [], []
    for n in nhats:
        Hpar = directional_hubble(Hz_iso, Sigma, n)             # km/s/Mpc
        DHn = U.C_LIGHT_KM_S / Hpar
        DH_dir.append(DHn); FAP.append(DM / DHn)
    DH_dir = np.array(DH_dir)
    aniso = float((DH_dir.max() - DH_dir.min()) / DH_dir.mean()) if DH_dir.size > 1 else 0.0
    return dict(nhats=nhats, DH_over_rs=DH_dir / r_s, F_AP=np.array(FAP),
                anisotropy=aniso, r_s=float(r_s), DM_over_rs=DM / r_s)


def alcock_paczynski_quadrupole(z, Sigma, r_s=None, H0=67.4, Om=0.315,
                                Or=9.24e-5, n_theta=16, n_phi=32):
    """AP 비 F_AP(n̂)=D_M/D_H(n̂) 의 사중극 진폭 (구면 분해 ℓ=2 파워).

    Σ→0 이면 등방 → C_2→0.  Σ≠0 이면 C_2 ∝ Σ (선두)."""
    th = np.linspace(0, np.pi, n_theta); ph = np.linspace(0, 2 * np.pi, n_phi, endpoint=False)
    T, P = np.meshgrid(th, ph, indexing="ij")
    nx = np.sin(T) * np.cos(P); ny = np.sin(T) * np.sin(P); nz = np.cos(T)
    Hz_iso = flrw_hubble(z, H0, Om, Or); DM = transverse_distance(z, H0=H0, Om=Om, Or=Or)
    Sig = np.asarray(Sigma, float)
    proj = (nx ** 2 * Sig[0, 0] + ny ** 2 * Sig[1, 1] + nz ** 2 * Sig[2, 2]
            + 2 * nx * ny * Sig[0, 1] + 2 * nx * nz * Sig[0, 2] + 2 * ny * nz * Sig[1, 2])
    Hpar = Hz_iso * (1.0 + proj)
    FAP = DM / (U.C_LIGHT_KM_S / Hpar)
    # ℓ=2 파워
    try:
        from scipy.special import sph_harm_y
        Y = lambda l, m: sph_harm_y(l, m, T, P)
    except ImportError:
        from scipy.special import sph_harm
        Y = lambda l, m: sph_harm(m, l, P, T)
    dOm = np.sin(T) * (th[1] - th[0]) * (ph[1] - ph[0])
    resid = FAP - np.sum(FAP * dOm) / np.sum(dOm)
    C2 = sum(abs(np.sum(resid * np.conj(Y(2, m)) * dOm)) ** 2 for m in range(-2, 3)) / 5.0
    return float(C2)
