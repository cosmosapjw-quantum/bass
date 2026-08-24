"""
R5b · **tilted 계층 전체를 Rust 로** — 식(12) 좌변 + 질량행렬 + 선형해 + RK4 를 한 호출로.

R5a 는 텐서층만 옮겨 **1.32배**에 그쳤다.  원인은 (l,i) 조합마다 작은 배열이 FFI 를
넘나든 것이었다.  여기서는 루프 전체가 Rust 안에 있고 J 가 Python 으로 돌아오지 않는다.

★ 속도 (l_max=3, i_max=3, 20 스텝, m=1):
```
Rust 커널        0.061 s
Python 루프      1.678 s        → 28배
```
같은 척도에서 R5a 는 1.32배였다.  차이는 **경계를 넘는 횟수**뿐이다.

★★ 처음 판을 계수로 반증했다 — 기본 경로만 옮겼더니 tilted 시험 **1260 적분스텝 중
  310 스텝(25%)** 만 Rust 로 갔다.  나머지는 전부 대조군이었다:
```
frozen + J̇닫힘끔   450 스텝     ratio + n_* 삼각절단   260 스텝
phys_sqrt/phys_5w  160 스텝     frozen + J̇닫힘        60 스텝
```
  대조군이 느리면 전체 벽시계는 그대로다.  그래서 `tilted_closure.MODES` 전부와
  J̇ 닫힘 on/off, 삼각절단까지 옮겼다.  결과 (5 개 tilted 시험파일):
```
115.5 s  →  70.6 s
```

★ **비트-정확은 되지 않는다** (R5a 와 다르다) — 그리고 **어디서 깨지는지 정확히**
  가려 두었다:
```
F (좌변)  l = 0 블록          : 비트-정확
F (좌변)  나머지             : ≤ 1.5e−17 (ρ 규격)  = 1 ulp
M (질량행렬)                 : 2.2e−16             = 1 ulp
같은 (M,F) 로 LAPACK 대 Rust-LU : 2.6e−17
전 경로 Python 대 Rust          : 5.1e−17   (cond(M) = 1.37 이라 증폭이 없다)
```
  즉 **항 조립은 정확하고, 남는 차이는 전부 작은 numpy 커널의 합 순서**다.

★★ **반증 기록** — 처음에는 "PSTF 를 안 쓰는 l < 2 층은 비트-정확" 이라고 적고
  그대로 시험을 세웠다.  i_max=1 에서는 통과했는데 i_max=2 의 (l,i)=(1,1) 에서
  3.6e−15 로 깨졌다.  블록을 하나씩 0 으로 만드는 이분법으로 좁히니 원인은 PSTF 가
  아니라
```
np.einsum("a,ba->b", J, σ)   대   순차합 Σ_a J_a σ_{ba}   →   1.4e−17 차이
```
  였다.  (그 자리에서 `np.tensordot` 과 `einsum("abi,ab->i")` 는 마침 같았지만,
  무작위 배열로 다시 재 보니 `tensordot` 도 어긋난다 — 즉 "이 커널은 안전하다" 는
  분류 자체가 성립하지 않는다.)  경계는 **"PSTF 를 쓰는가" 가 아니라 "numpy 축약
  커널을 타는가"** 이고, l=0 블록만 그 커널을 전혀 타지 않아 비트-정확이 남는다.
  설명을 고치고 게이트를 다시 세웠다.
"""
import time

import numpy as np
import pytest

from bianchi.matter import tilted_closure as TC
from bianchi.matter import tilted_equation as TE
from bianchi.matter import tilted_integrate as TI
from bianchi.matter import tilted_mass as TMass
from bianchi.matter import tilted_rust as TR

pytestmark = pytest.mark.skipif(not TR.USE_RUST,
                                reason="bianchi_rustcore 의 R5b 커널 없음")

L_MAX, I_MAX, MASS = 3, 2, 1.0


def _state(l_max=L_MAX, i_max=I_MAX, mass=MASS, n_star=None):
    bg = TI.Background()
    keys, _, _ = TMass.layout(l_max, i_max, n_star)
    J = {k: v for k, v in TI.initial_state(bg, mass, l_max, i_max).items()
         if k in keys}
    return bg, J, keys


def _python_force_and_matrix(J, geo, l_max, i_max, mode="ratio", jdot=True,
                             n_star=None):
    Jc = TI.closure(J, l_max, i_max, mode, n_star)
    zero = {k: np.zeros(np.asarray(Jc[k]).shape) for k in Jc}
    F = {(l, i): -np.asarray(TE.equation_lhs(Jc, zero, geo, l, i, None), float)
         for l in range(l_max + 1) for i in range(i_max + 1)}
    ir = (TC.jdot_ratio(Jc, l_max, i_max, mode)
          if (jdot and n_star is None) else None)
    return F, TMass.dense(geo, l_max, i_max, None, ir, n_star)


# ═══════════════════════════════════════ 층별 정확도
def _force_gaps(l_max=L_MAX, i_max=I_MAX, mass=MASS, n_star=None):
    """(l=0 이 비트-정확인가, 전 블록 ρ-규격 최대 상대차)."""
    bg, J, keys = _state(l_max, i_max, mass, n_star)
    geo = bg.geometry(0.03)
    f_r, _ = TR.force_and_matrix(J, geo, l_max, i_max, n_star=n_star)
    F, _ = _python_force_and_matrix(J, geo, l_max, i_max, n_star=n_star)
    scale = max(abs(float(np.atleast_1d(np.asarray(F[(0, 0)], float))[0])), 1e-300)
    p, exact0, worst = 0, True, 0.0
    for l in range(l_max + 1):
        d = 3 ** l
        for i in range(i_max + 1):
            a, b = f_r[p:p + d], np.atleast_1d(np.asarray(F[(l, i)], float)).ravel()
            p += d
            if (l, i) not in keys:
                continue
            if l == 0:
                exact0 = exact0 and np.array_equal(a, b)
            worst = max(worst, float(np.abs(a - b).max()) / scale)
    return exact0, worst


@pytest.mark.parametrize("cfg", [(3, 1, 1.0, None), (3, 2, 1.0, None),
                                 (3, 3, 0.0, None), (2, 2, 2.0, None),
                                 (3, 1, 1.0, 4), (3, 2, 4.0, 6)])
def test_the_l0_force_blocks_are_bit_identical(cfg):
    """★★ **가장 결정적** — numpy 축약 커널을 전혀 타지 않는 l=0 블록이 마지막
    비트까지 같다.  항 조립·부호·결합순서를 전부 맞췄다는 뜻이다.
    """
    l_max, i_max, mass, n_star = cfg
    exact0, _ = _force_gaps(l_max, i_max, mass, n_star)
    assert exact0


@pytest.mark.parametrize("cfg", [(3, 1, 1.0, None), (3, 2, 1.0, None),
                                 (3, 3, 0.0, None), (2, 2, 2.0, None),
                                 (3, 1, 1.0, 4), (3, 2, 4.0, 6)])
def test_the_remaining_force_blocks_match_to_one_ulp(cfg):
    """★ 나머지는 1 ulp — `einsum`/`@` 의 합 순서 때문이다.  크기를 고정한다."""
    l_max, i_max, mass, n_star = cfg
    _, worst = _force_gaps(l_max, i_max, mass, n_star)
    assert worst < 1e-15, worst


def test_the_residual_really_comes_from_a_numpy_contraction_kernel():
    """★★ **반증 기록의 근거** — 작은 numpy 축약이 순차합과 마지막 비트에서 다르다.

    이게 전부 비트-정확이 되면 위 설명이 틀린 것이므로 기록을 고쳐야 한다
    (그 경우 F 도 전 블록 비트-정확이어야 한다).

    ★ 두 커널을 함께 잰다 — 처음에는 `tensordot` 을 "안전한 쪽" 으로 분류했다가
      무작위 배열에서 반증됐다.  안전한 커널 같은 것은 없다.
    """
    rng = np.random.default_rng(0)
    sig, j, a2 = rng.normal(size=(3, 3)), rng.normal(size=3), rng.normal(size=(3, 3))
    seq = np.array([sum(j[a] * sig[b, a] for a in range(3)) for b in range(3)])
    differs = [not np.array_equal(np.einsum("a,ba->b", j, sig), seq),
               not np.array_equal(np.tensordot(a2, j, axes=([0], [0])),
                                  sum(a2[k] * j[k] for k in range(3)))]
    assert any(differs), differs


def test_the_mass_matrix_matches_numpy():
    """★★ 질량행렬을 **성분별로** 대조한다 (PSTF 기저를 Python 것으로 받았기에 가능)."""
    bg, J, _ = _state()
    geo = bg.geometry(0.03)
    _, m_r = TR.force_and_matrix(J, geo, L_MAX, I_MAX)
    _, m_p = _python_force_and_matrix(J, geo, L_MAX, I_MAX)
    assert m_r.shape == m_p.shape
    assert np.abs(m_r - m_p).max() < 1e-15, np.abs(m_r - m_p).max()


def test_bit_exactness_is_lost_only_in_the_linear_solve():
    """★★ **분해 시험** — 같은 (M, F) 를 두 선형해에 넣으면 차가 전 경로 차와 같은 크기다.

    ⇒ 남는 불일치의 정체는 항 조립이 아니라 LAPACK `dgesv` 대 Rust 부분추축 LU 의
      합 순서다.  cond(M) ≈ 1.4 라 증폭도 없다.
    """
    bg, J, keys = _state()
    geo = bg.geometry(0.05)
    f_flat, M = TR.force_and_matrix(J, geo, L_MAX, I_MAX)
    b = TMass.pack(TR.unpack_state(f_flat, L_MAX, I_MAX, set(keys)), L_MAX, I_MAX)
    x_lapack = np.linalg.solve(M, b)
    x_rust = TMass.pack(TR.rhs(J, geo, L_MAX, I_MAX, keys=set(keys)), L_MAX, I_MAX)
    x_python = TMass.pack(TI.rhs(J, bg, 0.05, L_MAX, I_MAX), L_MAX, I_MAX)
    sc = np.abs(x_python).max()
    solve_only = float(np.abs(x_lapack - x_rust).max()) / sc
    end_to_end = float(np.abs(x_python - x_rust).max()) / sc
    assert float(np.linalg.cond(M)) < 5.0
    assert solve_only < 1e-15
    assert end_to_end < 1e-15
    # 전 경로 차가 선형해 차와 **같은 자릿수**여야 한다 (조립이 추가 오차를 안 냈다)
    assert end_to_end <= 10.0 * max(solve_only, 1e-18)


# ═══════════════════════════════════════ 궤적 (전 모드)
@pytest.mark.parametrize("mode", ["ratio", "frozen", "ratio_scalar",
                                  "phys_sqrt", "phys_5w", "phys_interp"])
@pytest.mark.parametrize("jdot", [True, False])
def test_the_trajectory_matches_the_numpy_oracle(mode, jdot):
    """★★ 모드 × J̇ 닫힘 전 조합에서 궤적오차가 numpy 오라클과 1e−12 이내로 같다."""
    bg = TI.Background()
    a = TI.trajectory_error(bg, MASS, 0.2, 10, L_MAX, I_MAX, mode=mode,
                            jdot_closure=jdot)
    b = TI.trajectory_error(bg, MASS, 0.2, 10, L_MAX, I_MAX, mode=mode,
                            jdot_closure=jdot, backend="python")
    assert set(a) == set(b)
    for k in a:
        assert abs(a[k] - b[k]) <= 1e-12 * max(b[k], 1e-300), (k, a[k], b[k])


@pytest.mark.parametrize("n_star", [2, 3, 4])
def test_the_triangular_truncation_matches(n_star):
    """★ L1 의 삼각 절단 l + 2i ≤ n_* — 상태공간 자체가 줄어드는 경로."""
    bg = TI.Background()
    a = TI.trajectory_error(bg, MASS, 0.2, 10, L_MAX, 1, n_star=n_star)
    b = TI.trajectory_error(bg, MASS, 0.2, 10, L_MAX, 1, n_star=n_star,
                            backend="python")
    for k in a:
        assert abs(a[k] - b[k]) <= 1e-12 * max(b[k], 1e-300), (k, a[k], b[k])


def test_the_history_keys_match_the_python_layout():
    """★ 이력 dict 의 키가 절단 뒤에도 Python 배치와 같다 (삼각절단이면 줄어든다)."""
    bg = TI.Background()
    for n_star in (None, 3):
        keys, _, _ = TMass.layout(L_MAX, 1, n_star)
        h = TI.integrate(bg, MASS, 0.05, 2, L_MAX, 1, n_star=n_star)
        assert set(h["J"][-1]) == set(keys), n_star
        assert len(h["t"]) == 3


# ═══════════════════════════════════════ 함정과 회귀
def test_the_half_step_times_are_the_same_floats_as_the_python_loop():
    """★★ **함정** — `(step+1)*dt` 와 `step*dt + dt` 는 부동소수에서 다르다.

    기하를 미리 만들어 넘기므로 시각을 Python 루프와 **같은 산술**로 만들어야 한다.
    스텝당 2 개(끝을 다음 스텝의 시작으로 재사용)로 줄이면 여기서 어긋난다.
    """
    dt = 0.2 / 40
    clash = [s for s in range(40) if (s + 1) * dt != s * dt + dt]
    assert clash, "이 dt 에서는 함정이 드러나지 않는다 — 시험이 무의미하다"
    rows = TR.geometry_rows(TI.Background(), 40, dt)
    s = clash[0]
    assert not np.array_equal(rows[3 * s + 2], rows[3 * (s + 1)])


def test_no_supported_mode_silently_falls_back_to_python():
    """★★ **회귀** — 대조군이 조용히 Python 으로 돌아가면 벽시계가 그대로다.

    처음 판이 정확히 그랬다 (1260 스텝 중 310 스텝만 Rust).
    """
    for mode in TC.MODES:
        assert TI.rust_available(mode), mode
    assert TI.rust_available("ratio", jdot_closure=False)
    assert TI.rust_available("ratio", n_star=3)


def test_state_packing_round_trips_including_the_truncated_blocks():
    """★ 절단으로 빠진 블록을 0 으로 채우고 되읽을 때 떨어뜨린다."""
    _, J, keys = _state(L_MAX, 1, MASS, n_star=3)
    flat = TR.pack_state(J, L_MAX, 1)
    back = TR.unpack_state(flat, L_MAX, 1, set(keys))
    assert set(back) == set(keys)
    for k in keys:
        assert np.allclose(np.atleast_1d(np.asarray(back[k], float)).ravel(),
                           np.atleast_1d(np.asarray(J[k], float)).ravel())


def test_the_numpy_oracle_is_still_reachable():
    """★ 포트가 오라클을 지우지 않았다 — `backend="python"` 이 살아 있다."""
    bg = TI.Background()
    h = TI.integrate(bg, 0.0, 0.05, 2, 2, 1, backend="python")
    assert len(h["J"]) == 3
    assert np.isfinite(np.asarray(h["J"][-1][(2, 0)])).all()


def test_the_kernel_is_much_faster_than_the_python_loop():
    """★★ 이 증분의 **목적** — 루프 전체를 옮겨야 이득이 난다는 R5a 의 결론을 확인.

    측정 28배 (R5a 는 같은 척도에서 1.32배).  게이트는 넉넉히 8배로 둔다.
    """
    bg = TI.Background()
    lm, im, ns = 3, 3, 20
    TI.integrate(bg, MASS, 0.2, 2, lm, im)                       # 워밍업
    keys, _, _ = TMass.layout(lm, im)
    J0 = {k: v for k, v in TI.initial_state(bg, MASS, lm, im).items() if k in keys}
    t0 = time.perf_counter()
    TR.integrate(bg, J0, 0.2, ns, lm, im, keys=set(keys))
    t_rust = time.perf_counter() - t0
    t0 = time.perf_counter()
    TI.integrate(bg, MASS, 0.2, ns, lm, im, backend="python")
    t_py = time.perf_counter() - t0
    assert t_py / t_rust > 8.0, (t_py, t_rust)
