"""
R1/R2 · **type V 커널의 Rust 이식** — 빠르게만 하고, 정확도는 오라클로 지킨다.

프로파일이 지목한 병목은 노드 배열(55296점)을 여러 번 훑는 두 함수였다:
```
moments_from_nodes(l≤2,i≤1)  11.2 ms      kinetic_rhs            4.1 ms
characteristic_rhs_vec        3.3 ms      evolve_coupled 한 스텝  68 ms
```
메모리 대역폭 문제라서 **융합 순회 + rayon** 이 바로 듣는다.

★ 측정 (같은 기계, 55296 노드):
```
evolve_coupled(60스텝)   python 3.94 s → rust 0.38 s   10.4배
back_trace(256스텝)      python 2.78 s → rust 0.27 s   11배
forward_vs_backward      python 1.61 s → rust 0.47 s    3.5배
```
★★ **오라클을 지우지 않았다**: `backend="python"` 이면 numpy 판이 그대로 돈다.
  이 파일이 두 경로를 대조한다 — 포트는 빠르게만 할 뿐 정확해지지 않는다.

★ 물리 결론은 하나도 안 바뀐다:  구속 4차 수렴이 Rust 경로에서 **같은 수**를 낸다
  (1.323e−06 → 8.141e−08 → 5.042e−09 → 3.136e−10, 비 16.3/16.1/16.1).
"""
import numpy as np
import pytest

from bianchi.matter import type_v as TV
from bianchi.matter import type_v_coupled as TC

pytestmark = pytest.mark.skipif(not TC.rust_available(),
                                reason="bianchi_rustcore 없음 (Python 폴백만)")

KEYS = ("a", "h", "rho", "q1", "pi", "sigma1", "Hdot_spatial", "Hdot_ray",
        "qdot_node", "qdot_law", "qdot_naive")


# ═══════════════════════════════ 1. 노드 커널 (R1)
def test_moments_agree_with_the_numpy_oracle():
    """★★ (ρ, 3p, q, π) 가 numpy 판과 기계정밀도로 같다."""
    import bianchi_rustcore as RC
    P, W = TC.initial_nodes(0.6)
    a = np.array([1.0, 0.9, 1.2])
    rho, tp, q, pi = RC.tv_moments(np.ascontiguousarray(P), W, a, 0.6)
    ref = TC.moments_from_nodes(P, W, a, 0.6, 2, 1)
    assert abs(rho / float(ref[(0, 0)]) - 1) < 1e-13
    assert abs(tp / float(ref[(0, 1)]) - 1) < 1e-13
    assert np.abs(np.asarray(q) - np.asarray(ref[(1, 0)])).max() / rho < 1e-13
    assert np.abs(np.asarray(pi) - np.asarray(ref[(2, 0)])).max() / rho < 1e-13


def test_kinetic_rhs_agrees_with_the_numpy_oracle():
    """★ (Ṗ, Ẇ) 가 numpy 판과 같다 (특성곡선 + Liouville 무게)."""
    import bianchi_rustcore as RC
    P, W = TC.initial_nodes(0.6)
    a = np.array([1.0, 0.9, 1.2])
    dP, dW = RC.tv_kinetic_rhs(np.ascontiguousarray(P), W, a, 0.6, 0.7)
    rP, rW = TC.kinetic_rhs(P, W, a, 0.6, 0.7)
    assert np.abs(np.asarray(dP) - rP).max() / max(np.abs(rP).max(), 1e-300) < 1e-13
    assert np.abs(np.asarray(dW) - rW).max() / np.abs(rW).max() < 1e-13


def test_flux_rate_agrees_with_the_numpy_oracle():
    """★ q̇₁ 의 노드 계산 (D2b 운동량 법칙에 쓰인다).

    ★ t=0 격자에서는 q₁ 이 **정확히 0** (1.8e−15) 이라 상대비교가 무의미하다 —
      실제로 첫 판이 거기서 0.084 를 냈다.  노드를 굴려 q₁ ≠ 0 으로 만든 뒤 재고,
      규격화는 ρ 로 한다.
    """
    import bianchi_rustcore as RC
    bg = TV.Background(A=0.7)
    P, W = TC.initial_nodes(0.6)
    P, W = TC._push_nodes(P, W, bg.a, 0.6, 0.7, 0.3, 40, True, rate=bg.H + bg.sig)
    a = np.asarray(bg.a(0.3), float)
    rho = float(TC.moments_from_nodes(P, W, a, 0.6, 0, 0)[(0, 0)])
    q1, src = RC.tv_flux_rate(np.ascontiguousarray(P), W, a, 0.6, 0.7)
    rq, rs = TC.flux_rate_from_nodes(P, W, a, 0.6, 0.7)
    assert abs(rq) / rho > 1e-4, rq            # 실제로 0 이 아닌 곳에서 재는가
    assert abs(q1 - rq) / rho < 1e-15
    assert abs(src - rs) / rho < 1e-15


# ═══════════════════════════════ 2. 결합 진화 전체 (R1)
def test_coupled_evolution_matches_the_python_loop():
    """★★ **가장 중요한 게이트** — 궤적·구속·진단이 전부 일치한다."""
    kw = dict(nsteps=30, t_end=0.3)
    ref = TC.evolve_coupled(backend="python", **kw)
    got = TC.evolve_coupled(**kw)
    for k in KEYS:
        x, y = np.asarray(ref[k], float), np.asarray(got[k], float)
        sc = max(float(np.abs(x).max()), 1e-300)
        assert np.abs(x - y).max() / sc < 1e-11, (k, np.abs(x - y).max() / sc)


def test_constraint_residuals_agree_in_absolute_terms():
    """★ F, C 는 그 자체가 절단오차 크기라 **절대값**으로 본다 (ρ 로 규격화)."""
    kw = dict(nsteps=30, t_end=0.3)
    ref = TC.evolve_coupled(backend="python", **kw)
    got = TC.evolve_coupled(**kw)
    rho = np.asarray(ref["rho"], float)
    for k in ("friedmann", "codazzi"):
        d = np.abs(np.asarray(ref[k], float) - np.asarray(got[k], float)) / rho
        assert d.max() < 1e-14, (k, d.max())


def test_projection_path_also_matches():
    """★ D2 의 매-스텝 투영 경로도 두 판이 같다."""
    kw = dict(nsteps=20, t_end=0.08, hsign=-1.0, sigma1=0.02, project=True)
    ref = TC.evolve_coupled(backend="python", **kw)
    got = TC.evolve_coupled(**kw)
    for k in ("a", "h", "rho", "sigma1"):
        x, y = np.asarray(ref[k], float), np.asarray(got[k], float)
        assert np.abs(x - y).max() / np.abs(x).max() < 1e-11, k


def test_the_fourth_order_gate_survives_the_port():
    """★★ 물리 결론이 안 바뀐다 — 구속 잔차가 여전히 RK4 4차로 사라진다."""
    lo = TC.constraint_drift(nsteps=30, t_end=0.3)
    hi = TC.constraint_drift(nsteps=60, t_end=0.3)
    assert 12.0 < lo["friedmann"] / hi["friedmann"] < 20.0, (lo, hi)
    assert 12.0 < lo["codazzi"] / hi["codazzi"] < 20.0, (lo, hi)


# ═══════════════════════════════ 3. 특성곡선 (R2)
@pytest.mark.parametrize("mass,A", [(0.0, 0.7), (0.6, 0.7), (2.0, 0.3)])
def test_back_trace_matches_the_python_oracle(mass, A):
    """★★ K4b 역추적 — 1.9e−16 (11배 빠르다)."""
    bg = TV.Background(A=A)
    P, _ = TC.initial_nodes(mass)
    ref = TV.back_trace(P, bg, mass, 0.35, 64, backend="python")
    got = TV.back_trace(P, bg, mass, 0.35, 64)
    assert np.abs(ref - got).max() / np.abs(ref).max() < 1e-13


@pytest.mark.parametrize("measure", [True, False])
def test_push_nodes_matches_the_python_oracle(measure):
    """★ K5b 순방향 밀기 — 측도 규칙 on/off 양쪽."""
    bg = TV.Background(A=0.7)
    P, W = TC.initial_nodes(0.6)
    rate = bg.H + bg.sig
    a = TC._push_nodes(P, W, bg.a, 0.6, 0.7, 0.3, 40, measure, backend="python")
    b = TC._push_nodes(P, W, bg.a, 0.6, 0.7, 0.3, 40, measure, rate=rate)
    assert np.abs(a[0] - b[0]).max() / np.abs(a[0]).max() < 1e-13
    assert np.abs(a[1] - b[1]).max() / max(np.abs(a[1]).max(), 1e-300) < 1e-13


def test_forward_vs_backward_gives_the_same_number_on_both_paths():
    """★ K5b 의 측도-규칙 대조 자체가 두 백엔드에서 같은 값을 낸다 (1.41e−11)."""
    x = TC.forward_vs_backward(nsteps=60, backend="python")
    y = TC.forward_vs_backward(nsteps=60)
    # 이 지표 자체가 반올림 크기의 최대값이라 **절대차**로 본다 (첫 판은 상대차로
    # 재다가 6.8e−06 에 걸렸다 — 지표가 1.4e−11 인데 상대비교를 한 셈).
    assert abs(x - y) < 1e-15, (x, y)
    assert x < 1e-9 and y < 1e-9, (x, y)


# ═══════════════════════════════ 4. 폴백이 살아 있는가
def test_the_python_oracle_is_still_reachable():
    """★★ 포트가 오라클을 **지우지 않았다** — 언제든 되돌릴 수 있어야 한다."""
    r = TC.evolve_coupled(nsteps=4, t_end=0.02, backend="python")
    assert set(("a", "h", "rho", "friedmann", "codazzi")) <= set(r)
    assert np.isfinite(np.asarray(r["a"], float)).all()
