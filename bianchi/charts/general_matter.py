"""
D2c · **물질을 차트의 상태변수로 승격** — 구속계가 비로소 닫힌 채로 굴러간다.

`charts/general` 은 물질(Ω, q_flux, Π)을 **args 로 얼려** 받는다.  D2b 가 잰 대로 그
상태에서는 구속계가 닫히지 않는다 (잔차 ~1) — 그래서 `amplification_rate` 도,
`solve_with_projection` 도 닫히지 않은 계 위에서 돌고 있었다.

여기서 Ω 와 Q^a 를 **상태로 올린다**.  진화식은 D2b 가 닫힘을 요구해 **적합으로
결정**한 것이다 (인용 아님, 잔차 1e−15):

    Q̇^a = (2q − 2)Q^a − Σ^a{}_b Q^b + 3 Π^{ab}A_b + ε^{abc}N_{bd}Π^d{}_c
    Ω̇   = (2q − 2)Ω + (2/3) A_aQ^a − (1/3) Σ_abΠ^{ab}

기하는 `charts/general.rhs` 를 그대로 쓴다 — **한 줄도 다시 쓰지 않는다** (두 판이
갈라지면 어느 쪽이 맞는지 알 수 없게 된다).

★ Π 는 여전히 **입력**이다.  D2b 의 적합에서 Π 방향의 잔차까지 0 이 됐으므로,
  **어떤 Π 를 주든** Q, Ω 만 위 법칙으로 굴리면 구속계는 닫힌다.  Π 자체의 진화는
  계층(l=2 모멘트)의 몫이고 이 차트의 범위 밖이다 — 그 한계를 숨기지 않는다.
  (`dPi` 를 0 이 아니게 주면 닫힘이 깨지는지도 `audit` 에서 잰다.)

★ `trace` 구속은 여기서도 **감시하지 않는다**: 상태를 `tracefree_from_5` 로 짜므로
  tr Σ 는 위반될 수 없다 (D2b 측정: 기울기 노름 정확히 0).

LIMITATIONS
  - Π (비등방 응력) 는 처방 입력이다.  물리적 Π 는 운동론 계층이 준다.
  - 회전 R 은 args 로 남는다 (Fermi 게이지 기본).
  - Ω 를 상태로 올렸으므로 Gauss 는 더 이상 항등식이 아니다 — **감시 대상**이다.
"""
from __future__ import annotations

import equinox as eqx
import jax
import jax.numpy as jnp
import numpy as np

from bianchi.charts import general as G
from bianchi.constraint_rates import CLOSURE_COEFFS
from bianchi.conventions import EPS3_J, sym_from_6, tracefree_from_5

name = "general_matter"
LIMITATIONS = __doc__.split("LIMITATIONS")[1].strip()

#: 물질 법칙 계수 — D2b 가 닫힘 적합으로 결정한 값 (`constraint_rates.CLOSURE_COEFFS`).
C = CLOSURE_COEFFS


class StateGM(eqx.Module):
    """Σ (5) + N (6) + A (3) + Q (3) + Ω (1) = 18."""

    Sigma: jnp.ndarray
    N: jnp.ndarray
    A: jnp.ndarray
    Q: jnp.ndarray
    Omega: jnp.ndarray

    @staticmethod
    def of(Sigma, N, A, Q, Omega):
        f = lambda x: jnp.asarray(x, jnp.float64)
        return StateGM(f(Sigma), f(N), f(A), f(Q), f(Omega))

    @staticmethod
    def from_packed(v):
        return StateGM(tracefree_from_5(*v[:5]), sym_from_6(*v[5:11]),
                       v[11:14], v[14:17], v[17])

    def packed(self):
        S, N = self.Sigma, self.N
        return jnp.concatenate([
            jnp.array([S[0, 0], S[1, 1], S[0, 1], S[0, 2], S[1, 2]]),
            jnp.array([N[0, 0], N[1, 1], N[2, 2], N[0, 1], N[0, 2], N[1, 2]]),
            self.A, self.Q, jnp.atleast_1d(self.Omega),
        ])

    def geometry(self):
        """기하 부분만 잘라 `charts.general` 의 상태로."""
        return G.StateG(self.Sigma, self.N, self.A)


def _Pi(args):
    return jnp.asarray(args.get("Pi", jnp.zeros((3, 3))))


def general_args(y: StateGM, args):
    """★ `charts.general` 에 넘길 args — 물질을 **상태에서** 채운다.

    이게 D2c 의 전부다: 얼어 있던 Ω, q_flux 자리에 상태값을 꽂는다.
    """
    a = dict(args)
    a["Omega"] = y.Omega
    a["q_flux"] = y.Q
    a["Pi"] = _Pi(args)
    return a


def aux(y: StateGM, args):
    return G.aux(y.geometry(), general_args(y, args))


# ---------------------------------------------------------------- RHS
def matter_rhs(y: StateGM, args):
    """★★ D2b 가 **닫힘으로 결정한** 물질 진화식 (계수는 `CLOSURE_COEFFS`)."""
    Pi = _Pi(args)
    a = aux(y, args)
    q, S, N, A, Q, Om = a["q"], y.Sigma, y.N, y.A, y.Q, y.Omega
    dQ = (C[0] * Q + C[1] * (S @ Q) + C[2] * q * Q + C[3] * (Pi @ A)
          + C[4] * jnp.einsum("abc,bd,cd->a", EPS3_J, N, Pi)
          + C[5] * (N @ Q) + C[6] * jnp.einsum("abc,b,c->a", EPS3_J, A, Q))
    dOm = (C[7] * Om + C[8] * q * Om + C[9] * jnp.dot(A, Q)
           + C[10] * jnp.sum(S * Pi))
    return dQ, dOm


def rhs(tau, y: StateGM, args) -> StateGM:
    """기하는 `general.rhs` 그대로, 물질은 D2b 의 법칙."""
    g = G.rhs(tau, y.geometry(), general_args(y, args))
    dQ, dOm = matter_rhs(y, args)
    return StateGM(g.Sigma, g.N, g.A, dQ, dOm)


# ---------------------------------------------------------------- 구속
def constraint_residuals(y: StateGM, args):
    """Gauss / Codazzi / Jacobi.  ★ `trace` 는 구조상 위반 불가라 빼둔다 (D2b)."""
    c = G.constraint_residuals(y.geometry(), general_args(y, args))
    return dict(gauss=c["gauss"], codazzi=c["codazzi"], jacobi=c["jacobi"])


def constraint_vector(y: StateGM, args):
    c = constraint_residuals(y, args)
    return jnp.concatenate([jnp.atleast_1d(c["gauss"]), c["codazzi"], c["jacobi"]])


def constraints(y: StateGM, args):
    """`constraints.monitor` 규약용 (dict of 잔차)."""
    return constraint_residuals(y, args)


# ---------------------------------------------------------------- 초기자료
def on_constraint_surface(Sigma, N, A1, Q_extra=None, gamma=4.0 / 3.0):
    """★★ **구속을 정확히 만족하는** 초기자료를 만든다.

    Codazzi 는 Q 를 맞춰서, Gauss 는 Ω 를 맞춰서 0 으로 둔다.
    ★ Jacobi (N^{ab}A_b = 0) 는 호출자의 몫이다 — A 방향의 N 행·열을 0 으로 둘 것.
      (D2b 에서 이걸 어겨 계수 적합이 통째로 어긋난 적이 있다.)
    """
    Sigma = np.asarray(Sigma, float)
    N = np.asarray(N, float)
    Av = np.array([float(A1), 0.0, 0.0])
    S2 = float(np.trace(Sigma @ Sigma)) / 6.0
    K = float(G.curvature(jnp.asarray(N), jnp.asarray(Av))[0])
    Q = 3.0 * Av @ Sigma + np.einsum("abc,bd,cd->a", np.asarray(EPS3_J), N, Sigma)
    if Q_extra is not None:
        Q = Q + np.asarray(Q_extra, float)
    return StateGM.of(Sigma, N, Av, Q, 1.0 - S2 - K), {"gamma": float(gamma)}


def jacobi_safe_N(n22, n23, n33):
    """★ A = (A₁,0,0) 과 Jacobi 를 만족하는 N (1-행·열이 0)."""
    return np.array([[0.0, 0.0, 0.0], [0.0, n22, n23], [0.0, n23, n33]])


# ---------------------------------------------------------------- 진단
def closure_residual(y: StateGM, args):
    """★★ 이 상태에서 구속계가 닫혔는가 — D2b 의 검사를 **상태 위에서** 돌린다.

        ∂(J f)/∂w = M·J  를 최소제곱으로 풀고 잔차를 낸다 (0 이어야 닫힌 것).
    """
    Cf = lambda v: constraint_vector(StateGM.from_packed(v), args)
    ff = lambda v: rhs(0.0, StateGM.from_packed(v), args).packed()
    w = y.packed()
    J = np.asarray(jax.jacfwd(Cf)(w))
    Gv = np.asarray(jax.jacfwd(lambda v: jax.jacfwd(Cf)(v) @ ff(v))(w))
    M = np.linalg.lstsq(J.T, Gv.T, rcond=None)[0].T
    sc = max(float(np.abs(Gv).max()), 1e-300)
    return dict(M=M, residual=float(np.abs(M @ J - Gv).max() / sc),
                spectrum=np.linalg.eigvals(M))


def amplification_rate(y: StateGM, args):
    """★ 구속 증폭률 — M 의 스펙트럼 상한 (닫혀 있을 때만 의미가 있다)."""
    r = closure_residual(y, args)
    return dict(rate=float(np.max(r["spectrum"].real)), closure=r["residual"])
