"""
H5-b · tilted 계층 부호의 **독립 오라클** 시험 — ∇_μ T^{μν} = 0.

★ 왜 이게 오라클인가: 식 (12) 의 (l,i)=(0,0) 과 (1,0) 은 **T^{μν} 변수만으로 닫힌다**
  (l=1 에서 J^(1)_a 계수 (1−n)=0 이고 (B) 는 (l−n)=(n−1)=0 이라 완전 소멸).
  즉 그 두 방정식이 에너지·운동량 보존이므로, 보존식을 독립 유도해 부호를 확정할 수 있다.

★ 통제군 설계: 같은 절차가 H1 에서 이미 확정된 SIGN_A=+1, SIGN_B=−1 을 **재생산**해야
  한다.  재생산 없이 새 부호를 채택하지 않는다 (통제군 시험이 이 파일의 핵심).

여기서 확정된 값 (잔차 1.3e−15, 유일성 마진 1.4e14 배):
    s_A = +1  s_B = −1        ← 통제군 (H1 일치)
    s_D = +1  s_E = −1        ← 가속도 u̇  (자유첨자 / 축약)
    s_Ω = +1                  ← 회전 ω
    s_divcon = +1  s_divfree = −1   ← 공간미분 (★ tilted 에서 살아난다)
"""
import numpy as np
import pytest

O = pytest.importorskip("audit.h5_tilted_conservation")

#: 확정된 부호 (이 파일이 회귀 잠금 역할을 한다)
EXPECTED = dict(s_A=+1.0, s_B=-1.0, s_D=+1.0, s_E=-1.0, s_Omega=+1.0,
                s_divcon=+1.0, s_divfree=-1.0)


@pytest.fixture(scope="module")
def solved():
    sol, resid, rel, M, b, ortho = O.solve_signs(nsamp=60, seed=0)
    return dict(sol=sol, resid=resid, rel=rel, M=M, b=b, ortho=ortho)


# ═══════════════════════════════ 오라클 구성의 자기검증
def test_tetrad_is_orthonormal(solved):
    """u·u=−1, u·E_A=0, E_A·E_B=δ — 사틀이 틀리면 나머지 전부가 무의미하다."""
    assert solved["ortho"] < 1e-13, solved["ortho"]


def test_scalar_spatial_gradient_closed_form():
    """★ tilted 에서 D_Aρ = γ v_A ρ̇ (순수 boost 사틀에서 E_A^t = γv_A).

    법선합동이면 D_a 가 죽지만 **tilted 는 죽지 않는다** — 균질성이 법선 합동의
    초곡면에 대한 것이고 tilted 관측자의 초곡면은 다르기 때문.
    """
    import sympy as sp
    for A in range(3):
        assert sp.simplify(O.EUP[A][0] - O.gam * O.v[A]) == 0, A


# ═══════════════════════════════ 부호 확정
def test_least_squares_gives_exact_plus_minus_one(solved):
    """★ 최소제곱해가 정확히 ±1 — 벗어나면 **항 구조가 틀렸다**는 신호.

    (실제로 공간미분 항을 빼고 돌렸을 때 s_A=+1.11, s_B=−0.88 로 어긋났고
     잔차가 0.40 남았다.  그 어긋남이 누락 항을 찾아준 것이다.)
    """
    for k, want in EXPECTED.items():
        got = solved["sol"][k]
        assert abs(got - want) < 1e-8, (k, got, want)


def test_residual_is_machine_zero(solved):
    """항 구조가 완전하면 잔차가 기계정밀도 (측정 1.3e−15)."""
    assert solved["rel"] < 1e-12, solved["rel"]


def test_control_group_reproduces_h1_signs(solved):
    """★★ 통제군: H1 의 정확구적 오라클과 **다른 방법**으로 SIGN_A, SIGN_B 재생산.

    두 독립 오라클(정확 구적 / 보존법칙)이 같은 부호를 주는 것이 신규 부호의 근거다.
    """
    assert abs(solved["sol"]["s_A"] - 1.0) < 1e-8
    assert abs(solved["sol"]["s_B"] + 1.0) < 1e-8
    from bianchi.matter import hierarchy as H
    assert H.SIGMA_SIGNS["A"] == pytest.approx(+1.0)
    assert H.SIGMA_SIGNS["B"] == pytest.approx(-1.0)


def test_uniqueness_margin_is_large(solved):
    """2^7=128 부호조합 전수에서 최적이 차선보다 10^10 배 이상 우월 (측정 1.4e14)."""
    (r0, s0), (r1, _), margin = O.uniqueness_margin(solved["M"], solved["b"])
    assert margin > 1e10, margin
    got = dict(zip(O.NAMES, s0.tolist()))
    assert got == EXPECTED, got


def test_signs_stable_across_seeds():
    """다른 난수 표본에서도 같은 부호 (표본 우연이 아님)."""
    for seed in (1, 2, 7):
        sol, _, rel, M, b, _ = O.solve_signs(nsamp=40, seed=seed)
        assert rel < 1e-11, (seed, rel)
        (_, s0), _, margin = O.uniqueness_margin(M, b)
        assert dict(zip(O.NAMES, s0.tolist())) == EXPECTED, seed
        assert margin > 1e9, (seed, margin)


# ═══════════════════════════════ 구조적 발견 (정직한 한계 포함)
def test_axis_aligned_tilt_cannot_activate_vorticity():
    """★ 단일축 tilt 는 ω ≡ 0 — (Ω) 항 시험에 **다축 tilt 가 필수**다.

    비등방 주축과 boost 방향이 정렬되면 D_au_b 의 반대칭부가 사라진다.
    이 사실을 모르고 단일축으로만 시험하면 s_Ω 을 확정했다고 착각한다.
    """
    rng = np.random.default_rng(7)
    r_single = O.evaluate(O._sample(rng, single_axis=True))
    rng = np.random.default_rng(7)
    r_multi = O.evaluate(O._sample(rng, single_axis=False))
    assert np.abs(r_single["omega"]).max() < 1e-14
    assert np.abs(r_multi["omega"]).max() > 1e-3
    # 가속도는 단일축에서도 켜진다 (u̇ 는 다축이 필요 없다)
    assert np.abs(r_single["udot"]).max() > 1e-3


def test_single_axis_system_is_rank_deficient():
    """단일축 표본만으로는 계의 rank 가 6/7 → s_Ω 미결정 (오라클 한계의 명시)."""
    _, _, _, M, _, _ = O.solve_signs(nsamp=40, seed=0, single_axis=True)
    assert np.linalg.matrix_rank(M, tol=1e-10) == 6


def test_spatial_divergence_terms_are_nonzero():
    """tilted 에서 D^aq_a, D^bπ_ba, D_a p 가 모두 살아 있다 (법선합동과의 차이)."""
    rng = np.random.default_rng(3)
    r = O.evaluate(O._sample(rng))
    assert abs(r["div_q"]) > 1e-3
    assert np.abs(r["div_pi"]).max() > 1e-3
    assert np.abs(r["grad_p"]).max() > 1e-3


def test_divergence_terms_carry_time_derivatives():
    """★★ 구현 설계를 바꾸는 발견: D 항이 **이웃 l 의 시간미분**을 품는다.

        ∂(D^a q_a)/∂q̇_A  →  v_A   (v→0)

    ⇒ tilted 계층은 명시적 RHS 가 아니라 **질량행렬 음함수 ODE** 다.
      `hierarchy_rhs` 처럼 dJ/dt 를 바로 반환하는 형태로 구현하면 틀린다.
    """
    import sympy as sp
    for A, name in enumerate(("q1", "q2", "q3")):
        c = sp.diff(O.DIV_Q, O.D1[name])
        # v→0 극한에서 계수 → v_A
        small = {O.v[0]: 1e-6, O.v[1]: 2e-6, O.v[2]: -3e-6}
        val = float(sp.N(c.subs(small).subs({O.v[k]: v for k, v in
                                             zip(range(3), (1e-6, 2e-6, -3e-6))})))
        want = (1e-6, 2e-6, -3e-6)[A]
        assert abs(val - want) < 1e-9 * max(abs(want), 1e-9) + 1e-12, (A, val, want)


def test_vanishing_tilt_kills_all_new_terms():
    """★ v→0 환원: 새 항 (ω, u̇, D) 이 모두 0 → 법선합동 계층으로 정확히 되돌아간다."""
    rng = np.random.default_rng(5)
    vals = O._sample(rng)
    n = len(O._BASE)
    for k, name in enumerate(O._BASE):
        if name in ("v1", "v2", "v3"):
            vals[k] = 0.0
            vals[n + k] = 0.0                     # v̇ = 0 도 함께
    r = O.evaluate(vals)
    assert np.abs(r["omega"]).max() < 1e-15
    assert np.abs(r["udot"]).max() < 1e-15
    assert abs(r["div_q"]) < 1e-15
    assert np.abs(r["div_pi"]).max() < 1e-15
    assert np.abs(r["grad_p"]).max() < 1e-15
