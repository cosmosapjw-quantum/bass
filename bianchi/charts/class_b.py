"""
PR-07 · Class B 비틸트 차트 (HW93 축소, kappa 파라미터화).

상태: (Sigma_+, Sigmatilde, Delta, Atilde, N_+),  파라미터 kappa = 1/h.

유도로 확정된 계수 (derive_u2_final.py; 오라클로는 못 잡는다):
    (b3, c2, c) = (-4, 2, 6)
  * c2 = 2, c = 6 은 **항등적으로** 결정
  * b3 = -4 는 **Codazzi 구속면 위에서만** -4 다. off-shell 유도형은
        Sigmatilde' = 2(q-2)St - 4 Delta N_+ - 4A(N_- Sx - Nx Sm)
    이며, HW93 은 C = 0 (즉 N_-Sx - NxSm = A Sigma_+) 을 써서
    마지막 항을 -4 Sigma_+ Atilde 로 바꿔 적었다.

  K = Ntilde + Atilde,   Ntilde = (1/3)(N_+^2 - kappa Atilde)
  Codazzi: C = St*Nt - Delta^2 - Sigma_+^2 * Atilde = 0,  C' = 4(q+Sigma_+-1)C

kappa 커버리지: 0 -> {IV (N_+!=0), V (N_+=0)}, -1 -> III, <0 -> VI_h,
                >0 -> VII_h, -9 -> 예외형(이 차트는 축퇴! charts.exceptional 로)

LIMITATIONS
  - kappa = -9 에서 Codazzi rank 가 떨어져 이 차트는 축퇴한다 (런타임 가드 있음).
  - tilt 없음. class A (Atilde=0) 도 다룰 수 없다 (kappa*Atilde 관계가 무너짐).
  - Sigmatilde, Ntilde >= 0 은 정의역 조건 — 위반 시 구속 표류 신호.
"""
from __future__ import annotations

import equinox as eqx
import jax.numpy as jnp

from bianchi.charts.base import deceleration

name = "class_b"
LIMITATIONS = __doc__.split("LIMITATIONS")[1].strip()

KAPPA_EXCEPTIONAL = -9.0
STATE_NAMES = ("Sigma_p", "Sigma_tilde", "Delta", "A_tilde", "N_p")


class StateB(eqx.Module):
    Sigma_p: jnp.ndarray
    Sigma_tilde: jnp.ndarray
    Delta: jnp.ndarray
    A_tilde: jnp.ndarray
    N_p: jnp.ndarray

    @staticmethod
    def of(Sp, St, De, At, Np):
        f = lambda x: jnp.asarray(x, dtype=jnp.float64)
        return StateB(f(Sp), f(St), f(De), f(At), f(Np))

    def as_array(self):
        return jnp.stack([self.Sigma_p, self.Sigma_tilde, self.Delta,
                          self.A_tilde, self.N_p])

    @staticmethod
    def from_array(v):
        return StateB(v[0], v[1], v[2], v[3], v[4])


def N_tilde(N_p, A_tilde, kappa):
    """Ntilde = (1/3)(N_+^2 - kappa Atilde). 군 관계식 n2n3 = kappa A^2 의 직접 결과."""
    return (N_p**2 - kappa * A_tilde) / 3.0


def aux(y: StateB, gamma, kappa):
    Nt = N_tilde(y.N_p, y.A_tilde, kappa)
    Sigma2 = y.Sigma_p**2 + y.Sigma_tilde
    K = Nt + y.A_tilde
    Omega = 1.0 - Sigma2 - K
    q = deceleration(Sigma2, Omega, gamma)
    return dict(N_tilde=Nt, Sigma2=Sigma2, K=K, Omega=Omega, q=q)


def rhs(tau, y: StateB, args) -> StateB:
    gamma, kappa = args["gamma"], args["kappa"]
    a = aux(y, gamma, kappa)
    q, Nt = a["q"], a["N_tilde"]
    Sp, St, De, At, Np = (y.Sigma_p, y.Sigma_tilde, y.Delta, y.A_tilde, y.N_p)
    return StateB(
        Sigma_p=(q - 2.0) * Sp - 2.0 * Nt,
        Sigma_tilde=2.0 * (q - 2.0) * St - 4.0 * Sp * At - 4.0 * De * Np,   # b3 = -4 (on-shell)
        Delta=2.0 * (q + Sp - 1.0) * De + 2.0 * (St - Nt) * Np,             # c2 = 2 (항등적)
        A_tilde=2.0 * (q + 2.0 * Sp) * At,
        N_p=(q + 2.0 * Sp) * Np + 6.0 * De,                                 # c = 6 (항등적)
    )


def codazzi(y: StateB, kappa):
    """C = Sigmatilde*Ntilde - Delta^2 - Sigma_+^2 * Atilde.C = Sigmatilde*Ntilde - Delta^2 - Sigma_+^2 * Atilde.

    ★ v1.3 (감사 결함 #4): 이 잔차는 2차식 C = S~N~ - Delta^2 - Sigma_+^2 A~ 로,
      Lagrange 항등식에 의해 **두 Codazzi 시트 (N_-Sigma_x - N_xSigma_- = ±A Sigma_+)
      를 구분하지 못한다.** 축소 변수 (Sigma_+, S~, Delta, A~, N_+) 는 시트 부호를
      아예 담지 않으므로 이 차트 안에서는 부호 잔차가 원리적으로 불가능하다.
      시트 선택은 (Sigma_-, Sigma_x, N_-, N_x) 로 **리프트하는 시점**의 규약이다
      — 보고서 Branch caveat 의 "코드가 부호 잔차를 반환한다" 는 서술은 v1.3 에서
      정정되었다 (문서가 코드를 과대포장했던 사례).
    """
    Nt = N_tilde(y.N_p, y.A_tilde, kappa)
    return y.Sigma_tilde * Nt - y.Delta**2 - y.Sigma_p**2 * y.A_tilde


def constraints(y: StateB, args):
    kappa = args["kappa"]
    a = aux(y, args["gamma"], kappa)
    return dict(
        codazzi=codazzi(y, kappa),
        domain_St=jnp.maximum(0.0, -y.Sigma_tilde),
        domain_Nt=jnp.maximum(0.0, -a["N_tilde"]),
        domain_At=jnp.maximum(0.0, -y.A_tilde),
        Omega_negative=jnp.maximum(0.0, -a["Omega"]),
    )


def codazzi_propagation_residual(y: StateB, args):
    """C' = 4(q + Sigma_+ - 1) C 의 잔차 (런타임 오라클 F)."""
    import jax
    gamma, kappa = args["gamma"], args["kappa"]
    f = lambda v: codazzi(StateB.from_array(v), kappa)
    v = y.as_array()
    dC = jnp.dot(jax.grad(f)(v), rhs(0.0, y, args).as_array())
    a = aux(y, gamma, kappa)
    return dC - 4.0 * (a["q"] + y.Sigma_p - 1.0) * codazzi(y, kappa)


def kappa_conserved_check(kappa_series):
    """kappa 는 파라미터이므로 진화하지 않는다 — 정의상 보존.
    Layer 0 진단은 algebra.type_drift 를 쓸 것."""
    k = jnp.asarray(kappa_series)
    return float(jnp.max(jnp.abs(k / k[0] - 1.0)))


def guard_exceptional(kappa, tol=1e-8):
    """kappa = -9 에서 이 차트는 축퇴한다."""
    if abs(float(kappa) - KAPPA_EXCEPTIONAL) < tol:
        raise ValueError(
            f"kappa = {kappa} 는 예외형 VI*_-1/9 — class_b 차트는 여기서 축퇴한다. "
            "charts.exceptional 을 사용할 것."
        )


# ---------------------------------------------------------------- 초기조건
def solve_type_V():
    """유형 V: N_+ = 0 => Ntilde = 0, Codazzi 가 Delta = Sigma_+ = 0 을 강제.
       남는 것은 (Sigmatilde, Atilde) 2차원 (설계 §1.2, U14)."""
    return "state: Sigma_p = Delta = N_p = 0; free (Sigma_tilde, A_tilde)"


def type_V_state(St, At):
    return StateB.of(0.0, St, 0.0, At, 0.0)


def on_codazzi_surface(Sp, St, At, Np, kappa):
    """Codazzi C=0 을 Delta 에 대해 풀어 구속면 위 상태를 만든다."""
    Nt = N_tilde(Np, At, kappa)
    d2 = St * Nt - Sp**2 * At
    De = jnp.sqrt(jnp.maximum(d2, 0.0))
    return StateB.of(Sp, St, De, At, Np), d2
