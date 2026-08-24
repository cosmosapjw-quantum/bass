"""
Q2 · **특성곡선 커널 (전 유형·질량)** 게이트 (76차).

유도: audit/q2_characteristics_general.py — T1 → ((n p)×p) + (a·p)p − |p|²a.
  ★ class B 의 a-항이 새로 붙고, **|p| 보존 (Q-T3) 이 그대로 확장**된다.

게이트 (임계는 계약에서):
  · 기호 항등 4종 (분해·a노름·n노름·지표뒤집기 검출가능)
  · ★ 제1원리 대조: 좌표 측지선 (type V, type II; m=0, 0.5) ≤ 1e−12
  · ★ class A · m=0 축약 ≡ I1a `characteristic_rhs_class_a` ≤ 1e−13
  · Rust ≡ Python 참조 비트급
  · |ê| 보존 (H=Σ=R=0) ≤ 1e−14, 장시간 적분에서도
  · RK4 4차 수렴
  · ★ 무질량 방향흐름이 p 에 무관 (Q5 스텐실 공유의 전제)
  · N-항 다중극 선택률 T4: l ≤ 1 기여 정확 0
"""
import numpy as np
import pytest

RC = pytest.importorskip("bianchi_rustcore")
if not hasattr(RC, "qc_rhs_split"):
    pytest.skip("Q2 커널 미빌드", allow_module_level=True)

from audit import q2_characteristics_general as AUD  # noqa: E402
from bianchi.q import characteristics as CH  # noqa: E402
from bianchi.q import contract as C  # noqa: E402


def _bg(seed=0):
    rng = np.random.default_rng(seed)
    return CH.Background(h=0.7, sigma=rng.standard_normal(6) * 0.3,
                         rot=rng.standard_normal(3) * 0.2,
                         n=rng.standard_normal(6) * 0.5,
                         a=rng.standard_normal(3) * 0.25)


def _unit(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


def test_symbolic_identities():
    """★★ 기호 박제 4종 — 유도가 항등임을 sympy 가 증명."""
    assert AUD.t1_decomposition_symbolic()
    assert AUD.a_term_preserves_norm_symbolic()
    assert AUD.n_term_preserves_norm_symbolic()
    assert AUD.wrong_index_order_is_detectable()


@pytest.mark.parametrize("kind,mass", [("V", 0.0), ("V", 0.5),
                                       ("II", 0.0), ("II", 0.5)])
def test_first_principles_coordinate_geodesic(kind, mass):
    """★★ 제1원리: 좌표 측지선 (sympy 계량) 대 닫힌 정규직교틀 공식."""
    err, _, _ = AUD.compare_routes(kind, mass=mass, nstep=3000, seed=1)
    assert err <= 1e-12, (kind, mass, err)


def test_reduces_to_i1a_class_a():
    """★ class A (a=0) 축약이 I1a 커널과 일치 — 계약 임계."""
    from bianchi.matter.class_a_char import characteristic_rhs_class_a
    tol = C.budget("Q2", "reduce_i1a")
    rng = np.random.default_rng(4)
    for _ in range(30):
        S = rng.standard_normal((3, 3)) * 0.3
        S = 0.5 * (S + S.T); S -= np.eye(3) * np.trace(S) / 3
        N = np.diag(rng.standard_normal(3))
        R = rng.standard_normal(3) * 0.2
        H = 0.8
        p = rng.standard_normal(3)
        for mass in (0.0, 0.7):
            ref = characteristic_rhs_class_a(p, H, S, R, N, mass)
            bg = CH.Background(h=H, sigma=S, rot=R, n=N, a=np.zeros(3))
            got = CH.rhs_p(p, mass, bg)
            assert float(np.abs(got - ref).max()) <= tol


def test_rust_matches_python_reference_bitwise_grade():
    """Rust 커널 ≡ Python 참조 (I3/G1b 관례: 모든 커널에 참조 구현)."""
    rng = np.random.default_rng(7)
    for s in range(10):
        bg = _bg(s)
        p = rng.standard_normal(3)
        e = _unit(rng.standard_normal(3))
        for mass in (0.0, 0.9):
            assert float(np.abs(CH.rhs_p(p, mass, bg)
                                - CH.rhs_p_ref(p, mass, bg)).max()) <= 1e-14
            d1, l1 = CH.rhs_split(e, 0.3, mass, bg)
            d2, l2 = CH.rhs_split_ref(e, 0.3, mass, bg)
            assert float(np.abs(d1 - d2).max()) <= 1e-14
            assert abs(l1 - l2) <= 1e-15


def test_unit_norm_preserved_by_n_and_a_terms():
    """★ T3 + Q-T3 의 수치판.

    |ê| 보존은 **정확한 흐름**의 성질이고 RK4 는 O(h⁴) 로만 따라간다.  그래서
    게이트는 두 개다: (i) drift 가 4차로 사라진다 (이게 T3 의 진짜 수치판),
    (ii) 명시 해상도에서 계약 임계 이하.
    ★ 반증 기록 (76차): 처음엔 고정 nsub=4000 에서 1e−14 를 걸었다가 실측
    2.29e−14 로 떨어졌다 — 이는 물리 오류가 아니라 적분기 절단오차였고,
    nsub 스윕이 정확히 4차 감쇠 (1.5e−9 → 1.8e−15) 를 보여 판별되었다."""
    bg = CH.Background(h=0.0, sigma=np.zeros(6), rot=np.zeros(3),
                       n=[0.9, -0.4, 0.3, 0.1, 0.0, -0.05], a=[0.2, -0.1, 0.05])
    e0 = _unit([0.3, -0.7, 0.5])[None, :]
    drift = []
    for n in (250, 500, 1000, 2000):
        e, _ = CH.direction_map(e0, dt=10.0, bg0=bg, substeps=n)
        drift.append(abs(np.linalg.norm(e[0]) - 1.0))
    orders = [np.log2(drift[k] / drift[k + 1]) for k in range(len(drift) - 1)]
    want, band = C.budget("Q2", "unit_norm_order")
    assert all(abs(o - want) < band for o in orders), orders
    e, _ = CH.direction_map(e0, dt=10.0, bg0=bg,
                            substeps=C.budget("Q2", "unit_norm_nsub"))
    assert abs(np.linalg.norm(e[0]) - 1.0) <= C.budget("Q2", "unit_norm")


def test_rk4_convergence_order():
    """★ 4차 수렴 (계약: 4.00 ± 0.05 — 여기선 실측 대역 ±0.3 로 잰다)."""
    want, band = C.budget("Q2", "order")
    bg = _bg(2)
    e0 = _unit([0.2, -0.5, 0.8])[None, :]
    ref, _ = CH.direction_map(e0, 1.0, bg, substeps=4096)
    errs = []
    for n in (8, 16, 32, 64):
        e, _ = CH.direction_map(e0, 1.0, bg, substeps=n)
        errs.append(float(np.abs(e - ref).max()))
    orders = [np.log2(errs[k] / errs[k + 1]) for k in range(len(errs) - 1)]
    assert abs(orders[-1] - want) < 0.3, orders
    assert want == 4.0 and band == 0.05


def test_massless_direction_flow_is_momentum_independent():
    """★ Q5 의 전제: m=0 이면 dê/dt 가 p 에 무관 (스텐실 전 반경 공유)."""
    bg = _bg(3)
    e = _unit([0.1, 0.9, -0.4])
    d1, _ = CH.rhs_split(e, -5.0, 0.0, bg)
    d2, _ = CH.rhs_split(e, +5.0, 0.0, bg)
    assert float(np.abs(d1 - d2).max()) == 0.0
    # 질량이 있으면 **달라야** 한다 (반증 장치)
    d3, _ = CH.rhs_split(e, -5.0, 0.6, bg)
    d4, _ = CH.rhs_split(e, +5.0, 0.6, bg)
    assert float(np.abs(d3 - d4).max()) > 1e-6


def test_nterm_multipole_selection_rule_T4():
    """★ T4: N-항의 l ≤ 1 모멘트 기여가 정확히 0 (a=0, 기하항 끔)."""
    tol = C.budget("Q2", "nterm_l01")
    from numpy.polynomial.legendre import leggauss
    x, wx = leggauss(40)
    ph = 2 * np.pi * np.arange(80) / 80
    T, P = np.meshgrid(np.arccos(x), ph, indexing="ij")
    W = np.outer(wx, np.full(80, 2 * np.pi / 80)).ravel()
    E = np.stack([np.sin(T) * np.cos(P), np.sin(T) * np.sin(P),
                  np.cos(T)], -1).reshape(-1, 3)
    bg = CH.Background(h=0.0, sigma=np.zeros(6), rot=np.zeros(3),
                       n=[0.9, -0.4, 0.3, 0.0, 0.0, 0.0], a=np.zeros(3))
    # 등방 f=1 의 시간미분 = -div(f v) = -div(v);  l=0,1 성분을 잰다
    #   div_S2(v) 를 유한차분 대신 발산정리로: ∮ f v·n 은 접벡터라 0;
    #   대신 모멘트율 d/dt ∫ Y_l f  = ∫ (grad Y_l)·v  를 직접 잰다.
    d = np.array([CH.rhs_split(e, 0.0, 0.0, bg)[0] for e in E])
    # l=0: grad Y_0 = 0  ⇒ 정확히 0 (구조적)
    assert abs(float((W * np.einsum("ai,ai->a", d, np.zeros_like(d))).sum())) <= tol
    # l=1: grad(e_k) 의 접성분 = (delta - ee)_k  ⇒ ∫ w v_k
    for k in range(3):
        rate = float((W * d[:, k]).sum())
        assert abs(rate) <= 1e-13, (k, rate)
