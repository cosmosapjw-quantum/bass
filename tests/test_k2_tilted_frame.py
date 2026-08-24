"""
K2 · on-shell tilt 속도 검증 — v(t) 를 처방하지 않고 물질에서 푼다.

★ tilt 의 well-posed 정의: **에너지틀(Landau)** — q′_a(v) = 0.
  boosted 정확 구적이 있으므로 이 방정식을 직접 풀 수 있다 (근찾기 오라클).

★ 두 독립 경로:
  A — 에너지틀 **근찾기** 를 시간에 따라 유한차분한 v̇   (계층 미사용)
  B — **tilted Euler** (계층 l=1) 를 v̇ 에 대해 푼 값     (근찾기 미사용)

★ 정직한 범위: 여기서 배경 a(t) 는 여전히 **처방**이다.  tilt 와 Einstein 결합을
  동시에 푸는 것(K1+K2 통합)은 다음 단계다.
"""
import numpy as np
import pytest

from bianchi.matter import tilted_frame as TF

A0 = (1.0, 0.9, 1.2)


# ═══════════════════════════════ 언제 tilt 가 물리적으로 존재하는가
def test_isotropic_distribution_has_no_tilt():
    """★ 등방 f₀ 는 f(p)=f(−p) 라 법선틀에서 이미 q_a = 0 — tilt 가 **없다**.

    쌍극 f₀ (벌크 운동량) 라야 tilt 가 산다.  H1 에서 `f_dipole` 은 홀수 l 을 켜려는
    **인공 장치**였는데, 여기서는 "움직이는 물질" 이라는 **물리적 설정**이다.
    """
    d = TF.normal_frame_has_flux_only_with_dipole()
    assert d["isotropic"] < 1e-14, d
    assert d["dipole"] > 1e-2, d


# ═══════════════════════════════ 에너지틀 근찾기 (오라클)
@pytest.mark.parametrize("mass", [0.0, 0.7, 2.0])
def test_energy_frame_solve_converges(mass):
    """★ q′_a(v) = 0 이 Newton 3회로 수렴, 잔차 ~1e−17."""
    r = TF.energy_frame_velocity(A0, mass)
    assert r["converged"], r
    assert r["residual"] < 1e-13, r
    assert r["iters"] <= 10, r
    assert 0.0 < np.linalg.norm(r["v"]) < 1.0


def test_tilt_aligns_with_the_dipole_axis():
    """쌍극이 z축이면 tilt 도 z축 — 다른 성분은 기계정밀도로 0."""
    v = TF.energy_frame_velocity(A0, 0.0)["v"]
    assert abs(v[2]) > 1e-3
    assert abs(v[0]) < 1e-12 and abs(v[1]) < 1e-12


def test_heavier_matter_tilts_less():
    """유질량일수록 tilt 가 작다 (측정 0.0677 → 0.0664 → 0.0591).

    같은 쌍극 세기라도 무거우면 벌크 속도가 낮다 — 물리적으로 기대되는 방향.
    """
    vs = [np.linalg.norm(TF.energy_frame_velocity(A0, m)["v"])
          for m in (0.0, 0.7, 2.0)]
    assert vs[0] > vs[1] > vs[2], vs


def test_energy_frame_kills_the_flux():
    """구한 v 에서 q′ 가 실제로 0 (정의를 만족하는지 직접 확인)."""
    f0 = TF.dipole_f0()
    v = TF.energy_frame_velocity(A0, 0.0, f0)["v"]
    q = TF.energy_flux(v, np.asarray(A0, float), 0.0, f0)
    from bianchi.matter import tilted_moments as TM
    rho = TM.J_moment_tilted(A0, v, 0.0, 0, 0, f0)
    assert np.abs(q).max() / rho < 1e-13


# ═══════════════════════════════ on-shell v(t)
def test_v_trajectory_stays_on_the_energy_frame():
    """배경을 따라가며 매 시각 에너지틀을 유지 (잔차 ≤1e−15)."""
    tr = TF.exact_v_trajectory(A0, 1.0, (0.06, -0.02, -0.04), 0.0, 0.3, nsteps=6)
    assert tr["residual"].max() < 1e-13, tr["residual"]
    assert np.all(np.abs(tr["v"][:, 2]) > 1e-3)


def test_v_evolves_slowly_under_expansion():
    """무질량 tilt 는 팽창에서 거의 보존 (측정 0.06772 → 0.06829, +0.8%)."""
    tr = TF.exact_v_trajectory(A0, 1.0, (0.06, -0.02, -0.04), 0.0, 0.3, nsteps=6)
    v0, vT = abs(tr["v"][0, 2]), abs(tr["v"][-1, 2])
    assert abs(vT / v0 - 1.0) < 0.05, (v0, vT)


# ═══════════════════════════════ ★★ 두 경로 교차검증
@pytest.mark.parametrize("mass", [0.0, 0.7])
def test_tilted_euler_matches_root_finding(mass):
    """★★ tilted Euler 로 푼 v̇ 가 근찾기 FD 와 일치 (1.6e−8 / 2.1e−6).

    두 경로는 독립이다: 하나는 q′=0 을 직접 풀고, 다른 하나는 계층 l=1 방정식을
    v̇ 에 대해 푼다.  일치는 "에너지틀이 계층의 운동량 방정식과 정합" 임을 뜻한다.
    """
    c = TF.cross_validate_vdot(mass=mass)
    assert c["rel"] < 1e-4, c
    assert c["cond"] < 100.0, c


def test_euler_reuses_verified_assembly_not_hand_transcription():
    """★ 회귀: l=1 항을 **손으로 다시 적지 않는다**.

    처음에 손 전사했다가 (div-free) 에서 J^(1) 대신 p 를 넣어 **3배** 틀렸고,
    교차검증이 24배 어긋나며 잡아냈다 (부호까지 반대였다).
    이제 `tilted_equation.equation_lhs` (두 오라클로 검증됨) 를 그대로 쓴다.
    """
    import inspect
    src = inspect.getsource(TF._euler_lhs)
    assert "equation_lhs" in src
    assert "TE." in src


def test_vdot_system_is_well_conditioned():
    """v̇ 선형계가 온순 (cond ~1.1) — 근찾기 없이도 안정적으로 풀린다."""
    f0 = TF.dipole_f0()
    a = np.asarray(A0, float)
    v = TF.energy_frame_velocity(a, 0.0, f0)["v"]
    da = (1.0 + np.array([0.06, -0.02, -0.04])) * a
    _, M = TF.tilted_euler_vdot(a, da, v, 0.0, f0)
    assert np.linalg.cond(M) < 100.0
    assert abs(np.linalg.det(M)) > 1e-6


# ═══════════════════════════════ 경계·방어
def test_superluminal_step_is_clamped():
    """Newton 스텝이 |v| ≥ 1 로 넘어가지 않는다 (물리적 경계 유지)."""
    r = TF.energy_frame_velocity(A0, 0.0, eps=0.9)
    assert np.linalg.norm(r["v"]) < 1.0


def test_stronger_dipole_gives_larger_tilt():
    """쌍극이 강할수록 tilt 가 크다 (단조성)."""
    vs = [np.linalg.norm(TF.energy_frame_velocity(A0, 0.0, eps=e)["v"])
          for e in (0.1, 0.3, 0.6)]
    assert vs[0] < vs[1] < vs[2], vs
