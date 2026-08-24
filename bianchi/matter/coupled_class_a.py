"""
I1c · Einstein-Boltzmann 결합 진화 — untilted class A, 대각 절편 (67차).

구조 (PLAN-I1-coupled §1): 상태 y = [Σ₊, Σ₋, N₁, N₂, N₃, lnH, Jflat].
    기하 → 계층: (Σ-c5, N) 주입 (τ-시간: H→1 — 계층·N-항이 (H,σ,N) 에 선형).
    계층 → 기하: Ω = J(0,0)/(3H²),  Π_chart = π/H² (π = J(2,0) 텐서),
                 q = 2Σ² + Ω  (무질량: ½(Ω+3P̂), P̂=Ω/3).
    dlnH/dτ = −(1+q).
무질량 i-닫힘: J^{(i)} 전부 동일 (비=1 정확) — i=0 층만 나르고 (l,i+1) 별칭.
절단: l > l_max ⇒ 0 (단순절단 — kin_integrate 와 동일 계약).

대각 절편 계약: 기하는 5-차원 (class_a).  ★ 대각-대칭 부분공간은 닫혀 있다
(66차 분석: 대각 J₂ 의 N-비틀림은 xyz-팔중극을 만들고, 그 되먹임도 대각 J₂ —
쌍극·비대각 π 는 안 생긴다).  q-잔차 (J(1,0)) 와 π-비대각을 **감시 잔차**로
보고; 커지면 대각 차트 이탈 신호 (tilted 결합 I1d 몫).

LIMITATIONS: 무질량 · 대각 class A · Python RK4 (Rust 는 I3) · 충돌항 없음.
"""
from __future__ import annotations

import numpy as np

from bianchi.matter import hierarchy_nterm as HN
from bianchi.matter import pstf_coeff as PC
from bianchi.matter.hierarchy_coeff import hierarchy_rhs_coeff

SQRT3 = np.sqrt(3.0)


def grid_len(l_max):
    return sum(2 * l + 1 for l in range(l_max + 1))


def pack(chart5, lnH, Jc, l_max):
    parts = [np.asarray(chart5, float), [float(lnH)]]
    for l in range(l_max + 1):
        parts.append(np.asarray(Jc[(l, 0)], float).reshape(2 * l + 1))
    return np.concatenate([np.ravel(p) for p in parts])


def unpack(y, l_max):
    y = np.asarray(y, float)
    chart5, lnH = y[:5], float(y[5])
    Jc, o = {}, 6
    for l in range(l_max + 1):
        n = 2 * l + 1
        Jc[(l, 0)] = y[o:o + n]
        o += n
    return chart5, lnH, Jc


class _AliasJ(dict):
    """무질량 별칭 + 단순절단: (l,i) → i=0 층; l>l_max → 0."""

    def __init__(self, Jc, l_max):
        super().__init__()
        self._J, self._lm = Jc, l_max

    def get(self, key, default=None):
        l, i = key
        if l > self._lm:
            return np.zeros(2 * l + 1)
        return self._J[(l, 0)]

    def __getitem__(self, key):
        return self.get(key)


def _sigma_matrix(chart5):
    Sp, Sm = chart5[0], chart5[1]
    return np.diag([-2.0 * Sp, Sp + SQRT3 * Sm, Sp - SQRT3 * Sm])


def _curvature_terms(N):
    n1, n2, n3 = N
    tn = n1 + n2 + n3
    b = np.array([2*n1*n1 - tn*n1, 2*n2*n2 - tn*n2, 2*n3*n3 - tn*n3])
    b -= b.mean()
    K = (n1*n1 + n2*n2 + n3*n3 - 2.0*(n1*n2 + n2*n3 + n3*n1)) / 12.0
    return K, b                                        # ³S 대각 (trace-free)


def sources_from_J(Jc, lnH, l_max):
    """(Ω, Π_diag(3,), π_offdiag_resid, q_resid) — 무질량 소싱."""
    H2 = np.exp(2.0 * lnH)
    rho = float(np.asarray(Jc[(0, 0)]).reshape(1)[0])
    Om = rho / (3.0 * H2)
    Pi_d = np.zeros(3)
    off = 0.0
    if l_max >= 2:
        pi = PC.from_ccoef(Jc[(2, 0)], 2) / H2
        Pi_d = np.array([pi[0, 0], pi[1, 1], pi[2, 2]])
        off = float(max(abs(pi[0, 1]), abs(pi[0, 2]), abs(pi[1, 2])))
    qres = 0.0
    if l_max >= 1:
        qres = float(np.abs(np.asarray(Jc[(1, 0)])).max()) / (3.0 * H2)
    return Om, Pi_d, off, qres


def coupled_rhs(y, l_max, nterm_on=True):
    chart5, lnH, Jc = unpack(y, l_max)
    Sp, Sm = chart5[0], chart5[1]
    N = chart5[2:5]
    Sigma2 = Sp * Sp + Sm * Sm
    K, S3 = _curvature_terms(N)
    Om, Pi_d, _, _ = sources_from_J(Jc, lnH, l_max)
    q = 2.0 * Sigma2 + Om                              # 무질량 (γ_eff = 4/3)
    sig = np.array([-2.0 * Sp, Sp + SQRT3 * Sm, Sp - SQRT3 * Sm])
    # dΣ_ab (대각): −(2−q)σ_a − ³S_a + Π_a  → (₊,₋) 사영
    d = -(2.0 - q) * sig - S3 + Pi_d
    dSp = -d[0] / 2.0
    dSm = (d[1] - d[2]) / (2.0 * SQRT3)
    dN = (q + 2.0 * sig) * N
    dlnH = -(1.0 + q)
    A = _AliasJ(Jc, l_max)
    s5 = PC.to_ccoef(_sigma_matrix(chart5), 2)
    dJ = {}
    for l in range(l_max + 1):
        r = hierarchy_rhs_coeff(A, 1.0, s5, l, 0)      # τ-시간: H→1
        if nterm_on:
            r = r + HN.nterm_coeff(A, N, l, 0)
        dJ[(l, 0)] = r
    return pack(np.array([dSp, dSm, *dN]), dlnH, dJ, l_max)


def rk4_evolve(y0, l_max, tau, nsteps, nterm_on=True, keep=False):
    y = np.asarray(y0, float).copy()
    h = tau / nsteps
    traj = [y.copy()] if keep else None
    for _ in range(nsteps):
        k1 = coupled_rhs(y, l_max, nterm_on)
        k2 = coupled_rhs(y + 0.5 * h * k1, l_max, nterm_on)
        k3 = coupled_rhs(y + 0.5 * h * k2, l_max, nterm_on)
        k4 = coupled_rhs(y + h * k3, l_max, nterm_on)
        y = y + (h / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        if keep:
            traj.append(y.copy())
    return (y, np.stack(traj)) if keep else y


def gauss_residual(y, l_max):
    chart5, lnH, Jc = unpack(y, l_max)
    Sp, Sm = chart5[0], chart5[1]
    K, _ = _curvature_terms(chart5[2:5])
    Om, _, _, _ = sources_from_J(Jc, lnH, l_max)
    return 1.0 - (Sp * Sp + Sm * Sm) - K - Om


def monitors(y, l_max):
    """감시 잔차: (Gauss, q-잔차, π-비대각) — 대각 절편 계약의 상시 확인."""
    chart5, lnH, Jc = unpack(y, l_max)
    _, _, off, qres = sources_from_J(Jc, lnH, l_max)
    return dict(gauss=gauss_residual(y, l_max), q_resid=qres, pi_offdiag=off)


def isotropic_ic(chart5, lnH, l_max, rho=None):
    """등방 J(0,0) 만 — Gauss 를 정확히 맞추도록 ρ 결정 (기본)."""
    chart5 = np.asarray(chart5, float)
    Sp, Sm = chart5[0], chart5[1]
    K, _ = _curvature_terms(chart5[2:5])
    H2 = np.exp(2.0 * lnH)
    if rho is None:
        rho = 3.0 * H2 * (1.0 - Sp * Sp - Sm * Sm - K)
    Jc = {(l, 0): np.zeros(2 * l + 1) for l in range(l_max + 1)}
    Jc[(0, 0)] = np.array([float(rho)])
    return pack(chart5, lnH, Jc, l_max)
