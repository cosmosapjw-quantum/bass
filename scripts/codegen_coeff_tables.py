"""
J3 · 계수공간 블록표의 Rust 코드생성 — **좌표-동일 캐리** (R5b 전략).

`bianchi.matter.pstf_coeff` 의 블록 6종 (outer/c1/c2/ov/cv/rot) 을 **Python 산출
그대로** `_rustcore/src/kinetic/coeff_tables.rs` 상수로 내보낸다.  Rust 쪽 재유도는
0 — 규약 (Condon–Shortley real_gaunt, 정준기저, 회전생성자 conj(V)(+iL)Vᵀ) 이
표에 이미 구워져 있으므로 커널은 축약만 한다.

**벽 (표 한계에서 유도)**: gaunt_tables.npz 는 l ≤ 12.
  · c2(l) 은 l_in = l+2 → l ≤ 10   ← 커널 좌변 벽 (L_KERNEL_MAX = 10)
  · cv(l) 은 l_in = l+1 → l ≤ 11
  · outer/c1/ov/rot → l ≤ 12  (격자 이웃 l+2 ≤ 12 와 정합)

사용:  python -m scripts.codegen_coeff_tables
"""
from __future__ import annotations

import os

import numpy as np

from bianchi.matter import pstf_coeff as PC

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_OUT = os.path.join(_ROOT, "_rustcore", "src", "kinetic", "coeff_tables.rs")

#: (이름, 블록함수, l 범위, K)  — l_in 은 커널이 이름에서 안다.
_OPS = [
    ("outer", PC.outer_block, range(2, 13), 5),
    ("c1", PC.c1_block, range(1, 13), 5),
    ("c2", PC.c2_block, range(0, 11), 5),
    ("ov", PC.outer_vec_block, range(1, 13), 3),
    ("cv", PC.contract_vec_block, range(0, 12), 3),
    ("rot", PC.rot_block, range(1, 13), 3),
]


def fmt(vals):
    """Serialize binary64 values with one representation for mathematical zero.

    Linear-algebra backends may return either sign bit for an exact zero.  The
    sign has no coefficient meaning here, so normalize both variants to +0.0
    before emitting Rust and keep every nonzero binary64 unchanged.
    """
    return ", ".join(
        repr(0.0 if float(v) == 0.0 else float(v)) for v in vals
    )


def generate() -> str:
    lines = [
        "//! J3 · 계수공간 블록표 — **자동생성** (수정 금지).",
        "//!",
        "//! 생성기: `scripts/codegen_coeff_tables.py`",
        "//! 소스:   `bianchi.matter.pstf_coeff` (gaunt_tables.npz "
        "stamp=sympy_real_gaunt_CS_v1)",
        "//!",
        "//! 좌표-동일 캐리 (R5b): Rust 재유도 0 — 규약 전부 표에 구워짐.",
        "//! 축 규약 주의: rot 의 3번째 축은 **카르테시안 (x,y,z)**,",
        "//! ov/cv 의 3번째 축은 **정준 l=1 (y,z,x)** — 혼용 금지 (J2 문서).",
        "",
        "#![allow(clippy::all)]",
        "",
        "pub const L_KERNEL_MAX: usize = 10;",
        "",
    ]
    for name, fn, ls, k in _OPS:
        up = name.upper()
        lmin, lmax = ls.start, ls.stop - 1
        offs, chunks = [0], []
        for l in ls:
            G = np.asarray(fn(l), float)
            chunks.append(G.ravel())          # (2l+1, 2l_in+1, K) row-major
            offs.append(offs[-1] + G.size)
        data = np.concatenate(chunks)
        assert np.isfinite(data).all(), name
        lines += [
            f"/// {name}: l = {lmin}..={lmax}, K={k}, 총 {data.size} f64",
            f"pub const {up}_MIN_L: usize = {lmin};",
            f"pub const {up}_MAX_L: usize = {lmax};",
            "#[rustfmt::skip]",
            f"pub static {up}_OFF: [usize; {len(offs)}] = [{', '.join(map(str, offs))}];",
            "#[rustfmt::skip]",
            f"pub static {up}_DATA: [f64; {data.size}] = [{fmt(data)}];",
            "",
        ]
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    src = generate()
    with open(_OUT, "w") as f:
        f.write(src)
    print(f"wrote {_OUT}  ({len(src)/1e6:.2f} MB)")
