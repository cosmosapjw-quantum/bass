"""
B1 · 열역학 표의 Rust 코드생성 (중복 표류 방지).

`bianchi.thermo.dof` 의 g_*(T), g_*s(T) 표를 **단일 진리원(single source of truth)**
으로 삼아 `_rustcore/src/thermo/dof_table.rs` 를 생성한다.  Rust 쪽에 손으로 베껴두면
Python 표를 고칠 때(A1 처럼) 조용히 어긋나므로, 기계적으로 뽑는다.

사용:  python -m scripts.codegen_thermo_tables
"""
from __future__ import annotations

import os

from bianchi.thermo import dof

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_OUT = os.path.join(_ROOT, "_rustcore", "src", "thermo", "dof_table.rs")


def fmt(arr):
    """★ numpy 스칼라의 repr 은 `np.float64(...)` 이므로 float() 로 벗겨야 한다."""
    return ", ".join(repr(float(v)) for v in arr)


def generate() -> str:
    x, gs, gss = dof._x, dof._gs, dof._gss          # 오름차순 log10 T[GeV]
    n = len(x)
    lines = [
        "//! B1 · g_*(T), g_*s(T) 표 — **자동생성** (수정 금지).",
        "//!",
        "//! 생성기: `scripts/codegen_thermo_tables.py`",
        "//! 소스:   `bianchi.thermo.dof` (Husdal 2016 Table A1, 격자QCD 반영)",
        f"//! {n}점, 오름차순 log10 T[GeV].  Python 과 동일한 로그-선형 보간을 쓴다.",
        "",
        f"pub const N: usize = {n};",
        "",
        "/// log10(T / GeV), 오름차순",
        "#[allow(clippy::approx_constant)]",
        "#[rustfmt::skip]",
        f"pub const LOG10_T: [f64; N] = [{fmt(x)}];",
        "",
        "/// 에너지밀도 유효자유도 g_*",
        "#[rustfmt::skip]",
        f"pub const G_STAR: [f64; N] = [{fmt(gs)}];",
        "",
        "/// 엔트로피 유효자유도 g_*s",
        "#[rustfmt::skip]",
        f"pub const G_STAR_S: [f64; N] = [{fmt(gss)}];",
        "",
    ]
    return "\n".join(lines)


def main():
    src = generate()
    os.makedirs(os.path.dirname(_OUT), exist_ok=True)
    with open(_OUT, "w") as f:
        f.write(src)
    print(f"wrote {_OUT}  ({dof._x.size} points)")


if __name__ == "__main__":
    main()
