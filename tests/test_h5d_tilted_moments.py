"""
H5-d1 · boosted 정확구적 오라클 시험.

★ 게이트 순서가 설계다 — **계층을 경유하지 않는 것부터** 세운다:
  1. boost 대수 자기검증 (λ′² = E′² − m²)  ← 부호 오타를 한 줄로 잡는다
  2. v→0 비트-정확 환원
  3. ★★ T^{μν} 프레임 무관성 — boost 대수 + 구적을 한 번에 검증.
     여기서 어긋나면 이후 어떤 계층 검증도 의미가 없다.
  4. 닫힌형 |q′|/ρ′ = v(ρ+p)/(ρ+pv²) 와 대조 (구적을 쓰지 않는 독립 검산)
  5. 홀수 l 이 **인공 왜곡 없이** 켜진다 (H1 은 `f_dipole` 을 도입해야 했다)
"""
import numpy as np
import pytest

from bianchi.matter import hierarchy as H
from bianchi.matter import tilted_moments as TM

A_ANISO = (1.0, 0.9, 1.2)
V_MULTI = (0.15, -0.1, 0.2)


# ═══════════════════════════════ 1. boost 대수 자기검증
@pytest.mark.parametrize("mass", [0.0, 0.7, 3.0])
def test_boost_preserves_mass_shell(mass):
    """★ λ′² = E′² − m² 가 격자 **전점**에서 성립 (측정 1.3e−15).

    유도를 믿지 않고 측정한다.  boost 부호가 하나만 틀려도 이 항등식이 깨진다.
    """
    r = TM.boost_algebra_residual(mass=mass)
    assert r["mass_shell"] < 1e-13, r
    assert r["energy_positive"]


def test_boost_rejects_superluminal():
    with pytest.raises(ValueError):
        TM.boost_factors((0.8, 0.8, 0.0))


def test_boost_factor_k_is_regular_at_zero():
    """k = γ²/(γ+1) 은 v→0 에서 1/2 로 매끄럽다 ((γ−1)/v² 형태의 0/0 회피)."""
    _, k0 = TM.boost_factors((0.0, 0.0, 0.0))
    assert abs(k0 - 0.5) < 1e-15
    _, k1 = TM.boost_factors((1e-8, 0.0, 0.0))
    assert abs(k1 - 0.5) < 1e-12


# ═══════════════════════════════ 2. v→0 환원
@pytest.mark.parametrize("l,i", [(0, 0), (0, 1), (1, 0), (2, 0), (3, 0), (4, 0)])
def test_zero_tilt_is_bit_exact(l, i):
    """★ v=0 이면 피적분함수가 문자 그대로 같아지므로 **비트-정확**이어야 한다."""
    j0 = np.atleast_1d(np.asarray(H.J_moment(A_ANISO, 0.7, l, i), float))
    jt = np.atleast_1d(np.asarray(TM.J_moment_tilted(A_ANISO, (0.0, 0.0, 0.0), 0.7,
                                                     l, i), float))
    assert np.array_equal(j0, jt), (l, i, np.abs(j0 - jt).max())


# ═══════════════════════════════ 3. ★★ T^{μν} 프레임 무관성
@pytest.mark.parametrize("mass", [0.0, 0.7, 3.0])
def test_frame_independence_of_stress_tensor(mass):
    """★★ 가장 결정적: boosted 구적 (ρ′,q′,π′) = 법선 (ρ,0,p,π) 의 텐서 변환.

    계층 방정식을 전혀 쓰지 않는다 — boost 대수와 구적을 **동시에** 검증한다.
    측정: ρ 4e−16, p 2e−16, q 3e−15, π 1e−14.
    """
    r = TM.frame_independence_residual(A_ANISO, V_MULTI, mass)
    assert r["rho"] < 1e-13, r
    assert r["p"] < 1e-13, r
    assert r["q"] < 1e-12, r
    assert r["pi"] < 1e-12, r


def test_normal_frame_has_no_energy_flux():
    """법선 프레임에서 q_a = 0 (전제 확인 — 이게 깨지면 위 게이트의 설정이 틀린 것)."""
    r = TM.frame_independence_residual(A_ANISO, V_MULTI, 0.7)
    assert r["normal_q_is_zero"] < 1e-14


def test_tilted_energy_density_exceeds_normal():
    """boost 하면 ρ′ > ρ (γ² 인자) — 부호·방향 감각 확인."""
    r = TM.frame_independence_residual(A_ANISO, V_MULTI, 0.7)
    assert r["rho_tilted"] > r["rho_normal"]


# ═══════════════════════════════ 4. 닫힌형 대조 (구적 미사용)
@pytest.mark.parametrize("mass", [0.0, 1.0])
@pytest.mark.parametrize("s", [0.05, 0.2, 0.4, 0.7])
def test_dipole_matches_closed_form(mass, s):
    """★ |q′|/ρ′ = v(ρ+p)/(ρ+pv²) — 구적을 전혀 쓰지 않는 독립 검산.

    무질량이면 (4/3)v/(1+v²/3).  측정: v=0.4 에서 0.506329114 (닫힌형과 일치).
    """
    a = (1.0, 1.0, 1.0)                       # 등방 → π = 0 이라 닫힌형이 정확
    v = (0.0, 0.0, s)
    rho = H.J_moment(a, mass, 0, 0)
    p = H.J_moment(a, mass, 0, 1) / 3.0
    rho_t, _, q_t, _ = TM.moments_tilted(a, v, mass)
    got = float(np.abs(q_t).max() / rho_t)
    want = TM.analytic_dipole_ratio(rho, p, v)
    assert abs(got - want) < 1e-12, (got, want)


def test_massless_dipole_approaches_four_thirds_v():
    """작은 v 극한: |q′|/ρ′ → (4/3)v (복사의 표준 결과)."""
    rows = TM.dipole_from_boost(vs=(0.01, 0.05))
    for s, ratio, rel in rows:
        assert abs(rel - 1.0) < 2e-3 * (1 + s / 0.01), (s, rel)


def test_dipole_points_against_boost():
    """q′ 는 boost 반대방향 — 움직이는 관측자는 물질이 뒤로 흐르는 것을 본다."""
    _, _, q, _ = TM.moments_tilted((1.0, 1.0, 1.0), (0.0, 0.0, 0.3), 0.0)
    assert q[2] < 0.0
    assert abs(q[0]) < 1e-14 and abs(q[1]) < 1e-14


# ═══════════════════════════════ 5. ★ 홀수 l 이 인공 왜곡 없이 켜진다
def test_boost_activates_odd_l_without_f_dipole():
    """★★ H1 대비 개선: 등방 f₀ + 등방 a_vec 에서도 boost 가 홀수 l 을 켠다.

    H1 은 |J_a| ~ 4e−17 (항등적 0) 이라 (A) 항군을 시험하려고 `f_dipole` 을
    **인공 도입**해야 했다.  boost 는 물리적 쌍극자원이므로 분포를 왜곡하지 않는다.
    측정 (v=0.25): l=1 → 3.3e−1, l=3 → 7.0e−3, l=5 → 8.1e−5.
    """
    iso = (1.0, 1.0, 1.0)
    rows = dict(TM.odd_l_activation(iso, 0.0, (0.0, 0.0, 0.25), l_max=5))
    for l in (1, 3, 5):
        assert rows[l] > 1e-6, (l, rows[l])
    # 같은 설정의 법선 프레임에서는 항등적으로 0
    rho = H.J_moment(iso, 0.0, 0, 0)
    for l in (1, 3, 5):
        w = float(np.abs(np.asarray(H.J_moment(iso, 0.0, l, 0), float)).max())
        assert w / rho < 1e-14, (l, w / rho)


def test_odd_l_magnitudes_decrease():
    """다극 크기가 l 에 따라 단조감소 (절단이 정당하다는 신호)."""
    rows = dict(TM.odd_l_activation((1.0, 1.0, 1.0), 0.0, (0.0, 0.0, 0.25), l_max=5))
    vals = [rows[l] for l in range(6)]
    assert all(b < a for a, b in zip(vals, vals[1:])), vals


def test_tilted_moments_are_pstf():
    """J′_{A_l} 이 PSTF (대각합 제거) — boost 후에도 구조가 유지된다."""
    for l in (2, 3, 4):
        j = np.asarray(TM.J_moment_tilted(A_ANISO, V_MULTI, 0.5, l, 0), float)
        tr = np.abs(np.trace(j, axis1=0, axis2=1)).max()
        assert tr < 1e-10 * np.abs(j).max(), (l, tr)


# ═══════════════════════════════ 6. 격자 적합성 (유효 범위를 명시)
def test_grid_stays_adequate_up_to_extreme_tilt():
    """★ |v| → 0.9 (γ=2.29) 까지 프레임 무관성 잔차 ≤ 5e−14.

    boost 후 E′ 가 방향의존이라 반경격자가 부적합해질 수 있다 — 조용히 쓰지 않고
    측정해 고정한다.  (측정: 0.1→2.3e−15, 0.5→2.8e−15, 0.9→4.6e−14)
    """
    scan = TM.grid_adequacy_scan(vmax=0.9, n=10)
    worst = max(r for _, _, r in scan)
    assert worst < 1e-12, scan
    assert scan[-1][1] > 2.0                       # γ 가 실제로 커졌는지
