"""
B2b 접합면 · **이력 주입 인터페이스 계약 게이트** (75차).

외부 모듈 도착 전 접합면을 굳힌다 (PLAN §8).  외부 이력이 오면 이 파일을
그 이력으로 파라미터화해 그대로 재실행한다 (docs/B2B-INTEGRATION-SPEC.md §7).

  · 계약 검사 7종 (validate_history) — 범위 가드 포함.
  · ★ 계획 명시 게이트: **주입 이력 = 내장일 때 기존 결과 비트-재현**
    (optical_depth 주입 경로 ≡ 기존 optical_depth_and_visibility, 차 0.0).
  · Tabulated 왕복 (격자 위 정확), 보간 단조성, 범위 밖 예외.
  · ν_τ 물리: 재결합 전 ≫ 1 (결합) → 후 ≪ 1 (이탈); n_H 상수 단일 진실원.
"""
import numpy as np
import pytest

from bianchi.thermo import history_api as HA
from bianchi.thermo import recombination as REC


@pytest.fixture(scope="module")
def hist():
    return HA.SahaHistory()


def test_contract_checks_pass(hist):
    """★ 계약 7종 — 외부 모듈이 가장 먼저 통과해야 할 관문."""
    res = HA.validate_history(hist)
    assert res["ok"], res["checks"]
    assert set(res["checks"]) >= {"finite", "nonneg", "bounded",
                                  "high_z_ionized", "recombines",
                                  "range_sane", "range_guard"}


def test_injection_path_reproduces_builtin_bitwise(hist):
    """★★ 계획 §8 게이트: 주입 경로 ≡ 기존 직접 경로 (비트-재현)."""
    zg = np.linspace(2800.0, 600.0, 300)
    a = HA.optical_depth(hist, zg)
    b = REC.optical_depth_and_visibility(zg, np.asarray(hist.x_e(zg), float))
    assert a["z_star"] == b["z_star"]
    assert np.abs(a["tau"] - b["tau"]).max() == 0.0
    assert np.abs(a["g"] - b["g"]).max() == 0.0


def test_tabulated_roundtrip_and_range_guard(hist):
    """★ 표 수입 (외부 모듈의 표준 형태): 격자 위 정확 + 범위 밖 예외."""
    zg = np.linspace(2900.0, 700.0, 250)
    t = HA.TabulatedHistory(zg, np.asarray(hist.x_e(zg), float), name="ext-mock")
    assert np.abs(np.asarray(t.x_e(zg)) - np.asarray(hist.x_e(zg))).max() == 0.0
    with pytest.raises(ValueError, match="범위"):
        t.x_e(5000.0)
    assert HA.validate_history(t, strict=False)["checks"]["range_guard"]


def test_thomson_rate_physics_and_single_source(hist):
    """★ ν_τ: 재결합 전 ≫1 → 후 ≪1;  n_H 상수는 recombination 과 동일."""
    nu_hi = HA.thomson_rate(hist, 2500.0)
    nu_lo = HA.thomson_rate(hist, 700.0)
    assert nu_hi > 10.0 > 1e-3 > nu_lo
    z = np.array([1100.0])
    assert np.allclose(HA.n_H_cm3(z),
                       REC._NB0_PER_OBH2 * 0.0224 * (1 + z) ** 3, rtol=0, atol=0)
    nt = HA.thomson_rate(hist, 1100.0, tau_units=False)
    assert nt > 0.0 and np.isfinite(nt)


def test_protocol_duck_typing():
    """★ 덕 타이핑: 최소 계약만 만족하는 임의 객체도 소비자 경로에 꽂힌다."""
    class Ext:
        name = "ext-minimal"
        z_range = (500.0, 2000.0)

        def x_e(self, z):
            z = np.atleast_1d(np.asarray(z, float))
            if z.min() < 500.0 or z.max() > 2000.0:
                raise ValueError("z 범위 밖")
            return 0.5 * (1.0 + np.tanh((z - 1200.0) / 100.0))

    e = Ext()
    assert isinstance(e, HA.IonizationHistory)
    assert HA.validate_history(e, strict=False)["checks"]["range_guard"]
    assert HA.thomson_rate(e, 1500.0) > 0.0
