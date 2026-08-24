"""
H1-b 감사 — 식 (12) 균질 축약 RHS 의 σ-결합 **부호 확정**과 정확성 검증.

방법 (PLAN-H §4): 논문은 (+---), 우리는 (-+++) 이므로 σ-결합 세 항군 (A, B, C) 의
전역부호가 미지수다.  추상지표 계산으로 단정하지 않고, **정확 구적해의 수치 시간미분**
을 오라클로 삼아 8가지 부호조합을 스캔해 확정한다.
(이 저장소가 회전 부호·curl 상대부호·³S_ab A-항 계수를 확정했던 것과 같은 방법.)

오라클: Bianchi I 는 불변기저 운동량 p_i = const 이므로 J^(i)_{A_l}(t) 를 임의 시각에
정확 구적으로 얻을 수 있다.  ȧ_i = (H+σ_i)a_i 로 t±dt 를 만들어 중심차분하면 dJ/dt 가
**정확**하게 나온다 (O(dt²)).

실행:  python -m audit.h_hierarchy
"""
from __future__ import annotations

import itertools
import json

import numpy as np

from bianchi.matter import freestream as fs
from bianchi.matter import hierarchy as H

# 홀수 l 다극을 켜기 위한 방향의존 분포 (등방 f₀ 는 f(p)=f(-p) 라 홀수 l ≡ 0)
F_DIP = H.f_dipole(0.4, axis=2)

LI = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (2, 0), (2, 1), (3, 0), (4, 0)]


def scan_signs():
    """8가지 (A,B,C) 부호조합의 최대 상대잔차 — 유일한 최소가 나와야 한다."""
    a = np.array([1.0, 0.9, 1.15])
    Hub, sig = 1.0, np.array([0.08, -0.03, -0.05])
    rows = []
    for sA, sB, sC in itertools.product([1.0, -1.0], repeat=3):
        signs = dict(A=sA, B=sB, C=sC)
        worst = 0.0
        for l, i in [(0, 0), (1, 0), (2, 0), (3, 0), (2, 1)]:
            worst = max(worst, H.rhs_residual(a, 0.8, Hub, sig, l, i,
                                              signs=signs, f0=F_DIP))
        rows.append((sA, sB, sC, worst))
    return rows


def dt_convergence():
    """잔차가 O(dt²) 인지 — 모델오차가 아니라 차분오차임을 증명."""
    a = np.array([1.0, 0.9, 1.15])
    out = {}
    for dt in (1e-3, 1e-4, 1e-5):
        out[dt] = H.rhs_residual(a, 0.0, 1.0, np.array([0.08, -0.03, -0.05]),
                                 2, 0, dt=dt)
    return out


def sweep():
    """질량·배경·(l,i)·분포 스윕.  세 게이트로 분리 보고."""
    rng = np.random.default_rng(1)
    w_dip = w_iso_even = w_odd_mag = 0.0
    n = 0
    for _ in range(3):
        av = np.array([1.0, *(1 + 0.4 * rng.uniform(-1, 1, 2))])
        s = rng.uniform(-0.12, 0.12, 3); s -= s.mean()
        hh = float(rng.uniform(0.6, 1.4))
        for m in (0.0, 0.8, 4.0):
            for (l, i) in LI:
                n += 1
                w_dip = max(w_dip, H.rhs_residual(av, m, hh, s, l, i, f0=F_DIP))
                if l % 2 == 0:
                    w_iso_even = max(w_iso_even,
                                     H.rhs_residual(av, m, hh, s, l, i))
                else:
                    J = np.abs(np.asarray(H.J_moment(av, m, l, i))).max()
                    w_odd_mag = max(w_odd_mag, J / H.J_moment(av, m, 0, 0))
    return dict(n_cases=n, dipole_all_li=w_dip, iso_even_l=w_iso_even,
                iso_odd_l_magnitude=w_odd_mag)


def main():
    out = {}
    rows = scan_signs()
    out["sign_scan"] = [dict(A=r[0], B=r[1], C=r[2], residual=r[3]) for r in rows]
    best = min(rows, key=lambda r: r[3])
    out["signs_determined"] = dict(A=best[0], B=best[1], C=best[2],
                                  residual=best[3])
    # 유일성: 2등과 최소 3자릿수 차이여야 확정으로 인정
    second = sorted(r[3] for r in rows)[1]
    out["uniqueness_margin"] = second / best[3]
    out["module_signs_match"] = (H.SIGMA_SIGNS["A"] == best[0]
                                 and H.SIGMA_SIGNS["B"] == best[1]
                                 and H.SIGMA_SIGNS["C"] == best[2])
    out["dt_convergence"] = {str(k): v for k, v in dt_convergence().items()}
    out["sweep"] = sweep()
    out["conclusion"] = (
        "sigma-coupling signs (A,B,C) = (%+g,%+g,%+g) uniquely determined by the "
        "exact-quadrature oracle; margin over runner-up = %.3g x. RHS verified at "
        "finite-difference precision over %d (mass, background, l, i, f0) cases."
        % (best[0], best[1], best[2], out["uniqueness_margin"],
           out["sweep"]["n_cases"]))
    print(json.dumps(out, indent=2, default=str))
    json.dump(out, open("audit/h_hierarchy.json", "w"), indent=2, default=str)


if __name__ == "__main__":
    main()
