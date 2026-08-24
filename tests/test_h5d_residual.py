"""
H5-d2/d3 · 일반 rank tilted 항 + **l ≥ 2 잔차** 검증.

★ 이 파일이 메우는 공백: H5-b 의 보존법칙 오라클은 (l,i) = (0,0), (1,0) 만 통제한다.
  l ≥ 2 의 (Ω),(D),(E),(div) 계수는 여기서 처음 독립 검증된다.

★ 절단이 필요 없다: 잔차 시험은 이웃 (l±2, i−1…i+2) 을 **모두 구적으로 직접 공급**할
  수 있으므로 절단 오차가 섞이지 않고 계수·부호만 순수하게 시험된다.

기록해 둘 두 가지 한계 (아래 시험으로 고정):
  1. **(E) 는 (l,i)=(2,0) 에서 항등적으로 0** — n=2 가 (n−2) 를, i=0 이 (l−n)=−2i 를
     동시에 죽인다.  이 칸만으로 부호 스캔을 하면 마진 1.000 이 나온다 (실측).
  2. **무질량은 i 구조를 시험하지 못한다** — J^(i) 가 i-무관이라 각 항군의 계수합이
     n-무관으로 붕괴한다 ((A)→5, (D)→l+3, (B)→l−1, (E)→l−2, (C)→−(l+2)).
     i 의존성을 시험하려면 **유질량**이 필요하다.
"""
import numpy as np
import pytest

from bianchi.matter import tilted as TL
from bianchi.matter import tilted_terms as TT

R = pytest.importorskip("audit.h5d_tilted_residual")

KW = dict(a_vec=(1.0, 0.9, 1.2), da_vec=(0.35, 0.28, 0.42),
          v=(0.08, -0.05, 0.12), dv=(0.015, 0.01, -0.02))


# ═══════════════════════════════ H5-d2 · 일반 rank 코드가 검증된 값을 재생산
@pytest.fixture(scope="module")
def geo_state():
    geo = TT.geometry(KW["a_vec"], KW["da_vec"], KW["v"], KW["dv"])
    st = TL.state(**KW)
    return geo, st


def test_general_rank_reproduces_perp_dot(geo_state):
    """★ 일반 rank ⊥J̇ 가 `tilted.py` (∇T 로 검증됨) 의 rank 0·1 값을 재생산.

    재생산이 higher rank 신뢰의 근거다 — 일반 코드를 직접 검증할 오라클이 없으므로.
    """
    geo, st = geo_state
    q = np.array(TL._DEF["q"]); dq = np.array(TL._DEF["dq"])
    assert np.abs(TT.perp_dot(q, dq, geo) - st["q_dot"]).max() < 1e-15
    g0 = TT.perp_dot(np.array(TL._DEF["rho"]), np.array(TL._DEF["drho"]), geo)
    assert abs(float(g0) - st["rho_dot"]) < 1e-15


def test_general_rank_reproduces_divergences(geo_state):
    """D^aq_a, D^bπ_ba, D_a p 를 rank 1·2 에서 재생산."""
    geo, st = geo_state
    q = np.array(TL._DEF["q"]); dq = np.array(TL._DEF["dq"])
    pi = TL._pi_matrix(TL._DEF["pi5"]); dpi = TL._pi_matrix(TL._DEF["dpi5"])
    assert abs(float(TT.div_contracted(q, dq, geo)) - st["div_q"]) < 1e-15
    assert np.abs(TT.div_contracted(pi, dpi, geo) - st["div_pi"]).max() < 1e-15
    gp = TT.div_free_index(np.array(TL._DEF["p"]), np.array(TL._DEF["dp"]), geo, l=1)
    assert np.abs(gp - st["grad_p"]).max() < 1e-15


def test_tetrad_rotation_term_is_not_negligible(geo_state):
    """★ 사틀 회전항을 빼면 ⊥J̇ 가 실제로 틀린다 — 함정이 실재함을 못 박는다."""
    geo, _ = geo_state
    q = np.array(TL._DEF["q"]); dq = np.array(TL._DEF["dq"])
    full = TT.perp_dot(q, dq, geo)
    naive = TT.perp_dot(q, dq, dict(geo, deup=np.zeros_like(geo["deup"])))
    assert np.abs(full - naive).max() > 1e-4 * np.abs(full).max()


# ═══════════════════════════════ H5-d3 · 잔차
@pytest.mark.parametrize("l,i", [(0, 0), (1, 0), (2, 0), (3, 0), (2, 1), (1, 1)])
def test_equation_residual_is_fd_limited(l, i):
    """★★ 식 (12) 이 l ≤ 3 에서 성립 (측정 1e−11 ~ 1.5e−10, 중앙차분 한계)."""
    assert R.residual(l, i, **KW) < 1e-8, (l, i)


@pytest.mark.parametrize("l,i", [(2, 0), (3, 0), (2, 1), (3, 1)])
def test_equation_residual_with_mass(l, i):
    """★ 유질량에서도 성립 — **i 구조까지** 시험된다 (무질량은 붕괴시킨다)."""
    assert R.residual(l, i, mass=1.0, **KW) < 1e-8, (l, i)


def test_residual_is_central_difference_limited():
    """★ dt 스캔이 U자 곡선 — 절단(∝dt²) + 반올림(∝1/dt).

    잔차가 계수 오류가 아니라 **차분 한계**임을 보인다 (H3R 에서 배운 진단).
    측정: 1e−3 → 3.9e−8,  1e−5 → 1.5e−10,  1e−7 → 1.2e−8.
    """
    rows = dict(R.dt_scan(2, 0, dts=(1e-3, 1e-5, 1e-7), **KW))
    assert rows[1e-5] < rows[1e-3]           # 큰 dt: 절단 지배
    assert rows[1e-5] < rows[1e-7]           # 작은 dt: 반올림 지배
    assert rows[1e-5] < 1e-9


# ═══════════════════════════════ ★ 부호 유일성 (l ≥ 2 에서 독립 확인)
def test_sign_scan_confirms_h5b_signs():
    """★★ l ≥ 2 에서 (Ω),(D),(E),(div) 부호가 H5-b 보존법칙 확정값과 **일치**.

    두 오라클이 독립이다: H5-b 는 ∇_μT^{μν}=0 (l≤1), 여기는 boosted 정확구적 (l≥2).
    측정 마진 5.8e5 배 (무질량) / 5.4e5 배 (m=1).
    """
    best, second, margin = R.sign_scan(**KW)
    assert margin > 1e4, (best, second, margin)
    for k, v in best[1].items():
        assert v == TL.SIGNS[k], (k, v, TL.SIGNS[k])


def test_sign_scan_with_mass_agrees():
    best, _, margin = R.sign_scan(mass=1.0, **KW)
    assert margin > 1e4, margin
    assert best[1] == {k: TL.SIGNS[k] for k in best[1]}


# ═══════════════════════════════ ★ 한계 1 — (E) 가 죽는 칸
def test_E_term_vanishes_identically_at_l2_i0():
    """★ (E) 는 (l,i)=(2,0) 에서 항등적 0 — n=2 가 (n−2) 를, i=0 이 (l−n)=−2i 를 죽인다.

    이 칸만으로 스캔하면 마진이 **1.000** 이 나온다 (실패가 아니라 **미결정**).
    활성도 진단 없이 마진만 보면 오독한다 — 그래서 `term_activity` 를 만들었다.
    """
    act = R.term_activity(2, 0, mass=1.0, **KW)
    assert act["E"] == 0.0, act["E"]
    act31 = R.term_activity(3, 1, mass=1.0, **KW)
    assert act31["E"] > 1e-6, act31["E"]        # 다른 칸에서는 살아 있다


def test_single_cell_scan_is_degenerate_for_E():
    """단일 칸 (2,0) 스캔은 (E) 부호를 확정하지 못한다 (마진 ≈ 1)."""
    _, _, margin = R.sign_scan(pairs=((2, 0),), mass=1.0, **KW)
    assert margin < 1.01, margin


# ═══════════════════════════════ ★ 한계 2 — 무질량은 i 구조를 시험 못 한다
def test_massless_moments_are_i_independent():
    """★ 무질량은 J^(i) 가 i-무관 ⇒ 각 항군의 계수합이 n-무관으로 붕괴한다.

        (A) (2n+3)+(2−2n) = 5      (D) (l+n+1)+(2−n) = l+3
        (B) (l−n)+(n−1)   = l−1    (E) (l−n)+(n−2)   = l−2
        (C) (n−1)−(l+n+1) = −(l+2)

    ⇒ 무질량 잔차는 **l 구조만** 시험한다.  i 구조는 유질량이 필요하다.
    """
    J0 = R.moment_grid(KW["a_vec"], KW["v"], 0.0, l_max=2, i_max=2)
    Jm = R.moment_grid(KW["a_vec"], KW["v"], 1.0, l_max=2, i_max=2)
    rho = float(J0[(0, 0)])
    for l in (0, 2):
        base0 = np.atleast_1d(np.asarray(J0[(l, 0)], float))
        basem = np.atleast_1d(np.asarray(Jm[(l, 0)], float))
        d0 = np.abs(np.atleast_1d(np.asarray(J0[(l, 1)], float)) - base0).max()
        dm = np.abs(np.atleast_1d(np.asarray(Jm[(l, 1)], float)) - basem).max()
        assert d0 / rho < 1e-14, (l, d0 / rho)      # 무질량: i-무관
        assert dm > 1e-3, (l, dm)                    # 유질량: i-의존 살아남


def test_massless_E_dies_at_all_of_l2():
    """무질량에서 (E) 계수합이 (l−2) 라 **l=2 전체**에서 죽는다 (i=1 도)."""
    act = R.term_activity(2, 1, mass=0.0, **KW)
    assert act["E"] < 1e-14, act["E"]
    act_m = R.term_activity(2, 1, mass=1.0, **KW)
    assert act_m["E"] > 1e-6, act_m["E"]            # 유질량은 살아난다


# ═══════════════════════════════ 범위의 정직한 명시
def test_grid_supports_l_up_to_three():
    """l 방정식은 l+2 이웃을 참조 ⇒ L_MAX=5 는 l ≤ 3 까지만 절단 없이 시험한다."""
    assert R.L_MAX == 5
    with pytest.raises(KeyError):
        R.residual(4, 0, **KW)                       # l=4 는 rank-6 필요
