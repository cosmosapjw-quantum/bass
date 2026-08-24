"""
PR-05 · 검증 오라클 묶음 — 그리고 각 오라클이 **못 잡는 것**.

  A  Omega' 항등식          Omega' = [2q - (3g-2)] Omega
  B  LRS 불변집합           {Sigma_- = 0, N2 = N3} 위에서 Sigma_-' = 0, (N2-N3)' = 0
  C  불변 부분다양체         N_i = 0 보존 (RHS 가 N_i 를 인수로)
  D  축 순환치환 등변성      (1,2,3)->(2,3,1)  <->  (Sigma_+,Sigma_-) 평면 -2pi/3 회전
  E  Kasner 원              진공 I 에서 Sigma_+^2 + Sigma_-^2 = 1 불변
  F  구속 전파              C' = 4(q+Sigma_+-1) C  등

★ 오라클 A 는 커널을 가진다: (dS_+, dS_-) = (Sigma_- f, -Sigma_+ f) 형 오염은
  f 가 무엇이든 통과한다. 이는 프레임 회전항 오전사와 같은 모양이므로, class A /
  Layer 0 에는 B·D·E 를 반드시 함께 걸어야 한다. 이 사실 자체를 테스트로 박제한다
  (inject_kernel + tests/test_oracles.py).
"""
from __future__ import annotations

import random
from itertools import product

from bianchi.optional_dependencies import require_optional

sp = require_optional("sympy", feature=__name__)

I3 = range(3)
R3S = sp.sqrt(3)


# ---------------------------------------------------------------- 헬퍼
def random_zero_check(expr, syms, n=25, seed=17):
    """유리수 랜덤 대입으로 expr == 0 판정 (Schwartz-Zippel)."""
    rng = random.Random(seed)
    for _ in range(n):
        sub = {s: sp.Rational(rng.randint(-19, 19), rng.randint(1, 13)) for s in syms}
        val = sp.cancel(sp.together(sp.sympify(expr).subs(sub)))
        if val != 0 and sp.simplify(val) != 0:
            return False, sp.simplify(val)
    return True, None


def lie_derivative(expr, flow):
    """d/dtau expr,  flow: {sym: dsym}."""
    return sp.expand(sum(sp.diff(expr, v) * dv for v, dv in flow.items()))


# ---------------------------------------------------------------- class A 계 구성
def class_a_system(kernel_f=0, flip_Sm=False, flip_N2=False, ringstrom_K=False):
    """WE class A RHS. 오염 주입 옵션으로 오라클 감도를 시험한다."""
    g = sp.Symbol("gamma")
    Sp, Sm, N1, N2, N3 = sp.symbols("Sigma_p Sigma_m N_1 N_2 N_3")
    kc = sp.Rational(3, 4) if ringstrom_K else sp.Rational(1, 12)
    K = kc * (N1**2 + N2**2 + N3**2 - 2 * (N1*N2 + N2*N3 + N3*N1))
    Om = 1 - Sp**2 - Sm**2 - K
    q = 2 * (Sp**2 + Sm**2) + sp.Rational(1, 2) * (3*g - 2) * Om
    Splus = sp.Rational(1, 6) * ((N2 - N3)**2 - N1*(2*N1 - N2 - N3)) + Sm * kernel_f
    Sminus = (1 / (2*R3S)) * (N3 - N2) * (N1 - N2 - N3) * (-1 if flip_Sm else 1) - Sp * kernel_f
    s2 = 2 * R3S * Sm * (-1 if flip_N2 else 1)
    flow = {
        N1: (q - 4*Sp) * N1,
        N2: (q + 2*Sp + s2) * N2,
        N3: (q + 2*Sp - 2*R3S*Sm) * N3,
        Sp: -(2 - q) * Sp - Splus,
        Sm: -(2 - q) * Sm - Sminus,
    }
    return dict(syms=(Sp, Sm, N1, N2, N3, g), Omega=Om, q=q, K=K, flow=flow)


# ---------------------------------------------------------------- 오라클
def oracle_A_omega(sysd):
    """Omega' = [2q - (3gamma-2)] Omega."""
    g = sysd["syms"][-1]
    Om, q, flow = sysd["Omega"], sysd["q"], sysd["flow"]
    return sp.expand(lie_derivative(Om, flow) - (2*q - (3*g - 2)) * Om)


def oracle_B_lrs(sysd):
    """LRS {Sigma_-=0, N2=N3} 불변."""
    Sp, Sm, N1, N2, N3, g = sysd["syms"]
    sub = {Sm: 0, N3: N2}
    return [
        sp.expand(sysd["flow"][Sm].subs(sub)),
        sp.expand((sysd["flow"][N2] - sysd["flow"][N3]).subs(sub)),
    ]


def oracle_C_invariant_submanifolds(sysd):
    """N_i = 0 이 불변."""
    Sp, Sm, N1, N2, N3, g = sysd["syms"]
    return [sp.simplify(sysd["flow"][Ni].subs(Ni, 0)) for Ni in (N1, N2, N3)]


def oracle_D_cyclic(sysd):
    """축 순환치환 등변성."""
    Sp, Sm, N1, N2, N3, g = sysd["syms"]
    c, s = sp.Rational(-1, 2), R3S / 2
    rot = {Sp: c*Sp - s*Sm, Sm: s*Sp + c*Sm, N1: N2, N2: N3, N3: N1}
    f = sysd["flow"]
    return [
        sp.expand(f[Sp].subs(rot, simultaneous=True) - (c*f[Sp] - s*f[Sm])),
        sp.expand(f[Sm].subs(rot, simultaneous=True) - (s*f[Sp] + c*f[Sm])),
    ]


def oracle_E_kasner(sysd):
    """진공 Bianchi I 에서 Kasner 원 불변."""
    Sp, Sm, N1, N2, N3, g = sysd["syms"]
    vac = {N1: 0, N2: 0, N3: 0}
    kas = Sp**2 + Sm**2 - 1
    d = lie_derivative(kas, sysd["flow"])
    return sp.simplify(d.subs(vac).subs(Sm**2, 1 - Sp**2))


def oracle_F_constraint(constraint, flow, rate):
    """구속 전파: C' = rate * C."""
    return sp.expand(lie_derivative(constraint, flow) - rate * constraint)


# ---------------------------------------------------------------- 커널 실증
def inject_kernel(f=None):
    """오라클 A 의 커널 방향 오염을 주입한 계를 반환.

    (dS_+, dS_-) = (Sigma_- f, -Sigma_+ f) 는 (Sigma_+,Sigma_-) 평면의 회전
    생성자이고 Omega 는 회전 불변량이므로 A 에 보이지 않는다.
    """
    if f is None:
        _, _, N1, N2, N3 = sp.symbols("Sigma_p Sigma_m N_1 N_2 N_3")
        f = N1 * N2 + N3**2
    return class_a_system(kernel_f=f)


ORACLE_BLIND_SPOTS = {
    "A_omega": (
        "회전 생성자 방향 (dS_+,dS_-)=(Sigma_- f, -Sigma_+ f) 오염을 통과시킨다. "
        "이는 프레임 회전항 Sigma'_pm ⊃ ±2 R_1 Sigma_mp 의 오전사와 같은 모양이다. "
        "-> B(LRS), D(순환치환) 을 반드시 함께 걸 것."
    ),
    "class_b_coefficients": (
        "Omega' 와 C' 을 둘 다 걸어도 (b3,c2,c)=(-4s,2s,6s) 스케일 자유도가 남는다. "
        "계수는 오라클이 아니라 **제1원리 유도**만 고정한다."
    ),
    "time_gauge": "dtau = H dt 선택 자체는 어떤 오라클도 검증하지 않는다.",
}
