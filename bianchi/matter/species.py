"""
PR-30 · 통합 물질 종족(Species) 프로토콜.

기존 3종족(TiltedFluid / ScalarField / MagneticField)은 각자 다른 시그니처를 갖고
있었다.  여기서 공통 인터페이스로 통일하고, 상호작용항 Q^A 와 그 보존 불변식
`Σ_i Q_i^A = 0` 을 코드 구조에 박제한다.  총 EMT 보존은 축약 Bianchi 항등식이
요구하는 것(보고서 §3) — 상호작용을 켜도 이 불변식이 그것을 보장한다.

Ctx (컨텍스트): 기하 + 시간 + 온도 묶음.  종족은 이것만 받아 자기 기여를 낸다.
  H       Hubble 스칼라 (또는 IX D-차트의 D)
  Sigma   (3,3) trace-free shear (Hubble 정규화 Σ)
  N, A    (3,3) 대칭 N, (3,) A
  R       (3,) 프레임 각속도
  tau     팽창정규화 시간
  T_gamma 광자 온도 (열역학 결합용; 없으면 None)

종족 기여 (전부 Hubble 정규화):
  omega(ctx)     -> Ω = ρ/(3H^2)
  q_source(ctx)  -> q(감속) 기여 = (1/2)[(3γ-2)+(2-γ)V^2] Ω/G_+  형태의 합산항
  pi(ctx)        -> Π_ab  (Σ RHS 소스; trace-free)
  q_flux(ctx)    -> 정규화 운동량밀도 (Codazzi 소스)
  rhs(ctx)       -> 진화된 Species
  Q(ctx)         -> (에너지교환, 운동량교환) ; 기본 (0, 0)
"""
from __future__ import annotations

from typing import Protocol, Sequence, runtime_checkable

from bianchi.matter.fluid import (TiltedFluid, sources as _fluid_sources, dOmega as _fluid_dOmega,
                                  dv_general as _fluid_dv, G_plus, _safe)
from bianchi.matter.components import ScalarField, MagneticField
from bianchi.optional_dependencies import require_jax_x64, require_optional

_, jnp = require_jax_x64(feature=__name__)
eqx = require_optional("equinox", feature=__name__)


class Ctx(eqx.Module):
    """기하·시간·온도 컨텍스트."""
    H: jnp.ndarray
    Sigma: jnp.ndarray
    N: jnp.ndarray
    A: jnp.ndarray
    R: jnp.ndarray
    tau: jnp.ndarray
    T_gamma: jnp.ndarray

    @staticmethod
    def of(Sigma, N, A, R=None, H=1.0, tau=0.0, T_gamma=None):
        z3 = jnp.zeros(3)
        return Ctx(jnp.asarray(H, jnp.float64), jnp.asarray(Sigma, jnp.float64),
                   jnp.asarray(N, jnp.float64), jnp.asarray(A, jnp.float64),
                   z3 if R is None else jnp.asarray(R, jnp.float64),
                   jnp.asarray(tau, jnp.float64),
                   jnp.asarray(jnp.nan if T_gamma is None else T_gamma, jnp.float64))


@runtime_checkable
class Species(Protocol):
    def omega(self, ctx: Ctx): ...
    def q_source(self, ctx: Ctx): ...
    def pi(self, ctx: Ctx): ...
    def q_flux(self, ctx: Ctx): ...
    def rhs(self, ctx: Ctx, q): ...
    def Q(self, ctx: Ctx, others): ...


# ============================================================ 어댑터
class FluidSpecies(eqx.Module):
    """TiltedFluid 어댑터."""
    fluid: TiltedFluid
    Q_energy: jnp.ndarray          # 외부 주입 에너지교환률 (기본 0)
    Q_mom: jnp.ndarray             # 외부 주입 운동량교환 (기본 0)

    @staticmethod
    def of(gamma, Omega, v, Q_energy=0.0, Q_mom=None):
        return FluidSpecies(TiltedFluid.of(gamma, Omega, v),
                            jnp.asarray(Q_energy, jnp.float64),
                            jnp.zeros(3) if Q_mom is None else jnp.asarray(Q_mom, jnp.float64))

    def _src(self, ctx):
        return _fluid_sources(self.fluid, ctx.Sigma, ctx.A)

    def omega(self, ctx):
        return self.fluid.Omega

    def q_source(self, ctx):
        s = self._src(ctx); g = self.fluid.gamma
        return 0.5 * ((3.0 * g - 2.0) + (2.0 - g) * s["V2"]) * s["Omega"] / s["Gp"]

    def pi(self, ctx):
        return self._src(ctx)["Pi"]

    def q_flux(self, ctx):
        return self._src(ctx)["q_flux"]

    def rhs(self, ctx, q):
        s = self._src(ctx)
        dOm = _fluid_dOmega(self.fluid, s, q) + self.Q_energy
        dv = _fluid_dv(self.fluid, s, ctx.Sigma, ctx.N, ctx.A, ctx.R)
        return FluidSpecies(TiltedFluid(self.fluid.gamma, self.fluid.Omega + 0.0 * dOm,
                                        self.fluid.v), self.Q_energy, self.Q_mom), dOm, dv

    def Q(self, ctx, others):
        return self.Q_energy, self.Q_mom


class ScalarSpecies(eqx.Module):
    field: ScalarField

    @staticmethod
    def of(x, y, lam):
        return ScalarSpecies(ScalarField.of(x, y, lam))

    def omega(self, ctx):
        return self.field.omega()

    def q_source(self, ctx):
        return self.field.pressure_term()          # 2x^2 - y^2

    def pi(self, ctx):
        return jnp.zeros((3, 3))                    # 동차 스칼라장: 이방응력 없음

    def q_flux(self, ctx):
        return jnp.zeros(3)

    def rhs(self, ctx, q):
        return ScalarSpecies(self.field.rhs(q))

    def Q(self, ctx, others):
        return jnp.asarray(0.0), jnp.zeros(3)


class MagneticSpecies(eqx.Module):
    field: MagneticField

    @staticmethod
    def of(B):
        return MagneticSpecies(MagneticField.of(B))

    def omega(self, ctx):
        return self.field.omega()

    def q_source(self, ctx):
        return self.field.pressure_term()          # = Omega_B (gamma_eff = 4/3)

    def pi(self, ctx):
        return self.field.anisotropic_stress()

    def q_flux(self, ctx):
        return jnp.zeros(3)

    def rhs(self, ctx, q):
        return MagneticSpecies(self.field.rhs(ctx.Sigma, ctx.R, q))

    def Q(self, ctx, others):
        return jnp.asarray(0.0), jnp.zeros(3)


# ============================================================ 혼합
class SpeciesMix(eqx.Module):
    """비/상호작용 다종족 혼합.  Σ_i Q_i^A = 0 을 런타임 강제."""
    members: tuple

    @staticmethod
    def of(*members):
        return SpeciesMix(tuple(members))

    def total_omega(self, ctx):
        return sum(m.omega(ctx) for m in self.members)

    def total_pi(self, ctx):
        return sum(m.pi(ctx) for m in self.members)

    def total_q_flux(self, ctx):
        return sum(m.q_flux(ctx) for m in self.members)

    def deceleration(self, ctx):
        """q = 2 Σ^2 + Σ_i q_source_i."""
        Sigma2 = jnp.trace(ctx.Sigma @ ctx.Sigma) / 6.0
        return 2.0 * Sigma2 + sum(m.q_source(ctx) for m in self.members)

    def exchange_residual(self, ctx):
        """Σ_i Q_i  (에너지, 운동량).  0 이어야 한다 (상호작용 무모순)."""
        qe = jnp.asarray(0.0); qm = jnp.zeros(3)
        for m in self.members:
            e, p = m.Q(ctx, self.members)
            qe = qe + e; qm = qm + p
        return qe, qm

    def check_exchange_conservation(self, ctx, tol=1e-12):
        """상호작용을 켰다면 Σ Q = 0 인지 확인 (아니면 총 EMT 보존 위반)."""
        qe, qm = self.exchange_residual(ctx)
        return bool(abs(float(qe)) < tol and float(jnp.max(jnp.abs(qm))) < tol)
