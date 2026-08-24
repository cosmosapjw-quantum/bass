"""
H5-e2 · tilted 계층의 **일반 l 질량행렬** — M(v)·J̇ = F.

H5-c 는 l ≤ 1 블록에서 M = γ(I + e₀vᵀ) (상삼각) 을 얻었다.  일반 l 에서는 상삼각성이
깨진다: (div-con) 이 l+1 로, (div-free) 가 l−1 **그리고 i+1** 로 결합하기 때문이다.

★ 닫힌형 (아래 두 경로로 교차검증):

    M[(l,i) ← (l,i)]     = γ · P                                   ⊥J̇ 의 J̇ 부분
    M[(l,i) ← (l+1,i)]   = s_dc · γ · P∘(v 를 첫 지표에 축약)        D^a J^(i)_{aA_l}
    M[(l,i) ← (l−1,i+1)] = s_df · (−l/(2l+1)) · γ · P∘(· ⊗ v)       D_{⟨a_l}J^(i+1)_{A_{l−1}⟩}

  P 는 PSTF 사영자 (l ≥ 2 에서만 비자명).  근거: 순수 boost 사틀에서 **E_A^t = γ v_A**
  이므로 D_B 가 시간미분을 γv_B 배로 끌어오고, ⊥J̇ 의 J̇ 계수는 u^t = γ 다.

★ **상태공간은 3^l 이 아니라 2l+1 차원 PSTF 부분공간이다.**
  초기 판은 3^l 저장공간에 그대로 M 을 세웠는데, 그러면 대각합 방향에서 **특이**해진다
  (측정: rank(P) = 2l+1 정확히 — l=2 에서 9 중 5, l=5 에서 243 중 11).
  ⇒ 여기서는 PSTF 정규직교기저 좌표로 M 을 세운다.  논문의 "2l+1 독립성분" 규약과도 맞다.
  이 사실을 놓치면 `np.linalg.solve` 가 특이행렬에서 조용히 쓰레기를 낸다.

★ **M 은 물질과 무관하다 (순수 기하)** — 방정식이 J̇ 에 대해 아핀이고 J̇-선형부가 J 를
  포함하지 않기 때문 (사틀 회전항은 J 에만 붙어 F 로 간다).  측정으로 확인: m=0 과
  m=1.5 에서 M 이 1.4e−14 이내 동일.

★ 검증 전략 (프로젝트 관례 — 두 경로):
  경로 A — 여기의 **닫힌형**
  경로 B — `audit/h5d_tilted_residual.equation_lhs` 를 J̇ 단위벡터로 때려 뽑는
           **일반 아핀 추출** (닫힌형을 전혀 쓰지 않는다)
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np

from bianchi.matter.hierarchy import pstf
from bianchi.matter.tilted import SIGNS


# ═══════════════════════════════════════ PSTF 부분공간 좌표
@lru_cache(maxsize=16)
def pstf_projector(l):
    """PSTF 사영자 P — (3^l, 3^l) 조밀행렬 (단위벡터에 `pstf` 를 때려 조립)."""
    d = 3 ** l
    if l < 2:
        return np.eye(d)
    P = np.empty((d, d))
    for c in range(d):
        e = np.zeros(d)
        e[c] = 1.0
        P[:, c] = np.asarray(pstf(e.reshape((3,) * l)), float).ravel()
    return P


@lru_cache(maxsize=16)
def pstf_basis(l):
    """PSTF 부분공간의 정규직교기저 Q — (3^l, 2l+1).

    ★ rank(P) = 2l+1 임을 여기서 **확인**한다 (가정하지 않는다).
    """
    P = pstf_projector(l)
    u, s, _ = np.linalg.svd(P)
    k = int((s > 1e-9).sum())
    if k != 2 * l + 1:
        raise AssertionError(f"l={l}: rank(P)={k} ≠ 2l+1={2 * l + 1}")
    return u[:, :k]


def to_coef(T, l):
    """rank-l PSTF 텐서 → 2l+1 좌표."""
    return pstf_basis(l).T @ np.asarray(T, float).ravel()


def to_tensor(c, l):
    """2l+1 좌표 → rank-l PSTF 텐서."""
    v = pstf_basis(l) @ np.asarray(c, float)
    return v.reshape((3,) * l) if l else float(v[0])


# ═══════════════════════════════════════ 닫힌형 연산자
def gamma_and_v(geo):
    """기하에서 (γ, v_A) 를 되읽는다 — 순수 boost 사틀의 E_A^t = γ v_A 를 이용.

    ★ v 를 따로 받지 않고 기하에서 뽑는 이유: 인자와 기하가 어긋날 여지를 없앤다.
    """
    gam = float(geo["uup"][0])
    return gam, np.asarray(geo["eup"], float)[:, 0] / gam


def _project(x, l):
    return pstf(np.asarray(x, float)) if l >= 2 else np.asarray(x, float)


def matvec(dJ, geo, l_max, i_max, signs=None, i_ratio=None):
    """M·J̇ — dict[(l,i)] → rank-l 배열 (닫힌형).

    ★ 마지막에 PSTF 사영을 적용한다 — `equation_lhs` 가 l ≥ 2 에서 그렇게 하기 때문.
      이걸 빼면 대각 블록이 γ·Id 가 되어 일반 아핀 추출과 어긋난다 (실제로 겪었다:
      l=2 에서 0.51, l=3 에서 0.84 불일치).

    ★ `i_ratio` (L3): (div-free) 는 (l,i) ← (l−1, i+1) 로 결합하므로 i = i_max 에서
      **격자 밖 J̇** 를 요구한다.  기본값(None)은 그것을 **버린다** — 그런데 J 쪽은
      닫힘으로 채우고 있어서 **닫힘이 J 와 J̇ 에서 서로 어긋난다**.
      `i_ratio[l−1]` (성분별 배열 또는 스칼라) 을 주면

            J̇^(i_max+1)_{A_{l−1}}  ≈  r_{l−1} · J̇^(i_max)_{A_{l−1}}

      로 **J 닫힘과 같은 비**를 써서 일관되게 닫는다.  무질량이면 r ≡ 1 이라
      정확한 축퇴(J^(i)=J^(0) ⇒ J̇^(i)=J̇^(0))를 그대로 재현한다.
      r 은 현재 상태에서 온 **상수 계수**이므로 M 은 여전히 J̇ 에 선형이다.
    """
    s = SIGNS if signs is None else signs
    gam, v = gamma_and_v(geo)
    out = {}
    for l in range(l_max + 1):
        for i in range(i_max + 1):
            acc = None                    # ★ R3: 기여가 없으면 사영도 하지 않는다
            if (l, i) in dJ:                                  # 대각: γ
                acc = gam * np.asarray(dJ[(l, i)], float)
            if l + 1 <= l_max and (l + 1, i) in dJ:           # (div-con): l+1 → l
                c = s["divcon"] * gam * np.tensordot(
                    np.asarray(dJ[(l + 1, i)], float), v, axes=([0], [0]))
                acc = c if acc is None else acc + c
            if l >= 1:                                        # (div-free)
                src = None
                if i + 1 <= i_max and (l - 1, i + 1) in dJ:
                    src = np.asarray(dJ[(l - 1, i + 1)], float)
                elif i + 1 == i_max + 1 and i_ratio is not None \
                        and (l - 1, i_max) in dJ:
                    r = i_ratio.get(l - 1)
                    if r is not None:
                        src = np.asarray(r, float) * np.asarray(
                            dJ[(l - 1, i_max)], float)
                if src is not None:
                    t = np.multiply.outer(src, v)
                    c = s["divfree"] * (-l / (2.0 * l + 1.0)) * gam * \
                        (pstf(t) if l >= 2 else t)
                    acc = c if acc is None else acc + c
            # ★ pstf(0) = 0 이므로 빈 블록은 사영을 건너뛴다 (수학은 동일).
            out[(l, i)] = np.zeros((3,) * l) if acc is None else _project(acc, l)
    return out


# ═══════════════════════════════════════ PSTF 좌표의 조밀 행렬
def layout(l_max, i_max, n_star=None):
    """상태벡터 배치 (**PSTF 좌표**) — [(l,i) 순서, 오프셋, 총 길이].

    블록 크기는 3^l 이 아니라 **2l+1** 이다 (물리 상태공간).

    ★ `n_star` 를 주면 **삼각 절단** `l + 2i ≤ n_*` 으로 걸러낸다 (원논문 체계).
      기본값(None)은 기존 직사각 절단 — 옛 거동 그대로.
    """
    keys, off, n = [], {}, 0
    for l in range(l_max + 1):
        for i in range(i_max + 1):
            if n_star is not None and l + 2 * i > int(n_star):
                continue
            keys.append((l, i))
            off[(l, i)] = n
            n += 2 * l + 1
    return keys, off, n


def pack(dJ, l_max, i_max, n_star=None):
    keys, off, n = layout(l_max, i_max, n_star)
    x = np.zeros(n)
    for (l, i) in keys:
        if (l, i) in dJ:
            x[off[(l, i)]:off[(l, i)] + 2 * l + 1] = to_coef(dJ[(l, i)], l)
    return x


def unpack(x, l_max, i_max, n_star=None):
    keys, off, _ = layout(l_max, i_max, n_star)
    return {(l, i): to_tensor(x[off[(l, i)]:off[(l, i)] + 2 * l + 1], l)
            for (l, i) in keys}


def dense(geo, l_max, i_max, signs=None, i_ratio=None, n_star=None):
    """PSTF 좌표의 조밀 M — 단위벡터에 matvec 을 때려 조립.

    ★ 3^l 좌표가 아니라 2l+1 좌표라서 **정칙**이다 (3^l 판은 특이).
    ★ `n_star` 삼각 절단에서는 상태벡터 자체가 삼각형으로 줄어든다 — 절단 밖 J̇ 는
      `unpack` 이 만들지 않으므로 `matvec` 의 `in dJ` 검사가 자동으로 떨어뜨린다.
    """
    keys, off, n = layout(l_max, i_max, n_star)
    M = np.zeros((n, n))
    # ★ R3: 단위벡터는 **한 블록만** 비어 있지 않다.  전체 dict 를 만들면 `matvec` 이
    #   빈 블록마다 0 배열을 만들고 사영까지 했다 (프로파일: pstf 87057회).
    #   희소 dict 를 넘기면 `in dJ` 검사가 나머지를 그대로 떨어뜨린다.
    for (l0, i0) in keys:
        d = 2 * l0 + 1
        for j in range(d):
            coef = np.zeros(d)
            coef[j] = 1.0
            col = pack(matvec({(l0, i0): to_tensor(coef, l0)}, geo, l_max, i_max,
                              signs, i_ratio), l_max, i_max, n_star)
            M[:, off[(l0, i0)] + j] = col
    return M


def solve(F, geo, l_max, i_max, signs=None, i_ratio=None, n_star=None):
    """M·J̇ = F 를 풀어 J̇ dict 반환 (PSTF 좌표에서 선형해)."""
    M = dense(geo, l_max, i_max, signs, i_ratio, n_star)
    x = np.linalg.solve(M, pack(F, l_max, i_max, n_star))
    return unpack(x, l_max, i_max, n_star)


def conditioning_scan(a_vec=(1.0, 0.9, 1.2), da_vec=(0.35, 0.28, 0.42),
                      dv=(0.015, 0.01, -0.02), l_max=3, i_max=1,
                      vmax=0.9, n=10):
    """★ |v| 를 키우며 cond(M) 측정 — **유효 tilt 범위를 조용히 쓰지 않고 보고**한다.

    l ≤ 1 에서는 상삼각이라 온순했다(cond ≤ 2.4).  일반 l 은 결합이 늘어 더 커진다.
    """
    from bianchi.matter.tilted_terms import geometry
    d = np.array([1.0, -0.5, 1.5])
    d /= np.linalg.norm(d)
    out = []
    for f in np.linspace(0.0, vmax, n):
        geo = geometry(a_vec, da_vec, tuple(d * f), dv)
        M = dense(geo, l_max, i_max)
        out.append((float(f), float(np.linalg.cond(M)),
                    float(np.abs(M - np.eye(M.shape[0])).max())))
    return out
