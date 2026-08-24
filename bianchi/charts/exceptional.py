"""
PR-08 · 예외형 Bianchi VI*_{-1/9} 차트 (Hewitt-Horwood-Wainwright 게이지).

HHW 게이지: n33 = 0, n23 = 3A   <=>   N_+ = sqrt3 N_-,  N_x = sqrt3 A
  * 이 게이지가 kappa = -9 를 **자동으로 강제**한다 (유도 확인).
  * K = N_-^2 + 4 A^2  =>  Omega = 1 - Sigma^2 - N_-^2 - 4A^2
    ★ 계수 4 는 A 의 재정규화가 아니라 게이지 n23 = 3A 의 산물이다.
      A_exc = A_WE  (2배 환산 없음 — U13 가설 기각, conventions.A_EXCEPTIONAL_RESCALE).
  * det L = 0, rank L = 1  ->  off-diagonal shear 한 성분이 살아남는다.
  * 구속 g = (Sigma_+ + sqrt3 Sigma_-) A - Sigma_x N_- = 0,
    g' = 2(q + Sigma_+ - 1) g  (항등적),
    Omega' - [2q-(3g-2)]Omega = -4 A g  (구속면 위에서 소멸).
  * 6변수 - 구속 1개 = 5차원  ->  VIII, IX 와 동등한 일반성.

LIMITATIONS
  - kappa = -9 전용. 다른 kappa 는 charts.class_b.
  - tilt 없음.
"""
from __future__ import annotations

import equinox as eqx
import jax.numpy as jnp

from bianchi.conventions import SQRT3
from bianchi.charts.base import deceleration

name = "exceptional_VI"
LIMITATIONS = __doc__.split("LIMITATIONS")[1].strip()
KAPPA = -9.0

STATE_NAMES = ("Sigma_p", "Sigma_m", "Sigma_2", "Sigma_x", "N_m", "A")


class StateE(eqx.Module):
    Sigma_p: jnp.ndarray
    Sigma_m: jnp.ndarray
    Sigma_2: jnp.ndarray
    Sigma_x: jnp.ndarray
    N_m: jnp.ndarray
    A: jnp.ndarray

    @staticmethod
    def of(Sp, Sm, S2, Sx, Nm, A):
        f = lambda x: jnp.asarray(x, dtype=jnp.float64)
        return StateE(f(Sp), f(Sm), f(S2), f(Sx), f(Nm), f(A))

    def as_array(self):
        return jnp.stack([self.Sigma_p, self.Sigma_m, self.Sigma_2,
                          self.Sigma_x, self.N_m, self.A])

    @staticmethod
    def from_array(v):
        return StateE(v[0], v[1], v[2], v[3], v[4], v[5])


def aux(y: StateE, gamma):
    Sigma2 = y.Sigma_p**2 + y.Sigma_m**2 + y.Sigma_2**2 + y.Sigma_x**2
    K = y.N_m**2 + 4.0 * y.A**2          # 4 는 게이지 n23=3A 산물
    Omega = 1.0 - Sigma2 - K
    q = deceleration(Sigma2, Omega, gamma)
    return dict(Sigma2=Sigma2, K=K, Omega=Omega, q=q)


def rhs(tau, y: StateE, args) -> StateE:
    gamma = args["gamma"]
    a = aux(y, gamma)
    q = a["q"]
    Sp, Sm, S2, Sx, Nm, A = (y.Sigma_p, y.Sigma_m, y.Sigma_2,
                             y.Sigma_x, y.N_m, y.A)
    return StateE(
        Sigma_p=(q - 2.0) * Sp + 3.0 * S2**2 - 2.0 * Nm**2 - 6.0 * A**2,
        Sigma_m=((q - 2.0) * Sm - SQRT3 * S2**2 + 2.0 * SQRT3 * Sx**2
                 - 2.0 * SQRT3 * Nm**2 + 2.0 * SQRT3 * A**2),
        Sigma_2=(q - 3.0 * Sp + SQRT3 * Sm - 2.0) * S2,
        Sigma_x=(q - 2.0 * SQRT3 * Sm - 2.0) * Sx - 8.0 * Nm * A,
        N_m=(q + 2.0 * Sp + 2.0 * SQRT3 * Sm) * Nm + 6.0 * Sx * A,
        A=(q + 2.0 * Sp) * A,
    )


def g_constraint(y: StateE):
    """g = (Sigma_+ + sqrt3 Sigma_-) A - Sigma_x N_-.  (Codazzi C^1 = -6 g)"""
    return (y.Sigma_p + SQRT3 * y.Sigma_m) * y.A - y.Sigma_x * y.N_m


def constraints(y: StateE, args):
    a = aux(y, args["gamma"])
    return dict(g=g_constraint(y), Omega_negative=jnp.maximum(0.0, -a["Omega"]))


def g_propagation_residual(y: StateE, args):
    """g' = 2(q + Sigma_+ - 1) g  — 항등적으로 성립해야 한다."""
    import jax
    v = y.as_array()
    dg = jnp.dot(jax.grad(lambda w: g_constraint(StateE.from_array(w)))(v),
                 rhs(0.0, y, args).as_array())
    a = aux(y, args["gamma"])
    return dg - 2.0 * (a["q"] + y.Sigma_p - 1.0) * g_constraint(y)


def omega_identity_residual(y: StateE, args):
    """Omega' - [2q-(3g-2)]Omega = -4 A g  (구속면 위에서 0)."""
    import jax
    gamma = args["gamma"]
    v = y.as_array()
    dOm = jnp.dot(jax.grad(lambda w: aux(StateE.from_array(w), gamma)["Omega"])(v),
                  rhs(0.0, y, args).as_array())
    a = aux(y, gamma)
    return dOm - (2.0 * a["q"] - (3.0 * gamma - 2.0)) * a["Omega"] + 4.0 * y.A * g_constraint(y)


def on_g_surface(Sp, Sm, S2, Nm, A):
    """g = 0 을 Sigma_x 에 대해 풀어 구속면 위 상태를 만든다 (N_m != 0)."""
    Sx = (Sp + SQRT3 * Sm) * A / Nm
    return StateE.of(Sp, Sm, S2, Sx, Nm, A)


def essential_parameters():
    """6 변수 - 구속 1개 = 5  ->  VIII, IX 와 동등한 일반성 (HHW)."""
    return len(STATE_NAMES) - 1
