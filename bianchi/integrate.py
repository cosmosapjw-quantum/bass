"""
PR-09 · diffrax 래퍼.

설계 §5 의 함정을 전부 코드로 막는다:
  * throw=False 강제        — vmap 하에서 한 원소 실패가 배치 전체를 죽인다
  * 원소별 sol.result 검사   — 이벤트 종료는 result != successful 이다(정상)
  * 성분별 가중 RMS 노름     — Sigma~O(1), N~수십자릿수, Omega~0, v~1 을 동등취급 금지
  * SaveAt(fn=) 축약 출력    — dense=True 금지, len(ts) 작게
  * eqx.filter_jit          — jax.jit 대신 (에러 메시지 품질)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional, Sequence

import diffrax as dfx
import equinox as eqx
import jax
import jax.numpy as jnp
import optimistix as optx


# ---------------------------------------------------------------- 가중 노름
def weighted_rms(weights):
    """성분별 가중 RMS 노름 팩토리.  weights: 상태와 같은 구조의 pytree 또는 배열."""
    w = jnp.asarray(weights)

    def norm(y):
        v = jnp.concatenate([jnp.ravel(jnp.asarray(l)) for l in jax.tree.leaves(y)])
        return jnp.sqrt(jnp.mean((v / w) ** 2))

    return norm


#: 차트별 기본 가중 (성분 스케일 차이를 반영)
DEFAULT_WEIGHTS = {
    "class_a":        (1.0, 1.0, 3.0, 3.0, 3.0),
    "class_b":        (1.0, 1.0, 1.0, 1.0, 3.0),
    "exceptional_VI": (1.0, 1.0, 1.0, 1.0, 3.0, 1.0),
}


@dataclass(frozen=True)
class SolverConfig:
    rtol: float = 1e-8
    atol: float = 1e-10
    pcoeff: float = 0.4          # 비평활 오차추정 대응
    icoeff: float = 0.3
    dcoeff: float = 0.0
    dt0: float = 1e-4
    max_steps: int = 4096
    dtmin: float = 1e-14
    solver: str = "Kvaerno5"     # diffrax 0.7.2 에는 Rosenbrock/Radau/BDF 없음
    weights: Optional[tuple] = None      # tuple 이어야 hashable -> jit static 가능


_SOLVERS = {
    "Kvaerno3": dfx.Kvaerno3, "Kvaerno4": dfx.Kvaerno4, "Kvaerno5": dfx.Kvaerno5,
    "Dopri8": dfx.Dopri8, "Tsit5": dfx.Tsit5,
}


def make_solver(cfg: SolverConfig):
    return _SOLVERS[cfg.solver]()


def make_controller(cfg: SolverConfig):
    kw = dict(rtol=cfg.rtol, atol=cfg.atol,
              pcoeff=cfg.pcoeff, icoeff=cfg.icoeff, dcoeff=cfg.dcoeff,
              dtmin=cfg.dtmin, force_dtmin=False)
    if cfg.weights is not None:
        kw["norm"] = weighted_rms(jnp.asarray(cfg.weights))
    return dfx.PIDController(**kw)


# ---------------------------------------------------------------- 이벤트
def float_event(cond_fn, direction=None, rtol=1e-10, atol=1e-12):
    """정확한 근을 찾는 이벤트. 불리언 cond_fn 은 스텝 끝에서 끊겨 부정확하다."""
    return dfx.Event(cond_fn, root_finder=optx.Newton(rtol=rtol, atol=atol),
                     direction=direction)


def blowup_event(norm_fn, limit=1e6):
    """상태 노름 상한. VII_0 / VII_h 는 N -> inf 로 **상태공간이 컴팩트하지 않다**
       (Weyl 곡률 증가). 물리적으로 옳은 거동이므로 발산 자체를 이벤트로 잡는다."""
    def cond(t, y, args, **kw):
        return limit - norm_fn(y)
    return float_event(cond, direction=False)


def singularity_event(aux_fn, eps=1e-6):
    """Omega -> 0 또는 Sigma^2 -> 1 접근 시 종료."""
    def cond(t, y, args, **kw):
        a = aux_fn(y, args)
        return jnp.minimum(a["Omega"] - eps, 1.0 - eps - a["Sigma2"])
    return float_event(cond, direction=False)


# ---------------------------------------------------------------- 적분
def solve(rhs, y0, t0, t1, args, ts=None, cfg: SolverConfig = None,
          event=None, save_fn=None):
    """단일 궤적 적분. **throw=False 고정** — 호출자가 sol.result 를 검사할 것."""
    cfg = cfg or SolverConfig()
    kw_save = {} if save_fn is None else {"fn": save_fn}
    saveat = (dfx.SaveAt(ts=ts, **kw_save) if ts is not None
              else dfx.SaveAt(t1=True, **kw_save))
    return dfx.diffeqsolve(
        dfx.ODETerm(rhs), make_solver(cfg),
        t0=t0, t1=t1, dt0=cfg.dt0, y0=y0, args=args,
        stepsize_controller=make_controller(cfg),
        saveat=saveat, event=event,
        max_steps=cfg.max_steps,
        throw=False,               # ★ vmap 안전
    )


def solve_jit(rhs, y0, t0, t1, args, ts=None, cfg=None, event=None, save_fn=None):
    """jit 캐시된 solve. rhs/cfg/event/save_fn/ts 유무는 static."""
    cfg = cfg or SolverConfig()
    has_ts = ts is not None
    key = (rhs, cfg, event, save_fn, has_ts)
    fn = _JIT_CACHE.get(key)
    if fn is None:
        if has_ts:
            @eqx.filter_jit
            def fn(y0, t0, t1, args, ts):
                return solve(rhs, y0, t0, t1, args, ts=ts, cfg=cfg,
                             event=event, save_fn=save_fn)
        else:
            @eqx.filter_jit
            def _f(y0, t0, t1, args):
                return solve(rhs, y0, t0, t1, args, ts=None, cfg=cfg,
                             event=event, save_fn=save_fn)
            fn = lambda y0, t0, t1, args, ts: _f(y0, t0, t1, args)
        _JIT_CACHE[key] = fn
    return fn(y0, t0, t1, args, ts)


_JIT_CACHE: dict = {}


def status(sol):
    """원소별 상태 해석. 이벤트 종료는 실패가 아니다."""
    ok = sol.result == dfx.RESULTS.successful
    ev = getattr(sol, "event_mask", None)
    fired = False
    if ev is not None:
        leaves = [jnp.asarray(l) for l in jax.tree.leaves(ev)]
        if leaves:
            fired = bool(jnp.any(jnp.stack([jnp.any(l) for l in leaves])))
    return dict(
        successful=bool(ok),
        event_fired=fired,
        # 이벤트로 끊긴 것은 '정상 종료' 로 취급
        accepted=bool(ok) or fired,
        num_steps=int(sol.stats.get("num_steps", -1)),
        result=str(sol.result),
    )


# ---------------------------------------------------------------- 진단 저장
def diagnostics_saver(aux_fn, constraint_fn):
    """SaveAt(fn=) 용 축약 출력: 전체 상태 대신 진단량만 저장 (메모리 절약)."""
    def fn(t, y, args):
        a = aux_fn(y, args)
        c = constraint_fn(y, args)
        return dict(
            tau=t, Omega=a["Omega"], Sigma2=a["Sigma2"], q=a["q"],
            constraint=jnp.max(jnp.stack(
                [jnp.abs(jnp.asarray(v)) for v in c.values()]
            )),
        )
    return fn
