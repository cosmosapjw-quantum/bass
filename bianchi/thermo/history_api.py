"""
B2b 접합면 · **이온화 이력 주입 인터페이스** (75차) — PLAN-NEXT-v5 §8 이행.

설계 원칙 (계획 §8 그대로): 소비자 쪽을 **이력 주입형**으로 만든다 —
내장 Peebles 와 외부 모듈 (RECFAST/HyRec/CosmoRec 급 + 재이온화) 을 **같은
프로토콜**로 받아, 충돌항 ν(z) 경로가 그것을 읽는다.  게이트는 계획이 명시한
"주입 이력 = 내장 Peebles 일 때 기존 결과 **비트-재현**".

프로토콜 (외부 모듈이 만족해야 할 최소 계약 — docs/B2B-INTEGRATION-SPEC.md):
    name        : str                       — 식별자 (기록용)
    z_range     : (z_min, z_max)            — 유효범위 (밖은 호출 금지)
    x_e(z)      : array→array               — 자유전자분율 n_e/n_H (He 포함 시 >1 가능)
    T_matter(z) : array→array (선택)        — 물질온도 [K] (없으면 None)
    metadata    : dict (선택)               — 오차추정·참조케이스·He 규약 등

단위·규약 (계획 §8 ①): z 는 무차원 적색이동, x_e = n_e/n_H (수소 기준),
n_H = 8.50e−6·Ω_b h² (1+z)³ cm⁻³ (Y_p=0.24), σ_T = 6.6524587e−25 cm².
이방성 결합 (계획 §8 ④): **등방 이력 + 이방 기하** — 이력은 z 만의 함수로
받고, 이방성은 기하 (H_of_z, 방향 스케일인자) 쪽에서만 들어온다.  방향의존
재이온화가 필요해지면 `x_e(z, nhat)` 확장 훅을 열되 **명시 버전 표기**할 것.

충돌률: 계층/격자 사다리는 τ-시간을 쓰므로
    ν_τ(z) = σ_T n_e c / H(z)          (무차원 — G2 사다리의 ν)
    ν_t(z) = σ_T n_e c                 (1/s — 물리시간)
"""
from __future__ import annotations

from typing import Protocol, runtime_checkable

import numpy as np

from bianchi.physical import units as U
from bianchi.thermo import recombination as REC

SIGMA_T_CM2 = 6.6524587e-25
C_CM_S = 2.99792458e10


@runtime_checkable
class IonizationHistory(Protocol):
    """외부 재결합/재이온화 모듈이 만족해야 할 최소 계약."""

    name: str
    z_range: tuple

    def x_e(self, z):                                  # pragma: no cover - 프로토콜
        ...


class TabulatedHistory:
    """격자 (z, x_e[, T_m]) 로 주는 이력 — 외부 모듈의 표준 수입 형태.

    보간: ln(1+z) 선형 (재결합 급강하에서 안정).  범위 밖은 명시 예외."""

    def __init__(self, z, xe, T_m=None, name="tabulated", metadata=None):
        z = np.asarray(z, float)
        order = np.argsort(z)
        self._z = z[order]
        self._xe = np.asarray(xe, float)[order]
        self._Tm = None if T_m is None else np.asarray(T_m, float)[order]
        if self._z.size < 2:
            raise ValueError("이력 격자는 2점 이상")
        if not np.isfinite(self._xe).all():
            raise ValueError("x_e 에 비유한값")
        self.name = name
        self.z_range = (float(self._z[0]), float(self._z[-1]))
        self.metadata = dict(metadata or {})

    def _interp(self, z, vals):
        z = np.atleast_1d(np.asarray(z, float))
        lo, hi = self.z_range
        if z.min() < lo - 1e-9 or z.max() > hi + 1e-9:
            raise ValueError(f"z 범위 밖 요청: {z.min()}..{z.max()} ∉ [{lo},{hi}]")
        out = np.interp(np.log1p(z), np.log1p(self._z), vals)
        return out if out.size > 1 else float(out[0])

    def x_e(self, z):
        return self._interp(z, self._xe)

    def T_matter(self, z):
        if self._Tm is None:
            return None
        return self._interp(z, self._Tm)


class SahaHistory(TabulatedHistory):
    """내장 Saha (닫힌형·빠름) 참조 이력 — 주입 경로의 **상시 게이트용**.
    물리적으로는 평형 근사 (z≳1300) 이며, 정밀 이력은 외부 모듈 몫."""

    def __init__(self, z_grid=None, Omega_b_h2=0.0224, T0_K=U.T_CMB_K):
        if z_grid is None:
            z_grid = np.linspace(3000.0, 500.0, 401)
        xe = np.atleast_1d(np.asarray(
            REC.saha_xe(z_grid, Omega_b_h2=Omega_b_h2, T0_K=T0_K), float))
        super().__init__(z_grid, xe, name="builtin-saha",
                         metadata=dict(Omega_b_h2=Omega_b_h2,
                                       source="bianchi.thermo.recombination.saha_xe",
                                       caveat="평형 근사 — 정밀 이력은 외부 모듈"))


class BuiltinPeeblesHistory(TabulatedHistory):
    """내장 Peebles 를 **같은 프로토콜로** 감싼 참조 이력.

    ★ 비용 경고 (75차 실측): peebles_xe 는 강성 ODE 라 격자 100점에 분 단위 —
    상시 시험은 `SahaHistory` 로 하고, 이 클래스는 **명시 호출**에서만 쓴다."""

    def __init__(self, z_grid=None, Omega_b_h2=0.0224, Omega_m_h2=0.143,
                 h=0.674, T0_K=U.T_CMB_K, H_of_z=None):
        if z_grid is None:
            z_grid = np.linspace(3000.0, 200.0, 601)
        xe = np.asarray(REC.peebles_xe(z_grid, Omega_b_h2=Omega_b_h2,
                                       Omega_m_h2=Omega_m_h2, h=h,
                                       T0_K=T0_K, H_of_z=H_of_z), float)
        super().__init__(z_grid, xe, name="builtin-peebles",
                         metadata=dict(Omega_b_h2=Omega_b_h2, h=h,
                                       source="bianchi.thermo.recombination"))


def validate_history(hist, strict=True):
    """계약 검사 — 외부 모듈이 들어오면 **가장 먼저** 이걸 통과해야 한다.

    반환 dict(ok, checks{...}).  strict 면 실패 시 예외."""
    checks = {}
    zlo, zhi = hist.z_range
    zs = np.linspace(zlo, zhi, 64)
    xe = np.atleast_1d(np.asarray(hist.x_e(zs), float))
    checks["finite"] = bool(np.isfinite(xe).all())
    checks["nonneg"] = bool((xe >= -1e-12).all())
    checks["bounded"] = bool((xe <= 1.3).all())         # He 완전이온화 여유
    checks["high_z_ionized"] = bool(xe[np.argmax(zs)] > 0.9) if zhi > 1500 else True
    # 재결합 급강하: 최고 z → 최저 z 로 가면서 크게 감소
    checks["recombines"] = bool(xe[np.argmin(zs)] < 0.5 * xe[np.argmax(zs)]) \
        if zhi > 1500 and zlo < 800 else True
    checks["range_sane"] = bool(zhi > zlo >= 0.0)
    try:
        hist.x_e(zhi * 1.5 + 10.0)
        checks["range_guard"] = False                   # 범위 밖인데 통과 = 결함
    except Exception:
        checks["range_guard"] = True
    ok = all(checks.values())
    if strict and not ok:
        bad = [k for k, v in checks.items() if not v]
        raise ValueError(f"이력 계약 위반: {bad}")
    return dict(ok=ok, checks=checks)


def n_H_cm3(z, Omega_b_h2=0.0224):
    """수소 수밀도 [cm⁻³] — recombination 모듈과 **같은 상수** (단일 진실원)."""
    return REC._NB0_PER_OBH2 * Omega_b_h2 * (1.0 + np.asarray(z, float)) ** 3


def thomson_rate(hist, z, Omega_b_h2=0.0224, H_of_z=None, h=0.674,
                 Omega_m_h2=0.143, tau_units=True):
    """ν = σ_T n_e c [/ H]  — G2 사다리가 읽는 충돌률.

    tau_units=True 면 τ-시간 무차원 ν_τ = ν_t/H (사다리 규약)."""
    z = np.atleast_1d(np.asarray(z, float))
    xe = np.atleast_1d(np.asarray(hist.x_e(z), float))
    nu_t = SIGMA_T_CM2 * xe * n_H_cm3(z, Omega_b_h2) * C_CM_S     # 1/s
    if not tau_units:
        return nu_t if nu_t.size > 1 else float(nu_t[0])
    if H_of_z is None:
        Om = Omega_m_h2 / h**2
        Or = REC._OMEGA_R_H2 / h**2
        OL = 1.0 - Om - Or
        Hz = (100.0 * h / U.MPC_KM) * np.sqrt(Or*(1+z)**4 + Om*(1+z)**3 + OL)
    else:
        Hz = np.atleast_1d(np.asarray(H_of_z(z), float))
    out = nu_t / Hz
    return out if out.size > 1 else float(out[0])


def optical_depth(hist, z_grid, **kw):
    """주입 이력으로 τ(z)·g(z)·z_* — 기존 함수를 **그대로** 재사용
    (계획 §8 게이트: 주입 = 내장일 때 비트-재현)."""
    xe = np.atleast_1d(np.asarray(hist.x_e(z_grid), float))
    return REC.optical_depth_and_visibility(np.asarray(z_grid, float), xe, **kw)
