"""
C2 · **차트 커버리지** — class_b_tilted / exceptional / type_ix_d RHS 의 Rust 이식.

지금까지 Rust 고속 경로(diffsol BDF + Rayon 배치)는 class_a / class_b 만 커버했다.
남은 세 차트를 `Chart` enum 에 올리고 (11/6/7 상태 — solve 층을 MAX_STATES=11 로
일반화), 세 겹으로 검증한다:

  1. **RHS 패리티**: 무작위 상태 40점에서 Python(jax) 대 Rust —
       class_b_tilted 1.3e−16,  exceptional 3.6e−16,  type_ix_d(±방향) **0.00e+00**
  2. **기호 항등** (sympy, V15 방식): 예외형 g′ = 2(q+Σ₊−1)g 와
       Ω′−[2q−(3γ−2)]Ω = −4Ag 가 항등 0;  IX-D 의 G′ = −2(qH+F)G 는 **trace-free
       부과 시에만** 0 (일반에선 ≠ 0 — Python 문서의 조건부 주장을 기호로 확정).
  3. **궤적 패리티 + 구속 수송**: diffsol BDF 대 diffrax 오라클, 온셸 초기조건에서
       구속이 적분 내내 작게 유지.

★★ 감사 수확 (반증 꼴): tilted-B 의 닫힌형 `dOmega()` 는 **Codazzi 온셸 전용**이다 —
  오프셸에서 사슬법칙과 ~1e−1 차이, C₂=C₃=C₄=0 위에서 1e−14 (실측 4점).
  class B 의 b3=−4 와 같은 구조인데 문서에 단서가 없었다.  여기서 못박는다.
"""
import numpy as np
import pytest

RC = pytest.importorskip("bianchi_rustcore")

import jax  # noqa: E402
import jax.numpy as jnp  # noqa: E402

from bianchi import integrate as itg  # noqa: E402
from bianchi.charts import class_b_tilted as BT  # noqa: E402
from bianchi.charts import exceptional as EX  # noqa: E402
from bianchi.charts import type_ix_d as XD  # noqa: E402


def _bt_state(rng):
    y = rng.normal(size=11) * 0.25
    y[6] = rng.uniform(-0.9, 0.9)          # |λ| ≤ 1
    y[8:] *= 0.4                           # |v| < 1
    return y


def _bt_onshell(rng, gamma=1.3):
    """무작위 기하 + C₂=C₃=C₄=0 을 v 로 풀어 온셸 상태를 만든다."""
    from scipy.optimize import fsolve
    geo = rng.normal(size=8) * 0.2
    geo[6] = rng.uniform(-0.8, 0.8)

    def cons(v):
        y = np.concatenate([geo, v])
        c = BT.constraints(BT.StateBT.from_array(jnp.asarray(y)), {"gamma": gamma})
        return [float(c["C2"]), float(c["C3"]), float(c["C4"])]

    v = fsolve(cons, rng.normal(size=3) * 0.1)
    assert max(abs(x) for x in cons(v)) < 1e-10
    return np.concatenate([geo, v])


# ═══════════════════════════════════════ 1. RHS 패리티
def test_rhs_parity_class_b_tilted():
    """★★ 11-상태 tilted RHS — jax 대 Rust, 무작위 40점 1e−14 이내 (실측 1.3e−16)."""
    rng = np.random.default_rng(3)
    for _ in range(40):
        g = float(rng.uniform(1.0, 1.9))
        y = _bt_state(rng)
        py = np.asarray(BT.rhs(0.0, BT.StateBT.of(*y), {"gamma": g}).as_array())
        ru = np.asarray(RC.chart_rhs("class_b_tilted", y, g))
        assert np.abs(py - ru).max() / max(1.0, np.abs(py).max()) < 1e-14


def test_rhs_parity_exceptional():
    rng = np.random.default_rng(5)
    for _ in range(40):
        g = float(rng.uniform(1.0, 1.9))
        y = rng.normal(size=6) * 0.3
        py = np.asarray(EX.rhs(0.0, EX.StateE.from_array(jnp.asarray(y)),
                               {"gamma": g}).as_array())
        ru = np.asarray(RC.chart_rhs("exceptional", y, g))
        assert np.abs(py - ru).max() / max(1.0, np.abs(py).max()) < 1e-14


def test_rhs_parity_type_ix_d_both_directions():
    """★ D-차트 ± 방향 — 실측 0.00e+00 (연산 순서까지 같다)."""
    rng = np.random.default_rng(7)
    for _ in range(40):
        g = float(rng.uniform(1.0, 1.9))
        w = rng.normal(size=7) * 0.5
        st = XD.StateD.of(w[0], w[1:4], w[4:7])
        y = np.asarray(st.as_array())
        for name, fn in (("type_ix_d", XD.rhs), ("type_ix_d_future", XD.rhs_future)):
            py = np.asarray(fn(0.0, st, {"gamma": g}).as_array())
            ru = np.asarray(RC.chart_rhs(name, y, g))
            assert np.array_equal(py, ru) or np.abs(py - ru).max() < 1e-15, name


def test_chart_aux_reports_the_representative_constraint():
    """★ chart_aux 의 (Ω, 대표구속) 이 Python 정의와 일치한다."""
    rng = np.random.default_rng(9)
    g = 1.3
    y = _bt_state(rng)
    om, c2 = RC.chart_aux("class_b_tilted", y, g)
    a = BT.aux(BT.StateBT.of(*y), {"gamma": g})
    c = BT.constraints(BT.StateBT.of(*y), {"gamma": g})
    assert abs(om - float(a["Omega"])) < 1e-14
    assert abs(c2 - float(c["C2"])) < 1e-14
    y = rng.normal(size=6) * 0.3
    _, gcon = RC.chart_aux("exceptional", y, g)
    assert abs(gcon - float(EX.g_constraint(EX.StateE.from_array(jnp.asarray(y))))) < 1e-14
    w = rng.normal(size=7) * 0.4
    st = XD.StateD.of(w[0], w[1:4], w[4:7])
    _, defin = RC.chart_aux("type_ix_d", np.asarray(st.as_array()), g)
    assert abs(defin - float(XD.constraints(st, {"gamma": g})["definition"])) < 1e-14


# ═══════════════════════════════════════ 2. 기호 항등 (sympy)
def test_exceptional_identities_close_symbolically():
    """★★ g′ = 2(q+Σ₊−1)g 와 Ω′−[2q−(3γ−2)]Ω = −4Ag — 문서의 두 주장이 항등."""
    from audit import v15_physics_audit as A
    rg, ro = A.exceptional_identities()
    assert rg == 0 and ro == 0


def test_type_ix_d_definition_identity_is_conditional():
    """★★ G′ = −2(qH+F)G 는 trace-free 에서만 — 조건부 주장을 기호로 확정."""
    from audit import v15_physics_audit as A
    nonzero_general, tracefree = A.type_ix_d_definition_identity()
    assert nonzero_general is True
    assert tracefree == 0


# ═══════════════════════════════════════ ★★ 감사 수확: dOmega 는 온셸 전용
def test_bt_domega_closed_form_is_onshell_only():
    """★★ 오프셸 ~1e−1, C₂..C₄=0 위 1e−12 이내 — 단서 없던 온셸 제한을 못박는다."""
    rng = np.random.default_rng(1)
    g = 1.3

    def gap(y):
        st = BT.StateBT.from_array(jnp.asarray(y))
        om = lambda w: BT.aux(BT.StateBT.from_array(w), {"gamma": g})["Omega"]
        chain = float(jnp.dot(jax.grad(om)(jnp.asarray(y)),
                              BT.rhs(0.0, st, {"gamma": g}).as_array()))
        return chain - float(BT.dOmega(st, {"gamma": g}))

    on = _bt_onshell(rng, g)
    off = np.array(on, copy=True)
    off[8:] = rng.normal(size=3) * 0.3
    assert abs(gap(off)) > 1e-5          # 오프셸에서는 닫힌형이 성립하지 않는다
    assert abs(gap(on)) < 1e-12


# ═══════════════════════════════════════ 3. 궤적 패리티 + 구속 수송
def _diffrax_final(rhs_fn, y0_state, args, t1, ts):
    cfg = itg.SolverConfig(rtol=1e-11, atol=1e-13, max_steps=200000)
    sol = itg.solve_jit(rhs_fn, y0_state, 0.0, t1, args, ts=ts, cfg=cfg)
    return jax.tree.map(lambda x: np.asarray(x)[-1], sol.ys)


def test_trajectory_parity_exceptional():
    """★★ diffsol BDF 대 diffrax — 온셸 IC, 종단 상태 1e−7 이내 + g 수송 ~0."""
    g = 1.2
    y0 = np.asarray(EX.on_g_surface(0.2, -0.1, 0.15, 0.3, 0.12).as_array())
    ts = np.linspace(0.0, 3.0, 31)
    ys, ok = RC.integrate_background("exceptional", y0, ts, g)
    assert ok and ys.shape == (31, 6)
    ref = _diffrax_final(EX.rhs, EX.StateE.from_array(jnp.asarray(y0)),
                         {"gamma": g}, 3.0, jnp.asarray(ts))
    assert np.abs(ys[-1] - np.asarray(ref.as_array())).max() < 1e-7
    # g-구속 수송: 시작 0 → 내내 작게
    gs = [abs(RC.chart_aux("exceptional", ys[i], g)[1]) for i in range(31)]
    assert max(gs) < 1e-9, max(gs)


def test_trajectory_parity_type_ix_d():
    """★ 등방 닫힌 IX — 재붕괴 접근 구간 (H̄ 감소), 정의식·trace 수송."""
    g = 1.0
    y0 = np.asarray(XD.isotropic_closed_ic(0.6).as_array())
    ts = np.linspace(0.0, 2.0, 21)
    ys, ok = RC.integrate_background("type_ix_d_future", y0, ts, g)
    assert ok and ys.shape == (21, 7)
    ref = _diffrax_final(XD.rhs_future, XD.StateD.from_array(jnp.asarray(y0)),
                         {"gamma": g}, 2.0, jnp.asarray(ts))
    assert np.abs(ys[-1] - np.asarray(ref.as_array())).max() < 1e-7
    for i in range(21):
        assert abs(RC.chart_aux("type_ix_d", ys[i], g)[1]) < 1e-9   # 정의식
        assert abs(ys[i][1] + ys[i][2] + ys[i][3]) < 1e-10          # trace
    assert ys[-1][0] < ys[0][0]                                     # 닫힌 IX: H̄ 감소


def test_trajectory_parity_class_b_tilted():
    """★★ 11-상태 tilted — 온셸 IC 로 BDF 대 diffrax, C₂..C₄ 수송."""
    g = 1.3
    rng = np.random.default_rng(11)
    y0 = _bt_onshell(rng, g)
    ts = np.linspace(0.0, 1.5, 16)
    ys, ok = RC.integrate_background("class_b_tilted", y0, ts, g)
    assert ok and ys.shape == (16, 11)
    ref = _diffrax_final(BT.rhs, BT.StateBT.from_array(jnp.asarray(y0)),
                         {"gamma": g}, 1.5, jnp.asarray(ts))
    assert np.abs(ys[-1] - np.asarray(ref.as_array())).max() < 1e-6
    for i in range(16):
        c = BT.constraints(BT.StateBT.from_array(jnp.asarray(ys[i])), {"gamma": g})
        for k in ("C2", "C3", "C4"):
            assert abs(float(c[k])) < 1e-8, (k, i)


def test_batch_scan_covers_the_new_charts():
    """★ Rayon 배치가 6-상태 차트를 (K,6) 모양으로 소화한다 (모양 검증 포함)."""
    g = 1.2
    y0 = np.asarray(EX.on_g_surface(0.2, -0.1, 0.15, 0.3, 0.12).as_array())
    y0s = np.stack([y0, y0 * 0.5])
    ts = np.linspace(0.0, 1.0, 5)
    ys, ok = RC.integrate_batch("exceptional", y0s, ts, g)
    assert ys.shape == (2, 6) and ok.shape == (2,)
    assert bool(ok[0]) and bool(ok[1])
    with pytest.raises(Exception):
        RC.integrate_batch("exceptional", np.zeros((2, 5)), ts, g)


def test_unknown_chart_error_lists_the_new_names():
    with pytest.raises(Exception, match="class_b_tilted"):
        RC.chart_rhs("nope", np.zeros(5), 1.0)
