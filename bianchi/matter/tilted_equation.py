"""
H5 · tilted 계층 식 (12) **좌변 조립** — 전 항 (σ, ω, u̇, 공간미분).

`hierarchy.hierarchy_rhs` 의 tilted 일반화.  법선합동 판과 달리 명시적 RHS 가 아니라
**좌변**을 준다: 좌변이 J̇ 에 대해 아핀이고 D 항이 이웃 l 의 J̇ 를 품기 때문에
dJ/dt 를 바로 풀어낼 수 없다 (질량행렬이 필요하다 → `tilted_mass.py`).

    LHS(J, J̇) = M(v)·J̇ − F(J)          (J̇ 에 대해 정확히 아핀)

부호는 H5-b (∇_μT^{μν}=0, l≤1) 와 H5-d (boosted 정확구적, l≤3) 두 독립 오라클로
확정됐다.  ★ 원래 `audit/h5d_tilted_residual.py` 에 있던 것을 라이브러리로 옮겼다 —
적분기가 이걸 필요로 하는데 라이브러리가 audit 을 임포트하는 것은 의존 방향이 거꾸로다.
audit 쪽은 여기서 재수출해 쓰므로 시험 API 는 바뀌지 않는다.
"""
from __future__ import annotations

import numpy as np

from bianchi.matter import tilted as TL
from bianchi.matter import tilted_terms as TT
from bianchi.matter.hierarchy import (_contract_one, _contract_two, _outer_sigma,
                                      pstf)


# ═══════════════════════════════════════ 식 (12) 좌변 (전 항)
def _contract_vec_first(J, w):
    """J_{a A_l} w^a — 첫 지표를 벡터와 축약 (rank l+1 → l).  (E) 항."""
    return np.tensordot(np.asarray(J, float), np.asarray(w, float), axes=([0], [0]))


def _outer_vec_last(J, w, l):
    """J_{⟨A_{l−1}} w_{a_l⟩} — 마지막 지표에 벡터 외적 후 PSTF (rank l−1 → l).  (D) 항."""
    T = np.multiply.outer(np.asarray(J, float), np.asarray(w, float))
    return pstf(T) if l >= 2 else T


def equation_lhs(J, dJ, geo, l, i, signs=None, backend=None):
    """식 (12) 좌변 (tilted 전 항).  0 이어야 한다."""
    s = TL.SIGNS if signs is None else signs
    n = l + 2 * i
    H = geo["H"]
    sig, omg, ud = geo["sigma"], geo["omega"], geo["udot"]

    def g(ll, ii):
        return J[(ll, ii)]

    def dg(ll, ii):
        return dJ[(ll, ii)]

    # ⊥J̇  (사틀 회전항 포함)
    out = TT.perp_dot(g(l, i), dg(l, i), geo, backend=backend)
    # H 항
    out = out + H * ((3.0 + n) * g(l, i) + (1.0 - n) * g(l, i + 1))
    # (div-con)  D^a J^(i)_{a A_l}
    out = out + s["divcon"] * TT.div_contracted(
        g(l + 1, i), dg(l + 1, i), geo, backend=backend
    )
    # (div-free) −(l/(2l+1)) D_{⟨a_l} J^(i+1)_{A_{l−1}⟩}
    if l >= 1:
        cf = l / (2.0 * l + 1.0)
        out = out + s["divfree"] * (-cf * TT.div_free_index(
            g(l - 1, i + 1), dg(l - 1, i + 1), geo, l, backend=backend
        ))
    # (Ω) −l J^(i)_{a⟨A_{l−1}} ω_{a_l⟩}{}^a
    if l >= 1:
        tO = _contract_one(g(l, i), omg)
        out = out + s["Omega"] * (-l * (pstf(tO) if l >= 2 else tO))
    # (D) (l/(2l+1))[(l+n+1)J^(i) + (2−n)J^(i+1)]_{⟨A_{l−1}} u̇_{a_l⟩}
    if l >= 1:
        cd = l / (2.0 * l + 1.0)
        tD = ((l + n + 1.0) * _outer_vec_last(g(l - 1, i), ud, l)
              + (2.0 - n) * _outer_vec_last(g(l - 1, i + 1), ud, l))
        out = out + s["D"] * cd * tD
    # (E) [(l−n)J^(i−1) + (n−2)J^(i)]_{a A_l} u̇^a       ★ (l−n) = −2i
    tE = (n - 2.0) * _contract_vec_first(g(l + 1, i), ud)
    if (l - n) != 0.0:
        tE = tE + (l - n) * _contract_vec_first(g(l + 1, i - 1), ud)
    out = out + s["E"] * tE
    # (A) (l/(2l+3))[(2n+3)J^(i) + (2−2n)J^(i+1)]_{a⟨A_{l−1}} σ_{a_l⟩}{}^a
    if l >= 1:
        ca = l / (2.0 * l + 3.0)
        tA = ((2.0 * n + 3.0) * _contract_one(g(l, i), sig)
              + (2.0 - 2.0 * n) * _contract_one(g(l, i + 1), sig))
        out = out + s["A"] * ca * (pstf(tA) if l >= 2 else tA)
    # (B) [(l−n)J^(i−1) + (n−1)J^(i)]_{ab A_l} σ^{ab}
    tB = (n - 1.0) * _contract_two(g(l + 2, i), sig)
    if (l - n) != 0.0:
        tB = tB + (l - n) * _contract_two(g(l + 2, i - 1), sig)
    out = out + s["B"] * tB
    # (C) (l(l−1)/(4l²−1))[(n−1)J^(i+2) − (l+n+1)J^(i+1)]_{⟨A_{l−2}} σ_{a_{l−1}a_l⟩}
    if l >= 2:
        cc = l * (l - 1.0) / (4.0 * l * l - 1.0)
        tC = ((n - 1.0) * _outer_sigma(g(l - 2, i + 2), sig)
              - (l + n + 1.0) * _outer_sigma(g(l - 2, i + 1), sig))
        out = out + s["C"] * cc * tC
    return pstf(out) if l >= 2 else out

