"""
PR-12 · 구속 잔차 모니터링 + Gauss-Newton 투영.

구속은 **곱셈적으로 전파**한다: 예컨대 class B 의 Codazzi 는
    C' = 4(q + Sigma_+ - 1) C
이므로 초기 오차가 exp[4 int (q+Sigma_+-1) dtau] 로 지수 증폭한다.
q in [-1,2] 이므로 팽창기 일부 구간에서 지수가 명백히 양수 -> **장시간 적분에는
투영이 필수**.

전략 3단계 (설계 §3.2):
  1. 모니터링 (항상, 거의 공짜)
  2. 투영 (기본 on) : y <- y - J^T (J J^T)^{-1} C(y)
  3. 좌표 소거 (Layer 1 축소차트)
"""
from __future__ import annotations

from typing import Callable

from bianchi.optional_dependencies import require_jax_x64, require_optional

jax, jnp = require_jax_x64(feature=__name__)
eqx = require_optional("equinox", feature=__name__)
lx = require_optional("lineax", feature=__name__)


def gauss_newton_project(constraint_fn, pack, unpack, y, args,
                         iters: int = 3, damping: float = 1e-12):
    """상태를 구속 다양체로 최소제곱 투영.

    constraint_fn(y, args) -> (m,) 잔차 벡터
    pack(y) -> (n,) ,  unpack(v) -> y
    """
    def C(v):
        return constraint_fn(unpack(v), args)

    v = pack(y)
    for _ in range(iters):
        c = C(v)
        J = jax.jacfwd(C)(v)                      # (m, n)
        JJt = J @ J.T
        m = JJt.shape[0]
        op = lx.MatrixLinearOperator(JJt + damping * jnp.eye(m))
        lam = lx.linear_solve(op, c, solver=lx.AutoLinearSolver(well_posed=None)).value
        v = v - J.T @ lam
    return unpack(v)


def make_projector(chart, iters=3):
    """차트별 투영기. general 차트는 constraint_vector 를, 축소차트는 스칼라 구속을."""
    if getattr(chart, "name", None) == "general_matter":
        # ★ D2c: 물질(Ω, Q)까지 상태에 들어 있어 구속계가 **닫혀 있다**.
        #   투영도 그 확장 상태 위에서 해야 한다 (기하만 고치면 Ω, Q 가 어긋난 채 남는다).
        cfn = chart.constraint_vector
        pack, unpack = (lambda y: y.packed()), chart.StateGM.from_packed
    elif hasattr(chart, "constraint_vector"):
        cfn = chart.constraint_vector
        pack, unpack = (lambda y: y.packed()), chart.StateG.from_packed
    elif chart.name == "class_b":
        def cfn(y, args):
            return jnp.atleast_1d(chart.codazzi(y, args["kappa"]))
        pack, unpack = (lambda y: y.as_array()), chart.StateB.from_array
    elif chart.name == "exceptional_VI":
        def cfn(y, args):
            return jnp.atleast_1d(chart.g_constraint(y))
        pack, unpack = (lambda y: y.as_array()), chart.StateE.from_array
    elif chart.name == "class_b_tilted":
        # ★ v1.3 (감사): 이전에는 조용히 항등 투영을 돌려줬다 — 구속이 가장 많은
        #   차트가 무보호였던 셈. C2..C5 잔차 벡터로 투영한다 (C1 은 Omega 정의).
        def cfn(y, args):
            c = chart.constraints(y, args)
            return jnp.stack([c["C2"], c["C3"], c["C4"]])
        pack, unpack = (lambda y: y.as_array()), chart.StateBT.from_array
    elif chart.name == "type_ix_D":
        def cfn(y, args):
            c = chart.constraints(y, args)
            return jnp.stack([c["definition"], c["trace"]])
        pack, unpack = (lambda y: y.as_array()), chart.StateD.from_array
    elif chart.name == "class_a":
        return lambda y, args: y            # Gauss 가 Omega 정의에 흡수됨 (명시 화이트리스트)
    else:
        raise ValueError(
            f"make_projector: 미등록 차트 {getattr(chart, 'name', chart)!r} — "
            "조용한 항등 투영은 v1.3 에서 금지되었다 (감사 결함 #3).")

    def project(y, args):
        return gauss_newton_project(cfn, pack, unpack, y, args, iters=iters)
    return project


def monitor(chart, y, args):
    """구속 잔차 요약 (SaveAt(fn=) 안에서 호출해도 될 만큼 싸다)."""
    c = chart.constraints(y, args) if hasattr(chart, "constraints") else {}
    vals = [jnp.max(jnp.abs(jnp.asarray(v))) for v in c.values()]
    return jnp.max(jnp.stack(vals)) if vals else jnp.asarray(0.0)


def amplification_rate(chart, y, args):
    """구속 증폭률. class B: 4(q + Sigma_+ - 1); 예외형: 2(q + Sigma_+ - 1).

    ★ D2b: general 차트는 더 이상 **조용히 0.0** 을 돌려주지 않는다.  구속면 위에서
      d(Jf)/dy = M·J 를 풀어 M 의 스펙트럼 상한을 낸다 (`bianchi.constraint_rates`).
      물질이 얼어 있으면 그 계는 닫히지 않으므로, 닫힘 잔차가 크면 **0.0 대신
      NaN** 을 돌려준다 — 못 믿을 수를 조용히 내놓지 않기 위해서다.
    """
    if chart.name == "class_b":
        a = chart.aux(y, args["gamma"], args["kappa"])
        return 4.0 * (a["q"] + y.Sigma_p - 1.0)
    if chart.name == "exceptional_VI":
        a = chart.aux(y, args["gamma"])
        return 2.0 * (a["q"] + y.Sigma_p - 1.0)
    if getattr(chart, "name", None) == "general_matter":
        # ★ D2c: 닫힌 계라 닫힘 잔차가 기계정밀도다 — NaN 이 나올 일이 없다.
        r = chart.amplification_rate(y, args)
        return jnp.asarray(r["rate"] if r["closure"] < 1e-8 else jnp.nan)
    if getattr(chart, "name", None) == "general":
        from bianchi.constraint_rates import general_amplification_rate
        r = general_amplification_rate(y, args)
        return jnp.asarray(r["rate"] if r["closure"] < 1e-8 else jnp.nan)
    return jnp.asarray(0.0)


def solve_with_projection(chart, rhs, y0, t0, t1, args, n_chunks=20,
                          cfg=None, project_every=True):
    """구간을 쪼개 적분 사이사이 투영. 지수 증폭을 억제한다."""
    from bianchi import integrate as itg
    project = make_projector(chart)
    ts = jnp.linspace(t0, t1, n_chunks + 1)
    y = y0
    residuals = [float(monitor(chart, y, args))]
    for i in range(n_chunks):
        sol = itg.solve_jit(rhs, y, float(ts[i]), float(ts[i + 1]), args, cfg=cfg)
        y = jax.tree.map(lambda x: x[-1] if jnp.ndim(x) else x, sol.ys)
        if project_every:
            y = project(y, args)
        residuals.append(float(monitor(chart, y, args)))
    return y, jnp.asarray(residuals)
