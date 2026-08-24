"""
I1b · 계층 N-항 (곡률-방향 결합) — 계수공간 닫힘 (66차).

물리 (64–65차): ė = (N·e)×e 의 수송 ∂_t f ⊃ −ė·∇_e f — (l,i) 에서 **i-대각**
(질량0 전용; 질량>0 은 p/Ê 인자가 i-혼합 → 명시 거부).

구조 (측정 확정):
    O = −Σ_d N_d · (e_d-곱) ∘ (L_d)          [d = 카르테시안]
  · 선택규칙: Δl∉{±1} 정확 0;  N 등방 ⇒ O ≡ 0 (e·L = 0).
  · 합성 항등 X = −M@G 오라클 내 실측 1.1e−16.
  · ★ 닫힌형: α_up(l) = (l+1)/(2l+3) (M(l+1←l)=α·ov), α_dn ≡ 1
    (M(l−1←l)=cv) — 표준 다중극 재귀 가중.  기존 ov/cv/rot 재사용, 새 표 0.
  · ★★ 반증 박제 (67차): 1판은 α_up≡1·α_dn=l/(2l+1) 로 **뒤바뀐** 배정 —
    계수↔함수 규약 (to_ccoef: F = Σ c·√D·Z) 을 φ=Z/√D 로 오독, 오라클·수송
    시험이 **같은 오규약으로 순환 자기일치**해 통과했었다.  결합 freestream
    (to_ccoef-텐서 오라클) 이 순환을 깨고 D₃/D₂ = 7/3 인자로 적발.
    ⇒ 교훈: 표현 규약 검증은 반드시 **외부 규약원** (dense 텐서) 에 앵커.
오라클: 구면 GL×균등 구적 (다항 정확).  계수기저 ψ_m = √D_l·Z_lm (to_ccoef 규약).
LIMITATIONS: 질량0 · N 대각 (n-대각 게이지) · 오라클 l≤6 (닫힘은 rg 표까지).
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np
import sympy as sp

from bianchi.matter import pstf_coeff as PC

CART_TO_CANON = (2, 0, 1)
L_ORACLE_MAX = 6


@lru_cache(maxsize=None)
def _grid(nq):
    xs, ws = np.polynomial.legendre.leggauss(nq)
    phis = 2.0 * np.pi * (np.arange(2 * nq) + 0.5) / (2 * nq)
    wphi = 2.0 * np.pi / (2 * nq)
    pts, wts = [], []
    for c, w in zip(xs, ws):
        s = np.sqrt(1.0 - c * c)
        for ph in phis:
            pts.append([s * np.cos(ph), s * np.sin(ph), c])
            wts.append(w * wphi)
    return np.asarray(pts), np.asarray(wts)


@lru_cache(maxsize=None)
def _z_funcs(l):
    x, y, z = sp.symbols("x y z", real=True)
    return tuple(sp.lambdify((x, y, z), PC.solid_expr(l, m), "numpy")
                 for m in range(-l, l + 1))


@lru_cache(maxsize=None)
def _grad_z_funcs(l):
    x, y, z = sp.symbols("x y z", real=True)
    out = []
    for m in range(-l, l + 1):
        expr = PC.solid_expr(l, m)
        out.append(tuple(sp.lambdify((x, y, z), sp.diff(expr, v), "numpy")
                         for v in (x, y, z)))
    return tuple(out)


def _eval_basis(l, pts):
    return np.stack([f(pts[:, 0], pts[:, 1], pts[:, 2])
                     * np.ones(len(pts)) for f in _z_funcs(l)], axis=1)


def dense_nterm_matrix(l_out, l_in, d, nq=None):
    """오라클: X_d[m',m] = √D_out·∫ Z_out (−ė·∇φ_in), ė = (ê_d-슬롯)×e."""
    if max(l_out, l_in) > L_ORACLE_MAX:
        raise ValueError("N-항 오라클은 l ≤ 6")
    if nq is None:
        nq = l_out + l_in + 6
    pts, wts = _grid(nq)
    Zout = _eval_basis(l_out, pts)
    e = pts
    w = np.zeros_like(e)
    w[:, d] = e[:, d]
    edot = np.cross(w, e)
    n_in = 2 * l_in + 1
    X = np.zeros((2 * l_out + 1, n_in))
    grads = _grad_z_funcs(l_in)
    sD_in = np.sqrt(PC.D_norm(l_in))
    sD_out = np.sqrt(PC.D_norm(l_out))
    for m in range(n_in):
        g = np.stack([grads[m][k](pts[:, 0], pts[:, 1], pts[:, 2])
                      * np.ones(len(pts)) for k in range(3)], axis=1)
        adv = -np.sum(edot * g, axis=1) * sD_in
        X[:, m] = (1.0 / sD_out) * (Zout * (adv * wts)[:, None]).sum(axis=0)
    return X


def mult_matrix(l_out, l_in, d, nq=None):
    """e_d-곱 연산자의 (l_out←l_in) 사영 블록."""
    if nq is None:
        nq = l_out + l_in + 6
    pts, wts = _grid(nq)
    Zout = _eval_basis(l_out, pts)
    Zin = _eval_basis(l_in, pts)
    sD_in = np.sqrt(PC.D_norm(l_in))
    sD_out = np.sqrt(PC.D_norm(l_out))
    F = Zin * sD_in * pts[:, d][:, None]
    return (1.0 / sD_out) * (Zout.T @ (F * wts[:, None]))


def rot_gen(l, d):
    """L_d 생성자 (카르테시안) = l · rot_block(l)[:,:,d]."""
    return l * PC.rot_block(l)[:, :, d]


def alpha_up(l):
    return (l + 1.0) / (2.0 * l + 3.0)


def alpha_dn(l):
    return 1.0


def measure_mult_constants(l_max=L_ORACLE_MAX):
    """오라클 실측 (게이트 전용) — 비비례면 RuntimeError (구조 반증 신호)."""
    a_up, a_dn = {}, {}
    for l in range(0, l_max):
        M = mult_matrix(l + 1, l, 0)
        B = PC.outer_vec_block(l + 1)[:, :, CART_TO_CANON[0]]
        a_up[l] = _ratio_const(M, B)
    for l in range(1, l_max + 1):
        M = mult_matrix(l - 1, l, 0)
        B = PC.contract_vec_block(l - 1)[:, :, CART_TO_CANON[0]]
        a_dn[l] = _ratio_const(M, B)
    return a_up, a_dn


def _ratio_const(M, B, tol=1e-10):
    mask = np.abs(B) > 1e-9                            # |B|<1e-9 = 구조적 0 취급
    if not mask.any():
        raise RuntimeError("비례 판정 불가 — 기준 블록이 0")
    r = M[mask] / B[mask]
    if np.abs(r - r.mean()).max() > tol * max(1.0, abs(r.mean())):
        raise RuntimeError(f"곱-블록 비비례 (구조 반증): 산포 {np.ptp(r):.2e}")
    if np.abs(M[~mask]).max() > 1e-12:
        raise RuntimeError("영형 불일치 (구조 반증)")
    return float(r.mean())


def closed_nterm_matrix(l_out, l_in, d):
    """닫힌 재구성 — 임의 l (rg 표까지).  Δl∉{±1}·l_in=0 은 정확 0."""
    if abs(l_out - l_in) != 1 or l_in < 1:
        # l_in=0: L_d(스칼라) ≡ 0 ⇒ 블록 정확 0.  (rot_block(0) 호출 금지 —
        #  pstf_coeff 0-나눗셈; 리뷰 지적, 이 가드가 봉인.)
        return np.zeros((2 * l_out + 1, 2 * l_in + 1))
    s = CART_TO_CANON[d]
    if l_out == l_in + 1:
        M = alpha_up(l_in) * PC.outer_vec_block(l_out)[:, :, s]
    else:
        M = alpha_dn(l_in) * PC.contract_vec_block(l_out)[:, :, s]
    return -(M @ rot_gen(l_in, d))                     # 부호: −ė·∇ (오라클 동일)


def nterm_coeff(Jc, N3, l, i, mass=0.0):
    """dJ_{l,i}/dt 의 N-항 (질량0, i-대각)."""
    if mass != 0.0:
        raise NotImplementedError("질량>0 은 p/Ê 인자가 i-혼합 — I 티어 후속")
    N3 = np.asarray(N3, float)
    if N3.shape != (3,):
        raise ValueError("N: 대각 (3,) — n-대각 게이지")

    def get(ll, ii):
        v = Jc.get((ll, ii))
        if v is None:
            raise KeyError(f"Jc[({ll},{ii})] 없음 — 이웃 필수 (절단은 호출자)")
        return np.asarray(v, float)

    out = np.zeros(2 * l + 1)
    for d in range(3):
        if N3[d] == 0.0:
            continue
        if l >= 2:
            out += N3[d] * (closed_nterm_matrix(l, l - 1, d) @ get(l - 1, i))
        out += N3[d] * (closed_nterm_matrix(l, l + 1, d) @ get(l + 1, i))
    return out
