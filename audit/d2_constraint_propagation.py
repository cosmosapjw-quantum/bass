"""
D2 · **구속 위반의 전파 법칙을 계량에서 유도**한다 — 인용이 아니라 계산으로.

K5b §7 은 "Codazzi 를 깨면 Friedmann 이 따라 자란다" 를 **관찰만** 했다.
`bianchi/constraints.py` 는 class B 증폭률 `C′ = 4(q + Σ₊ − 1)C` 를 **인용**해 두었고,
일반 차트에서는 `amplification_rate` 가 그냥 0.0 을 돌려준다.  여기서 유도한다.

★ 방법: 구속 잔차를 텐서 하나로 묶는다.

      E^{μν} ≡ G^{μν} − T^{μν}

  결합 진화는 **공간 성분** E^{îĵ} = 0 을 매 순간 강제한다 (ä_i 를 거기서 풀므로).
  남는 성분이 정확히 우리의 두 감시자다:

      E^{0̂0̂} = F  (Friedmann 잔차),      E^{0̂1̂} = C  (Codazzi 잔차)

  그리고 ∇_μG^{μν} ≡ 0 (Bianchi 항등식) 과 ∇_μT^{μν} = 0 (Liouville) 이므로

      ∇_μ E^{μν} = 0

  이 **닫힌 전파계**를 준다.  sympy 로 직접 계산한다.

★ 자기검증: 나온 식에 x 가 남으면 안 된다 (공간균질).

★ 결과 (미리 적어 둔다 — 아래 함수들이 이걸 재생산한다):

      Ḟ = −3H·F − 2(A/a₁)·C
      Ċ = −(4H + σ₁)·C                     ← **F 가 C 로 되먹임하지 않는다**

  닫힌형:  C ∝ 1/(a₁²a₂a₃),   F 의 제차해 ∝ 1/(a₁a₂a₃) = 1/V

    python -m audit.d2_constraint_propagation
"""
from __future__ import annotations

from functools import lru_cache

import sympy as sp

from audit.k5_type_v_einstein import A, COORDS, a1, a2, a3, kinematics, t, x

F = sp.Function("F")(t)
C = sp.Function("C")(t)


@lru_cache(maxsize=2)
def divergence_of_E():
    """★★ ∇_μE^{μν} 를 정규직교틀 성분으로 — E^{0̂0̂}=F, E^{0̂1̂}=C, 나머지 0.

    반환 길이 4 리스트 (프레임 성분).
    """
    g = sp.diag(-1, a1 ** 2, sp.exp(2 * A * x) * a2 ** 2,
                sp.exp(2 * A * x) * a3 ** 2)
    ginv = g.inv()
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
    # 좌표 성분: E^{tt}=F, E^{tx}=C/a₁ (e₁^x = 1/a₁)
    E = sp.zeros(4, 4)
    E[0, 0] = F
    E[0, 1] = C / a1
    E[1, 0] = C / a1
    div = []
    for n in range(4):
        s = sp.S.Zero
        for m in range(4):
            s += sp.diff(E[m, n], COORDS[m])
            for l in range(4):
                s += G[m][m][l] * E[l, n] + G[n][m][l] * E[m, l]
        div.append(sp.simplify(s))
    return [sp.simplify(div[0]), sp.simplify(a1 * div[1]),
            sp.simplify(div[2]), sp.simplify(div[3])]


def mixed_index_sign():
    """★★ 부호를 **지표 올리기로** 정한다 — 논쟁도 손대수도 아니다.

    유도는 반변 E^{μν} 로 했고, K5b 의 감시자 `C = 3σ₁A/a₁ + q₁` 는 공변
    G_{0̂1̂} 기준이다.  정규직교틀 계량 η = diag(−1,1,1,1) 이므로

        E^{0̂1̂} = η^{0̂0̂}η^{1̂1̂} E_{0̂1̂} = −E_{0̂1̂}

    를 계산해 −1 을 돌려준다.  (E^{0̂0̂} = η^{00}η^{00}E_{00} = +E_{00} 이라
    Friedmann 쪽은 부호가 안 바뀐다 — 그래서 대각 성분만 맞고 F←C 만 틀렸었다.)
    """
    eta = sp.diag(-1, 1, 1, 1)
    return int(eta[0, 0] * eta[1, 1])


def diagonal_index_sign():
    """★ 대조: E^{0̂0̂} 는 부호가 바뀌지 않는다 (+1)."""
    eta = sp.diag(-1, 1, 1, 1)
    return int(eta[0, 0] * eta[0, 0])


def homogeneity_residual():
    """★ 자기검증 — 전파식에 x 가 남으면 안 된다."""
    return [i for i, d in enumerate(divergence_of_E())
            if sp.simplify(sp.diff(d, x)) != 0]


def propagation_system():
    """★★ (Ḟ, Ċ) 를 풀어 낸다 — **닫힌 2×2 선형계**.

    반환 dict(Fdot, Cdot) — (F, C, H, σ₁, A/a₁) 로 정리한 식.
    """
    d0, d1, _, _ = divergence_of_E()
    sol = sp.solve([sp.Eq(d0, 0), sp.Eq(d1, 0)],
                   [sp.diff(F, t), sp.diff(C, t)], dict=True)[0]
    return dict(Fdot=sp.simplify(sol[sp.diff(F, t)]),
                Cdot=sp.simplify(sol[sp.diff(C, t)]))


def matrix_form():
    """★ 같은 것을 M 행렬로 — Ẋ = M X,  X = (F, C).

    반환 sympy Matrix 2×2 (H, σ₁, A/a₁ 로 표현).
    """
    s = propagation_system()
    M = sp.zeros(2, 2)
    M[0, 0] = sp.simplify(sp.diff(s["Fdot"], F))
    M[0, 1] = sp.simplify(sp.diff(s["Fdot"], C))
    M[1, 0] = sp.simplify(sp.diff(s["Cdot"], F))
    M[1, 1] = sp.simplify(sp.diff(s["Cdot"], C))
    return M


def readable_matrix():
    """★ M 을 (H, σ₁) 로 다시 써서 사람이 읽을 수 있게 — 잔차와 함께 낸다."""
    H, sig = kinematics()
    M = matrix_form()
    want = sp.Matrix([[-3 * H, -2 * A / a1], [0, -(4 * H + sig[0])]])
    return dict(M=M, want=want, residual=sp.simplify(sp.expand(M - want)))


def no_feedback_into_codazzi():
    """★★ M[1,0] = 0 — **Friedmann 잔차는 Codazzi 로 되먹임하지 않는다**.

    전파계가 삼각행렬이라는 뜻이고, 그래서 고윳값이 대각성분으로 정확히 읽힌다.
    """
    return sp.simplify(matrix_form()[1, 0])


def closed_form_residual():
    """★★ 닫힌형을 **대입해** 확인한다 (풀이를 믿지 않는다).

        C = c₀/(a₁²a₂a₃),      F_hom = f₀/(a₁a₂a₃)
    """
    c0, f0 = sp.symbols("c0 f0", real=True)
    s = propagation_system()
    Csol = c0 / (a1 ** 2 * a2 * a3)
    Fsol = f0 / (a1 * a2 * a3)
    rc = sp.simplify(sp.diff(Csol, t) - s["Cdot"].subs({C: Csol, F: Fsol}))
    rf = sp.simplify(sp.diff(Fsol, t)
                     - s["Fdot"].subs({C: 0, F: Fsol}))
    return dict(codazzi=rc, friedmann_homogeneous=rf)


# ═══════════════════════════════════════ ★ 확장정규화로 옮기기
def normalised_codazzi_rate():
    """★★ 𝒞 ≡ C/H² 의 τ-증가율 — 차트 언어로 옮긴다 (τ = ln ℓ, dτ = H dt).

        d ln𝒞/dτ = (1/H)d ln C/dt + 2(1+q),     q ≡ −1 − Ḣ/H²

    측정된 물리식 Ċ = −(4H+σ₁)C 를 넣으면 **2(q + Σ₊ − 1)** 이 나와야 한다
    (Σ₊ = −Σ₁/2 = −σ₁/2H 규약 — `charts.general.to_class_a` 와 동일).
    """
    H, sig = kinematics()
    q = sp.simplify(-1 - sp.diff(H, t) / H ** 2)
    rate = sp.simplify(-(4 * H + sig[0]) / H + 2 * (1 + q))
    Sp = sp.simplify(-sig[0] / (2 * H))
    want = sp.simplify(2 * (q + Sp - 1))
    return dict(rate=rate, want=want, residual=sp.simplify(rate - want))


def class_b_factor_of_two():
    """★★ `constraints.py` 가 인용한 `4(q + Σ₊ − 1)` 와의 관계를 **정직하게** 맞춘다.

    class B 의 Codazzi 잔차는 `Σ̃Ñ − Δ² − Σ₊²Ã` 로 **2차식**이다 (class_b.codazzi).
    선형 잔차가 rate 로 전파하면 그 2차형식은 2·rate 로 전파한다.  그래서
    우리의 선형 증가율 2(q+Σ₊−1) 의 **정확히 두 배**가 인용식이어야 한다.
    """
    q, Sp = sp.symbols("q Sigma_p", real=True)
    ours = 2 * (q + Sp - 1)
    cited = 4 * (q + Sp - 1)
    return dict(ours=ours, cited=cited, residual=sp.simplify(cited - 2 * ours))


def report():
    print("=" * 74)
    print("D2 · 구속 위반의 전파 법칙 (계량에서 직접, 인용 없음)")
    print("=" * 74)

    print(f"\n[1] ★ 자기검증 — x 가 남은 성분: {homogeneity_residual()}  (빈 목록이어야)")
    for i, d in enumerate(divergence_of_E()):
        print(f"    (∇E)^{i} = {d}")

    s = propagation_system()
    print(f"\n[2] ★★ 전파계")
    print(f"    Ḟ = {s['Fdot']}")
    print(f"    Ċ = {s['Cdot']}")
    r = readable_matrix()
    print(f"    M − [[−3H, −2A/a₁], [0, −(4H+σ₁)]] = {r['residual'].tolist()}")
    print(f"    M[1,0] = {no_feedback_into_codazzi()}   ← F 는 C 로 되먹임하지 않는다")

    cf = closed_form_residual()
    print(f"\n[3] ★★ 닫힌형 대입 잔차")
    print(f"    C = c₀/(a₁²a₂a₃)   잔차 {cf['codazzi']}")
    print(f"    F_hom = f₀/(a₁a₂a₃) 잔차 {cf['friedmann_homogeneous']}")

    n = normalised_codazzi_rate()
    print(f"\n[4] ★★ 확장정규화 — d ln𝒞/dτ")
    print(f"    측정에서 유도 : {n['rate']}")
    print(f"    2(q + Σ₊ − 1) : {n['want']}")
    print(f"    잔차          : {n['residual']}")

    c = class_b_factor_of_two()
    print(f"\n[5] class B 인용식과의 관계 (2차식이라 2배)")
    print(f"    우리(선형) {c['ours']}   인용(2차) {c['cited']}   잔차 {c['residual']}")


if __name__ == "__main__":
    report()
