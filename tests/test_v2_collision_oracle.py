"""
V2 · **충돌항 오라클** — H3 이 "오라클이 없다" 고 정직하게 적어둔 자리를 메운다.

★ 설계 판정 (PLAN-V2): 몬테카를로가 아니라 **결정론적 각도구적**.
  MC 광자 10⁶개가 p₂ 를 9 % 로 재는 동안 격자 32점이 4e−15 로 잰다.
  이유는 세 겹이다 — 진동 배경에서 스텝을 늘려도 잡음이 바닥에 붙고(3.7e−4 정체),
  강한 감쇠 자체가 상관표본의 전제를 파괴하며(상관계수 0.10),
  잡음이 1/(a√N) 이라 우주론적 a~10⁻⁵ 에서 N~10¹⁶ 이 필요하다.

★ 순환 차단 — 오라클은 **두 가지를 인용하지 않고 재구성**한다:
  · 위상함수를 쌍극복사 |ê·ê′|² 에서 조립하고 규격화 상수까지 측정으로 정한다
  · PSTF 기저를 n_{⟨A_l⟩} = (−1)^l/(2l−1)!!·r^{l+1}∂_{A_l}(1/r) 로 기호미분한다

★★ 부수 수확: 편광을 합산하지 않은 판을 만들자 H3 의 미결 항목
  (`8/27 vs 4/15`) 이 닫혔다 — 정답은 **둘 다 아닌 16/45** 다.
"""
import inspect

import numpy as np
import pytest

from bianchi.matter import collision as C
from bianchi.matter import collision_oracle as CO
from bianchi.matter import hierarchy as H


# ═══════════════════════════════ 0. 독립성 (순환 논증 차단)
def test_oracle_does_not_import_the_thing_it_tests():
    """★ 회귀: 오라클이 `collision` 이나 `hierarchy.pstf` 를 쓰면 검증이 아니다.

    주석에 이름이 나오는 것은 허용하되 **실행되는 줄**만 검사한다.
    """
    import ast
    tree = ast.parse(inspect.getsource(CO))
    imported, called = set(), set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            imported.update(f"{node.module}.{a.name}" for a in node.names)
        elif isinstance(node, ast.Import):
            imported.update(a.name for a in node.names)
        elif isinstance(node, ast.Attribute):
            called.add(node.attr)
        elif isinstance(node, ast.Name):
            called.add(node.id)
    assert not any("collision" in m for m in imported), imported
    assert not any(m.endswith("hierarchy") for m in imported), imported
    assert "pstf" not in called, "PSTF 사영을 오라클이 재사용하면 순환이다"


def test_phase_normalisation_is_measured_not_quoted():
    """★ ∫P_raw dΩ = 8π/3 을 **측정**한다 ⇒ 3/16π 가 독립적으로 확인된다."""
    r = CO.phase_norm()
    assert r["rel_err"] < 1e-14, r


@pytest.mark.parametrize("l", [2, 3, 4])
def test_stf_basis_matches_the_projection_construction(l):
    """★ 기호미분 STF 와 `hierarchy.pstf` (최소제곱 사영) 가 일치 — 두 구성.

    측정: l=2 1.1e−16, l=3 3.3e−16, l=4 4.4e−16.
    """
    n, _ = CO.sphere_grid(6, 12)
    A = CO.stf_basis(l, n)
    letters = "ijkm"[:l]
    B = np.stack([H.pstf(np.einsum(",".join(letters) + "->" + "".join(letters),
                                   *([v] * l))) for v in n])
    assert np.abs(A - B).max() < 1e-13


# ═══════════════════════════════ 1. ★ 핵심 — λ_l 을 격자에서 잰다
@pytest.mark.parametrize("l,expected", [(0, 1.0), (1, 0.0), (2, 0.1),
                                        (3, 0.0), (4, 0.0)])
def test_eigenvalue_from_grid(l, expected):
    """★★ Legendre 도 다극 대수도 쓰지 않고 λ_l 을 재현 (1e−13).

    고유벡터 잔차도 함께 본다 — λ 만 맞고 고유함수가 아니면 의미가 없다.
    """
    r = CO.eigenvalue_from_grid(l)
    assert abs(r["lam"] - expected) < 1e-13, r
    assert r["residual"] < 1e-13, r


def test_grid_agrees_with_the_hierarchy_eigenvalues():
    """★ 오라클 ↔ H3 대조 (여기서 처음으로 두 쪽을 만나게 한다)."""
    for l in range(5):
        assert abs(CO.eigenvalue_from_grid(l)["lam"] - C.thomson_eigenvalue(l)) < 1e-13


def test_grid_converges_and_is_not_an_accident():
    """32점과 1152점이 같은 답 — 저차 구적이 맞는 게 우연이 아님을 확인."""
    a = CO.eigenvalue_from_grid(2, 4, 8)["lam"]
    b = CO.eigenvalue_from_grid(2, 24, 48)["lam"]
    assert abs(a - b) < 1e-13, (a, b)


@pytest.mark.parametrize("l", [0, 1, 2, 3, 4])
def test_operator_does_not_mix_multipoles(l):
    """★ 순수 l 이 아닌 f 에서도 M_l[Sf] = λ_l M_l[f] (1e−14).

    연산자가 l 을 섞으면 여기서 깨진다 — 고유값 시험보다 강하다.
    """
    assert CO.operator_residual(l) < 1e-13


def test_photon_number_conserved_on_the_grid():
    assert CO.photon_number_residual() < 1e-14


# ═══════════════════════════════ 2. 대조군 — 게이트가 죽어 있지 않다
@pytest.mark.parametrize("l", [2, 3])
def test_perturbing_the_phase_function_moves_the_eigenvalue(l):
    """★ 위상함수에 δ·P_l 을 더하면 λ_l 이 **선형으로 움직인다**.

    측정 l=2: δ=0.1 → 0.12 (Δ = 0.2δ);  l=3: δ=0.1 → 0.00857 (Δ = 0.0857δ).
    아무것이나 통과시키는 시험이 아님을 고정한다.
    """
    base = CO.perturbed_eigenvalue(l, 0.0)
    small = CO.perturbed_eigenvalue(l, 1e-3)
    big = CO.perturbed_eigenvalue(l, 1e-1)
    assert abs(small - base) > 1e-5
    assert abs(big - base) > 1e-3
    assert abs((big - base) / (small - base) - 100.0) < 1.0     # 선형


def test_wrong_lambda2_would_be_caught():
    """★ '만약 λ₂ 를 1/5 로 적었다면' 게이트가 깨지는가 (반사실 대조군)."""
    meas = CO.eigenvalue_from_grid(2)["lam"]
    assert abs(meas - 0.2) > 0.09                              # 0.1 과 0.2 를 구별


# ═══════════════════════════════ 3. 전체 사슬 (모멘트까지)
def test_odd_l_is_reported_before_being_gated():
    """★ 정직성: 등방 f₀ 는 홀수 l 이 **정확히 0** 이라 게이트가 0/0 이 된다.

    측정 |J₁|/ρ: 등방 2.3e−17 → 쌍극 7.5e−2.  0 인 칸에 게이트를 걸고
    "통과했다" 고 말하지 않기 위해 먼저 보고한다.
    """
    t = dict((l, (a, b)) for l, a, b in CO.odd_l_is_switched_on())
    assert t[1][0] < 1e-14 and t[3][0] < 1e-14                 # 등방: 0
    assert t[1][1] > 1e-2 and t[3][1] > 1e-3                   # 쌍극: 살아난다


@pytest.mark.parametrize("mass", [0.0, 1.0])
def test_full_chain_matches_the_hierarchy_collision_term(mass):
    """★★ 실제 분포에 산란을 걸고 모멘트를 재조립 → 계층의 C[J] 와 일치 (1e−14).

    이것이 V2 의 표적이었다: λ_l **값**이 아니라 그것을 **계층에 붙인 결과**.
    """
    r = CO.collision_chain_residual(mass=mass, l_max=4, i_max=2)
    assert max(r.values()) < 1e-13, r


def test_elastic_scattering_does_not_mix_i():
    """★ 계층의 가정 '탄성이라 i 에 무관' 을 **측정으로** 확인 (유질량에서도).

    측정: m=1, l=2 에서 i=0..3 모두 감쇠비 0.10000000000000.
    """
    vals = [v for _, v in CO.i_mixing_residual(mass=1.0, l=2, i_max=3)]
    assert max(abs(v - vals[0]) for v in vals) < 1e-13, vals
    assert abs(vals[0] - 0.1) < 1e-12


# ═══════════════════════════════ 4. ★★ V2d — 편광이 미결 항목을 닫는다
def test_polarized_block_has_the_sqrt6_structure():
    """★★ l=2 축소 블록 = [[1/10, √6/10], [√6/10, 3/5]], 차원 **2**.

    √6/10 = 0.24495 — CMB 편광 계층의 그 √6 이 **격자에서 저절로 나온다**.
    (우리는 √6 을 어디에도 적어 넣지 않았다.)
    """
    r = CO.l2_reduced_block()
    S = r["block"]
    assert r["dim"] == 2, r
    assert abs(S[0, 0] - 0.1) < 1e-12
    assert abs(S[1, 1] - 0.6) < 1e-12
    assert abs(S[0, 1] - np.sqrt(6) / 10) < 1e-6
    assert abs(S[1, 0] - np.sqrt(6) / 10) < 1e-6


def test_polarized_l2_eigenvalues_are_7_over_10_and_zero():
    ev = CO.l2_reduced_block()["eigenvalues"]
    assert abs(ev[0] - 0.7) < 1e-12, ev
    assert abs(ev[1]) < 1e-12, ev


def test_effective_quadrupole_damping_is_three_quarters():
    """★★ 준정적 유효 감쇠 = **3/4** (비편광 9/10 대비 비 = 6/5).

    Hu 의 강의노트 "polarization increases the viscosity of the fluid by a factor
    of 6/5" 와 일치 — 우리는 그 6/5 를 **측정으로** 얻었다.
    """
    r = CO.effective_quadrupole_damping()
    assert abs(r["effective"] - 0.75) < 1e-12, r
    assert abs(r["ratio"] - 1.2) < 1e-12, r


def test_viscosity_open_item_is_closed():
    """★★ H3 의 미결 (`8/27 vs 4/15`) → 정답은 **둘 다 아닌 16/45**.

        각구조 무시 (감쇠 1)   → 4/15  = 0.2667   ← 문헌에서 흔히 인용되던 값
        비편광    (감쇠 9/10)  → 8/27  = 0.2963   ← 우리 비편광 계층의 자기정합 값
        편광 포함 (감쇠 3/4)   → 16/45 = 0.3556   ← **물리적으로 옳은 값**
    """
    v = CO.shear_viscosity_coefficient()
    assert abs(v["unpolarised"] - 8 / 27) < 1e-12, v
    assert abs(v["polarised"] - 16 / 45) < 1e-12, v
    assert abs(v["no_angular_structure"] - 4 / 15) < 1e-15, v


def test_collision_module_now_exposes_the_polarised_value():
    """★ 측정 결과가 `collision.thomson_viscosity` 에 실제로 반영됐는지."""
    r = C.thomson_viscosity(1.0, 1.0, 0.0, polarised=True)
    assert abs(r["eta_times_nesigT_over_rho"] - 16 / 45) < 1e-12, r
    old = C.thomson_viscosity(1.0, 1.0, 0.0, include_thomson_9_10=True)
    assert abs(old["eta_times_nesigT_over_rho"] - 8 / 27) < 1e-12, old
