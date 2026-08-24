"""
R5c · **정확구적을 이미 있던 Rust 커널로 라우팅** — 커널을 새로 만들지 않은 증분.

R5b 후 프로파일이 보인 것: tilted 시험 54.6 s 중 **43.4 s 가 `J_moment_tilted`**
(1815 회).  그런데 `kin_j_moment_tilted` 는 H5-e 때 이미 Rust 에 있었고 차등테스트로
1e−12 에 묶여 있었다 — **아무도 그 디스패치를 부르지 않았을 뿐이다** (`backend.py` 를
거치는 호출자가 없었다).  이번 증분은 디스패치를 `J_moment_tilted` / `J_moment`
**안으로** 옮겨 모든 호출자가 자동으로 Rust 를 타게 한다.

★ 속도 (이 컨테이너에서 재측정):
```
J_moment_tilted   numpy 21.0 ms → rust 2.8 ms   (7.4배)
J_moment          numpy 18.4 ms → rust 2.7 ms   (6.8배)
기준 5파일 블록   115.5 s (R5a) → 70.6 s (R5b) → 16.9 s (R5c)
```

★★ **두 함수를 함께 갈아끼워야 한다** — v=0 비트-정확 쌍 때문이다.
  `test_h5d_tilted_moments.test_zero_tilt_is_bit_exact` 는 J(v=0) ↔ J′(v=0) 가
  마지막 비트까지 같음을 요구한다.  이 불변식은 numpy 쌍끼리, Rust 쌍끼리는 성립하지만
  (각각 피적분함수가 문자 그대로 같다) **섞으면 깨진다** (rust−numpy ~1e−15·ρ).
  한쪽만 라우팅했으면 그 시험이 깨졌을 것이다 — 여기서 그 사실 자체를 게이트로 둔다.

★★ 오라클 고정이 취향이 아니라 **산술적 필요**인 지점:
  `audit.h5d_tilted_residual.moment_grid` 는 dt=1e−5 중앙차분의 원료다.  백엔드 차
  ~3e−14 는 값으로는 무해하지만 차분을 지나며 **1/(2dt) 배 증폭**되어 ~1e−9 가 된다
  — 잔차 게이트 1.5e−10 을 넘는다.  그래서 audit 은 `backend="python"` 에 못박았고,
  증폭이 실재함을 여기서 측정으로 고정한다.

★ f₀ 인식 규칙: Rust 커널은 f₀ 콜백을 받지 않는다.  페르미-디랙과, base 가 기본인
  `f_dipole(eps, axis)` (반환 클로저에 `_rust_dipole` 표식) 만 라우팅하고 나머지는
  numpy 폴백 — **조용히 다른 분포를 적분하는 것보다 느린 쪽이 낫다**.
"""
import time

import numpy as np
import pytest

from bianchi.matter import freestream as fs
from bianchi.matter import hierarchy as HH
from bianchi.matter import tilted_moments as TM

pytestmark = pytest.mark.skipif(TM._RC is None,
                                reason="bianchi_rustcore 없음 (numpy 폴백만)")

A = np.array([1.05, 0.93, 1.22])
V = np.array([0.08, -0.05, 0.12])


# ═══════════════════════════════════════ 두 경로 대조
@pytest.mark.parametrize("mass", [0.0, 0.7, 3.0])
def test_the_dispatch_matches_the_numpy_oracle(mass):
    """★★ 디스패치가 켠 Rust 값이 numpy 오라클과 1e−12(ρ 규격) 안에서 같다."""
    rho = TM.J_moment_tilted(A, V, mass, 0, 0, backend="python")
    for l in range(6):
        for i in (-1, 0, 1, 2):
            r = np.atleast_1d(np.asarray(TM.J_moment_tilted(A, V, mass, l, i),
                                         float)).ravel()
            p = np.atleast_1d(np.asarray(
                TM.J_moment_tilted(A, V, mass, l, i, backend="python"),
                float)).ravel()
            assert np.abs(r - p).max() / rho < 1e-12, (mass, l, i)


def test_the_plain_moment_dispatch_matches_too():
    """★ `hierarchy.J_moment` 도 같은 규칙 — 쌍극 f₀ 포함."""
    fd = HH.f_dipole(0.4, 2)
    rho = HH.J_moment(A, 0.7, 0, 0, backend="python")
    for l in range(6):
        for f0 in (fs.f_fermi_dirac, fd):
            r = np.atleast_1d(np.asarray(HH.J_moment(A, 0.7, l, 0, f0), float))
            p = np.atleast_1d(np.asarray(HH.J_moment(A, 0.7, l, 0, f0,
                                                     backend="python"), float))
            assert np.abs(r - p).max() / rho < 1e-12, (l, f0)


# ═══════════════════════════════════════ ★★ 왜 둘을 함께 갈아끼웠는가
def test_the_zero_tilt_pair_is_bit_exact_within_the_rust_backend():
    """★★ v=0 쌍 J ↔ J′ 이 **Rust 쌍끼리** 마지막 비트까지 같다 (l=0..5).

    기존 시험(`test_zero_tilt_is_bit_exact`)이 R5c 후에도 손대지 않고 통과하는 근거.
    """
    z = np.zeros(3)
    for l in range(6):
        for i in (0, 1):
            j0 = np.atleast_1d(np.asarray(HH.J_moment(A, 0.7, l, i), float))
            jt = np.atleast_1d(np.asarray(TM.J_moment_tilted(A, z, 0.7, l, i),
                                          float))
            assert np.array_equal(j0, jt), (l, i)


def test_mixing_backends_would_break_the_pair():
    """★★ **한쪽만 라우팅했으면 깨졌다** — rust 와 numpy 는 어딘가에서 비트가 다르다.

    이게 실패하면(두 백엔드가 전 격자 비트-동일) 함께-교체 논거가 필요 없었던 것이므로
    문서를 고쳐야 한다.
    """
    differs = False
    for l in range(4):
        for i in (0, 1):
            r = np.atleast_1d(np.asarray(TM.J_moment_tilted(A, V, 0.7, l, i),
                                         float)).ravel()
            p = np.atleast_1d(np.asarray(
                TM.J_moment_tilted(A, V, 0.7, l, i, backend="python"),
                float)).ravel()
            differs = differs or not np.array_equal(r, p)
    assert differs


# ═══════════════════════════════════════ f₀ 인식 규칙
def test_a_custom_f0_falls_back_to_numpy():
    """★★ 알아볼 수 없는 f₀ 는 폴백 — 조용히 페르미-디랙을 적분하면 안 된다.

    폴백이면 두 호출이 **비트-동일**해야 한다 (같은 numpy 경로).
    """
    def custom(q):
        return fs.f_fermi_dirac(q) * (1.0 + 0.1 * np.tanh(q))
    a = HH.J_moment(A, 0.7, 2, 0, custom)
    b = HH.J_moment(A, 0.7, 2, 0, custom, backend="python")
    assert np.array_equal(np.asarray(a), np.asarray(b))
    # 그리고 페르미-디랙과는 실제로 다른 값이다 (폴백이 무의미하지 않다)
    c = HH.J_moment(A, 0.7, 2, 0, backend="python")
    assert not np.allclose(np.asarray(a), np.asarray(c), rtol=1e-6)


def test_a_dipole_with_a_nonstandard_base_is_not_marked():
    """★ base ≠ 페르미-디랙인 f_dipole 은 표식이 없다 — Rust 로 가면 틀린 분포다."""
    fd = HH.f_dipole(0.3, 2, base=fs.f_bose_einstein)
    assert getattr(fd, "_rust_dipole", None) is None
    assert HH.rust_f0_args(fd) is None


def test_the_default_dipole_is_marked():
    fd = HH.f_dipole(0.4, 1)
    assert fd._rust_dipole == (0.4, 1)
    assert HH.rust_f0_args(fs.f_fermi_dirac) == (0.0, 2)


def test_out_of_range_l_falls_back():
    """★ l > 5 (Rust codegen 한계) 는 폴백 — 예외가 아니라 값이 나와야 한다."""
    r = HH.J_moment(A, 0.0, 6, 0)
    p = HH.J_moment(A, 0.0, 6, 0, backend="python")
    assert np.array_equal(np.asarray(r), np.asarray(p))


# ═══════════════════════════════════════ ★★ 오라클 고정의 산술적 근거
def test_the_audit_grid_is_pinned_to_python():
    """★★ audit 격자가 라우팅 후에도 numpy 오라클과 비트-동일하다."""
    from audit import h5d_tilted_residual as R
    g = R.moment_grid(A, V, 0.7, l_max=2, i_max=1)
    for (l, i), val in g.items():
        p = np.asarray(TM.J_moment_tilted(A, V, 0.7, l, i, backend="python"),
                       float)
        assert np.array_equal(np.asarray(val, float), p), (l, i)


def test_finite_differencing_amplifies_the_backend_gap_past_the_audit_gate():
    """★★ 백엔드 차가 dt=1e−5 중앙차분에서 1/(2dt) 배로 증폭됨을 **격자 전체로** 측정.

    ★ 반증 기록: 처음엔 소박한 추정 |Δ|_max/(2dt) = 3.3e−14/2e−5 ≈ 1.6e−9 라 적고
      (l,i)=(2,0) 한 점만 쟀다 — 9.4e−11 이 나와 게이트(1.5e−10) **아래**였다.
      성분별 백엔드 차가 최악값보다 대체로 작기 때문이다.  격자 전체(l≤3, i≤3)를
      재니 최악은 (1,0) 의 **1.78e−10** — 추정보다 9배 작지만 여전히 게이트를 넘는다.
      ⇒ 결론(왜 audit 을 못박는가)은 살아남았고, 크기 추정은 고쳤다.
      증폭 최악값이 게이트의 1/10 아래로 내려가면 고정을 풀어도 되므로 이 시험이
      그 결정을 감시한다.
    """
    dt, mass = 1e-5, 0.7
    da = np.array([0.35, 0.28, 0.42])
    rho = TM.J_moment_tilted(A, V, mass, 0, 0, backend="python")

    def dJ(l, i, backend):
        p = np.atleast_1d(np.asarray(TM.J_moment_tilted(
            A + da * dt, V, mass, l, i, backend=backend), float))
        m = np.atleast_1d(np.asarray(TM.J_moment_tilted(
            A - da * dt, V, mass, l, i, backend=backend), float))
        return (p - m) / (2.0 * dt)

    worst = max(float(np.abs(dJ(l, i, None) - dJ(l, i, "python")).max() / rho)
                for l in range(4) for i in (-1, 0, 1, 2, 3))
    assert worst > 1.5e-11, f"증폭이 게이트의 1/10 아래다 ({worst:.2e}) — 고정 재검토"
    assert worst < 1e-8, f"증폭이 측정(1.8e−10)보다 두 자릿수 크다 ({worst:.2e})"


def test_the_rustcore_differential_reference_is_not_vacuous():
    """★ 차등테스트의 python 참조가 명시적 `backend="python"` 을 쓴다 (회귀).

    디스패치를 함수 안으로 옮기면 옛 참조가 조용히 Rust 가 되어 Rust 대 Rust 의
    공허한 비교가 된다 — 소스에서 못박음을 확인한다.
    """
    import pathlib
    src = pathlib.Path(__file__).with_name("test_rustcore_differential.py").read_text()
    assert 'J_moment(a, mass, l, i, f0,\n                                                backend="python")' in src \
        or 'backend="python"' in src.split("def _kin_pyref")[1].split("def ")[0]


# ═══════════════════════════════════════ 효과
def test_the_dispatch_is_actually_faster():
    """★ 이 증분의 목적 — 대표 호출에서 3배 이상 (측정 7.4배)."""
    TM.J_moment_tilted(A, V, 1.0, 3, 1)                    # 워밍업
    t0 = time.perf_counter()
    for _ in range(10):
        TM.J_moment_tilted(A, V, 1.0, 3, 1)
    t_rust = time.perf_counter() - t0
    t0 = time.perf_counter()
    for _ in range(10):
        TM.J_moment_tilted(A, V, 1.0, 3, 1, backend="python")
    t_py = time.perf_counter() - t0
    assert t_py / t_rust > 3.0, (t_py, t_rust)


def test_production_diagnostics_agree_across_backends():
    """★ L2/L3 진단(비 수열)이 두 백엔드에서 1e−12 로 같다 — 생산 경로의 종단 확인."""
    from bianchi.matter import tilted_closure as TC
    r_rust = TC.exact_ratio_sequence(1.0, l=2, i_max=3)
    TM_call = TM.J_moment_tilted
    seq = []
    for i in range(5):
        seq.append(np.abs(np.atleast_1d(np.asarray(
            TM_call((1.0, 0.9, 1.2), (0.08, -0.05, 0.12), 1.0, 2, i,
                    backend="python"), float))).max())
    r_py = [seq[i + 1] / max(seq[i], 1e-300) for i in range(4)]
    for a, b in zip(r_rust, r_py):
        assert abs(a - b) < 1e-12
