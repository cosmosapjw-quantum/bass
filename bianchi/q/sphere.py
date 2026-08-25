"""
Q3 · 구면 표현층의 Python 면 + **독립 구적 오라클** (76차).

Rust `QSphere` 를 감싸고, 검증용으로 두 가지를 더 준다:
  · `lebedev26` — 8차 정확 Lebedev 규칙 (팔면체 대칭).  곱격자와 **족이 다른**
    구적이라 모멘트 대조의 독립 심판이 된다 (계획 §Q3 의 'Lebedev 교차').
  · 파이썬 참조 구현 (`ylm_ref`) — Rust 규약의 비트급 대조.
"""
from __future__ import annotations

import numpy as np

from bianchi.backend_policy import require_native

SQ2 = np.sqrt(2.0)


def sphere(n_theta=24, n_phi=48):
    rust = require_native("q.sphere.sphere")
    return rust.QSphere(n_theta, n_phi)


def nodes(sph):
    return np.asarray(sph.ehat()).reshape(-1, 3), np.asarray(sph.weights())


def idx(l, m):
    return l * l + (m + l)


def n_coef(l_max):
    return (l_max + 1) ** 2


# ───────────────────────────────────────────── 참조 구현 (scipy 무의존)
def ylm_ref(l_max, e):
    """실수 구면조화 참조 — 재귀는 Rust 와 같은 완전정규화 규약."""
    e = np.asarray(e, float)
    x = float(np.clip(e[2], -1.0, 1.0))
    s = float(np.sqrt(max(0.0, 1.0 - x * x)))
    phi = float(np.arctan2(e[1], e[0]))
    out = np.zeros(n_coef(l_max))
    for m in range(l_max + 1):
        col = np.zeros(l_max + 1)
        pmm = 1.0 / np.sqrt(4.0 * np.pi)
        for k in range(1, m + 1):
            pmm *= -np.sqrt((2.0 * k + 1.0) / (2.0 * k)) * s
        if m <= l_max:
            col[m] = pmm
        if m + 1 <= l_max:
            col[m + 1] = np.sqrt(2.0 * m + 3.0) * x * pmm
        for l in range(m + 2, l_max + 1):
            a = np.sqrt((2 * l - 1) * (2 * l + 1) / ((l - m) * (l + m)))
            b = np.sqrt((2 * l + 1) * (l + m - 1) * (l - m - 1)
                        / ((2 * l - 3) * (l - m) * (l + m)))
            col[l] = a * x * col[l - 1] - b * col[l - 2]
        c, sn = np.cos(m * phi), np.sin(m * phi)
        for l in range(m, l_max + 1):
            if m == 0:
                out[idx(l, 0)] = col[l]
            else:
                out[idx(l, m)] = SQ2 * col[l] * c
                out[idx(l, -m)] = SQ2 * col[l] * sn
    return out


# ───────────────────────────────────────────── 독립 구적 (Lebedev 26점, 8차)
def lebedev26():
    """26점 Lebedev 규칙 — 다항식 차수 7 까지 정확.  (nhat (26,3), w (26,) 합 4π)

    구성: 6 축점 (w=1/21), 12 면대각 (w=4/105), 8 체대각 (w=27/840).
    가중은 ∫dΩ/4π 정규이므로 4π 를 곱해 돌려준다.
    """
    pts, ws = [], []
    for k in range(3):
        for s in (+1.0, -1.0):
            v = np.zeros(3); v[k] = s
            pts.append(v); ws.append(1.0 / 21.0)
    r = 1.0 / np.sqrt(2.0)
    for i in range(3):
        for j in range(i + 1, 3):
            for si in (+1.0, -1.0):
                for sj in (+1.0, -1.0):
                    v = np.zeros(3); v[i] = si * r; v[j] = sj * r
                    pts.append(v); ws.append(4.0 / 105.0)
    t = 1.0 / np.sqrt(3.0)
    for sx in (+1.0, -1.0):
        for sy in (+1.0, -1.0):
            for sz in (+1.0, -1.0):
                pts.append(np.array([sx * t, sy * t, sz * t]))
                ws.append(27.0 / 840.0)
    return np.array(pts), 4.0 * np.pi * np.array(ws)


def moments_on(nhat, w, f):
    """(rho, q(3), pi(3,3)) — 임의 구적 위에서 (오라클 공용)."""
    wf = w * f
    rho = float(wf.sum())
    q = np.einsum("a,ai->i", wf, nhat)
    ee = np.einsum("ai,aj->aij", nhat, nhat) - np.eye(3) / 3.0
    pi = np.einsum("a,aij->ij", wf, ee)
    return rho, q, pi


def moments(sph, f):
    v = np.asarray(sph.moments(np.ascontiguousarray(f, float)))
    pi = np.array([[v[4], v[7], v[8]],
                   [v[7], v[5], v[9]],
                   [v[8], v[9], v[6]]])
    return float(v[0]), v[1:4].copy(), pi


def grid_quality(sph):
    """Σw − 4π 와 ∫êê − (4π/3)δ — 격자 항등의 상시 지표."""
    e, w = nodes(sph)
    s = abs(float(w.sum()) - 4.0 * np.pi)
    ee = np.einsum("a,ai,aj->ij", w, e, e) - (4.0 * np.pi / 3.0) * np.eye(3)
    return s, float(np.abs(ee).max())
