"""
I2 · Mixmaster 물질 보정의 측정 (70차) — 'BKL 물질 무시' 를 수치로.

설정: type II 벽 (BKL 기본 튐), 무질량 운동종, 붕괴 방향 (τ<0),
결합 루프 = I3 Rust (cp_evolve).  IC: 진공 Taub-II 궤도점을 Gauss 로
Ω₀ 만큼 보정 (N₁² = 12(1−Σ²−Ω₀)).

측정 (70차 실측, 창 τ∈[−5,0], IC Σ=(0.3,0.4)):
  · 진공 극한 (Ω₀=1e−12): |ΔL| = 2.4e−11 — 결합기계 안에서 F2 Taub-II
    제1적분 회귀.
  · ★ 선형 응답: ΔL = C·Ω₀^p,  p = 0.99, C ≈ 11.8 (Ω₀ ≤ 1e−2) —
    'BKL 무시' 의 정량형: 벽 하나당 궤도 보정이 Ω 에 1차.
  · ★ 에너지 항등 (기계 관통, rhs-기반): dlnΩ/dτ = (2q−2) − Σ:Π/(3Ω)
    잔차 1.3e−15;  일-항 |W| 최대 ≈ 2 — 벽에서 이방압력 일이 O(1).
  · ★★ 절단-민감 발견: max|J₂|/J₀ 가 l_max=3 → 1.02, l_max=5 → 8.8 —
    자유흐름 다극이 벽 영역에서 절단-민감 성장 (π/ρ>1 은 f≥0 위배 신호):
    무충돌 근사의 유효범위 측정.  정칙화는 충돌 (G1/B2b) 몫.
"""
from __future__ import annotations

import numpy as np

from bianchi.matter import coupled_tilted as CT
from bianchi.matter import pstf_coeff as PC


def type_ii_collapse(Om0, tau=-5.0, ns=4000, lmax=3, Sp=0.3, Sm=0.4):
    """붕괴 궤적 (keep) — IC 는 Gauss-보정 Taub-II 점."""
    s2 = Sp*Sp + Sm*Sm
    N1 = np.sqrt(12.0 * (1.0 - s2 - Om0))
    Jc = {(l, 0): np.zeros(2*l + 1) for l in range(lmax + 1)}
    Jc[(0, 0)] = np.array([3.0 * Om0])                 # lnH = 0
    y = CT.pack(np.array([Sp, Sm, 0, 0, 0]), np.array([N1, 0, 0]), 0.0,
                np.zeros(0), np.zeros((0, 3)), Jc, lmax)
    return CT.rk4_evolve_rust(y, np.zeros(0), lmax, tau, ns, keep=True)[1]


def L_drift(traj):
    """|ΔL|, L = (2−Σ₊)/Σ₋ (F2 제1적분)."""
    L = (2.0 - traj[:, 0]) / traj[:, 1]
    return abs(float(L[-1] - L[0]))


def linear_response(oms=(1e-3, 1e-2)):
    """(p, C): ΔL = C·Ω₀^p 적합 (2점 로그기울기)."""
    d = [L_drift(type_ii_collapse(o)) for o in oms]
    p = np.log(d[1]/d[0]) / np.log(oms[1]/oms[0])
    C = d[1] / oms[1]**p
    return float(p), float(C), d


def energy_identity_residual(Om0=1e-2, lmax=3, ns=4000, stride=200):
    """rhs-기반: |dlnΩ − (2q−2) + Σ:Π/(3Ω)| 최대 + 일-항 최대."""
    traj = type_ii_collapse(Om0, ns=ns, lmax=lmax)
    worst, wmax = 0.0, 0.0
    r3 = np.sqrt(3.0)
    for k in range(0, ns + 1, stride):
        row = traj[k]
        d = CT.coupled_rhs_rust(row, np.zeros(0), lmax)
        S5, lnH = row[:5], row[8]
        H2 = np.exp(2.0 * lnH)
        J0, dJ0 = row[9], d[9]
        c2 = row[13:18]
        dlnOm = dJ0 / J0 - 2.0 * d[8]
        S = np.array([[-2*S5[0], r3*S5[2], r3*S5[3]],
                      [r3*S5[2], S5[0]+r3*S5[1], r3*S5[4]],
                      [r3*S5[3], r3*S5[4], S5[0]-r3*S5[1]]])
        Om = J0 / (3.0 * H2)
        q = 2.0 * float(S5 @ S5) + Om
        pi = np.asarray(PC.from_ccoef(c2, 2), float) / H2
        W = -float(np.einsum("ab,ab->", S, pi)) / (3.0 * Om)
        worst = max(worst, abs(dlnOm - ((2.0*q - 2.0) + W)))
        wmax = max(wmax, abs(W))
    return worst, wmax


def truncation_sensitivity(Om0=1e-2, ns=4000):
    """{l_max: max|J₂|/J₀} — 절단-민감 성장의 실측 (발견 박제용)."""
    out = {}
    for lmax in (3, 5):
        traj = type_ii_collapse(Om0, ns=ns, lmax=lmax)
        o = 9
        J0 = traj[:, o]
        c2 = traj[:, o + 4:o + 9]
        out[lmax] = float(np.max(np.abs(c2).max(axis=1) / J0))
    return out
