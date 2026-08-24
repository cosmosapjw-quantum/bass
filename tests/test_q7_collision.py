"""
Q7 · **정확 충돌 지수 (3항)** 게이트 (76차).

    exp(x C) f = P₀f + e^{−x}(f − P₀f − P₂f) + e^{−0.9x} P₂f,  x = νΔτ

  · ★★ dense 행렬지수 (Taylor) 심판 대비 ≤ 1e−13
  · ★ k_l 하드코딩 금지 — 수치 구적 재계산과 대조
  · 등방화율 e^{−ντ}, e^{−0.9ντ} 해석 일치
  · ★ **근사 절환 없음**: νΔτ = 10⁶ 에서 발산 없이 정확히 P₀f
    (tight-coupling 근사가 존재할 이유 자체가 사라진다 — 계약 §3)
  · 수 보존 정확 · 양수성 구조적
  · Rust ≡ Python 참조
  · 공변격자 (로그공간) 경로 ≡ 선형 경로
"""
import numpy as np
import pytest

RC = pytest.importorskip("bianchi_rustcore")
if not hasattr(RC, "qx_collide"):
    pytest.skip("Q7 미빌드", allow_module_level=True)

from bianchi.q import collide as X  # noqa: E402
from bianchi.q import comoving as CM  # noqa: E402
from bianchi.q import contract as C  # noqa: E402
from bianchi.q import sphere as S  # noqa: E402


@pytest.fixture(scope="module")
def grid():
    sph = S.sphere(16, 32)
    e, w = S.nodes(sph)
    rng = np.random.default_rng(0)
    f = 1.0 + 0.7 * rng.standard_normal(len(w))
    return sph, e, w, f


def test_eigenvalues_are_recomputed_not_hardcoded(grid):
    """★ k_l = (1, 0, 1/10, 0, ...) 을 수치 구적으로 재계산해 대조."""
    k = X.kernel_eigenvalues(6)
    ref = X.kernel_eigenvalues_ref(6)
    assert float(np.abs(k - ref).max()) <= 1e-13
    assert abs(k[0] - 1.0) <= 1e-13 and abs(k[1]) <= 1e-13
    assert abs(k[2] - 0.1) <= 1e-13
    assert float(np.abs(k[3:]).max()) <= 1e-13
    assert C.CONVENTIONS["thomson_eigenvalues"] == (1.0, 0.0, 0.1, 0.0)


def test_matches_dense_matrix_exponential(grid):
    """★★ dense expm 심판 (계약 임계 1e−13)."""
    sph, e, w, f = grid
    tol = C.budget("Q7", "vs_taylor")
    M = X.dense_operator(sph)
    for x in (0.01, 0.1, 1.0, 5.0, 50.0):
        ref = X.dense_expm_apply(M, f, x)
        got = X.collide(sph, f, x)
        rel = float(np.abs(got - ref).max() / np.abs(ref).max())
        assert rel <= tol, (x, rel)


def test_no_switching_stiff_limit_exact(grid):
    """★★ 계약 §3 '근사 절환 부재' 의 시험 ID.

    νΔτ = 10⁶ 에서 발산·오버플로 없이 **정확히** 등방화 극한 P₀f 로 떨어진다.
    ⇒ tight-coupling 근사로 갈아탈 이유가 존재하지 않는다."""
    sph, e, w, f = grid
    x = C.budget("Q7", "stiff_x")
    got = X.collide(sph, f, x)
    p0 = np.asarray(sph.project_l(np.ascontiguousarray(f), 0))
    assert np.isfinite(got).all()
    assert float(np.abs(got - p0).max()) <= 1e-12


def test_isotropization_rates_match_analytic(grid):
    """l=1 은 e^{−ντ}, l=2 는 e^{−0.9ντ} (계약 임계)."""
    sph, e, w, f = grid
    tol = C.budget("Q7", "rate")
    for l, rate in ((1, 1.0), (2, 0.9)):
        base = np.asarray(sph.project_l(np.ascontiguousarray(f), l))
        for x in (0.3, 2.0):
            out = X.collide(sph, f, x)
            got = np.asarray(sph.project_l(np.ascontiguousarray(out), l))
            assert float(np.abs(got - np.exp(-rate * x) * base).max()) <= tol


def test_number_conserved_and_positive(grid):
    sph, e, w, f = grid
    tol = C.budget("Q7", "number")
    pos = np.exp(2.0 * e[:, 2])
    n0 = float((w * pos).sum())
    for x in (0.05, 1.0, 20.0, 1e4):
        out = X.collide(sph, pos, x)
        assert (out > 0).all(), x
        assert abs(float((w * out).sum()) - n0) / n0 <= tol


def test_rust_matches_python_reference(grid):
    sph, e, w, f = grid
    for kern in ("thomson", "bgk", "bgk_cons"):
        for x in (0.2, 3.0):
            a = X.collide(sph, f, x, kern)
            b = X.collide_ref(sph, f, x, kern)
            assert float(np.abs(a - b).max()) <= 1e-13, (kern, x)


def test_bgk_ladder_conserves_what_it_claims(grid):
    """BGK-등방은 수만, BGK-보존형은 수+운동량 보존."""
    sph, e, w, f = grid
    pos = np.exp(1.5 * e[:, 0])
    n0 = float((w * pos).sum())
    q0 = np.einsum("a,ai->i", w * pos, e)
    a = X.collide(sph, pos, 2.0, "bgk")
    b = X.collide(sph, pos, 2.0, "bgk_cons")
    for out in (a, b):
        assert abs(float((w * out).sum()) - n0) / n0 <= 1e-14
    qa = np.einsum("a,ai->i", w * a, e)
    qb = np.einsum("a,ai->i", w * b, e)
    assert float(np.abs(qb - q0).max()) <= 1e-13         # 보존형은 운동량 유지
    assert float(np.abs(qa - q0).max()) > 1e-3           # 등방형은 감쇠


def test_comoving_log_path_matches_linear_path():
    """★ 공변격자 (로그공간) 경로 ≡ 선형 경로 — 두 구현의 교차."""
    sph = S.sphere(16, 32)
    e, w = S.nodes(sph)
    lG = 2.0 * e[:, 2]
    lw = np.log(w)
    for x in (0.1, 1.0, 8.0):
        lg = CM.collide_log(lw, lG, e, x)
        lin = X.collide_ref(sph, np.exp(lG), x)
        rel = float(np.abs(np.exp(lg) - lin).max() / np.abs(lin).max())
        assert rel <= 1e-11, (x, rel)


def test_modeb_applies_same_operator_to_every_radial_slice():
    """★ 에너지-교환 정리: 핵이 λ-무관 ⇒ 반경마다 같은 연산."""
    sph = S.sphere(16, 32)
    e, w = S.nodes(sph)
    n_p = 5
    rng = np.random.default_rng(2)
    ang = 1.0 + 0.5 * rng.standard_normal(len(w))
    rad = np.array([0.3, 1.0, 2.5, 7.0, 11.0])
    f = (ang[:, None] * rad[None, :]).ravel()
    out = X.collide_modeb(sph, f, n_p, 1.7).reshape(len(w), n_p)
    ref = X.collide(sph, ang, 1.7)
    for j in range(n_p):
        assert float(np.abs(out[:, j] - ref * rad[j]).max()) <= 1e-12
