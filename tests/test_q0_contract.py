"""
Q0 · **계약 동결** 게이트 (76차).

이 시험이 지키는 것: 규약이 조용히 바뀌지 않는다.
  · 기존 `bianchi.conventions` 와의 패리티 4종 (회전·Levi-Civita·W·Thomson k_l)
  · "벗는 것" 5종 각각에 **대응 시험 ID 가 존재**한다 (미구현이면 xfail 로 등록)
  · 오차예산이 계획서 §6 의 결정적 임계를 담고 있다
  · ★ 시험은 임계를 스스로 정하지 않는다 — `contract.budget()` 로만 읽는다
"""
import pytest

from bianchi.q import contract as C


def test_conventions_parity_with_existing_core():
    """★ 규약 패리티 4종 — 하나라도 깨지면 Q 티어 전체가 무효."""
    res = C.validate_contract()
    assert all(res.values()), res


def test_thomson_eigenvalues_are_recomputed_not_trusted():
    """k_l 하드코딩 금지 원형: 수치 구적 재계산이 계약값과 일치."""
    assert C._thomson_parity()
    assert C.CONVENTIONS["thomson_eigenvalues"] == (1.0, 0.0, 0.1, 0.0)


def test_no_approximation_claims_have_test_ids():
    """§1 '벗는 것' 5종 각각에 시험 ID 가 붙어 있다 (주장 = 시험 가능해야 한다)."""
    assert len(C.NO_APPROXIMATION) == 5
    for name, spec in C.NO_APPROXIMATION.items():
        assert spec["test"].startswith("tests/"), (name, spec)
        assert "::" in spec["test"], (name, spec)


def test_discretization_axes_declare_expected_orders():
    """§1 '남는 것' 축이 기대 수렴차수를 선언 (Q17 이 이걸 잰다).

    ★ 82차: Mode B 두 축 (modeb_angular, modeb_range) 추가 등재.  둘 다 지수
    수렴이라 `order="spectral"` + `decay_rate` 로 적는다."""
    base = {"angular", "radial", "interp", "time", "splitting"}
    assert base <= set(C.DISCRETIZATION)
    assert {"modeb_angular", "modeb_range"} <= set(C.DISCRETIZATION)
    assert C.DISCRETIZATION["splitting"]["order"] == 2.0
    assert C.DISCRETIZATION["time"]["order"] == 4.0


def test_error_budget_covers_every_pr():
    """Q1–Q18 전부 예산이 있다 (예산 없는 PR = 게이트 없는 PR)."""
    need = ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q7b", "Q8", "Q9",
            "Q10", "Q11", "Q12", "Q13", "Q14", "Q15", "Q16", "Q17", "Q18"]
    assert set(need) <= set(C.ERROR_BUDGET)


def test_budget_rejects_unknown_threshold():
    """계약에 없는 임계를 시험이 몰래 쓰지 못한다."""
    with pytest.raises(KeyError, match="계약에 없는 임계"):
        C.budget("Q7", "no_such_gate")


def test_measured_anchors_are_frozen():
    """계획을 강제한 실측값 박제 — 이 숫자가 바뀌면 계획의 근거가 바뀐 것."""
    m = C.MEASURED
    assert m["i2b_grid_exponent"] == 0.234
    assert m["i2b_pstf_lmax8"] == -0.258          # ★ 부호 반전
    assert m["i2b_grid_exponent"] * m["i2b_pstf_lmax8"] < 0
    assert m["i2c_lna_wall"] == 300.0


def test_units_declare_collision_rate_matching_b2b_spec():
    """ν 의 무차원화가 B2b 통합양식 §6 과 같은 정의인지."""
    assert C.UNITS["collision_rate"] == "nu_tau = sigma_T n_e c / H"
    assert C.UNITS["dtau_dt"] == "H"
