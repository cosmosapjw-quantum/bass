"""
F2b · 예외형 VI*_{-1/9} 평형 정확해 + Taub(진공 LRS IX) 축약 — 기호 유도.

경로 1(sympy, 이 파일) + 경로 2(Wolfram, 56차 기록) + 경로 3(γ=1.5 수치 전수
4000-시드 fsolve — 유도가 아니라 **심판**).  세 경로 합치로 닫힌 가족:

  [진공 호]   A = Σ₊+1, Σ₋ = √3(Σ₊+1), Nm = w, Sx = **−w**,
              w = √(−(Σ₊+1)(4Σ₊+3)),  S₂=0,  Σ₊ ∈ (−1, −3/4],  Ω=0 자동.
              ★ 상대부호 Sx=−Nm 필수 — (+w,+w) 는 Nm-식 잔차 **12(Σ₊+1)w**,
                Sx-식 잔차 −16(Σ₊+1)w (Wolfram 적발; 리뷰가 계수 6→12 정정).
  [Collins]   Σ₊=−(3γ−2)/4, Σ₋=−Σ₊/√3, A²=−Σ₊(Σ₊+1)/3, S₂=Sx=Nm=0,
              Ω=(5−3γ)/3 — **F2 의 Collins VI_h 를 κ=−9 로 축약한 것과 정확 일치**
              (독립 게이지 재유도).  존재: Ω>0 ⇔ γ<5/3 (F2 조건 κ<−(3γ−2)/(2−γ)
              의 κ=−9 값과 동치).
  [S₂-진공점] Σ₊=−1/3, Σ₋=1/(3√3), S₂²=5/27, A²=1/6, Sx=Nm=0, Ω=0 — γ-무관.
  [Wainwright γ=10/9 선] Σ₊=−1/3, Σ₋=1/(3√3), Sx=Nm=0, **S₂²=2A²−4/27**,
              A² ∈ [2/27, 1/6] — Collins(A²=2/27, S₂=0)와 S₂-진공점(A²=1/6)을
              잇는 **평형점 선분**.  γ≠10/9 이면 강제식 (6A²−1)(9γ−10)=0 으로
              A²=1/6 만 생존 — 분기값 10/9 가 구조에서 자연 출현 (thresholds.py
              의 "γ=10/9 Wainwright 해" 문서와 독립 합치).

반증 기록:
  · 손축약 CF 라디칼 가지 (Nm≠0, S₂≠0): S₂² = Σ₊(1−2Σ₊)/6 < 0 (Nm²>0 창
    Σ₊∈(−1/2,−1/3) 전역) — **실정의역 공허**, 수치 전수도 부재 확인.  즉
    "Collinson–French" 이름으로 기대했던 Nm≠0 유체 평형 가지는 이 차트의
    평형점이 아니다 (문헌명 단정 대신 측정 성질로 명명하는 이유).
  · 진공 호 (+w,+w) 부호 — 위 참조.

Taub (진공 LRS IX, class_a 차트, Σ₋=0, N₂=N₃=n):
    u ≡ N₁/n:  u' = −6Σ₊u,   Σ₊' = 2(1−Σ₊²)[2(u−1)−Σ₊(u−4)]/(u−4),
    구속  n²·u(u−4) = 12(1−Σ₊²)  (진공 Gauss).  u>4 가 IX 가지.
    ★ 명시 빈칸: 궤도 제1적분의 초등 닫힌형 — sympy dsolve 240s 타임아웃,
      Wolfram DSolve 게이트웨이 오류(말미 재시도).  축약 ODE 자체는 확보라
      게이트는 축약-항등 + 구속 보존으로 세운다.

실행: python -m audit.f2b_exact_derivation
"""
from __future__ import annotations

import sympy as sp

g = sp.symbols("gamma", positive=True)
Sp, Sm, S2, Sx, Nm, A = sp.symbols("Sp Sm S2 Sx Nm A", real=True)
R3 = sp.sqrt(3)


def rhs_exceptional():
    Sig2 = Sp**2 + Sm**2 + S2**2 + Sx**2
    Om = 1 - Sig2 - Nm**2 - 4*A**2
    q = 2*Sig2 + sp.Rational(1, 2)*(3*g - 2)*Om
    f = [
        (q - 2)*Sp + 3*S2**2 - 2*Nm**2 - 6*A**2,
        (q - 2)*Sm - R3*S2**2 + 2*R3*Sx**2 - 2*R3*Nm**2 + 2*R3*A**2,
        (q - 3*Sp + R3*Sm - 2)*S2,
        (q - 2*R3*Sm - 2)*Sx - 8*Nm*A,
        (q + 2*Sp + 2*R3*Sm)*Nm + 6*Sx*A,
        (q + 2*Sp)*A,
    ]
    gc = (Sp + R3*Sm)*A - Sx*Nm
    return f, gc, Om


def vacuum_arc_residuals():
    """진공 호: Sx=−Nm 부호 포함 잔차 전 성분 0 + (+w,+w) 반례 잔차."""
    f, gc, Om = rhs_exceptional()
    w = sp.symbols("w", positive=True)
    sub = {A: Sp + 1, Sm: R3*(Sp + 1), S2: 0, Sx: -w, Nm: w}
    red = [sp.expand(e.subs(sub)).subs(w**2, -(Sp + 1)*(4*Sp + 3)) for e in f]
    good = [sp.factor(sp.simplify(e)) for e in red]
    omv = sp.simplify(sp.expand(Om.subs(sub)).subs(w**2, -(Sp + 1)*(4*Sp + 3)))
    gv = sp.simplify(sp.expand(gc.subs(sub)).subs(w**2, -(Sp + 1)*(4*Sp + 3)))
    bad_sub = {A: Sp + 1, Sm: R3*(Sp + 1), S2: 0, Sx: w, Nm: w}
    bad = sp.factor(sp.simplify(sp.expand(f[4].subs(bad_sub))
                                .subs(w**2, -(Sp + 1)*(4*Sp + 3))))
    return dict(residuals=good, Omega=omv, g=gv, wrong_sign_Nm_eq=bad)


def collins_residuals():
    """Collins(κ=−9 축약): 전 성분 0 + Ω=(5−3γ)/3."""
    f, gc, Om = rhs_exceptional()
    a2 = -Sp*(Sp + 1)/3
    sub = {Sm: -Sp/R3, S2: 0, Sx: 0, Nm: 0, A: sp.sqrt(a2)}
    red = [sp.simplify(e.subs(sub).subs(Sp, -(3*g - 2)/4)) for e in f]
    omv = sp.simplify(Om.subs(sub).subs(Sp, -(3*g - 2)/4))
    return dict(residuals=[sp.simplify(r) for r in red], Omega=sp.factor(omv))


def wainwright_line_residuals():
    """γ=10/9 선: S₂²=2A²−4/27 전체가 평형 + γ≠10/9 강제식 (6A²−1)(9γ−10)∝."""
    f, gc, Om = rhs_exceptional()
    aa = sp.symbols("aa", positive=True)
    sub = {Sp: -sp.Rational(1, 3), Sm: 1/(3*R3), Sx: 0, Nm: 0,
           S2: sp.sqrt(2*aa**2 - sp.Rational(4, 27)), A: aa}
    on_line = [sp.simplify(e.subs(sub).subs(g, sp.Rational(10, 9))) for e in f]
    force = sp.factor(sp.simplify(f[0].subs(sub)))
    s2vac = [sp.simplify(e.subs({Sp: -sp.Rational(1, 3), Sm: 1/(3*R3), Sx: 0,
                                 Nm: 0, S2: sp.sqrt(sp.Rational(5, 27)),
                                 A: 1/sp.sqrt(6)})) for e in f]
    return dict(on_line=on_line, forcing=force, s2_vacuum=s2vac)


def spurious_cf_is_empty():
    """반증 박제: CF 라디칼 가지의 S₂² = Σ₊(1−2Σ₊)/6 은 Nm²>0 창에서 음.
    (전창 기호 증명: Σ₊<0 ∧ 1−2Σ₊>0 ⇒ 곱 음 — 리뷰 MINOR 7a 로 승격.)"""
    s2sq = Sp*(1 - 2*Sp)/6
    whole = sp.simplify(sp.refine(s2sq < 0, sp.Q.negative(Sp)))
    window = [sp.Rational(-9, 20), sp.Rational(-2, 5), sp.Rational(-7, 20)]
    return dict(whole_window=bool(whole is sp.true or whole == True),  # noqa: E712
                samples=[(w, sp.nsimplify(s2sq.subs(Sp, w))) for w in window])


def numeric_census(n_seeds=4000, gamma=1.5, seed=0, tol=1e-11):
    """★ 경로 3 보존 (리뷰 MAJOR 2): 시드 고정 fsolve 전수 — 예외형 (A≠0,
    g=0) 평형점이 알려진 가족 밖에 없는지의 **완전성 심판**.  반환:
    (분류 카운터, 미분류 목록 — 비어 있어야 한다)."""
    import numpy as np
    from scipy.optimize import fsolve
    r3n = float(sp.sqrt(3))
    f_sym, gc_sym, _ = rhs_exceptional()
    vars6 = (Sp, Sm, S2, Sx, Nm, A)
    f_num = sp.lambdify(vars6 + (g,), f_sym, "numpy")
    g_num = sp.lambdify(vars6, gc_sym, "numpy")
    rng = np.random.default_rng(seed)
    hits, unknown = {"vacuum_arc": 0, "collins": 0, "s2_vacuum": 0}, []
    for _ in range(n_seeds):
        x0 = rng.uniform(-0.8, 0.8, 6)
        x, _info, ier, _m = fsolve(lambda v: f_num(*v, gamma), x0,
                                   full_output=True)
        if ier != 1 or np.abs(f_num(*x, gamma)).max() > tol:
            continue
        if abs(x[5]) < 1e-8 or abs(g_num(*x)) > 1e-9:
            continue
        sp_, sm_, s2_, sx_, nm_, a_ = x
        if (abs(s2_) < 1e-7 and abs(nm_) > 1e-7
                and abs(abs(sx_) - abs(nm_)) < 1e-6
                and abs(abs(a_) - (sp_ + 1.0)) < 1e-6
                and abs(abs(sm_) - r3n*(sp_ + 1.0)) < 1e-6):
            hits["vacuum_arc"] += 1
        elif (abs(s2_) < 1e-7 and abs(nm_) < 1e-7 and abs(sx_) < 1e-7
              and abs(sp_ + (3.0*gamma - 2.0)/4.0) < 1e-6):
            hits["collins"] += 1
        elif (abs(sp_ + 1.0/3.0) < 1e-6 and abs(nm_) < 1e-7 and abs(sx_) < 1e-7
              and abs(s2_*s2_ - 5.0/27.0) < 1e-6 and abs(a_*a_ - 1.0/6.0) < 1e-6):
            hits["s2_vacuum"] += 1
        else:
            unknown.append(tuple(np.round(x, 6)))
    return hits, sorted(set(unknown))


def taub_reduction():
    """진공 LRS IX 축약: class_a rhs 에서 (Σ₊,u) 계를 유도·검산.

    정의역 (리뷰 MINOR 6): 진공 Gauss 의 실가지는 u>4 (IX, N 전부 동부호)와
    u<0 (**LRS VIII** — N₁ 반대부호; 분류기 실측 확인) 둘.  0≤u≤4 는 n²≤0
    으로 공허.  u=4 는 축약식의 극 (n²→∞)."""
    u, n = sp.symbols("u n", positive=True)
    S_plus = sp.simplify(((0)**2 - u*n*(2*u*n - 2*n))/6)   # N₂=N₃=n, N₁=un
    K = sp.simplify(((u*n)**2 + 2*n**2 - 2*(u*n*n + n**2 + n*u*n))/12)
    q = 2*Sp**2                                            # 진공
    n2 = 12*(1 - Sp**2)/(u*(u - 4))                        # Ω=0 구속 → n²
    dSp_chart = sp.simplify(((q - 2)*Sp - S_plus).subs(n**2, n2))
    dSp_reduced = 2*(1 - Sp**2)*(2*(u - 1) - Sp*(u - 4))/(u - 4)
    du_chart = sp.simplify(u*((q - 4*Sp) - (q + 2*Sp)))    # u'/u = N₁'/N₁ − n'/n
    return dict(dSp_match=sp.simplify(dSp_chart - dSp_reduced),
                du_match=sp.simplify(du_chart - (-6*Sp*u)),
                K_check=sp.simplify(K.subs(n**2, n2) - (1 - Sp**2)))


def report():
    print("== vacuum arc:", vacuum_arc_residuals())
    print("== collins:", collins_residuals())
    print("== wainwright:", wainwright_line_residuals())
    print("== spurious CF window:", spurious_cf_is_empty())
    print("== taub reduction:", taub_reduction())


if __name__ == "__main__":
    report()
