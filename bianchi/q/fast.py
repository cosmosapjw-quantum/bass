"""
Q11 · **전-루프 Rust 경로** + Mode B 잔여 이류 (79차).

R5b 규율의 완성: Python 은 설정만 주고 **스텝 루프가 Rust 에서 돈다**.
`bianchi.q.coupled` 의 Python 경로는 **참조 구현**으로 남는다 (비트급 대조 대상).

결정성 계약 (Q11):
  · 병렬성은 **멤버 단위**로만 (rayon).  멤버 내부는 직렬.
  · 모든 축약은 고정 순서 pairwise (`reduce_det`).
  ⇒ 같은 시드 → **스레드 수 무관 비트 동일**.
"""
from __future__ import annotations

import numpy as np

from bianchi.backend_policy import require_native


def reduce_det(v):
    rust = require_native("q.fast.reduce_det")
    return rust.qe_reduce_det(np.ascontiguousarray(np.asarray(v, float).ravel()))


def evolve(st, dtau, nsteps, nu=0.0, kernel="thomson", k_theta=6, k_phi=6,
           sub=2, keep_every=0, sched=None, v_b=None):
    """★ 전-루프 진화 — PyO3 호출 **1회**.  st 를 제자리 갱신하고 궤적을 준다.

    Q19: `sched` (`rate.RateSchedule`) 를 주면 ν 가 커널 안에서 **매 스텝** 이력에서
    계산된다 (Python 스텝 루프는 여전히 0회 — R5b 유지).  주지 않으면 상수 ν 로
    기존과 **비트 동일**."""
    v = np.ascontiguousarray(st.pack())
    ns, ha = (None, 0.0) if sched is None else sched.sample(dtau, nsteps)
    rust = require_native("q.fast.evolve")
    out = np.asarray(rust.qe_evolve(
        int(st.sph.n_theta), int(st.sph.n_phi), v,
        np.ascontiguousarray(st.rot, float), bool(st.residual),
        float(dtau), int(nsteps), float(nu), kernel,
        int(k_theta), int(k_phi), int(sub), int(keep_every),
        0, -5.0, 5.0, "wien", 8,
        # ★ 85차 (독립 리뷰): 여기에 None 을 하드코딩해 두고 `model.run()` 이
        #   `collision.v_b` 를 이 경로에만 안 넘겼다 — fast 와 참조가 조용히 갈렸다.
        None if v_b is None or not np.any(v_b) else np.ascontiguousarray(v_b, float),
        None if ns is None else np.ascontiguousarray(ns, float), float(ha)))
    n = v.size
    new = st.unpack(out[:n])
    st.S6, st.N6, st.A3 = new.S6, new.N6, new.A3
    st.lnH, st.M, st.lG = new.lnH, new.M, new.lG
    traj = out[n:].reshape(-1, n) if out.size > n else np.zeros((0, n))
    return st, traj


def diagnostics(st):
    """(Ω, Π6, q, gauss) — Rust 경로에서 직접."""
    rust = require_native("q.fast.diagnostics")
    v = np.asarray(rust.qe_diagnostics(
        int(st.sph.n_theta), int(st.sph.n_phi),
        np.ascontiguousarray(st.pack()), np.ascontiguousarray(st.rot, float)))
    return dict(Omega=float(v[0]), Pi6=v[1:7].copy(), q=float(v[7]),
                gauss=float(v[8]))


def ensemble(states, dtau, nsteps, nu=0.0, kernel="thomson", k_theta=6, k_phi=6,
             sub=2):
    """★ 멤버 병렬 (rayon).  states: QState 목록 (같은 격자·rot·residual)."""
    if not states:
        return np.zeros((0, 0))
    s0 = states[0]
    flat = np.concatenate([np.ascontiguousarray(s.pack()) for s in states])
    rust = require_native("q.fast.ensemble")
    out = np.asarray(rust.qe_ensemble(
        int(s0.sph.n_theta), int(s0.sph.n_phi), flat, len(states),
        np.ascontiguousarray(s0.rot, float), bool(s0.residual),
        float(dtau), int(nsteps), float(nu), kernel,
        int(k_theta), int(k_phi), int(sub)))
    return out.reshape(len(states), -1)


# ───────────────────────────────────────────── Mode B 잔여 이류
def residual_mode_b(sph, rad, M, f, N6, A3, dtau, k_theta=6, k_phi=6, k_rad=8,
                    sub=2, log_state=False, tail="wien"):
    """★ 방향 스텐실 + **방향별 반경 시프트** 결합.

    (R2) 의 δ(q̂) = ∫(dln|q|/dτ)dτ 가 그대로 ln p 시프트가 된다 — Q4 의 반경
    스텐실 기계를 재사용한다.  f 배치는 방향-주 f[i*n_p + j].
    """
    rust = require_native("q.fast.residual_mode_b")
    return np.asarray(rust.qe_residual_mode_b(
        sph, rad, np.ascontiguousarray(np.asarray(M, float).ravel()),
        np.ascontiguousarray(np.asarray(f, float).ravel()),
        np.ascontiguousarray(np.asarray(N6, float)),
        np.ascontiguousarray(np.asarray(A3, float)),
        float(dtau), int(k_theta), int(k_phi), int(k_rad), int(sub),
        bool(log_state), tail))


def mode_b_moments(sph, rad, f):
    """(ρ, q, π) — 반경 적분 후 각 구적 (절단 없음)."""
    from bianchi.q import sphere as S
    m, n_p = int(sph.n), int(rad.n)
    F = np.asarray(f, float).reshape(m, n_p)
    p = np.asarray(rad.p())
    wt = np.ones(n_p); wt[0] = wt[-1] = 0.5
    G = (F * (p ** 4)[None, :] * wt[None, :]).sum(axis=1) * float(rad.dlnp)
    return S.moments(sph, G)
