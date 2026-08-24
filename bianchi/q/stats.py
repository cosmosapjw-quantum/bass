"""
Q16 · **통계 분석층** (76차) — 장기 run 의 산출을 물리 결론으로.

측도 의존성은 숨기지 않는다: 같은 양을 두 측도에서 재고 차이를 보고한다 (Q13).
"""
from __future__ import annotations

import numpy as np

from bianchi.q import boost as B


def bootstrap(fn, data, n=1000, seed=0, alpha=0.05):
    """(값, 신뢰구간) — 부트스트랩."""
    rng = np.random.default_rng(seed)
    d = np.asarray(data)
    base = float(fn(d))
    reps = np.array([float(fn(d[rng.integers(0, len(d), len(d))])) for _ in range(n)])
    lo, hi = np.quantile(reps, [alpha / 2, 1 - alpha / 2])
    return base, (float(lo), float(hi))


def gauss_map(u):
    """BKL/Gauss 사상: u > 2 → u−1, 1<u<2 → 1/(u−1)."""
    return u - 1.0 if u > 2.0 else 1.0 / (u - 1.0)


def gauss_invariant_pdf(x):
    """Gauss 사상의 정지분포 1/((1+x) ln2) on [0,1]."""
    return 1.0 / ((1.0 + x) * np.log(2.0))


def kasner_sequence(u0, n):
    us = [float(u0)]
    for _ in range(n):
        us.append(gauss_map(us[-1]))
    return np.array(us)


def gauss_measure_ks(us):
    """u 수열의 소수부가 Gauss 측도를 따르는가 (KS 통계·p)."""
    from scipy import stats
    x = np.asarray(us) % 1.0
    x = x[(x > 0) & (x < 1)]
    cdf = lambda t: np.log2(1.0 + t)          # noqa: E731
    return stats.kstest(x, cdf)


def matter_correction_exponent(tau, ln_omega, t_cut=-5.0):
    """dlnΩ/dτ — I2b 의 물질보정 지수."""
    t = np.asarray(tau); y = np.asarray(ln_omega)
    m = t < t_cut
    return float(np.polyfit(t[m], y[m], 1)[0])


def spectral_distortion(sph, rad, dT_over_T, nu_dt=50.0):
    """★ 비섭동 y-왜곡 (Q7b) 과 2차 해석 기대의 비."""
    y, ye = B.y_from_mixing(sph, rad, dT_over_T, nu_dt)
    return dict(y=y, y_second_order=ye, ratio=y / ye if ye else np.nan)


def distortion_convergence(dT_over_T, n_theta=(16, 24, 32), n_p=(200, 400, 800)):
    """★ 결과를 내기 전에 **수렴**을 먼저 보인다 (계획 §9 위험표)."""
    from bianchi.q import sphere as S
    from bianchi.q import transport as T
    out = []
    for nt, npz in zip(n_theta, n_p):
        y, ye = B.y_from_mixing(S.sphere(nt, 2 * nt), T.radial(-7.0, 4.5, npz),
                                dT_over_T)
        out.append(y)
    return np.array(out)
