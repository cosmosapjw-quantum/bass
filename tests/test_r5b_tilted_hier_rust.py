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
import json

import numpy as np
import pytest

from bianchi.matter import tilted_closure as TC
from bianchi.matter import tilted_equation as TE
from bianchi.matter import tilted_integrate as TI
from bianchi.matter import tilted_mass as TMass
from bianchi.matter import tilted_moments as TM
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


def _backward_error(M, x, b):
    """Engineering normwise backward residual for one concrete linear solve."""
    residual = float(np.linalg.norm(b - M @ x, ord=np.inf))
    denominator = (float(np.linalg.norm(M, ord=np.inf))
                   * float(np.linalg.norm(x, ord=np.inf))
                   + float(np.linalg.norm(b, ord=np.inf)))
    if denominator == 0.0:
        return 0.0 if residual == 0.0 else float("inf")
    return residual / denominator


def _record_json(request, name, payload):
    """Attach deterministic diagnostics to JUnit without pytest fixture warnings."""
    request.node.user_properties.append((name, json.dumps(payload, sort_keys=True)))


def _endpoint_error_from_history(bg, mass, history):
    """Keep exact-quadrature endpoint errors as diagnostics without reintegration."""
    final_time = float(history["t"][-1])
    state = history["J"][-1]
    a_final, v_final = bg.a(final_time), bg.v(final_time)
    rho_exact = float(TM.J_moment_tilted(a_final, v_final, mass, 0, 0))
    out = {}
    for name, key in (("rho", (0, 0)), ("q", (1, 0)), ("pi", (2, 0))):
        if key not in state:
            continue
        exact = np.atleast_1d(np.asarray(
            TM.J_moment_tilted(a_final, v_final, mass, *key), float)).ravel()
        got = np.atleast_1d(np.asarray(state[key], float)).ravel()
        out[name] = float(np.abs(got - exact).max() / rho_exact)
    return out


def _compare_histories(bg, mass, rust_history, python_history):
    """Direct, scale-stable backend parity over every retained state block."""
    rust_times = np.asarray(rust_history["t"], float)
    python_times = np.asarray(python_history["t"], float)
    assert np.array_equal(rust_times, python_times), (rust_times, python_times)
    assert np.isfinite(rust_times).all()
    assert len(rust_history["J"]) == len(python_history["J"]) == len(rust_times)

    worst = {"gap": 0.0, "checkpoint": 0, "block": [0, 0]}
    for checkpoint, (rust_state, python_state) in enumerate(
            zip(rust_history["J"], python_history["J"])):
        assert set(rust_state) == set(python_state), checkpoint
        rust_rho = np.asarray(rust_state[(0, 0)], float)
        python_rho = np.asarray(python_state[(0, 0)], float)
        assert rust_rho.size == python_rho.size == 1
        rust_rho_value = float(rust_rho)
        python_rho_value = float(python_rho)
        assert np.isfinite(rust_rho_value) and rust_rho_value > 0.0
        assert np.isfinite(python_rho_value) and python_rho_value > 0.0
        rho_scale = max(abs(rust_rho_value), abs(python_rho_value))

        for key in sorted(rust_state):
            rust_value = np.asarray(rust_state[key], float)
            python_value = np.asarray(python_state[key], float)
            assert rust_value.shape == python_value.shape, (checkpoint, key)
            assert np.isfinite(rust_value).all(), (checkpoint, key, "rust")
            assert np.isfinite(python_value).all(), (checkpoint, key, "python")
            rust_norm = float(np.abs(rust_value).max())
            python_norm = float(np.abs(python_value).max())
            denominator = max(rho_scale, rust_norm, python_norm)
            gap = float(np.abs(rust_value - python_value).max()) / denominator
            if gap > worst["gap"]:
                worst = {"gap": gap, "checkpoint": checkpoint,
                         "block": [int(key[0]), int(key[1])]}
            assert gap <= 1e-12, (checkpoint, key, gap, denominator)
    return worst


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


def test_bit_exactness_is_lost_only_in_the_linear_solve(request):
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
    f_python, m_python = _python_force_and_matrix(J, geo, L_MAX, I_MAX)
    b_python = TMass.pack(f_python, L_MAX, I_MAX)
    x_python = TMass.pack(TI.rhs(J, bg, 0.05, L_MAX, I_MAX), L_MAX, I_MAX)
    sc = np.abs(x_python).max()
    solve_only = float(np.abs(x_lapack - x_rust).max()) / sc
    end_to_end = float(np.abs(x_python - x_rust).max()) / sc
    cond_2_rust = float(np.linalg.cond(M))
    cond_2_python = float(np.linalg.cond(m_python))
    cond_inf_rust = float(np.linalg.cond(M, p=np.inf))
    cond_inf_python = float(np.linalg.cond(m_python, p=np.inf))
    eta_rust = _backward_error(M, x_rust, b)
    eta_python = _backward_error(m_python, x_python, b_python)
    # Fixed engineering gate: binary64 unit roundoff u=2^-53 and solve dimension n.
    eta_limit = 64.0 * M.shape[0] * 2.0 ** -53
    _record_json(request, "linear_solve_diagnostics", {
        "cond_2_python": cond_2_python, "cond_2_rust": cond_2_rust,
        "cond_inf_python": cond_inf_python, "cond_inf_rust": cond_inf_rust,
        "eta_limit": eta_limit, "eta_python": eta_python, "eta_rust": eta_rust,
    })
    assert cond_2_rust < 5.0
    assert cond_2_python < 5.0
    assert eta_rust <= eta_limit, (eta_rust, eta_limit)
    assert eta_python <= eta_limit, (eta_python, eta_limit)
    assert solve_only < 1e-15
    assert end_to_end < 1e-15
    # 전 경로 차가 선형해 차와 **같은 자릿수**여야 한다 (조립이 추가 오차를 안 냈다)
    assert end_to_end <= 10.0 * max(solve_only, 1e-18)


@pytest.mark.parametrize("mode", ["frozen", "ratio_scalar"])
def test_former_red_modes_match_on_common_state_operators(mode, request):
    """Primitive F/M/RHS parity at 0, N/2, N on identical Python states.

    The fixture's dimensionless background has |H|=1, which supplies the explicit
    inverse-time scale.  These gates compare like-dimensioned quantities only.
    """
    bg = TI.Background()
    nsteps = 10
    python_history = TI.integrate(bg, MASS, 0.2, nsteps, L_MAX, I_MAX,
                                  mode=mode, jdot_closure=True, backend="python")
    omega_ref = abs(float(bg.H))
    assert np.isfinite(omega_ref) and omega_ref > 0.0
    keys, _, _ = TMass.layout(L_MAX, I_MAX)
    diagnostics = []
    for checkpoint in (0, nsteps // 2, nsteps):
        time_value = float(python_history["t"][checkpoint])
        common_state = python_history["J"][checkpoint]
        rho_scale = abs(float(np.asarray(common_state[(0, 0)], float)))
        assert np.isfinite(rho_scale) and rho_scale > 0.0
        geo = bg.geometry(time_value)
        force_rust, matrix_rust = TR.force_and_matrix(
            common_state, geo, L_MAX, I_MAX, mode=mode, jdot_closure=True)
        force_python_blocks, matrix_python = _python_force_and_matrix(
            common_state, geo, L_MAX, I_MAX, mode=mode, jdot=True)
        force_python = TR.pack_state(force_python_blocks, L_MAX, I_MAX)
        rhs_rust = TMass.pack(TR.rhs(
            common_state, geo, L_MAX, I_MAX, mode=mode, jdot_closure=True,
            keys=set(keys)), L_MAX, I_MAX)
        rhs_python = TMass.pack(TI.rhs(
            common_state, bg, time_value, L_MAX, I_MAX, mode=mode,
            jdot_closure=True), L_MAX, I_MAX)

        force_denominator = max(
            rho_scale * omega_ref,
            float(np.linalg.norm(force_rust, ord=np.inf)),
            float(np.linalg.norm(force_python, ord=np.inf)))
        matrix_denominator = max(
            1.0, float(np.linalg.norm(matrix_rust, ord=np.inf)),
            float(np.linalg.norm(matrix_python, ord=np.inf)))
        rhs_denominator = max(
            rho_scale * omega_ref,
            float(np.linalg.norm(rhs_rust, ord=np.inf)),
            float(np.linalg.norm(rhs_python, ord=np.inf)))
        force_gap = (float(np.linalg.norm(force_rust - force_python, ord=np.inf))
                     / force_denominator)
        matrix_gap = (float(np.linalg.norm(matrix_rust - matrix_python, ord=np.inf))
                      / matrix_denominator)
        rhs_gap = (float(np.linalg.norm(rhs_rust - rhs_python, ord=np.inf))
                   / rhs_denominator)
        diagnostics.append({"checkpoint": checkpoint, "time": time_value,
                            "force_gap": force_gap, "matrix_gap": matrix_gap,
                            "rhs_gap": rhs_gap})
        assert force_gap <= 1e-15, diagnostics[-1]
        assert matrix_gap <= 1e-15, diagnostics[-1]
        assert rhs_gap <= 1e-15, diagnostics[-1]
    _record_json(request, "common_state_operator_diagnostics", diagnostics)


# ═══════════════════════════════════════ 궤적 (전 모드)
@pytest.mark.parametrize("mode", ["ratio", "frozen", "ratio_scalar",
                                  "phys_sqrt", "phys_5w", "phys_interp"])
@pytest.mark.parametrize("jdot", [True, False])
def test_the_trajectory_matches_the_numpy_oracle(mode, jdot, request):
    """★★ 모드 × J̇ 닫힘 전 조합에서 전체 상태 이력이 직접 일치한다."""
    bg = TI.Background()
    rust_history = TI.integrate(bg, MASS, 0.2, 10, L_MAX, I_MAX, mode=mode,
                                jdot_closure=jdot)
    python_history = TI.integrate(bg, MASS, 0.2, 10, L_MAX, I_MAX, mode=mode,
                                  jdot_closure=jdot, backend="python")
    worst = _compare_histories(bg, MASS, rust_history, python_history)
    rust_errors = _endpoint_error_from_history(bg, MASS, rust_history)
    python_errors = _endpoint_error_from_history(bg, MASS, python_history)
    assert all(np.isfinite(value) for value in rust_errors.values()), rust_errors
    assert all(np.isfinite(value) for value in python_errors.values()), python_errors
    # Endpoint errors stay machine-readable diagnostics.  Their near-zero relative
    # difference is intentionally not an acceptance observable.
    _record_json(request, "trajectory_contract_diagnostics", {
        "jdot_closure": jdot, "max_state_gap": worst,
        "mode": mode, "python_endpoint_errors": python_errors,
        "rust_endpoint_errors": rust_errors,
    })


@pytest.mark.parametrize("n_star", [2, 3, 4])
def test_the_triangular_truncation_matches(n_star, request):
    """★ L1 의 삼각 절단 l + 2i ≤ n_* — 상태공간 자체가 줄어드는 경로."""
    bg = TI.Background()
    rust_history = TI.integrate(bg, MASS, 0.2, 10, L_MAX, 1, n_star=n_star)
    python_history = TI.integrate(bg, MASS, 0.2, 10, L_MAX, 1, n_star=n_star,
                                  backend="python")
    worst = _compare_histories(bg, MASS, rust_history, python_history)
    rust_errors = _endpoint_error_from_history(bg, MASS, rust_history)
    python_errors = _endpoint_error_from_history(bg, MASS, python_history)
    assert all(np.isfinite(value) for value in rust_errors.values()), rust_errors
    assert all(np.isfinite(value) for value in python_errors.values()), python_errors
    _record_json(request, "triangular_contract_diagnostics", {
        "max_state_gap": worst, "n_star": n_star,
        "python_endpoint_errors": python_errors,
        "rust_endpoint_errors": rust_errors,
    })


@pytest.mark.parametrize("mass", [0.0, 1.0])
def test_both_backends_meet_the_designated_exact_quadrature_gate(
        mass, monkeypatch, request):
    """Independent physical-accuracy gate; native execution is fail-closed."""
    assert TR.USE_RUST
    assert TI.rust_available("ratio", jdot_closure=True, n_star=None)
    bg = TI.Background()

    def unexpected_python_rhs(*_args, **_kwargs):
        raise AssertionError("native exact-quadrature lane fell back to TI.rhs")

    with monkeypatch.context() as native_guard:
        native_guard.setattr(TI, "rhs", unexpected_python_rhs)
        rust_errors = TI.trajectory_error(
            bg, mass, t_end=0.2, nsteps=20, l_max=2, i_max=2, backend=None)
    python_errors = TI.trajectory_error(
        bg, mass, t_end=0.2, nsteps=20, l_max=2, i_max=2, backend="python")

    for backend, errors in (("rust", rust_errors), ("python", python_errors)):
        assert all(np.isfinite(value) for value in errors.values()), (backend, errors)
        assert errors["rho"] < 1e-3, (backend, errors)
        assert errors["q"] < 1e-3, (backend, errors)
        assert errors["pi"] < 2e-3, (backend, errors)
    _record_json(request, "exact_quadrature_diagnostics", {
        "mass": mass, "python": python_errors, "rust": rust_errors,
        "rust_fallback_guard": "PASS",
    })


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


def test_no_supported_mode_silently_falls_back_to_python(monkeypatch):
    """★★ **회귀** — 대조군이 조용히 Python 으로 돌아가면 벽시계가 그대로다.

    처음 판이 정확히 그랬다 (1260 스텝 중 310 스텝만 Rust).
    """
    for mode in TC.MODES:
        assert TI.rust_available(mode), mode
    assert TI.rust_available("ratio", jdot_closure=False)
    assert TI.rust_available("ratio", n_star=3)

    def unexpected_python_rhs(*_args, **_kwargs):
        raise AssertionError("a supported native configuration called TI.rhs")

    monkeypatch.setattr(TI, "rhs", unexpected_python_rhs)
    bg = TI.Background()
    for mode in TC.MODES:
        TI.integrate(bg, MASS, 0.01, 1, 2, 1, mode=mode)
    TI.integrate(bg, MASS, 0.01, 1, 2, 1, mode="ratio", jdot_closure=False)
    TI.integrate(bg, MASS, 0.01, 1, 2, 1, mode="ratio", n_star=3)


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
