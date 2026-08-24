"""
G2 · 충돌항 계층화 + 이방배경 방향 재맵 + Strang 실측 (72차).

★ 구조 정리 (이 증분의 핵심 — G1 이 이월한 "이방배경" 을 정면으로):
  이방 배경에서 **두 팔은 서로 다른 변수에서 대각**이다 —
    자유흐름: 불변운동량 p_i 에서 대각 (f 는 아예 상수)
    충돌:     물리 프레임 (λ, ê),  λ=|P|, ê=P/|P|,  P^i = p_i/a_i 에서 대각.
  둘을 잇는 사상은 구면 위 비선형 사상 ê = (n̂/a)/|n̂/a| 이고 야코비안은
        dΩ_phys/dΩ_inv = det(1/a) / μ³,   μ ≡ |n̂/a|
  ⇒ 물리 구적무게 w_phys = w_inv·det(1/a)/μ³  (Σw_phys = 4π 기계 게이트).

★ 에너지-교환 정리 (해석): Thomson·BGK 핵은 **λ-무관**이므로 충돌은 임의의
  에너지 가중과 **가환**이다.  따라서 가중 각밀도
        Ĝ^{(n)}_a := μ_a^{n+4} · Σ_r DQ_r Q_r^{n+3} F[r,a]      (ρ = Σ_a w_phys Ĝ^{(0)})
  는 **보간 없이** 정확히 진화한다:
        자유흐름:  Ĝ_a ← Ĝ_a · (μ_a(t₁)/μ_a(t₀))^{n+4}          (정확)
        충돌:      Ĝ ← exp(ν dt (K − I)) Ĝ                        (동결-a 정확)
  두 팔이 각각 정확하므로 **분할오차만 남고**, Strang 2차를 깨끗이 잰다.

사다리 (계획 §6 G2 단계):
  (a) BGK-등방  : K = 1·wᵀ/4π — 전 l≥1 이 **정확히 ν** (해석 대조군)
  (a') BGK-보존 : K = P_{l≤1} — 수·에너지·**운동량** 기계보존 (l≥1 중 l=1 보존)
  (b) Thomson   : K = w_j(3/16π)(1+(ê·ê')²), **Sinkhorn 대칭 스케일링**으로
                  행합=1 & w-열합=1 동시 만족 (보존형 이산화 — D2 접점).
운동량: 광자-단독 Thomson 은 쌍극을 ν(1−k₁)=ν 로 감쇠 — 전자욕으로 전달
(비보존이 물리).  BGK-보존이 운동량-보존 대조군 (B2b 접합 대비).

LIMITATIONS: 전체-f 재맵 (반경 보간) 은 여기 없음 — 모멘트/각밀도 경로가
결합에 필요한 전부이고 정확하다 (에너지-교환 정리).  질량0·탄성.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np

from bianchi.matter.grid_boltzmann import DQ, NA, NHAT, Q, WANG


def physical_frame(a_vec):
    """(ê (NA,3), μ (NA,), w_phys (NA,)) — 야코비안 무게 포함."""
    a = np.asarray(a_vec, float)
    P = NHAT / a[None, :]
    mu = np.linalg.norm(P, axis=1)
    ehat = P / mu[:, None]
    w_phys = WANG * (1.0 / np.prod(a)) / mu**3
    return ehat, mu, w_phys


def angular_density(F, a_vec, n=0):
    """Ĝ^{(n)}_a = μ^{n+4}·Σ_r DQ Q^{n+3} F — 에너지-교환 정리의 상태변수."""
    _, mu, _ = physical_frame(a_vec)
    rad = (DQ * Q**(n + 3)) @ np.asarray(F, float)
    return mu**(n + 4) * rad


def free_stream(G, a0, a1, n=0):
    """자유흐름 팔 (정확): Ĝ ← Ĝ·(μ₁/μ₀)^{n+4}."""
    _, mu0, _ = physical_frame(a0)
    _, mu1, _ = physical_frame(a1)
    return np.asarray(G, float) * (mu1 / mu0) ** (n + 4)


def _sinkhorn_symmetric(k, w, iters=200, tol=1e-15):
    """대칭 스케일링 d: K_ij = d_i k_ij d_j w_j 가 행합 1 & w-열합 1.
    (보존형 이산화 — 수·에너지 좌우 고유벡터 동시 확보.)"""
    d = np.ones(len(w))
    for _ in range(iters):
        r = (k * (d[None, :] * w[None, :])).sum(axis=1) * d
        d = d / np.sqrt(r)
        if np.abs(r - 1.0).max() < tol:
            break
    K = d[:, None] * k * (d[None, :] * w[None, :])
    return K


@lru_cache(maxsize=8)
def _thomson_cached(key):
    a = np.array(key, float)
    ehat, _, w = physical_frame(a)
    mu = ehat @ ehat.T
    k = (3.0 / (16.0 * np.pi)) * (1.0 + mu * mu)
    K = _sinkhorn_symmetric(k, w)
    sw = np.sqrt(w)
    S = (sw[:, None] * K) / sw[None, :]
    S = 0.5 * (S + S.T)
    lam, U = np.linalg.eigh(S)
    return K, lam, U, sw, w


def thomson_operator(a_vec):
    """(K, 고유쌍) — 물리 프레임 Thomson 핵 (보존형)."""
    return _thomson_cached(tuple(np.asarray(a_vec, float)))


def _lowl_projector(a_vec, l_max=1):
    """w-내적 정규직교 {1, ê_x, ê_y, ê_z} 사영자 (l ≤ l_max)."""
    ehat, _, w = physical_frame(a_vec)
    cols = [np.ones(NA)]
    if l_max >= 1:
        cols += [ehat[:, k] for k in range(3)]
    B = np.stack(cols, axis=1)
    # w-내적 그람-슈미트
    for j in range(B.shape[1]):
        for i in range(j):
            B[:, j] -= (w * B[:, i] * B[:, j]).sum() * B[:, i]
        B[:, j] /= np.sqrt((w * B[:, j] ** 2).sum())
    return B @ (B.T * w[None, :]), w


def collide(G, a_vec, nu_dt, kind="thomson"):
    """충돌 팔 (동결-a 정확): Ĝ ← exp(ν dt (K−I)) Ĝ."""
    G = np.asarray(G, float)
    if kind == "thomson":
        _, lam, U, sw, _ = thomson_operator(a_vec)
        return ((G * sw) @ U * np.exp(nu_dt * (lam - 1.0))) @ U.T / sw
    if kind == "bgk_iso":                              # K = 1·wᵀ/4π (사영자)
        P, w = _lowl_projector(a_vec, l_max=0)
        return P @ G + np.exp(-nu_dt) * (G - P @ G)
    if kind == "bgk_cons":                             # K = P_{l≤1} (운동량 보존)
        P, w = _lowl_projector(a_vec, l_max=1)
        return P @ G + np.exp(-nu_dt) * (G - P @ G)
    raise ValueError(f"unknown kind {kind}")


def invariants(G, a_vec):
    """(수/에너지 적분, 운동량 3벡터) — 물리 측도 (보존 게이트)."""
    ehat, _, w = physical_frame(a_vec)
    G = np.asarray(G, float)
    return float((w * G).sum()), np.einsum("a,a,ai->i", w, G, ehat)


def phys_multipole(G, a_vec, l):
    """물리 프레임 다중극 진폭 (정준계수 노름) — 감쇠율 측정."""
    from bianchi.matter import pstf_coeff as PC
    ehat, _, w = physical_frame(a_vec)
    G = np.asarray(G, float)
    if l == 0:
        return float((w * G).sum())
    letters = "ijklmn"[:l]
    subs = ",".join(f"a{c}" for c in letters)
    T = np.einsum(f"a,{subs}->{letters}", w * G, *([ehat] * l))
    return float(np.linalg.norm(PC.to_ccoef(T, l)))


def strang_evolve(G0, a_of, t0, t1, nsteps, nu, kind="thomson", n=0):
    """Strang: ½충돌(a(t)) → 자유흐름(t→t+dt, 정확) → ½충돌(a(t+dt))."""
    G = np.asarray(G0, float).copy()
    h = (t1 - t0) / nsteps
    for k in range(nsteps):
        ta, tb = t0 + k * h, t0 + (k + 1) * h
        aa, ab = a_of(ta), a_of(tb)
        G = collide(G, aa, 0.5 * nu * h, kind)
        G = free_stream(G, aa, ab, n=n)
        G = collide(G, ab, 0.5 * nu * h, kind)
    return G


def lie_evolve(G0, a_of, t0, t1, nsteps, nu, kind="thomson", n=0):
    """1차 (Lie) 분할 — 차수 대조군."""
    G = np.asarray(G0, float).copy()
    h = (t1 - t0) / nsteps
    for k in range(nsteps):
        ta, tb = t0 + k * h, t0 + (k + 1) * h
        aa, ab = a_of(ta), a_of(tb)
        G = collide(G, aa, nu * h, kind)
        G = free_stream(G, aa, ab, n=n)
    return G


# ═══════════════════════════════ G1b · 이방-강건 각격자 + Rust 커널 (73차)
def angular_grid(n_theta, n_phi):
    """정밀화 가능한 곱 규칙 (GL(cosθ) × 균등 φ) — freestream 규약 동일."""
    xc, wc = np.polynomial.legendre.leggauss(n_theta)
    phi = 2.0 * np.pi * (np.arange(n_phi) + 0.5) / n_phi
    wphi = np.full(n_phi, 2.0 * np.pi / n_phi)
    st = np.sqrt(1.0 - xc**2)
    nhat = np.stack([np.outer(st, np.cos(phi)).ravel(),
                     np.outer(st, np.sin(phi)).ravel(),
                     np.outer(xc, np.ones_like(phi)).ravel()], axis=-1)
    return nhat, np.outer(wc, wphi).ravel()


def physical_frame_on(nhat, wang, a_vec):
    """임의 각격자에서의 물리 프레임 (야코비안 무게 포함)."""
    a = np.asarray(a_vec, float)
    P = np.asarray(nhat, float) / a[None, :]
    mu = np.linalg.norm(P, axis=1)
    return P / mu[:, None], mu, np.asarray(wang, float) / np.prod(a) / mu**3


def measure_grid_quality(a_vec, n_theta, n_phi):
    """(Σw−4π, |∫dΩ êê − (4π/3)δ|) — 이방-강건성 실측 (G2 열화 곡선 대응)."""
    nhat, wang = angular_grid(n_theta, n_phi)
    e, _, w = physical_frame_on(nhat, wang, a_vec)
    M = np.einsum("a,ai,aj->ij", w, e, e)
    return (abs(float(w.sum()) - 4.0*np.pi),
            float(np.abs(M - (4.0*np.pi/3.0)*np.eye(3)).max()))


def thomson_matrix_rust(a_vec, nhat=None, wang=None):
    """Rust Sinkhorn 핵 (보존형) — Python `thomson_operator` 의 K 와 대조."""
    import bianchi_rustcore as _R
    if nhat is None:
        nhat, wang = NHAT, WANG
    e, _, w = physical_frame_on(nhat, wang, a_vec)
    return np.asarray(_R.gc_thomson(np.ascontiguousarray(e),
                                    np.ascontiguousarray(w)))


def collide_rust(G, K, nu_dt, tol=1e-16):
    """exp(νdt(K−I))·G — Rust 테일러 (eigh 없음)."""
    import bianchi_rustcore as _R
    return np.asarray(_R.gc_expm_apply(np.ascontiguousarray(K, float),
                                       np.ascontiguousarray(G, float),
                                       float(nu_dt), float(tol)))


def strang_evolve_rust(G0, a_of, t0, t1, nsteps, nu, n=0, tol=1e-16,
                       nhat=None, wang=None):
    """Strang 루프째 (Rust) — 물리 프레임 시퀀스는 Python 이 캐리 (좌표-동일)."""
    import bianchi_rustcore as _R
    if nhat is None:
        nhat, wang = NHAT, WANG
    h = (t1 - t0) / nsteps
    es, ws, ms = [], [], []
    for k in range(nsteps + 1):
        e, mu, w = physical_frame_on(nhat, wang, a_of(t0 + k * h))
        es.append(e)
        ws.append(w)
        ms.append(mu)
    out = _R.gc_strang(np.ascontiguousarray(G0, float),
                       np.ascontiguousarray(np.stack(es)),
                       np.ascontiguousarray(np.stack(ws)),
                       np.ascontiguousarray(np.stack(ms)),
                       int(nsteps), float(nu), float(h), int(n), float(tol))
    return np.asarray(out)
