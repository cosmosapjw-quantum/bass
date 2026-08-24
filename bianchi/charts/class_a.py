"""
PR-06 · Class A 비틸트 차트 (Wainwright-Hsu, WE 규약).

상태: (Sigma_+, Sigma_-, N_1, N_2, N_3);  Omega 는 Gauss 로 소거.

★ N_i' = (...) N_i 라는 **곱셈 구조** 덕분에 N_i = 0 과 부호가 부동소수점에서도
  정확히 보존된다 -> 유형 안전성이 구조적으로 보장된다 (Layer 0 는 근사적).

LIMITATIONS
  - class B (A != 0) 를 다룰 수 없다.
  - tilt 없음 (비대각 shear 를 담지 못한다).
  - Bianchi IX 재붕괴 구간에서 H -> 0 이면 발산한다 -> charts.type_ix_d 사용.
"""
from __future__ import annotations

import equinox as eqx
import jax.numpy as jnp

from bianchi.conventions import K_COEFF_WE, S_COEFF_WE, SQRT3
from bianchi.charts.base import deceleration

name = "class_a"
LIMITATIONS = __doc__.split("LIMITATIONS")[1].strip()

STATE_NAMES = ("Sigma_p", "Sigma_m", "N1", "N2", "N3")


class StateA(eqx.Module):
    Sigma_p: jnp.ndarray
    Sigma_m: jnp.ndarray
    N1: jnp.ndarray
    N2: jnp.ndarray
    N3: jnp.ndarray

    @staticmethod
    def of(Sp, Sm, N1, N2, N3):
        f = lambda x: jnp.asarray(x, dtype=jnp.float64)
        return StateA(f(Sp), f(Sm), f(N1), f(N2), f(N3))

    def as_array(self):
        return jnp.stack([self.Sigma_p, self.Sigma_m, self.N1, self.N2, self.N3])

    @staticmethod
    def from_array(v):
        return StateA(v[0], v[1], v[2], v[3], v[4])


# ---------------------------------------------------------------- 보조량
def curvature_K(N1, N2, N3):
    return K_COEFF_WE * (
        N1**2 + N2**2 + N3**2 - 2.0 * (N1*N2 + N2*N3 + N3*N1)
    )


def S_plus(N1, N2, N3):
    return S_COEFF_WE * ((N2 - N3)**2 - N1 * (2.0*N1 - N2 - N3))


def S_minus(N1, N2, N3):
    return (N3 - N2) * (N1 - N2 - N3) / (2.0 * SQRT3)


def aux(y: StateA, gamma):
    Sp, Sm = y.Sigma_p, y.Sigma_m
    Sigma2 = Sp**2 + Sm**2
    K = curvature_K(y.N1, y.N2, y.N3)
    Omega = 1.0 - Sigma2 - K
    q = deceleration(Sigma2, Omega, gamma)
    return dict(Sigma2=Sigma2, K=K, Omega=Omega, q=q)


# ---------------------------------------------------------------- RHS
def rhs(tau, y: StateA, args) -> StateA:
    gamma = args["gamma"]
    a = aux(y, gamma)
    q, Sp, Sm = a["q"], y.Sigma_p, y.Sigma_m
    N1, N2, N3 = y.N1, y.N2, y.N3
    return StateA(
        Sigma_p=-(2.0 - q) * Sp - S_plus(N1, N2, N3),
        Sigma_m=-(2.0 - q) * Sm - S_minus(N1, N2, N3),
        # 곱셈 구조: N_i = 0 이 정확히 보존된다
        N1=(q - 4.0*Sp) * N1,
        N2=(q + 2.0*Sp + 2.0*SQRT3*Sm) * N2,
        N3=(q + 2.0*Sp - 2.0*SQRT3*Sm) * N3,
    )


# ---------------------------------------------------------------- 구속·진단
def constraints(y: StateA, args):
    """Gauss 는 Omega 정의에 흡수됨. 물리 영역 위반만 잔차로 보고."""
    a = aux(y, args["gamma"])
    return dict(
        Omega_negative=jnp.maximum(0.0, -a["Omega"]),
        gauss=jnp.asarray(0.0),      # 정의상 0 (Omega 를 소거했으므로)
    )


def omega_identity_residual(y: StateA, args):
    """오라클 A 의 런타임 버전: Omega' - [2q-(3g-2)]Omega."""
    import jax
    gamma = args["gamma"]
    f = lambda v: aux(StateA.from_array(v), gamma)["Omega"]
    v = y.as_array()
    dOm = jnp.dot(jax.grad(f)(v), rhs(0.0, y, args).as_array())
    a = aux(y, gamma)
    return dOm - (2.0*a["q"] - (3.0*gamma - 2.0)) * a["Omega"]


def state_norm(y: StateA):
    return jnp.max(jnp.abs(y.as_array()))


def type_of(y: StateA, tol=1e-12):
    """N_i 부호로 유형 판정 (곱셈 구조 덕에 정확)."""
    import numpy as np
    from bianchi import algebra as alg
    n = np.array([float(y.N1), float(y.N2), float(y.N3)])
    n = np.where(np.abs(n) < tol, 0.0, n)
    return alg.classify(n, np.zeros(3))


# ---------------------------------------------------------------- 초기조건 헬퍼
def kasner(psi):
    """진공 Bianchi I 의 Kasner 원 위 점: Sigma_+^2 + Sigma_-^2 = 1."""
    return StateA.of(jnp.cos(psi), jnp.sin(psi), 0.0, 0.0, 0.0)


def from_type(type_name, Sp=0.0, Sm=0.0, scale=1.0):
    """알려진 유형의 대표 초기조건."""
    from bianchi import algebra as alg
    n, a = alg.CANONICAL[type_name]
    if float(jnp.linalg.norm(jnp.asarray(a))) > 1e-14:
        raise ValueError(f"{type_name} 은 class B — class_a 차트로 못 다룬다")
    return StateA.of(Sp, Sm, *(scale * jnp.asarray(n)))
