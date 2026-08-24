"""
H5-e3 · tilted 계층 **시간적분** 검증 — M(v)·J̇ = F 를 닫고 RK4.

★ 종단 게이트는 H2 가 법선합동에 쓴 것과 같다: 적분 궤적을 **정확 구적**과 대조.
  (초기조건도 정확 구적이므로, 오차는 순전히 닫힘 + 시간적분에서 온다.)

이 파일이 고정하는 측정 결과 3가지:
  1. **dt 는 이미 수렴**했다 — nsteps 10→80 에서 오차 불변 (RK4 가 충분).
  2. **지배 오차는 i-닫힘**이다 — i_max 1→4 에서 5.3e−4 → 6.3e−6.
     ★ 법선합동(H2)에서는 l_max 가 한계였는데, tilted 는 (div-free) 가
       (l,i) → (l−1, i+1) 로 결합해 **i 를 능동적으로 퍼뜨리기** 때문이다.
  3. 오차가 **tilt 크기와 함께 ~v²** 로 커진다 (측정 지수 1.79).
     v=0 에서는 1.6e−7 (법선합동 수준) 로 떨어진다.
"""
import numpy as np
import pytest

from bianchi.matter import tilted_integrate as TI


@pytest.fixture(scope="module")
def bg():
    return TI.Background()


# ★ L3 이후: 아래 기전 시험들은 **대조군** (격자 밖 J̇ 를 버리는 옛 거동) 을 명시한다.
#   기본값은 J̇ 닫힘이라 이 오차 채널이 사라져 있다 — 그게 L3 의 수확이다.
CTRL = dict(mode="frozen", jdot_closure=False)


# ═══════════════════════════════ 닫힘 근거 (가정하지 않고 측정)
@pytest.mark.parametrize("l", [0, 2, 3])
def test_massless_i_independence_survives_boost(l):
    """★ `close_i` 의 근거가 boost 후에도 성립 — 무질량은 J′^(i) 가 i-무관.

    무질량은 E′ = λ′ 이라 (λ′/E′)^n ≡ 1 이므로 n(=i) 의존성이 사라진다.
    유도로 그렇게 보이지만 **측정으로 확인**한다 (측정: 1.0000).
    """
    r = TI.i_independence_ratios(0.0, l=l)
    assert all(abs(x - 1.0) < 1e-10 for x in r), r


@pytest.mark.parametrize("mass", [0.5, 2.0])
def test_massive_i_ratios_decay_monotonically(mass):
    """유질량은 기하급수 감쇠 (close_i 의 외삽 대상).  m=2, l=0: 0.70, 0.53, 0.42."""
    r = TI.i_independence_ratios(mass, l=0)
    assert all(b < a for a, b in zip([1.0] + r, r)), r
    assert r[-1] < 1.0


def test_l_plus_one_truncation_is_larger_than_sigma():
    """★ tilted 의 새 l+1 결합 절단오차가 기존 σ 의 l+2 절단보다 **약 3배** 크다.

    조용히 쓰지 않고 정량화한다: 같은 정확도를 원하면 tilted 는 l_max 를 더 올려야 한다.
    (측정 l=2: 2.10e−4 vs 7.32e−5.)
    """
    r = TI.truncation_error(l=2)
    assert r["exact"] < 1e-8
    assert r["trunc_l_plus_1"] > 1e-5
    assert 2.0 < r["ratio"] < 6.0, r


# ═══════════════════════════════ ★ 종단 게이트 (정확 구적 대조)
@pytest.mark.parametrize("mass", [0.0, 1.0])
def test_trajectory_matches_exact_quadrature(bg, mass):
    """★★ 적분 궤적이 정확 구적과 일치 (i_max=2 에서 ~1e−4)."""
    e = TI.trajectory_error(bg, mass, t_end=0.2, nsteps=20, l_max=2, i_max=2)
    assert e["rho"] < 1e-3, e
    assert e["q"] < 1e-3, e
    assert e["pi"] < 2e-3, e


def test_time_step_is_already_converged(bg):
    """★ dt 는 지배 오차가 아니다 — nsteps 10 → 80 에서 오차가 바뀌지 않는다.

    ⇒ 남은 오차를 "적분 정밀도" 로 오해하면 안 된다 (닫힘 오차다).
    """
    lo = TI.trajectory_error(bg, 0.0, 0.2, 10, l_max=2, i_max=1, **CTRL)["rho"]
    hi = TI.trajectory_error(bg, 0.0, 0.2, 80, l_max=2, i_max=1, **CTRL)["rho"]
    assert abs(hi / lo - 1.0) < 1e-3, (lo, hi)


def test_i_closure_is_the_dominant_error(bg):
    """★★ i_max 를 올리면 오차가 단조 감소 (5.3e−4 → 9.2e−5 → 2.1e−5 → 6.3e−6).

    반면 l_max 는 거의 영향이 없다 — 법선합동(H2)과 **반대**다.
    이유: (div-free) 가 (l,i) → (l−1,i+1) 로 결합해 i 를 능동적으로 퍼뜨린다.
    """
    errs = [TI.trajectory_error(bg, 0.0, 0.2, 20, l_max=2, i_max=I, **CTRL)["rho"]
            for I in (1, 2, 3)]
    assert all(b < a for a, b in zip(errs, errs[1:])), errs
    assert errs[0] / errs[-1] > 10.0, errs


def test_l_max_barely_matters_for_rho(bg):
    """l_max 2 → 3 은 ρ 오차를 거의 바꾸지 않는다 (i-닫힘이 지배하므로)."""
    e2 = TI.trajectory_error(bg, 0.0, 0.2, 20, l_max=2, i_max=1, **CTRL)["rho"]
    e3 = TI.trajectory_error(bg, 0.0, 0.2, 20, l_max=3, i_max=1, **CTRL)["rho"]
    assert abs(e3 / e2 - 1.0) < 0.05, (e2, e3)


def test_error_scales_like_v_squared():
    """★ 오차가 tilt 크기와 함께 ~v² 로 커진다 (측정 지수 1.79)."""
    xs, ys = [], []
    for s in (0.02, 0.05, 0.1, 0.15):
        b = TI.Background(v0=(s, -0.6 * s, 1.5 * s))
        e = TI.trajectory_error(b, 0.0, 0.2, 20, l_max=2, i_max=2, **CTRL)["rho"]
        xs.append(np.log(s * 1.9))
        ys.append(np.log(e))
    p = np.polyfit(xs, ys, 1)[0]
    assert 1.5 < p < 2.5, p


def test_zero_tilt_recovers_normal_congruence_accuracy(bg):
    """★ v=0 에서 오차가 법선합동 수준(1.6e−7)으로 떨어진다 — tilt 가 원인임을 확정."""
    b0 = TI.Background(v0=(0.0, 0.0, 0.0), dv=(0.0, 0.0, 0.0))
    e0 = TI.trajectory_error(b0, 0.0, 0.2, 20, l_max=2, i_max=2, **CTRL)
    ev = TI.trajectory_error(bg, 0.0, 0.2, 20, l_max=2, i_max=2, **CTRL)
    assert e0["rho"] < 1e-5, e0
    assert e0["rho"] < ev["rho"] / 50.0, (e0, ev)
    assert e0["q"] < 1e-12                       # 법선 프레임은 q ≡ 0


# ═══════════════════════════════ 구조
def test_rhs_solves_the_mass_system(bg):
    """rhs 가 실제로 M·J̇ = F 를 만족하는 J̇ 를 낸다."""
    from bianchi.matter import tilted_mass as TMass
    from bianchi.matter import tilted_equation as TE
    L, I = 2, 1
    keys, _, _ = TMass.layout(L, I)
    J = {k: v for k, v in TI.initial_state(bg, 0.0, L, I).items() if k in keys}
    dJ = TI.rhs(J, bg, 0.0, L, I, **CTRL)
    geo = bg.geometry(0.0)
    Jc = TI.closure(J, L, I, "frozen")
    zero = {k: np.zeros(np.asarray(Jc[k]).shape) for k in Jc}
    F = {(l, i): -np.asarray(TE.equation_lhs(Jc, zero, geo, l, i), float)
         for l in range(L + 1) for i in range(I + 1)}
    Md = TMass.matvec(dJ, geo, L, I)
    rho = float(J[(0, 0)])
    assert max(np.abs(np.atleast_1d(Md[k] - F[k])).max() for k in F) / rho < 1e-10


def test_closure_fills_required_neighbours(bg):
    """닫힘이 방정식이 요구하는 (l+2, i+2) 이웃을 모두 채운다."""
    L, I = 2, 1
    J = {k: v for k, v in TI.initial_state(bg, 0.0, L, I).items()}
    Jc = TI.closure(J, L, I)
    for l in range(L + 3):
        for i in range(-1, I + 3):
            assert (l, i) in Jc, (l, i)


# ═══════════════════════════════ ★ 무질량 1차원 환원 (문헌 근거)
# Lewis & Challinor (astro-ph/0203507): "For massless particles E=λ and the
# velocity-weighted moments are identical, J^(i) = J^(i').  The momentum-integrated
# equations then reduce to the usual one-dimensional Boltzmann hierarchy."
def test_two_dimensional_integration_breaks_the_massless_degeneracy(bg):
    """★★ 지배 오차의 **정체**: 정확한 축퇴를 수치가 깨뜨린다.

    무질량 초기조건은 J^(i)=J^(0) 를 3.1e−15 로 만족하지만, 2차원 격자를 독립
    적분하면 t=T 에서 **2.2e−1** 까지 깨진다 (궤적오차 1e−4 보다 크다).
    ⇒ "i-닫힘이 부정확" 이 아니라 "축퇴를 깨뜨림" 이 문제였다.
    """
    d = TI.degeneracy_violation(bg, l_max=2, i_max=1, **CTRL)
    assert d["t0"] < 1e-13, d
    assert d["tT"] > 1e-2, d
    # ★ L3: 같은 축퇴가 J̇ 닫힘(기본값)에서는 **유지**된다 (기계정밀도)
    n = TI.degeneracy_violation(bg, l_max=2, i_max=1)
    assert n["tT"] < 1e-12, n


def test_degenerate_reduction_is_far_more_accurate(bg):
    """★★ 축퇴를 강제하면 오차 채널이 통째로 사라진다.

        2차원 (l_max=2, i_max=1):  rho 5.3e−4   q 3.0e−4   pi 8.9e−4
        1차원 환원 (l_max=2):       rho 1.6e−6   q 1.5e−5   pi 1.5e−4
        1차원 환원 (l_max=3):       rho 7.8e−8   q 2.3e−6   pi 1.5e−5
    """
    two_d = TI.trajectory_error(bg, 0.0, 0.2, 20, l_max=2, i_max=1, **CTRL)
    one_d = TI.trajectory_error_degenerate(bg, 0.2, 20, l_max=2)
    assert one_d["rho"] < two_d["rho"] / 100.0, (one_d, two_d)
    assert one_d["pi"] < two_d["pi"], (one_d, two_d)
    # ★ L3: 환원이 특별한 게 아니었다 — J̇ 닫힘을 켜면 2차원이 **같은 값**을 낸다
    new = TI.trajectory_error(bg, 0.0, 0.2, 20, l_max=2, i_max=1)
    assert abs(new["rho"] - one_d["rho"]) < 1e-8 * one_d["rho"], (new, one_d)


def test_degenerate_reduction_is_l_truncation_limited(bg):
    """★ 환원 후에는 오차가 다시 **l_max 지배**가 된다 (H2 의 법선합동과 같은 성격).

    l_max 2 → 3 에서 rho 가 21배, pi 가 10배 개선 — 2차원 판에서는 거의 무변화였다.
    """
    e2 = TI.trajectory_error_degenerate(bg, 0.2, 20, l_max=2)
    e3 = TI.trajectory_error_degenerate(bg, 0.2, 20, l_max=3)
    assert e3["rho"] < e2["rho"] / 5.0, (e2, e3)
    assert e3["pi"] < e2["pi"] / 5.0, (e2, e3)


def test_degenerate_reduction_reaches_1e_7(bg):
    """환원 + l_max=3 에서 ρ 오차가 1e−7 수준 (2차원 판 대비 약 6800배)."""
    e = TI.trajectory_error_degenerate(bg, 0.2, 20, l_max=3)
    assert e["rho"] < 1e-6, e
    assert e["q"] < 1e-4, e
