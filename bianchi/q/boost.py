"""
Q7b · **정확 광행차** — 움직이는 전자에서 근사 없는 Thomson (76차).

★ 계획보다 강한 결과가 나왔다 (실측으로 확인):
  가중 각밀도 Ĝ(ê) = ∫f p³dp 는 부스트 하에서 **닫힌다**.
      f 는 로런츠 불변 ⇒ Ĝ'(ê') = 𝒟⁴ Ĝ(ê),  𝒟 = γ(1 − v·ê)
      dΩ' = dΩ/𝒟²
  Thomson 핵은 정지계에서 λ-무관이므로 ∫p³dp 와 가환.  따라서 **Mode A 도
  움직이는 전자에서 정확**하다 (계획은 Mode B 전용이라고 적었다 — 정정).

그리고 보간이 **0회**다: 정확 충돌 루틴이 임의 노드 방향·가중을 받으므로,
정지계로 간다는 것은 (ê, w, ln Ĝ) 를 (ê', w/𝒟², ln Ĝ + 4 ln 𝒟) 로 바꿔 넣는 것뿐이다.

한계 (정직하게): Ĝ 는 에너지 **1모멘트**라 스펙트럼을 나르지 않는다.
y-왜곡 같은 분광 관측량은 Mode B (완전 f) 가 필요하다 — `y_from_mixing`.
"""
from __future__ import annotations

import numpy as np

from bianchi.q.comoving import collide_log


def doppler(ehat, v):
    """𝒟 = γ(1 − v·ê),  그리고 광행차된 방향 ê'."""
    v = np.asarray(v, float)
    v2 = float(v @ v)
    if v2 >= 1.0:
        raise ValueError("|v| < 1 이어야 한다")
    g = 1.0 / np.sqrt(1.0 - v2)
    e = np.asarray(ehat, float).reshape(-1, 3)
    ve = e @ v
    D = g * (1.0 - ve)
    # ê' = [ê + γv(γ(v·ê)/(γ+1) − 1)] / (γ(1 − v·ê))
    num = e + (g * (g * ve / (g + 1.0) - 1.0))[:, None] * v[None, :]
    ep = num / D[:, None]
    ep /= np.linalg.norm(ep, axis=1)[:, None]
    return D, ep


def collide_moving_log(lw, lG, ehat, v, nu_dt, kernel="thomson"):
    """★ 정확 부스트 → 정지계 3항 → 역부스트.  보간 0회."""
    D, ep = doppler(ehat, v)
    lD = np.log(D)
    lw_p = np.asarray(lw, float) - 2.0 * lD
    lG_p = np.asarray(lG, float) + 4.0 * lD
    out_p = collide_log(lw_p, lG_p, ep, nu_dt, kernel)
    return out_p - 4.0 * lD


def collide_moving_ov(lw, lG, ehat, v, nu_dt, order=1, kernel="thomson"):
    """비교군: 𝒟 를 v 의 `order` 차까지 전개한 근사 (표준 코드의 방식)."""
    e = np.asarray(ehat, float).reshape(-1, 3)
    v = np.asarray(v, float)
    ve = e @ v
    if order == 1:
        lD = -ve
        ep = e - (v[None, :] - ve[:, None] * e)
    else:
        v2 = float(v @ v)
        lD = -ve + 0.5 * v2 - 0.5 * ve ** 2 + 0.0
        ep = e - (v[None, :] - ve[:, None] * e) * (1.0 - ve[:, None])
    ep = ep / np.linalg.norm(ep, axis=1)[:, None]
    out_p = collide_log(np.asarray(lw) - 2.0 * lD,
                        np.asarray(lG) + 4.0 * lD, ep, nu_dt, kernel)
    return out_p - 4.0 * lD


# ────────────────────────────────── 비섭동 분광 왜곡 (Mode B)
def planck(p, T=1.0):
    return 1.0 / np.expm1(p / np.asarray(T))


def y_from_mixing(sph, rad, dT_over_T, nu_dt=50.0):
    """★ 서로 다른 온도 흑체의 **비섭동 혼합**이 만드는 y-왜곡.

    선형 코드는 ΔT/T 를 1차로 자르므로 이 양이 구조적으로 0 이다.
    해석 기대 (Chluba-Sunyaev): y ≈ ½⟨(ΔT/T)²⟩ (등방화 완료 후).

    반환 (y_measured, y_expected).
    """
    from bianchi.q import collide as X
    from bianchi.q import sphere as S
    e, w = S.nodes(sph)
    p = np.asarray(rad.p())
    T = 1.0 + dT_over_T * e[:, 2]                  # 방향의존 온도 (O(1) 허용)
    f = np.array([planck(p, t) for t in T])        # (M, n_p)
    out = X.collide_modeb(sph, f.ravel(), len(p), nu_dt).reshape(len(w), len(p))
    # 등방화 후의 각평균 스펙트럼
    fbar = np.einsum("a,ap->p", w, out) / w.sum()
    # 같은 에너지밀도를 갖는 단일 흑체 T_eff 를 빼서 왜곡을 잰다
    dl = float(rad.dlnp); wt = np.ones(len(p)); wt[0] = wt[-1] = 0.5
    rho = float((fbar * p ** 4 * wt).sum() * dl)
    Teff = (rho / (np.pi ** 4 / 15.0)) ** 0.25
    resid = fbar - planck(p, Teff)
    # ★ 2성분 동시 적합 (온도이동 + y).  T_eff 를 **에너지**로 맞췄으므로
    #   잔차에는 온도이동 성분이 남아 있고, 그것은 y-모양과 직교하지 않는다.
    #   1성분으로 적합하면 y 가 오염된다 (76차 실측: 비 1.50 → 2성분에서 1.00).
    x = p / Teff
    g_T = x * np.exp(x) / np.expm1(x) ** 2                    # ∂n/∂lnT
    g_y = g_T * (x / np.tanh(x / 2.0) - 4.0)                  # y-모양
    msk = (x > 0.02) & (x < 20.0)
    A = np.stack([g_T[msk], g_y[msk]], axis=1)
    coef, *_ = np.linalg.lstsq(A, resid[msk], rcond=None)
    y = float(coef[1])
    T2 = float(np.einsum("a,a->", w, (dT_over_T * e[:, 2]) ** 2) / w.sum())
    return y, 0.5 * T2
