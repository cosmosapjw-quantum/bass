"""
J3 · 계수공간 계층의 Rust 커널 래퍼 — 격자 팩킹 + 1호출 FFI (61차).

계약:
  · 팩킹: l-major, (l,i) 블록 연속 — off(l,i) = Σ_{l'<l}(2l'+1)(i_pad+1)
    + i(2l+1).  좌변/RHS 격자는 이웃 (l+2, i+2) 패딩을 **호출자**가 채운다
    (dense 계약 "이웃 필수, 절단은 호출자" 동일).
  · 좌표-동일 (R5b): Rust 표는 pstf_coeff 산출의 codegen 캐리 — 두 경로의
    차이는 축약 합 순서뿐 (비트-정확 주장 안 함; 게이트는 두-경로 대조).
  · 벽: l_max ≤ 10 (c2 표 l_in=l+2 ≤ 12 에서 유도).
  · **이번 증분은 기존 호출자를 재배선하지 않는다** — 오라클 교체는 별도
    증분 (R5b 46차 6절: 포트와 교체를 섞으면 게이트 이동의 귀속 불가).
"""
from __future__ import annotations

import numpy as np

from bianchi.backend_policy import require_native
from bianchi.matter import pstf_coeff as PC
from bianchi.matter import tilted_coeff as TC
from bianchi.matter.hierarchy_coeff import SIGMA_SIGNS
from bianchi.matter.tilted import SIGNS

L_KERNEL_MAX = 10

#: lib.rs 와 고정 합의된 부호 순서.
_SIGN_ORDER = ("A", "B", "C", "D", "E", "Omega", "divcon", "divfree")


def grid_offsets(l_pad, i_pad):
    """{(l,i): (시작, 2l+1)} — 커널 off() 와 동일 산술."""
    out, o = {}, 0
    for l in range(l_pad + 1):
        n = 2 * l + 1
        for i in range(i_pad + 1):
            out[(l, i)] = (o, n)
            o += n
    return out, o


def pack_grid(Jc, l_pad, i_pad):
    """dict[(l,i)]→(2l+1,) 을 평탄 격자로.  누락 이웃은 KeyError (계약)."""
    offs, total = grid_offsets(l_pad, i_pad)
    g = np.empty(total)
    for (l, i), (o, n) in offs.items():
        v = np.asarray(Jc[(l, i)], float).reshape(n)
        g[o:o + n] = v
    return g


def unpack_grid(flat, l_max, i_max):
    offs, total = grid_offsets(l_max, i_max)
    assert flat.size == total
    return {(l, i): flat[o:o + n].copy()
            for (l, i), (o, n) in offs.items()}


def _signs_vec(signs, order, default):
    s = default if signs is None else signs
    return np.array([float(s[k]) for k in order])


def lhs_grid(Jc, dJc, geo, cg, l_max, i_max, signs=None):
    """tilted 좌변 전 격자 — `equation_lhs_coeff(gm=cg)` 의 1호출 Rust 판.

    cg: `ClosedGeoBlocks` (적합계수·γ·v3 의 단일 진실원 — R5a 가드 상속)."""
    rust = require_native("coeff_kernel.lhs_grid")
    if l_max > L_KERNEL_MAX:
        raise ValueError(f"coeff 커널 벽: l_max ≤ {L_KERNEL_MAX} "
                         "(c2 표 l_in=l+2 ≤ 12)")
    if not isinstance(cg, TC.ClosedGeoBlocks):
        raise TypeError("cg 는 ClosedGeoBlocks — 적합계수의 단일 진실원")
    cg._check_geo()                                    # R5a: 스테일 즉시 거부
    j = pack_grid(Jc, l_max + 2, i_max + 2)
    dj = pack_grid(dJc, l_max + 2, i_max + 2)
    s5 = PC.sigma_to_c5(geo["sigma"])
    w = TC._omega_vec(geo["omega"])                    # 카르테시안 (rot 축!)
    u3 = PC.vec_to_c3(geo["udot"])                     # 정준 (cv/ov 축)
    out = rust.coeff_lhs_grid(j, dj, l_max, i_max, float(geo["H"]), s5, w, u3,
                              cg.gamma, cg.v3, cg.c_pd, cg.c_dc, cg.c_df,
                              _signs_vec(signs, _SIGN_ORDER, SIGNS))
    return unpack_grid(np.asarray(out), l_max, i_max)


def mass_blocks(geo, l, signs=None):
    """`mass_blocks_for` 의 Rust 판 — (γI, up, down|None)."""
    rust = require_native("coeff_kernel.mass_blocks")
    s = SIGNS if signs is None else signs
    v = np.asarray(geo["v"], float)
    gam = float(geo["gamma_lorentz"])
    return rust.coeff_mass_blocks(l, gam, PC.vec_to_c3(v),
                                  float(s["divcon"]), float(s["divfree"]))


def rhs_grid(Jc, H, s5, l_max, i_max, signs=None):
    """untilted `hierarchy_rhs_coeff` 전 격자의 1호출 Rust 판."""
    rust = require_native("coeff_kernel.rhs_grid")
    if l_max > L_KERNEL_MAX:
        raise ValueError(f"coeff 커널 벽: l_max ≤ {L_KERNEL_MAX}")
    j = pack_grid(Jc, l_max + 2, i_max + 2)
    out = rust.coeff_rhs_grid(j, l_max, i_max, float(H), np.asarray(s5, float),
                              _signs_vec(signs, ("A", "B", "C"), SIGMA_SIGNS))
    return unpack_grid(np.asarray(out), l_max, i_max)
