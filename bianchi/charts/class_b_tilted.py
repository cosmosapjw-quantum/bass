"""
PR-16 · Tilted class B 차트 (Hervik 게이지) — 전부 제1원리 유도 확정.

게이지: n22 = n33 = sqrt3 lambda N,  n23 = sqrt3 N,  a = (A,0,0)

프레임 사전 (U12 확정):
    N = N_x ,  N_- = 0 ,  lambda = N_+/(sqrt3 N_x)
    n-대각 프레임과는 e_1 축 45도 회전:  (Sigma_-, Sigma_x) -> (Sigma_x, -Sigma_-)
    n2 n3 = -3 N^2 (1-lambda^2)   =>  C_5: A^2 + 3h(1-lambda^2)N^2 = 0
    K = N^2 + A^2                 =>  C_1: Sigma^2 + A^2 + N^2 + Omega = 1

★ 게이지 유지가 회전 **3개 전부**를 소모한다:
    R_1 = -sqrt3 Sigma_- lambda ,  R_2 = sqrt3 Sigma_13 ,  R_3 = -sqrt3 Sigma_12
  Sigma_+' 의 3(Sigma_12^2 + Sigma_13^2) 항은 곡률도 shear 도 아니라 이 **회전항**이다.
  R_1 만 켜면 shear 방정식이 전부 틀리는데 N', lambda', A' 는 맞아 보인다.

상태 (11): Sigma_+, Sigma_-, Sigma_12, Sigma_13, Sigma_23, N, lambda, A, v_1..v_3
구속 (5) : C_1 (Gauss), C_2..C_4 (Codazzi), C_5 (군 파라미터)
           유도된 Codazzi = -3 x (C_2, C_3, C_4)  (3성분 모두 확인)

LIMITATIONS
  - class B 전용. |lambda| <= 1.
  - Gauss 는 단독으로 닫히지 않는다 (Codazzi 아이디얼 필요, ADM 표준 구조).
"""
from __future__ import annotations

import equinox as eqx
import jax.numpy as jnp

from bianchi.conventions import SQRT3
from bianchi.matter.fluid import G_plus, G_minus, _safe

name = "class_b_tilted"
LIMITATIONS = __doc__.split("LIMITATIONS")[1].strip()

STATE_NAMES = ("Sigma_p", "Sigma_m", "Sigma_12", "Sigma_13", "Sigma_23",
               "N", "lam", "A", "v1", "v2", "v3")


class StateBT(eqx.Module):
    Sigma_p: jnp.ndarray
    Sigma_m: jnp.ndarray
    Sigma_12: jnp.ndarray
    Sigma_13: jnp.ndarray
    Sigma_23: jnp.ndarray
    N: jnp.ndarray
    lam: jnp.ndarray
    A: jnp.ndarray
    v1: jnp.ndarray
    v2: jnp.ndarray
    v3: jnp.ndarray

    @staticmethod
    def of(*vals):
        return StateBT(*[jnp.asarray(x, jnp.float64) for x in vals])

    def as_array(self):
        return jnp.stack([self.Sigma_p, self.Sigma_m, self.Sigma_12, self.Sigma_13,
                          self.Sigma_23, self.N, self.lam, self.A,
                          self.v1, self.v2, self.v3])

    @staticmethod
    def from_array(v):
        return StateBT(*[v[i] for i in range(11)])

    def v(self):
        return jnp.stack([self.v1, self.v2, self.v3])


# ---------------------------------------------------------------- 보조량
def shear_matrix(y: StateBT):
    """Sigma_ab (Hervik 파라미터화)."""
    r3 = SQRT3
    return jnp.array([
        [-2*y.Sigma_p,      r3*y.Sigma_12,          r3*y.Sigma_13],
        [r3*y.Sigma_12, y.Sigma_p + r3*y.Sigma_m,   r3*y.Sigma_23],
        [r3*y.Sigma_13,     r3*y.Sigma_23,      y.Sigma_p - r3*y.Sigma_m],
    ])


def aux(y: StateBT, args):
    g = args["gamma"]
    Om = args["Omega"] if "Omega" in args else None
    S = shear_matrix(y)
    Sigma2 = jnp.trace(S @ S) / 6.0
    K = y.N**2 + y.A**2                       # C_1 (유도 확인)
    v = y.v(); V2 = v @ v
    if Om is None:
        Om = 1.0 - Sigma2 - K
    Gp = _safe(G_plus(g, V2))
    q = 2.0*Sigma2 + 0.5*((3.0*g - 2.0) + (2.0 - g)*V2) * Om / Gp
    SV2 = jnp.einsum("ab,a,b->", S, v, v)
    Adv = y.A * y.v1
    return dict(Sigma2=Sigma2, K=K, Omega=Om, q=q, V2=V2, Gp=Gp,
                SV2=SV2, Adv=Adv, S=S)


# ---------------------------------------------------------------- RHS
def rhs(tau, y: StateBT, args) -> StateBT:
    g = args["gamma"]
    a = aux(y, args)
    q, Om, Gp, V2, SV2, Adv = (a["q"], a["Omega"], a["Gp"], a["V2"],
                               a["SV2"], a["Adv"])
    r3 = SQRT3
    Sp, Sm, S12, S13, S23 = (y.Sigma_p, y.Sigma_m, y.Sigma_12,
                             y.Sigma_13, y.Sigma_23)
    N, lam, A = y.N, y.lam, y.A
    v1, v2, v3 = y.v1, y.v2, y.v3
    Gm = _safe(G_minus(g, V2))
    T = (((3.0*g - 4.0) - 2.0*(g - 1.0)*Adv) * (1.0 - V2) + (2.0 - g)*SV2) / Gm

    return StateBT(
        # ★ 3(S12^2+S13^2) 는 프레임 회전항 (R_2, R_3 에서 나온다)
        Sigma_p=((q - 2.0)*Sp + 3.0*(S12**2 + S13**2) - 2.0*N**2
                 + (g*Om/(2.0*Gp)) * (-2.0*v1**2 + v2**2 + v3**2)),
        Sigma_m=((q - 2.0 - 2.0*r3*S23*lam)*Sm + r3*(S12**2 - S13**2) + 2.0*A*N
                 + (r3*g*Om/(2.0*Gp)) * (v2**2 - v3**2)),
        Sigma_12=((q - 2.0 - 3.0*Sp - r3*Sm)*S12 - r3*(S23 + Sm*lam)*S13
                  + (r3*g*Om/Gp)*v1*v2),
        Sigma_13=((q - 2.0 - 3.0*Sp + r3*Sm)*S13 - r3*(S23 - Sm*lam)*S12
                  + (r3*g*Om/Gp)*v1*v3),
        # 의심받았던 +2 sqrt3 lambda Sigma_-^2 항: 계수 정확히 2 sqrt3 (유도 확정)
        Sigma_23=((q - 2.0)*S23 - 2.0*r3*N**2*lam + 2.0*r3*lam*Sm**2
                  + 2.0*r3*S12*S13 + (r3*g*Om/Gp)*v2*v3),
        N=(q + 2.0*Sp + 2.0*r3*S23*lam) * N,
        lam=2.0*r3*S23*(1.0 - lam**2),
        A=(q + 2.0*Sp) * A,
        v1=((T + 2.0*Sp)*v1 - 2.0*r3*S13*v3 - 2.0*r3*S12*v2
            - A*(v2**2 + v3**2) - r3*N*(v2**2 - v3**2)),
        v2=((T - Sp - r3*Sm)*v2 - r3*(S23 + Sm*lam)*v3
            + r3*lam*N*v1*v3 + (A + r3*N)*v1*v2),
        v3=((T - Sp + r3*Sm)*v3 - r3*(S23 - Sm*lam)*v2
            - r3*lam*N*v1*v2 + (A - r3*N)*v1*v3),
    )


def dOmega(y: StateBT, args):
    """Omega' — 분모 G_+ (U4 확정).

    ★ V15/C2 감사 수확: 이 닫힌형은 **Codazzi 온셸(C₂=C₃=C₄=0) 전용**이다.
      오프셸에서는 사슬법칙 dΩ 와 ~1e−1 급으로 다르고, 구속면 위에서는 1e−14 로
      일치한다 (실측 4점).  class B 의 b3=−4 가 온셸 전용인 것과 같은 구조인데
      여기엔 그 단서가 빠져 있었다 — `test_c2_chart_coverage` 가 이 사실을 고정한다.
    """
    g = args["gamma"]
    a = aux(y, args)
    Om, q, Gp, V2 = a["Omega"], a["q"], a["Gp"], a["V2"]
    return (Om / Gp) * (
        2.0*q - (3.0*g - 2.0) + 2.0*g*a["Adv"]
        + (2.0*q*(g - 1.0) - (2.0 - g))*V2 - g*a["SV2"]
    )


# ---------------------------------------------------------------- 구속 C_1..C_5
def constraints(y: StateBT, args):
    g = args["gamma"]
    a = aux(y, args)
    Om, Gp = a["Omega"], a["Gp"]
    r3 = SQRT3
    h = args.get("h", None)
    C1 = a["Sigma2"] + y.A**2 + y.N**2 + Om - 1.0
    C2 = 2.0*y.Sigma_p*y.A + 2.0*y.Sigma_m*y.N + g*Om*y.v1/Gp
    C3 = -(y.Sigma_12*(y.N + r3*y.A) + y.Sigma_13*y.lam*y.N) + g*Om*y.v2/Gp
    C4 = (y.Sigma_13*(y.N - r3*y.A) + y.Sigma_12*y.lam*y.N) + g*Om*y.v3/Gp
    out = dict(C1=C1, C2=C2, C3=C3, C4=C4)
    if h is not None:
        out["C5"] = y.A**2 + 3.0*h*(1.0 - y.lam**2)*y.N**2
    return out


def codazzi_derived(y: StateBT, args):
    """유도된 Codazzi C^a. Hervik 의 (C_2,C_3,C_4) 와 비 = -3."""
    from bianchi.conventions import codazzi_residual
    a = aux(y, args)
    g = args["gamma"]
    q_flux = 3.0 * g * a["Omega"] * y.v() / a["Gp"]
    r3 = SQRT3
    N = jnp.array([[0.0, 0.0, 0.0],
                   [0.0, r3*y.lam*y.N, r3*y.N],
                   [0.0, r3*y.N, r3*y.lam*y.N]])
    A = jnp.array([y.A, 0.0, 0.0])
    return codazzi_residual(a["S"], N, A, q_flux)


def frame_dictionary():
    """n-대각 프레임 <-> Hervik 프레임 사전 (U12 확정)."""
    return {
        "N": "N_x",
        "N_minus": 0.0,
        "lambda": "N_+/(sqrt3 * N_x)",
        "rotation": "e_1 축 45도:  (Sigma_-, Sigma_x) -> (Sigma_x, -Sigma_-)",
        "n2n3": "-3 N^2 (1 - lambda^2)",
        "K": "N^2 + A^2",
    }


def gauge_rotations(y: StateBT):
    """게이지 유지가 강제하는 R_1, R_2, R_3 (함정 2)."""
    from bianchi.conventions import gauge_rotation_classB
    return gauge_rotation_classB(y.Sigma_m, y.Sigma_12, y.Sigma_13, y.lam)
