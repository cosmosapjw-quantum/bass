"""
D2b · **일반 Bianchi 차트의 구속 증폭** — 0.0 을 돌려주던 자리를 메운다.

D2 는 type V 를 **물리 단위**에서 계량으로 유도했다.  여기서는 프로덕션 차트
(`charts/general`, 확장정규화) 로 올린다.  방법은 손대수가 아니라 **자동미분**이다.

★ 닫힘의 정의.  구속벡터 C(y) 와 흐름 f(y) 에 대해 Ċ = J(y)f(y) (J = ∂C/∂y) 다.
  계가 **닫혔다**는 것은 M(y) 가 있어 Ċ = M·C 라는 뜻이고, 구속면 위(C = 0)에서
  미분하면

        ∂(Jf)/∂y = M · J                         ← 이걸 최소제곱으로 푼다

  이고 **그 잔차가 곧 닫힘의 검사**다.  M 이 존재하면 그 스펙트럼이 증폭률이다.

★ 이 파일이 확정한 것:
  1. `trace` 구속의 기울기가 **항등적으로 0** 이다 (`tracefree_from_5` 로 짜서
     애초에 위반될 수 없다) — rank(J) = 7 ≠ 8.  감시해도 아무 정보가 없다.
  2. `gauss` 는 args 에 Ω 를 안 주면 **항등적으로 0** 이다 (`aux` 가 Gauss 로 Ω 를
     소거한다) — 기본 설정에서 Gauss 감시는 공허하다.
  3. 물질(Ω, Q, Π)을 **얼어붙은 args** 로 두면 구속계가 닫히지 않는다 (잔차 ~1).
  4. ★★ 닫히게 하는 물질 법칙을 **적합으로 결정**했다 (Jacobi 를 만족하는 무작위
     일반형 배위 4개, 잔차 1e−15):

        Q̇^a = (2q − 2)Q^a − Σ^a{}_b Q^b + 3 Π^{ab}A_b + ε^{abc}N_{bd}Π^d{}_c
        Ω̇   = (2q − 2)Ω + (2/3) A_aQ^a − (1/3) Σ_abΠ^{ab}

     후보로 넣은 `N Q` 와 `ε A Q` 는 계수가 **정확히 0** 으로 나왔다.
  5. ★★ 닫은 뒤 Codazzi 대각성분이 **2(q + Σ₊ − 1)** — D2 가 계량에서 얻은 값과
     같다.  `constraints.py` 가 인용한 `4(q + Σ₊ − 1)` 은 그 잔차가 2차식이라 두 배.

★ 대조군: Jacobi (N^{ab}A_b = 0) 를 **깨면** 같은 계수로도 잔차가 1e−1 로 튄다.
  구속면 위에서만 성립하는 관계라는 뜻이고, 방법에 이빨이 있다는 확인이다.

    python -m audit.d2b_chart_amplification
"""
from __future__ import annotations

import jax
import jax.numpy as jnp
import numpy as np

from bianchi.charts import general as G
from bianchi.conventions import EPS3_J, tracefree_from_5

from functools import lru_cache

from bianchi.constraint_rates import (ACTIVE, CLOSURE_COEFFS, NAMES,
                                     TERM_NAMES, amplification_matrix,
                                     configuration, constraint_fn, flow_fn,
                                     _pieces)


@lru_cache(maxsize=8)
def closure_coefficients(seed=11, n=4):
    """★★ 닫힘을 요구해 물질 법칙의 계수를 **적합으로 결정**한다.

    잔차 R(c) = Gv(c)·(I − J⁺J) 는 c 에 **선형**이므로 (Gv 가 흐름에 선형)
    한 번의 최소제곱으로 끝난다.  여러 배위를 쌓아 축퇴를 없앤다.
    """
    cfgs = _random_configs(seed, n)
    base = np.concatenate([_null_residual(w, g, np.zeros(11)) for w, g in cfgs])
    cols = []
    for k in range(11):
        e = np.eye(11)[k]
        cols.append(np.concatenate([_null_residual(w, g, e) for w, g in cfgs]) - base)
    X = np.stack(cols, axis=1)
    sol = np.linalg.lstsq(X, -base, rcond=None)[0]
    return dict(zip(TERM_NAMES, sol.tolist())), tuple(sol.tolist())


def _null_residual(w, gamma, coeffs):
    C = constraint_fn(gamma)
    f = flow_fn(gamma, coeffs)
    wj = jnp.asarray(w)
    J = np.asarray(jax.jacfwd(C)(wj))
    Gv = np.asarray(jax.jacfwd(lambda v: jax.jacfwd(C)(v) @ f(v))(wj))
    return (Gv @ (np.eye(J.shape[1]) - np.linalg.pinv(J) @ J)).ravel()


@lru_cache(maxsize=8)
def _random_configs(seed=11, n=4, jacobi=True):
    """★ 무작위 **일반형** 배위 — `jacobi=False` 면 N^{ab}A_b ≠ 0 (대조군)."""
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n):
        Sig = np.asarray(tracefree_from_5(*(rng.normal(size=5) * 0.15)))
        nn = rng.normal(size=3) * 0.4
        if jacobi:                      # A 방향(1)의 행·열을 0 으로 → N·A = 0
            N = np.array([[0.0, 0.0, 0.0], [0.0, nn[0], nn[1]], [0.0, nn[1], nn[2]]])
        else:
            N = np.asarray(tracefree_from_5(*(rng.normal(size=5) * 0.3)))
            N = 0.5 * (N + N.T)
        out.append(configuration(Sig, N, float(rng.uniform(0.3, 0.9)),
                                 rng.normal(size=5) * 0.06))
    return out


def closure_table(seed=11, n=4, jacobi=True, coeffs=None,
                  freeze_matter=False):
    """★ 배위마다 닫힘 잔차 — 표로."""
    c = CLOSURE_COEFFS if coeffs is None else np.asarray(coeffs, float)
    return [amplification_matrix(w, g, c, freeze_matter)["residual"]
            for w, g in _random_configs(seed, n, jacobi)]


# ═══════════════════════════════════════ 진단: 공허한 감시자들
def degenerate_constraints(w=None, gamma=4.0 / 3.0):
    """★★ 기울기가 **항등적으로 0** 인 구속을 찾는다 (감시해도 정보가 없다).

    반환 dict(row_norms, rank, trace_norm_full).
    """
    if w is None:
        w, gamma = _random_configs()[0]
    full = lambda v: G.constraint_vector(*(lambda p: (p[0], p[2]))(_pieces(v, gamma)))
    J = np.asarray(jax.jacfwd(full)(jnp.asarray(w)))
    return dict(row_norms=np.linalg.norm(J, axis=1),
                rank=int(np.linalg.matrix_rank(J, tol=1e-10)),
                trace_row=float(np.linalg.norm(J[1])))


def gauss_is_vacuous_without_omega(w=None, gamma=4.0 / 3.0):
    """★ args 에 Ω 를 안 주면 `aux` 가 Gauss 로 Ω 를 소거해 잔차가 **항등적 0**."""
    if w is None:
        w, gamma = _random_configs()[0]
    y, Pi, args = _pieces(jnp.asarray(w), gamma)
    with_om = float(G.constraint_residuals(y, args)["gauss"])
    no_om = {k: v for k, v in args.items() if k != "Omega"}
    # Ω 없이: Σ, N, A 를 흔들어도 gauss 가 0 인지 본다
    def g(v):
        yy, _, aa = _pieces(v, gamma)
        aa.pop("Omega")
        return G.constraint_residuals(yy, aa)["gauss"]
    grad = np.asarray(jax.grad(g)(jnp.asarray(w + 0.01)))
    return dict(with_omega=with_om,
                without_omega=float(G.constraint_residuals(y, no_om)["gauss"]),
                gradient_norm=float(np.linalg.norm(grad)))


def report():
    print("=" * 74)
    print("D2b · 일반 Bianchi 차트의 구속 증폭 (자동미분, 인용 없음)")
    print("=" * 74)

    d = degenerate_constraints()
    print(f"\n[1] ★★ 공허한 감시자")
    print(f"    구속별 기울기 노름: "
          + "  ".join(f"{n}={v:.3g}" for n, v in
                      zip(("gauss", "trace") + NAMES[1:], d["row_norms"])))
    print(f"    rank(J) = {d['rank']}  (8 이 아니다 — trace 는 위반될 수 없다)")
    v = gauss_is_vacuous_without_omega()
    print(f"    Ω 없이 gauss 잔차 = {v['without_omega']:.3e}, 기울기 노름 "
          f"{v['gradient_norm']:.3e}  ← 기본 설정에서 공허")

    print(f"\n[2] ★★ 물질을 얼리면 닫히지 않는다")
    print(f"    잔차: " + "  ".join(f"{r:.2e}" for r in closure_table(freeze_matter=True)))

    c, sol = closure_coefficients()
    print(f"\n[3] ★★ 닫힘이 결정하는 물질 법칙 (적합)")
    for k, val in c.items():
        print(f"    {k:12s} {val:+.9f}")
    print(f"\n    Q̇^a = (2q−2)Q^a − Σ^a_bQ^b + 3Π^{{ab}}A_b + ε^{{abc}}N_bd Π^d_c")
    print(f"    Ω̇   = (2q−2)Ω + (2/3)A·Q − (1/3)Σ·Π")
    print(f"    적합 계수로 잔차: " + "  ".join(f"{r:.2e}" for r in
                                              closure_table(coeffs=tuple(sol))))
    print(f"    정수 계수로 잔차: " + "  ".join(f"{r:.2e}" for r in closure_table()))

    print(f"\n[4] ★ 대조군 — Jacobi (N·A = 0) 를 깨면")
    print(f"    잔차: " + "  ".join(f"{r:.2e}" for r in closure_table(jacobi=False)))

    print(f"\n[5] ★★ Codazzi 증폭률 (type V 배위)")
    r = type_v_rate()
    print(f"    M[cod1,cod1] = {r['measured']:+.9f}")
    print(f"    2(q + Σ₊ − 1) = {r['predicted']:+.9f}   차 {r['gap']:.2e}")
    print(f"    인용식 4(q + Σ₊ − 1) = {2 * r['predicted']:+.9f} (2차 잔차라 두 배)")


def type_v_rate(A1=0.6, sigma=(0.12, -0.05, -0.07), gamma=4.0 / 3.0):
    """★★ type V (N = 0, Π = 0) 배위에서 Codazzi 대각 증폭률을 잰다."""
    Sig = np.diag(np.asarray(sigma, float))
    w, g = configuration(Sig, np.zeros((3, 3)), A1, np.zeros(5), gamma)
    r = amplification_matrix(w, g)
    pred = 2.0 * (r["q"] + r["Sigma_p"] - 1.0)
    return dict(measured=float(r["M"][1, 1]), predicted=pred,
                gap=abs(float(r["M"][1, 1]) - pred), residual=r["residual"])


if __name__ == "__main__":
    report()
