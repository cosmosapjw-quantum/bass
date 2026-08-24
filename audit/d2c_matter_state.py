"""
D2c · **물질을 상태로 올린 효과를 잰다** — 얼린 판과 나란히.

D2b 는 "물질이 args 로 얼려 있으면 구속계가 닫히지 않는다 (잔차 ~1)" 를 **한 점에서**
보였다.  여기서는 그 결과가 **적분 궤적 위에서** 무엇을 뜻하는지 잰다.

    python -m audit.d2c_matter_state
"""
from __future__ import annotations

import jax
import jax.numpy as jnp
import numpy as np

from bianchi import constraints as con
from bianchi import integrate as itg
from bianchi.charts import general as G
from bianchi.charts import general_matter as GM
from functools import lru_cache

from bianchi.conventions import tracefree_from_5


@lru_cache(maxsize=8)
def configuration(seed=11, A1=0.6, pi_scale=0.06, gamma=4.0 / 3.0):
    """★ Jacobi 를 만족하는 무작위 일반형 배위 + 처방 Π."""
    rng = np.random.default_rng(seed)
    Sig = np.asarray(tracefree_from_5(*(rng.normal(size=5) * 0.15)))
    N = GM.jacobi_safe_N(*(rng.normal(size=3) * 0.4))
    y0, args = GM.on_constraint_surface(Sig, N, A1, gamma=gamma)
    args["Pi"] = jnp.asarray(tracefree_from_5(*(rng.normal(size=5) * pi_scale)))
    return y0, args


def _worst(c):
    return max(float(np.abs(np.asarray(v)).max()) for v in c.values())


def drift_comparison(tau=3.0, n=7, rtol=1e-11, atol=1e-13, **kw):
    """★★ 같은 초기자료를 **물질을 상태로** / **args 로 얼려** 굴린다.

    반환 dict(t, state, frozen) — 각 시각의 최악 구속 잔차.
    """
    y0, args = configuration(**kw)
    cfg = itg.SolverConfig(rtol=rtol, atol=atol)
    ts = jnp.linspace(0.0, tau, n)
    sol = itg.solve_jit(GM.rhs, y0, 0.0, tau, args, ts=ts, cfg=cfg)
    st = [_worst(GM.constraint_residuals(jax.tree.map(lambda x: x[j], sol.ys), args))
          for j in range(n)]
    ga = dict(args)
    ga["Omega"] = float(y0.Omega)
    ga["q_flux"] = np.asarray(y0.Q)
    sol2 = itg.solve_jit(G.rhs, y0.geometry(), 0.0, tau, ga, ts=ts, cfg=cfg)
    fr = [_worst(G.constraint_residuals(jax.tree.map(lambda x: x[j], sol2.ys), ga))
          for j in range(n)]
    om = [float(jax.tree.map(lambda x: x[j], sol.ys).Omega) for j in range(n)]
    return dict(t=np.asarray(ts), state=np.array(st), frozen=np.array(fr),
                omega=np.array(om))


def closure_along_trajectory(tau=2.0, n=5, **kw):
    """★★ D2b 의 닫힘 검사를 **궤적 위 여러 점에서** 돌린다 (한 점이 아니라)."""
    y0, args = configuration(**kw)
    cfg = itg.SolverConfig(rtol=1e-11, atol=1e-13)
    ts = jnp.linspace(0.0, tau, n)
    sol = itg.solve_jit(GM.rhs, y0, 0.0, tau, args, ts=ts, cfg=cfg)
    out = []
    for j in range(n):
        y = jax.tree.map(lambda x: x[j], sol.ys)
        r = GM.closure_residual(y, args)
        out.append((float(ts[j]), r["residual"], float(np.max(r["spectrum"].real))))
    return out


def tolerance_convergence(tau=2.0, rtols=(1e-7, 1e-9, 1e-11), **kw):
    """★ 구속 잔차가 **적분 tolerance 를 따라간다** (구조적 표류가 아니라는 뜻)."""
    y0, args = configuration(**kw)
    rows = []
    for rt in rtols:
        cfg = itg.SolverConfig(rtol=rt, atol=rt * 1e-2)
        sol = itg.solve_jit(GM.rhs, y0, 0.0, tau, args, cfg=cfg)
        yf = jax.tree.map(lambda x: x[-1] if jnp.ndim(x) else x, sol.ys)
        rows.append((float(rt), _worst(GM.constraint_residuals(yf, args))))
    return rows


def projection_is_nearly_a_noop(tau=1.5, n_chunks=4, **kw):
    """★★ D2 의 교훈을 확인 — **닫힌 계에서는 투영이 거의 할 일이 없다**."""
    y0, args = configuration(**kw)
    cfg = itg.SolverConfig(rtol=1e-11, atol=1e-13)
    _, off = con.solve_with_projection(GM, GM.rhs, y0, 0.0, tau, args,
                                       n_chunks=n_chunks, cfg=cfg,
                                       project_every=False)
    _, on = con.solve_with_projection(GM, GM.rhs, y0, 0.0, tau, args,
                                      n_chunks=n_chunks, cfg=cfg,
                                      project_every=True)
    return dict(off=float(np.asarray(off).max()), on=float(np.asarray(on).max()))


def projection_restores_broken_data(kick=(3e-3, -1e-3, 2e-3), dom=4e-3, **kw):
    """★ 깨진 자료를 확장 상태 위에서 투영해 되돌린다."""
    y0, args = configuration(**kw)
    bad = GM.StateGM.of(y0.Sigma, y0.N, y0.A,
                        np.asarray(y0.Q) + np.asarray(kick, float),
                        float(y0.Omega) + float(dom))
    fixed = con.make_projector(GM)(bad, args)
    return dict(before=float(con.monitor(GM, bad, args)),
                after=float(con.monitor(GM, fixed, args)),
                correction=float(np.abs(np.asarray(fixed.packed())
                                        - np.asarray(bad.packed())).max()))


def reduces_to_the_geometry_chart(**kw):
    """★★ 환원 게이트 — Q = 0, Π = 0 이면 기하가 `charts.general` 과 **정확히** 같다.

    (Ω 는 Gauss 로 채워 넣어 두 판이 같은 값을 보게 한다.)
    """
    y0, args = configuration(**kw)
    y = GM.StateGM.of(y0.Sigma, y0.N, y0.A, jnp.zeros(3), y0.Omega)
    a = dict(args)
    a["Pi"] = jnp.zeros((3, 3))
    d1 = GM.rhs(0.0, y, a)
    d2 = G.rhs(0.0, y.geometry(), {**a, "Omega": y.Omega, "q_flux": jnp.zeros(3)})
    return max(float(np.abs(np.asarray(d1.Sigma) - np.asarray(d2.Sigma)).max()),
               float(np.abs(np.asarray(d1.N) - np.asarray(d2.N)).max()),
               float(np.abs(np.asarray(d1.A) - np.asarray(d2.A)).max()))


def prescribed_Pi_can_drain_omega(tau=3.0, **kw):
    """★ **정직한 한계** — Π 를 처방으로 얼려두면 Ω 가 음수로 갈 수 있다.

    구속계는 여전히 닫혀 있지만(그게 D2c 의 주장이다) 물질 모형은 무모순이 아니다.
    물리적 Π 는 운동론 계층이 줘야 한다.
    """
    r = drift_comparison(tau=tau, **kw)
    return dict(omega_end=float(r["omega"][-1]),
                went_negative=bool(np.any(r["omega"] < 0.0)),
                constraint_worst=float(r["state"].max()))


def report():
    print("=" * 74)
    print("D2c · 물질을 차트의 상태변수로 승격")
    print("=" * 74)
    r = drift_comparison()
    print("\n[1] ★★ 구속 표류 — 상태로 올린 판 vs args 로 얼린 판")
    print("      τ      상태(D2c)     얼림(기존)      Ω")
    for t, s, f, om in zip(r["t"], r["state"], r["frozen"], r["omega"]):
        print(f"    {t:5.2f}   {s:.3e}    {f:.3e}   {om:+.6f}")
    print("\n[2] ★★ 닫힘 잔차 — 궤적 위 여러 점에서")
    for t, res, rate in closure_along_trajectory():
        print(f"    τ={t:5.2f}  닫힘 {res:.2e}   증폭률(max Re λ) {rate:+.6f}")
    print("\n[3] ★ 구속 잔차가 tolerance 를 따라간다")
    for rt, w in tolerance_convergence():
        print(f"    rtol={rt:.0e}  최악 잔차 {w:.3e}")
    print("\n[4] ★★ 닫힌 계에서는 투영이 거의 무동작")
    print(f"    {projection_is_nearly_a_noop()}")
    print("\n[5] 깨진 자료 투영")
    print(f"    {projection_restores_broken_data()}")
    print(f"\n[6] 환원 게이트 (Q=0, Π=0 → charts.general): "
          f"{reduces_to_the_geometry_chart():.3e}")
    print(f"\n[7] ★ 정직한 한계 — 처방 Π 는 Ω 를 음수로 끌 수 있다")
    print(f"    {prescribed_Pi_can_drain_omega()}")


if __name__ == "__main__":
    report()
