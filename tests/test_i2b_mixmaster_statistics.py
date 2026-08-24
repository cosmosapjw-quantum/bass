"""
I2b · **IX 다중튐 × 물질: 절단 계층 vs 정확 격자의 결정실험** (74차).

  · 진공 극한 u-수열 ≡ BKL 사상 (≤1e−3) — 결합기계 안 D1/R4 회귀.
  · 수동 추적자: dlnΩ/dτ 가 Ω₀ 무관 (1e−10 vs 1e−6, 차 ≤5e−3).
  · ★★ 결정실험: 정확 격자 **+0.234** vs 절단 계층 **−0.258** (부호 반전),
    완전유체 +1.906.  ⇒ BKL 무시는 **성립하되 8배 느린 감쇠**; PSTF 절단은
    이 영역에서 **정성적 오답** (l_max=4 는 Ω<0 양수성 붕괴).
  · 반증 박제: 절단 계층 BGK-감쇠 (l≥2) 로 유체극한 흉내내기 → 발산.
"""
import numpy as np
import pytest

pytest.importorskip("bianchi_rustcore")

from audit.i2b_mixmaster_statistics import (collapse, grid_exponent,  # noqa: E402
                                            omega_exponent,
                                            perfect_fluid_exponent,
                                            u_sequence_coupled)
from bianchi.analysis import kasner as K  # noqa: E402


@pytest.fixture(scope="module")
def traj():
    return collapse(u0=3.7, Om0=1e-12, l_max=3)


def test_vacuum_limit_reproduces_bkl_map(traj):
    """★ 진공 극한: 결합기계의 에폭 u-수열이 BKL 사상을 따른다."""
    us = u_sequence_coupled(traj)
    assert len(us) >= 2
    for a, b in zip(us[1:], us[:-1]):
        assert abs(a - K.bkl_map(b)) <= 1e-3, (us,)


def test_matter_is_passive_tracer(traj):
    """★ Ω₀-무관 지수 (선형 영역 — I2 의 p≈1 과 정합)."""
    s_lo, _ = omega_exponent(collapse(Om0=1e-10))
    s_hi, _ = omega_exponent(collapse(Om0=1e-6))
    assert abs(s_lo - s_hi) <= 5e-3, (s_lo, s_hi)


def test_decisive_grid_vs_truncated_hierarchy(traj):
    """★★ 결정실험: 정확 격자는 **감쇠**(+), 절단 계층은 **성장**(−) 를 준다.

    격자 = G1 (자유흐름 정확·양수성 구조보장) ⇒ 이쪽이 참값.
    ⇒ BKL 무시 성립 (감쇠), 단 완전유체보다 훨씬 느림; 절단 계층은 오답."""
    sg, Om_g, _ = grid_exponent(traj)
    sh, _ = omega_exponent(traj)
    sf = perfect_fluid_exponent(traj)
    assert sg > 0.15, sg                                # 격자: 감쇠 (τ→−∞)
    assert sh < -0.15, sh                               # 계층: 성장 (오답)
    assert sg * sh < 0.0                                # ★ 부호 반전 실재
    assert sf > 5.0 * sg                                # 유체가 훨씬 빠른 감쇠
    assert Om_g[-1] < Om_g[0]                           # 특이점 방향 감쇠 확인


def test_truncation_positivity_breakdown():
    """★★ I2 발견의 현실화: l_max=4 에서 Ω<0 (양수성 붕괴), l_max=2 는 양수."""
    Om2 = omega_exponent(collapse(l_max=2))[1]
    Om4 = omega_exponent(collapse(l_max=4))[1]
    assert Om2.min() > 0.0
    assert Om4.min() < 0.0


def test_bgk_in_truncated_hierarchy_is_falsified():
    """★ 반증 박제: 절단 계층에 BGK-감쇠 (l≥2) 를 넣으면 Ω<0 로 발산 —
    정칙화는 **격자** (양수성 보존) 에서 해야 한다 (G1/G2 의 정당화)."""
    Om = omega_exponent(collapse(l_max=3, nu_bgk=5.0))[1]
    assert (Om.min() < 0.0) or (not np.isfinite(Om).all())
