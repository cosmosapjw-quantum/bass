"""
Q8 ★ **아인슈타인 결합 — 11유형 전부** (76차).

상태 (통합 캐리어, 유형별 차트 아님):
    y = [Σ6(대칭 6, 무대각 사영), N6(대칭 6), A3, lnH, M9(공변 프레임), lnĜ(M)]

기하 (Ellis-MacCallum 정규직교틀, 팽창 정규화 — `charts.general` 규약 승계):
    Σ_ab' = −(2−q)Σ_ab − ³S_ab + Π_ab + [W,Σ]
    N_ab' = q N_ab + (ΣN + NΣ) + [W,N]
    A_a'  = q A_a − Σ_a^b A_b + W A
    lnH'  = −(1+q),      q = 2Σ² + ½(Ω + 3𝒫)

물질 (절단 없음 — 소스는 **격자 구적의 출력**):
    Ω = ρ/(3H²),   Π_ab = (∫w Ĝ (ê_aê_b − δ/3)) / H² = 3Ω · (π/ρ)_ab
    dlnĜ/dτ = −4(1 + Σ_ab ê^a ê^b)          ← 공변 프레임의 해석적 자유흐름
충돌은 RHS 에 넣지 않는다 — **정확 지수**를 Strang 으로 붙인다 (강성 소멸).

구속 (Gauss·Codazzi·Jacobi) 은 소거하지 않고 **감시자**로 둔다.
"""
from __future__ import annotations

import numpy as np

from bianchi.q import comoving as CM
from bianchi.q import sphere as S

SYM = ((0, 0), (1, 1), (2, 2), (0, 1), (0, 2), (1, 2))


def sym6(M):
    M = np.asarray(M, float)
    return np.array([M[i, j] for i, j in SYM])


def mat3(v6):
    v = np.asarray(v6, float)
    M = np.zeros((3, 3))
    for x, (i, j) in zip(v, SYM):
        M[i, j] = M[j, i] = x
    return M


def eps_mat(R):
    R = np.asarray(R, float)
    return np.array([[0.0, -R[2], R[1]], [R[2], 0.0, -R[0]], [-R[1], R[0], 0.0]])


class QState:
    """Q8 결합 상태."""

    __slots__ = ("sph", "qhat", "w_com", "S6", "N6", "A3", "lnH", "M", "lG",
                 "rot", "residual", "jac_min")

    def __init__(self, sph, Sigma, N, A, lnH=0.0, lG=None, M=None, rot=None,
                 residual=True):
        self.sph = sph
        self.qhat, self.w_com = S.nodes(sph)
        self.S6 = sym6(Sigma) if np.ndim(Sigma) == 2 else np.asarray(Sigma, float)
        self.N6 = sym6(N) if np.ndim(N) == 2 else np.asarray(N, float)
        self.A3 = np.asarray(A, float)
        self.lnH = float(lnH)
        self.M = np.eye(3).ravel() if M is None else np.asarray(M, float).ravel()
        self.lG = np.zeros(len(self.w_com)) if lG is None else np.asarray(lG, float)
        self.rot = np.zeros(3) if rot is None else np.asarray(rot, float)
        self.residual = bool(residual)       # Q5b — 기본 켬
        self.jac_min = 1.0

    # ---------------------------------------------------------------- 포장
    def pack(self):
        return np.concatenate([self.S6, self.N6, self.A3, [self.lnH],
                               self.M, self.lG])

    def unpack(self, v):
        v = np.asarray(v, float)
        o = QState.__new__(QState)
        o.sph, o.qhat, o.w_com, o.rot = self.sph, self.qhat, self.w_com, self.rot
        o.residual, o.jac_min = self.residual, self.jac_min
        o.S6, o.N6, o.A3 = v[:6].copy(), v[6:12].copy(), v[12:15].copy()
        o.lnH = float(v[15]); o.M = v[16:25].copy(); o.lG = v[25:].copy()
        return o

    # ---------------------------------------------------------------- 기하·소스
    def geometry(self):
        fr = CM.frame_from(self.M)
        e, mu = CM.phys(fr, self.qhat)
        lw = CM.ln_phys_weights(fr, self.w_com, mu)
        return fr, e, mu, lw

    def sources(self):
        """(Ω, Π_ab) — 절단 없는 격자 구적의 **출력**."""
        _, e, mu, lw = self.geometry()
        ln_rho, _, pi_over_rho = CM.moments_log(lw, self.lG, e)
        lnOm = ln_rho - np.log(3.0) - 2.0 * self.lnH
        Om = float(np.exp(lnOm))
        return Om, 3.0 * Om * pi_over_rho

    def curvature(self):
        from bianchi.q import group as G
        return G.curvature(mat3(self.N6), self.A3)

    def aux(self):
        Sm = mat3(self.S6)
        Sigma2 = float(np.trace(Sm @ Sm) / 6.0)
        K, S3 = self.curvature()
        Om, Pi = self.sources()
        q = 2.0 * Sigma2 + Om                      # 무질량 (𝒫 = Ω/3)
        return dict(Sigma2=Sigma2, K=K, S3=S3, Omega=Om, Pi=Pi, q=q)

    def gauss_residual(self):
        a = self.aux()
        return a["Sigma2"] + a["K"] + a["Omega"] - 1.0

    def codazzi_residual(self):
        from bianchi.conventions import codazzi_residual
        _, e, mu, lw = self.geometry()
        ln_rho, q_over_rho, _ = CM.moments_log(lw, self.lG, e)
        Om = float(np.exp(ln_rho - np.log(3.0) - 2.0 * self.lnH))
        return np.asarray(codazzi_residual(mat3(self.S6), mat3(self.N6),
                                           self.A3, 3.0 * Om * q_over_rho))

    def jacobi_residual(self):
        return mat3(self.N6) @ self.A3

    # ---------------------------------------------------------------- RHS
    def rhs(self, v=None):
        st = self if v is None else self.unpack(v)
        a = st.aux()
        Sm, Nm, A = mat3(st.S6), mat3(st.N6), st.A3
        W = eps_mat(-st.rot)                        # W_ab = -eps_abc R_c
        q, S3, Pi = a["q"], a["S3"], a["Pi"]
        dS = -(2.0 - q) * Sm - S3 + Pi + (W @ Sm - Sm @ W)
        dS = dS - np.trace(dS) * np.eye(3) / 3.0
        dN = q * Nm + (Sm @ Nm + Nm @ Sm) + (W @ Nm - Nm @ W)
        dA = q * A - Sm @ A + W @ A
        dlnH = -(1.0 + q)
        # 공변 프레임:  dM/dτ = −(I + Σ − εR) M
        Mm = st.M.reshape(3, 3)
        dM = -((np.eye(3) + Sm - eps_mat(st.rot)) @ Mm)
        # 자유흐름 (해석):  dlnĜ/dτ = −4(1 + ê·Σ·ê)
        _, e, mu, _ = st.geometry()
        ese = np.einsum("ai,ij,aj->a", e, Sm, e)
        dlG = -4.0 * (1.0 + ese)
        return np.concatenate([sym6(dS), sym6(0.5 * (dN + dN.T)), dA,
                               [dlnH], dM.ravel(), dlG])

    # ---------------------------------------------------------------- 적분
    def rk4_step(self, dtau):
        v = self.pack()
        k1 = self.rhs(v)
        k2 = self.rhs(v + 0.5 * dtau * k1)
        k3 = self.rhs(v + 0.5 * dtau * k2)
        k4 = self.rhs(v + dtau * k3)
        out = self.unpack(v + dtau / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4))
        self.S6, self.N6, self.A3 = out.S6, out.N6, out.A3
        self.lnH, self.M, self.lG = out.lnH, out.M, out.lG
        return self

    def collide(self, nu_dtau, kernel="thomson", v_b=None):
        if nu_dtau <= 0.0:
            return self
        _, e, mu, lw = self.geometry()
        if v_b is None or not np.any(v_b):
            self.lG = CM.collide_log(lw, self.lG, e, nu_dtau, kernel)
        else:
            from bianchi.q.boost import collide_moving_log
            self.lG = collide_moving_log(lw, self.lG, e, v_b, nu_dtau, kernel)
        return self

    def residual_step(self, dtau, k_theta=6, k_phi=6, substeps=2):
        """Q5b · 잔여 곡률 이류 (곡률항이 방향공간에 만드는 흐름)."""
        if not self.residual:
            return self
        from bianchi.q.residual import residual_step as rstep
        self.lG, self.jac_min = rstep(self.sph, self.M, self.lG, self.N6,
                                      self.A3, dtau, k_theta, k_phi, substeps)
        return self

    def strang_step(self, dtau, nu=0.0, kernel="thomson", v_b=None):
        """★ 충돌은 **정확 지수** (강성 없음), 잔여 이류는 반-라그랑주,
        나머지는 RK4 — 대칭 배열이라 Strang 2차가 유지된다.

        ★ 85차: 시간의존 ν 용 `nu_end` 인자를 넣었다가 **뺐다** (독립 리뷰 m2).
        뒤 반스텝의 ν 는 RK4 **이후의** lnH 에 의존하므로 여기서는 알 수 없다 —
        시간의존 경로는 `integrate.integrate(sched=...)` 가 순서를 직접 편다."""
        h = abs(dtau)
        self.collide(0.5 * nu * h, kernel, v_b)
        self.residual_step(0.5 * dtau)
        self.rk4_step(dtau)
        self.residual_step(0.5 * dtau)
        self.collide(0.5 * nu * h, kernel, v_b)
        return self

    def ln_omega(self):
        _, e, mu, lw = self.geometry()
        return CM.moments_log(lw, self.lG, e)[0] - np.log(3.0) - 2.0 * self.lnH


def on_gauss_surface(sph, Sigma, N, A, Omega0, lnH=0.0, aniso=None,
                     residual=True):
    """Gauss 를 정확히 만족하도록 격자 진폭을 잡아 초기상태 생성."""
    e_q, w = S.nodes(sph)
    lG = np.zeros(len(w)) if aniso is None else np.asarray(
        [np.log(max(aniso(x), 1e-300)) for x in e_q], float)
    st = QState(sph, Sigma, N, A, lnH, lG, residual=residual)
    Om_now = st.sources()[0]
    st.lG = st.lG + np.log(Omega0 / Om_now)
    return st


def evolve(st, dtau, nsteps, nu=0.0, kernel="thomson", keep=False, v_b=None):
    traj = [st.pack().copy()] if keep else None
    for _ in range(nsteps):
        st.strang_step(dtau, nu, kernel, v_b)
        if keep:
            traj.append(st.pack().copy())
    return (st, np.stack(traj)) if keep else st
