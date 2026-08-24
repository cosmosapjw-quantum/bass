"""
PR-18/19/20 · 물질 컴포넌트 (다중 유체 · 스칼라장 · 자기장).

각 컴포넌트는 공통 인터페이스를 제공한다:
    omega(state)            -> Omega 기여
    pressure_term(state)    -> q 기여
    anisotropic_stress(...) -> Pi_ab  (Sigma_ab RHS 소스)
    momentum_flux(...)      -> q_a    (Codazzi 소스)
    rhs(...)                -> 자체 진화

★ anisotropic_stress 가 0 이 아닌 순간 대각 shear 가정이 무너진다. 이 인터페이스가
  그 사실을 코드 구조에 명시한다.
"""
from __future__ import annotations

from typing import Sequence

import equinox as eqx
import jax
import jax.numpy as jnp

from bianchi.matter.fluid import (TiltedFluid, G_plus, G_minus, _safe, sources,
                                  dOmega, dV2, T_coefficient)


# ================================================================ PR-18 다중 유체
class MultiFluid(eqx.Module):
    """비상호작용 다중 tilted 유체. 성분별 독립 보존 (교환항 Q^A = 0 가정)."""
    comps: tuple

    @staticmethod
    def of(*fluids: TiltedFluid):
        return MultiFluid(tuple(fluids))

    def total_sources(self, Sigma, A):
        ss = [sources(f, Sigma, A) for f in self.comps]
        Pi = sum(s["Pi"] for s in ss)
        qf = sum(s["q_flux"] for s in ss)
        Om = sum(s["Omega"] for s in ss)
        return dict(Pi=Pi, q_flux=qf, Omega=Om, per=ss)

    def deceleration(self, Sigma2, Sigma, A):
        tot = 2.0 * Sigma2
        for f, s in zip(self.comps, self.total_sources(Sigma, A)["per"]):
            g = f.gamma
            tot = tot + 0.5*((3*g - 2) + (2 - g)*s["V2"]) * s["Omega"] / s["Gp"]
        return tot

    def rhs(self, Sigma, A, q):
        """성분별 (Omega', v') 반환."""
        out = []
        for f in self.comps:
            s = sources(f, Sigma, A)
            out.append(dict(dOmega=dOmega(f, s, q), dV2=dV2(f, s),
                            T=T_coefficient(f, s)))
        return out

    def total_omega_rate(self, Sigma, A, q):
        """sum_i dOmega_i (부기용 합계). ★ v1.3: 이 값은 보존 '잔차'가 아니다 —
        총 EMT 보존은 성분별 방정식의 구조적 귀결이라 여기서 검출할 것이 없다.
        이전 이름 total_emt_conserved 는 검사 함수로 오독되어 폐기."""
        return sum(float(r["dOmega"]) for r in self.rhs(Sigma, A, q))

    # 하위호환 별칭 (deprecated)
    total_emt_conserved = total_omega_rate


def anisotropic_stress_is_nonzero(mf: MultiFluid, Sigma, A, tol=1e-14):
    """상대운동하는 다중 유체는 진짜 이방성 응력을 만든다 (대각 shear 불가)."""
    Pi = mf.total_sources(Sigma, A)["Pi"]
    off = Pi - jnp.diag(jnp.diag(Pi))
    return float(jnp.max(jnp.abs(off))) > tol


# ================================================================ PR-19 스칼라장
class ScalarField(eqx.Module):
    """동차 스칼라장. 지수 퍼텐셜 V = V_0 exp(-lambda phi).

    정규화: x = phidot/(sqrt6 H),  y = sqrt(V)/(sqrt3 H)
      Omega_phi = x^2 + y^2 ,  gamma_phi = 2x^2/(x^2+y^2)
      x' = (q-2) x + sqrt(3/2) lambda y^2
      y' = (q+1) y - sqrt(3/2) lambda x y
    ★ 동차 스칼라장은 shear 와 결합하지 않는다 (pi_ab = 0) — KG 는 -3H phidot - V'.
    """
    x: jnp.ndarray
    y: jnp.ndarray
    lam: jnp.ndarray

    @staticmethod
    def of(x, y, lam):
        f = lambda v: jnp.asarray(v, jnp.float64)
        return ScalarField(f(x), f(y), f(lam))

    def omega(self):
        return self.x**2 + self.y**2

    def gamma_eff(self):
        Om = self.omega()
        return 2.0 * self.x**2 / jnp.where(Om > 0, Om, 1.0)

    def pressure_term(self):
        """q 기여: (1/2)(3 gamma_phi - 2) Omega_phi = 2x^2 - y^2."""
        return 2.0 * self.x**2 - self.y**2

    def anisotropic_stress(self):
        return jnp.zeros((3, 3))      # 동차 스칼라장은 이방성 응력 없음

    def momentum_flux(self):
        return jnp.zeros(3)

    def rhs(self, q):
        s32 = jnp.sqrt(1.5)
        return ScalarField(
            x=(q - 2.0) * self.x + s32 * self.lam * self.y**2,
            y=(q + 1.0) * self.y - s32 * self.lam * self.x * self.y,
            lam=jnp.zeros_like(self.lam),
        )

    def conservation_residual(self, q):
        """Omega_phi' = [2q - (3 gamma_phi - 2)] Omega_phi."""
        d = self.rhs(q)
        dOm = 2.0 * (self.x * d.x + self.y * d.y)
        Om = self.omega()
        return dOm - (2.0 * q - (3.0 * self.gamma_eff() - 2.0)) * Om


# ================================================================ PR-20 자기장
class MagneticField(eqx.Module):
    """동차 source-free 자기장 (E_a = 0).

    유도 결과 (gen_frame_einstein.py):
      rho_B = B^2/2 ,  p_B = B^2/6  (gamma_eff = 4/3)
      pi_ab = -B_a B_b + (1/3) B^2 delta_ab
      Faraday:  Bdot_a = -2H B_a + sigma_ab B^b + eps_abc R^b B^c
                (회전항 부호: 마스터 규칙 Y_a' ⊃ +(R x Y)_a — v1.1 정정)
      정규화 :  B(코드) = B_a / H  (Hubble 정규화),  Omega_B = B.B/6
      대수 제약 1 (dF=0 공간):     a_b B^b = 0
      대수 제약 2 (nabla F = 0):   n_ab B^b + eps_abc a^b B^c = 0
                                   (★ v1.2 부호 정정 — audit/d_matter.py)

    ★ 제약이 유형/방향을 제한한다: 예컨대 유형 V (n=0, a!=0) 에서는 B=0 만 가능.
    """
    B: jnp.ndarray      # (3,) Hubble 정규화

    @staticmethod
    def of(B):
        return MagneticField(jnp.asarray(B, jnp.float64))

    def omega(self):
        return (self.B @ self.B) / 6.0        # Omega_B = B^2/(6 H^2) (정규화)

    def pressure_term(self):
        return self.omega()                   # (1/2)(3*4/3-2)Omega = Omega

    def anisotropic_stress(self):
        B2 = self.B @ self.B
        return -(jnp.outer(self.B, self.B) - B2 * jnp.eye(3) / 3.0)

    def momentum_flux(self):
        return jnp.zeros(3)

    def constraints(self, N, A):
        from bianchi.conventions import EPS3_J
        return dict(
            div_free=A @ self.B,
            # ★ v1.2 (audit/d_matter.py): E, B 를 동시에 넣고 nabla_a F^{ab}=0 을
            #   풀면 curl 결합은 n_ab X^b + eps_abc a^b X^c 이다 (상대부호 +).
            #   v1.0/v1.1 은 -eps 로 적혀 있었다. 차이는 n!=0 이고 a!=0 인
            #   class B (III, IV, VI_h, VII_h) 에서만 드러난다.
            ampere=N @ self.B + jnp.einsum("abc,b,c->a", EPS3_J, A, self.B),
        )

    def rhs(self, Sigma, R, q):
        """B_a' = (q - 1) B_a + Sigma_ab B^b + (R x B)_a   (B = B_a/H).

        ★ v1.1 (외부검토 R1): 회전항 부호가 -(R x B) 로 되어 있었다.  a_a, v_a
          와 동일한 공간 벡터이므로 반드시 +(R x B) 여야 한다.
        """
        from bianchi.conventions import rotation_apply_vector
        rot = rotation_apply_vector(R, self.B)
        return MagneticField((q - 1.0) * self.B + Sigma @ self.B + rot)

    def allowed_types(self):
        """제약을 만족하는 유형/방향 안내."""
        return {
            "I":  "임의 B (n=0, a=0)",
            "II": "B in ker(n) (예: n=diag(1,0,0) -> B_1 = 0)",
            "V":  "B = 0 (n=0, a!=0 이면 a.B=0 & a x B=0 -> B=0)",
            "VII_0": "n B = 0 이어야 -> 일반적으로 B = 0",
        }
