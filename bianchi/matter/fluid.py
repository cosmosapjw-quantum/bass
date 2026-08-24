"""
PR-14/15 · Tilted gamma-law 완전유체.

전부 제1원리 유도로 확정된 형태 (derive_tilt.py / verify_hervik.py, 좌표계 검산 통과):

  u^A = Gamma(n^A + v^A),  Gamma^2 = 1/(1-V^2),  p = (gamma-1) rho
  G_pm = 1 pm (gamma-1) V^2

  1+3 분해:
    rho_n  = Gamma^2 rho G_+          ->  Omega = rho_n/(3H^2)
    q_a    = gamma rho Gamma^2 v_a    ->  정규화 3 gamma Omega v_a / G_+
    pi_ab  = gamma rho Gamma^2 (v_a v_b - V^2 d_ab/3)
                                      ->  Pi_ab = 3 gamma Omega (v_a v_b - V^2 d/3)/G_+

  q      = 2 Sigma^2 + (1/2)[(3g-2) + (2-g)V^2] Omega / G_+
  ★ Omega' = (Omega/G_+){2q - (3g-2) + 2g(A.v) + [2q(g-1)-(2-g)]V^2 - g S V^2}
     — 분모는 **G_+** 다 (G_- 아님). 8개 후보 중 정확히 하나.
  V'     = [V(1-V^2)/G_-][(3g-4) - 2(g-1)(A.v) - S]
  T      = {[(3g-4) - 2(g-1)(A.v)](1-V^2) + (2-g) S V^2}/G_-

  구조적 사실: **G_- 가 tilt 를, G_+ 가 에너지밀도를 지배한다.**

가드 2종 (설계 §2.6):
  * G_- -> 0  at (gamma, V) = (2, 1)   : stiff + extreme tilt 퇴화
  * G_+ -> 0  as (gamma, V) -> (0, 1)  : 경로의존 특이점 (v1.1 에서 제거가능\n    극한 주장 철회됨 — 보고서 Degeneracies 절). 가드만 하고 극한을 취하지 말 것.
"""
from __future__ import annotations

from bianchi.optional_dependencies import require_jax_x64, require_optional

jax, jnp = require_jax_x64(feature=__name__)
eqx = require_optional("equinox", feature=__name__)

GUARD_EPS = 1e-12


class TiltedFluid(eqx.Module):
    """단일 tilted gamma-law 유체 성분."""
    gamma: jnp.ndarray
    Omega: jnp.ndarray
    v: jnp.ndarray          # (3,) 프레임 성분

    @staticmethod
    def of(gamma, Omega, v):
        return TiltedFluid(jnp.asarray(gamma, jnp.float64),
                           jnp.asarray(Omega, jnp.float64),
                           jnp.asarray(v, jnp.float64))


def G_plus(gamma, V2):
    return 1.0 + (gamma - 1.0) * V2


def G_minus(gamma, V2):
    return 1.0 - (gamma - 1.0) * V2


def _safe(x):
    """0 나눗셈 가드. 부호를 보존하며 |x| >= GUARD_EPS 로 클리핑."""
    return jnp.where(jnp.abs(x) < GUARD_EPS,
                     jnp.where(x >= 0, GUARD_EPS, -GUARD_EPS), x)


def guard_report(gamma, V2):
    """퇴화 근접도. 1 에 가까울수록 위험."""
    Gm, Gp = G_minus(gamma, V2), G_plus(gamma, V2)
    return dict(
        G_minus=Gm, G_plus=Gp,
        stiff_extreme=jnp.abs(Gm) < 1e-6,      # (gamma,V)=(2,1)
        zero_gamma_extreme=jnp.abs(Gp) < 1e-6,  # (gamma,V)->(0,1)
    )


# ---------------------------------------------------------------- 소스
def sources(f: TiltedFluid, Sigma, A):
    """(Omega, Pi_ab, q_flux_a, S, V2, A.v) — 기하 RHS 에 주입할 소스."""
    v, g, Om = f.v, f.gamma, f.Omega
    V2 = v @ v
    Gp = _safe(G_plus(g, V2))
    SV2 = jnp.einsum("ab,a,b->", Sigma, v, v)          # = S * V^2
    Adv = A @ v
    Pi = 3.0 * g * Om / Gp * (jnp.outer(v, v) - V2 * jnp.eye(3) / 3.0)
    q_flux = 3.0 * g * Om * v / Gp
    return dict(Omega=Om, Pi=Pi, q_flux=q_flux, SV2=SV2, V2=V2, Adv=Adv, Gp=Gp)


def deceleration(Sigma2, comps):
    """q = 2 Sigma^2 + sum_i (1/2)[(3g-2)+(2-g)V^2] Omega/G_+  (다중 성분 합)."""
    tot = 2.0 * Sigma2
    for s, g in comps:
        tot = tot + 0.5 * ((3.0*g - 2.0) + (2.0 - g)*s["V2"]) * s["Omega"] / s["Gp"]
    return tot


# ---------------------------------------------------------------- 진화 (유도 확정)
def dOmega(f: TiltedFluid, s, q):
    """★ 분모 G_+ (U4 확정)."""
    g, Om = f.gamma, f.Omega
    return (Om / s["Gp"]) * (
        2.0*q - (3.0*g - 2.0)
        + 2.0*g*s["Adv"]
        + (2.0*q*(g - 1.0) - (2.0 - g)) * s["V2"]
        - g * s["SV2"]
    )


def T_coefficient(f: TiltedFluid, s):
    """v_a' 공통 스칼라 계수. 분모 G_-."""
    g = f.gamma
    Gm = _safe(G_minus(g, s["V2"]))
    return (((3.0*g - 4.0) - 2.0*(g - 1.0)*s["Adv"]) * (1.0 - s["V2"])
            + (2.0 - g) * s["SV2"]) / Gm


def dV2(f: TiltedFluid, s):
    """(V^2)' = 2 V^2 (1-V^2)/G_- [(3g-4) - 2(g-1)(A.v) - S].

    V=0 과 V=1 이 둘 다 불변 경계임을 구조적으로 보장한다.
    """
    g = f.gamma
    Gm = _safe(G_minus(g, s["V2"]))
    V2 = s["V2"]
    S_times_V2 = s["SV2"]
    return 2.0 * (1.0 - V2) / Gm * (
        V2 * ((3.0*g - 4.0) - 2.0*(g - 1.0)*s["Adv"]) - S_times_V2
    )


def dv_general(f: TiltedFluid, s, Sigma, N, A, R):
    """일반 프레임에서의 완전한 v_a'  (v1.1: 외부검토 R2 로 전면 재유도).

        v_a' = T v_a - Sigma_a^b v_b + (R x v)_a - P_a ,
        P_a  = A_a V^2 - (A.v) v_a + eps_abc v^b (N v)^c ,
        T    = [ ((3g-4) - 2(g-1) A.v)(1 - V^2) + (2-g) S ] / G_- ,
        S    = Sigma_ab v^a v^b .

    P_a 는 3차원 접속의 이중 축약  ^3Gamma^a_{bc} v^b v^c  이며, 계수
    (+1, -1, +1) 은 수치 동정으로 확정했다 (audit/r5d_tilt_closed.py,
    잔차 3.1e-14).  전체 식은 4차원 nabla^a T_ab = 0 의 직접 풀이와
    3.2e-14 까지 일치한다.

    ★ v1.0 의 이 함수는 (i) shear 항이 +2 Sigma.v (정답 -Sigma.v),
      (ii) (A.v) v 부호 반대, (iii) -A V^2 항 누락 — 세 군데가 틀렸었다.
      Hervik 게이지 특수화(charts.class_b_tilted)는 영향받지 않는다
      (그쪽은 게이지 고정된 조합을 직접 코딩하며, v1.1 검증에서 정확히 재현됨).
    """
    from bianchi.conventions import EPS3_J, rotation_apply_vector
    T = T_coefficient(f, s)
    v = f.v
    V2 = v @ v
    Adv = A @ v
    P = A * V2 - Adv * v + jnp.einsum("abc,b,c->a", EPS3_J, v, N @ v)
    return T * v - (Sigma @ v) + rotation_apply_vector(R, v) - P


# ---------------------------------------------------------------- 극한/불변성
def is_invariant_boundary(V2, tol=1e-12):
    """V=0 (비틸트) 과 V=1 (extreme tilt) 이 불변 경계."""
    return bool(abs(float(V2)) < tol or abs(float(V2) - 1.0) < tol)


def q_at_extreme_tilt(Sigma2, Omega):
    """q|_{V=1} = 2 Sigma^2 + Omega   (gamma 무관 — null fluid, gamma_eff = 4/3)."""
    return 2.0 * Sigma2 + Omega


def dOmega_at_extreme_tilt(Omega, q, A_dot_c, S_cc):
    """Omega'|_{V=1} = Omega (2q - 2 + 2 A.c - Sigma_ab c^a c^b),  c = v/V.

    ★ Omega 는 V=1 면에서 0 이 되지 않는다 (Omega' ∝ Omega 이므로 Omega=0 만 불변).
    """
    return Omega * (2.0*q - 2.0 + 2.0*A_dot_c - S_cc)
