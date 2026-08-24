"""
K2 · **on-shell tilt 속도** — v(t) 를 처방하지 않고 물질에서 **풀어낸다**.

지금까지 `tilted_integrate.Background` 는 v(t) 를 임의로 처방했다.  식 (12) 는 어떤
합동에 대해서도 성립하므로 검증용으로는 정당했지만, **물리적 tilt** 는 자유롭지 않다.

★ tilt 의 well-posed 정의: **에너지틀(Landau frame)** — 에너지 유속이 사라지는 틀.

        q′_a(v) ≡ J′^(0)_a(a_vec, v, m, f₀) = 0        ← v 에 대한 3원 방정식

  boosted 정확 구적이 있으므로 이 방정식을 **직접 풀 수 있다** (근찾기).
  ⇒ 배경 a(t) 를 따라 매 시각 풀면 **정확한 on-shell v(t)** 를 얻는다 — 오라클이다.

★ 언제 tilt 가 0 이 아닌가: 등방 f₀ 는 f(p)=f(−p) 라 법선틀에서 이미 q_a = 0 이고
  v ≡ 0 이다 (H1 에서 측정).  **분포에 실제 쌍극자(벌크 운동량)가 있어야** tilt 가 산다.
  `hierarchy.f_dipole(ε, axis)` 가 그 역할 — 이번엔 인공 장치가 아니라 **물리적 설정**이다
  (움직이는 물질).

★ tilted Euler: 에너지틀에서 q_a ≡ 0 이므로 계층의 l=1 방정식이 **q̇ 방정식이 아니라
  u̇ 를 정하는 대수식**이 된다:

        D^bπ_ba − D_a p + (ρ+p) u̇_a − π_ab u̇^b = 0

  u̇ 는 (a, ȧ, v, v̇) 의 운동학이고 v̇ 에 대해 **아핀**이므로 v̇ 를 풀 수 있다.
  이것이 tilt 속도의 진화식이다 — 근찾기 오라클과 **독립**인 두 번째 경로.
"""
from __future__ import annotations

import numpy as np

from bianchi.matter import hierarchy as H
from bianchi.matter import tilted as TL
from bianchi.matter import tilted_moments as TM
from bianchi.matter import tilted_terms as TT


def dipole_f0(eps=0.3, axis=2):
    """벌크 운동량을 가진 분포 — 이 경우에만 tilt 가 물리적으로 존재한다."""
    return H.f_dipole(eps, axis)


# ═══════════════════════════════════════ 에너지틀 (근찾기 오라클)
def energy_flux(v, a_vec, mass, f0):
    """q′_a(v) — tilted 사틀에서 본 에너지 유속 (0 이면 에너지틀)."""
    return np.asarray(TM.J_moment_tilted(a_vec, v, mass, 1, 0, f0), float)


def energy_frame_velocity(a_vec, mass, f0=None, eps=0.3, axis=2, v0=None,
                          tol=1e-13, itmax=60):
    """★ q′_a(v) = 0 을 v 에 대해 푼다 (Newton + 수치 야코비안).

    반환 dict(v, residual, iters, converged).
    ★ 이것이 **on-shell tilt 의 정의**다 — 처방이 아니라 물질이 정한다.
    """
    f0 = dipole_f0(eps, axis) if f0 is None else f0
    a = np.asarray(a_vec, float)
    rho = TM.J_moment_tilted(a, np.zeros(3), mass, 0, 0, f0)
    v = np.zeros(3) if v0 is None else np.asarray(v0, float).copy()
    h = 1e-6
    for it in range(itmax):
        F = energy_flux(v, a, mass, f0)
        if np.abs(F).max() / rho < tol:
            return dict(v=v, residual=float(np.abs(F).max() / rho),
                        iters=it, converged=True)
        Jm = np.empty((3, 3))
        for k in range(3):
            e = np.zeros(3)
            e[k] = h
            Jm[:, k] = (energy_flux(v + e, a, mass, f0)
                        - energy_flux(v - e, a, mass, f0)) / (2 * h)
        step = np.linalg.solve(Jm, -F)
        # |v| < 1 유지 (물리적 경계)
        while np.linalg.norm(v + step) >= 0.995:
            step *= 0.5
        v = v + step
    F = energy_flux(v, a, mass, f0)
    return dict(v=v, residual=float(np.abs(F).max() / rho), iters=itmax,
                converged=False)


def exact_v_trajectory(a0, H_hub, sigma_diag, mass, t_end, nsteps=20,
                       eps=0.3, axis=2):
    """★ 배경 a(t) 를 따라 매 시각 에너지틀을 풀어 **정확한 on-shell v(t)**.

    a_i(t) = a_i(0) exp((H+σ_i)t)  (배경은 처방; K1 결합은 별도).
    반환 dict(t, v[N,3], residual[N]).
    """
    a0 = np.asarray(a0, float)
    sg = np.asarray(sigma_diag, float)
    f0 = dipole_f0(eps, axis)
    ts = np.linspace(0.0, t_end, nsteps + 1)
    vs, res = [], []
    guess = None
    for t in ts:
        a = a0 * np.exp((H_hub + sg) * t)
        r = energy_frame_velocity(a, mass, f0, v0=guess)
        vs.append(r["v"].copy())
        res.append(r["residual"])
        guess = r["v"]
    return dict(t=ts, v=np.array(vs), residual=np.array(res))


# ═══════════════════════════════════════ tilted Euler (독립 경로)
def _euler_lhs(a_vec, da_vec, v, dv, mass, f0, l_max=4, i_max=2):
    """에너지틀 l=1 방정식의 좌변 — **검증된 `tilted_equation.equation_lhs` 를 재사용**.

    ★ 처음에 l=1 항들을 손으로 다시 적었다가 (div-free) 에서 J^(1) 대신 p 를 넣어
      **3배** 틀렸다 (교차검증이 24배 어긋나며 잡아냈다).  손 전사를 버리고
      이미 두 오라클로 검증된 조립을 그대로 쓴다.

    에너지틀 조건:  J^(i)_a ≡ 0  이고 ⊥q̇ = 0 (틀을 유지하므로) → dJ^(i)_a = 0.
    나머지 (l=0,2,3,4) 의 J 와 시간미분은 boosted 정확 구적에서 온다.
    """
    from bianchi.matter import tilted_equation as TE
    a = np.asarray(a_vec, float)
    da = np.asarray(da_vec, float)
    vv = np.asarray(v, float)
    dvv = np.asarray(dv, float)
    geo = TT.geometry(a, da, vv, dvv)
    dt = 1e-5

    def grid(av, vvv):
        out = {}
        for l in range(l_max + 3):
            for i in range(-1, i_max + 3):
                if l == 1:
                    out[(l, i)] = np.zeros(3)              # ★ 에너지틀
                elif l <= l_max:
                    out[(l, i)] = np.atleast_1d(np.asarray(
                        TM.J_moment_tilted(av, vvv, mass, l, i, f0),
                        float)).reshape((3,) * l)
                else:
                    out[(l, i)] = np.zeros((3,) * l)       # l 절단
        return out

    J = grid(a, vv)
    Jp = grid(a + da * dt, vv + dvv * dt)
    Jm = grid(a - da * dt, vv - dvv * dt)
    dJ = {k: (Jp[k] - Jm[k]) / (2 * dt) for k in J}
    for i in range(-1, i_max + 3):
        dJ[(1, i)] = np.zeros(3)                           # ★ ⊥q̇ = 0
    return np.asarray(TE.equation_lhs(J, dJ, geo, 1, 0), float)


def tilted_euler_vdot(a_vec, da_vec, v, mass, f0=None, eps=0.3, axis=2):
    """★ tilted Euler 를 v̇ 에 대해 푼다 — 근찾기와 **독립**인 두 번째 경로.

    좌변이 v̇ 에 대해 아핀이므로 4회 평가로 (M, b) 를 정확히 뽑아 M·v̇ = b 를 푼다.
    """
    f0 = dipole_f0(eps, axis) if f0 is None else f0
    base = _euler_lhs(a_vec, da_vec, v, np.zeros(3), mass, f0)
    cols = []
    for k in range(3):
        e = np.zeros(3)
        e[k] = 1.0
        cols.append(_euler_lhs(a_vec, da_vec, v, e, mass, f0) - base)
    M = np.column_stack(cols)
    return np.linalg.solve(M, -base), M


# ═══════════════════════════════════════ 게이트
def normal_frame_has_flux_only_with_dipole(a_vec=(1.0, 0.9, 1.2), mass=0.0, eps=0.3):
    """★ 등방 f₀ 는 tilt 가 **정확히 0**, 쌍극 f₀ 라야 tilt 가 산다."""
    from bianchi.matter import freestream as fs
    a = np.asarray(a_vec, float)
    q_iso = np.abs(np.asarray(
        TM.J_moment_tilted(a, np.zeros(3), mass, 1, 0, fs.f_fermi_dirac), float)).max()
    q_dip = np.abs(np.asarray(
        TM.J_moment_tilted(a, np.zeros(3), mass, 1, 0, dipole_f0(eps)), float)).max()
    rho = TM.J_moment_tilted(a, np.zeros(3), mass, 0, 0, fs.f_fermi_dirac)
    return dict(isotropic=q_iso / rho, dipole=q_dip / rho)


def cross_validate_vdot(a0=(1.0, 0.9, 1.2), H_hub=1.0, sigma_diag=(0.06, -0.02, -0.04),
                        mass=0.0, eps=0.3, dt=1e-3):
    """★★ 두 경로 교차검증:
      경로 A — 에너지틀 **근찾기** 를 시간에 따라 유한차분한 v̇  (계층 미사용)
      경로 B — **tilted Euler** 를 v̇ 에 대해 푼 값                (근찾기 미사용)
    """
    a0 = np.asarray(a0, float)
    sg = np.asarray(sigma_diag, float)
    f0 = dipole_f0(eps)
    v0 = energy_frame_velocity(a0, mass, f0)["v"]
    ap = a0 * np.exp((H_hub + sg) * dt)
    am = a0 * np.exp(-(H_hub + sg) * dt)
    vp = energy_frame_velocity(ap, mass, f0, v0=v0)["v"]
    vm = energy_frame_velocity(am, mass, f0, v0=v0)["v"]
    vdot_A = (vp - vm) / (2 * dt)
    da = (H_hub + sg) * a0
    vdot_B, M = tilted_euler_vdot(a0, da, v0, mass, f0)
    scale = max(np.abs(vdot_A).max(), np.abs(vdot_B).max(), 1e-300)
    return dict(v=v0, vdot_root=vdot_A, vdot_euler=vdot_B,
                rel=float(np.abs(vdot_A - vdot_B).max() / scale),
                cond=float(np.linalg.cond(M)))
