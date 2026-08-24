"""
PR-45 · 프레임 Riemann/Weyl 코드 생성기.

audit/einstein_frame.py 의 심볼릭 프레임 Riemann (jacobi 대입 후) 을 pickle 로
직렬화한다.  성분은 (H, N, A, σ, R, Ḣ, σ̇) 의 유리식이며 (Ṙ, Ṅ, Ȧ 는 Jacobi 로
소거되거나 게이지로 탈락), 좌표계 검산(D16, 잔차 2.8e-14)으로 검증된 것과 동일하다.

    python -m bianchi.rays.generate_weyl   ->  bianchi/generated/riemann_frame.pkl

weyl.py 가 이 pickle 을 unpickle 하여 JAX 함수로 lambdify 한다 (심볼릭 재빌드는
~1분이므로 생성은 1회, 로드는 수초).
"""
from __future__ import annotations

import os
import pickle
import sys


def build_and_pickle(out_path=None):
    # audit/ 를 경로에 추가하여 einstein_frame 재사용
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(os.path.dirname(here))
    audit = os.path.join(root, "audit")
    if audit not in sys.path:
        sys.path.insert(0, audit)
    import sympy as sp
    from einstein_frame import einstein, t, I4

    m = einstein(with_rotation=True)
    Riem, H, n, a, s, R = m["Riem"], m["H"], m["n"], m["a"], m["s"], m["R"]
    Hd = sp.Derivative(H, t)
    sd = [sp.Derivative(s[i, j], t) for i, j in ((0, 0), (0, 1), (0, 2), (1, 1), (1, 2))]

    # 순서 고정된 심볼 리스트 (플레인 심볼로 치환하여 pickle/lambdify 안전화)
    fun_syms = ([H] + [n[0, 0], n[0, 1], n[0, 2], n[1, 1], n[1, 2], n[2, 2]]
                + [a[0], a[1], a[2]]
                + [s[0, 0], s[0, 1], s[0, 2], s[1, 1], s[1, 2]]
                + [R[0], R[1], R[2]] + [Hd] + sd)
    names = (["H", "n00", "n01", "n02", "n11", "n12", "n22",
              "a0", "a1", "a2", "s00", "s01", "s02", "s11", "s12",
              "R0", "R1", "R2", "Hd", "sd00", "sd01", "sd02", "sd11", "sd12"])
    plain = [sp.Symbol(nm) for nm in names]
    repl = dict(zip(fun_syms, plain))

    comps = {}
    for A in I4:
        for B in I4:
            for C in I4:
                for D in I4:
                    e = sp.sympify(Riem[A][B][C][D])
                    e = sp.expand(e).subs(repl, simultaneous=True)
                    if e != 0:
                        comps[(A, B, C, D)] = e

    payload = dict(names=names, components={k: sp.srepr(v) for k, v in comps.items()})
    if out_path is None:
        gen_dir = os.path.join(root, "bianchi", "generated")
        os.makedirs(gen_dir, exist_ok=True)
        out_path = os.path.join(gen_dir, "riemann_frame.pkl")
    with open(out_path, "wb") as f:
        pickle.dump(payload, f)
    return out_path, len(comps)


if __name__ == "__main__":
    path, ncomp = build_and_pickle()
    print(f"wrote {path}  ({ncomp} nonzero Riemann components)")
