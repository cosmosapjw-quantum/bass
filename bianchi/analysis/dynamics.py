"""
PR-26/27 · 동역학계 분석: 고정점, 선형안정성, Lyapunov, 분기.

★ jax.jacfwd 가 손야코비안을 완전히 대체한다 — JAX 를 고른 주된 이유 중 하나.
"""
from __future__ import annotations

from typing import Callable

import jax
import jax.numpy as jnp
import numpy as np
import optimistix as optx


# ---------------------------------------------------------------- 고정점
def find_fixed_point(rhs_arr, y0_arr, args, rtol=1e-12, atol=1e-14, max_steps=200):
    """rhs_arr: (v, args) -> (n,).  optimistix Newton."""
    def F(v, a):
        return rhs_arr(v, a)
    solver = optx.Newton(rtol=rtol, atol=atol)
    sol = optx.root_find(F, solver, jnp.asarray(y0_arr), args=args,
                         max_steps=max_steps, throw=False)
    return sol.value, sol


def continuation(rhs_arr, y0_arr, args_fn, param_values, **kw):
    """파라미터 연속법: gamma 또는 kappa 를 따라 고정점을 추적."""
    out, v = [], jnp.asarray(y0_arr)
    for p in param_values:
        v, sol = find_fixed_point(rhs_arr, v, args_fn(p), **kw)
        out.append((float(p), np.asarray(v),
                    float(jnp.max(jnp.abs(rhs_arr(v, args_fn(p)))))))
    return out


# ---------------------------------------------------------------- 안정성
def jacobian(rhs_arr, v, args):
    return jax.jacfwd(lambda w: rhs_arr(w, args))(jnp.asarray(v))


def eigenvalues(rhs_arr, v, args):
    J = np.asarray(jacobian(rhs_arr, v, args))
    return np.linalg.eigvals(J)


def classify_fixed_point(rhs_arr, v, args, tol=1e-9):
    ev = eigenvalues(rhs_arr, v, args)
    re = ev.real
    n_pos = int((re > tol).sum()); n_neg = int((re < -tol).sum())
    n_zero = int((np.abs(re) <= tol).sum())
    if n_pos == 0 and n_zero == 0:
        kind = "sink"
    elif n_neg == 0 and n_zero == 0:
        kind = "source"
    elif n_zero > 0:
        kind = "non-hyperbolic"
    else:
        kind = "saddle"
    return dict(kind=kind, eigenvalues=ev, n_pos=n_pos, n_neg=n_neg, n_zero=n_zero)


# ---------------------------------------------------------------- Lyapunov
def lyapunov_spectrum(rhs_arr, v0, args, T=200.0, dt=0.01, n_exp=None,
                      renorm_every=10):
    """Benettin: tangent 공간을 jvp 로 동시 전파 + QR 재정규화.

    ★ R3 (성능): 옛 판은 `for i in range(steps)` 안에서 매 스텝 JAX 를 **즉시 실행**
      했다 (스텝당 f 4회 + jacfwd 1회).  T=20, dt=0.01 이면 디스패치가 1만 번이라
      회귀시험 하나가 54 초를 먹었다.  같은 알고리즘·같은 연산 순서를 `lax.scan`
      두 겹(스텝 / 재정규화 청크)으로 옮기고 통째로 jit 한다.

    ★ 남는 스텝(steps % renorm_every)은 옛 판과 같이 **재정규화 없이** 돌리고
      lyap 에도 기여하지 않는다 — 거동을 바꾸지 않으려고 그대로 뒀다.
    """
    v = jnp.asarray(v0, jnp.float64)
    n = v.shape[0]
    k = n_exp or n
    Q0 = jnp.eye(n)[:, :k]
    steps = int(T / dt)
    nchunk, rem = divmod(steps, int(renorm_every))

    def f(w):
        return rhs_arr(w, args)

    def one_step(carry, _):
        v, Q = carry
        k1 = f(v); k2 = f(v + 0.5*dt*k1); k3 = f(v + 0.5*dt*k2); k4 = f(v + dt*k3)
        v_new = v + dt/6.0*(k1 + 2*k2 + 2*k3 + k4)
        J = jax.jacfwd(f)(v)
        return (v_new, Q + dt * (J @ Q)), None

    def chunk(carry, _):
        carry, _ = jax.lax.scan(one_step, carry, None, length=int(renorm_every))
        v, Q = carry
        Q, R = jnp.linalg.qr(Q)
        return (v, Q), jnp.log(jnp.abs(jnp.diag(R)))

    @jax.jit
    def run(v, Q):
        if nchunk:
            (v, Q), logs = jax.lax.scan(chunk, (v, Q), None, length=nchunk)
            lyap = logs.sum(axis=0)
        else:
            lyap = jnp.zeros(k)
        if rem:
            (v, Q), _ = jax.lax.scan(one_step, (v, Q), None, length=rem)
        return lyap

    return np.asarray(run(v, Q0)) / (steps * dt)


def largest_lyapunov(rhs_arr, v0, args, **kw):
    return float(lyapunov_spectrum(rhs_arr, v0, args, n_exp=1, **kw)[0])


# ---------------------------------------------------------------- 분기·attractor
def bifurcation_scan(rhs_arr, y0_arr, args_fn, param_values, **kw):
    """파라미터 스캔 + attractor 유형 라벨링."""
    rows = []
    for p in param_values:
        args = args_fn(p)
        v, sol = find_fixed_point(rhs_arr, jnp.asarray(y0_arr), args, **kw)
        res = float(jnp.max(jnp.abs(rhs_arr(v, args))))
        if res < 1e-8:
            c = classify_fixed_point(rhs_arr, v, args)
            rows.append(dict(param=float(p), state=np.asarray(v),
                             kind=c["kind"], eigs=c["eigenvalues"], residual=res))
        else:
            rows.append(dict(param=float(p), state=None, kind="not-found",
                             eigs=None, residual=res))
    return rows


def detect_limit_cycle(rhs_arr, v0, args, T=400.0, dt=0.005, tail=0.3,
                       tol=1e-3):
    """극한주기 검출 (Mussel attractor 용).

    긴 적분 후 꼬리 구간에서 (a) 고정점 수렴이 아니고 (b) 재귀(Poincare 근접)
    가 있으면 극한주기 후보로 본다.

    ★ R3 (성능): 적분 루프를 `lax.scan` + jit 로 옮겼다 (옛 판은 스텝마다 JAX 를
      즉시 실행해 T=30, dt=0.01 에 27 초).  판정 로직과 꼬리 자르는 규칙은 그대로다.
    """
    v = jnp.asarray(v0, jnp.float64)
    steps = int(T/dt)

    def one(v, _):
        k1 = rhs_arr(v, args); k2 = rhs_arr(v + .5*dt*k1, args)
        k3 = rhs_arr(v + .5*dt*k2, args); k4 = rhs_arr(v + dt*k3, args)
        v = v + dt/6.0*(k1 + 2*k2 + 2*k3 + k4)
        return v, v

    _, ys = jax.jit(lambda v: jax.lax.scan(one, v, None, length=steps))(v)
    ys = np.asarray(ys)
    # 옛 판의 `if i > steps*(1-tail)` 과 **같은** 인덱스 집합
    keep = np.arange(steps) > steps * (1 - tail)
    traj = ys[keep]
    spread = traj.max(axis=0) - traj.min(axis=0)
    if spread.max() < tol:
        return dict(kind="fixed-point", spread=float(spread.max()), period=None)
    last = traj[-1]
    d = np.linalg.norm(traj[:-10] - last, axis=1)
    j = int(np.argmin(d))
    period = (len(traj) - 1 - j) * dt
    return dict(kind="limit-cycle" if d[j] < tol else "aperiodic",
                spread=float(spread.max()), period=float(period),
                closure=float(d[j]))


# ---------------------------------------------------------------- 불변량 모니터
def invariant_monitor(chart, states, args):
    """유형 표류·구속 잔차 시계열."""
    from bianchi import constraints as con
    return np.array([float(con.monitor(chart, s, args)) for s in states])
