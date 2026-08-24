"""
H'2 · 교환항 유도의 기호 박제 (sympy) — 총 운동량 보존 항등.

두 항등 (PLAN §4 "총 운동량 보존을 기호 항등으로"):
  (1) δdq̂ = R:  δdv 닫힌식을 q̂ = 3γΩv/G₊ 의 v-방향미분에 넣으면 R 가
      **항등으로** 나온다 (핵심 소거 G₋ + 2(γ−1)V² = G₊ 포함).  δdΩ=0 전제
      (I⁰=0 에서 에너지행이 강제).
  (2) Σ_c R_c = 0:  κ 대칭·영대각이면 쌍별 반대칭으로 총합이 항등 0.

사용:  python -m audit.h2_exchange_derivation
"""
from __future__ import annotations

import sympy as sp


def delta_dq_is_R_symbolic():
    """(1) 3-벡터 기호로 δ(dq̂) − R ≡ 0 을 simplify 로 증명."""
    g, Om = sp.symbols("gamma Omega", positive=True)
    v = sp.Matrix(sp.symbols("v1 v2 v3", real=True))
    R = sp.Matrix(sp.symbols("R1 R2 R3", real=True))
    V2 = (v.T @ v)[0]
    Gp = 1 + (g - 1) * V2
    Gm = 1 - (g - 1) * V2
    vR = (v.T @ R)[0]
    ddv = (Gp / (3 * g * Om)) * (R + (2 * (g - 1) / Gm) * vR * v)
    # q̂(v) = 3γΩ v/G₊ 의 방향미분 (Ω 고정 — δdΩ=0)
    dq = sp.zeros(3, 1)
    for a in range(3):
        qa = 3 * g * Om * v[a] / Gp
        for b in range(3):
            dq[a] += sp.diff(qa, v[b]) * ddv[b]
    resid = sp.simplify(dq - R)
    return all(r == 0 for r in resid)


def total_R_vanishes_symbolic(nc=3):
    """(2) 임의 대칭 κ (영대각) 에서 Σ_c R_c ≡ 0."""
    kap = sp.Matrix(nc, nc, lambda i, j: 0 if i == j
                    else sp.Symbol(f"k{min(i,j)}{max(i,j)}", real=True))
    Om = [sp.Symbol(f"Om{c}", positive=True) for c in range(nc)]
    v = [sp.Matrix(sp.symbols(f"v{c}1 v{c}2 v{c}3", real=True))
         for c in range(nc)]
    tot = sp.zeros(3, 1)
    for c in range(nc):
        for d in range(nc):
            tot += kap[c, d] * Om[c] * Om[d] * (v[d] - v[c])
    return all(sp.simplify(x) == 0 for x in tot)


if __name__ == "__main__":
    print("delta_dq == R :", delta_dq_is_R_symbolic())
    print("sum R == 0    :", total_R_vanishes_symbolic())
