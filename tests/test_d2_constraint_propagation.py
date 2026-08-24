"""
D2 · **구속 사영과 감시** — 위반은 어떻게 자라고, 투영은 무엇을 고치는가.

K5b §7 은 "Codazzi 를 깨면 Friedmann 이 따라 자란다" 를 **관찰만** 했다.
`bianchi/constraints.py` 는 class B 증폭률 `4(q + Σ₊ − 1)` 을 **인용**해 두었을 뿐
어디에서도 재지 않았고, 일반 차트의 `amplification_rate` 는 0.0 을 돌려준다.

★ 이 파일이 고정하는 측정:
  · ★★ 전파 법칙을 계량에서 **유도**했다 (E^{μν} ≡ G^{μν} − T^{μν}, ∇_μE^{μν} = 0):
        Ḟ = −3H·F − 2(A/a₁)·C
        Ċ = −(4H + σ₁)·C           ← **삼각행렬** (F 는 C 로 되먹임하지 않는다)
    닫힌형 C ∝ 1/(a₁²a₂a₃),  F 의 제차해 ∝ 1/V — 대입 잔차 0
  · ★★ 같은 Φ 를 **섭동 실험으로 측정**해 대조: 상대차가 ε 에 **정비례**
    (ε=4e−3/2e−3/1e−3 → 8.60/4.30/2.15 e−05) — 남은 것은 O(ε) 비선형뿐
  · ★★ (F, C) 가 **닫힌 선형계**인가: 셋째 섭동을 Φ 로 예측해 1.8e−05 로 맞음
  · Φ_CF (F→C 되먹임) 측정값 2.6e−11 — 유도가 예측한 0
  · ★★ 확장정규화로 옮기면 d ln𝒞/dτ = **2(q + Σ₊ − 1)**.  `constraints.py` 가
    인용한 `4(q + Σ₊ − 1)` 은 class B 잔차가 **2차식**이라 정확히 두 배다.
  · ★★ 증폭은 **방향에 달렸다**: 팽창이면 감쇠 (C 0.157배), 수축이면 증폭 (23.3배).
    닫힌형이 두 경우 다 1e−7 이하로 맞는다.
  · 투영 — 정합 자료에 무동작 (4.3e−10), 깨진 자료 복원 (2.1e−03 → 3.7e−16, 2차 수렴)

★ 반증 기록: 처음엔 Φ_FC 의 **부호**가 반대였다 (상대차 6.8e−02, 대각 성분만 맞음).
  유도를 반변 E^{μν} 로 했는데 감시자는 공변 기준이고 η^{0̂0̂}η^{1̂1̂} = −1 이다.
  부호를 논쟁 대신 **지표 올리기로** 정했다 (`mixed_index_sign`).
"""
import numpy as np
import pytest
import sympy as sp

from bianchi.matter import type_v_constraints as D2


# ═══════════════════════════════ 1. 전파 법칙을 계량에서 유도
def test_propagation_equations_are_spatially_homogeneous():
    """★ 자기검증 — ∇_μE^{μν} 에 x 가 남으면 계량·틀 설정이 틀린 것이다."""
    from audit import d2_constraint_propagation as P
    assert P.homogeneity_residual() == []


def test_transverse_divergence_components_vanish_identically():
    """★ (∇E)² = (∇E)³ = 0 — 전파계가 (F, C) 둘로 **닫힌다**."""
    from audit import d2_constraint_propagation as P
    d = P.divergence_of_E()
    assert sp.simplify(d[2]) == 0 and sp.simplify(d[3]) == 0, d


def test_propagation_matrix_is_the_derived_one():
    """★★ M = [[−3H, −2A/a₁], [0, −(4H+σ₁)]] — 잔차 0."""
    from audit import d2_constraint_propagation as P
    r = P.readable_matrix()
    assert sp.simplify(r["residual"]) == sp.zeros(2, 2), r["residual"]


def test_friedmann_does_not_feed_back_into_codazzi():
    """★★ M[1,0] = 0 — 삼각행렬이라 고윳값을 대각에서 바로 읽는다."""
    from audit import d2_constraint_propagation as P
    assert sp.simplify(P.no_feedback_into_codazzi()) == 0


def test_closed_forms_satisfy_the_system_by_substitution():
    """★★ 풀이를 믿지 않고 **대입**해 확인 — C ∝ 1/(a₁²a₂a₃), F_hom ∝ 1/V."""
    from audit import d2_constraint_propagation as P
    r = P.closed_form_residual()
    assert sp.simplify(r["codazzi"]) == 0, r
    assert sp.simplify(r["friedmann_homogeneous"]) == 0, r


def test_the_sign_comes_from_raising_indices_not_from_argument():
    """★★ **반증 기록** — η^{0̂0̂}η^{1̂1̂} = −1 이라 F←C 부호가 뒤집힌다.

    이걸 놓쳐 처음엔 Φ_FC 만 부호가 반대였다 (대각은 맞았다).
    """
    from audit import d2_constraint_propagation as P
    assert P.mixed_index_sign() == -1
    assert P.diagonal_index_sign() == +1


# ═══════════════════════════════ 2. 차트 언어로 — 인용식을 유도로 바꾼다
def test_normalised_codazzi_rate_is_two_q_plus_sigma_minus_one():
    """★★ d ln𝒞/dτ = **2(q + Σ₊ − 1)** — 물리 단위 유도에서 나온다 (잔차 0)."""
    from audit import d2_constraint_propagation as P
    assert sp.simplify(P.normalised_codazzi_rate()["residual"]) == 0


def test_cited_class_b_rate_is_twice_ours_because_it_is_quadratic():
    """★ `constraints.py` 의 `4(q + Σ₊ − 1)` 은 잔차가 **2차식**이라 두 배다.

    class_b.codazzi = Σ̃Ñ − Δ² − Σ₊²Ã 는 선형 Codazzi 자료의 2차형식이다.
    """
    from audit import d2_constraint_propagation as P
    assert sp.simplify(P.class_b_factor_of_two()["residual"]) == 0


# ═══════════════════════════════ 3. ★★ 측정 vs 유도
def test_the_residual_pair_is_a_closed_linear_system():
    """★★ **반증 가능한 검사** — 셋째 섭동을 Φ 로 예측해 맞는가 (1.8e−05).

    (F, C) 밖의 자유도가 끼어들면 예측이 어긋난다.
    """
    c = D2.closure_prediction(eps=2e-3, nsteps=40, t_end=0.3)
    assert c["rel"] < 1e-3, c["rel"]


def test_response_is_linear_in_the_perturbation():
    """★ 섭동을 2배로 하면 응답도 2배 (8.7e−04)."""
    assert D2.linearity_check(eps=2e-3, ratio=2.0, nsteps=40, t_end=0.3) < 1e-2


@pytest.mark.parametrize("eps", [2e-3, 1e-3])
def test_measured_fundamental_matrix_matches_the_derived_closed_form(eps):
    """★★ **두 경로** — 섭동으로 잰 Φ vs 계량에서 유도한 닫힌형 Φ.

    남은 차이는 O(ε) 비선형이다 (ε 를 반으로 하면 절반이 된다).
    """
    r = D2.propagation_law_residual(eps=eps, nsteps=40, t_end=0.3)
    assert r["rel"] < 60.0 * eps, r["rel"]
    assert r["no_feedback"] < 1e-8, r["no_feedback"]


def test_measured_no_feedback_confirms_the_triangular_structure():
    """★★ Φ_CF 측정값 2.6e−11 — 유도가 예측한 정확한 0 과 맞는다."""
    r = D2.propagation_law_residual(eps=2e-3, nsteps=40, t_end=0.3)
    assert r["no_feedback"] < 1e-8, r


# ═══════════════════════════════ 4. ★★ 증폭은 방향에 달렸다
def test_violations_decay_while_expanding():
    """★★ 팽창이면 C 가 1/(V a₁) 로 **줄어든다** — 닫힌형 잔차 1e−8."""
    g = D2.violation_growth(hsign=+1.0, nsteps=40, t_end=0.15)
    assert g["V_ratio"] > 3.0, g["V_ratio"]
    assert g["C_ratio"] < 0.25, g["C_ratio"]
    assert g["law_residual"] < 1e-6, g["law_residual"]


def test_violations_amplify_while_contracting():
    """★★ 수축이면 **자란다** (23.3배) — 같은 닫힌형이 두 방향 다 맞는다.

    `constraints.py` 의 "구속은 지수 증폭한다" 는 서술은 **방향에 달렸다**.
    """
    g = D2.violation_growth(hsign=-1.0, nsteps=40, t_end=0.08)
    assert g["V_ratio"] < 0.2, g["V_ratio"]
    assert g["C_ratio"] > 10.0, g["C_ratio"]
    assert g["law_residual"] < 1e-5, g["law_residual"]


# ═══════════════════════════════ 5. 투영기
def test_analytic_jacobian_matches_central_differences():
    """★ 손대수 금지 — ∂(F,C)/∂h 를 중심차분과 대조 (1.6e−09)."""
    assert D2.jacobian_check() < 1e-6


def test_projection_restores_broken_data_and_does_nothing_to_good_data():
    """★★ 깨진 자료 2.1e−03 → 3.7e−16, 정합 자료엔 **정확히 무동작**."""
    r = D2.projection_report()
    assert r["broken_before"] > 1e-4, r
    assert r["broken_after"] < 1e-14, r
    assert r["restored"] < 1e-14, r
    assert r["noop"] == 0.0, r


def test_projection_is_minimal_norm():
    """★ 보정이 J 의 행공간 안에 있다 (영공간 성분 6.5e−10)."""
    assert D2.projection_is_minimal_norm() < 1e-6


def test_gauss_newton_converges_quadratically():
    """★ F 의 H² 항이 비선형이라 1회로는 안 된다 — 2.1e−03 → 5.3e−05 → 6.9e−10."""
    seq = D2.iteration_convergence()
    assert seq[0] > 1e-4, seq
    assert seq[2] < 1e-8, seq
    assert seq[3] < 1e-14, seq
    for a, b in zip(seq[:3], seq[1:4]):
        assert b < a, seq


# ═══════════════════════════════ 6. ★★ 투영이 무엇을 고치고 무엇을 못 고치는가
def test_projection_controls_the_amplification_in_collapse():
    """★★ 증폭 구간(수축)에서 투영이 실제로 잡는다: 5.8e−04 → 3.6e−17."""
    r = D2.projection_controls_growth(nsteps=40, t_end=0.08, hsign=-1.0)
    assert r["off_C"] > 1e-4, r
    assert r["on_C"] < 1e-14, r
    assert r["on_F"] < 1e-14 < r["off_F"], r


def test_projection_does_not_disturb_a_consistent_run():
    """★ 대조군 — 이미 정합한 자료에 매 스텝 투영해도 궤적이 4.3e−10 이내로 같다."""
    r = D2.projection_is_harmless_on_good_data(nsteps=40, t_end=0.15)
    assert r["a"] < 1e-8, r
    assert r["rho"] < 1e-7, r


def test_projection_lands_near_but_not_on_the_consistent_solution():
    """★★ **정직한 몫** — 투영은 구속을 되찾지만 같은 해로 돌려놓지는 않는다.

    측정: 구속 5.5e−17 이지만 a_i 가 정합 궤적과 7.2e−04 (σ₁ 차 3.7e−05) 다르다.
    투영은 **적분 오차를 지우는 도구**지 잘못된 초기자료를 고쳐 주지 않는다.
    """
    r = D2.projection_moves_the_solution(nsteps=40, t_end=0.15)
    assert r["constraint"] < 1e-14, r
    assert r["a_distance"] > 1e-5, r
