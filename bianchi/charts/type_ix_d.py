"""
PR-21 · Bianchi IX: D-정규화 차트 (Heinzle-Uggla). **기본 적분 차트**.

    D = sqrt( H^2 + (1/6)(n1n2 + n1n3 + n2n3) )
    3 D^2 = (1/2) sigma_ab sigma^ab + rho + (1/4) sum n_i^2    <- 우변 전부 비음수
  => D > 0 이 항상 보장. 계수 1/6 은 이를 성립시키는 **유일한** 값 (유도 확인).

    (Sigma_a, N_a, H, Omega) 를 D 로 정규화, dtau_-/dt = -D:
      H'  = q(1 - H^2) - F H
      S_a'= S_a[(2-q)H - F] + ^3S_a
      N_a'= -N_a[q H + 2 S_a + F]
      F   = (1/6)(N1 N2 S3 + N1 S2 N3 + S1 N2 N3)
      ^3S_a = (1/3)[N_a(2N_a - N_b - N_c) - (N_b - N_c)^2]
      q   = 2 Sigma^2 + (1/2)(3 gamma - 2) Omega,  Sigma^2 = (1/6) sum S_a^2

    구속:  Gauss  Sigma^2 + (1/12) sum N_a^2 + Omega = 1
           정의식 G = H^2 + (1/6)(N1N2+N1N3+N2N3) - 1 = 0
           ★ G' = -2(q H + F) G 는 **trace-free (sum S_a = 0) 를 부과했을 때만**
             성립한다. trace 구속도 감시 목록에 넣을 것.

★ 재붕괴는 H-차트로 잡을 수 없다: 상태변수가 ln H 이고 (ln H)' = -(1+q) 는 유계라
  H = exp(ln H) > 0 이 모든 유한 tau 에서 성립 -> **근이 존재하지 않는다**.
  D-차트에서 H_bar 의 영교차를 이벤트로 잡는 것이 유일하게 올바른 설계.

LIMITATIONS
  - class A 전용 (a = 0). class B 는 H-정규화 차트를 쓴다.
  - tilt 미지원 (비틸트 gamma-law).
"""
from __future__ import annotations

from bianchi.optional_dependencies import require_jax_x64, require_optional

jax, jnp = require_jax_x64(feature=__name__)
eqx = require_optional("equinox", feature=__name__)

name = "type_ix_D"
LIMITATIONS = __doc__.split("LIMITATIONS")[1].strip()


class StateD(eqx.Module):
    H: jnp.ndarray                # H_bar
    S: jnp.ndarray                # (3,) Sigma_bar_a,  sum = 0
    N: jnp.ndarray                # (3,) N_bar_a

    @staticmethod
    def of(H, S, N):
        S = jnp.asarray(S, jnp.float64)
        S = S - jnp.mean(S)       # trace-free 강제
        return StateD(jnp.asarray(H, jnp.float64), S, jnp.asarray(N, jnp.float64))

    def as_array(self):
        return jnp.concatenate([jnp.atleast_1d(self.H), self.S, self.N])

    @staticmethod
    def from_array(v):
        return StateD(v[0], v[1:4], v[4:7])


def _S3(N):
    N1, N2, N3 = N[0], N[1], N[2]
    return jnp.array([
        (N1*(2*N1 - N2 - N3) - (N2 - N3)**2) / 3.0,
        (N2*(2*N2 - N3 - N1) - (N3 - N1)**2) / 3.0,
        (N3*(2*N3 - N1 - N2) - (N1 - N2)**2) / 3.0,
    ])


def aux(y: StateD, gamma):
    Sigma2 = jnp.sum(y.S**2) / 6.0
    Omega = 1.0 - Sigma2 - jnp.sum(y.N**2) / 12.0        # Gauss
    q = 2.0*Sigma2 + 0.5*(3.0*gamma - 2.0)*Omega
    N1, N2, N3 = y.N[0], y.N[1], y.N[2]
    S1, S2, S3s = y.S[0], y.S[1], y.S[2]
    F = (N1*N2*S3s + N1*S2*N3 + S1*N2*N3) / 6.0
    return dict(Sigma2=Sigma2, Omega=Omega, q=q, F=F)


def rhs(tau, y: StateD, args) -> StateD:
    a = aux(y, args["gamma"])
    q, F, H = a["q"], a["F"], y.H
    dS = y.S * ((2.0 - q)*H - F) + _S3(y.N)
    dS = dS - jnp.mean(dS)                     # trace-free 유지
    return StateD(
        H=q*(1.0 - H**2) - F*H,
        S=dS,
        N=-y.N * (q*H + 2.0*y.S + F),
    )


def rhs_future(tau, y: StateD, args) -> StateD:
    """미래 방향 진화.

    ★ Heinzle-Uggla 의 ' 는 dtau_-/dt = -D 기준이라 **과거 지향**이다.
      우주시간이 증가하는 방향(재붕괴 추적)은 부호를 뒤집어야 한다.
    """
    d = rhs(tau, y, args)
    return StateD(H=-d.H, S=-d.S, N=-d.N)


def constraints(y: StateD, args):
    a = aux(y, args["gamma"])
    N1, N2, N3 = y.N[0], y.N[1], y.N[2]
    # ★ v1.3: 'gauss' 항목 제거 — Omega 가 Gauss 로 정의되므로 그 잔차는
    #   항등적으로 0 이라 감시 가치가 없다 (살아있는 잔차는 definition, trace).
    return dict(
        definition=y.H**2 + (N1*N2 + N1*N3 + N2*N3)/6.0 - 1.0,
        trace=jnp.sum(y.S),                    # ★ 반드시 감시
        Omega_negative=jnp.maximum(0.0, -a["Omega"]),
    )


def definition_propagation_residual(y: StateD, args):
    """G' = -2(q H + F) G  — trace-free 부과 시에만 성립."""
    G = lambda v: constraints(StateD.from_array(v), args)["definition"]
    v = y.as_array()
    dG = jnp.dot(jax.grad(G)(v), rhs(0.0, y, args).as_array())
    a = aux(y, args["gamma"])
    return dG + 2.0*(a["q"]*y.H + a["F"]) * constraints(y, args)["definition"]


def isotropic_closed_ic(H_bar):
    """정의식 구속을 만족하는 등방 닫힌 IX 초기조건.
       H^2 + (1/6)*3*n^2 = 1  =>  n = sqrt(2(1-H^2))."""
    n = jnp.sqrt(2.0 * (1.0 - jnp.asarray(H_bar) ** 2))
    return StateD.of(H_bar, jnp.zeros(3), jnp.array([n, n, n]))


def recollapse_event(eps=0.0):
    """H_bar 의 하향 영교차 = 최대팽창(재붕괴 시작). rhs_future 와 함께 쓸 것."""
    from bianchi import integrate as itg
    def cond(t, y, args, **kw):
        return y.H - eps
    return itg.float_event(cond, direction=False)


def from_H_chart(yA, gamma):
    """class_a StateA (H-정규화) -> StateD.  H > 0 구간에서만 유효."""
    N = jnp.stack([yA.N1, yA.N2, yA.N3])
    from bianchi.conventions import SQRT3
    S = jnp.stack([-2*yA.Sigma_p,
                   yA.Sigma_p + SQRT3*yA.Sigma_m,
                   yA.Sigma_p - SQRT3*yA.Sigma_m])
    # D/H = sqrt(1 + (1/6) sum_{i<j} N_i N_j)   (H-정규화 N 기준)
    N1, N2, N3 = N[0], N[1], N[2]
    ratio = jnp.sqrt(1.0 + (N1*N2 + N1*N3 + N2*N3)/6.0)
    return StateD.of(1.0/ratio, S/ratio, N/ratio)


def D_positive_identity(y: StateD, gamma):
    """3 D^2 = (1/2)sigma^2 + rho + (1/4) sum n^2 의 정규화판:
       H^2 + (1/6) sum_{i<j} N_i N_j = 1 (정의식) 와 동치."""
    return constraints(y, {"gamma": gamma})["definition"]
