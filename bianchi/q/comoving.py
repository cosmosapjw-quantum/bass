"""
Q5' · **공변 운동량 프레임** 캐리어 (76차 정정 설계).

반증 기록 (PLAN-Q §0 의 결정을 뒤집은 실측):
  고정 tetrad 격자는 Mixmaster 붕괴 (축비 2.2e28) 에서 표현 불가 — 물리 각분포가
  폭 ~1/축비 의 연필빔이 된다.  보간 횟수를 200배 줄여도 발산이 남았다 ⇒
  보간 불안정이 아니라 **표현 한계**.  계획 §9 위험표의 사전 등록 대응대로
  **공변격자 하이브리드**로 후퇴한다.

설계:
    p = M(τ) q ,   dM/dτ = −(I + Σ − ε·R) M
  · H·Σ·R 흐름이 정확히 흡수 (보간 0회).  Bianchi I 은 수송이 **항등**.
  · 곡률항 (N, A) 만 잔여 흐름 — 작고 벽 근처에서만 (Q5b 에서 반-라그랑주).
  · 격자점이 물리 프레임에서 **빔 쪽으로 모인다** (피적분함수 있는 곳에 노드).
  · 상태는 **ln Ĝ** (로그공간) — I2c 의 LNA_WALL 제거.

상태 정의:  Ĝ(q̂) = μ(q̂)⁴ · ∫ f q³ dq  (I2c 의 에너지-가중 각밀도),  μ = |M q̂|.
   ρ = Σ w_phys Ĝ,   w_phys = w_com · |det M| / μ³.
자유흐름 (곡률항 무시 영역): ∫f q³dq 불변 ⇒ **ln Ĝ 는 4 ln μ 로만 움직인다** (해석).
"""
from __future__ import annotations

import numpy as np

SQ3 = np.sqrt(3.0)


def sigma6_from_we5(S5):
    """WE 5성분 (Σ₊, Σ₋, Σ₁₂, Σ₁₃, Σ₂₃) → 대칭 6성분 (11,22,33,12,13,23)."""
    s = np.asarray(S5, float)
    return np.array([-2 * s[0], s[0] + SQ3 * s[1], s[0] - SQ3 * s[1],
                     s[2], s[3], s[4]])


def frame():
    import bianchi_rustcore as R
    return R.QFrame()


def frame_from(M):
    import bianchi_rustcore as R
    return R.QFrame.from_matrix(np.ascontiguousarray(np.asarray(M, float).ravel()))


def phys(fr, qhat):
    """(ê (M,3), μ (M,))."""
    q = np.ascontiguousarray(np.asarray(qhat, float).reshape(-1, 3)).ravel()
    v = np.asarray(fr.phys_dirs(q))
    m = q.size // 3
    return v[:3 * m].reshape(m, 3), v[3 * m:]


def ln_phys_weights(fr, w_com, mu):
    return np.asarray(fr.ln_phys_weights(np.ascontiguousarray(w_com, float),
                                         np.ascontiguousarray(mu, float)))


def moments_log(lw, lG, ehat):
    """**(ln ρ, q_a/ρ, π_ab/ρ)** — 로그-스케일 분리형.

    ★ 깊은 붕괴에서 ρ 자체는 double 범위를 넘는다 (ln ρ ~ 900).  물리가 쓰는
    것은 Ω = ρ/(3H²) 와 Π/Ω 같은 **비**이므로 비는 항상 범위 안이고 스케일만
    ln 으로 나른다 — 이것이 I2c 의 LNA_WALL 을 완전히 없애는 방식이다."""
    import bianchi_rustcore as R
    v = np.asarray(R.qm_moments_log(np.ascontiguousarray(lw, float),
                                    np.ascontiguousarray(lG, float),
                                    np.ascontiguousarray(np.asarray(ehat).ravel(), float)))
    pi = np.array([[v[4], v[7], v[8]], [v[7], v[5], v[9]], [v[8], v[9], v[6]]])
    return float(v[0]), v[1:4].copy(), pi


def collide_log(lw, lG, ehat, nu_dt, kernel="thomson"):
    import bianchi_rustcore as R
    return np.asarray(R.qm_collide_log(
        np.ascontiguousarray(lw, float), np.ascontiguousarray(lG, float),
        np.ascontiguousarray(np.asarray(ehat).ravel(), float),
        float(nu_dt), kernel))


class ComovingState:
    """공변격자 위의 (프레임, ln Ĝ) 상태 — Mode A."""

    __slots__ = ("sph", "qhat", "w_com", "fr", "lG")

    def __init__(self, sph, lG=None, fr=None):
        from bianchi.q import sphere as S
        self.sph = sph
        self.qhat, self.w_com = S.nodes(sph)
        self.fr = fr if fr is not None else frame()
        self.lG = np.zeros(len(self.w_com)) if lG is None else np.asarray(lG, float)

    def geometry(self):
        e, mu = phys(self.fr, self.qhat)
        return e, mu, ln_phys_weights(self.fr, self.w_com, mu)

    def moments(self):
        """(ln ρ, q/ρ, π/ρ)."""
        e, mu, lw = self.geometry()
        return moments_log(lw, self.lG, e)

    def ln_omega(self, lnH):
        """ln Ω = ln ρ − ln 3 − 2 ln H — 범위 벽 없이."""
        return self.moments()[0] - np.log(3.0) - 2.0 * float(lnH)

    def free_stream(self, S5_0, R0, S5_1, R1, dtau, weight_n=4.0):
        """★ 보간 0회 — 프레임만 굴리고 ln Ĝ 는 4 ln μ 로 해석적으로."""
        _, mu0 = phys(self.fr, self.qhat)
        fr1 = self.fr.step(sigma6_from_we5(S5_0), np.asarray(R0, float),
                           sigma6_from_we5(S5_1), np.asarray(R1, float), dtau)
        _, mu1 = phys(fr1, self.qhat)
        self.fr = fr1
        self.lG = self.lG + weight_n * (np.log(mu1) - np.log(mu0))
        return self

    def collide(self, nu_dt, kernel="thomson"):
        e, mu, lw = self.geometry()
        self.lG = collide_log(lw, self.lG, e, nu_dt, kernel)
        return self
