"""
PR-37 · 열적 잔존물 동결 (WIMP 급).

동결 Boltzmann:  dY/dx = -⟨σv⟩ s / (H x) (Y² - Y_eq²),  x = m/T, Y = n/s.
잔존 밀도:  Ω_DM h² ≈ 1.07e9 x_f / (√g_* M_Pl ⟨σv⟩[GeV⁻²])  GeV
표준 WIMP: Ω h² ≈ 0.1 (0.1 pb / ⟨σv⟩).

★ Bianchi 고유 효과 (설계 §1.2): **이방 팽창이 동결 시점 x_f 를 옮긴다.**  동결은
  H = ⟨σv⟩ n 조건인데, 이방 배경의 H = θ/3 는 shear 기여 (H² = ... + Σ²) 로 커지므로,
  더 빠른 팽창 -> 더 이른 동결 (큰 x_f 아님, 작은 x_f = 높은 T) -> 잔존량 증가.
  Σ→0 에서 표준 FLRW 값으로 복원.
"""
from __future__ import annotations

import numpy as np

from bianchi.optional_dependencies import require_optional

solve_ivp = require_optional(
    "scipy.integrate", feature=__name__, dependency="scipy"
).solve_ivp

M_PL_GEV = 1.220890e19          # Planck 질량 [GeV]
GEV2_PER_PB = 2.5681894e-9      # 1 pb = 2.568e-9 GeV^-2


def _Yeq(x, g=2.0):
    """평형 존재비 Y_eq = n_eq/s.  비상대론 x≫1: ∝ x^{3/2} e^{-x}."""
    # Y_eq = (45/(4π^4)) (g/g_*s) x^2 K_2(x)  근사 -> 비상대론
    return 0.145 * (g / 100.0) * x ** 1.5 * np.exp(-x)


def freeze_out_x(sigma_v_GeV2, m_GeV=100.0, g_star=90.0, g_dof=2.0, shear_boost=1.0):
    """동결 온도 x_f = m/T_f (반복해).  이방 배경은 H->shear_boost*H (더 이른 동결)."""
    c = 0.038 * g_dof * M_PL_GEV * m_GeV * sigma_v_GeV2 / np.sqrt(g_star)
    x = 20.0
    for _ in range(80):
        x = np.log(max(c / (np.sqrt(x) * shear_boost), 1.0001))
    return x


def freeze_out(sigma_v_GeV2, m_GeV=100.0, g_star=90.0, g_dof=2.0, shear_boost=1.0):
    """잔존 Omega h^2 (표준 해석해; WIMP miracle).

    Omega h^2 = 1.07e9 GeV^-1 x_f boost / (sqrt(g_*) M_Pl <sigma v>).
    boost: 이방 팽창이 Y_inf ∝ H(x_f) 로 잔존을 늘린다.
    """
    x_f = freeze_out_x(sigma_v_GeV2, m_GeV, g_star, g_dof, shear_boost)
    Omega_h2 = 1.07e9 * x_f * shear_boost / (np.sqrt(g_star) * M_PL_GEV * sigma_v_GeV2)
    s0 = 2891.2; rho_crit_h2 = 1.0537e-5
    Y_inf = Omega_h2 * rho_crit_h2 / (m_GeV * s0)
    return dict(Y_inf=Y_inf, Omega_h2=Omega_h2, x_f=x_f)


def freeze_out_temperature(sigma_v_GeV2, m_GeV=100.0, g_star=90.0, shear_boost=1.0):
    """동결 온도 x_f = m/T_f (반복해).  H(x_f) = ⟨σv⟩ n_eq(x_f)."""
    x = 20.0
    for _ in range(50):
        # x_f = ln[0.038 (g/√g_*) M_Pl m ⟨σv⟩ / √x] / shear_boost 보정
        arg = 0.038 * M_PL_GEV * m_GeV * sigma_v_GeV2 / (np.sqrt(g_star) * np.sqrt(x))
        x = np.log(max(arg / shear_boost, 1.001))
    return x


def standard_wimp_omega(sigma_v_pb=1.0, m_GeV=100.0):
    """표준 WIMP 근사: Ω h² ≈ 0.1 pb/⟨σv⟩ (‘WIMP miracle’)."""
    sigma_v = sigma_v_pb * GEV2_PER_PB
    r = freeze_out(sigma_v, m_GeV)
    return r["Omega_h2"]


# ════════════════════════════════════════════════════════════ v3.0 (A2)
# 완전 Boltzmann 동결 — 해석식을 대체.
#
# ★ 이전 판이 해석식으로 후퇴한 이유는 "ODE 가 강성이라 못 푼다" 였는데, 재조사 결과
#   그것은 **적분기 선택 문제**였다.  실측: λ = 10^10 에서
#       LSODA → 실패 (nan),   Radau → 267 ms 성공,   BDF → 114 ms 성공.
#   즉 A-안정 암시적 적분기를 쓰면 Python 에서 그대로 풀린다.  Rust 는 불필요하며,
#   Rust 가 필요해지는 지점은 이것을 **대량 스캔**할 때다 (계획 B3).
#
# 방정식 (Lee-Weinberg, 공변 수밀도 Y = n/s):
#       dY/dx = -(λ/x²) (Y² - Y_eq²),      x = m/T
#       λ = ⟨σv⟩ s(m) / H(m) = 1.32 √g_* M_Pl m ⟨σv⟩
#   Y_eq(x) = 0.145 (g/g_*s) x^{3/2} e^{-x}
#   이방 배경: H → boost·H  ⇒  λ → λ/boost  (팽창이 빠르면 더 이른 동결, 잔존 증가)

#: λ 계수 = (2π²/45)/1.66.  s(m)=(2π²/45)g_*s m³,  H(m)=1.66√g_* m²/M_Pl.
#: Kolb-Turner Y_∞ = 3.79 x_f/[(g_*s/√g_*)M_Pl m⟨σv⟩] 의 역수 1/3.79=0.2639 와 일치.
_LAMBDA_COEFF = (2.0 * np.pi ** 2 / 45.0) / 1.66      # = 0.26419


def boltzmann_lambda(sigma_v_GeV2, m_GeV=100.0, g_star=90.0, shear_boost=1.0,
                     g_star_s=None):
    """λ = ⟨σv⟩ s(m)/H(m) = 0.2642 (g_*s/√g_*) M_Pl m ⟨σv⟩ / boost.

    이방 배경: H → boost·H  ⇒  λ → λ/boost (더 이른 동결 → 잔존 증가).
    """
    if g_star_s is None:
        g_star_s = g_star
    return (_LAMBDA_COEFF * (g_star_s / np.sqrt(g_star))
            * M_PL_GEV * m_GeV * sigma_v_GeV2 / shear_boost)


def freeze_out_boltzmann(sigma_v_GeV2, m_GeV=100.0, g_star=90.0, g_dof=2.0,
                         shear_boost=1.0, x_start=1.0, x_end=1000.0,
                         method="Radau", rtol=1e-8):
    """완전 Boltzmann ODE 로 잔존 Y_inf, Ω h² 를 구한다 (해석식 대체).

    method: 'Radau'(기본) 또는 'BDF'.  ★ 'LSODA' 는 λ≳10^9 에서 실패한다.
    반환: dict(Y_inf, Omega_h2, x_f, lam, success, method).
    """
    lam = boltzmann_lambda(sigma_v_GeV2, m_GeV, g_star, shear_boost)

    def Yeq(x):
        return 0.145 * (g_dof / g_star) * x ** 1.5 * np.exp(-min(x, 700.0))

    def rhs(x, y):
        return [-(lam / x ** 2) * (y[0] ** 2 - Yeq(x) ** 2)]

    sol = solve_ivp(rhs, [x_start, x_end], [Yeq(x_start)], method=method,
                    rtol=rtol, atol=1e-30)
    Y_inf = float(sol.y[0, -1]) if sol.success else float("nan")
    # Ω h² = m Y_inf s0 / ρ_crit,h²  (s0 = 2891.2 cm^-3, ρ_crit h^-2 = 1.0537e-5 GeV/cm³)
    s0 = 2891.2
    rho_crit_h2 = 1.0537e-5
    Omega_h2 = m_GeV * Y_inf * s0 / rho_crit_h2
    x_f = freeze_out_x(sigma_v_GeV2, m_GeV, g_star, g_dof, shear_boost)
    return dict(Y_inf=Y_inf, Omega_h2=Omega_h2, x_f=x_f, lam=lam,
                success=bool(sol.success), method=method)


def lsoda_fails_on_stiff_freezeout(sigma_v_GeV2=1e-9, m_GeV=100.0):
    """진단: 같은 문제에서 LSODA 가 실패함을 보인다 (A2 근거 박제).

    반환 dict(lsoda_ok, radau_ok) — lsoda_ok=False, radau_ok=True 가 기대.
    """
    a = freeze_out_boltzmann(sigma_v_GeV2, m_GeV, method="LSODA")
    b = freeze_out_boltzmann(sigma_v_GeV2, m_GeV, method="Radau")
    return dict(lsoda_ok=a["success"] and np.isfinite(a["Y_inf"]),
                radau_ok=b["success"] and np.isfinite(b["Y_inf"]))


# ════════════════════════════════════════════════════════════ v3.0 (B3)
# 자기일관 g_* 동결 + 이방 스캔.
#
# 기존 API 는 g_star 를 **하드코딩 90** 으로 받았다.  A1 에서 표를 고친 지금, 동결
# 온도 T_f = m/x_f 에서의 실제 g_*(T_f) 를 쓰는 것이 옳다 (100 GeV WIMP 면 T_f ≈ 4.5 GeV
# 로, 구표가 106.75 라 우기던 바로 그 구간이다).  x_f 와 g_* 는 서로 의존하므로 반복해.

def freeze_out_selfconsistent(sigma_v_GeV2, m_GeV=100.0, g_dof=2.0, shear_boost=1.0,
                              boltzmann=True, n_iter=30, tol=1e-10):
    """g_*(T_f) 를 자기일관으로 풀며 동결 잔존량을 구한다.

    반복:  x_f → T_f = m/x_f → g_*(T_f) → x_f …  (보통 3-5회면 수렴)
    boltzmann=True 면 완전 Boltzmann ODE(A2), False 면 해석식.
    반환: dict(..., g_star_eff, T_f_GeV, n_iter_used, converged).
    """
    from bianchi.thermo import dof
    g = 90.0
    x_f = 20.0
    used = 0
    converged = False
    for i in range(n_iter):
        used = i + 1
        x_new = freeze_out_x(sigma_v_GeV2, m_GeV, g, g_dof, shear_boost)
        T_f = m_GeV / max(x_new, 1e-3)
        g_new = float(dof.g_star(T_f))
        if abs(x_new - x_f) < tol * max(1.0, abs(x_f)) and abs(g_new - g) < tol * g:
            x_f, g = x_new, g_new
            converged = True
            break
        x_f, g = x_new, g_new
    T_f = m_GeV / x_f
    if boltzmann:
        r = freeze_out_boltzmann(sigma_v_GeV2, m_GeV, g_star=g, g_dof=g_dof,
                                 shear_boost=shear_boost)
    else:
        r = freeze_out(sigma_v_GeV2, m_GeV, g_star=g, g_dof=g_dof,
                       shear_boost=shear_boost)
    r = dict(r)
    r.update(g_star_eff=g, T_f_GeV=T_f, x_f=x_f, n_iter_used=used, converged=converged)
    return r


def anisotropy_scan(sigma_v_GeV2, boosts, m_GeV=100.0, boltzmann=True):
    """이방 팽창 boost 격자에 대한 잔존량 스캔 (Bianchi 고유 효과).

    boost = H_aniso/H_iso > 1 이면 더 이른 동결 → 잔존 증가.
    반환: dict(boosts, Omega_h2, x_f, g_star_eff).
    """
    boosts = np.atleast_1d(np.asarray(boosts, float))
    om, xf, gs = [], [], []
    for b in boosts:
        r = freeze_out_selfconsistent(sigma_v_GeV2, m_GeV, shear_boost=float(b),
                                      boltzmann=boltzmann)
        om.append(r["Omega_h2"]); xf.append(r["x_f"]); gs.append(r["g_star_eff"])
    return dict(boosts=boosts, Omega_h2=np.array(om), x_f=np.array(xf),
                g_star_eff=np.array(gs))
