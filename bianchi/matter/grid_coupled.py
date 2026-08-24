"""
I2c · **절단 없는 격자-결합** (75차) — I2b 결정실험의 귀결을 계에 반영.

I2b 가 보인 것: PSTF 절단 계층은 Mixmaster 벽 영역에서 **정성적으로 틀린다**
(dlnΩ/dτ 부호 반전, l_max=4 에서 Ω<0).  ⇒ 결합계의 물질을 **격자**로 나른다.

★ 상태 (절단·보간 **둘 다 없음**):
    y = [Σ5(5), N3(3), lnH, ln a(3), Ĝ(NA)]
  · Ĝ_a = μ_a⁴ Σ_r DQ Q³ F[r,a]  (G2 의 에너지-가중 물리 각밀도).
  · 자유흐름: f 가 불변이므로 Ĝ 의 진화는 **해석**:
        dlnμ_a/dτ = −Σ_i ê_{a,i}²(1+σ_i)   ⇒   dĜ_a/dτ = 4 dlnμ_a/dτ · Ĝ_a
  · 충돌: G2 사다리 (Thomson/BGK) 를 **정확 지수**로 (핵 λ-무관 ⇒ 가중 각밀도와
    가환 — 에너지-교환 정리).  ν(τ) 는 호출자가 준다 (B2b 이력 주입 경로).
  · 소스: ρ = Σ w_phys Ĝ,  π_ab = Σ w_phys Ĝ (ê_aê_b − δ/3)  — 절단 없는 정확값.

게이트: 진공극한 ≡ 차트 · 약물질 지수 ≡ I2b 시험장 격자 (+0.234) ·
       ★강충돌 극한 → 완전유체 지수 (+1.9) 회복 (사다리의 결합계 내 검증) ·
       Gauss 잔차 유계 · f ≥ 0 구조보장 (Ĝ > 0 보존).

LIMITATIONS: class A 대각 절편 (Σ 비대각·회전은 I1d 경로가 담당) · 질량0 ·
단일 종 · Python (Rust 격자-결합은 필요 시 I3b).
★ 깊은 붕괴의 표현범위: 축비가 e^{±300} 를 넘으면 μ⁴ 가 부동소수 범위를 넘는다
  — `LNA_WALL` 이 **명시 거부**한다 (무언 NaN 금지).  해법은 로그-공간 상태
  (ln Ĝ, logsumexp 충돌) — 필요해지는 증분에서 (측정: 무충돌 τ≳−25 는 안전,
  강충돌은 등방화로 축비가 더 빨리 커져 τ≈−8 이 실용 한계).
"""
from __future__ import annotations

import numpy as np

from bianchi.matter import collision_ladder as CL
from bianchi.matter import grid_boltzmann as GB

SQ3 = np.sqrt(3.0)
NA = GB.NA


def pack(S5, N3, lnH, lna, G):
    return np.concatenate([np.asarray(S5, float), np.asarray(N3, float),
                           [float(lnH)], np.asarray(lna, float),
                           np.asarray(G, float)])


def unpack(y):
    y = np.asarray(y, float)
    return y[:5], y[5:8], float(y[8]), y[9:12], y[12:]


def initial_state(S5, N3, Om0, aniso=None, lnH=0.0):
    """Gauss 를 만족하도록 격자 진폭을 잡는다 (Ω(0) = Om0)."""
    lna = np.zeros(3)
    F = GB.initial_grid(aniso=aniso)
    G = CL.angular_density(F, np.exp(lna))
    _, _, w = CL.physical_frame(np.exp(lna))
    rho = float((w * G).sum())
    scale = 3.0 * np.exp(2.0*lnH) * Om0 / rho
    return pack(S5, N3, lnH, lna, G * scale)


def sources(G, lna, lnH):
    """(Ω, Π_diag(3,), Π_full(3,3)) — 절단 없는 정확 모멘트."""
    a = np.exp(lna)
    e, mu, w = CL.physical_frame(a)
    H2 = np.exp(2.0 * lnH)
    rho = float((w * G).sum())
    T = np.einsum("a,a,ai,aj->ij", w, G, e, e)
    Pi = (T - np.trace(T) / 3.0 * np.eye(3)) / H2
    return rho / (3.0 * H2), np.diag(Pi).copy(), Pi


#: 축비 벽 — |ln a_i| 가 이보다 크면 exp 오버플로 영역 (명시 거부).
LNA_WALL = 300.0


def rhs(y, nu=0.0, kind="thomson"):
    S5, N3, lnH, lna, G = unpack(y)
    if np.abs(lna).max() > LNA_WALL:
        raise OverflowError(
            "축비 |ln a| > %g — 격자 μ⁴ 가 표현범위를 넘는다.  로그-공간 상태"
            " (ln Ĝ) 로 옮겨야 한다 (I2c LIMITATIONS; 후속 증분)." % LNA_WALL)
    a = np.exp(lna)
    Sigma2 = float(S5 @ S5)
    n1, n2, n3 = N3
    tn = n1 + n2 + n3
    b = np.array([2*n1*n1 - tn*n1, 2*n2*n2 - tn*n2, 2*n3*n3 - tn*n3])
    b = b - b.mean()
    Om, Pi_d, _ = sources(G, lna, lnH)
    q = 2.0 * Sigma2 + Om                              # 무질량 (γ_eff = 4/3)
    sig = np.array([-2.0*S5[0], S5[0] + SQ3*S5[1], S5[0] - SQ3*S5[1]])
    d = -(2.0 - q) * sig - b + Pi_d
    dS5 = np.array([-d[0]/2.0, (d[1] - d[2])/(2.0*SQ3), 0.0, 0.0, 0.0])
    dN3 = (q + 2.0*sig) * N3
    dlnH = -(1.0 + q)
    dlna = 1.0 + sig
    e, mu, _ = CL.physical_frame(a)
    dlnmu = -np.einsum("ai,i->a", e*e, dlna)
    dG = 4.0 * dlnmu * G
    if nu != 0.0:
        # 충돌은 **정확 지수** (사다리) — RHS 에는 그 생성자를 넣는다:
        #   d/dτ G = ν(K−I)G  (K 는 물리 프레임 핵; a 에 의존)
        if kind == "thomson":
            K = CL.thomson_matrix_rust(a)              # Rust Sinkhorn (eigh 없음)
            dG = dG + nu * (K @ G - G)
        else:
            P, _ = CL._lowl_projector(a, l_max=(0 if kind == "bgk_iso" else 1))
            dG = dG + nu * (P @ G - G)
    return pack(dS5, dN3, dlnH, dlna, dG)


def rk4(y0, tau, nsteps, nu=0.0, kind="thomson", keep=False):
    y = np.asarray(y0, float).copy()
    h = tau / nsteps
    traj = [y.copy()] if keep else None
    for _ in range(nsteps):
        k1 = rhs(y, nu, kind)
        k2 = rhs(y + 0.5*h*k1, nu, kind)
        k3 = rhs(y + 0.5*h*k2, nu, kind)
        k4 = rhs(y + h*k3, nu, kind)
        y = y + (h/6.0) * (k1 + 2*k2 + 2*k3 + k4)
        if keep:
            traj.append(y.copy())
    return (y, np.stack(traj)) if keep else y


def gauss_residual(y):
    S5, N3, lnH, lna, G = unpack(y)
    n1, n2, n3 = N3
    K = (n1*n1 + n2*n2 + n3*n3 - 2.0*(n1*n2 + n2*n3 + n3*n1)) / 12.0
    Om, _, _ = sources(G, lna, lnH)
    return 1.0 - float(S5 @ S5) - K - Om


def omega_series(traj):
    return np.array([sources(unpack(r)[4], unpack(r)[3], unpack(r)[2])[0]
                     for r in traj])
