"""
G1 · 운동량격자 볼츠만 f(t, q, n̂) — 비-PSTF 절편 1 (71차).

표현: **불변운동량** 격자 (Bianchi I: p_i 상수) — 반경 = freestream GL (96),
방향 = freestream 각격자 (576).  ⇒ 자유흐름 팔이 **항등으로 정확** (계획
"특성곡선 정확"의 가장 강한 형태); 시간의존은 모멘트 사상 (P=p/a) 과
충돌항에만 들어간다.

충돌 (Thomson, 탄성·비등방핵 — 비-PSTF 직접구적):
    C[f](n̂) = ν·(K̂f − f),   K̂[i,j] = w_j·(3/16π)(1+(n̂_i·n̂_j)²)
  · 이산 보존형: K̂ 행을 **이산 정규화** (Σ_j K̂[i,j] = 1 기계정밀) — 수·
    에너지 보존이 구적오차 없이 성립 (G2 보존형 설계의 선취).
  · 운동량은 광자-단독 완화에선 비보존 (전자욕 흡수) — B2b 가 복원 (문서화).
  · 스텝 = 대칭화 고유분해 지수 (√w-상사) — 양수성 보존 (마르코프 생성자).

게이트 (계획 삼중): (i) 충돌 off + 이방 a: J-모멘트 ≡ J_moment 오라클 (동일
구적 — 기계 0); (ii) PSTF 계층 절단 대조; (iii) 격자 감쇠율 ≡ ν(1−k_l),
k_l = Thomson 핵 고유값 (rustcore); + 보존·양수성 기계 게이트.

LIMITATIONS: 충돌 게이트는 등방 배경 (phys≡불변 방향) — **이방배경 충돌의
방향 재맵 + Strang 오차 측정은 G2** (자유흐름 팔이 항등이라 여기선 분할오차
자체가 0).  Rust 격자 커널 = G1b.  질량0.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np

import bianchi.matter.freestream as fs

Q, DQ, NHAT, WANG = fs._Q, fs._DQ, fs._NHAT, fs._WANG
NR, NA = Q.shape[0], NHAT.shape[0]


def initial_grid(f0=fs.f_fermi_dirac, aniso=None):
    """F[r, a] = f(q_r, n̂_a).  aniso(nhat)->(NA,) 곱인자 (방향 이방성 씨앗)."""
    F = np.repeat(np.asarray(f0(Q), float)[:, None], NA, axis=1)
    if aniso is not None:
        F = F * np.asarray(aniso(NHAT), float)[None, :]
    return F


def moments_from_grid(F, a_vec, l, i):
    """J^(i)_{A_l} — hierarchy.J_moment 와 **동일 측도·격자** (무질량):
    ∫dλ λ² E (λ/E)^n e^{⊗l} f,  E=λ,  P = p/a."""
    a = np.asarray(a_vec, float)
    V = float(np.prod(a))
    P = (Q[:, None, None] * NHAT[None, :, :]) / a[None, None, :]
    lam = np.sqrt(np.einsum("rai,rai->ra", P, P))
    w = (DQ[:, None] * Q[:, None] ** 2) * WANG[None, :] / V
    integ = w * lam * F                                # E=λ, (λ/E)^n = 1
    if l == 0:
        return float(integ.sum())
    ehat = P / lam[:, :, None]
    letters = "ijklmn"[:l]
    subs = ",".join(f"ra{c}" for c in letters)
    T = np.einsum(f"ra,{subs}->{letters}", integ, *([ehat] * l))
    from bianchi.matter.hierarchy import pstf
    return pstf(T)


@lru_cache(maxsize=1)
def _thomson_eig():
    """대칭화 고유분해 (√w-상사) — 보존형 정규화 후."""
    mu = NHAT @ NHAT.T
    K = (3.0 / (16.0 * np.pi)) * (1.0 + mu * mu) * WANG[None, :]
    K = K / K.sum(axis=1, keepdims=True)               # ★ 이산 보존형
    sw = np.sqrt(WANG)
    S = (sw[:, None] * K) / sw[None, :]
    S = 0.5 * (S + S.T)                                # 대칭 (상사 후 잔여 반올림)
    lam, U = np.linalg.eigh(S)
    return lam, U, sw


def thomson_step(F, nu_dt):
    """F ← exp(ν dt (K̂−I)) F — 셸별 (탄성: 반경 불변).  양수성 보존."""
    lam, U, sw = _thomson_eig()
    e = np.exp(nu_dt * (lam - 1.0))
    # f̃ = √w f;  f̃' = U e Uᵀ f̃
    Ft = F * sw[None, :]
    Ft = (Ft @ U) * e[None, :] @ U.T
    return Ft / sw[None, :]


def multipole_amplitudes(F, l_max=3):
    """방향 다중극 진폭 (반경 축약 후 정준계수 노름) — 감쇠율 측정용."""
    from bianchi.matter import pstf_coeff as PC
    g = (DQ * Q**3) @ F                                # 에너지-가중 방향밀도
    out = {}
    for l in range(l_max + 1):
        if l == 0:
            out[0] = float((g * WANG).sum())
            continue
        letters = "ijklmn"[:l]
        subs = ",".join(f"a{c}" for c in letters)
        T = np.einsum(f"a,{subs}->{letters}", g * WANG, *([NHAT] * l))
        out[l] = float(np.linalg.norm(PC.to_ccoef(T, l)))
    return out
