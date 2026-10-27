"""
J2 · **계층 RHS 의 계수공간 스왑** — 비틸트 hierarchy_rhs 의 2l+1 표현판.

dense `hierarchy.hierarchy_rhs` 와 **항별로 같은 수식**을 (2l'+1)×(2l+1)×5
블록으로 계산한다.  상태는 dict[(l,i)] → (2l+1,) 계수 (l=0 은 (1,)).

    out = −H[(3+n)J^(i) + (1−n)J^(i+1)]
          − s_A·(l/(2l+3))·[(2n+3)·c1(J^(i)) + (2−2n)·c1(J^(i+1))]
          − s_B·[(n−1)·c2(J^(i)_{l+2}) + (l−n)·c2(J^(i−1)_{l+2})]     (l−n = −2i)
          − s_C·(l(l−1)/(4l²−1))·[(n−1)·out(J^(i+2)_{l−2}) − (l+n+1)·out(J^(i+1)_{l−2})]

게이트: l≤4 (이웃 l+2≤6) 에서 dense 와 성분별 ≤1e−13; l=10 에서 가동
(3^10 무생성 — dense 는 원리적으로 불가한 영역).

tilted equation_lhs 의 추가 연산 (ω-회전 rot_block, u̇ 의 ov/cv 블록) 은
pstf_coeff 에 준비 완료 — 좌변 조립(질량행렬 포함) 스왑은 J2b 몫 (명시 이월).
"""
from __future__ import annotations

import numpy as np

from bianchi.matter.hierarchy import SIGMA_SIGNS
from bianchi.matter.pstf_coeff import (apply_block, c1_block, c2_block,
                                       outer_block, sigma_to_c5)


def hierarchy_rhs_coeff(Jc, H, s5, l, i, signs=None):
    """dense `hierarchy_rhs` 의 계수공간 판 — 같은 계약 (이웃 필수, 절단은 호출자)."""
    if signs is None:
        signs = SIGMA_SIGNS
    n = l + 2 * i

    def get(ll, ii):
        v = Jc.get((ll, ii))
        if v is None:
            raise KeyError(f"Jc[({ll},{ii})] 없음 — 이웃을 요구한다")
        return np.asarray(v, float)

    out = -H * ((3.0 + n) * get(l, i) + (1.0 - n) * get(l, i + 1))

    if l >= 1:
        cA = l / (2.0 * l + 3.0)
        G1 = c1_block(l)
        tA = ((2.0 * n + 3.0) * apply_block(G1, get(l, i), s5)
              + (2.0 - 2.0 * n) * apply_block(G1, get(l, i + 1), s5))
        out = out - signs["A"] * cA * tA

    G2 = c2_block(l)
    tB = (n - 1.0) * apply_block(G2, get(l + 2, i), s5)
    if (l - n) != 0.0:                                 # = −2i
        tB = tB + (l - n) * apply_block(G2, get(l + 2, i - 1), s5)
    out = out - signs["B"] * tB

    if l >= 2:
        cC = l * (l - 1.0) / (4.0 * l * l - 1.0)
        GO = outer_block(l)
        tC = ((n - 1.0) * apply_block(GO, get(l - 2, i + 2), s5)
              - (l + n + 1.0) * apply_block(GO, get(l - 2, i + 1), s5))
        out = out - signs["C"] * cC * tC

    return out


def sigma_c5(sigma):
    """(3,3) σ → 5-계수 (편의 재수출)."""
    return sigma_to_c5(sigma)
