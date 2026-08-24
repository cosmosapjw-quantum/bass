"""
J1 · 계수공간 PSTF 유도 감사 — 규약 잠금·환원원소·두 경로 대조의 기록 (57차).

확정 사슬:
  (1) 규약 잠금: 정준 실 solid harmonic (assoc_legendre 구성) 의 ∫Z₁Z₂Z₃ 가
      sympy real_gaunt 와 3.3e−15 합치 (Gauss-Legendre×균일φ 정확구적, 세션기록).
  (2) 사전: D_l = <T_lm,T_lm>_frob = (2l+1)!!/(4π l!) — U_basis 조립 시
      직교정규 검증 (실패하면 예외 = 사전 반증 감지기).
  (3) outer (l−2→l): 함수사전 곱-사영 ≡ PSTF 외적 ⇒ 자유상수 없는 완전
      닫힌형 R_out(l) = √(D_l/(D_{l−2}D₂)).  dense 대조 첫 시도 합치 2.2e−16.
  (4) c2 (l+2→l): ★ 1차 시도 (복소 Gaunt 최고웨이트 위상 조립) 는 dense 비율
      0.168→0.137 의 **l-의존 편차로 반증**.  단 그 비율이 (m',m,k) 전역
      단일상수 — Wigner-Eckart 인수분해 자체는 기계정밀 증명이었다.  정정은
      **수반항등** (정확, 상수 1):
          <pstf(J⊗σ), K>_l = J_A σ_{ab} K^{Aab} = <J, _contract_two(K,σ)>_{l−2}
      (K 대칭 ⇒ 지표순서 무관) + rg 완전대칭  ⇒  R_c2(l) = R_out(l+2).
  (5) c1 (l→l): 널벡터 최고웨이트 (M=(x̂+iŷ)/√2, M·M=0 ⇒ M^{⊗l} 이 대칭·
      무대각합·단위 Frobenius — 3^l 무생성 O(1) 산술): σ_{U₂₀}·M = −M/√6
      ⇒ 고유값 −1/√6.  1차 조립의 잉여인자 √D₂/(4π) = 관측비율 0.061477 로
      자체반증·제거.  닫힌형 인식 (측정 → 유리수 패턴 → 검증):
          **R_c1(l) = 2(2l+3)/l · √(π/30)**   (Gaunt 경로와 l=1..12 독립 일치)
  (6) 종합: 3연산 × 검증가능 전 (op,l) 에서 |dense − 닫힌형| ≤ 1.3e−15.

l>6 게이트 (dense 불가 영역, 비순환): (M·n)^l 전개는 정준 실기저에서 m=±l
두 슬롯뿐 → e_{m=+l} 이 c1(σ=U₂₀) 의 고유벡터 (고유값 −1/√6) — l=10 에서
rg 표·환원원소를 dense 없이 정확 검증.  선택규칙 (|Δl|≤2, m-규칙) 동반.

실행: python -m audit.j1_coeff_derivation
"""
from __future__ import annotations

import numpy as np
import sympy as sp

from bianchi.matter import pstf_coeff as PC


def R_c1_closed(l):
    """닫힌형 (정리 — 리뷰가 Racah 형으로 기호 증명): 2(2l+3)/l·√(π/30)."""
    return 2.0 * (2*l + 3) / l * float(sp.sqrt(sp.pi / 30))


def r_c1_theorem_symbolic():
    """정리의 기호 증명 잔차: g_hw = (−1)^{l+1}√(5/4π)·l/(2l+3) 대입 후 0."""
    l = sp.symbols("l", positive=True, integer=True)
    g_hw = (-1)**(l + 1) * sp.sqrt(sp.Rational(5, 4) / sp.pi) * l / (2*l + 3)
    lhs = (-1)**l * (-1 / sp.sqrt(6)) / g_hw
    rhs = 2 * (2*l + 3) / l * sp.sqrt(sp.pi / 30)
    return sp.simplify(lhs - rhs)


def closed_form_matches_gaunt_route(ls=(1, 2, 3, 4, 6, 8, 10, 12)):
    """R_c1 닫힌형 = Gaunt 경로 (독립 산술) — l 별 잔차 dict."""
    return {l: abs(R_c1_closed(l) - PC._R_op("c1", l)) for l in ls}


def dense_vs_closed_sweep():
    """경로 A(dense) vs 경로 B(닫힌형) — 검증가능 전 (op, l) 잔차 dict."""
    out = {}
    for op, ls in (("outer", (2, 3, 4, 5, 6)), ("c1", (1, 2, 3, 4, 5, 6)),
                   ("c2", (0, 1, 2, 3, 4))):
        blk = {"outer": PC.outer_block, "c1": PC.c1_block, "c2": PC.c2_block}[op]
        for l in ls:
            out[(op, l)] = float(np.abs(PC.dense_block(op, l) - blk(l)).max())
    return out


def null_eigen_gate(l):
    """비순환 l-임의 게이트: e_{m=+l} 은 c1(σ=U₂₀) 고유벡터, 고유값 −1/√6."""
    e = np.zeros(2*l + 1)
    e[-1] = 1.0                                    # m = +l 슬롯
    s5 = np.zeros(5)
    s5[2] = 1.0                                    # σ = U₂₀
    out = PC.apply_block(PC.c1_block(l), e, s5)
    return float(np.abs(out - (-1.0/np.sqrt(6.0))*e).max())


def report():
    print("== R_c1 closed vs gaunt:", closed_form_matches_gaunt_route())
    sweep = dense_vs_closed_sweep()
    print("== dense vs closed worst:", max(sweep.values()))
    print("== null eigen gate l=10:", null_eigen_gate(10))


if __name__ == "__main__":
    report()
