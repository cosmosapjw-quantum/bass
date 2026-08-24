"""
PR-42 · 기울어진 유체 합동의 운동학:  팽창 θ_u, 가속도 u̇_a, vorticity ω_ab, CMB 쌍극.

법선 합동 e_0 는 측지·비회전(ω=0)이지만, 물질의 4-속도

    u^μ = Γ(e_0 + v^a e_a),   Γ = 1/√(1 - v²)

는 tilt v 때문에 일반적으로 vorticity 를 가진다.  운동학은 프레임 접속
(rays.frame.frame_connection, d_transport 잔차 ≤ 6.7e-16) 의 이중축약으로 계산한다:

    ∇_c u_b = e_c(u_b) - Γ^d_{bc} u_d           (동차성 ⇒ 공간 e_i(u_b)=0)
    θ_u   = ∇_a u^a
    u̇_b  = u^c ∇_c u_b                          (가속도)
    ω_μν  = h_μ^ρ h_ν^σ ∇_[σ u_ρ] ,  h = δ + u⊗u  (u-직교 사영)

★ D22 (부채 A, v1.4 로 해소):  ω 는 off-shell 에서 v̇ 에 **진짜로** 의존한다(물리).
  관측량은 **on-shell** ω 다 — 운동량 보존(∇_μT^μν=0)이 v̇ 를 결정하면 가속도가 v 에
  평행해지고(잔차 1.8e-10), 공간 vorticity 는 **EOS-무관**(4.9e-11)·u-직교·반대칭·
  v=0 에서 0 인 깨끗한 상태함수가 된다 (audit/d_vorticity.py).

여기의 σ, N, A 는 **차원량** (Hubble 정규화 아님) — 광선/합동 계산은 우주시간 t 로 한다.

CMB 쌍극:  관측자(물질)가 CMB 정지틀(법선 합동) 대비 v 로 움직이면 상대론적 도플러로
    T(n̂) = T₀ √(1-v²)/(1 - v·n̂)  → 선두차수 쌍극 진폭 β = |v|.
"""
from __future__ import annotations

import numpy as np

from bianchi.rays.frame import frame_connection

_ETA = np.diag([-1.0, 1.0, 1.0, 1.0])

#: Planck 2015 (VII_h) vorticity 상한 (ω/H)₀ < 7.6e-10 (95% CL) — 참조 오라클.
PLANCK_VORTICITY_BOUND = 7.6e-10


def four_velocity(v):
    """u^μ (upper), u_μ (lower).  u = Γ(1, v),  u·u = -1."""
    v = np.asarray(v, float)
    Gam = 1.0 / np.sqrt(1.0 - v @ v)
    u_up = np.array([Gam, *(Gam * v)])
    u_lo = _ETA @ u_up                       # (-Γ, Γv)
    return u_up, u_lo, float(Gam)


def velocity_gradient(H, sigma, N, A, R, v, vdot):
    """∇_c u_b  (4×4, b=벡터 지표, c=미분 슬롯).  vdot = dv/dt (차원량, per t)."""
    G = np.asarray(frame_connection(H, sigma, N, A, R), float)   # G[a,b,c]=Γ^a_bc
    v = np.asarray(v, float); vdot = np.asarray(vdot, float)
    Gam = 1.0 / np.sqrt(1.0 - v @ v)
    Gdot = Gam ** 3 * (v @ vdot)                                 # dΓ/dt
    u_lo = np.array([-Gam, *(Gam * v)])
    du_lo = np.array([-Gdot, *(Gdot * v + Gam * vdot)])          # d(u_b)/dt
    Du = np.zeros((4, 4))
    for b in range(4):
        for c in range(4):
            e_c = du_lo[b] if c == 0 else 0.0                    # 동차 ⇒ 공간미분 0
            Du[b, c] = e_c - sum(G[d, b, c] * u_lo[d] for d in range(4))
    return Du


def congruence_kinematics(H, sigma, N, A, R, v, vdot):
    """유체 합동의 (θ_u, u̇_a, ω_μν, ω_ab, ω_vec) 를 반환.

        theta   : ∇_a u^a  (팽창)
        accel   : u̇^μ = u^c ∇_c u^μ  (4-가속도, upper)
        omega4  : ω_μν  (4×4, u-사영·반대칭)
        omega3  : 공간 블록 ω_ab (3×3) — 관측 vorticity
        omega_vec : ω_ab 의 축벡터 ω^a = -½ eps^{abc} ω_bc
    """
    u_up, u_lo, Gam = four_velocity(v)
    Du = velocity_gradient(H, sigma, N, A, R, v, vdot)
    theta = float(np.einsum("bc,bc->", _ETA, Du))               # ∇_a u^a = η^{ac}∇_c u_a
    # 가속도 u̇_b = u^c ∇_c u_b, 올림
    acc_lo = np.array([sum(u_up[c] * Du[b, c] for c in range(4)) for b in range(4)])
    acc_up = _ETA @ acc_lo
    # vorticity: 완전 사영 반대칭부.  h_μ^ρ = δ + u_μ u^ρ
    h = np.eye(4) + np.outer(u_lo, u_up)
    K = np.einsum("ma,nb,ab->mn", h, h, Du)
    omega4 = 0.5 * (K - K.T)
    omega3 = omega4[1:, 1:]
    from bianchi.conventions import EPS3
    omega_vec = -0.5 * np.einsum("abc,bc->a", EPS3, omega3)
    return dict(theta=theta, accel=acc_up, accel_lo=acc_lo,
                omega4=omega4, omega3=omega3, omega_vec=omega_vec,
                u_up=u_up, Gamma=Gam)


# ---------------------------------------------------------------- on-shell v̇ (운동량 보존)
def onshell_vdot(H, sigma, N, A, R, v, gamma, rho):
    """∇_μ T^μν = 0 (차원량 gamma-law 유체) 로부터 on-shell dv/dt 를 선형해로 구한다.

    T^{μν} = γρ Γ² u^μu^ν + (γ-1)ρ η^{μν}.  미지수 (ρ̇, v̇) 4개를 divT=0 4식으로.
    (audit/d_vorticity.py 의 검증된 절차를 프레임 접속 위에서 재현.)
    """
    G = np.asarray(frame_connection(H, sigma, N, A, R), float)
    v = np.asarray(v, float); g4 = _ETA

    def Tup(rho_, v_):
        G2 = 1.0 / (1.0 - v_ @ v_)
        uup = np.array([np.sqrt(G2), *(np.sqrt(G2) * v_)])
        return gamma * rho_ * np.outer(uup, uup) + (gamma - 1.0) * rho_ * g4

    def divT(rhod, vd):
        h = 1e-6
        dT = (Tup(rho + h * rhod, v + h * vd) - Tup(rho - h * rhod, v - h * vd)) / (2 * h)
        Tu = Tup(rho, v)
        out = np.zeros(4)
        for nu in range(4):
            tot = dT[0, nu]                                     # ∂_0 T^{0ν}
            for c in range(4):
                tot += sum(G[c, d, c] * Tu[d, nu] for d in range(4))   # Γ^c_{dc} T^{dν}
                tot += sum(G[nu, d, c] * Tu[c, d] for d in range(4))   # Γ^ν_{dc} T^{cd}
            out[nu] = tot
        return out

    b = -divT(0.0, np.zeros(3))
    M = np.zeros((4, 4))
    cols = [(1.0, np.zeros(3))] + [(0.0, np.eye(3)[k]) for k in range(3)]
    for j, (dr, dv) in enumerate(cols):
        M[:, j] = divT(dr, dv) + b
    X = np.linalg.solve(M, b)
    return X[1:]                                                # v̇ (dv/dt)


def onshell_kinematics(H, sigma, N, A, R, v, gamma, rho):
    """운동량 보존으로 v̇ 를 공급한 뒤 합동 운동학을 계산 (관측 vorticity)."""
    vd = onshell_vdot(H, sigma, N, A, R, v, gamma, rho)
    k = congruence_kinematics(H, sigma, N, A, R, v, vd)
    k["vdot"] = vd
    return k


def vorticity_scalar(omega3):
    """ω = √(½ ω_ab ω^ab)  (vorticity 스칼라, 차원량)."""
    om = np.asarray(omega3, float)
    return float(np.sqrt(0.5 * np.einsum("ab,ab->", om, om)))


def vorticity_over_H(omega3, H):
    """(ω/H) — Planck VII_h 상한 PLANCK_VORTICITY_BOUND 과 비교할 정규화 vorticity."""
    return vorticity_scalar(omega3) / abs(H)


# ---------------------------------------------------------------- CMB 쌍극 (tilt 도플러)
def cmb_temperature_pattern(v, nhat, T0=1.0):
    """상대론적 도플러 T(n̂) = T₀ √(1-v²)/(1 - v·n̂).  n̂: 관측 방향(단위)."""
    v = np.asarray(v, float); nhat = np.asarray(nhat, float)
    nhat = nhat / np.linalg.norm(nhat)
    return T0 * np.sqrt(1.0 - v @ v) / (1.0 - v @ nhat)


def cmb_dipole_amplitude(v):
    """선두차수 쌍극 진폭 β = |v|  (ΔT/T = v·n̂ + O(v²))."""
    return float(np.linalg.norm(np.asarray(v, float)))


def cmb_multipoles_from_tilt(v):
    """tilt 도플러의 저차 다극 진폭 (축대칭, μ=cosθ 전개).

        ΔT/T = √(1-v²)/(1-βμ) - 1,  β=|v|
             = βμ + β²(μ² - 1/2) + ...        (선두: 쌍극 β, 사중극 β²/3 형)
    반환 dict(beta, dipole=β, quadrupole≈β²/3):  정확 다극은 도플러 급수의 표준결과.
    """
    beta = float(np.linalg.norm(np.asarray(v, float)))
    return dict(beta=beta, dipole=beta, quadrupole=beta ** 2 / 3.0)


def normal_congruence_is_irrotational(H, sigma, N, A, R):
    """법선 합동(v=0)은 vorticity=0 (구성상).  검증용: ω_ab 최대성분 반환(≈0)."""
    k = congruence_kinematics(H, sigma, N, A, R, np.zeros(3), np.zeros(3))
    return float(np.abs(k["omega3"]).max())
