"""
Q1 · **11유형 통합 군 코어** 게이트 (76차).

측정·게이트 (임계는 계약에서 읽는다 — 시험이 스스로 정하지 않는다):
  · ★ 12개 이름 전부 Rust 분류 ≡ Python `bianchi.algebra.classify` (문자열 동일)
  · ★ 포장 왕복 (n(3,3) → 6성분 → (3,3)) **비트 동일**
  · Jacobi 잔차 ≤ 1e-15 (정준 상태 전부)
  · 구조상수 ≡ Python `algebra.structure_constants` 비트급
  · ricci3 ≡ Python `charts.general.ricci3` (dense 경로 대조)
  · ^3R 닫힌형 −tr(N²)+½(trN)²−6A·A 와 대조 (독립 공식)
  · 예외형은 상수 κ=−9 가 아니라 **구속 퇴화 det L = 0** 으로 잡힌다
  · 부호서명 보존: N_i = 0 이 정확히 0
"""
import numpy as np
import pytest

RC = pytest.importorskip("bianchi_rustcore")
pytest.importorskip("bianchi_rustcore").qg_classify  # 신규 심볼 없으면 스킵

from bianchi import algebra as AL  # noqa: E402
from bianchi.q import contract as C  # noqa: E402
from bianchi.q import group as G  # noqa: E402

NAMES = list(AL.CANONICAL)


@pytest.mark.parametrize("name", NAMES)
def test_rust_classification_matches_python_oracle(name):
    """★★ 12개 이름 전부 — Rust 포트 ≡ Python 단일 진실원."""
    n, a = AL.CANONICAL[name]
    got = G.classify(n, a)
    ref = AL.classify(n, a)
    assert got["name"] == ref.name == name, (got, ref)
    assert got["group_class"] == ref.group_class
    assert got["exceptional"] == ref.exceptional
    if ref.kappa is None:
        assert got["kappa"] is None
    else:
        assert abs(got["kappa"] - ref.kappa) <= 1e-12


@pytest.mark.parametrize("name", NAMES)
def test_packing_roundtrip_is_bitwise(name):
    """★ 포장 왕복 비트 동일 (계약 임계: 'bitwise')."""
    assert C.budget("Q1", "roundtrip") == "bitwise"
    n, a = AL.CANONICAL[name]
    N = np.diag(np.asarray(n, float))
    N2, a2 = G.roundtrip(N, a)
    assert np.array_equal(N, N2)
    assert np.array_equal(np.asarray(a, float), a2)


@pytest.mark.parametrize("name", NAMES)
def test_jacobi_residual_within_budget(name):
    n, a = AL.CANONICAL[name]
    r = G.jacobi_residual(n, a)
    assert float(np.abs(r).max()) <= C.budget("Q1", "jacobi")


def test_structure_constants_match_python():
    """★ C^c_ab 비트급 대조 — 지표 배열까지 같은지."""
    rng = np.random.default_rng(3)
    for _ in range(20):
        # Jacobi 를 만족시키는 임의 상태: a 를 n 의 영공간으로
        n_diag = rng.standard_normal(3)
        n_diag[0] = 0.0
        N = np.diag(n_diag)
        a = np.array([rng.standard_normal(), 0.0, 0.0])
        got = G.structure_constants(N, a)
        ref = AL.structure_constants(N, a)
        assert float(np.abs(got - ref).max()) <= 1e-15


def test_ricci3_matches_general_chart():
    """★ Rust ricci3 ≡ jax dense 경로 (charts.general)."""
    import jax
    jax.config.update("jax_enable_x64", True)
    from bianchi.charts import general as GEN
    rng = np.random.default_rng(11)
    tol = C.budget("Q1", "ricci3")
    for _ in range(20):
        n_diag = rng.standard_normal(3); n_diag[0] = 0.0
        N = np.diag(n_diag) + 0.0
        A = np.array([rng.standard_normal(), 0.0, 0.0])
        got = G.ricci3(N, A)
        ref = np.asarray(GEN.ricci3(N, A))
        assert float(np.abs(got - ref).max()) <= tol, (got, ref)


def test_R3_matches_independent_closed_form():
    """^3R = −tr(N²) + ½(tr N)² − 6 A·A — 유도가 다른 독립 공식."""
    rng = np.random.default_rng(5)
    for _ in range(20):
        n_diag = rng.standard_normal(3); n_diag[0] = 0.0
        N = np.diag(n_diag)
        A = np.array([rng.standard_normal(), 0.0, 0.0])
        want = -np.trace(N @ N) + 0.5 * np.trace(N) ** 2 - 6.0 * float(A @ A)
        got = float(np.trace(G.ricci3(N, A)))
        assert abs(got - want) <= 1e-12, (got, want)


def test_exceptional_detected_by_constraint_degeneracy_not_kappa_constant():
    """★ 예외형은 κ=−9 상수가 아니라 det L = 3(9A²+n₂n₃) = 0 으로 잡힌다."""
    for a in (0.3, 1.0, 2.5):
        n2 = 3.0 * a
        n3 = -3.0 * a          # n2 n3 = -9 a^2
        c = G.classify(np.array([0.0, n2, n3]), np.array([a, 0.0, 0.0]))
        assert c["exceptional"], (a, c)
        assert c["name"] == "VI*_-1/9"
        assert abs(c["kappa"] + 9.0) <= 1e-9


def test_zero_n_components_stay_exactly_zero():
    """부호서명 보존 — 0 은 정확히 0 (class A 곱셈구조의 전제)."""
    N = np.diag([1.0, 0.0, 0.0])
    A = np.zeros(3)
    C3 = G.structure_constants(N, A)
    assert G.classify(N, A)["name"] == "II"
    # n2 = n3 = 0 이면 대응 구조상수 성분이 **정확히** 0
    assert C3[1, 2, 0] == 0.0 and C3[2, 0, 1] == 0.0
