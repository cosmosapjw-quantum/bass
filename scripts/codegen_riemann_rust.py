"""
C1 · 일반유형 프레임 Riemann 의 Rust 코드생성.

`bianchi/generated/riemann_frame.pkl` (sympy, 144 비영성분, 24 인자) 를 읽어
`_rustcore/src/rays/riemann_gen.rs` 를 생성한다.  CSE 로 공통부분식을 공유해
컴팩트·고속 산술로 만든다.

★ 왜 codegen 인가: 대각 Bianchi I 은 Gauss-Codazzi 닫힌형으로 손유도했지만(R4),
  일반유형(N,A,R≠0)은 항이 많아 손유도가 위험하다.  **검증된 sympy 소스에서 기계적으로
  뽑으면 구성상 정확**하고, 차등테스트가 이를 확인한다.

사용:  python -m scripts.codegen_riemann_rust     (저장소 루트에서)
"""
from __future__ import annotations

import os
import pickle

import sympy as sp
from sympy.printing.rust import RustCodePrinter

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
_PKL = os.path.join(_ROOT, "bianchi", "generated", "riemann_frame.pkl")
_OUT = os.path.join(_ROOT, "_rustcore", "src", "rays", "riemann_gen.rs")

#: sympy 심볼명 -> Rust 식별자 (소문자, 충돌 없음)
_RUST_NAME = {"H": "hh", "Hd": "hd"}


def rust_ident(name: str) -> str:
    return _RUST_NAME.get(name, name.lower())


def generate() -> str:
    payload = pickle.load(open(_PKL, "rb"))
    names = payload["names"]
    comps = {k: sp.sympify(v) for k, v in payload["components"].items()}
    keys = sorted(comps.keys())
    exprs = [comps[k] for k in keys]

    # 심볼을 Rust 식별자로 치환한 뒤 CSE
    subs = {sp.Symbol(n): sp.Symbol(rust_ident(n)) for n in names}
    exprs = [e.xreplace(subs) for e in exprs]
    repl, reduced = sp.cse(exprs, optimizations="basic")

    printer = RustCodePrinter()

    def P(e):
        """Rust 코드 출력.  ★ nfloat 필수 — 정수 리터럴(`2*x`)은 Rust 에서 f64 와
        곱셈이 안 되므로 모든 수를 f64 리터럴(`2.0*x`)로 변환한다."""
        return printer.doprint(sp.nfloat(e, n=17))

    lines = []
    lines.append("//! C1 · 일반유형 프레임 Riemann R^a_bcd — **자동생성** (수정 금지).")
    lines.append("//!")
    lines.append("//! 생성기: `scripts/codegen_riemann_rust.py`")
    lines.append("//! 소스:   `bianchi/generated/riemann_frame.pkl` (sympy, 검증된 심볼 유도)")
    lines.append(f"//! 비영성분 {len(keys)}개, 인자 {len(names)}개, CSE 임시변수 {len(repl)}개.")
    lines.append("//!")
    lines.append("//! 인자 순서 (Python `weyl.pack_state` 와 동일):")
    lines.append("//!   " + ", ".join(names))
    lines.append("")
    lines.append("#![allow(clippy::all)]")
    lines.append("")
    lines.append("/// R^a_bcd 를 평탄 배열 out[a*64+b*16+c*4+d] 에 기록 (먼저 0 으로 채움).")
    lines.append("pub fn riemann_up(p: &[f64; 24], out: &mut [f64; 256]) {")
    # 인자 언팩
    for i, n in enumerate(names):
        lines.append(f"    let {rust_ident(n)} = p[{i}];")
    lines.append("    out.fill(0.0);")
    # CSE 임시변수
    for s, e in repl:
        lines.append(f"    let {s} = {P(e)};")
    # 성분 대입
    for k, e in zip(keys, reduced):
        a, b, c, d = k
        idx = a * 64 + b * 16 + c * 4 + d
        lines.append(f"    out[{idx}] = {P(e)};   // R^{a}_{{{b}{c}{d}}}")
    lines.append("}")
    lines.append("")
    lines.append("/// R_{abcd} = eta_ae R^e_bcd  (eta = diag(-1,1,1,1)) — a=0 행 부호반전.")
    lines.append("pub fn riemann_low(p: &[f64; 24], out: &mut [f64; 256]) {")
    lines.append("    riemann_up(p, out);")
    lines.append("    for i in 0..64 {")
    lines.append("        out[i] = -out[i];")
    lines.append("    }")
    lines.append("}")
    lines.append("")
    return "\n".join(lines) + "\n"


def main():
    src = generate()
    os.makedirs(os.path.dirname(_OUT), exist_ok=True)
    with open(_OUT, "w") as f:
        f.write(src)
    print(f"wrote {_OUT}  ({len(src.splitlines())} lines, {len(src)} bytes)")


if __name__ == "__main__":
    main()
