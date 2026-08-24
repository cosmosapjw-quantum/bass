"""
F3 · Tilted class A 차트 (n-대각 게이지) — **합성 정의**, 두 경로 검증.

닫힌형을 문헌에서 옮겨 적지 않는다.  이 차트의 RHS 는 저장소에서 이미 제1원리로
확정된 부품의 합성이다:
    기하   : charts.general (Σ' = −(2−q)Σ − ³S + Π + [W,Σ], N' = qN + (SN+NS) + [W,N])
    유체   : matter.fluid (sources / deceleration / dv_general — 4D ∇T=0 대비 3.2e−14)
경로 1 (`rhs`) 은 성분별 전개 (Rust 미러링용), 경로 2 (`rhs_via_general`) 는
general+fluid 를 그대로 합성 — 둘의 일치가 유도 게이트다 (audit/f3, ≤1e−13).

게이지: n 대각 유지가 회전 3개를 전부 소모한다 (BT 와 같은 구조):
    (SN+NS)_ij + W_ij(N_j−N_i) = 0   ⇒   W_ij = S_ij(N_i+N_j)/(N_i−N_j)
    R = (−W₂₃, +W₁₃, −W₁₂)           (W = −ε·R, COMMUTATOR 규약)
  ★ 분모 (N_i−N_j): **LRS 축퇴** — N_i=N_j 인데 S_ij≠0 이면 게이지가 깨진다.
    불변 부분공간 (S_ij≡0, 예: v ∥ 축 type II) 에서는 분자가 정확히 0 → W=0.

상태 (11): Σ₊, Σ₋, Σ₁₂, Σ₁₃, Σ₂₃, N₁, N₂, N₃, v₁, v₂, v₃
    전단행렬: 대각 (−2Σ₊, Σ₊+√3Σ₋, Σ₊−√3Σ₋), 비대각 √3·Σ_ij (BT 규약)
    Σ² = Σ₊²+Σ₋²+Σ₁₂²+Σ₁₃²+Σ₂₃²,  K = [ΣNᵢ² − 2(N₁N₂+N₂N₃+N₃N₁)]/12
    Ω 는 Gauss 로 소거.  A ≡ 0 (class A) 은 dA = qA − SA + WA 에서 정확 보존.

★ N 구조 보존이 tilt 에도 살아남는다: [W,N] 대각 = 0, (SN+NS)ᵢᵢ = 2σᵢNᵢ 라
    Nᵢ' = (q + 2σᵢ)Nᵢ  (곱셈 구조 — Nᵢ=0 과 부호가 부동소수점에서도 정확 보존).

★ 편타면 (whiplash): G₋ = 1 − (γ−1)V².  (55차 리뷰로 2단 정정 — 반증의 반증)
    · γ < 2 : G₋ ≥ 2−γ > 0 — 영교차도, 그 아래 문턱 발화도 **원리적으로 불가**.
    · γ = 2 : 1차 주장 "V²=1 불변 경계라 점근 접근뿐"은 **거짓** — dV² 의
      (1−V²) 인자가 1/G₋ = 1/(1−V²) 와 대수적으로 **정확히 소거**되어 경계
      보호가 사라지고, V²=1 을 **유한 τ 에 관통**한다 (리뷰 실측: on-shell
      IC 에서 τ≈2.15 관통, 이후 V²~10¹⁶ 까지 발산).  따라서 문턱 통과
      (G₋ < ε) 이벤트가 **유일한 유효 종료 신호**이고, 무감시 적분은
      초광속(V²>1) 가드로 별도 차단한다 (solve.rs).

LIMITATIONS
  - LRS 축퇴 (N_i = N_j, S_ij ≠ 0): n-대각 게이지 불능 — audit/f3 가 잰다.
  - 다성분 tilt 는 H'1 몫.  Π 는 유체 자체 (계층 모멘트 아님).
"""
from __future__ import annotations

import equinox as eqx
import jax.numpy as jnp

from bianchi.conventions import SQRT3
from bianchi.matter.fluid import G_minus, G_plus, _safe

name = "class_a_tilted"
LIMITATIONS = __doc__.split("LIMITATIONS")[1].strip()

STATE_NAMES = ("Sigma_p", "Sigma_m", "Sigma_12", "Sigma_13", "Sigma_23",
               "N1", "N2", "N3", "v1", "v2", "v3")


class StateAT(eqx.Module):
    Sigma_p: jnp.ndarray
    Sigma_m: jnp.ndarray
    Sigma_12: jnp.ndarray
    Sigma_13: jnp.ndarray
    Sigma_23: jnp.ndarray
    N1: jnp.ndarray
    N2: jnp.ndarray
    N3: jnp.ndarray
    v1: jnp.ndarray
    v2: jnp.ndarray
    v3: jnp.ndarray

    @staticmethod
    def of(*vals):
        return StateAT(*[jnp.asarray(x, jnp.float64) for x in vals])

    def as_array(self):
        return jnp.stack([self.Sigma_p, self.Sigma_m, self.Sigma_12,
                          self.Sigma_13, self.Sigma_23, self.N1, self.N2,
                          self.N3, self.v1, self.v2, self.v3])

    @staticmethod
    def from_array(v):
        return StateAT(*[v[i] for i in range(11)])

    def v(self):
        return jnp.stack([self.v1, self.v2, self.v3])


def shear_matrix(y: StateAT):
    r3 = SQRT3
    return jnp.array([
        [-2.0*y.Sigma_p,   r3*y.Sigma_12,             r3*y.Sigma_13],
        [r3*y.Sigma_12,    y.Sigma_p + r3*y.Sigma_m,  r3*y.Sigma_23],
        [r3*y.Sigma_13,    r3*y.Sigma_23,             y.Sigma_p - r3*y.Sigma_m],
    ])


def aux(y: StateAT, args):
    g = args["gamma"]
    s2 = (y.Sigma_p**2 + y.Sigma_m**2 + y.Sigma_12**2
          + y.Sigma_13**2 + y.Sigma_23**2)
    n1, n2, n3 = y.N1, y.N2, y.N3
    K = (n1*n1 + n2*n2 + n3*n3 - 2.0*(n1*n2 + n2*n3 + n3*n1)) / 12.0
    Om = args["Omega"] if "Omega" in args else 1.0 - s2 - K
    v1, v2, v3 = y.v1, y.v2, y.v3
    V2 = v1*v1 + v2*v2 + v3*v3
    Gp = _safe(G_plus(g, V2))
    Gm = _safe(G_minus(g, V2))
    q = 2.0*s2 + 0.5*((3.0*g - 2.0) + (2.0 - g)*V2) * Om / Gp
    # σᵢ (전단 대각) — N 의 곱셈 구조를 나르는 계수
    sig = (-2.0*y.Sigma_p, y.Sigma_p + SQRT3*y.Sigma_m,
           y.Sigma_p - SQRT3*y.Sigma_m)
    S = shear_matrix(y)
    vv = jnp.stack([v1, v2, v3])
    SV2 = vv @ (S @ vv)
    return dict(Sigma2=s2, K=K, Omega=Om, q=q, V2=V2, Gp=Gp, Gm=Gm,
                SV2=SV2, sig=sig, S=S)


def gauge_W(y: StateAT):
    """n-대각 유지 회전 (반대칭 성분 3).  0/0 (불변 부분공간)은 정확히 0."""
    r3 = SQRT3
    w12 = r3*y.Sigma_12 * (y.N1 + y.N2) / _safe(y.N1 - y.N2)
    w13 = r3*y.Sigma_13 * (y.N1 + y.N3) / _safe(y.N1 - y.N3)
    w23 = r3*y.Sigma_23 * (y.N2 + y.N3) / _safe(y.N2 - y.N3)
    return w12, w13, w23


def gauge_R(y: StateAT):
    """R 벡터 (W = −ε·R):  R = (−W₂₃, +W₁₃, −W₁₂)."""
    w12, w13, w23 = gauge_W(y)
    return jnp.stack([-w23, w13, -w12])


def rhs(tau, y: StateAT, args) -> StateAT:
    """경로 1 — 성분별 전개 (Rust 가 이 산술을 그대로 미러링한다)."""
    g = args["gamma"]
    a = aux(y, args)
    q, Om, Gp, Gm, V2, SV2 = a["q"], a["Omega"], a["Gp"], a["Gm"], a["V2"], a["SV2"]
    r3 = SQRT3
    S12, S13, S23 = y.Sigma_12, y.Sigma_13, y.Sigma_23
    n1, n2, n3 = y.N1, y.N2, y.N3
    v1, v2, v3 = y.v1, y.v2, y.v3
    w12, w13, w23 = gauge_W(y)
    s1, s2c, s3c = a["sig"]

    # ³S (n 대각 → 대각): Bᵢ = 2Nᵢ² − (trN)Nᵢ, tracefree 사영
    tn = n1 + n2 + n3
    b1 = 2.0*n1*n1 - tn*n1
    b2 = 2.0*n2*n2 - tn*n2
    b3 = 2.0*n3*n3 - tn*n3
    bm = (b1 + b2 + b3) / 3.0
    s3_1, s3_2, s3_3 = b1 - bm, b2 - bm, b3 - bm

    # Π (유체): Π_ab = c_pi (v_a v_b − V²δ_ab/3),  c_pi = 3γΩ/G₊
    c_pi = 3.0*g*Om / Gp
    pi11 = c_pi*(v1*v1 - V2/3.0)
    pi22 = c_pi*(v2*v2 - V2/3.0)
    pi33 = c_pi*(v3*v3 - V2/3.0)
    pi12 = c_pi*v1*v2
    pi13 = c_pi*v1*v3
    pi23 = c_pi*v2*v3

    # dΣ_ab = −(2−q)Σ_ab − ³S_ab + Π_ab + [W,Σ]_ab   (성분별; W 반대칭)
    S12m, S13m, S23m = r3*S12, r3*S13, r3*S23
    c11 = 2.0*(w12*S12m + w13*S13m)
    c22 = 2.0*(-w12*S12m + w23*S23m)
    c33 = 2.0*(-w13*S13m - w23*S23m)
    c12 = w12*(s2c - s1) + w13*S23m + w23*S13m
    c13 = w13*(s3c - s1) + w12*S23m - w23*S12m
    c23 = w23*(s3c - s2c) - w12*S13m - w13*S12m
    d11 = -(2.0 - q)*s1 - s3_1 + pi11 + c11
    d22 = -(2.0 - q)*s2c - s3_2 + pi22 + c22
    d33 = -(2.0 - q)*s3c - s3_3 + pi33 + c33
    d12 = -(2.0 - q)*S12m + pi12 + c12
    d13 = -(2.0 - q)*S13m + pi13 + c13
    d23 = -(2.0 - q)*S23m + pi23 + c23

    # v' = T v − Σv + W v − P,  P = v × (Nv)  (A=0 이라 A·v 항 소멸)
    T = ((3.0*g - 4.0) * (1.0 - V2) + (2.0 - g)*SV2) / Gm
    Sv1 = s1*v1 + S12m*v2 + S13m*v3
    Sv2v = S12m*v1 + s2c*v2 + S23m*v3
    Sv3 = S13m*v1 + S23m*v2 + s3c*v3
    Wv1 = w12*v2 + w13*v3
    Wv2 = -w12*v1 + w23*v3
    Wv3 = -w13*v1 - w23*v2
    P1 = v2*(n3*v3) - v3*(n2*v2)
    P2 = v3*(n1*v1) - v1*(n3*v3)
    P3 = v1*(n2*v2) - v2*(n1*v1)

    return StateAT(
        Sigma_p=-d11 / 2.0,
        Sigma_m=(d22 - d33) / (2.0*r3),
        Sigma_12=d12 / r3,
        Sigma_13=d13 / r3,
        Sigma_23=d23 / r3,
        N1=(q + 2.0*s1)*n1,
        N2=(q + 2.0*s2c)*n2,
        N3=(q + 2.0*s3c)*n3,
        v1=T*v1 - Sv1 + Wv1 - P1,
        v2=T*v2 - Sv2v + Wv2 - P2,
        v3=T*v3 - Sv3 + Wv3 - P3,
    )


def rhs_via_general(tau, y: StateAT, args) -> StateAT:
    """경로 2 — charts.general + matter.fluid 합성 (독립 산술 경로)."""
    from bianchi.charts import general as G
    from bianchi.matter import fluid as F
    a = aux(y, args)
    S = a["S"]
    N = jnp.diag(jnp.stack([y.N1, y.N2, y.N3]))
    A = jnp.zeros(3)
    f = F.TiltedFluid.of(args["gamma"], a["Omega"], y.v())
    s = F.sources(f, S, A)
    R = gauge_R(y)
    gargs = dict(gamma=args["gamma"], q=a["q"], Omega=a["Omega"],
                 Pi=s["Pi"], R=R)
    dG = G.rhs(tau, G.StateG(S, N, A), gargs)
    dv = F.dv_general(f, s, S, N, A, R)
    dS = dG.Sigma
    r3 = SQRT3
    return StateAT(
        Sigma_p=-dS[0, 0] / 2.0,
        Sigma_m=(dS[1, 1] - dS[2, 2]) / (2.0*r3),
        Sigma_12=dS[0, 1] / r3,
        Sigma_13=dS[0, 2] / r3,
        Sigma_23=dS[1, 2] / r3,
        N1=dG.N[0, 0], N2=dG.N[1, 1], N3=dG.N[2, 2],
        v1=dv[0], v2=dv[1], v3=dv[2],
    )


def off_diagonal_n_rate(y: StateAT, args):
    """게이지 감사량: 일반 프레임 dN 의 비대각 성분 (정의상 0 이어야 한다)."""
    from bianchi.charts import general as G
    a = aux(y, args)
    N = jnp.diag(jnp.stack([y.N1, y.N2, y.N3]))
    gargs = dict(gamma=args["gamma"], q=a["q"], Omega=a["Omega"],
                 Pi=jnp.zeros((3, 3)), R=gauge_R(y))
    dG = G.rhs(0.0, G.StateG(a["S"], N, jnp.zeros(3)), gargs)
    dN = dG.N
    return jnp.stack([dN[0, 1], dN[0, 2], dN[1, 2]])


def constraints(y: StateAT, args):
    """**잔차만** (constraints.monitor 계약 — 리뷰 MAJOR 3 정정: G₋/V² 는
    잔차가 아니라 진단량이라 여기 두면 on-shell 상태가 O(1) 위반으로 오보된다;
    diagnostics() 로 분리).  Gauss 는 정의상 0 (Ω 소거)."""
    from bianchi.conventions import codazzi_residual
    from bianchi.matter import fluid as F
    a = aux(y, args)
    f = F.TiltedFluid.of(args["gamma"], a["Omega"], y.v())
    s = F.sources(f, a["S"], jnp.zeros(3))
    N = jnp.diag(jnp.stack([y.N1, y.N2, y.N3]))
    cod = codazzi_residual(a["S"], N, jnp.zeros(3), s["q_flux"])
    return dict(codazzi=cod)


def diagnostics(y: StateAT, args):
    """비-잔차 진단량: G₋(편타 여유), V², LRS 게이지 근접도 (|W| 최댓값)."""
    a = aux(y, args)
    w12, w13, w23 = gauge_W(y)
    return dict(G_minus=a["Gm"], V2=a["V2"],
                gauge_w_max=jnp.max(jnp.abs(jnp.stack([w12, w13, w23]))))


def whiplash_gap(y: StateAT, gamma):
    """G₋ = 1 − (γ−1)V² — 문턱 통과 이벤트의 감시량 (γ≤2: 영교차 불가)."""
    v = y.v()
    return G_minus(gamma, v @ v)
