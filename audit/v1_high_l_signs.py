"""
V1 감사 · **l ≥ 4 tilted 부호** — 식 (12) 를 l=4 에서 boosted 정확구적으로 심판.

H5-d 는 l ≤ 3 까지만 검증했다 (당시 기록: "l=4 는 rank-6 필요").  l=4 방정식은
  · (B) 항이 J^(i)_{A_6} — **rank-6 PSTF** 텐서 — 를 이중축약하고
  · (div-con) 이 l=5, (div-free)/(D)/(C) 가 l=3 을 참조한다.
격자를 l_max=6 까지 정확구적으로 채우면 절단 없이 **계수·부호만** 심판된다.

★ l=5 를 여기서 멈추는 이유 (정직): l=5 방정식은 l=7 격자가 필요하고 rank-7
  대칭화는 5040 순열 × 2187² — 분 단위가 아니라 시간 단위다.  l≤4 에서 전 항의
  l-의존 계수(l/(2l+1), l/(2l+3), l(l−1)/(4l²−1), (l−n))가 이미 네 값의 l 로
  과결정되므로, l=5 는 비용 대비 정보가 없다.

    python -m audit.v1_high_l_signs
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np

from audit import h5d_tilted_residual as R
from bianchi.matter import tilted as TL
from bianchi.matter import tilted_equation as TE
from bianchi.matter import tilted_terms as TT

A_VEC = (1.0, 0.9, 1.2)
DA_VEC = (0.35, 0.28, 0.42)
V = (0.08, -0.05, 0.12)
DV = (0.015, 0.01, -0.02)


@lru_cache(maxsize=8)
def _grids(mass, dt=1e-5, l_max=6, i_max=3):
    """rank-6 격자 (구축이 비싸다 — 부호반전 표가 재사용한다)."""
    geo = TT.geometry(A_VEC, DA_VEC, V, DV)
    J = R.moment_grid(A_VEC, V, mass, l_max=l_max, i_max=i_max)
    dJ = R.moment_grid_dot(A_VEC, DA_VEC, V, DV, mass, dt=dt,
                           l_max=l_max, i_max=i_max)
    rho = float(np.atleast_1d(np.asarray(J[(0, 0)], float))[0])
    return geo, J, dJ, rho


def residual_l4(mass, i, dt=1e-5, l_max=6, i_max=3, signs=None):
    """l=4, 속도가중 i 의 식(12) 잔차 (ρ 규격) — 격자는 l_max=6 정확구적."""
    geo, J, dJ, rho = _grids(float(mass), float(dt), int(l_max), int(i_max))
    r = np.asarray(TE.equation_lhs(J, dJ, geo, 4, i, signs), float)
    return float(np.abs(r).max() / rho)


def sign_flip_table(mass=0.7, i=0, dt=1e-5):
    """★★ 각 부호군을 하나씩 뒤집어 잔차가 몇 자릿수 뛰는지 — 시험의 이빨 확인.

    l=4 에서 항이 0 이 아니어야 대조군이 유효하다 ((l−n) = −2i 라 i=0 이면 (B),(E)
    의 J^(i−1) 갈래가 원래 0 — i=1 로도 본다).
    """
    base = residual_l4(mass, i, dt)
    rows = []
    for key in sorted(TL.SIGNS):
        s = dict(TL.SIGNS)
        s[key] = -s[key]
        rows.append((key, residual_l4(mass, i, dt, signs=s) / max(base, 1e-300)))
    return base, rows


def report():
    print("=" * 74)
    print("V1 · l=4 tilted 부호 — rank-6 PSTF 격자, 절단 없는 잔차")
    print("=" * 74)
    print("\n[1] ★★ 잔차 (ρ 규격, dt=1e−5 중앙차분 한계 ~1e−10)")
    for mass in (0.0, 0.7, 3.0):
        for i in (0, 1):
            print(f"    m={mass:3.1f}  i={i}:  {residual_l4(mass, i):.3e}")
    print("\n[2] ★★ 부호 반전 대조군 (잔차 증폭배수) — 전부 ≫ 1 이어야 이빨이 있다")
    for i in (0, 1):
        base, rows = sign_flip_table(i=i)
        print(f"    i={i} (기준 {base:.2e}):")
        for k, amp in rows:
            print(f"      {k:8s} 반전 → ×{amp:.1e}")


if __name__ == "__main__":
    report()
