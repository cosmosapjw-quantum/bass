"""
H5-b · tilted 계층의 ω/u̇ 부호를 **∇_μ T^{μν} = 0 오라클로 확정**한다.

★ 왜 이 오라클이 성립하는가 (구조적 사실):
  식 (12) 의 (l,i) = (0,0) 과 (1,0) 방정식은 **T^{μν} 변수만으로 닫힌다**.
    l=0,i=0 (n=0):  H-항 = 3ρ + J^(1) = 3(ρ+p);  (A),(C),(D),(Ω) 은 l 인자로 소멸;
                     (B) 는 (l−n)=0 이라 J^(−1) 이 죽고 −π_ab σ^ab 만 남는다.
    l=1,i=0 (n=1):  (1−n)J^(1)_a = 0  (★ J^(1)_a 가 소멸한다 — 이게 결정적);
                     (A) 의 (2−2n)=0;  (B) 는 (l−n)=0 **및** (n−1)=0 이라 완전 소멸;
                     (D) = (1/3)[3ρ + 3p]u̇_a = (ρ+p)u̇_a;   (E) = −π_ab u̇^b.
  즉 두 방정식은 (ρ, p, q_a, π_ab) 와 운동학 (H, σ, ω, u̇) 만 포함한다 —
  이것이 바로 에너지·운동량 보존이다.  따라서 보존식을 **독립적으로 유도**하면
  부호를 논문 전사에 의존하지 않고 확정할 수 있다.

★ 통제군(control): 같은 절차가 이미 확정된 SIGN_A = +1, SIGN_B = −1 을 **재생산**해야
  한다.  재생산하면 새 부호 (D, E, Ω) 도 같은 근거로 신뢰할 수 있다.  통제군이 깨지면
  이 오라클 구성 자체를 폐기한다 — 새 부호를 채택하지 않는다.

방법: tilted Bianchi I 계량에서 T^{μν} = (ρ+p)u^μu^ν + p g^{μν} + q^μu^ν + u^μq^ν + π^{μν}
  의 발산을 직접 계산하고 tilted 사틀 성분으로 사영, 무작위 수치 표본에서 부호를
  최소제곱 + 전수 마진으로 푼다.  기억이나 문헌 인용에 의존하지 않는다.

★ 구현 메모: 1차 도함수만 등장하므로 sympy `Function` 대신 **제트 기호**(값 심볼 +
  점심볼)를 쓰고 `lambdify` 한다.  Function/`subs` 판은 표현식이 폭주해 10분에도
  안 끝났다 (측정) — 이 판은 수 초.

부호 규약: 코드가 `out -= SIGN_X * (논문 대괄호식)` 이므로
  SIGN_X = +1 → 논문 부호 그대로,  −1 → 뒤집힘 (부호규약 (+---)→(-+++) 변환).
"""
from __future__ import annotations

import numpy as np
import sympy as sp

# ═══════════════════════════════════════ 0. 제트 기호 (값 + 1차 도함수)
_BASE = ["a1", "a2", "a3", "v1", "v2", "v3", "rho", "p",
         "q1", "q2", "q3", "pi0", "pi1", "pi2", "pi3", "pi4"]
S = {n: sp.Symbol(n, real=True) for n in _BASE}
D1 = {n: sp.Symbol("d" + n, real=True) for n in _BASE}
ARGS = [S[n] for n in _BASE] + [D1[n] for n in _BASE]


def Dt(e):
    """t-도함수 (연쇄율).  ★ 2차 도함수는 이 문제에 등장하지 않는다."""
    e = sp.sympify(e)
    return sp.Add(*[sp.diff(e, S[n]) * D1[n] for n in _BASE])


a = [S["a1"], S["a2"], S["a3"]]
v = [S["v1"], S["v2"], S["v3"]]
rho, prs = S["rho"], S["p"]
qA_sym = [S["q1"], S["q2"], S["q3"]]
pi5 = [S[f"pi{k}"] for k in range(5)]

g = sp.diag(-1, a[0] ** 2, a[1] ** 2, a[2] ** 2)
ginv = sp.diag(-1, 1 / a[0] ** 2, 1 / a[1] ** 2, 1 / a[2] ** 2)

# ═══════════════════════════════════════ 1. 접속 (대각·t-의존 계량의 닫힌형)
GAM = [[[sp.Integer(0)] * 4 for _ in range(4)] for _ in range(4)]
for i in range(3):
    GAM[0][i + 1][i + 1] = a[i] * Dt(a[i])
    GAM[i + 1][0][i + 1] = GAM[i + 1][i + 1][0] = Dt(a[i]) / a[i]

# ═══════════════════════════════════════ 2. tilted 4-속도와 순수 boost 사틀
v2 = v[0] ** 2 + v[1] ** 2 + v[2] ** 2
gam = 1 / sp.sqrt(1 - v2)
#: n^μ = (1,0,0,0),  ê_i = (1/a_i)∂_i  (법선 프레임 정규직교기저)
nup = [sp.Integer(1), sp.Integer(0), sp.Integer(0), sp.Integer(0)]
ehat = [[sp.Integer(0)] * 4 for _ in range(3)]
for i in range(3):
    ehat[i][i + 1] = 1 / a[i]

uup = [gam * nup[m] + gam * sum(v[i] * ehat[i][m] for i in range(3)) for m in range(4)]
udn = [sp.together(sum(g[m, n] * uup[n] for n in range(4))) for m in range(4)]

#: 순수 boost 사틀:  E_A = γv_A n + [δ_AB + (γ−1)v_Av_B/v²] ê_B
#: ★ (γ−1)/v² = γ²/(γ+1) 로 써서 v→0 특이점을 제거한다 (Gram-Schmidt 보다 훨씬 작다).
_k = gam ** 2 / (gam + 1)
EUP = [[gam * v[A] * nup[m]
        + sum((1 if A == B else 0) * ehat[B][m] for B in range(3))
        + _k * v[A] * sum(v[B] * ehat[B][m] for B in range(3))
        for m in range(4)] for A in range(3)]
EDN = [[sum(g[m, n] * E[n] for n in range(4)) for m in range(4)] for E in EUP]

# ═══════════════════════════════════════ 3. 운동학 (H, σ, ω, u̇)
NABLA_U = sp.Matrix(4, 4, lambda m, n: (Dt(udn[n]) if m == 0 else sp.Integer(0))
                    - sum(GAM[l][m][n] * udn[l] for l in range(4)))
THETA = sum(ginv[m, m] * NABLA_U[m, m] for m in range(4))
HUB = THETA / 3
UDOT = [sum(uup[m] * NABLA_U[m, n] for m in range(4)) for n in range(4)]

HMIX = sp.Matrix(4, 4, lambda m, n: (1 if m == n else 0) + uup[m] * udn[n])
HDN = sp.Matrix(4, 4, lambda m, n: g[m, n] + udn[m] * udn[n])
DU = sp.Matrix(4, 4, lambda i, j: sum(HMIX[c, i] * HMIX[d, j] * NABLA_U[c, d]
                                      for c in range(4) for d in range(4)))
SIG_T = sp.Matrix(4, 4, lambda i, j: (DU[i, j] + DU[j, i]) / 2 - HUB * HDN[i, j])
OMG_T = sp.Matrix(4, 4, lambda i, j: (DU[i, j] - DU[j, i]) / 2)

SIG_A = sp.Matrix(3, 3, lambda A, B: sum(EUP[A][m] * EUP[B][n] * SIG_T[m, n]
                                         for m in range(4) for n in range(4)))
OMG_A = sp.Matrix(3, 3, lambda A, B: sum(EUP[A][m] * EUP[B][n] * OMG_T[m, n]
                                         for m in range(4) for n in range(4)))
UDOT_A = [sum(EUP[A][m] * UDOT[m] for m in range(4)) for A in range(3)]

# ═══════════════════════════════════════ 4. T^{μν} 와 발산
PI_AB = [[pi5[0], pi5[2], pi5[3]],
         [pi5[2], pi5[1], pi5[4]],
         [pi5[3], pi5[4], -pi5[0] - pi5[1]]]          # 대칭·무대각합 (5 성분)
QUP = [sum(qA_sym[A] * EUP[A][m] for A in range(3)) for m in range(4)]
PIUP = sp.Matrix(4, 4, lambda m, n: sum(PI_AB[A][B] * EUP[A][m] * EUP[B][n]
                                        for A in range(3) for B in range(3)))
TUP = sp.Matrix(4, 4, lambda m, n: (rho + prs) * uup[m] * uup[n] + prs * ginv[m, n]
                + QUP[m] * uup[n] + uup[m] * QUP[n] + PIUP[m, n])

DIV = [Dt(TUP[0, n])
       + sum(GAM[m][m][l] * TUP[l, n] for m in range(4) for l in range(4))
       + sum(GAM[n][m][l] * TUP[m, l] for m in range(4) for l in range(4))
       for n in range(4)]
ENERGY_CONS = -sum(udn[n] * DIV[n] for n in range(4))
MOM_CONS = [sum(EDN[A][n] * DIV[n] for n in range(4)) for A in range(3)]

# ═══════════════════════════════════════ 5. 계층 쪽 항
RHO_DOT = uup[0] * D1["rho"]                                    # ⊥ρ̇ = u^μ∂_μρ
NAB_Q = sp.Matrix(4, 4, lambda m, n: (Dt(QUP[n]) if m == 0 else sp.Integer(0))
                  + sum(GAM[n][m][l] * QUP[l] for l in range(4)))
QDOT_UP = [sum(HMIX[m, n] * sum(uup[l] * NAB_Q[l, n] for l in range(4))
               for n in range(4)) for m in range(4)]
QDOT_A = [sum(EDN[A][m] * QDOT_UP[m] for m in range(4)) for A in range(3)]

# ── ★ tilted 에서는 공간미분이 **살아난다** (법선합동과의 결정적 차이)
#    균질성은 법선 합동의 초곡면에 대한 것이고 tilted 관측자의 초곡면은 다르다:
#    스칼라조차 D_Aρ = E_A^μ∂_μρ = E_A^t ρ̇ = γ v_A ρ̇ ≠ 0.
#    (이 항을 빼면 최소제곱 잔차가 0.40 남는다 — 측정으로 확인했다.)
QDN = [sum(g[m, n] * QUP[n] for n in range(4)) for m in range(4)]
NAB_QDN = sp.Matrix(4, 4, lambda m, n: (Dt(QDN[n]) if m == 0 else sp.Integer(0))
                    - sum(GAM[l][m][n] * QDN[l] for l in range(4)))
DQ_AB = sp.Matrix(3, 3, lambda A, B: sum(EUP[A][m] * EUP[B][n] * NAB_QDN[m, n]
                                         for m in range(4) for n in range(4)))
DIV_Q = sum(DQ_AB[A, A] for A in range(3))                     # D^a q_a

PIDN = [[sum(g[m, p] * g[n, q] * PIUP[p, q] for p in range(4) for q in range(4))
         for n in range(4)] for m in range(4)]
NAB_PI = [[[(Dt(PIDN[n][l]) if m == 0 else sp.Integer(0))
            - sum(GAM[r][m][n] * PIDN[r][l] for r in range(4))
            - sum(GAM[r][m][l] * PIDN[n][r] for r in range(4))
            for l in range(4)] for n in range(4)] for m in range(4)]
DIV_PI_A = [sum(EUP[B][m] * EUP[B][n] * EUP[A][l] * NAB_PI[m][n][l]
                for B in range(3) for m in range(4) for n in range(4)
                for l in range(4)) for A in range(3)]           # D^b π_{ba}
GRAD_P_A = [EUP[A][0] * D1["p"] for A in range(3)]              # D_a p

# ── 정규직교성 진단 (사틀이 실제로 u 에 직교·정규인지)
ORTHO = [sum(g[m, n] * uup[m] * uup[n] for m in range(4) for n in range(4)) + 1]
for A in range(3):
    ORTHO.append(sum(g[m, n] * uup[m] * EUP[A][n] for m in range(4) for n in range(4)))
    for B in range(3):
        ORTHO.append(sum(g[m, n] * EUP[A][m] * EUP[B][n]
                         for m in range(4) for n in range(4)) - (1 if A == B else 0))

# ═══════════════════════════════════════ 6. lambdify → 수치 표본
_OUT = ([ENERGY_CONS] + MOM_CONS + [RHO_DOT] + QDOT_A + [HUB]
        + [SIG_A[i, j] for i in range(3) for j in range(3)]
        + [OMG_A[i, j] for i in range(3) for j in range(3)]
        + UDOT_A + [DIV_Q] + DIV_PI_A + GRAD_P_A + ORTHO)
_F = sp.lambdify(ARGS, _OUT, "numpy")


def evaluate(vals):
    r = np.asarray(_F(*vals), float)
    k = 0
    def take(n):
        nonlocal k
        out = r[k:k + n]; k += n; return out
    energy = take(1)[0]; mom = take(3); rhod = take(1)[0]; qdot = take(3)
    H_ = take(1)[0]
    sig = take(9).reshape(3, 3); omg = take(9).reshape(3, 3); ud = take(3)
    div_q = take(1)[0]; div_pi = take(3); grad_p = take(3)
    ortho = r[k:]
    return dict(energy=energy, mom=mom, rho_dot=rhod, q_dot=qdot, H=H_,
                sigma=sig, omega=omg, udot=ud, div_q=div_q, div_pi=div_pi,
                grad_p=grad_p, ortho=float(np.abs(ortho).max()))


def _sample(rng, single_axis=False):
    d = {}
    for n in ("a1", "a2", "a3"):
        d[n] = rng.uniform(0.7, 1.4)
    for n in ("v1", "v2", "v3"):
        d[n] = rng.uniform(-0.25, 0.25)
    if single_axis:
        d["v1"] = d["v2"] = 0.0
    d["rho"] = rng.uniform(0.5, 2.0)
    d["p"] = d["rho"] * rng.uniform(0.05, 0.33)
    for n in ("q1", "q2", "q3", "pi0", "pi1", "pi2", "pi3", "pi4"):
        d[n] = rng.uniform(-0.3, 0.3)
    dd = {n: rng.uniform(-0.5, 0.5) for n in _BASE}
    if single_axis:
        dd["v1"] = dd["v2"] = 0.0
    return [d[n] for n in _BASE] + [dd[n] for n in _BASE]


NAMES = ["s_A", "s_B", "s_D", "s_E", "s_Omega", "s_divcon", "s_divfree"]


def build_system(nsamp=80, seed=0, single_axis=False):
    """[보존식] = [계층식(부호 미지)] 를 선형계로.

    미지수 x = (s_A, s_B, s_D, s_E, s_Ω, s_divcon, s_divfree) — 7개.

    ★ l=0 과 l=1 을 **한 계로 합쳐** s_E 를 공유하게 만든다 — 두 다른 방정식이 같은
      s_E 를 주는지가 강한 일관성 시험이다 (따로 풀면 이 정보를 버린다).
    """
    rng = np.random.default_rng(seed)
    rows, rhs, worst_ortho = [], [], 0.0
    for _ in range(nsamp):
        vals = _sample(rng, single_axis)
        d = dict(zip(_BASE, vals[:len(_BASE)]))
        r = evaluate(vals)
        worst_ortho = max(worst_ortho, r["ortho"])
        qv = np.array([d["q1"], d["q2"], d["q3"]])
        pAB = np.array([[d["pi0"], d["pi2"], d["pi3"]],
                        [d["pi2"], d["pi1"], d["pi4"]],
                        [d["pi3"], d["pi4"], -d["pi0"] - d["pi1"]]])
        ud, sig, omg = r["udot"], r["sigma"], r["omega"]
        H_, rho_, p_ = r["H"], d["rho"], d["p"]

        # l=0:  ρ̇ + 3H(ρ+p) + s_dc(D^aq_a) − 2 s_E (q·u̇) − s_B (π:σ)  =  ENERGY
        row = np.zeros(7)
        row[3] = -2.0 * float(qv @ ud)                       # s_E
        row[1] = -float((pAB * sig).sum())                   # s_B
        row[5] = float(r["div_q"])                           # s_divcon
        rows.append(row)
        rhs.append(r["energy"] - r["rho_dot"] - 3.0 * H_ * (rho_ + p_))

        # l=1:  q̇_A + 4H q_A − s_Ω Σ_B q_B ω_AB + s_D(ρ+p)u̇_A
        #                     − s_E Σ_B π_AB u̇_B + s_A Σ_B q_B σ_AB  =  MOM_A
        for A in range(3):
            row = np.zeros(7)
            row[4] = -float(qv @ omg[A])                     # s_Ω
            row[2] = float((rho_ + p_) * ud[A])              # s_D
            row[3] = -float(pAB[A] @ ud)                     # s_E
            row[0] = float(qv @ sig[A])                      # s_A
            row[5] = float(r["div_pi"][A])                   # s_divcon (l=1 에서 공유)
            row[6] = -float(r["grad_p"][A])                  # s_divfree
            rows.append(row)
            rhs.append(r["mom"][A] - r["q_dot"][A] - 4.0 * H_ * qv[A])
    return np.array(rows), np.array(rhs), worst_ortho


def solve_signs(nsamp=80, seed=0, single_axis=False):
    M, b, ortho = build_system(nsamp, seed, single_axis)
    x, *_ = np.linalg.lstsq(M, b, rcond=None)
    resid = float(np.abs(M @ x - b).max())
    return dict(zip(NAMES, x.tolist())), resid, resid / max(np.abs(b).max(), 1e-300), \
        M, b, ortho


def uniqueness_margin(M, b):
    """★ H1 방식 유일성 마진: 2^7 = 128 부호조합 전수 → 최소 잔차 대 차선 비."""
    cand = []
    for mask in range(128):
        s = np.array([1.0 if (mask >> k) & 1 == 0 else -1.0 for k in range(7)])
        cand.append((float(np.abs(M @ s - b).max()), s))
    cand.sort(key=lambda p: p[0])
    margin = cand[1][0] / cand[0][0] if cand[0][0] > 0 else np.inf
    return cand[0], cand[1], margin


def report():
    print("=" * 76)
    print("H5-b · ∇_μT^{μν}=0 오라클로 tilted 부호 확정 (tilted Bianchi I)")
    print("=" * 76)
    sol, resid, rel, M, b, ortho = solve_signs()
    print(f"\n[사틀 정규직교성] max|잔차| = {ortho:.3e}   (u·u=−1, u·E=0, E·E=δ)")
    print("\n[최소제곱해]  ±1 에서 벗어나면 **항 구조가 틀렸다**는 신호")
    for k, val in sol.items():
        tag = "  ← 통제군 (H1 에서 이미 확정)" if k in ("s_A", "s_B") else "  ← 신규"
        print(f"  {k:9s} = {val:+.12f}{tag}")
    print(f"\n[잔차] 절대 {resid:.3e},  상대 {rel:.3e}")

    (r0, s0), (r1, s1), margin = uniqueness_margin(M, b)
    print("\n[유일성 마진] 2^7 = 128 부호조합 전수")
    print("  최적:", dict(zip(NAMES, [int(z) for z in s0])), f"잔차 {r0:.3e}")
    print("  차선:", dict(zip(NAMES, [int(z) for z in s1])), f"잔차 {r1:.3e}")
    print(f"  → 마진 {margin:.4e} 배")

    ctrl = abs(s0[0] - 1.0) < 1e-9 and abs(s0[1] + 1.0) < 1e-9
    print(f"\n[통제군] s_A=+1, s_B=−1 재생산: {'통과 ✓' if ctrl else '실패 ✗'}")
    if not ctrl:
        print("  ★ 실패 → 이 오라클 구성을 신뢰할 수 없다.  새 부호를 채택하지 않는다.")

    print("\n[운동학 진단] tilted Bianchi I 에서 ω_ab 가 정말 0 이 아닌가")
    rng = np.random.default_rng(7)
    r_multi = evaluate(_sample(rng, single_axis=False))
    rng = np.random.default_rng(7)
    r_single = evaluate(_sample(rng, single_axis=True))
    om_m = float(np.abs(r_multi["omega"]).max())
    om_s = float(np.abs(r_single["omega"]).max())
    print(f"  다축 tilt   max|ω_AB| = {om_m:.6e}   max|u̇_A| = {np.abs(r_multi['udot']).max():.6e}")
    print(f"  단일축 tilt max|ω_AB| = {om_s:.6e}   max|u̇_A| = {np.abs(r_single['udot']).max():.6e}")
    if om_s < 1e-12 <= om_m:
        print("  ★ 축정렬 tilt 는 ω 를 켜지 못한다 ⇒ (Ω) 항 시험에는 **다축 tilt 필수**.")
    elif om_m < 1e-12:
        print("  ★ Bianchi I tilted 합동은 비회전(ω≡0) — (Ω) 항은 이 오라클로 확정 불가.")
    else:
        print("  ★ 단일축에서도 ω≠0.")

    # 단일축만으로 풀면 s_Ω 이 결정되지 않는지 확인 (오라클 한계의 정직한 노출)
    if om_s < 1e-12:
        _, _, _, Ms, bs, _ = solve_signs(single_axis=True)
        rank = np.linalg.matrix_rank(Ms, tol=1e-10)
        print(f"  단일축 계의 rank = {rank}/7 → s_Ω 은 다축 표본 없이는 미결정")
    return sol, s0, margin, ctrl


if __name__ == "__main__":
    report()
