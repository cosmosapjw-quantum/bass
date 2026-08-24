"""
I2 · **Mixmaster 물질 보정 측정** (70차) — 'BKL 무시' 정량 게이트.

  · 진공 극한: 결합기계 안 F2 Taub-II 제1적분 |ΔL| ≤ 1e−9 (실측 2.4e−11).
  · ★ 선형 응답: p∈[0.9,1.1], C 기록 (실측 p=0.99, C≈11.8).
  · ★ 에너지 항등 (rhs-기반): dlnΩ = (2q−2) − Σ:Π/(3Ω) ≤1e−12 (실측 1.3e−15)
    + 일-항 O(1) 실증 (|W|>0.5).
  · BKL 감쇠: Ω(τ=−5) < Ω(0).
  · ★★ 절단-민감 **발견 박제**: |J₂|/J₀ 가 l_max 5 에서 3 대비 ≥3× — 자유흐름
    다극의 벽-영역 성장 (정칙화 = 충돌 G1/B2b 몫; π/ρ>1 = f≥0 위배 신호).
"""
import numpy as np
import pytest

pytest.importorskip("bianchi_rustcore")

from audit.i2_mixmaster_matter import (L_drift, energy_identity_residual,
                                       linear_response, truncation_sensitivity,
                                       type_ii_collapse)


def test_vacuum_limit_preserves_taub_first_integral():
    """★ 진공 극한 — F2 회귀 (결합기계 관통)."""
    tr = type_ii_collapse(1e-12, ns=2000)
    assert np.isfinite(tr).all()
    assert L_drift(tr) <= 1e-9


def test_matter_linear_response():
    """★★ ΔL = C·Ω₀^p — p≈1 (벽당 보정이 Ω 에 1차)."""
    p, C, d = linear_response()
    assert 0.9 <= p <= 1.1, (p, C)
    assert 5.0 <= C <= 20.0, C                         # 창·IC 고정의 실측 대역
    assert d[0] > 1e-3                                 # 감도 확보 (비자명)


def test_energy_identity_and_o1_work():
    """★ dlnΩ = (2q−2) − Σ:Π/(3Ω) 기계 관통 + 벽 일-항 O(1)."""
    resid, wmax = energy_identity_residual(ns=2000, stride=250)
    assert resid <= 1e-12, resid
    assert wmax > 0.5                                  # 이방압력 일 실증


def test_bkl_omega_decay_towards_singularity():
    """★ Ω 감쇠 (BKL 방향) — 벽 통과 포함 창."""
    tr = type_ii_collapse(1e-2, ns=2000)
    lnH0, lnHT = tr[0, 8], tr[-1, 8]
    Om0 = tr[0, 9] / (3.0*np.exp(2*lnH0))
    OmT = tr[-1, 9] / (3.0*np.exp(2*lnHT))
    assert OmT < Om0
    assert tr[-1, 0] < 0.0                             # 벽 반사 (Σ₊ 부호 전환)


def test_truncation_sensitivity_finding_pinned():
    """★★ 발견 박제: l_max=5 의 |J₂|/J₀ 성장 ≥ 3× (l_max=3 대비) —
    자유흐름 근사의 벽-영역 유효범위 한계 (통과가 아니라 **기록**)."""
    s = truncation_sensitivity(ns=2000)
    assert s[3] < 2.0                                  # 저절단은 유계
    assert s[5] / s[3] >= 3.0, s                       # 민감 성장 실재
