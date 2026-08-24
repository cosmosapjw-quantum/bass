"""
K4 · **type V 자유흐름 오라클** — tilt 결합의 선행조건.

K2b 의 no-go 로 Bianchi I 은 tilt 를 담을 수 없음이 확립됐다.  담으려면 A ≠ 0 과
Σ ≠ 0 이 동시에 필요한데, type V 에서는 **불변기저 운동량이 보존되지 않아**
type I 정확 구적의 근거가 사라진다.  여기서 특성곡선을 다시 세우고 검증한다.

★ 이 파일이 고정하는 측정:
  · 두 경로 (구조상수 조립 vs 기호 측지선) 일치 **2.1e−16**
  · A→0 에서 p_i = const **정확히 0.00e+00**,  모멘트는 type I 정확구적과 **9.5e−17**
  · p₂/p₃ 보존 4.6e−16 ;  등방에서 Σp_i² 보존 6.8e−14 (이방 대조군은 1.96e−3 로 깨짐)
  · Killing 운동량 p_y, p_z 보존 **1.5e−15** — 불변기저 ODE 를 안 쓰는 독립 게이트
  · 등방 무질량 ρ ∝ a⁻⁴ 잔차 1.2e−12

★ 사전 경고가 **너무 비관적이었다** (정직하게 기록): "닫힌형이 아니라 정확도가 ODE
  솔버에 걸리므로 type I 오라클보다 약할 것" 이라고 적어 두었는데, 실제로는 역방향
  특성곡선이 4차 수렴해 64스텝에 1e−13, 128스텝에 5e−14 다.  **약한 오라클이 아니다.**
"""
import numpy as np
import pytest

from bianchi.matter import type_v as TV


# ═══════════════════════════════ 1. ★★ 두 경로
@pytest.mark.parametrize("x", [0.0, 0.37, -0.5])
def test_structure_constants_match_symbolic_geodesic(x):
    """★★ 구조상수 조립 vs **명시적 계량의 기호 측지선** (2e−16).

    부호를 유도로 단정하지 않고 두 경로로 확정한다 — 프로젝트 관례.
    """
    assert TV.route_residual(x=x)["residual"] < 1e-13


@pytest.mark.parametrize("mass", [0.0, 0.6, 2.0])
def test_routes_agree_for_any_mass(mass):
    assert TV.route_residual(mass=mass)["residual"] < 1e-13


# ═══════════════════════════════ 2. ★ A → 0 환원
def test_type_I_reduction_is_bit_exact():
    """★ A = 0 이면 p_i 가 **정확히** 상수 (0.00e+00) — type I 의 근거 복원."""
    assert TV.type_I_reduction_residual() == 0.0


def test_moments_reduce_to_type_I_exact_quadrature():
    """★★ A→0 에서 모멘트가 type I **정확 구적**과 9.5e−17 일치.

    역방향 특성곡선·격자·측도를 한 번에 검증하는 종단 게이트.
    """
    assert TV.type_I_moment_residual() < 1e-13


# ═══════════════════════════════ 3. ★★ 보존량
def test_p2_over_p3_is_conserved():
    """ṗ₂/p₂ = ṗ₃/p₃ 이므로 p₂/p₃ 가 보존 (4.6e−16)."""
    assert TV.p2_over_p3_residual() < 1e-12


def test_isotropic_case_conserves_momentum_norm():
    """★★ 등방 a_i 에서 Σp_i² 보존 (6.8e−14) — open FRW 의 λ ∝ 1/a 와 같은 말."""
    assert TV.isotropic_invariant_residual() < 1e-11


def test_anisotropic_control_breaks_it():
    """★ 대조군: 이방이면 Σp_i² 가 **깨진다** (1.96e−3) — 게이트가 살아 있다."""
    assert TV.anisotropic_invariant_is_broken() > 1e-5


def test_killing_momenta_are_conserved():
    """★★ 좌표 그림의 Killing 운동량 p_y, p_z 보존 (1.5e−15 / 3.0e−15).

    y, z 가 순환좌표라는 사실만 쓰고 불변기저 ODE 를 **전혀 안 쓴다** — 독립 게이트.
    """
    r = TV.killing_momentum_residual()
    assert r["py"] < 1e-12, r
    assert r["pz"] < 1e-12, r
    assert abs(r["x_final"]) > 1e-3, r          # 실제로 x 가 움직였다


def test_isotropic_massless_redshifts_as_a_to_the_minus_four():
    """★ 등방 type V (= open FRW) 무질량에서 ρ ∝ a⁻⁴ (잔차 1.2e−12) — 물리 게이트."""
    assert TV.isotropic_redshift_residual() < 1e-9


# ═══════════════════════════════ 4. 오라클의 실제 정확도 (정직하게 노출)
def test_backward_tracing_is_fourth_order():
    """★ 역추적이 4차 수렴 — 8스텝 3.4e−9 → 128스텝 5.3e−14."""
    rows = TV.moment_convergence()
    n = np.array([r[0] for r in rows], float)
    e = np.array([r[1] for r in rows], float)
    p = -np.polyfit(np.log(n), np.log(e), 1)[0]
    assert 3.5 < p < 4.5, (rows, p)
    assert rows[-1][1] < 1e-12, rows


def test_solver_accuracy_is_reported_not_assumed():
    """★ 특성곡선 자체의 수렴차수도 노출 (RK4, 측정 3.82 — 최고정밀에서 반올림 지배)."""
    rows = TV.solver_accuracy()
    n = np.array([r[0] for r in rows], float)
    e = np.array([r[1] for r in rows], float)
    p = -np.polyfit(np.log(n), np.log(e), 1)[0]
    assert 3.0 < p < 4.5, (rows, p)


def test_the_pessimistic_prediction_was_wrong():
    """★ **정직성 고정**: "ODE 솔버에 걸려 type I 보다 약한 오라클이 될 것" 이라는
    사전 경고가 틀렸다.  64스텝에서 이미 1e−12 아래다.
    """
    rows = dict(TV.moment_convergence(steps=(64,)))
    assert rows[64] < 1e-11, rows
