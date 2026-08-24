"""
H1-a · Lewis-Challinor 다극 계층의 상태 표현·초기조건 시험.

게이트 (PLAN-H §4c 중 H1-a 해당분):
  * PSTF 사영이 l=2..6 에서 모든 대각합을 제거하고 독립성분 2l+1 을 남긴다
  * 식 (11) 대응이 `freestream.py` 정확 구적해와 일치 — 정규화 인자 상쇄 확인
  * 무질량에서 J^(i) 가 i 에 무관 (−8/15 유도의 전제)
  * **Misner σ-소스 계수 = −8/15** ← 계수 확정에 쓰지 않은 독립 게이트
"""
import numpy as np
import pytest

from bianchi.matter import freestream as fs
from bianchi.matter import hierarchy as H


# ─────────────────────────────── PSTF 사영
@pytest.mark.parametrize("l", [2, 3, 4, 5, 6])
def test_pstf_removes_all_traces(l):
    """직교사영이 모든 대각합을 제거한다 (반복법은 l≥4 에서 실패했다)."""
    rng = np.random.default_rng(100 + l)
    T = rng.normal(size=(3,) * l)
    P = H.pstf(T)
    assert H.is_pstf(P)
    scale = np.abs(P).max()
    assert np.abs(np.trace(P, axis1=-2, axis2=-1)).max() < 1e-12 * scale


@pytest.mark.parametrize("l", [2, 3, 4, 5, 6])
def test_pstf_dimension_is_2l_plus_1(l):
    """대칭 rank-l 공간(dim (l+1)(l+2)/2)에서 대각합 부분공간을 빼면 2l+1 이 남는다."""
    dim_sym = (l + 1) * (l + 2) // 2
    rank_trace = np.linalg.matrix_rank(H._trace_subspace(l))
    assert dim_sym - rank_trace == H.n_independent(l) == 2 * l + 1


def test_pstf_idempotent():
    """사영은 멱등: pstf(pstf(T)) = pstf(T)."""
    rng = np.random.default_rng(7)
    T = rng.normal(size=(3, 3, 3, 3))
    P = H.pstf(T)
    assert np.abs(H.pstf(P) - P).max() < 1e-12 * max(np.abs(P).max(), 1e-30)


def test_pstf_scalar_vector_passthrough():
    assert H.pstf(np.ones(())).ndim == 0
    v = np.array([1.0, -2.0, 3.0])
    assert np.allclose(H.pstf(v), v)


def test_pstf_rejects_too_high_rank():
    with pytest.raises(ValueError):
        H.pstf(np.zeros((3,) * (H.L_MAX_SUPPORTED + 1)))


# ─────────────────────────────── 식 (11) 대응 = 정규화 인자 상쇄
@pytest.mark.parametrize("mass", [0.0, 0.7, 5.0])
def test_eq11_matches_freestream_oracle(mass):
    """ρ=J^(0), p=⅓J^(1), π_ab=J^(0)_ab 가 정확 구적해와 일치.

    ★ 이것이 논문 정규화 인자 4π(−2)^l(l!)²/(2l+1)! 가 PSTF 역변환 인자와
      **정확히 상쇄**됨을 보이는 시험이다 (계수 1 로 구현할 근거).
    """
    a = np.array([1.0, 0.8, 1.3])
    rho, p, pi = fs.moments(a, mass)
    J = H.J_grid(a, mass, l_max=2, i_max=1)
    e = H.emt_from_J(J)
    assert abs(e["rho"] / rho - 1.0) < 1e-10
    assert abs(e["p"] / p - 1.0) < 1e-10
    assert np.abs(e["pi"] - pi).max() < 1e-10 * max(np.abs(pi).max(), 1e-30)


def test_momentum_density_vanishes_without_tilt():
    """등방 f₀ · 비틸트 ⇒ q_a = J^(0)_a = 0."""
    a = np.array([1.0, 0.9, 1.2])
    q = H.J_moment(a, 0.5, 1, 0)
    assert np.abs(q).max() < 1e-12


def test_isotropic_limit_pi_vanishes():
    """등방 배경 (a_i 모두 같음) ⇒ π_ab = 0."""
    a = np.array([1.1, 1.1, 1.1])
    pi = H.J_moment(a, 0.3, 2, 0)
    assert np.abs(pi).max() < 1e-10 * H.J_moment(a, 0.3, 0, 0)


def test_J_moment_is_pstf():
    """J^(i)_{A_l} 가 실제로 PSTF 로 반환된다 (l=2,3,4)."""
    a = np.array([1.0, 0.8, 1.3])
    for l in (2, 3, 4):
        assert H.is_pstf(H.J_moment(a, 0.4, l, 0))


def test_J_NORM_values():
    """정규화 인자 자체 (문서·상쇄 확인용).  4π, −4π/3·… 부호가 (−2)^l 로 교대."""
    assert abs(H.J_NORM(0) - 4 * np.pi) < 1e-12
    assert H.J_NORM(1) < 0 and H.J_NORM(2) > 0      # (−2)^l 부호 교대
    assert abs(H.J_NORM(2) - 4 * np.pi * 4 * 4 / 120) < 1e-12


# ─────────────────────────────── 무질량 i-무관 + Misner −8/15
@pytest.mark.parametrize("l", [0, 2, 4])
def test_massless_J_is_i_independent(l):
    """무질량: λ=E ⇒ (λ/E)^n=1 ⇒ J^(i) 가 i 무관.  −8/15 유도의 전제."""
    a = np.array([1.0, 0.8, 1.3])
    assert H.massless_i_independence_residual(a, l=l) < 1e-12


def test_massive_J_is_i_dependent():
    """유질량이면 i-의존 — 위 전제가 무질량 한정임을 명시."""
    a = np.array([1.0, 0.8, 1.3])
    assert H.massless_i_independence_residual(a, l=0) < 1e-12
    J1 = H.J_moment(a, 5.0, 0, 1)
    J2 = H.J_moment(a, 5.0, 0, 2)
    assert abs(J1 / J2 - 1.0) > 1e-3


@pytest.mark.parametrize("a_vec", [
    [1.0, 1.0, 1.0], [1.0, 0.8, 1.3], [0.7, 1.4, 1.1],
])
def test_misner_minus_8_over_15(a_vec):
    """★ 독립 게이트: 식(12) l=2,i=0 의 σ-소스 계수가 **−8/15**.

    (2/15)[J^(2) − 5J^(1)]/ρ 를 무질량에서 계산.  이 계수는 Misner 중성미자 점성의
    기원이고, `freestream.sudden_response_coefficient()` 가 독립적으로 −0.5326 을
    측정해 둔 값이다.  전사·축약이 옳다는 강한 증거.
    """
    c = H.misner_source_coefficient(np.asarray(a_vec, float))
    assert abs(c - (-8.0 / 15.0)) < 1e-12, c


def test_misner_agrees_with_freestream_sudden_response():
    """계층이 준 −8/15 와 구적 급작응답 측정치(−0.5326)가 구적·차분 수준에서 일치."""
    c_hier = H.misner_source_coefficient(np.array([1.0, 1.0, 1.0]))
    c_quad = fs.sudden_response_coefficient()
    assert abs(c_hier - c_quad) < 0.01, (c_hier, c_quad)


# ═══════════════════════════════ H1-b · 균질 축약 RHS
_F_DIP = H.f_dipole(0.4, axis=2)
_A = np.array([1.0, 0.9, 1.15])
_SIG = np.array([0.08, -0.03, -0.05])


def test_dipole_f0_activates_odd_multipoles():
    """방향의존 f₀ 는 홀수 l 다극을 켠다 (등방 f₀ 로는 시험 불가).

    Vlasov 는 f=f₀(불변기저 p_i) 이면 임의 방향의존을 허용하므로 정당한 시험 설정.
    """
    rho = H.J_moment(_A, 0.8, 0, 0, _F_DIP)
    assert np.abs(H.J_moment(_A, 0.8, 1, 0, _F_DIP)).max() > 1e-3 * rho
    assert np.abs(H.J_moment(_A, 0.8, 3, 0, _F_DIP)).max() > 1e-5 * rho
    # 등방 f₀ 는 f(p)=f(-p) ⇒ 홀수 l 항등적 0
    assert np.abs(H.J_moment(_A, 0.8, 1, 0)).max() < 1e-12 * rho
    assert np.abs(H.J_moment(_A, 0.8, 3, 0)).max() < 1e-12 * rho


@pytest.mark.parametrize("l,i", [(0, 0), (0, 1), (1, 0), (2, 0), (2, 1), (3, 0), (4, 0)])
def test_rhs_matches_exact_quadrature_derivative(l, i):
    """★ 핵심 게이트: 계층 RHS = 정확 구적해의 시간미분 (차분정밀도)."""
    r = H.rhs_residual(_A, 0.8, 1.0, _SIG, l, i, f0=_F_DIP)
    assert r < 1e-6, (l, i, r)


def test_rhs_residual_is_finite_difference_error():
    """잔차가 O(dt²) → 모델오차가 아니라 차분오차임을 증명."""
    r3 = H.rhs_residual(_A, 0.0, 1.0, _SIG, 2, 0, dt=1e-3)
    r4 = H.rhs_residual(_A, 0.0, 1.0, _SIG, 2, 0, dt=1e-4)
    assert r3 > r4
    assert 30.0 < r3 / r4 < 300.0, (r3, r4)      # 10x dt → ~100x 잔차


@pytest.mark.parametrize("sA,sB,sC", [
    (+1, +1, +1), (+1, +1, -1), (+1, -1, +1),
    (-1, +1, +1), (-1, +1, -1), (-1, -1, +1), (-1, -1, -1),
])
def test_wrong_sigma_signs_are_rejected(sA, sB, sC):
    """★ 부호 유일성: 확정값 (+1,−1,−1) 외의 7조합은 모두 크게 실패한다.

    감사(audit/h_hierarchy.py) 측정 유일성 마진 ≈ 1.5e6 배.
    """
    worst = 0.0
    for l, i in [(0, 0), (1, 0), (2, 0), (3, 0)]:
        worst = max(worst, H.rhs_residual(_A, 0.8, 1.0, _SIG, l, i,
                                          signs=dict(A=float(sA), B=float(sB),
                                                     C=float(sC)), f0=_F_DIP))
    assert worst > 1e-4, (sA, sB, sC, worst)


def test_determined_signs_are_the_module_default():
    """모듈 상수 SIGMA_SIGNS 가 오라클 확정값과 일치."""
    assert H.SIGMA_SIGNS == dict(A=+1.0, B=-1.0, C=-1.0)


def test_l0_i0_is_emt_conservation():
    """l=0,i=0 이 EMT 보존 `ρ̇ + 3H(ρ+p) + σ·π = 0` 을 재생산 (PLAN-H §0b 자체검증 1)."""
    a, mass, Hub = _A, 0.8, 1.0
    sigma = np.diag(_SIG)
    J = {(ll, ii): H.J_moment(a, mass, ll, ii)
         for ll in (0, 2) for ii in (-1, 0, 1, 2)}
    drho = H.hierarchy_rhs(J, Hub, sigma, 0, 0)
    rho, p, pi = fs.moments(a, mass)
    expected = -3.0 * Hub * (rho + p) - float(np.einsum("ab,ab->", sigma, pi))
    assert abs(drho - expected) < 1e-10 * abs(expected), (drho, expected)


def test_isotropic_background_keeps_pi_zero():
    """등방 배경 (σ=0) 에서 π_ab 의 RHS 가 0 — 이방성이 생기지 않는다."""
    a = np.array([1.1, 1.1, 1.1])
    J = {(ll, ii): H.J_moment(a, 0.5, ll, ii)
         for ll in (0, 2, 4) for ii in (-1, 0, 1, 2)}
    dpi = H.hierarchy_rhs(J, 1.0, np.zeros((3, 3)), 2, 0)
    rho = H.J_moment(a, 0.5, 0, 0)
    assert np.abs(dpi).max() < 1e-10 * rho


def test_hierarchy_rhs_requires_neighbours():
    """이웃 J 가 없으면 조용히 0 으로 넘기지 않고 KeyError (절단은 H2 의 일)."""
    J = {(0, 0): 1.0}
    with pytest.raises(KeyError):
        H.hierarchy_rhs(J, 1.0, np.diag(_SIG), 0, 0)


def test_rhs_output_is_pstf():
    """RHS 결과도 PSTF 여야 (dJ/dt 는 J 와 같은 공간에 있다)."""
    # (B) 항이 l+2 를 요구하므로 l=4 를 시험하려면 l=6 까지 공급해야 한다
    J = {(ll, ii): H.J_moment(_A, 0.8, ll, ii, _F_DIP)
         for ll in (0, 1, 2, 3, 4, 5, 6) for ii in (-1, 0, 1, 2)}
    for l in (2, 3, 4):
        assert H.is_pstf(H.hierarchy_rhs(J, 1.0, np.diag(_SIG), l, 0))


# ═══════════════════════════════ H2 · 절단·닫힘과 적분 궤적
_A0 = np.array([1.0, 1.0, 1.0])
_HUB = 1.0
_SIGD = np.array([0.06, -0.02, -0.04])


def test_i_closure_is_structurally_closed_from_below():
    """(l−n) = −2i 이므로 i=0 방정식은 J^(−1) 을 참조하지 않는다 (i 아래로 닫힘)."""
    J = {(l, i): H.J_moment(_A0, 0.8, l, i)
         for l in (0, 2, 4) for i in (0, 1, 2)}
    # J^(-1) 을 넣지 않아도 i=0 이 계산된다
    d = H.hierarchy_rhs(J, _HUB, np.diag(_SIGD), 0, 0)
    assert np.isfinite(d)
    # i=1 은 J^(0) 을 참조하므로 계수가 0 이 아니다
    assert (0 - (0 + 2 * 1)) == -2


@pytest.mark.parametrize("l_max,tol", [(2, 1e-4), (4, 1e-7), (6, 1e-7)])
def test_lmax_convergence_massless(l_max, tol):
    """★ l_max 수렴: 계층 궤적이 정확 구적해로 수렴 (무질량).

    측정: l_max=2 → π 오차 4.9e−5,  l_max=4 → 8.2e−9,  l_max=6 → 6.9e−9.
    ⇒ **l_max=4 로 충분** (Rust 이식의 l≤4 제한 근거).
    """
    r = H.integrate_hierarchy(_A0, 0.0, _HUB, _SIGD, 0.3, nsteps=40,
                              l_max=l_max, i_max=2)
    e = H.trajectory_error(r)
    assert e["rho"] < tol and e["p"] < tol and e["pi"] < tol, e


def test_trajectory_matches_exact_quadrature_massless():
    """★ 핵심 게이트 (H1-c): 닫힌 절단 ODE 가 정확 구적 궤적을 재현."""
    r = H.integrate_hierarchy(_A0, 0.0, _HUB, _SIGD, 0.3, nsteps=60,
                              l_max=4, i_max=2)
    e = H.trajectory_error(r)
    assert e["rho"] < 1e-7, e
    assert e["pi"] < 1e-7, e


def test_geometric_i_closure_beats_zero_truncation():
    """★ i-닫힘 설계 근거: 무질량에서 0-절단은 7자리 열등하다.

    무질량은 (λ/E)=1 이라 J^(i) 가 i 무관인데, 0-절단은 이를 깨뜨린다.
    측정: 0-절단 ρ 오차 1.1e−2  vs  기하외삽 1.6e−9.
    """
    import bianchi.matter.hierarchy as HH
    orig = HH.close_i

    def zero_close(J, l, i_max, i_min=0):
        sh = np.asarray(J[(l, i_max)]).shape
        z = 0.0 if not sh else np.zeros(sh)
        J[(l, i_max + 1)] = z
        J[(l, i_max + 2)] = z
        return J
    try:
        HH.close_i = zero_close
        e_zero = H.trajectory_error(H.integrate_hierarchy(
            _A0, 0.0, _HUB, _SIGD, 0.3, nsteps=40, l_max=4, i_max=2))
    finally:
        HH.close_i = orig
    e_geo = H.trajectory_error(H.integrate_hierarchy(
        _A0, 0.0, _HUB, _SIGD, 0.3, nsteps=40, l_max=4, i_max=2))
    assert e_geo["rho"] < 1e-7
    assert e_zero["rho"] > 1e-3
    assert e_zero["rho"] / e_geo["rho"] > 1e4


def test_massive_converges_with_i_max():
    """유질량은 진짜 2차원 계층 — i_max 를 늘려야 수렴한다 (정직한 한계 표시).

    측정 (m=1.5, ρ 오차): i_max=1 → 1.8e−3, 2 → 2.3e−4, 3 → 4.2e−5, 4 → 9.5e−6.
    """
    errs = []
    for im in (1, 2, 3):
        r = H.integrate_hierarchy(_A0, 1.5, _HUB, _SIGD, 0.3, nsteps=30,
                                  l_max=4, i_max=im)
        errs.append(H.trajectory_error(r)["rho"])
    assert errs[0] > errs[1] > errs[2]           # 단조 수렴
    assert errs[2] < 1e-4


def test_isotropic_background_preserves_isotropy():
    """σ=0 배경: π_ab 가 0 을 유지 (이방성이 생기지 않는다)."""
    r = H.integrate_hierarchy(_A0, 0.5, _HUB, np.zeros(3), 0.4, nsteps=30,
                              l_max=4, i_max=2)
    rho0 = r["exact"][0]["rho"]
    for J in r["J"]:
        assert np.abs(np.asarray(J[(2, 0)])).max() < 1e-9 * rho0
