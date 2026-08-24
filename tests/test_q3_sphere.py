"""
Q3 · **구면 표현층** 게이트 (76차).

  · ★ 실수 구면조화 직교정규성을 **수치로** 잰다 (문헌 표를 믿지 않는다 — J1 3j 교훈)
  · Rust ≡ Python 참조 (규약 비트급)
  · 분석↔합성 왕복 (24×24 에서 L≤11, 48×96 에서 L≤23)
  · 임의점 합성 = 격자점 합성 (보간 경로의 무결성)
  · ★ 독립 구적 (Lebedev 26점, 8차) 대비 모멘트 교차 — 곱격자와 족이 다른 심판
  · P₀/P₂ 투영이 대역제한 f 에서 해석값과 일치 (Q7 3항 공식의 전제)
  · 격자 항등 Σw, ∫êê
  · 꼬리 에너지 지표가 대역제한 f 에서 0, 비대역제한에서 >0 (열화 감시자)
"""
import numpy as np
import pytest

RC = pytest.importorskip("bianchi_rustcore")
if not hasattr(RC, "QSphere"):
    pytest.skip("Q3 구면층 미빌드", allow_module_level=True)

from bianchi.q import contract as C  # noqa: E402
from bianchi.q import sphere as S  # noqa: E402


def test_real_sh_are_orthonormal_measured_not_assumed():
    """★★ <Y_k, Y_j> = δ_kj 를 격자 구적으로 실측."""
    sph = S.sphere(24, 48)
    e, w = S.nodes(sph)
    L = 6
    Y = np.array([S.ylm_ref(L, ei) for ei in e])          # (M, nc)
    G = np.einsum("a,ak,aj->kj", w, Y, Y)
    assert float(np.abs(G - np.eye(S.n_coef(L))).max()) <= 1e-12


def test_rust_ylm_matches_python_reference():
    rng = np.random.default_rng(2)
    for _ in range(20):
        v = rng.standard_normal(3); v /= np.linalg.norm(v)
        got = np.asarray(RC.qs_ylm_at(7, v))
        assert float(np.abs(got - S.ylm_ref(7, v)).max()) <= 1e-14


@pytest.mark.parametrize("nt,npz,L", [(24, 48, 11), (32, 64, 23)])
def test_analysis_synthesis_roundtrip(nt, npz, L):
    """★ 대역제한 f 의 왕복 (계약 임계)."""
    tol = C.budget("Q3", "sh_roundtrip")
    sph = S.sphere(nt, npz)
    rng = np.random.default_rng(L)
    a = rng.standard_normal(S.n_coef(L))
    f = np.asarray(sph.synthesize(a, L))
    a2 = np.asarray(sph.analyze(f, L))
    assert float(np.abs(a - a2).max()) <= tol, float(np.abs(a - a2).max())


def test_synthesize_at_matches_grid_synthesis():
    """임의점 합성 경로가 격자 합성과 같은 값 (Q5 보간 비교군의 무결성)."""
    sph = S.sphere(24, 48)
    e, _ = S.nodes(sph)
    L = 8
    rng = np.random.default_rng(1)
    a = rng.standard_normal(S.n_coef(L))
    f_grid = np.asarray(sph.synthesize(a, L))
    f_pts = np.asarray(sph.synthesize_at(a, L, e.ravel()))
    assert float(np.abs(f_grid - f_pts).max()) <= 1e-12


def test_moments_cross_checked_by_independent_lebedev_quadrature():
    """★★ 족이 다른 구적 (Lebedev 26점, 8차) 과의 교차 — 등방·이방 둘 다."""
    L = 3                                       # 26점 규칙이 정확한 대역 안에서
    rng = np.random.default_rng(9)
    a = rng.standard_normal(S.n_coef(L))
    sph = S.sphere(24, 48)
    e, w = S.nodes(sph)
    f = np.array([S.ylm_ref(L, ei) @ a for ei in e])
    r1, q1, p1 = S.moments(sph, f)

    nl, wl = S.lebedev26()
    fl = np.array([S.ylm_ref(L, ei) @ a for ei in nl])
    r2, q2, p2 = S.moments_on(nl, wl, fl)

    tol = C.budget("Q3", "lebedev_iso")
    assert abs(r1 - r2) <= tol * max(1.0, abs(r1))
    assert float(np.abs(q1 - q2).max()) <= tol * max(1.0, float(np.abs(q1).max()))
    assert float(np.abs(p1 - p2).max()) <= tol * max(1.0, float(np.abs(p1).max()))


def test_low_l_projections_are_exact_for_band_limited_f():
    """★ P₀·P₂ 가 해석값과 일치 — Q7 의 3항 공식이 여기에 의존한다."""
    tol = C.budget("Q3", "proj_exact")
    sph = S.sphere(24, 48)
    e, _ = S.nodes(sph)
    L = 5
    rng = np.random.default_rng(3)
    a = rng.standard_normal(S.n_coef(L))
    f = np.array([S.ylm_ref(L, ei) @ a for ei in e])
    for l in (0, 1, 2):
        got = np.asarray(sph.project_l(f, l))
        want = np.array([sum(a[S.idx(l, m)] * S.ylm_ref(L, ei)[S.idx(l, m)]
                             for m in range(-l, l + 1)) for ei in e])
        assert float(np.abs(got - want).max()) <= tol, (l, float(np.abs(got - want).max()))


def test_grid_identities():
    """Σw = 4π, ∫êê = (4π/3)δ (계약 임계)."""
    sph = S.sphere(24, 48)
    s, ee = S.grid_quality(sph)
    assert s <= C.budget("Q3", "sum_w")
    assert ee <= C.budget("Q3", "ee_identity")


def test_tail_energy_is_a_real_degradation_indicator():
    """★ 열화 감시자: 대역제한이면 꼬리 0, 뾰족한 f 면 유의미하게 >0."""
    sph = S.sphere(32, 64)
    e, _ = S.nodes(sph)
    rng = np.random.default_rng(4)
    a = rng.standard_normal(S.n_coef(4))
    f_band = np.array([S.ylm_ref(4, ei) @ a for ei in e])
    assert sph.tail_energy(f_band, 4, 20) <= 1e-20
    # 축비 큰 이방 분포 (강이방 광자장의 대용)
    f_sharp = np.exp(-20.0 * (1.0 - e[:, 2] ** 2))
    assert sph.tail_energy(f_sharp, 4, 20) > 1e-3
