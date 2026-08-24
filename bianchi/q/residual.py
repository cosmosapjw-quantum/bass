"""
Q5b ★ **잔여 곡률 이류** — 공변 방향공간에서 곡률항 (N, A) 의 흐름 (78차).

계획 부록 A.5 의 간극을 메운다.

═══ 유도 (여기서 제1원리로; 시험이 박제) ═══
공변좌표 p = M q 에서
    dq/dτ = M⁻¹[dp/dτ + (I + Σ − εR)p] = M⁻¹ · C-항(p)/Ê
무질량이면 Ê = |p| 이고 C-항 = |p|²[((N̂ê)×ê) + (Â·ê)ê − Â] 이므로

    dq/dτ = |q| μ(q̂) · M⁻¹ w(ê),      w(ê) ≡ ((N̂ê)×ê) − Â_⊥
    (μ = |M q̂|,  ê = M q̂/μ,  Â_⊥ = Â − (Â·ê)ê)

|q| 에 비례 ⇒ **방향흐름과 반경 팽창률이 둘 다 |q| 무관**:

    dq̂/dτ      = μ · P_⊥[M⁻¹ w]                     … (R1) 방향 이류
    dln|q|/dτ  = μ · (q̂ · M⁻¹ w)                    … (R2) 반경 팽창

상태 lnĜ = 4 ln μ + ln J,  J(q̂) = ∫ f q³ dq (공변 반경적분).
J 는 (R1) 로 이류되고 (R2) 로 e^{4δ} 배 된다 (dq³dq ∝ q⁴):

    ln J_new(q̂) = ln J_old(q̂_back) + 4 δ(q̂)
    ln Ĝ_new(q̂) = 4 ln μ_new(q̂) + ln J_new(q̂)

★ class A 대조 (T4): w 의 N-항은 l ≤ 1 모멘트에 정확히 0 을 준다 —
  그래서 class A 는 이 항 없이도 구속이 기계정밀이었다.
★ class B: A-항 −Â_⊥ 는 l = 1 에 **직접** 작용 (Q-T5) — Codazzi 가 이 항을 요구한다.
"""
from __future__ import annotations

import numpy as np

from bianchi.q import comoving as CM


def _unpack_sym(v6):
    v = np.asarray(v6, float)
    M = np.zeros((3, 3))
    for x, (i, j) in zip(v, ((0, 0), (1, 1), (2, 2), (0, 1), (0, 2), (1, 2))):
        M[i, j] = M[j, i] = x
    return M


def residual_field(M, qhat, N6, A3):
    """(v_res (M,3) — 공변 구면 접벡터, dlnq (M,) — 반경 팽창률)."""
    Mm = np.asarray(M, float).reshape(3, 3)
    q = np.asarray(qhat, float).reshape(-1, 3)
    p = q @ Mm.T
    mu = np.linalg.norm(p, axis=1)
    e = p / mu[:, None]
    Nm, A = _unpack_sym(N6), np.asarray(A3, float)
    w = np.cross(e @ Nm.T, e)                      # ((N̂ê)×ê)
    if np.any(A):
        w = w - (A[None, :] - (e @ A)[:, None] * e)   # −Â_⊥
    Minv_w = w @ np.linalg.inv(Mm).T
    rad = np.einsum("ai,ai->a", q, Minv_w)         # q̂ · M⁻¹w
    v = mu[:, None] * (Minv_w - rad[:, None] * q)
    return v, mu * rad


def _backtrace(M, qhat, N6, A3, dtau, substeps=2):
    """역추적 q̂_back 과 전방 δ = ∫(dln|q|/dτ)dτ (RK2, 부분스텝)."""
    q = np.asarray(qhat, float).reshape(-1, 3).copy()
    h = -float(dtau) / substeps                    # 역방향
    delta = np.zeros(len(q))
    for _ in range(substeps):
        v1, r1 = residual_field(M, q, N6, A3)
        qm = q + 0.5 * h * v1
        qm /= np.linalg.norm(qm, axis=1)[:, None]
        v2, r2 = residual_field(M, qm, N6, A3)
        q = q + h * v2
        q /= np.linalg.norm(q, axis=1)[:, None]
        delta = delta - h * r2                     # 전방 부호로 누적
    return q, delta


def residual_step(sph, M, lG, N6, A3, dtau, k_theta=6, k_phi=6, substeps=2):
    """★ 잔여 이류 한 스텝.  lnĜ 을 갱신해 돌려준다 (보간은 여기서만 일어난다).

    반환 (lG_new, jac_min)."""
    import bianchi_rustcore as R
    from bianchi.q import sphere as S

    N6 = np.asarray(N6, float)
    A3 = np.asarray(A3, float)
    if not np.any(N6) and not np.any(A3):
        return np.asarray(lG, float), 1.0          # 곡률 없음 = 항등 (Bianchi I)

    qhat, _ = S.nodes(sph)
    fr = CM.frame_from(M)
    _, mu0 = CM.phys(fr, qhat)
    lnJ = np.asarray(lG, float) - 4.0 * np.log(mu0)

    qb, delta = _backtrace(M, qhat, N6, A3, dtau, substeps)
    plan = R.qt_plan_from_points(sph, np.ascontiguousarray(qb.ravel()),
                                 np.zeros(len(qhat)), int(k_theta), int(k_phi))
    lnJ_new = np.asarray(plan.apply_mode_a(np.ascontiguousarray(lnJ), 0.0)) + 4.0 * delta
    return lnJ_new + 4.0 * np.log(mu0), float(plan.jac_min)


def multipole_rate(sph, M, N6, A3, l):
    """진단: 잔여 속도장이 등방 J 에 주는 l-차 모멘트 변화율 (T4/Q-T5 검증)."""
    from bianchi.q import sphere as S
    qhat, w = S.nodes(sph)
    v, rad = residual_field(M, qhat, N6, A3)
    fr = CM.frame_from(M)
    e, mu = CM.phys(fr, qhat)
    if l == 0:
        return float((w * 4.0 * rad).sum())
    if l == 1:
        return np.einsum("a,a,ai->i", w, 4.0 * rad, e)
    raise ValueError("l ≤ 1")
