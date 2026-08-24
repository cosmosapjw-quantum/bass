"""
R5a · **일반 rank tilted 텐서 커널을 Rust 로** — 그리고 그게 왜 부족한지.

프로파일 (tilted 적분 4.55 s → R3 이후 2.45 s, l_max=3, i_max=3, 20 스텝):
```
tensordot            52480 회   1.49 s (누적)   ← to_coord / covariant_derivative
equation_lhs                    2.46 s (누적)
covariant_derivative             0.58 s
to_coef / pack / matvec          0.90 s
```
**어느 한 곳도 지배하지 않는다** — 작은 배열에 대한 numpy 호출이 수만 번이라 호출
오버헤드가 고르게 깔려 있다.  이 파일은 그 중 텐서층(⊥Ẋ, D_B X, D^aJ, D_{⟨a⟩}J)을
Rust 로 옮긴 것을 고정한다.

★ 정확도: 값이 **비트-정확** 동일하다 (궤적오차 rho/q/pi 모두 차 0.00e+00).
  텐서층 자체도 rank 0~3 에서 5.3e−16 이내.

★★ **그런데 속도는 1.32배뿐이다** — 이게 이번 증분의 진짜 결과다.
```
trajectory_error(l=3,i=3,20스텝)   python 2.45 s → rust 1.86 s   1.32배
```
R1/R2 의 type V 커널이 10~35000 배였던 것과 대조된다.  차이는 **경계를 넘는 횟수**다:
type V 는 RK4 루프 전체가 Rust 안에 있어 노드가 Python 으로 돌아오지 않았는데,
여기서는 (l,i) 조합마다 작은 배열을 주고받는다.  FFI 왕복과 배열 생성이 이득을 먹는다.

⇒ **결론**: tilted 계층은 층별로 떼어 옮겨서는 안 되고, `equation_lhs` + 질량행렬 +
  RK4 루프를 **통째로** Rust 로 옮겨야 한다 (R5b).  이 파일의 커널이 그 토대다.
"""
import numpy as np
import pytest

from bianchi.backend_policy import BackendPolicy
from bianchi.matter import tilted_terms as TT

pytestmark = pytest.mark.skipif(not TT.available(),
                                reason="bianchi_rustcore 없음 (numpy 폴백만)")

GEO_ARGS = ((1.0, 0.9, 1.2), (0.35, 0.28, 0.42), (0.08, -0.05, 0.12),
            (0.015, 0.01, -0.02))


def _geo():
    return TT.geometry(*GEO_ARGS)


@pytest.mark.parametrize("r", [0, 1, 2, 3])
def test_perp_dot_matches_numpy(r):
    """★★ ⊥Ẋ — 사틀 회전항까지 포함해 numpy 판과 기계정밀도로 같다."""
    geo = _geo()
    rng = np.random.default_rng(3 + r)
    X, dX = rng.normal(size=(3,) * r), rng.normal(size=(3,) * r)
    a = np.asarray(TT.perp_dot(X, dX, geo, backend="python"), float)
    b = np.asarray(TT.perp_dot(X, dX, geo), float)
    assert np.abs(a - b).max() / max(np.abs(a).max(), 1e-300) < 1e-14


@pytest.mark.parametrize("r", [0, 1, 2, 3])
def test_spatial_derivative_matches_numpy(r):
    """★ D_B X — 반환 축 순서 (B, A₁…A_r) 까지 같다."""
    geo = _geo()
    rng = np.random.default_rng(11 + r)
    X, dX = rng.normal(size=(3,) * r), rng.normal(size=(3,) * r)
    a = np.asarray(TT.spatial_derivative(X, dX, geo, backend="python"), float)
    b = np.asarray(TT.spatial_derivative(X, dX, geo), float)
    assert a.shape == b.shape
    assert np.abs(a - b).max() / np.abs(a).max() < 1e-14


@pytest.mark.parametrize("r", [1, 2, 3])
def test_div_contracted_matches_numpy(r):
    """★ D^aJ_{aA_l} — 축약하는 축이 (B, A₁) 임을 실측으로 맞췄다."""
    geo = _geo()
    rng = np.random.default_rng(23 + r)
    X, dX = rng.normal(size=(3,) * r), rng.normal(size=(3,) * r)
    a = np.asarray(TT.div_contracted(X, dX, geo, backend="python"), float)
    b = np.asarray(TT.div_contracted(X, dX, geo), float)
    assert np.abs(a - b).max() / max(np.abs(a).max(), 1e-300) < 1e-14


@pytest.mark.parametrize("l", [1, 2, 3])
def test_div_free_index_matches_numpy(l):
    """★ D_{⟨a_l}J_{A_{l−1}⟩} — PSTF 는 Python 에 남겼고 그 앞까지가 Rust 다."""
    geo = _geo()
    rng = np.random.default_rng(31 + l)
    X, dX = rng.normal(size=(3,) * (l - 1)), rng.normal(size=(3,) * (l - 1))
    a = np.asarray(TT.div_free_index(X, dX, geo, l, backend="python"), float)
    b = np.asarray(TT.div_free_index(X, dX, geo, l), float)
    assert np.abs(a - b).max() / np.abs(a).max() < 1e-14


def test_typed_python_operator_never_calls_native_fallback(monkeypatch):
    """명시적 typed Python 오라클은 같은 연산자를 쓰며 native를 호출하지 않는다."""
    geo = _geo()
    X = np.arange(9.0).reshape(3, 3)
    dX = np.linspace(-0.75, 0.5, 9).reshape(3, 3)
    expected = np.asarray(TT.perp_dot(X, dX, geo, backend="python"), float)

    def unexpected_native(*args, **kwargs):
        raise AssertionError("typed Python oracle called the native tensor kernel")

    monkeypatch.setattr(TT, "_rc_call", unexpected_native)
    observed = np.asarray(
        TT.perp_dot(X, dX, geo, backend=BackendPolicy.PYTHON_ORACLE), float
    )
    np.testing.assert_array_equal(observed, expected)


def test_the_numpy_oracle_is_still_reachable():
    """★ 포트가 오라클을 지우지 않았다 — `backend="python"` 이 살아 있다."""
    geo = _geo()
    X = np.arange(9.0).reshape(3, 3)
    a = TT.perp_dot(X, X * 0.5, geo, backend="python")
    assert np.asarray(a).shape == (3, 3)
    assert np.isfinite(np.asarray(a)).all()


def test_geometry_arrays_are_marshalled_once():
    """★ geo 배열을 매 호출 복사하지 않는다 (캐시가 붙는다)."""
    geo = _geo()
    assert "_rc" not in geo
    TT.perp_dot(np.zeros(3), np.zeros(3), geo)
    assert "_rc" in geo and len(geo["_rc"][1]) == 6


def test_a_modified_geo_is_not_served_from_the_cache():
    """★★ **버그 회귀** — `dict(geo, deup=0)` 대조군이 옛 캐시를 물려받으면 안 된다.

    처음 판은 그래서 사틀 회전항 대조군을 조용히 무력화했다
    (`test_h5d_residual.py::test_tetrad_rotation_term_is_not_negligible` 이 잡았다).
    """
    geo = _geo()
    X = np.asarray(TT.TL._DEF["q"], float) if hasattr(TT, "TL") else np.ones(3)
    rng = np.random.default_rng(5)
    X, dX = rng.normal(size=3), rng.normal(size=3)
    full = np.asarray(TT.perp_dot(X, dX, geo), float)          # 캐시를 만든다
    flat = dict(geo, deup=np.zeros_like(np.asarray(geo["deup"])))
    naive = np.asarray(TT.perp_dot(X, dX, flat), float)
    assert np.abs(full - naive).max() > 1e-6 * np.abs(full).max(), (full, naive)
