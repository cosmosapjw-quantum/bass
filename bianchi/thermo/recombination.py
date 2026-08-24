"""
PR-36 · 재결합·탈결합.  Saha (평형) + Peebles (비평형 ODE).

수소 재결합의 자유전자분율 x_e(z).  Saha 는 평형 근사(고온), Peebles 는 3-준위 +
fudge 로 비평형 꼬리(잔존 x_e)를 잡는다 (RECFAST 수준).

★ 이방성 결합 (설계 D7): 재결합은 국소 스칼라 과정이라 이방성은 팽창률을 통해서만
  들어간다:  H -> θ/3 (평균 팽창).  방향 의존은 없다 (온도가 평균 ℓ 만 따르므로).
  따라서 Bianchi 배경에서도 x_e(z) 공식은 그대로, H(z) 만 이방 배경의 것으로 바꾼다.

기준 (설계 오라클):  z_* ≈ 1090, z_drag ≈ 1060, 잔존 x_e ≈ 2e-4.
"""
from __future__ import annotations

import numpy as np

from bianchi.physical import units as U
from bianchi.optional_dependencies import require_optional

solve_ivp = require_optional(
    "scipy.integrate", feature=__name__, dependency="scipy"
).solve_ivp
brentq = require_optional(
    "scipy.optimize", feature=__name__, dependency="scipy"
).brentq

# 상수 (CGS/자연 혼합, eV 단위 에너지)
_EION_H = 13.605693              # 수소 이온화에너지 [eV]
_ME_EV = 510998.95              # 전자 질량 [eV]
_ALPHA = 7.2973525693e-3
# 오늘 바리온 수밀도 계수:  n_b(z) = n_b0 (1+z)^3,  n_b0 ≈ 2.503e-7 Ω_b h^2 cm^-3
_NB0_PER_OBH2 = 8.50e-6         # n_H0 per Omega_b h^2 [cm^-3] (수소; Y_p=0.24)
#: 복사 밀도 Ω_r h² = 광자(2.47e-5) + 무질량 중성미자(1.71e-5, N_eff=3.044)
_OMEGA_R_H2 = 4.18e-5


def _saha_xe(T_eV, n_b):
    """Saha 방정식으로 x_e (수소만).  x_e^2/(1-x_e) = S/n_b,
       S = (m_e T/2π)^{3/2} exp(-E_ion/T)  (자연단위 근사)."""
    # S in cm^-3:  ((m_e k T)/(2π ħ^2))^{3/2} e^{-E/kT}
    # 수치 상수로 압축: S = 2.415e15 * T_K^{3/2} e^{-E/kT}  (cm^-3, T in K)
    T_K = T_eV / U.KB_EV_K
    S = 2.4147e15 * T_K ** 1.5 * np.exp(-_EION_H / T_eV)
    r = S / n_b
    # x_e^2/(1-x_e) = r  ->  x_e = (-r + sqrt(r^2+4r))/2
    return (-r + np.sqrt(r ** 2 + 4 * r)) / 2.0


def saha_xe(z, Omega_b_h2=0.0224, T0_K=U.T_CMB_K):
    """Saha x_e(z)  (평형 근사; z >~ 1300 에서 유효)."""
    z = np.atleast_1d(np.asarray(z, float))
    T_eV = U.KB_EV_K * T0_K * (1 + z)
    n_b = _NB0_PER_OBH2 * Omega_b_h2 * (1 + z) ** 3
    xe = np.array([_saha_xe(t, n) for t, n in zip(T_eV, n_b)])
    return xe if xe.size > 1 else float(xe[0])


def peebles_xe(z_grid, Omega_b_h2=0.0224, Omega_m_h2=0.143, h=0.674,
               T0_K=U.T_CMB_K, H_of_z=None):
    """Peebles 3-준위 ODE 로 x_e(z).  비평형 잔존 전자 포함 (RECFAST 급).

    표준형 (Dodelson 3.44; CGS):
        dx_e/dt = -C [ α_B n_H x_e^2 - β_e (1-x_e) ]
        β_e = α_B (m_e k T/2πħ²)^{3/2} e^{-B1/kT}              (광이온화)
        C   = (Λ_2γ + Λ_α) / (Λ_2γ + Λ_α + β)                 (Peebles 인자)
        Λ_α = 8π H / (λ_α^3 n_1s) ,  n_1s = (1-x_e) n_H
        β   = β_e e^{+(B1-B2)/kT}  (C 분모용, 2s 준위)
    H_of_z: 이방 배경 H(z) [s^-1] 콜백 (없으면 평탄 ΛCDM).
    """
    z_grid = np.asarray(z_grid, float)
    F = 1.14                                    # RECFAST fudge
    B1, B2 = _EION_H, _EION_H / 4.0             # n=1, n=2 결합에너지 [eV]
    Lam2g = 8.2245809                           # 2s-1s two-photon [s^-1]
    lam_alpha = 1.21567e-5                       # Lyα 파장 [cm]

    def H(z):
        """★ v3.0 (B2): **복사항 누락 버그 수정**.  이전 판은 Ω_m(1+z)³+Ω_Λ 만 썼는데,
        재결합기(z~1100)에서 복사는 물질의 32% 라 H 가 13% 과소평가되었다.
        dt/dz = -1/[H(1+z)] 이므로 H 과소 → dz 당 시간 과대 → 재결합 과속 → x_e 과소."""
        if H_of_z is not None:
            return H_of_z(z)
        Om = Omega_m_h2 / h ** 2
        Or = _OMEGA_R_H2 / h ** 2               # 광자 + 무질량 중성미자
        OL = 1 - Om - Or
        H0_s = 100 * h / U.MPC_KM               # s^-1
        return H0_s * np.sqrt(Or * (1 + z) ** 4 + Om * (1 + z) ** 3 + OL)

    def alpha_B(T_K):
        """Case-B 재결합 [cm^3/s] (Pequignot 1991 fit)."""
        t = T_K / 1e4
        return F * 4.309e-13 * t ** (-0.6166) / (1 + 0.6703 * t ** 0.5300)

    def rhs(z, y):
        xe = min(max(y[0], 1e-13), 1.0)
        T_K = T0_K * (1 + z); T_eV = U.KB_EV_K * T_K
        n_b = _NB0_PER_OBH2 * Omega_b_h2 * (1 + z) ** 3   # cm^-3 (n_H)
        aB = alpha_B(T_K)                                 # cm^3/s
        pref = 2.4147e15 * T_K ** 1.5                      # (m_e kT/2πħ²)^{3/2} cm^-3
        beta_e = aB * pref * np.exp(-B1 / T_eV)            # 광이온화 [1/s]
        beta = aB * pref * np.exp(-B2 / T_eV)              # C 분모용 (2s)
        n_1s = (1 - xe) * n_b
        Lam_a = 8 * np.pi * H(z) / (lam_alpha ** 3 * max(n_1s, 1e-30))   # [1/s]
        C = (Lam2g + Lam_a) / (Lam2g + Lam_a + beta)
        dxe_dt = -C * (aB * n_b * xe ** 2 - beta_e * (1 - xe))
        return [dxe_dt * (-1.0 / (H(z) * (1 + z)))]        # dt/dz = -1/[H(1+z)]

    z0 = z_grid[0]
    xe0 = float(saha_xe(z0, Omega_b_h2, T0_K))
    sol = solve_ivp(rhs, [z0, z_grid[-1]], [xe0], t_eval=z_grid,
                    method="LSODA", rtol=1e-7, atol=1e-12)
    return np.clip(sol.y[0], 0, 1.2)


def recombination_redshift(Omega_b_h2=0.0224, T0_K=U.T_CMB_K):
    """Saha 반이온화 z (x_e=0.5).  **평형 Saha 는 ≈1370** (관측 z_* 아님!).

    관측되는 최종산란 z_*≈1090 은 비평형(Peebles)로 지연되어 **가시함수 최대점**
    (optical_depth_and_visibility 의 z_star) 으로 정의된다.  이 함수는 순수 Saha 값."""
    f = lambda z: saha_xe(z, Omega_b_h2, T0_K) - 0.5
    return brentq(f, 800, 1600)


def drag_redshift(Omega_b_h2=0.0224):
    """z_drag (바리온 drag) 근사식 (Eisenstein-Hu 1998)."""
    b1 = 0.313 * (Omega_b_h2 / 0.0224 * 0.143) ** -0.419 * (1 + 0.607 * 0.143 ** 0.674)
    b2 = 0.238 * 0.143 ** 0.223
    Om_h2 = 0.143
    return 1291 * Om_h2 ** 0.251 / (1 + 0.659 * Om_h2 ** 0.828) * (1 + b1 * Omega_b_h2 ** b2)


def optical_depth_and_visibility(z_grid, xe, Omega_b_h2=0.0224, h=0.674,
                                 Omega_m_h2=0.143, T0_K=U.T_CMB_K, H_of_z=None):
    """Thomson 광학깊이 τ(z) 와 가시함수 g(z) = -dτ/dz e^{-τ}.

    dτ/dz = σ_T n_e c / [H(1+z)] ,  n_e = x_e n_H.  z_* = g(z) 최대점.
    반환: dict(tau, g, z_star).
    """
    z_grid = np.asarray(z_grid, float); xe = np.asarray(xe, float)
    sigma_T = 6.6524587e-25          # cm^2
    c_cm = 2.99792458e10             # cm/s

    def H(z):
        """복사항 포함 (v3.0 B2 — peebles_xe 와 동일한 수정)."""
        if H_of_z is not None:
            return H_of_z(z)
        Om = Omega_m_h2 / h ** 2
        Or = _OMEGA_R_H2 / h ** 2
        OL = 1 - Om - Or
        return (100 * h / U.MPC_KM) * np.sqrt(Or * (1 + z) ** 4 + Om * (1 + z) ** 3 + OL)

    n_H = _NB0_PER_OBH2 * Omega_b_h2 * (1 + z_grid) ** 3
    n_e = xe * n_H
    dtau_dz = sigma_T * n_e * c_cm / (H(z_grid) * (1 + z_grid))
    # τ(z) = ∫_0^z dτ/dz' dz'  (z_grid 오름차순 가정 -> 필요시 정렬)
    order = np.argsort(z_grid)
    zs = z_grid[order]; dt = dtau_dz[order]
    tau = np.concatenate([[0.0], np.cumsum(0.5 * (dt[1:] + dt[:-1]) * np.diff(zs))])
    g = dt * np.exp(-tau)
    z_star = zs[np.argmax(g)]
    return dict(z=zs, tau=tau, g=g, z_star=float(z_star), dtau_dz=dt)


# ════════════════════════════════════════════════════════════ v3.0 (B2a)
# 헬륨 재결합 — 이전 판에는 **헬륨이 통째로 없었다** (수소만).
#
# 바리온의 24%(질량)가 헬륨이고, 완전 이온화 시 헬륨 원자당 전자 2개를 낸다.
# n_e/n_H = x_H + f_He (x_HeII + 2 x_HeIII),   f_He = n_He/n_H = Y_p/(4(1-Y_p))
#
# 헬륨 재결합은 수소보다 훨씬 평형에 가까우므로 **Saha 로 충분**하다.
#   HeIII → HeII : χ = 54.4178 eV  (z ~ 6000)
#   HeII  → HeI  : χ = 24.5874 eV  (z ~ 2500),  통계무게비 4
#
# ★ 정직한 범위: 헬륨은 z ≳ 2000 에서만 작용하므로 z_*·z_drag·r_s 같은 배경 관측량은
#   거의 바뀌지 않는다.  완전성을 위한 추가다.

_EION_HE1 = 24.5874             # He I 이온화에너지 [eV]  (HeI -> HeII)
_EION_HE2 = 54.4178             # He II 이온화에너지 [eV] (HeII -> HeIII)
_G_HE1 = 4.0                    # HeI->HeII 통계무게비
_G_HE2 = 1.0                    # HeII->HeIII


def helium_fraction(Y_p=0.245):
    """f_He = n_He/n_H = Y_p / (4(1-Y_p)).  Y_p=0.245 → 0.0811."""
    return Y_p / (4.0 * (1.0 - Y_p))


def _saha_prefactor(T_K):
    """(m_e k T / 2πħ²)^{3/2}  [cm^-3]."""
    return 2.4147e15 * T_K ** 1.5


def saha_all_species(z, Omega_b_h2=0.0224, T0_K=U.T_CMB_K, Y_p=0.245):
    """수소+헬륨 동시 Saha 평형.  반환 dict(x_H, x_HeII, x_HeIII, x_e).

    x_e ≡ n_e/n_H (수소 기준 정규화; 완전이온화 시 1 + 2 f_He).
    n_e 에 대해 자기일관으로 풀어야 하므로 log n_e 에서 이분법.
    """
    T_K = T0_K * (1.0 + z)
    T_eV = U.KB_EV_K * T_K
    n_H = _NB0_PER_OBH2 * Omega_b_h2 * (1.0 + z) ** 3
    f_He = helium_fraction(Y_p)
    pref = _saha_prefactor(T_K)
    S_H = pref * np.exp(-min(_EION_H / T_eV, 700.0))
    S_He1 = _G_HE1 * pref * np.exp(-min(_EION_HE1 / T_eV, 700.0))
    S_He2 = _G_HE2 * pref * np.exp(-min(_EION_HE2 / T_eV, 700.0))

    def xe_of(ne):
        r = S_H / ne
        x_H = r / (1.0 + r)
        a = S_He1 / ne
        b = S_He2 / ne
        denom = 1.0 + a + a * b
        x_HeII = a / denom
        x_HeIII = a * b / denom
        return x_H + f_He * (x_HeII + 2.0 * x_HeIII), x_H, x_HeII, x_HeIII

    lo, hi = np.log(1e-30 * n_H), np.log((1.0 + 2.0 * f_He) * n_H)
    f = lambda ln_ne: xe_of(np.exp(ln_ne))[0] * n_H - np.exp(ln_ne)
    if f(lo) * f(hi) > 0:
        ne = np.exp(hi)
    else:
        ne = np.exp(brentq(f, lo, hi, xtol=1e-14, rtol=1e-14))
    x_e, x_H, x_HeII, x_HeIII = xe_of(ne)
    return dict(x_H=x_H, x_HeII=x_HeII, x_HeIII=x_HeIII, x_e=x_e, n_H=n_H)


def helium_ionization(z, Omega_b_h2=0.0224, T0_K=U.T_CMB_K, Y_p=0.245):
    """헬륨 이온화 분율 (x_HeII, x_HeIII) 만 (Saha)."""
    z = np.atleast_1d(np.asarray(z, float))
    out2 = np.empty(z.size); out3 = np.empty(z.size)
    for i, zi in enumerate(z):
        r = saha_all_species(zi, Omega_b_h2, T0_K, Y_p)
        out2[i], out3[i] = r["x_HeII"], r["x_HeIII"]
    return (out2, out3) if z.size > 1 else (float(out2[0]), float(out3[0]))


def xe_with_helium(z_grid, Omega_b_h2=0.0224, Omega_m_h2=0.143, h=0.674,
                   T0_K=U.T_CMB_K, Y_p=0.245, H_of_z=None):
    """전체 자유전자 분율 x_e = x_H(Peebles) + f_He (x_HeII + 2 x_HeIII)(Saha)."""
    z_grid = np.asarray(z_grid, float)
    x_H = peebles_xe(z_grid, Omega_b_h2, Omega_m_h2, h, T0_K, H_of_z)
    f_He = helium_fraction(Y_p)
    x2, x3 = helium_ionization(z_grid, Omega_b_h2, T0_K, Y_p)
    x2 = np.atleast_1d(x2); x3 = np.atleast_1d(x3)
    return x_H + f_He * (x2 + 2.0 * x3)


def peebles_rate_regime(z, xe, Omega_b_h2=0.0224, Omega_m_h2=0.143, h=0.674,
                        T0_K=U.T_CMB_K, fudge=1.14):
    """진단 (v3.0 B2): Peebles 억제항의 크기 분해 — 어떤 물리가 재결합률을 지배하는가.

    반환 dict(Lam_2gamma, Lam_alpha, beta, beta_over_Lam, C, saturated).

    ★ **구조적 발견 (v3.0)**:  C = Λ/(Λ+β),  β ∝ α_B  이므로 β ≫ Λ 인 영역에서
      C·α_B ≈ Λ·α_B/β 는 **α_B 와 무관**해진다.  즉 재결합률이 재결합계수가 아니라
      **탈출률 (Λ_2γ + Λ_α)** 로 제어된다.  실측 β/Λ:
          z=1400 → 635,   z=1200 → 157,   z=1100 → 51,   z=900 → 2.3
      따라서 (i) RECFAST fudge F(α_B 배율)는 급강하 구간에서 **효과가 없고**
      (F=0.7~1.3 스캔에서 z_* 불변으로 확인), (ii) x_e 정확도는 Λ_2γ(잘 측정된 원자상수)
      와 **Λ_α (Lyα 탈출)** 이 결정한다.
      → **B2b 다준위 작업의 표적은 α_B 정밀화가 아니라 Lyα 복사전달**이다
        (HyRec/CosmoRec 의 주요 개선이 정확히 이 부분: 2광자 보정·되먹임·확산).
    """
    z = float(z); xe = float(xe)
    T_K = T0_K * (1.0 + z)
    T_eV = U.KB_EV_K * T_K
    n_H = _NB0_PER_OBH2 * Omega_b_h2 * (1.0 + z) ** 3
    t = T_K / 1e4
    aB = fudge * 4.309e-13 * t ** (-0.6166) / (1 + 0.6703 * t ** 0.5300)
    pref = 2.4147e15 * T_K ** 1.5
    beta = aB * pref * np.exp(-min((_EION_H / 4.0) / T_eV, 700.0))
    Om = Omega_m_h2 / h ** 2
    Or = _OMEGA_R_H2 / h ** 2
    H = (100 * h / U.MPC_KM) * np.sqrt(Or * (1 + z) ** 4 + Om * (1 + z) ** 3
                                       + (1 - Om - Or))
    n_1s = max((1.0 - xe) * n_H, 1e-30)
    Lam_a = 8 * np.pi * H / (1.21567e-5 ** 3 * n_1s)
    Lam2g = 8.2245809
    L = Lam2g + Lam_a
    return dict(Lam_2gamma=Lam2g, Lam_alpha=Lam_a, beta=beta,
                beta_over_Lam=beta / L, C=L / (L + beta),
                saturated=bool(beta / L > 10.0))
