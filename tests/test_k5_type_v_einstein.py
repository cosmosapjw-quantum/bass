"""
K5a · **type V 의 Einstein 텐서를 계량에서 직접** — 곡률·구속을 인용하지 않는다.

K4c 까지 `3Σ^{ab}A_b = q^a` 와 type V 곡률을 **인용해** 썼다.  결합계를 세우기 전에
계량에서 직접 확정한다.

★ 이 파일이 고정하는 측정:
  · 자기검증 — 정규직교 불변기저 성분에 **x 가 하나도 남지 않는다** (공간균질)
  · Friedmann:  3H² = ρ + σ² + **3A²/a₁²**   (곡률항을 측정으로 얻었다)
  · ★★ Codazzi:  G_{0̂1̂} = 3σ₁·A/a₁,  그리고 프로젝트 규약과 **잔차 정확히 0**
  · 등방 극한이 open FRW (G₀₁ = 0, 곡률 −3A²/a²) ;  A→0 이 Bianchi I
  · ★ 부호 논쟁을 **교환자 계산으로** 끝냈다: [e₁,e₂] = −(A/a₁)e₂ ⇒ a_a = (−A/a₁,0,0)

★★ 그리고 구성적 결과: 운동량 구속을 **정확히** 만족하는 type V 구성을 찾았다
  (σ₁ = −0.02712 에서 잔차 0.0) — 자유흐름이 만든 q 를 기하가 그대로 담는다.
"""
import sympy as sp

from bianchi.matter import type_v as TV


# ═══════════════════════════════ 1. 자기검증
def test_frame_components_are_x_independent():
    """★★ 사영 성분에 x 가 남으면 계량·기저 설정이 틀린 것이다 (0개여야)."""
    from audit import k5_type_v_einstein as K5
    assert K5.homogeneity_residual() == []


# ═══════════════════════════════ 2. 구속식을 측정으로 확정
def test_friedmann_curvature_term_is_three_A_squared():
    """★ 3H² = ρ + σ² + **3A²/a₁²** — 곡률항을 계량에서 얻는다."""
    from audit import k5_type_v_einstein as K5
    e = K5.friedmann_in_H_sigma_A()
    assert sp.simplify(e + 3 * K5.A ** 2 / K5.a1 ** 2) == 0, e


def test_isotropic_limit_is_open_frw():
    """★ 등방 극한에서 G₀₁ = 0 이고 곡률항이 −3A²/a² (open FRW)."""
    from audit import k5_type_v_einstein as K5
    iso = K5.isotropic_limit()
    assert sp.simplify(iso["G01"]) == 0
    aa = sp.Function("a", positive=True)(K5.t)
    assert sp.simplify(iso["minus_3H2"] + 3 * K5.A ** 2 / aa ** 2) == 0


def test_A_zero_reduces_to_bianchi_I():
    """★ 대조군: A → 0 에서 K1 의 Friedmann (3H² = ρ + σ²) 재생산."""
    from audit import k5_type_v_einstein as K5
    assert sp.simplify(K5.type_I_limit()["minus_friedmann"]) == 0


# ═══════════════════════════════ 3. ★★ 부호를 교환자로 가른다
def test_structure_constant_sign_is_measured_not_argued():
    """★★ [e₁,e₂] = **−(A/a₁)e₂** — 우리 계량 e^{+2Ax} 의 a_a 는 **음수**다.

    이 부호를 몰라서 §Codazzi 측정이 프로젝트 규약과 어긋나 보였다.
    교환자를 직접 계산해 끝냈다.
    """
    from audit import k5_type_v_einstein as K5
    s = K5.structure_constants()
    assert sp.simplify(s["lam12"] + K5.A / K5.a1) == 0, s
    assert sp.simplify(s["lam13"] - s["lam12"]) == 0, s


def test_project_codazzi_convention_is_confirmed():
    """★★ 측정된 a_a 를 넣으면 `CODAZZI_G0A_SIGN = −1` 규약이 **잔차 0** 으로 맞다."""
    from audit import k5_type_v_einstein as K5
    r = K5.codazzi_normalisation()
    assert sp.simplify(r["residual"]) == 0, r


# ═══════════════════════════════ 4. 물리 단위 자기정합성
def test_flux_is_purely_along_the_type_V_axis():
    """★ 자발적 유속이 x 축 전용 (횡성분 1e−17) — type V 축과 일치."""
    r = TV.self_consistent_a_physical()
    assert r["transverse"] < 1e-14, r
    assert abs(r["q1"]) > 1e-3, r


def test_physical_units_replace_the_ambiguous_normalisation():
    """★ K4c 의 확장정규화 판은 규격화 인자가 불확실했다 (20배 차이로 보였다).

    물리 단위로 재면 |비| 가 O(1) 이다 — 정규화가 문제였지 물리가 아니었다.
    """
    r = TV.self_consistent_a_physical(t=0.35)
    assert 0.2 < abs(r["ratio"]) < 5.0, r


def test_sign_of_shear_sets_the_sign_of_consistency():
    """★ σ₁ 부호가 정합 여부의 부호를 정한다 (측정: σ₁>0 이면 비가 음수)."""
    pos = TV.self_consistent_a_physical(sigma_diag=(0.06, -0.02, -0.04))
    neg = TV.self_consistent_a_physical(sigma_diag=(-0.06, 0.02, 0.04))
    assert pos["ratio"] < 0 < neg["ratio"], (pos, neg)


# ═══════════════════════════════ 5. ★★ 구성적 — 정합 구성이 존재한다
def test_a_momentum_consistent_type_V_configuration_exists():
    """★★ 운동량 구속을 **정확히** 만족하는 σ₁ 이 존재한다 (잔차 0.0).

    측정: σ₁ = −0.02712 에서 q₁ = 0.04052 = 3σ₁a₁ (a₁ = −0.49799), 비 = 1.0.
    ★ 정직한 범위: **운동량 구속만**이다.  Friedmann 과 진화방정식까지 함께 푸는
      것은 K5 결합계의 몫이다.
    """
    r = TV.solve_self_consistent_shear()
    assert r["found"], r
    assert r["residual"] < 1e-12, r
    assert abs(r["ratio"] - 1.0) < 1e-6, r
    assert -0.05 < r["sigma1"] < 0.0, r
