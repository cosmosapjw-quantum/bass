"""
D2b · **일반 차트의 구속 증폭 행렬** — `amplification_rate` 가 0.0 을 돌려주던 자리.

구속벡터 C(y) 와 흐름 f(y) 에 대해 Ċ = J f (J = ∂C/∂y) 다.  계가 **닫혔다**는 것은
M(y) 가 있어 Ċ = M·C 라는 뜻이고, 구속면 위(C = 0)에서 미분하면

      ∂(Jf)/∂y = M · J          ← 최소제곱으로 풀고, **잔차가 곧 닫힘 검사**다

M 의 스펙트럼이 증폭률이다.  유도·측정 과정과 대조군은 `audit/d2b_chart_amplification.py`.

★ 물질(Ω, Q, Π)을 얼린 채로는 닫히지 않는다 (잔차 ~1).  닫히게 하는 법칙을
  **적합으로 결정**했다 (Jacobi 를 만족하는 무작위 일반형 배위, 잔차 1e−15):

      Q̇^a = (2q − 2)Q^a − Σ^a{{_b}} Q^b + 3 Π^{{ab}}A_b + ε^{{abc}}N_{{bd}}Π^d{{_c}}
      Ω̇   = (2q − 2)Ω + (2/3) A_aQ^a − (1/3) Σ_abΠ^{{ab}}

★ type V 배위에서 Codazzi 대각 증폭률이 **2(q + Σ₊ − 1)** — D2 가 계량에서 얻은 값.
"""
from __future__ import annotations

import numpy as np

from bianchi.charts import general as G
from bianchi.conventions import EPS3_J, tracefree_from_5
from bianchi.optional_dependencies import require_jax_x64

jax, jnp = require_jax_x64(feature=__name__)


#: 기울기가 항등적으로 0 인 `trace` (index 1) 를 뺀 구속 인덱스.
ACTIVE = (0, 2, 3, 4, 5, 6, 7)
NAMES = ("gauss", "cod1", "cod2", "cod3", "jac1", "jac2", "jac3")

#: 닫힘이 요구하는 물질 법칙의 계수 (적합으로 결정 — §4 참조).
#: (Q, ΣQ, qQ, ΠA, εNΠ, NQ, εAQ, Ω, qΩ, A·Q, tr(ΣΠ))
CLOSURE_COEFFS = np.array([-2.0, -1.0, 2.0, 3.0, 1.0, 0.0, 0.0,
                           -2.0, 2.0, 2.0 / 3.0, -1.0 / 3.0])
TERM_NAMES = ("Q", "SigmaQ", "qQ", "PiA", "epsNPi", "NQ", "epsAQ",
              "Omega", "qOmega", "A.Q", "tr(SigmaPi)")


# ═══════════════════════════════════════ 배위 만들기
def configuration(Sigma, N, A1, pi5, gamma=4.0 / 3.0):
    """★ **구속을 만족하는** 확장 상태 w = (y14, Q3, Ω, Π5) 를 만든다.

    Codazzi 는 q_flux 를 맞춰서, Gauss 는 Ω 를 맞춰서 0 으로 둔다.
    ★ Jacobi 는 **호출자의 몫**이다 — N^{ab}A_b = 0 인 N 을 줘야 한다
      (안 그러면 구속면 위가 아니라 위 논리가 통째로 무너진다; 대조군으로 쓴다).
    """
    Sigma = np.asarray(Sigma, float)
    N = np.asarray(N, float)
    Av = np.array([float(A1), 0.0, 0.0])
    S2 = float(np.trace(Sigma @ Sigma)) / 6.0
    K = float(G.curvature(jnp.asarray(N), jnp.asarray(Av))[0])
    qf = 3.0 * Av @ Sigma + np.einsum("abc,bd,cd->a", np.asarray(EPS3_J), N, Sigma)
    w = np.concatenate([np.asarray(G.StateG.of(Sigma, N, Av).packed()),
                        qf, [1.0 - S2 - K], np.asarray(pi5, float)])
    return w, gamma


def _pieces(w, gamma):
    Pi = tracefree_from_5(*w[18:23])
    args = {"gamma": gamma, "Omega": w[17], "q_flux": w[14:17], "Pi": Pi}
    return G.StateG.from_packed(w[:14]), Pi, args


def constraint_fn(gamma):
    def C(w):
        y, _, args = _pieces(w, gamma)
        return G.constraint_vector(y, args)[jnp.asarray(ACTIVE)]
    return C


def flow_fn(gamma, coeffs, freeze_matter=False):
    """확장 흐름 — 기하는 차트의 `rhs`, 물질은 `coeffs` 가 정한 법칙.

    `freeze_matter=True` 면 물질을 얼린다 (**현재 차트의 실제 동작**).
    """
    c = np.zeros(11) if freeze_matter else np.asarray(coeffs, float)

    def f(w):
        y, Pi, args = _pieces(w, gamma)
        a = G.aux(y, args)
        Q, S, N, A, q, Om = w[14:17], y.Sigma, y.N, y.A, a["q"], w[17]
        dQ = (c[0] * Q + c[1] * (S @ Q) + c[2] * q * Q + c[3] * (Pi @ A)
              + c[4] * jnp.einsum("abc,bd,cd->a", EPS3_J, N, Pi)
              + c[5] * (N @ Q) + c[6] * jnp.einsum("abc,b,c->a", EPS3_J, A, Q))
        dOm = (c[7] * Om + c[8] * q * Om + c[9] * jnp.dot(A, Q)
               + c[10] * jnp.sum(S * Pi))
        return jnp.concatenate([G.rhs(0.0, y, args).packed(), dQ,
                                jnp.atleast_1d(dOm), jnp.zeros(5)])
    return f


# ═══════════════════════════════════════ ★★ 증폭 행렬과 닫힘 잔차
def amplification_matrix(w, gamma, coeffs=CLOSURE_COEFFS, freeze_matter=False):
    """★★ ∂(Jf)/∂w = M·J 를 최소제곱으로 풀어 M 과 **닫힘 잔차**를 낸다.

    반환 dict(M, residual, rows, rank, q, Sigma_p).
    """
    C = constraint_fn(gamma)
    f = flow_fn(gamma, coeffs, freeze_matter)
    wj = jnp.asarray(w)
    J = np.asarray(jax.jacfwd(C)(wj))
    Gv = np.asarray(jax.jacfwd(lambda v: jax.jacfwd(C)(v) @ f(v))(wj))
    M = np.linalg.lstsq(J.T, Gv.T, rcond=None)[0].T
    sc = max(float(np.abs(Gv).max()), 1e-300)
    y, _, args = _pieces(wj, gamma)
    return dict(M=M, J=J, Gv=Gv,
                residual=float(np.abs(M @ J - Gv).max() / sc),
                rows=np.abs(M @ J - Gv).max(axis=1) / sc,
                rank=int(np.linalg.matrix_rank(J, tol=1e-10)),
                q=float(G.aux(y, args)["q"]),
                Sigma_p=-float(np.asarray(y.Sigma)[0, 0]) / 2.0)



def state_to_extended(y, args):
    """차트 상태 + args 의 물질 → 확장 상태 w = (y14, Q3, Ω, Π5)."""
    Pi = np.asarray(args.get("Pi", np.zeros((3, 3))), float)
    Q = np.asarray(args.get("q_flux", np.zeros(3)), float)
    a = G.aux(y, args)
    Om = float(args["Omega"]) if args.get("Omega") is not None else float(a["Omega"])
    pi5 = np.array([Pi[0, 0], Pi[1, 1], Pi[0, 1], Pi[0, 2], Pi[1, 2]])
    return np.concatenate([np.asarray(y.packed()), Q, [Om], pi5])


def general_amplification_rate(y, args):
    """★★ 일반 차트의 증폭률 — M 의 **스펙트럼 상한** (max Re λ).

    반환 dict(rate, closure, spectrum).  `closure` 가 크면 (물질이 얼어 있으면)
    rate 를 믿으면 안 된다 — 조용히 숫자만 돌려주지 않고 함께 낸다.
    """
    w = state_to_extended(y, args)
    r = amplification_matrix(w, float(args["gamma"]))
    ev = np.linalg.eigvals(r["M"])
    return dict(rate=float(np.max(ev.real)), closure=r["residual"],
                spectrum=ev, M=r["M"])
