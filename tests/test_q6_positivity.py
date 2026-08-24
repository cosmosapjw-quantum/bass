"""
Q6 · **양수성 · 로그공간** 게이트 (76차).

I2c 이월 (깊은 붕괴 + 강충돌) 을 로그공간 상태로 해소한다.
  · ★ ln Ĝ 상태에서 |ln Ĝ| > 700 (float 범위 밖) 이어도 모멘트가 유한
  · ★ f ≥ 0 이 **구조적** (상태가 ln f 이므로 exp 가 항상 양수)
  · 충돌 후에도 양수 (핵이 양성 ⇒ 지수가 양성보존)
  · I2c 의 LNA_WALL = 300 이 더는 필요없다 (강이방×강충돌 스윕)
  · 수 보존 (충돌은 P₀ 항이 구조적으로 보장)
"""
import numpy as np
import pytest

RC = pytest.importorskip("bianchi_rustcore")
if not hasattr(RC, "qm_collide_log"):
    pytest.skip("Q6 로그공간 미빌드", allow_module_level=True)

from bianchi.q import comoving as CM  # noqa: E402
from bianchi.q import contract as C  # noqa: E402
from bianchi.q import sphere as S  # noqa: E402


def _state(amp, n_theta=24, n_phi=48):
    sph = S.sphere(n_theta, n_phi)
    e, w = S.nodes(sph)
    st = CM.ComovingState(sph, lG=amp * e[:, 2])
    return st, sph


def test_moments_survive_extreme_log_range():
    """★ |ln Ĝ| ~ 700 (exp 가 float 범위를 넘는 값) 에서도 유한."""
    for amp in (300.0, 700.0, 2000.0):
        st, _ = _state(amp)
        lr, q, pi = st.moments()
        assert np.isfinite(lr), (amp, lr)
        assert lr > 100.0                      # 실제로 범위 밖 크기
        assert np.isfinite(q).all() and np.isfinite(pi).all()
        assert float(np.abs(q).max()) <= 1.0   # 비는 항상 유계
        assert float(np.abs(pi).max()) <= 1.0


def test_positivity_is_structural():
    """★ 상태가 ln Ĝ 이므로 Ĝ = exp(ln Ĝ) > 0 — 구조적 (위반 0건)."""
    viol = 0
    rng = np.random.default_rng(0)
    for _ in range(100):
        amp = rng.uniform(1.0, 500.0)
        nu = rng.uniform(0.0, 50.0)
        st, _ = _state(amp, 16, 32)
        e, mu, lw = st.geometry()
        lg = CM.collide_log(lw, st.lG, e, nu)
        if not np.isfinite(lg).all():
            viol += 1
    assert viol == C.budget("Q6", "positivity")


def test_lna_wall_is_no_longer_needed():
    """★ I2c 의 명시 거부 임계 (300) 를 훌쩍 넘겨도 정상 — 이월 항목 해소."""
    wall = C.MEASURED["i2c_lna_wall"]
    st, _ = _state(3.0 * wall, 16, 32)
    assert st.lG.max() > wall
    e, mu, lw = st.geometry()
    lg = CM.collide_log(lw, st.lG, e, 5.0)
    assert np.isfinite(lg).all()
    lr, q, pi = CM.moments_log(lw, lg, e)
    assert np.isfinite(lr) and lr > wall / 2.0
    assert np.isfinite(q).all() and np.isfinite(pi).all()


def test_number_conservation_under_collision():
    """충돌은 ρ (l=0 모멘트) 를 정확히 보존 — P₀ 항의 구조적 귀결."""
    tol = C.budget("Q6", "number")
    st, _ = _state(3.0, 24, 48)
    e, mu, lw = st.geometry()
    lr0 = CM.moments_log(lw, st.lG, e)[0]
    for x in (0.1, 3.0, 1e3):
        lg = CM.collide_log(lw, st.lG, e, x)
        lr1 = CM.moments_log(lw, lg, e)[0]
        assert abs(np.expm1(lr1 - lr0)) <= tol, (x, lr1, lr0)


def test_strong_anisotropy_times_strong_collision_sweep():
    """★ I2c 가 발산했던 조합 (강이방 × 강충돌) 100 케이스 전부 유한·양수."""
    rng = np.random.default_rng(7)
    for _ in range(100):
        amp = rng.uniform(50.0, 400.0)
        nu = rng.uniform(1.0, 1e4)
        st, _ = _state(amp, 16, 32)
        e, mu, lw = st.geometry()
        lg = CM.collide_log(lw, st.lG, e, nu)
        lr, q, pi = CM.moments_log(lw, lg, e)
        assert np.isfinite(lg).all() and np.isfinite(lr), (amp, nu)
        assert np.isfinite(q).all() and np.isfinite(pi).all()
