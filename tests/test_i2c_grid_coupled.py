"""
I2c · **절단 없는 격자-결합** (75차) — I2b 결정실험의 귀결을 계에 반영.

  · ★★ 무충돌 결합 지수 ≡ I2b 시험장 격자 (+0.234) — 절단 계층의 −0.258
    (부호 반전) 을 **결합계 안에서** 교정.  Gauss 잔차 ≤1e−8, Ĝ>0 보존.
  · 진공 극한: Ω→0 에서 기하가 차트 Mixmaster 와 일치 (Σ² → Kasner 원).
  · ★ 약이방 (B2b 실사용 영역): 충돌 켠 결합이 안정 + 유체 지수를
    |Π|/Ω ~4% 보정 이내로 재현 — G2 사다리의 결합계 내 검증.
  · ★ 표현범위 벽: 축비 |ln a| > 300 은 **명시 거부** (무언 NaN 금지) —
    깊은 붕괴의 로그-공간 상태는 후속 증분 (LIMITATIONS 박제).
"""
import numpy as np
import pytest

from bianchi.analysis import kasner as K
from bianchi.matter import grid_coupled as GC


def _ic(u0=3.7, Om0=1e-6, seed=1e-3):
    p = K.u_to_exponents(u0)
    Sp, Sm = K.sigma_from_exponents(p)
    n = np.array([seed] * 3)
    Kc = (n @ n - 2*(n[0]*n[1] + n[1]*n[2] + n[2]*n[0])) / 12.0
    r = np.sqrt(max(1.0 - Kc - Om0, 0.0) / (Sp*Sp + Sm*Sm))
    return GC.initial_state(np.array([Sp*r, Sm*r, 0, 0, 0]), n, Om0)


def _exponent(traj, tau, cut=-5.0, stride=40):
    Om = GC.omega_series(traj[::stride])
    t = np.linspace(0.0, tau, traj.shape[0])[::stride]
    m = t < cut
    return float(np.polyfit(t[m], np.log(Om[m]), 1)[0]), Om


def test_collisionless_matches_test_field_grid():
    """★★ I2b 교정: 결합 지수 = 시험장 격자 (+0.234), 계층의 −0.258 아님."""
    y = _ic()
    yT, tr = GC.rk4(y, -25.0, 4000, keep=True)
    assert np.isfinite(tr).all()
    s, Om = _exponent(tr, -25.0)
    assert 0.20 <= s <= 0.27, s                        # I2b 시험장 +0.234
    assert Om[-1] < Om[0]                              # 특이점 방향 감쇠


def test_constraint_and_positivity():
    """★ Gauss 잔차 유계 + Ĝ>0 (양수성 구조보장 — 계층이 잃던 성질)."""
    y = _ic()
    yT, tr = GC.rk4(y, -20.0, 3200, keep=True)
    res = [abs(GC.gauss_residual(r)) for r in tr[::200]]
    assert max(res) <= 1e-8, max(res)
    assert (tr[:, 12:] > 0.0).all()


def test_vacuum_limit_stays_on_kasner_circle():
    """★ 진공 극한 (Ω₀→0): Σ² 가 Kasner 원 근처 (튐 사이) — 차트 정합."""
    y = _ic(Om0=1e-12)
    yT, tr = GC.rk4(y, -12.0, 2400, keep=True)
    s2 = (tr[:, :5] ** 2).sum(axis=1)
    assert s2.max() <= 1.0 + 1e-6
    assert s2.max() >= 0.99                            # 대부분 Kasner 원 위


def test_weak_anisotropy_collisional_regime():
    """★ B2b 실사용 영역: 충돌 켠 결합이 안정 + 유체 지수 재현 (Π 보정 이내)."""
    S5 = np.array([0.02, -0.01, 0, 0, 0])
    N3 = np.array([1e-3, -5e-4, 3e-4])
    out = {}
    for nu, kind in ((0.0, "bgk_iso"), (50.0, "bgk_iso"), (50.0, "thomson")):
        y = GC.initial_state(S5, N3, 0.9,
                             aniso=lambda n: 1.0 + 0.15*n[:, 2]
                             + 0.1*(n[:, 0]**2 - n[:, 1]**2))
        yT, tr = GC.rk4(y, 3.0, 600, nu=nu, kind=kind, keep=True)
        assert np.isfinite(tr).all() and (tr[:, 12:] > 0).all()
        Om = GC.omega_series(tr[::6])
        t = np.linspace(0.0, 3.0, tr.shape[0])[::6]
        m = t > 0.5
        s = float(np.polyfit(t[m], np.log(Om[m]), 1)[0])
        q = 2.0*(tr[::6, :5]**2).sum(axis=1) + Om
        fluid = float(np.mean((2.0*q - 2.0)[m]))
        out[(nu, kind)] = (s, fluid)
        assert abs(s - fluid) <= 0.10 * abs(fluid), (nu, kind, s, fluid)
    # 충돌이 켜져도 (약이방에서는) 결과가 안정적으로 같은 대역
    vals = [v[0] for v in out.values()]
    assert max(vals) - min(vals) <= 1e-3


def test_representation_wall_is_explicit():
    """★ 표현범위 벽: |ln a| > 300 은 OverflowError (무언 NaN 금지)."""
    y = _ic()
    S5, N3, lnH, lna, G = GC.unpack(y)
    bad = GC.pack(S5, N3, lnH, np.array([400.0, -200.0, -200.0]), G)
    with pytest.raises(OverflowError, match="축비"):
        GC.rhs(bad)
