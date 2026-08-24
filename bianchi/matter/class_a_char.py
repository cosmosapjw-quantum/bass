"""
I1a · class A 자유흐름 특성곡선 커널 (65차) — PLAN-I1-coupled §0 규약.
    dp̂_a/dt = −H p̂_a − Σ_ab p̂_b + (R × p̂)_a + (1/Ê)·((N̂·p̂) × p̂)_a
유도: (T1)+(프레임 공변성 정확점)+(εN̂ 교차형) — audit/i1.  R 규약원 =
conventions.rotation_matrix (W=−ε·R).  ⚠ type_v.py 와 C-규약 상이 — 전사 금지.
LIMITATIONS: 배경 (H,Σ,R,N̂)(t) 는 호출자 몫 (결합은 I1c); Rust 는 I3.
"""
from __future__ import annotations

import numpy as np


def _nhat_matrix(N):
    N = np.asarray(N, float)
    if N.shape == (3,):
        return np.diag(N)
    if N.shape == (3, 3):
        if not np.allclose(N, N.T, atol=0.0):
            raise ValueError("N̂ 은 대칭이어야 한다 (class A)")
        return N
    raise ValueError("N̂: (3,) 대각 또는 (3,3) 대칭")


def characteristic_rhs_class_a(phat, H, Sigma, R, N, mass):
    ph = np.asarray(phat, float)
    S = np.asarray(Sigma, float)
    R = np.asarray(R, float)
    Nm = _nhat_matrix(N)
    one = ph.ndim == 1
    P = ph[None, :] if one else ph
    E = np.sqrt(mass * mass + np.sum(P * P, axis=1))
    Np = P @ Nm.T
    cross_N = np.cross(Np, P)
    cross_R = np.cross(np.broadcast_to(R, P.shape), P)
    out = -H * P - P @ S.T + cross_R + cross_N / E[:, None]
    return out[0] if one else out


def evolve_characteristic(p0, bg, mass, t0, t1, nsteps=128):
    P = np.asarray(p0, float).copy()
    dt = (t1 - t0) / nsteps
    for k in range(nsteps):
        s = t0 + k * dt

        def f(Q, u):
            H, S, R, N = bg(u)
            return characteristic_rhs_class_a(Q, H, S, R, N, mass)

        k1 = f(P, s)
        k2 = f(P + 0.5 * dt * k1, s + 0.5 * dt)
        k3 = f(P + 0.5 * dt * k2, s + 0.5 * dt)
        k4 = f(P + dt * k3, s + dt)
        P = P + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
    return P


def back_trace(P_t, bg, mass, t, nsteps=128):
    return evolve_characteristic(P_t, bg, mass, t, 0.0, nsteps=nsteps)


def solver_accuracy(p0, bg, mass, t, base=16, levels=4):
    sols = [evolve_characteristic(p0, bg, mass, 0.0, t, nsteps=base * 2**k)
            for k in range(levels)]
    errs = [float(np.max(np.abs(sols[k] - sols[-1])))
            for k in range(levels - 1)]
    orders = [np.log2(errs[k] / errs[k + 1]) for k in range(len(errs) - 1)]
    return errs, orders


def diag_triad_background(n_coord, c_exp, t_ref=1.0):
    c = np.asarray(c_exp, float)
    n = np.asarray(n_coord, float)

    def a_of(t):
        return (t_ref + t) ** c

    def bg(t):
        a = a_of(t)
        rate = c / (t_ref + t)
        H = float(np.mean(rate))
        S = np.diag(rate - H)
        N = np.array([n[0] * a[0] / (a[1] * a[2]),
                      n[1] * a[1] / (a[2] * a[0]),
                      n[2] * a[2] / (a[0] * a[1])])
        return H, S, np.zeros(3), N

    return bg, a_of
