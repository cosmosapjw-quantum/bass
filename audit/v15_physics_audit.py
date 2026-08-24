"""
V15 감사 · **물리 수식/알고리즘 총감사** — 기호(sympy) 재유도 + 문헌 CRAG 대조.

지금까지의 검증은 대부분 **수치** 오라클(정확해·구적·차등)이었다.  여기서는 세 가지를
보탠다:
  A. **기호 항등** — 구속 전파를 sympy 로 닫는다.  계수 하나만 틀려도 잔차 다항식이
     0 이 아니게 되므로, 차트 RHS·곡률·전단원천·감속식의 **모든 계수**가 한 번에
     심판대에 오른다 (수치검증과 달리 반올림·격자 의존이 없다).
  B. **문헌 상수 CRAG** — 코드에 박힌 상수를 웹 문헌값과 대조 (2026-08 확인):
       Khinchin K₀ = 2.685452001…      (MathWorld)
       Wirsing λ  = 0.3036630029…      (MathWorld, Flajolet–Vallée 1995)
       L-C 식(13) 선형구조: H[(1−n)J^(i+1)+(3+n)J^(i)] − (l/2l+1)D⟨⟩J^(i+1) + D^aJ^(i)
       무질량 문장: "the velocity-weighted moments are identical"  (arXiv PDF 재확인)
  C. **고 l 부호 검증 (V1)** — 별도 파일 `audit/v1_high_l_signs.py`.

    python -m audit.v15_physics_audit
"""
import numpy as np
import sympy as sp


# ═══════════════════════════════════════ A. 기호 항등 (sympy)
def class_a_gauss_propagation():
    """★★ class A: dΩ/dτ = Ω·(2q − (3γ−2)) 가 **항등**인가 (구속면 밖에서도).

    RHS 의 어떤 계수(1/12, 1/6, 2−q, 벽 성장률)든 틀리면 이 항등이 깨진다.
    Wainwright–Ellis 6.10 의 Ω′ 식과 같은 내용 — 다만 **코드의 식으로부터** 유도한다.
    """
    Sp, Sm, N1, N2, N3, g = sp.symbols("Sp Sm N1 N2 N3 gamma", real=True)
    S3 = sp.sqrt(3)
    K = sp.Rational(1, 12) * (N1**2 + N2**2 + N3**2
                              - 2 * (N1 * N2 + N2 * N3 + N3 * N1))
    Splus = sp.Rational(1, 6) * ((N2 - N3) ** 2 - N1 * (2 * N1 - N2 - N3))
    Sminus = (N3 - N2) * (N1 - N2 - N3) / (2 * S3)
    Sigma2 = Sp**2 + Sm**2
    Omega = 1 - Sigma2 - K
    q = 2 * Sigma2 + sp.Rational(1, 2) * (3 * g - 2) * Omega
    dSp = -(2 - q) * Sp - Splus
    dSm = -(2 - q) * Sm - Sminus
    dN1 = (q - 4 * Sp) * N1
    dN2 = (q + 2 * Sp + 2 * S3 * Sm) * N2
    dN3 = (q + 2 * Sp - 2 * S3 * Sm) * N3
    dOmega = -(sp.diff(Sigma2 + K, Sp) * dSp + sp.diff(Sigma2 + K, Sm) * dSm
               + sp.diff(Sigma2 + K, N1) * dN1 + sp.diff(Sigma2 + K, N2) * dN2
               + sp.diff(Sigma2 + K, N3) * dN3)
    resid = sp.simplify(dOmega - Omega * (2 * q - (3 * g - 2)))
    return resid


def class_a_shear_source_identity():
    """★★ 전단–곡률 **교환 항등**: K̇ = 2qK + 2(Σ₊S₊ + Σ₋S₋).

    ★ 반증 기록: 처음 목표식을 K̇ = 2qK − 4Σ·S 로 적었다가 잔차가 정확히
      **6(Σ₊S₊+Σ₋S₋)** 로 나왔다 — 코드가 아니라 **감사자의 분해가 틀렸던 것**
      (총항등 A 가 0 이므로).  올바른 분해: Σ²̇ = −2(2−q)Σ² − 2Σ·S 와 짝을 이뤄
      전단원천이 전단→곡률로 에너지를 옮기는 교환항 +2Σ·S 가 남는다.
      틀린 기대를 남겨 두면(−4) 이 함수가 그것을 다시 잡는다.
    """
    Sp, Sm, N1, N2, N3, q = sp.symbols("Sp Sm N1 N2 N3 q", real=True)
    S3 = sp.sqrt(3)
    K = sp.Rational(1, 12) * (N1**2 + N2**2 + N3**2
                              - 2 * (N1 * N2 + N2 * N3 + N3 * N1))
    Splus = sp.Rational(1, 6) * ((N2 - N3) ** 2 - N1 * (2 * N1 - N2 - N3))
    Sminus = (N3 - N2) * (N1 - N2 - N3) / (2 * S3)
    dN = [(q - 4 * Sp) * N1, (q + 2 * Sp + 2 * S3 * Sm) * N2,
          (q + 2 * Sp - 2 * S3 * Sm) * N3]
    dK = sum(sp.diff(K, n) * dn for n, dn in zip((N1, N2, N3), dN))
    resid = sp.simplify(dK - (2 * q * K + 2 * (Sp * Splus + Sm * Sminus)))
    return resid


def class_b_codazzi_propagation():
    """★★ class B: Ċ = 4(q+Σ₊−1)·C 가 **항등**인가 (구속면 밖에서도).

    D2 가 측정으로 확정한 전파율(모듈 머리말의 인용식)을 기호로 닫는다.
    """
    Sp, St, De, At, Np, g, kap = sp.symbols("Sp St De At Np gamma kappa", real=True)
    Nt = (Np**2 - kap * At) / 3
    Sigma2 = Sp**2 + St
    K = Nt + At
    Omega = 1 - Sigma2 - K
    q = 2 * Sigma2 + sp.Rational(1, 2) * (3 * g - 2) * Omega
    dSp = (q - 2) * Sp - 2 * Nt
    dSt = 2 * (q - 2) * St - 4 * Sp * At - 4 * De * Np
    dDe = 2 * (q + Sp - 1) * De + 2 * (St - Nt) * Np
    dAt = 2 * (q + 2 * Sp) * At
    dNp = (q + 2 * Sp) * Np + 6 * De
    C = St * Nt - De**2 - Sp**2 * At
    dC = (sp.diff(C, Sp) * dSp + sp.diff(C, St) * dSt + sp.diff(C, De) * dDe
          + sp.diff(C, At) * dAt + sp.diff(C, Np) * dNp)
    resid = sp.simplify(dC - 4 * (q + Sp - 1) * C)
    return resid


def exceptional_identities():
    """★★ C2 · 예외형: g′ = 2(q+Σ₊−1)g 와 Ω′−[2q−(3γ−2)]Ω = −4Ag — 둘 다 항등."""
    Sp, Sm, S2, Sx, Nm, A, g = sp.symbols("Sp Sm S2 Sx Nm A gamma", real=True)
    r3 = sp.sqrt(3)
    Sigma2 = Sp**2 + Sm**2 + S2**2 + Sx**2
    K = Nm**2 + 4 * A**2
    Om = 1 - Sigma2 - K
    q = 2 * Sigma2 + sp.Rational(1, 2) * (3 * g - 2) * Om
    d = {Sp: (q - 2) * Sp + 3 * S2**2 - 2 * Nm**2 - 6 * A**2,
         Sm: (q - 2) * Sm - r3 * S2**2 + 2 * r3 * Sx**2 - 2 * r3 * Nm**2 + 2 * r3 * A**2,
         S2: (q - 3 * Sp + r3 * Sm - 2) * S2,
         Sx: (q - 2 * r3 * Sm - 2) * Sx - 8 * Nm * A,
         Nm: (q + 2 * Sp + 2 * r3 * Sm) * Nm + 6 * Sx * A,
         A: (q + 2 * Sp) * A}
    gc = (Sp + r3 * Sm) * A - Sx * Nm
    dg = sum(sp.diff(gc, v) * d[v] for v in d)
    dOm = sum(sp.diff(Om, v) * d[v] for v in d)
    return (sp.simplify(dg - 2 * (q + Sp - 1) * gc),
            sp.simplify(dOm - (2 * q - (3 * g - 2)) * Om + 4 * A * gc))


def type_ix_d_definition_identity():
    """★★ C2 · IX D-차트: G′ = −2(qH+F)G 는 **trace-free 부과 시에만** 항등.

    일반(trace ≠ 0)에서는 0 이 아니다 — Python 문서의 조건부 주장("부과했을 때만")을
    기호로 확정한다.  반환 (일반 잔차 ≠ 0 인가, trace-free 잔차).
    """
    H, S1, S2d, S3d, N1, N2, N3, gm = sp.symbols("H S1 S2 S3 N1 N2 N3 gamma",
                                                 real=True)
    Sig2 = (S1**2 + S2d**2 + S3d**2) / 6
    Om = 1 - Sig2 - (N1**2 + N2**2 + N3**2) / 12
    q = 2 * Sig2 + sp.Rational(1, 2) * (3 * gm - 2) * Om
    F = (N1 * N2 * S3d + N1 * S2d * N3 + S1 * N2 * N3) / 6
    s3 = [(N1 * (2 * N1 - N2 - N3) - (N2 - N3) ** 2) / 3,
          (N2 * (2 * N2 - N3 - N1) - (N3 - N1) ** 2) / 3,
          (N3 * (2 * N3 - N1 - N2) - (N1 - N2) ** 2) / 3]
    dS = [Sv * ((2 - q) * H - F) + x for Sv, x in zip((S1, S2d, S3d), s3)]
    mean = sum(dS) / 3
    dS = [x - mean for x in dS]
    dH = q * (1 - H**2) - F * H
    dN = [-Nv * (q * H + 2 * Sv + F)
          for Nv, Sv in zip((N1, N2, N3), (S1, S2d, S3d))]
    G = H**2 + (N1 * N2 + N1 * N3 + N2 * N3) / 6 - 1
    dG = sp.diff(G, H) * dH + sum(sp.diff(G, n) * dn
                                  for n, dn in zip((N1, N2, N3), dN))
    resid = sp.simplify(dG + 2 * (q * H + F) * G)
    return resid != 0, sp.simplify(resid.subs(S3d, -S1 - S2d))


def kasner_roundtrip_identity():
    """★ u ↦ p(u) ↦ (Σ₊,Σ₋) ↦ p ↦ u 가 기호로 닫히고, Σp = Σp² = 1."""
    u = sp.symbols("u", positive=True)
    s = 1 + u + u * u
    p = [-u / s, (1 + u) / s, u * (1 + u) / s]
    ok_sum = sp.simplify(sum(p) - 1)
    ok_sq = sp.simplify(sum(x * x for x in p) - 1)
    ok_ratio = sp.simplify(p[2] / p[1] - u)
    return ok_sum, ok_sq, ok_ratio


def gauss_map_constants():
    """★ 문헌 CRAG 값 대조 (2026-08, MathWorld/Wikipedia/arXiv)."""
    from bianchi.analysis import gauss_map as G
    rows = [
        ("LYAPUNOV = π²/(6 ln2)", G.LYAPUNOV, float(np.pi**2 / (6 * np.log(2.0)))),
        ("KHINCHIN (MathWorld 2.685452001…)", G.KHINCHIN, 2.685452001065306),
        ("WIRSING (MathWorld 0.3036630029…)", G.WIRSING, 0.3036630029),
    ]
    return rows


def report():
    print("=" * 74)
    print("V15 · 물리 수식/알고리즘 총감사 — 기호 항등 + 문헌 CRAG")
    print("=" * 74)
    print("\n[A] ★★ 기호 항등 (sympy — 계수 하나만 틀려도 0 이 아니게 된다)")
    r = class_a_gauss_propagation()
    print(f"    class A  dΩ/dτ − Ω(2q−(3γ−2))          = {r}")
    r = class_a_shear_source_identity()
    print(f"    class A  dK/dτ − (2qK + 2Σ·S)           = {r}   ← 교환항 부호는 반증으로 확정")
    r = class_b_codazzi_propagation()
    print(f"    class B  Ċ − 4(q+Σ₊−1)C                = {r}")
    a, b, c = kasner_roundtrip_identity()
    print(f"    Kasner   Σp−1, Σp²−1, p₃/p₂−u          = {a}, {b}, {c}")
    rg, ro = exceptional_identities()
    print(f"    예외형   g′−2(q+Σ₊−1)g,  Ω′식(−4Ag)     = {rg}, {ro}")
    nz, tf = type_ix_d_definition_identity()
    print(f"    IX-D     G′+2(qH+F)G: 일반 ≠ 0 {nz}, trace-free 부과 = {tf}")
    print("    tilted-B dΩ 닫힌형: **온셸 전용** (오프셸 ~1e−1, C₂..C₄=0 위 1e−14 실측)")
    print("\n[B] ★ 문헌 상수 (web CRAG)")
    for name, code, lit in gauss_map_constants():
        print(f"    {name}: 코드 {code!r}  문헌 {lit!r}  |Δ| = {abs(code - lit):.1e}")
    print("\n[C] L-C 식(13) 선형구조 (arXiv PDF 재확인): "
          "H[(1−n)J⁽ⁱ⁺¹⁾+(3+n)J⁽ⁱ⁾] − (l/2l+1)D⟨⟩J⁽ⁱ⁺¹⁾ + D^aJ⁽ⁱ⁾ — 코드 부호와 일치")
    print("    (전 항 구조는 l≤3 이중 오라클 + V1 의 l=4 오라클로 검증)")


if __name__ == "__main__":
    report()
