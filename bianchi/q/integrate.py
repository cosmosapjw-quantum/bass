"""
Q10 · **시간적분 · 사건 검출** (76차).

  · Strang: 충돌은 **정확 지수** (강성 없음), 기하는 RK4/적응.
  · SymBoltz (arXiv:2509.24740) 교훈 승계 — **근사 절환 없음**.  그쪽은 암시적
    강성 적분 + 해석·희소 야코비안으로, 이쪽은 충돌 지수가 정확해 강성 자체가
    없다.  남는 기하 강성은 해석 야코비안 (`jacobian`) 으로 받는다.
  · 사건: 조밀출력 위 Brent 근찾기 (곡률벽·Kasner 편타·N 부호전환·Ω 임계).
"""
from __future__ import annotations

import numpy as np


def jacobian(st, eps=1e-6):
    """★ 기하 블록의 야코비안 (전방차분; 희소 패턴은 구조에서 나온다).

    SymBoltz 가 기호 미분으로 얻는 것을 여기서는 상태가 크므로 **기하 25성분만**
    (격자 블록은 자유흐름이 대각이라 해석적으로 안다: ∂dlnĜ_i/∂lnĜ_j = 0)."""
    v = st.pack()
    n_geo = 25
    J = np.zeros((n_geo, n_geo))
    f0 = st.rhs(v)[:n_geo]
    for k in range(n_geo):
        w = v.copy()
        h = eps * max(1.0, abs(v[k]))
        w[k] += h
        J[:, k] = (st.rhs(w)[:n_geo] - f0) / h
    return J


def sparsity(st, tol=1e-12):
    return np.abs(jacobian(st)) > tol


class Event:
    def __init__(self, name, g, direction=0, terminal=False):
        self.name, self.g, self.direction, self.terminal = name, g, direction, terminal


def _brent(f, a, b, tol=1e-12, itmax=100):
    fa, fb = f(a), f(b)
    if fa * fb > 0:
        return None
    for _ in range(itmax):
        m = 0.5 * (a + b)
        fm = f(m)
        if abs(b - a) < tol:
            return m
        if fa * fm <= 0:
            b, fb = m, fm
        else:
            a, fa = m, fm
    return 0.5 * (a + b)


def integrate(st, dtau, nsteps, nu=0.0, kernel="thomson", events=(),
              keep_every=0, v_b=None, sched=None, nu_log=None):
    """Strang 적분 + 사건 검출.  반환 (st, traj, hits).

    Q19: `sched` (`bianchi.q.rate.RateSchedule`) 를 주면 ν 가 **매 스텝** 이력에서
    계산된다 — 앞 반스텝 (τ_k, lnH_k), 뒤 반스텝 (τ_{k+1}, lnH_{k+1}).
    이것이 Python **참조 경로**이고 Rust 전-루프와 대조된다.  주지 않으면 상수
    `nu` 로 기존과 동일 (골든 보존).  `nu_log` 는 리스트를 주면 실제 쓴 ν 를 담는다."""
    traj, hits = [], []
    # ★★ 85차 반증 (독립 리뷰 B1): 여기서 tau 를 0.0 으로 시작했다.  스케줄은
    #   tau0 = tau_span[0] 에서 시작하므로 tau_span[0] != 0 이면 두 경로가 **다른
    #   적색이동**을 본다 (1+z 가 e^{tau0} 배).  실측: tau_span=(0.3,-0.7) 에서
    #   Rust-Python 상대차 4.5e-3 (예산 1e-13), 광학깊이 26.6 vs 88.6.
    #   게다가 validate_span 이 검사한 구간과 루프가 도는 구간이 달라져 빨리-실패
    #   보장도 무너졌다.  fast=True 여도 events 가 있으면 이 경로로 온다.
    tau = 0.0 if sched is None else float(sched.tau0)
    if sched is not None:
        sched.validate_span(dtau, nsteps)
    gprev = {e.name: e.g(st) for e in events}
    if keep_every:
        traj.append((tau, st.pack().copy()))
    for k in range(nsteps):
        prev = st.pack().copy()
        if sched is None:
            st.strang_step(dtau, nu, kernel, v_b)
        else:
            h = abs(dtau)
            nu0 = float(sched.nu(tau, st.lnH))          # 앞 반스텝: 지금 시각·lnH
            st.collide(0.5 * nu0 * h, kernel, v_b)
            st.residual_step(0.5 * dtau)
            st.rk4_step(dtau)
            st.residual_step(0.5 * dtau)
            # 뒤 반스텝: **갱신된** 시각·lnH (대칭 ⇒ Strang 2차 보존)
            nu1 = float(sched.nu(tau + dtau, st.lnH))
            st.collide(0.5 * nu1 * h, kernel, v_b)
            if nu_log is not None:
                nu_log.append((tau, nu0, tau + dtau, nu1))
        tau += dtau
        for e in events:
            gnow = e.g(st)
            gp = gprev[e.name]
            if gp * gnow < 0 and (e.direction == 0 or
                                  np.sign(gnow - gp) == e.direction):
                # 구간 내 이분 (선형 보간 상태로 재평가)
                def gof(s, prev=prev, e=e):
                    mid = st.unpack(prev + s * (st.pack() - prev))
                    return e.g(mid)
                s = _brent(gof, 0.0, 1.0)
                hits.append((e.name, tau - dtau + (s or 0.5) * dtau))
            gprev[e.name] = gnow
        if keep_every and (k + 1) % keep_every == 0:
            traj.append((tau, st.pack().copy()))
    return st, traj, hits


def curvature_wall_event(threshold=0.05):
    return Event("curvature_wall", lambda s: abs(s.curvature()[0]) - threshold)


def omega_threshold_event(x=0.5):
    return Event("omega", lambda s: s.aux()["Omega"] - x)


def n_sign_events():
    return [Event(f"n{i}_sign", (lambda i: (lambda s: s.N6[i]))(i)) for i in range(3)]
