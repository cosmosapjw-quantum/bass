"""
F2 · 정확해 매트릭스의 **기호 유도** (경로 1: sympy; 경로 2: Wolfram — PR-STATUS 기록).

차트 RHS 를 sympy 로 재구성해 (i) 평형점을 **풀고** (ii) 동적 닫힌형(제1적분)을
**미분으로 검증**한다.  참조값은 암기·문헌 인용이 아니라 여기서 유도된 것만
`bianchi/exact.py` 에 실린다 (오라클-대조 원칙).  기존 audit/d_tilted_II.py 의
cs_state 하드코드 (Σ₊=(3γ−2)/8, N₁²=9(2−γ)(3γ−2)/16) 는 이 유도의 대조 대상.

class_a (Σ₊,Σ₋,N₁,N₂,N₃):
    Σ₊' = (q−2)Σ₊ − S₊,  S₊ = [(N₂−N₃)² − N₁(2N₁−N₂−N₃)]/6
    Σ₋' = (q−2)Σ₋ − S₋,  S₋ = (N₃−N₂)(N₁−N₂−N₃)/(2√3)
    N₁' = (q−4Σ₊)N₁,  N₂' = (q+2Σ₊+2√3Σ₋)N₂,  N₃' = (q+2Σ₊−2√3Σ₋)N₃
    K = [ΣNᵢ² − 2(N₁N₂+N₂N₃+N₃N₁)]/12,  Ω=1−Σ²−K,  q=2Σ²+(3γ−2)Ω/2

class_b (Σ₊,Σ̃,Δ,Ã,N₊; κ):
    Σ₊' = (q−2)Σ₊ − 2Ñ            Σ̃' = 2(q−2)Σ̃ − 4Σ₊Ã − 4ΔN₊
    Δ'  = 2(q+Σ₊−1)Δ + 2(Σ̃−Ñ)N₊  Ã' = 2(q+2Σ₊)Ã   N₊' = (q+2Σ₊)N₊ + 6Δ
    Ñ = (N₊²−κÃ)/3,  K = Ñ+Ã
"""
from __future__ import annotations

import sympy as sp

g, k = sp.symbols("gamma kappa", real=True)
Sp, Sm, N1, N2, N3 = sp.symbols("Sigma_p Sigma_m N1 N2 N3", real=True)
St, De, At, Np = sp.symbols("Sigma_t Delta A_t N_p", real=True)
SQ3 = sp.sqrt(3)


def rhs_class_a():
    Sig2 = Sp**2 + Sm**2
    K = (N1**2 + N2**2 + N3**2 - 2*(N1*N2 + N2*N3 + N3*N1)) / 12
    Om = 1 - Sig2 - K
    q = 2*Sig2 + sp.Rational(1, 2)*(3*g - 2)*Om
    S_p = ((N2 - N3)**2 - N1*(2*N1 - N2 - N3)) / 6
    S_m = (N3 - N2)*(N1 - N2 - N3) / (2*SQ3)
    return dict(
        Sigma_p=(q - 2)*Sp - S_p,
        Sigma_m=(q - 2)*Sm - S_m,
        N1=(q - 4*Sp)*N1,
        N2=(q + 2*Sp + 2*SQ3*Sm)*N2,
        N3=(q + 2*Sp - 2*SQ3*Sm)*N3,
    ), dict(Omega=Om, q=q, K=K)


def rhs_class_b():
    Nt = (Np**2 - k*At) / 3
    Sig2 = Sp**2 + St
    Om = 1 - Sig2 - Nt - At
    q = 2*Sig2 + sp.Rational(1, 2)*(3*g - 2)*Om
    return dict(
        Sigma_p=(q - 2)*Sp - 2*Nt,
        Sigma_t=2*(q - 2)*St - 4*Sp*At - 4*De*Np,
        Delta=2*(q + Sp - 1)*De + 2*(St - Nt)*Np,
        A_t=2*(q + 2*Sp)*At,
        N_p=(q + 2*Sp)*Np + 6*De,
    ), dict(Omega=Om, q=q, N_tilde=Nt)


# ---------------------------------------------------------------- 평형점 (solve)
def collins_stewart_II():
    """CS(II): N₁≠0, N₂=N₃=0, Σ₋=0 인 완전유체 평형점 — Σ₊, N₁²(γ) 를 푼다."""
    f, aux = rhs_class_a()
    sub = {Sm: 0, N2: 0, N3: 0}
    eqs = [sp.simplify(f["Sigma_p"].subs(sub)),
           sp.simplify((f["N1"] / N1).subs(sub))]     # N₁≠0 → 괄호=0
    sols = sp.solve(eqs, [Sp, N1], dict=True)
    out = []
    for s in sols:
        if s.get(N1) == 0 or s[N1].could_extract_minus_sign():
            continue
        om = sp.simplify(aux["Omega"].subs(sub).subs(s))
        out.append(dict(Sigma_p=sp.simplify(s[Sp]),
                        N1_sq=sp.factor(sp.simplify(s[N1]**2)), Omega=om))
    return out


def collins_VIh():
    """Collins VI_h: class_b {Δ=N₊=0} 불변부분면 위 완전유체 평형점 (Ã≠0)."""
    f, aux = rhs_class_b()
    sub = {De: 0, Np: 0}
    eqs = [sp.simplify(f["Sigma_p"].subs(sub)),
           sp.simplify(sp.cancel(f["Sigma_t"].subs(sub) / 2)),
           sp.simplify((f["A_t"] / At).subs(sub) / 2)]  # Ã≠0 → q+2Σ₊=0
    sols = sp.solve(eqs, [Sp, St, At], dict=True)
    out = []
    for s in sols:
        if s.get(At, 0) == 0:
            continue
        full = {**sub, **s}
        om = sp.simplify(aux["Omega"].subs(full))
        out.append({str(v): sp.factor(sp.simplify(x)) for v, x in s.items()}
                   | {"Omega": sp.factor(om)})
    return out


def milne_V():
    """Milne: class_b κ=0, Σ₊=Σ̃=Δ=N₊=0 — Ã 를 푼다 (Ã'/Ã=0 ⇒ q=0)."""
    f, _ = rhs_class_b()
    sub = {Sp: 0, St: 0, De: 0, Np: 0, k: 0}
    return sp.solve(sp.simplify((f["A_t"] / At).subs(sub)), At)


def plane_wave_class_b():
    """진공 plane wave 호 (class_b, {Δ=N₊=0}, Ω=0): Σ₊ 를 호 파라미터로 푼다."""
    f, aux = rhs_class_b()
    sub = {De: 0, Np: 0}
    eqs = [sp.simplify(f["Sigma_p"].subs(sub)),
           sp.simplify(f["Sigma_t"].subs(sub)),
           sp.simplify((f["A_t"] / At).subs(sub)),
           sp.simplify(aux["Omega"].subs(sub))]
    return sp.solve(eqs, [St, At, k], dict=True)      # κ(Σ₊) 관계까지 해로
    # (κ 는 파라미터지만, 호가 어떤 κ 에서 사는지가 곧 관계식이다)


def plane_wave_full():
    """★ N₊≠0 포함 **완전** plane wave 족 (Δ=0; Ã≠0 ⇒ q=−2Σ₊; N₊≠0 ⇒ Σ̃=Ñ):
         Σ̃ = Ñ = −Σ₊(1+Σ₊),  Ã = (1+Σ₊)²,  N₊² = (1+Σ₊)[κ(1+Σ₊) − 3Σ₊]
       이면 Ω = 0 이 **자동**이다.  발견: Σ̃≥0 정의역이 Σ₊∈[−1,0] 를 강제하고,
       N₊=0 가지는 κ=3Σ₊/(1+Σ₊)≤0 뿐 — **VII_h(κ>0) plane wave 는 N₊≠0 필수**."""
    f, aux = rhs_class_b()
    sub = {De: 0}
    eqs = [sp.simplify((f["A_t"] / At).subs(sub)),        # q = −2Σ₊
           sp.simplify(f["Sigma_p"].subs(sub)),
           sp.simplify(f["Sigma_t"].subs(sub)),
           sp.simplify((f["Delta"] / (2*Np)).subs(sub))]  # N₊≠0 ⇒ Σ̃ = Ñ
    sols = sp.solve(eqs, [St, At, Np], dict=True)
    out = []
    for s in sols:
        if s.get(At, 0) == 0 or s.get(Np) == 0:
            continue
        om = sp.simplify(aux["Omega"].subs({**sub, **s}))
        out.append({str(v): sp.factor(sp.simplify(x)) for v, x in s.items()}
                   | {"Omega": om,
                      "Np_sq": sp.factor(sp.simplify(s[Np]**2))})
    return out


# ------------------------------------------------- 동적 닫힌형 (제1적분 검증)
def taub_II_first_integrals():
    """진공 type II (N₂=N₃=0, Ω=0, N₁²=12(1−Σ²)):
       (i) L = (2−Σ₊)/Σ₋ 정확 보존 — Taub 점 (2,0) 지나는 직선 궤도.
       (ii) LRS(Σ₋=0): Φ(Σ₊) = −ln(1−Σ₊)/4 + ln(1+Σ₊)/12 + ln(2−Σ₊)/6 에서
            dΦ/dτ = 1  (즉 Φ−τ 가 제1적분).
       둘 다 미분해서 0 을 확인한다."""
    f, _ = rhs_class_a()
    sub_vac = {N2: 0, N3: 0, N1: sp.sqrt(12*(1 - Sp**2 - Sm**2))}
    dSp = sp.simplify(f["Sigma_p"].subs(sub_vac))
    dSm = sp.simplify(f["Sigma_m"].subs(sub_vac))
    L = (2 - Sp)/Sm
    dL = sp.simplify(sp.diff(L, Sp)*dSp + sp.diff(L, Sm)*dSm)
    Phi = -sp.log(1 - Sp)/4 + sp.log(1 + Sp)/12 + sp.log(2 - Sp)/6
    dPhi_dt = sp.simplify((sp.diff(Phi, Sp)*dSp).subs(Sm, 0))
    return dict(dL=dL, dPhi_minus_1=sp.simplify(dPhi_dt - 1),
                dSp_lrs=sp.factor(sp.simplify(dSp.subs(Sm, 0))))


def typeV_vacuum_logistic():
    """진공 type V (Σ₊=Δ=N₊=0, κ=0, Ω=0 ⇒ Ã=1−Σ̃):
       Σ̃' = −4Σ̃(1−Σ̃)  →  Σ̃(τ) = Σ̃₀ / (Σ̃₀ + (1−Σ̃₀)e^{4τ})  (로지스틱).
       RHS 축약 일치 + 닫힌형의 ODE 대입 잔차 = 0 확인."""
    f, _ = rhs_class_b()
    sub = {Sp: 0, De: 0, Np: 0, k: 0, At: 1 - St}
    dSt = sp.simplify(f["Sigma_t"].subs(sub))
    reduced_ok = sp.simplify(dSt - (-4*St*(1 - St)))
    t, S0 = sp.symbols("tau S0", positive=True)
    sol = S0 / (S0 + (1 - S0)*sp.exp(4*t))
    ode_res = sp.simplify(sp.diff(sol, t) + 4*sol*(1 - sol))
    return dict(reduced_ok=reduced_ok, ode_res=ode_res)


def jacobs_disc():
    """γ=2 (stiff): N=0 이면 q=2 가 항등 → Σ-원판 전체가 평형 (Jacobs)."""
    f, aux = rhs_class_a()
    sub = {N1: 0, N2: 0, N3: 0, g: 2}
    return dict(dSp=sp.simplify(f["Sigma_p"].subs(sub)),
                dSm=sp.simplify(f["Sigma_m"].subs(sub)),
                q=sp.simplify(aux["q"].subs(sub)))


def report():
    print("== CS(II):", collins_stewart_II())
    print("== Collins VI_h:", collins_VIh())
    print("== Milne:", milne_V())
    print("== plane wave (N₊=0):", plane_wave_class_b())
    print("== plane wave (완전족):", plane_wave_full())
    print("== Taub II:", taub_II_first_integrals())
    print("== type V logistic:", typeV_vacuum_logistic())
    print("== Jacobs:", jacobs_disc())


if __name__ == "__main__":
    report()
