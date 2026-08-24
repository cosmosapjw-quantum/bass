"""
H5-d2 · 일반 rank tilted 항 — ⊥J̇, D^aJ_{aA_l}, D_{⟨a_l}J_{A_{l−1}⟩}.

`tilted.py` 는 rank 1·2 (l ≤ 1 블록) 를 손으로 조립해 ∇_μT^{μν} 오라클과 1e−11 로
맞췄다.  여기서는 그것을 **임의 rank 로 일반화**한다.  l ≥ 2 를 시험하려면 필요하다.

★ 핵심 함정 — 사틀이 시간의존이다:
    J′_{A_l}(t) 는 t-의존 사틀 E_A(t) 성분이므로  ⊥J̇_{A_l} ≠ dJ′_{A_l}/dt.
  성분을 직접 미분하면 사틀 회전항이 누락된다 (H1 에서 프레임 회전 규약 때문에 실제로
  부호 사고가 났던 지점과 같은 함정).

  **대응**: 성분이 아니라 **텐서로** 계산한다.
    J′^{μ₁…μ_l} = Σ J′_{A_l} E_{A₁}^{μ₁} … E_{A_l}^{μ_l}      (좌표성분, 공간균질)
    ∂_t J′^{μ…} = Σ (dJ′_A/dt) E…E  +  Σ J′_A ∂_t(E…E)        ← 둘째 항이 회전항
    ⊥J̇^{μ…} = h…h · u^λ∇_λ J′^{μ…}
  좌표성분이 공간균질이라 ∂_i = 0 이고 ∇ 가 닫힌다.  회전항이 **자동으로** 처리된다.

★ 검증 전략: 이 일반 코드가 rank 1·2 에서 `tilted.py` 의 (이미 ∇T 로 검증된) 값을
  재생산하는지 회귀로 고정한다.  재생산하면 higher rank 도 같은 근거로 신뢰한다.
  (`tests/test_h5d2_general_rank.py`)
"""
from __future__ import annotations

import numpy as np

from bianchi.matter.hierarchy import pstf
from bianchi.matter.tilted import _geometry

try:                                        # R5a · Rust 텐서 커널 (없으면 numpy)
    import bianchi_rustcore as _RC
except Exception:                           # pragma: no cover
    _RC = None

USE_RUST = _RC is not None


_RC_KEYS = ("eup", "edn", "deup", "hmix", "uup", "G")


def _rc_geo(geo):
    """geo 배열을 연속배열로 **한 번만** 만들어 캐시한다 (매 호출 마샬링 방지).

    ★ **버그 기록 (R5a)**: 처음엔 `geo["_rc"]` 에 그냥 넣었다.  그런데 시험이
      `dict(geo, deup=0)` 으로 geo 를 **복사·수정**해 대조군을 만드는데, 복사본이
      옛 `_rc` 를 그대로 물려받아 Rust 가 **낡은 deup 를 썼다** — 사틀 회전항 대조군이
      조용히 무력해졌다 (`test_tetrad_rotation_term_is_not_negligible` 이 잡았다).
      그래서 배열 **객체 동일성**을 키로 삼아, 하나라도 바뀌면 다시 만든다.
    """
    key = tuple(id(geo[k]) for k in _RC_KEYS)
    c = geo.get("_rc")
    if c is None or c[0] != key:
        c = (key, tuple(np.ascontiguousarray(np.asarray(geo[k], float))
                        for k in _RC_KEYS))
        geo["_rc"] = c
    return c[1]


def _rc_call(fn, X, dX, geo, out_rank):
    x = np.ascontiguousarray(np.asarray(X, float).ravel())
    d = np.ascontiguousarray(np.asarray(dX, float).ravel())
    r = np.asarray(X).ndim
    v = np.asarray(fn(x, d, r, *_rc_geo(geo)))
    return v.reshape((3,) * out_rank) if out_rank else float(v[0])


# ═══════════════════════════════════════ 사틀 ↔ 좌표 변환
def to_coord(X, eup):
    """X_{A₁…A_r} (사틀) → X^{μ₁…μ_r} (좌표).  지표 순서 보존."""
    out = np.asarray(X, float)
    for _ in range(out.ndim):
        out = np.tensordot(out, eup, axes=([0], [0]))
    return out


def to_tetrad(Xc, edn, n=None):
    """X^{μ₁…μ_r} → X_{A₁…A_r}.  `n` 지정 시 앞쪽 n 개 축만 변환."""
    out = np.asarray(Xc, float)
    r = out.ndim if n is None else n
    for _ in range(r):
        out = np.tensordot(out, edn, axes=([0], [1]))
    return out


def coord_time_derivative(X, dX, eup, deup):
    """∂_t X^{μ…} = Σ (dX_A/dt) E…E + Σ X_A ∂_t(E…E).

    ★ 둘째 항이 **사틀 회전항**이다 — 이걸 빼면 ⊥J̇ 가 틀린다.
    """
    X = np.asarray(X, float)
    dX = np.asarray(dX, float)
    r = X.ndim
    out = to_coord(dX, eup)
    for k in range(r):
        # k 번째 지표만 deup 로, 나머지는 eup 로
        cur = X
        for j in range(r):
            basis = deup if j == k else eup
            cur = np.tensordot(cur, basis, axes=([0], [0]))
        out = out + cur
    return out


def covariant_derivative(Xc, dXc, G):
    """∇_λ X^{μ₁…μ_r} = δ_λ⁰ ∂_t X^{μ…} + Σ_k Γ^{μ_k}_{λρ} X^{…ρ…}.

    반환 축 순서 (λ, μ₁, …, μ_r).  공간균질이라 ∂_i 항이 없다.
    """
    Xc = np.asarray(Xc, float)
    r = Xc.ndim
    out = np.zeros((4,) * (r + 1))
    out[0] += dXc
    for k in range(r):
        Xk = np.moveaxis(Xc, k, 0)                    # (ρ, 나머지…)
        term = np.tensordot(G, Xk, axes=([2], [0]))   # (μ_k, λ, 나머지…)
        out = out + np.moveaxis(term, 0, 1 + k)
    return out


def perp_dot(X, dX, geo, backend=None):
    """⊥Ẋ_{A₁…A_r} — 사영 시간미분의 사틀 성분 (회전항 포함).

    ★ R5a: Rust 커널이 있으면 그쪽으로 간다 (`backend="python"` 이 오라클).
    """
    if backend != "python" and USE_RUST:
        return _rc_call(_RC.tt_perp_dot, X, dX, geo, np.asarray(X).ndim)
    eup, edn, deup = geo["eup"], geo["edn"], geo["deup"]
    hmix, uup, G = geo["hmix"], geo["uup"], geo["G"]
    Xc = to_coord(X, eup)
    dXc = coord_time_derivative(X, dX, eup, deup)
    nab = covariant_derivative(Xc, dXc, G)
    uX = np.tensordot(uup, nab, axes=([0], [0]))      # u^λ∇_λ X^{μ…}
    for k in range(uX.ndim):                          # h^{μ_k}_{ν_k} 사영
        uX = np.moveaxis(np.tensordot(hmix, uX, axes=([1], [k])), 0, k)
    return to_tetrad(uX, edn)


def spatial_derivative(X, dX, geo, backend=None):
    """D_B X_{A₁…A_r} — 사영 공간미분.  반환 축 (B, A₁, …, A_r).

    ★ tilted 에서 이게 0 이 아니다: E_B^t = γ v_B 이므로 균질 양도 공간구배를 갖는다
      (균질성은 *법선* 합동의 초곡면에 대한 것이므로).
    """
    if backend != "python" and USE_RUST:
        return _rc_call(_RC.tt_spatial_derivative, X, dX, geo,
                        np.asarray(X).ndim + 1)
    eup, edn, deup, G = geo["eup"], geo["edn"], geo["deup"], geo["G"]
    Xc = to_coord(X, eup)
    dXc = coord_time_derivative(X, dX, eup, deup)
    nab = covariant_derivative(Xc, dXc, G)            # (λ, μ…)
    DX = np.tensordot(eup, nab, axes=([1], [0]))      # (B, μ…)
    r = np.asarray(X).ndim
    return to_tetrad(np.moveaxis(DX, 0, -1), edn, n=r)


def div_contracted(X_next, dX_next, geo, backend=None):
    """D^a J_{a A_l} — rank l+1 을 받아 rank l 반환 (div-con 항)."""
    if backend != "python" and USE_RUST:
        return _rc_call(_RC.tt_div_contracted, X_next, dX_next, geo,
                        np.asarray(X_next).ndim - 1)
    DX = spatial_derivative(X_next, dX_next, geo, backend)   # (B, a, A₁…A_l)
    return np.einsum("bb...->...", DX)


def div_free_index(X_prev, dX_prev, geo, l, backend=None):
    """D_{⟨a_l} J_{A_{l−1}⟩} — rank l−1 을 받아 **PSTF rank l** 반환 (div-free 항).

    ★ PSTF 는 Python 에 남겼다 — R3 에서 고정 행렬로 굳혀 이미 행렬곱 한 번이라
      포트 표면을 넓힐 이유가 없다.
    """
    if backend != "python" and USE_RUST:
        T = _rc_call(_RC.tt_div_free_raw, X_prev, dX_prev, geo,
                     np.asarray(X_prev).ndim + 1)
    else:
        DY = spatial_derivative(X_prev, dX_prev, geo, backend)
        T = np.moveaxis(DY, 0, -1)                     # (A₁…A_{l−1}, a_l)
    return pstf(T) if l >= 2 else T


# ═══════════════════════════════════════ 편의: 기하 핸들
def geometry(a_vec, da_vec, v, dv):
    """tilted 기하 묶음 (사틀·접속·운동학).  `tilted._geometry` + v/γ 탑재.

    ★ J2b 리뷰: 질량행렬의 v 와 geo 가 두 진실원이 되지 않게 v·γ 를 dict 에
    싣는다 (tilted_coeff.mass_blocks_for 가 소비)."""
    import numpy as _np
    d = _geometry(a_vec, da_vec, v, dv)
    d["v"] = _np.asarray(v, float)
    d["gamma_lorentz"] = 1.0 / _np.sqrt(1.0 - float(_np.dot(d["v"], d["v"])))
    return d
