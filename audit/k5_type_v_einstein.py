"""
K5a · **type V 의 Einstein 텐서를 직접 계산**한다 — 곡률·구속을 인용하지 않는다.

K4c 에서 type V 자유흐름이 법선틀 열유속 q ≠ 0 을 스스로 만든다는 것을 측정했고,
그 q 를 담는 A 를 Codazzi 로 풀었다.  그런데 **Codazzi 식 자체**(3Σ^{ab}A_b = q^a)와
**type V 의 3-곡률**은 아직 문헌 인용 상태다.  결합계를 세우기 전에 확정한다.

★ 방법: 계량

      ds² = −dt² + a₁²(t)dx² + e^{2Ax}[a₂²(t)dy² + a₃²(t)dz²]

  에서 Einstein 텐서를 sympy 로 직접 계산하고 **정규직교 불변기저**로 사영한다:

      e₀ = ∂_t,  e₁ = (1/a₁)∂_x,  e₂ = e^{−Ax}/a₂ ∂_y,  e₃ = e^{−Ax}/a₃ ∂_z

★ 자기검증 (가장 먼저): 사영한 성분이 **x 에 무관**해야 한다 (공간균질).
  하나라도 x 가 남으면 계량·기저 설정이 틀린 것이다 — 그 뒤 계산은 볼 필요가 없다.

★ 대조군: A → 0 에서 K1 의 Bianchi I 결과를 재생산해야 한다.

단위: 8πG = 1 (프로젝트 규약).

    python -m audit.k5_type_v_einstein
"""
from __future__ import annotations

from functools import lru_cache

import sympy as sp

t, x, y, z, A = sp.symbols("t x y z A", real=True)
COORDS = (t, x, y, z)
a1, a2, a3 = (sp.Function(n, positive=True)(t) for n in ("a1", "a2", "a3"))
AA = [a1, a2, a3]


@lru_cache(maxsize=2)
def einstein_frame():
    """★ G_{âb̂} — 정규직교 불변기저 성분 (계량에서 직접).

    반환 sympy Matrix 4×4.
    """
    g = sp.diag(-1, a1 ** 2, sp.exp(2 * A * x) * a2 ** 2,
                sp.exp(2 * A * x) * a3 ** 2)
    ginv = g.inv()
    # 크리스토펠
    G = [[[sp.S.Zero] * 4 for _ in range(4)] for _ in range(4)]
    for r in range(4):
        for m in range(4):
            for n in range(4):
                s = sp.S.Zero
                for k in range(4):
                    s += ginv[r, k] * (sp.diff(g[k, m], COORDS[n])
                                       + sp.diff(g[k, n], COORDS[m])
                                       - sp.diff(g[m, n], COORDS[k]))
                G[r][m][n] = sp.simplify(s / 2)
    # 리치
    Ric = sp.zeros(4, 4)
    for m in range(4):
        for n in range(4):
            s = sp.S.Zero
            for r in range(4):
                s += sp.diff(G[r][m][n], COORDS[r]) - sp.diff(G[r][m][r], COORDS[n])
                for k in range(4):
                    s += G[r][r][k] * G[k][m][n] - G[r][n][k] * G[k][m][r]
            Ric[m, n] = sp.simplify(s)
    Rs = sp.simplify(sum(ginv[m, n] * Ric[m, n] for m in range(4) for n in range(4)))
    Ein = sp.simplify(Ric - Rs * g / 2)
    # 정규직교 불변기저 (반변 성분)
    E = sp.zeros(4, 4)
    E[0, 0] = 1
    E[1, 1] = 1 / a1
    E[2, 2] = sp.exp(-A * x) / a2
    E[3, 3] = sp.exp(-A * x) / a3
    return sp.simplify(E.T * Ein * E)


def homogeneity_residual():
    """★★ 자기검증: 사영 성분이 **x 에 무관**한가 (공간균질).

    하나라도 x 가 남으면 계량·기저 설정이 틀린 것이다.
    반환 x 가 남은 성분 목록 (비어 있어야 정상).
    """
    Gf = einstein_frame()
    bad = []
    for i in range(4):
        for j in range(4):
            if sp.simplify(sp.diff(Gf[i, j], x)) != 0:
                bad.append((i, j, sp.simplify(Gf[i, j])))
    return bad


# ═══════════════════════════════════════ 운동학 (H, Σ) 로 다시 쓰기
def kinematics():
    """H = ⅓Σȧ_i/a_i,  σ_i = ȧ_i/a_i − H  (법선합동, 대각)."""
    hs = [sp.diff(ai, t) / ai for ai in AA]
    H = sum(hs) / 3
    return H, [sp.simplify(h - H) for h in hs]


def friedmann_expression():
    """★ G_{0̂0̂} = ρ 를 (H, σ, A) 로 정리 — **type V 의 Friedmann 구속**.

    Bianchi I 은 3H² = ρ + σ² 였다.  type V 는 곡률항이 붙는다: 얼마인지 **측정**한다.
    반환 sympy 식 (= ρ).
    """
    H, sig = kinematics()
    e = sp.simplify(einstein_frame()[0, 0])
    s2 = sp.simplify(sum(s ** 2 for s in sig) / 2)          # σ² ≡ ½σ_abσ^ab
    return sp.simplify(sp.expand(e))


def friedmann_in_H_sigma_A():
    """★ 같은 식을 3H² + σ² 로 나눈 나머지 — **곡률 계수**를 뽑는다."""
    H, sig = kinematics()
    s2 = sum(s ** 2 for s in sig) / 2
    e = sp.simplify(einstein_frame()[0, 0])
    return sp.simplify(sp.expand(e - 3 * H ** 2 + s2))


def momentum_constraint_expression():
    """★★ G_{0̂1̂} = −q^1 — **Codazzi(운동량) 구속**을 계량에서 직접 얻는다.

    K2b/K4c 가 인용해 쓴 `3Σ^{ab}A_b = q^a` 가 맞는지 여기서 확정한다.
    """
    return sp.simplify(sp.expand(einstein_frame()[0, 1]))


def codazzi_check():
    """★★ G_{0̂1̂} 이 −3σ₁·A/a₁ 꼴인지 — 인용식과 대조한다.

    Σ_ab = σ_ab/H, A_a = (A/a₁, 0, 0)/H 규약이면 3Σ^{ab}A_b|₁ = 3σ₁(A/a₁)/H².
    여기서는 규격화 전 단계(σ, A/a₁)로 비교한다.
    반환 dict(G01, candidate, ratio).
    """
    H, sig = kinematics()
    G01 = momentum_constraint_expression()
    cand = sp.simplify(-3 * sig[0] * A / a1)
    return dict(G01=G01, candidate=cand,
                ratio=sp.simplify(G01 / cand) if cand != 0 else None)


def isotropic_limit():
    """★ 등방 a₁=a₂=a₃=a 에서 open FRW 가 나오는가 (³R = −6A²/a²)."""
    aa = sp.Function("a", positive=True)(t)
    sub = {a1: aa, a2: aa, a3: aa}
    e00 = sp.simplify(einstein_frame()[0, 0].subs(sub).doit())
    e01 = sp.simplify(einstein_frame()[0, 1].subs(sub).doit())
    H = sp.diff(aa, t) / aa
    return dict(G00=e00, G01=e01,
                minus_3H2=sp.simplify(e00 - 3 * H ** 2))


def type_I_limit():
    """★ 대조군: A → 0 에서 Bianchi I 로 환원 (K1 결과 재생산)."""
    H, sig = kinematics()
    s2 = sum(s ** 2 for s in sig) / 2
    e00 = sp.simplify(einstein_frame()[0, 0].subs(A, 0))
    return dict(G00=e00, minus_friedmann=sp.simplify(e00 - 3 * H ** 2 + s2))


def report():
    print("=" * 74)
    print("K5a · type V 의 Einstein 텐서 (계량에서 직접, 인용 없음)")
    print("=" * 74)

    bad = homogeneity_residual()
    print(f"\n[1] ★★ 자기검증 — 사영 성분이 x 에 무관한가")
    print(f"    x 가 남은 성분: {len(bad)}개  {'(정상)' if not bad else bad}")

    print(f"\n[2] Friedmann 구속  G_{{0̂0̂}} = ρ")
    print(f"    G00 = {friedmann_expression()}")
    print(f"    G00 − 3H² + σ² = {friedmann_in_H_sigma_A()}      ← 곡률항")

    print(f"\n[3] ★★ 운동량(Codazzi) 구속  G_{{0̂1̂}} = −q^1")
    c = codazzi_check()
    print(f"    G01        = {c['G01']}")
    print(f"    −3σ₁·A/a₁  = {c['candidate']}")
    print(f"    비          = {c['ratio']}")

    print(f"\n[4] 등방 극한 (open FRW 여야 한다)")
    iso = isotropic_limit()
    print(f"    G00 = {iso['G00']}")
    print(f"    G00 − 3H² = {iso['minus_3H2']}          ← ³R/… 곡률항")
    print(f"    G01 = {iso['G01']}                      ← 등방이면 0 이어야")

    print(f"\n[5] 대조군 — A → 0 에서 Bianchi I")
    ti = type_I_limit()
    print(f"    G00 − (3H² − σ²) = {ti['minus_friedmann']}   (0 이어야)")


if __name__ == "__main__":
    report()


# ═══════════════════════════════════════ 구조상수 — 부호를 측정으로 가른다
def structure_constants():
    """★★ 기저 교환자에서 a_a 를 **직접 계산**한다 (부호 논쟁을 끝낸다).

    프로젝트 규약은 `CODAZZI_G0A_SIGN = −1` 로  G_0a = −(3a_bσ^ab + …) 인데,
    §3 의 측정은 G_{0̂1̂} = +3σ₁(A/a₁) 였다.  어긋나는 이유는 **부호 규약이 아니라
    a_a 의 부호**일 수 있다: 우리 계량이 e^{+2Ax} 이면 [e₁,e₂] = ? 를 재야 한다.

    반환 dict(comm_12, comm_13, a_vector) — a_a 는 정규직교 기저 기준.
    """
    e = [sp.Matrix([1, 0, 0, 0]),
         sp.Matrix([0, 1 / a1, 0, 0]),
         sp.Matrix([0, 0, sp.exp(-A * x) / a2, 0]),
         sp.Matrix([0, 0, 0, sp.exp(-A * x) / a3])]

    def comm(u, v):
        """[u, v]^μ = u^ν∂_ν v^μ − v^ν∂_ν u^μ."""
        out = sp.zeros(4, 1)
        for m in range(4):
            s = sp.S.Zero
            for n in range(4):
                s += u[n] * sp.diff(v[m], COORDS[n]) - v[n] * sp.diff(u[m], COORDS[n])
            out[m] = sp.simplify(s)
        return out

    c12, c13 = comm(e[1], e[2]), comm(e[1], e[3])
    # [e₁,e₂] = λ e₂ 의 λ 를 뽑는다
    lam12 = sp.simplify(c12[2] / e[2][2])
    lam13 = sp.simplify(c13[3] / e[3][3])
    # Ellis-MacCallum: [e₁, e_α] = a e_α  (α = 2,3)  ⇒  a_a = (a, 0, 0)
    return dict(lam12=lam12, lam13=lam13, a_vector=(lam12, sp.S.Zero, sp.S.Zero))


def spatial_einstein_symbols():
    """★★ 공간 대각 성분을 **평면 기호**로 — G_{îî}(a_i, h_i, u_i, A).

    Derivative 를 h_i ≡ ȧ_i/a_i, u_i ≡ ä_i/a_i 로 치환한다 (2계 → 1계 → 함수 순서).
    K5b 의 `accelerations` 가 이 식을 왕복으로 재검증하는 데 쓴다.
    """
    h = sp.symbols("h1 h2 h3", real=True)
    u = sp.symbols("u1 u2 u3", real=True)
    s = sp.symbols("s1 s2 s3", positive=True)
    Gf = einstein_frame()
    sub2 = {sp.diff(AA[i], t, 2): u[i] * AA[i] for i in range(3)}
    sub1 = {sp.diff(AA[i], t): h[i] * AA[i] for i in range(3)}
    sub0 = {AA[i]: s[i] for i in range(3)}
    out = []
    for i in range(1, 4):
        e = sp.simplify(Gf[i, i]).subs(sub2).subs(sub1).subs(sub0)
        out.append(sp.simplify(e))
    return dict(G=out, a=s, h=h, u=u, A=A)


def spatial_einstein_numeric():
    """★ 위 식의 수치판 — `G(a, h, u, A)` 를 반환 (배열 3개)."""
    d = spatial_einstein_symbols()
    f = sp.lambdify((d["a"], d["h"], d["u"], d["A"]), d["G"], "numpy")

    def G(a, h, u, Aval):
        return [float(v) for v in f(tuple(a), tuple(h), tuple(u), float(Aval))]
    return G


def codazzi_normalisation():
    """★★ 측정된 a_a 로 프로젝트 규약이 실제로 맞는지 확인한다.

        규약:  G_0a = CODAZZI_G0A_SIGN · 3 a_b σ^{ab}      (N = 0)
    """
    from bianchi.conventions import CODAZZI_G0A_SIGN
    H, sig = kinematics()
    av = structure_constants()["a_vector"][0]
    lhs = momentum_constraint_expression()                 # G_{0̂1̂}
    rhs = sp.simplify(CODAZZI_G0A_SIGN * 3 * av * sig[0])
    return dict(G01=sp.simplify(lhs), rule=rhs,
                residual=sp.simplify(sp.expand(lhs - rhs)),
                a_1=av, sign=CODAZZI_G0A_SIGN)
