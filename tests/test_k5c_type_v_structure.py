"""
K5c · **A 를 좌표상수로 둔 것의 정체** — 근사가 아니라 게이지였다.

K5b 는 A 를 상수로 두고 결합계를 굴렸다.  그런데 Ellis-MacCallum 형식에서 a_a 는
`ȧ_a = −(Hδ + σ)·a` 로 **진화하는 변수**다.  우리는 그 식을 넣은 적이 없다.
넣지 않아도 되는 이유를 계량에서 확정한다.

★ 이 파일이 고정하는 측정:
  · 전체 교환자표가 기저 위에서 **닫힌다** (새는 성분 0개)
      [e₀,e_α] = −h_α e_α    (가속도 0, 회전 0 — 법선 측지 합동)
      [e₁,e₂] = −(A/a₁)e₂,  [e₁,e₃] = −(A/a₁)e₃,  [e₂,e₃] = 0
  · 프로젝트 자신의 `algebra.decompose` 로 n_ab = **0.0**, a_a = (−A/a₁, 0, 0),
    Jacobi 잔차 **0.0**
  · ★★ `ȧ_a + (H+σ₁)a_a` 가 **항등적으로 0** ⇒ A = const 는 진화식의 **정확해**
  · ★ 확장정규화 차트의 `A′ = qA − Σ·A` 와도 잔차 0 — 물리 단위/차트 규격화가 잠긴다
  · ★★ Ḣ 를 공간 Einstein 과 Raychaudhuri 로 각각 재면 차이가 **정확히 −F/6**
    (측정 1.8e−16) — 두 구속 진단자를 묶는 대수 항등식
  · ★ x → λx 게이지 불변성 (λ=1.4 에서 1e−9; λ=2.5 의 1e−4 는 **각 구적** 오차로,
    NANG 24→32→40 에서 6.1e−05 → 1.9e−06 → 5.6e−08 로 스펙트럼 수렴)

★★ 그리고 **정직한 한계** 하나를 숫자로 못 박았다: 대각 계량은 대각 물질만 담는다.
  비대각 Einstein 성분이 항등적으로 0 이므로 q₂=q₃=π_{i≠j}=0 이 필요하다.
      등방 f₀           q⊥ 9.7e−18   π_off 2.4e−17     ← 허용
      쌍극자 p₁         q⊥ 5.8e−18   π_off 3.3e−17     ← **허용** (등방일 필요는 없다)
      쌍극자 p₂         q⊥ 1.0e−01                     ← 거부
      사중극자 p₁p₂                  π_off 5.9e−02     ← 거부
  필요한 것은 등방성이 아니라 **횡방향 반사대칭 두 개**다.  `evolve_coupled` 가
  t=0 에 검사해 **거부**한다 — 없으면 비대각 성분을 조용히 버리고 틀린 답을 낸다.
"""
import numpy as np
import pytest
import sympy as sp

from bianchi.matter import type_v_coupled as C


# ═══════════════════════════════ 1. 구조 — 계량에서 직접
def test_commutator_table_closes_on_the_frame():
    """★★ 자기검증: 각 교환자가 기저의 선형결합이어야 한다 (새는 성분 0개)."""
    from audit import k5c_type_v_structure as K5c
    _, bad = K5c.commutator_table()
    assert bad == [], bad


def test_the_normal_congruence_is_geodesic_and_non_rotating():
    """★ [e₀,e_α] = −h_α e_α — 가속도항도 회전항도 없다 (Ω = 0)."""
    from audit import k5c_type_v_structure as K5c
    tc = K5c.time_commutators()
    assert all(sp.simplify(e) == 0 for e in tc["coeff"]), tc["coeff"]
    assert all(sp.simplify(e) == 0 for e in tc["offdiag"]), tc["offdiag"]
    assert all(sp.simplify(e) == 0 for e in tc["acceleration"]), tc["acceleration"]


def test_project_algebra_reads_type_V_off_the_metric():
    """★★ 두 경로가 만난다 — sympy 교환자 → 프로젝트의 `algebra.decompose`.

    n_ab = 0 (정확히), a_a = (−A/a₁,0,0), Jacobi n·a = 0.
    """
    from audit import k5c_type_v_structure as K5c
    d = K5c.decomposed()
    assert np.abs(d["n"]).max() == 0.0, d["n"]
    assert np.abs(d["a"] - d["a_expected"]).max() < 1e-15, d
    assert np.abs(d["jacobi"]).max() == 0.0, d["jacobi"]


def test_type_is_preserved_because_n_is_identically_zero():
    """★ ṅ 은 n 에 선형이라 n=0 이 정확히 보존된다 — 유형이 흐르지 않는다."""
    from audit import k5c_type_v_structure as K5c
    n, nd = K5c.n_evolution_residual()
    assert np.abs(n).max() == 0.0
    assert np.abs(nd).max() == 0.0


# ═══════════════════════════════ 2. ★★ A = const 는 근사가 아니다
def test_constant_A_is_an_exact_solution_of_the_a_vector_evolution():
    """★★ **K5c 의 결론** — `ȧ_a + (H+σ₁)a_a` 가 항등적으로 0.

    K5b 가 Ellis-MacCallum 진화식을 빠뜨린 게 아니라, ansatz 가 이미 만족한다.
    """
    from audit import k5c_type_v_structure as K5c
    assert sp.simplify(K5c.a_vector_evolution_residual()) == 0


def test_chart_normalisation_agrees_with_physical_units():
    """★ 확장정규화 차트의 `A′ = qA − Σ·A` 와 잔차 0 — 규격화 인자를 잠근다."""
    from audit import k5c_type_v_structure as K5c
    assert sp.simplify(K5c.chart_normalisation_residual()) == 0


def test_A_is_pure_gauge_under_rescaling_x():
    """★★ x → λx 에서 (A, a₁) → (λA, λa₁) 이라 **a_a = −A/a₁ 이 불변**이다.

    A 를 상수로 고정한 것은 물리적 제약이 아니라 **게이지 고정**이다.
    """
    from audit import k5c_type_v_structure as K5c
    g = K5c.gauge_rescaling()
    assert sp.simplify(g["invariant"]) == 0, g


# ═══════════════════════════════ 3. ★★ Ḣ 이중경로 — 정확한 대수 항등식
@pytest.mark.parametrize("n", [30, 60])
def test_raychaudhuri_gap_is_exactly_minus_friedmann_over_six(n):
    """★★ 공간 Einstein 의 Ḣ 와 Raychaudhuri 의 Ḣ 차이가 **정확히 −F/6**.

    두 진단자(공간식 잔차와 Friedmann 잔차)를 묶는 항등식이라, 어느 한쪽이
    틀리면 기계정밀도로 맞을 수 없다.  측정 1.8e−16.
    """
    r = C.raychaudhuri_gap(nsteps=n, t_end=0.3)
    assert r["residual"] < 1e-13, r
    assert r["gap_max"] > 1e-9, r          # 차이 자체는 0 이 아니다 (재는 게 있다)


# ═══════════════════════════════ 4. ★★ 대각 ansatz 의 유효 범위
def test_isotropic_and_axial_f0_are_admissible():
    """★ 필요한 것은 **등방성이 아니라 횡방향 반사대칭 둘**이다.

    p₁ 쌍극자는 q₁ ≠ 0 을 만들지만 (그건 G_{0̂1̂} 이 담는다) 비대각은 만들지 않는다.
    """
    rows = dict((n, (a, b)) for n, a, b in C.ansatz_admissibility())
    for name in ("등방", "쌍극자 p₁"):
        qt, po = rows[name]
        assert qt < 1e-15 and po < 1e-15, (name, qt, po)


def test_transverse_dipole_and_quadrupoles_are_not():
    """★★ **정직한 한계** — 이 f₀ 들은 대각 계량에 담기지 않는다 (1e−2 수준)."""
    rows = dict((n, (a, b)) for n, a, b in C.ansatz_admissibility())
    assert rows["쌍극자 p₂"][0] > 1e-2, rows
    assert rows["사중극자 p₁p₂"][1] > 1e-2, rows
    assert rows["사중극자 p₂p₃"][1] > 1e-2, rows


def test_admissible_matter_stays_admissible_through_the_evolution():
    """★★ 특성곡선이 반사대칭을 보존하므로 비대각이 **진화 내내** 0 (2.4e−17)."""
    r = C.offdiagonal_matter(nsteps=40, t_end=0.3)
    assert r["worst"] < 1e-14, r


def test_the_solver_refuses_inadmissible_f0_instead_of_failing_quietly():
    """★★ 검사가 없으면 비대각 성분을 조용히 버리고 **틀린 답**을 낸다 — 막는다."""
    s = C.solver_rejects_inadmissible_f0()
    assert s["isotropic_ok"] and s["quadrupole_rejected"], s


def test_the_guard_can_be_disabled_for_controls():
    """★ 대조군을 돌릴 수 있어야 하므로 `check_ansatz=None` 로 끌 수 있다."""
    r = C.evolve_coupled(nsteps=2, t_end=1e-4, f0=C.quadrupole_f0(i=0, j=1),
                         check_ansatz=None)
    assert np.abs(r["offdiag"]).max() > 1e-2, r["offdiag"]


# ═══════════════════════════════ 5. 게이지 불변성 (수치)
def test_rescaling_x_leaves_the_physics_alone():
    """★ λ=1.4 재척도에서 ρ, H, σ₁, q₁ 이 1e−9 이내로 같다 (횡방향 a 는 불변)."""
    g = C.gauge_rescaling_invariance(lam=1.4, nsteps=20, t_end=0.2)
    assert max(g["rho"], g["q1"], g["sigma1"], g["H"]) < 1e-7, g
    assert g["a_transverse"] < 1e-7, g
    assert g["a1_ratio"] < 1e-6, g         # a₁ 비가 λ 로 일정
