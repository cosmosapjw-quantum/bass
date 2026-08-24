"""차트 공통 인터페이스.

각 차트는 (a) 상태 pytree, (b) RHS, (c) 구속 잔차, (d) **이 차트로 무엇을 못
하는가** 를 docstring 과 `LIMITATIONS` 에 명시한다 (PR 원칙 4).
"""
from __future__ import annotations

from typing import Protocol

import equinox as eqx
import jax.numpy as jnp


class Chart(Protocol):
    name: str
    LIMITATIONS: str

    def rhs(self, tau, y, args): ...
    def constraints(self, y, args): ...
    def aux(self, y, args): ...


class FluidParams(eqx.Module):
    """비틸트 gamma-law 유체 파라미터."""
    gamma: jnp.ndarray = eqx.field(converter=jnp.asarray)

    @staticmethod
    def of(gamma):
        return FluidParams(jnp.asarray(gamma, dtype=jnp.float64))


def deceleration(Sigma2, Omega, gamma):
    """q = 2 Sigma^2 + (1/2)(3 gamma - 2) Omega  (비틸트)."""
    return 2.0 * Sigma2 + 0.5 * (3.0 * gamma - 2.0) * Omega
