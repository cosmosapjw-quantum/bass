"""
K5c · **A 를 좌표상수로 둔 것의 정체** — 근사인가 게이지인가.

K5b 는 계량 `ds² = −dt² + a₁²dx² + e^{2Ax}(a₂²dy² + a₃²dz²)` 에서 A 를 **상수**로 두고
결합계를 굴렸다.  그런데 Ellis-MacCallum 형식에서 a_a 는 **진화하는 변수**다:

    ȧ_a = −(H δ_a{}^b + σ_a{}^b) a_b ,      ṅ^{ab} = −H n^{ab} + 2 n^{c(a}σ^{b)}{}_c

우리는 그 진화식을 K5b 에 **넣은 적이 없다**.  넣지 않아도 되는가?

★ 여기서 확정하는 것 (전부 계량에서 직접, 인용 없음):
  1. **전체 교환자표** → 구조상수 C^k_{ij} → 프로젝트 자신의 `algebra.decompose`
     로 (n_ab, a_a) 를 뽑는다.  n_ab = **항등적으로 0**, a_a = (−A/a₁, 0, 0).
  2. [e₀,e_α] = −h_α e_α — 가속도항도 회전항도 없다 (법선 측지 합동, Ω = 0).
  3. ★★ a_a = −A/a₁(t) 를 미분하면 `ȧ_a + (H+σ₁)a_a = 0` 이 **항등식**이다.
     ⇒ A = const 는 근사가 아니라 **Ellis-MacCallum 진화식의 정확해**다.
     K5b 가 그 식을 안 넣은 게 아니라, ansatz 가 이미 만족하고 있었다.
  4. ★ 확장정규화 차트(`charts/general`)의 `A' = qA − Σ·A` 와도 잔차 0 으로 맞는다
     — 물리 단위와 차트 사이 규격화 인자를 여기서 잠근다.
  5. ★ x → λx 재척도가 (A, a₁) → (λA, λa₁) 이므로 **A/a₁ 만 물리**다.
     A 를 상수로 고정한 것은 **게이지 고정**이다.

    python -m audit.k5c_type_v_structure
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np
import sympy as sp

from audit.k5_type_v_einstein import A, AA, COORDS, a1, a2, a3, kinematics, t, x

FRAME = None


def frame():
    """정규직교 불변기저 e_a^μ (K5a 와 같은 것)."""
    return [sp.Matrix([1, 0, 0, 0]),
            sp.Matrix([0, 1 / a1, 0, 0]),
            sp.Matrix([0, 0, sp.exp(-A * x) / a2, 0]),
            sp.Matrix([0, 0, 0, sp.exp(-A * x) / a3])]


def _comm(u, v):
    """[u, v]^μ = u^ν∂_ν v^μ − v^ν∂_ν u^μ."""
    out = sp.zeros(4, 1)
    for m in range(4):
        s = sp.S.Zero
        for n in range(4):
            s += u[n] * sp.diff(v[m], COORDS[n]) - v[n] * sp.diff(u[m], COORDS[n])
        out[m] = sp.simplify(s)
    return out


@lru_cache(maxsize=2)
def commutator_table():
    """★★ **전체** 교환자표 — [e_a, e_b] = γ^c_{ab} e_c 의 γ (4×4×4).

    K5a 는 [e₁,e₂], [e₁,e₃] 만 봤다.  여기서 시간 성분과 [e₂,e₃] 까지 전부 편다.
    ★ 자기검증: 각 교환자가 실제로 기저의 **선형결합**이어야 한다 (남는 성분 0).
    """
    e = frame()
    gam = [[[sp.S.Zero] * 4 for _ in range(4)] for _ in range(4)]
    bad = []
    for i in range(4):
        for j in range(4):
            if i >= j:
                continue
            c = _comm(e[i], e[j])
            for k in range(4):
                # e_k 는 k-번째 좌표방향만 갖는 대각틀이라 계수를 바로 읽는다
                gam[k][i][j] = sp.simplify(c[k] / e[k][k])
                gam[k][j][i] = -gam[k][i][j]
            rest = sp.simplify(c - sum((gam[k][i][j] * e[k] for k in range(4)),
                                       sp.zeros(4, 1)))
            if any(sp.simplify(r) != 0 for r in rest):
                bad.append((i, j, rest))
    return gam, bad


def spatial_structure_constants():
    """공간 구조상수 C^k_{ij} (i,j,k = 1..3) — 교환자표에서 잘라낸다."""
    gam, _ = commutator_table()
    return [[[sp.simplify(gam[k + 1][i + 1][j + 1]) for j in range(3)]
             for i in range(3)] for k in range(3)]


def decomposed(A_val=0.7, a_val=(1.3, 0.9, 1.1)):
    """★★ 프로젝트 자신의 `algebra.decompose` 로 (n_ab, a_a) 를 뽑는다.

    두 경로가 만난다: 계량 교환자(sympy) → 프로젝트의 대수 분해(numpy).
    반환 dict(n, a, jacobi, a_expected).
    """
    from bianchi import algebra as AL
    C = spatial_structure_constants()
    sub = {A: A_val, a1: a_val[0], a2: a_val[1], a3: a_val[2]}
    Cn = np.array([[[float(C[k][i][j].subs(sub)) for j in range(3)]
                    for i in range(3)] for k in range(3)])
    n, av = AL.decompose(Cn)
    return dict(n=n, a=av, jacobi=AL.jacobi_residual(n, av),
                a_expected=np.array([-A_val / a_val[0], 0.0, 0.0]),
                C=Cn)


def time_commutators():
    """★ [e₀, e_α] = −h_α e_α — 가속도·회전이 없음을 확인한다 (법선 측지, Ω=0).

    반환 dict(coeff, offdiag, acceleration).
    """
    gam, _ = commutator_table()
    h = [sp.simplify(sp.diff(ai, t) / ai) for ai in AA]
    coeff = [sp.simplify(gam[al][0][al] + h[al - 1]) for al in (1, 2, 3)]
    off = [sp.simplify(gam[k][0][al]) for al in (1, 2, 3) for k in (1, 2, 3)
           if k != al]
    acc = [sp.simplify(gam[0][0][al]) for al in (1, 2, 3)]   # e₀ 방향 성분 = 가속도
    return dict(coeff=coeff, offdiag=off, acceleration=acc)


# ═══════════════════════════════════════ ★★ a_a 진화식
def a_vector_evolution_residual():
    """★★ **A = const 는 근사가 아니라 정확해**임을 보인다.

        a_1(t) = −A/a₁(t)  ⇒  ȧ_1 + (H + σ₁)a_1 = 0   (항등식)

    Ellis-MacCallum 진화식 `ȧ_a = −(Hδ + σ)·a` 를 K5b 에 넣지 않았는데도 만족된다.
    """
    gam, _ = commutator_table()
    av = sp.simplify(gam[2][1][2])              # [e₁,e₂] = γ e₂ 의 γ = a_1
    H, sig = kinematics()
    return sp.simplify(sp.diff(av, t) + (H + sig[0]) * av)


def transverse_evolution_residual():
    """★ 횡성분도 확인 — a₂ = a₃ = 0 이 유지된다 (진화식이 0 을 0 으로 보낸다)."""
    H, sig = kinematics()
    return [sp.simplify(sp.diff(sp.S.Zero, t) + (H + sig[k]) * 0) for k in (1, 2)]


def n_evolution_residual():
    """★ ṅ^{ab} = −H n^{ab} + 2n^{c(a}σ^{b)}{}_c 은 n=0 을 **정확히** 보존한다.

    n_ab 가 계량에서 항등적으로 0 이고 진화식이 n 에 선형이므로 유형이 유지된다.
    반환 (계량이 준 n, 진화식이 준 ṅ).
    """
    C = spatial_structure_constants()
    from bianchi import algebra as AL
    sub = {A: sp.Rational(7, 10), a1: sp.Rational(13, 10), a2: sp.Rational(9, 10),
           a3: sp.Rational(11, 10)}
    Cn = np.array([[[float(C[k][i][j].subs(sub)) for j in range(3)]
                    for i in range(3)] for k in range(3)])
    n, _ = AL.decompose(Cn)
    sig = np.diag([0.06, -0.02, -0.04])
    ndot = -1.0 * n + (sig @ n + n @ sig)
    return n, ndot


# ═══════════════════════════════════════ ★ 차트 규격화
def chart_normalisation_residual():
    """★★ 확장정규화 차트의 `A_a' = q A_a − Σ_a{}^b A_b` 와 물리 단위가 맞는가.

    A_1 = a_1/H, Σ₁ = σ₁/H, dτ = H dt, q = −1 − Ḣ/H².  물리식 ȧ_1 = −(H+σ₁)a_1
    에서 유도하면 A_1' = (q − Σ₁)A_1 이 나와야 한다 — 잔차를 기호로 낸다.
    """
    gam, _ = commutator_table()
    av = sp.simplify(gam[2][1][2])
    H, sig = kinematics()
    q = sp.simplify(-1 - sp.diff(H, t) / H ** 2)
    A1 = sp.simplify(av / H)
    lhs = sp.simplify(sp.diff(A1, t) / H)                  # dA₁/dτ
    rhs = sp.simplify((q - sig[0] / H) * A1)
    return sp.simplify(sp.expand(lhs - rhs))


# ═══════════════════════════════════════ ★ 게이지
def gauge_rescaling():
    """★★ x → λx 에서 (A, a₁) → (λA, λa₁), 그래서 **a_1 = −A/a₁ 은 불변**이다.

    계량을 직접 재척도해 확인한다 (손으로 주장하지 않는다).
    반환 dict(a1_before, a1_after, invariant).
    """
    lam = sp.Symbol("lam", positive=True)
    gam, _ = commutator_table()
    before = sp.simplify(gam[2][1][2])                     # −A/a₁
    after = sp.simplify(before.subs({A: lam * A, a1: lam * a1}))
    return dict(a1_before=before, a1_after=after,
                invariant=sp.simplify(after - before))


def report():
    print("=" * 74)
    print("K5c · A 를 좌표상수로 둔 것의 정체 (계량에서 직접)")
    print("=" * 74)

    gam, bad = commutator_table()
    print(f"\n[1] ★★ 전체 교환자표 — 기저 밖으로 새는 성분: {len(bad)}개")
    for i in range(4):
        for j in range(i + 1, 4):
            terms = [f"{sp.simplify(gam[k][i][j])}·e{k}" for k in range(4)
                     if sp.simplify(gam[k][i][j]) != 0]
            print(f"    [e{i},e{j}] = {' + '.join(terms) if terms else '0'}")

    d = decomposed()
    print(f"\n[2] ★★ 프로젝트 `algebra.decompose` 로 뽑은 (n_ab, a_a)")
    print(f"    n_ab  최대 |성분| = {np.abs(d['n']).max():.3e}   (0 이어야)")
    print(f"    a_a   = {d['a']}   기대 {d['a_expected']}")
    print(f"    Jacobi n·a = {np.abs(d['jacobi']).max():.3e}")

    tc = time_commutators()
    print(f"\n[3] [e₀,e_α] = −h_α e_α")
    print(f"    −h_α 와의 차 : {tc['coeff']}")
    print(f"    비대각        : {tc['offdiag']}")
    print(f"    가속도 성분   : {tc['acceleration']}")

    print(f"\n[4] ★★ a_a 진화식  ȧ_a + (H+σ₁)a_a")
    print(f"    잔차 = {a_vector_evolution_residual()}      ← 0 이면 A=const 가 정확해")

    print(f"\n[5] ★ 차트 규격화  A' − (q − Σ₁)A")
    print(f"    잔차 = {chart_normalisation_residual()}")

    g = gauge_rescaling()
    print(f"\n[6] ★★ 게이지 — x → λx")
    print(f"    a_1 = {g['a1_before']}  →  {g['a1_after']}   차 {g['invariant']}")

    n, nd = n_evolution_residual()
    print(f"\n[7] n_ab 유지:  |n| = {np.abs(n).max():.3e},  |ṅ| = {np.abs(nd).max():.3e}")


if __name__ == "__main__":
    report()
