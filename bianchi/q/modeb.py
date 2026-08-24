"""
Q-ModeB · **완전 f 를 QState 에 정식 결합** (80차).

Mode A 는 에너지-가중 각밀도 Ĝ(q̂) = μ⁴∫f q³dq 를 나른다 — 반경을 미리 적분한 것.
Mode B 는 **f(q̂, q) 자체**를 나른다 (방향-주 배치 f[i*n_p + j]).

★★ 81차 반증 기록: 80차의 Mode B 충돌은 **공변 q 슬라이스**에서 방향을 섞었다.
   충돌 핵은 **고정 물리 p 에서** 섞으므로, mu(q̂) 가 방향마다 다르면 틀린다
   (실측: 비등방 프레임 + Planck 스펙트럼에서 lnĜ 최대차 **1.97**).
   Q7b (움직이는 전자) 를 붙이며 발각되었다 — 부스트가 같은 종류의 재격자화를
   요구하기 때문이다.  정정: 방향별 ln p 시프트 delta_i = ln(mu_i D_i) 로
   **공통 정지계 운동량 격자**로 옮긴 뒤 3항을 적용하고 되돌린다 (Q4 스텐실 재사용).

★ 세 가지가 Mode B 에서 더 강해진다:
  1. **자유흐름이 정확히 항등**.  공변 프레임이 H·Σ·R 을 흡수하고 |q| 도 보존하므로
     f 의 도함수가 **0** 이다 (Mode A 의 4 dlnμ 항은 반경적분의 부산물이었다).
  2. **분광 관측량**을 준다 (y-왜곡 등) — Ĝ 는 1모멘트라 불가능했다.
  3. 충돌은 여전히 정확 3항.  핵이 λ-무관이라 **반경 슬라이스마다 같은 연산**
     (에너지-교환 정리) — 반경 축이 비용에만 들어가고 정확도에는 안 들어간다.

축약 항등 (모멘트·기하 기계를 Mode A 와 공유하는 근거):
    ln Ĝ_i = 4 ln μ_i + ln Jr_i,   Jr_i = ∫ f_i q³ dq  (logsumexp)
Rust `QState::ln_ghat` 이 이걸 하고, 그 뒤는 Mode A 경로 그대로다.
"""
from __future__ import annotations

import numpy as np

from bianchi.q import sphere as S


class ModeBState:
    """Mode B 상태 — Rust 전-루프에 그대로 들어간다."""

    __slots__ = ("sph", "n_p", "lnq_min", "lnq_max", "tail", "k_rad",
                 "S6", "N6", "A3", "lnH", "M", "lnf", "rot", "residual", "v_b")

    def __init__(self, sph, n_p=64, lnq_min=-5.0, lnq_max=5.0, Sigma=None,
                 N=None, A=None, lnH=0.0, lnf=None, tail="wien", k_rad=8,
                 rot=None, residual=True, v_b=None):
        from bianchi.q.coupled import sym6
        self.sph, self.n_p = sph, int(n_p)
        self.lnq_min, self.lnq_max = float(lnq_min), float(lnq_max)
        self.tail, self.k_rad = tail, int(k_rad)
        Sigma = np.zeros((3, 3)) if Sigma is None else np.asarray(Sigma, float)
        N = np.zeros((3, 3)) if N is None else np.asarray(N, float)
        self.S6 = sym6(Sigma) if Sigma.ndim == 2 else np.asarray(Sigma, float)
        self.N6 = sym6(N) if N.ndim == 2 else np.asarray(N, float)
        self.A3 = np.zeros(3) if A is None else np.asarray(A, float)
        self.lnH = float(lnH)
        self.M = np.eye(3).ravel()
        m = int(sph.n)
        self.lnf = np.zeros(m * self.n_p) if lnf is None else np.asarray(lnf, float)
        self.rot = np.zeros(3) if rot is None else np.asarray(rot, float)
        self.residual = bool(residual)
        self.v_b = None if v_b is None else np.asarray(v_b, float)

    # ---------------------------------------------------------------- 격자
    def ln_q(self):
        return np.linspace(self.lnq_min, self.lnq_max, self.n_p)

    def q(self):
        return np.exp(self.ln_q())

    def dlnq(self):
        return (self.lnq_max - self.lnq_min) / (self.n_p - 1)

    def pack(self):
        return np.concatenate([self.S6, self.N6, self.A3, [self.lnH],
                               self.M, self.lnf])

    def set_from(self, v):
        v = np.asarray(v, float)
        self.S6, self.N6, self.A3 = v[:6].copy(), v[6:12].copy(), v[12:15].copy()
        self.lnH, self.M, self.lnf = float(v[15]), v[16:25].copy(), v[25:].copy()
        return self

    # ---------------------------------------------------------------- 축약·모멘트
    def ln_ghat(self):
        """ln Ĝ_i = 4 lnμ_i + ln Jr_i — Mode A 와 공유하는 축약 (Python 참조)."""
        from bianchi.q import comoving as CM
        qhat, _ = S.nodes(self.sph)
        _, mu = CM.phys(CM.frame_from(self.M), qhat)
        lq = self.ln_q()
        wt = np.ones(self.n_p); wt[0] = wt[-1] = 0.5
        F = self.lnf.reshape(-1, self.n_p) + (4.0 * lq + np.log(wt))[None, :]
        mx = F.max(axis=1)
        lnJr = mx + np.log(np.exp(F - mx[:, None]).sum(axis=1)) + np.log(self.dlnq())
        return lnJr + 4.0 * np.log(mu)

    def moments(self):
        """(ln ρ, q/ρ, π/ρ) — Mode A 와 같은 경로."""
        from bianchi.q import comoving as CM
        qhat, w_com = S.nodes(self.sph)
        fr = CM.frame_from(self.M)
        e, mu = CM.phys(fr, qhat)
        lw = CM.ln_phys_weights(fr, w_com, mu)
        return CM.moments_log(lw, self.ln_ghat(), e)

    def spectrum(self):
        """각평균 스펙트럼 f̄(q) — 분광 관측량의 입구 (Mode A 는 못 준다)."""
        _, w = S.nodes(self.sph)
        F = np.exp(self.lnf.reshape(-1, self.n_p))
        return np.einsum("a,ap->p", w, F) / w.sum()


def planck_state(sph, n_p=64, lnq_min=-6.0, lnq_max=4.0, T_of=None, **kw):  # noqa: D401
    """방향의존 온도 T(q̂) 의 흑체로 Mode B 초기자료 (O(1) 이방성 허용)."""
    st = ModeBState(sph, n_p, lnq_min, lnq_max, **kw)
    e, _ = S.nodes(sph)
    q = st.q()
    T = np.ones(len(e)) if T_of is None else np.array([T_of(x) for x in e], float)
    # ★ ln f 를 **해석적으로** (Wien 꼬리에서 expm1 이 넘친다 — 81차 실측):
    #     ln f = -ln(e^x - 1) = -x - ln(1 - e^{-x})
    x = q[None, :] / T[:, None]
    st.lnf = np.where(x > 30.0, -x, -np.log(np.expm1(np.minimum(x, 700.0)))).ravel()
    return st


def evolve(st: ModeBState, dtau, nsteps, nu=0.0, kernel="thomson",
           k_theta=6, k_phi=6, sub=2, keep_every=0, sched=None):
    """★ Rust 전-루프 (Mode B).  PyO3 진입 1회.

    Q19: `sched` 를 주면 ν 가 커널 안에서 매 스텝 이력에서 계산된다."""
    import bianchi_rustcore as R
    v = np.ascontiguousarray(st.pack())
    ns_, ha = (None, 0.0) if sched is None else sched.sample(dtau, nsteps)
    out = np.asarray(R.qe_evolve(
        int(st.sph.n_theta), int(st.sph.n_phi), v,
        np.ascontiguousarray(st.rot, float), bool(st.residual),
        float(dtau), int(nsteps), float(nu), kernel,
        int(k_theta), int(k_phi), int(sub), int(keep_every),
        int(st.n_p), st.lnq_min, st.lnq_max, st.tail, int(st.k_rad),
        None if st.v_b is None else np.ascontiguousarray(st.v_b, float),
        None if ns_ is None else np.ascontiguousarray(ns_, float), float(ha)))
    n = v.size
    st.set_from(out[:n])
    traj = out[n:].reshape(-1, n) if out.size > n else np.zeros((0, n))
    return st, traj


def diagnostics(st: ModeBState):
    import bianchi_rustcore as R
    v = np.asarray(R.qe_diagnostics(
        int(st.sph.n_theta), int(st.sph.n_phi),
        np.ascontiguousarray(st.pack()), np.ascontiguousarray(st.rot, float),
        int(st.n_p), st.lnq_min, st.lnq_max))
    return dict(Omega=float(v[0]), Pi6=v[1:7].copy(), q=float(v[7]),
                gauss=float(v[8]))


def y_parameter(st: ModeBState):
    """★ 비섭동 y-왜곡 — 등방화 후 각평균 스펙트럼에서 (온도이동 + y) 2성분 적합."""
    q = st.q()
    fbar = st.spectrum()
    wt = np.ones(st.n_p); wt[0] = wt[-1] = 0.5
    rho = float((fbar * q ** 4 * wt).sum() * st.dlnq())
    Teff = (rho / (np.pi ** 4 / 15.0)) ** 0.25
    x = q / Teff
    resid = fbar - 1.0 / np.expm1(x)
    g_T = x * np.exp(x) / np.expm1(x) ** 2
    g_y = g_T * (x / np.tanh(x / 2.0) - 4.0)
    m = (x > 0.02) & (x < 20.0)
    coef, *_ = np.linalg.lstsq(np.stack([g_T[m], g_y[m]], axis=1), resid[m],
                               rcond=None)
    return float(coef[1]), float(Teff)
