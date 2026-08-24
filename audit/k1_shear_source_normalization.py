"""
K1 · 차트의 Π 규격화를 **Einstein 방정식에서 직접 확정**한다.

`charts/general.py` 는  Σ'_ab = −(2−q)Σ_ab − ³S_ab + **Π_ab** + [W,Σ]  로 쓰는데,
Π 가 π_ab 를 어떻게 규격화한 것인지(π/H², π/(3H²), ½π/H² …)는 문헌마다 갈린다.
계층이 주는 π_ab 를 이 훅에 꽂으려면 **계수를 정확히 알아야** 한다.

★ 방법: 추측하거나 문헌을 인용하지 않고, Bianchi I 계량에서 Einstein 텐서를 직접
  계산해 공간 무대각합 방정식의 π 계수를 **측정**한다.  H5-b 의 제트기호+lambdify
  기법을 그대로 쓴다 (1·2차 도함수만 등장).

★ 통제군: 같은 계산이 **Friedmann 구속** (G^0_0 = ρ ⇒ 3H² = ρ + σ²…) 과
  **Raychaudhuri** 를 재생산해야 한다.  재생산하지 못하면 Einstein 텐서 구성 자체를
  신뢰할 수 없으므로 Π 계수도 채택하지 않는다.

단위: 8πG = 1 (프로젝트 규약 — Ω ≡ ρ/(3H²) 이 평탄에서 1 이 되려면 3H² = ρ).
"""
from __future__ import annotations

import numpy as np
import sympy as sp

# ═══════════════════════════════════════ 제트 기호 (값 + 1·2차 도함수)
_B = ["a1", "a2", "a3"]
S = {n: sp.Symbol(n, positive=True) for n in _B}
D1 = {n: sp.Symbol("d" + n, real=True) for n in _B}
D2 = {n: sp.Symbol("dd" + n, real=True) for n in _B}
ARGS = [S[n] for n in _B] + [D1[n] for n in _B] + [D2[n] for n in _B]


def Dt(e):
    """t-도함수 — a → ȧ → ä 까지 (Einstein 텐서에 2차가 등장한다)."""
    e = sp.sympify(e)
    return sp.Add(*[sp.diff(e, S[n]) * D1[n] + sp.diff(e, D1[n]) * D2[n]
                    for n in _B])


a = [S["a1"], S["a2"], S["a3"]]
g = sp.diag(-1, a[0] ** 2, a[1] ** 2, a[2] ** 2)
ginv = sp.diag(-1, 1 / a[0] ** 2, 1 / a[1] ** 2, 1 / a[2] ** 2)

# ═══════════════════════════════════════ 접속 → 리만 → 아인슈타인
GAM = [[[sp.Integer(0)] * 4 for _ in range(4)] for _ in range(4)]
for i in range(3):
    GAM[0][i + 1][i + 1] = a[i] * Dt(a[i])
    GAM[i + 1][0][i + 1] = GAM[i + 1][i + 1][0] = Dt(a[i]) / a[i]


def riemann():
    """R^ρ_{σμν} = ∂_μΓ^ρ_{νσ} − ∂_νΓ^ρ_{μσ} + ΓΓ − ΓΓ.  공간미분은 0 (균질)."""
    R = [[[[sp.Integer(0)] * 4 for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for r in range(4):
        for s in range(4):
            for m in range(4):
                for n in range(4):
                    t = sp.Integer(0)
                    if m == 0:
                        t += Dt(GAM[r][n][s])
                    if n == 0:
                        t -= Dt(GAM[r][m][s])
                    for l in range(4):
                        t += GAM[r][m][l] * GAM[l][n][s]
                        t -= GAM[r][n][l] * GAM[l][m][s]
                    R[r][s][m][n] = t
    return R


RIEM = riemann()
RIC = sp.Matrix(4, 4, lambda s, n: sum(RIEM[r][s][r][n] for r in range(4)))
RSCAL = sum(ginv[m, m] * RIC[m, m] for m in range(4))
EIN = sp.Matrix(4, 4, lambda m, n: RIC[m, n] - RSCAL * g[m, n] / 2)

# ═══════════════════════════════════════ 운동학 (법선 합동 u = ∂_t)
Hi = [Dt(a[i]) / a[i] for i in range(3)]           # 방향 Hubble
THETA = sum(Hi)
HUB = THETA / 3
SIG = [Hi[i] - HUB for i in range(3)]              # σ^i_i (무대각합)
SIG2 = sum(s ** 2 for s in SIG) / 2                # σ² ≡ ½σ_abσ^ab

# 정규직교틀 성분:  G_{\hat i \hat j} = G_{ij}/a_i a_j (대각)
G_ORTHO = [EIN[i + 1, i + 1] / a[i] ** 2 for i in range(3)]
G_00 = EIN[0, 0]

# ═══════════════════════════════════════ 측정 대상
#: Friedmann 구속 (통제군):  G_00 = ρ  ⇒  3H² = ρ + σ²   (Bianchi I, 8πG=1)
FRIEDMANN = G_00 - 3 * HUB ** 2 + SIG2

#: 전단 방정식 (측정 대상).  Bianchi I 은 ³S_ab = 0 이므로
#:     σ̇^i_i + θ σ^i_i = c_π · π^i_i
#: 여기서 π^i_i 는 정규직교틀 무대각합 이방응력.  Einstein 의 무대각합 공간 방정식
#:     G_{\hat i\hat i} − ⅓ tr G  =  −(p δ + π) 의 무대각합부 = −π^i_i
#: 를 σ 로 다시 쓰면 c_π 가 나온다.  ★ c_π 를 **측정**한다.
TR_G = sum(G_ORTHO) / 3
G_TF = [G_ORTHO[i] - TR_G for i in range(3)]        # 무대각합 공간 Einstein
SIGDOT = [Dt(s) for s in SIG]
LHS_SHEAR = [SIGDOT[i] + THETA * SIG[i] for i in range(3)]

_F = sp.lambdify(ARGS, [FRIEDMANN] + G_TF + LHS_SHEAR + [G_00, THETA, HUB, SIG2]
                 + SIG + SIGDOT, "numpy", cse=True)


def _sample(rng):
    v = [rng.uniform(0.7, 1.4) for _ in _B]
    d = [rng.uniform(-0.6, 0.6) for _ in _B]
    dd = [rng.uniform(-0.8, 0.8) for _ in _B]
    return v + d + dd


def evaluate(vals):
    r = np.asarray(_F(*vals), float)
    return dict(friedmann=r[0], G_tf=r[1:4], lhs_shear=r[4:7], G00=r[7],
                theta=r[8], H=r[9], sig2=r[10], sigma=r[11:14], sigdot=r[14:17])


# ═══════════════════════════════════════ 계수 확정
def shear_source_coefficient(nsamp=60, seed=0):
    """★ σ̇^i_i + θσ^i_i = c · (무대각합 공간 Einstein) 의 c 를 최소제곱으로 측정.

    Einstein 방정식 G_{ab} = T_{ab} 에서 무대각합 공간부는 −π_ab (부호는 규약)이므로,
    c 를 알면 π 로 다시 쓸 수 있다.
    """
    rng = np.random.default_rng(seed)
    rows, rhs = [], []
    for _ in range(nsamp):
        r = evaluate(_sample(rng))
        for i in range(3):
            rows.append([r["G_tf"][i]])
            rhs.append(r["lhs_shear"][i])
    M = np.array(rows)
    b = np.array(rhs)
    c, *_ = np.linalg.lstsq(M, b, rcond=None)
    resid = float(np.abs(M @ c - b).max())
    return float(c[0]), resid / max(np.abs(b).max(), 1e-300)


def friedmann_residual(nsamp=40, seed=1):
    """통제군: G_00 = 3H² − σ² 가 항등적으로 성립하는가 (Bianchi I, 진공 아님 무관)."""
    rng = np.random.default_rng(seed)
    w = 0.0
    for _ in range(nsamp):
        r = evaluate(_sample(rng))
        w = max(w, abs(r["friedmann"]) / max(abs(r["G00"]), 1e-300))
    return w


def report():
    print("=" * 74)
    print("K1 · 차트 Π 규격화를 Einstein 방정식에서 확정")
    print("=" * 74)
    fr = friedmann_residual()
    print(f"\n[통제군] Friedmann 구속 G_00 = 3H² − σ²   상대잔차 {fr:.3e}")
    if fr > 1e-12:
        print("  ★ 통제군 실패 → Einstein 텐서 구성을 신뢰할 수 없다.  계수 채택 금지.")
        return None
    c, res = shear_source_coefficient()
    print(f"\n[측정] σ̇^i + θσ^i = c · (무대각합 공간 Einstein)")
    print(f"  c = {c:+.12f}    상대잔차 {res:.3e}")
    print(f"\n  ⇒ G_tf = −π 규약이면  σ̇ + θσ = −c·π,  즉 σ̇ + 3Hσ = {-c:+.6f}·π")
    cc, rres, rank, null = raychaudhuri_coefficients()
    print(f"\n[측정] Raychaudhuri  Ḣ = c_H H² + c_s σ² + c_ρ ρ + c_p p")
    print(f"  c_H = {cc[0]:+.9f}   c_s = {cc[1]:+.9f}   c_ρ = {cc[2]:+.9f}   c_p = {cc[3]:+.9f}")
    print(f"  상대잔차 {rres:.3e}    설계행렬 rank = {rank}/4")
    eq = raychaudhuri_equivalent_to_standard()
    print("  ★ rank 결손 (Friedmann 3H² = ρ+σ² 이 {H²,σ²,ρ} 를 종속시킨다)")
    print(f"    ⇒ 계수 자체는 **유일하지 않다**.  교과서형 (−1, −2/3, −1/6, −1/2) 과의 차가")
    print(f"      영공간 (3,−1,−1,0) 에 평행한지가 판정 기준:")
    print(f"      평행성분 {eq['parallel_component']:+.6f},  수직성분 {eq['perpendicular']:.3e}"
          f"  → {'동치 ✓' if eq['equivalent'] else '불일치 ✗'}")

    vres = verify_chart_normalization()
    print(f"\n[검증] Σ' = −(2−q)Σ + Π  에서  **Π = π/H²**   상대잔차 {vres:.3e}")
    print("  (경로 A: 계량에서 직접 얻은 σ̇ 를 τ·Σ 로 변환 / 경로 B: 차트 공식)")
    return c, cc, vres




# ═══════════════════════════════════════ 차트 변수로의 변환 (손대수 대신 측정)
#: Raychaudhuri:  Ḣ = c_H·H² + c_s·σ² + c_r·ρ + c_p·p  — 계수를 **측정**한다.
HDOT = Dt(HUB)
_F2 = sp.lambdify(ARGS, [HDOT, HUB, SIG2, G_00] + G_ORTHO, "numpy", cse=True)


def raychaudhuri_coefficients(nsamp=80, seed=2):
    """★ Ḣ = c_H H² + c_s σ² + c_ρ ρ + c_p p 의 계수를 최소제곱으로 측정.

    ρ, p 는 Einstein 에서 읽는다: ρ = G_00,  3p = tr(G_ij) (정규직교틀).
    ★ 손으로 외운 공식을 쓰지 않는다 — H5-b 와 같은 방침.
    """
    rng = np.random.default_rng(seed)
    rows, rhs = [], []
    for _ in range(nsamp):
        r = np.asarray(_F2(*_sample(rng)), float)
        hdot, H, s2, rho = r[0], r[1], r[2], r[3]
        p = float(np.sum(r[4:7])) / 3.0
        rows.append([H ** 2, s2, rho, p])
        rhs.append(hdot)
    M, b = np.array(rows), np.array(rhs)
    c, *_ = np.linalg.lstsq(M, b, rcond=None)
    resid = float(np.abs(M @ c - b).max()) / max(np.abs(b).max(), 1e-300)
    # ★ 함정: Friedmann 구속 3H² = ρ + σ² 때문에 {H², σ², ρ} 가 **선형종속**이다.
    #   설계행렬 rank 가 3 (4 가 아님) 이라 최소제곱해가 **유일하지 않다**.
    #   영공간 방향 (3, −1, −1, 0) 을 함께 보고하지 않으면 계수를 오독한다.
    rank = int(np.linalg.matrix_rank(M, tol=1e-10))
    null = np.array([3.0, -1.0, -1.0, 0.0])
    null /= np.linalg.norm(null)
    return c, resid, rank, null


#: 교과서형 Raychaudhuri (Bianchi I, 8πG=1):  Ḣ = −H² − (2/3)σ² − (1/6)(ρ+3p)
RAYCHAUDHURI_STANDARD = np.array([-1.0, -2.0 / 3.0, -1.0 / 6.0, -0.5])


def raychaudhuri_equivalent_to_standard(tol=1e-9):
    """★ 측정해가 교과서형과 **Friedmann 영공간을 빼면** 같은지 확인.

    rank 결손이라 계수 자체는 유일하지 않다.  둘의 차가 영공간 (3,−1,−1,0) 에
    **평행**한지가 올바른 판정 기준이다.
    """
    c, _, rank, null = raychaudhuri_coefficients()
    d = np.asarray(c, float) - RAYCHAUDHURI_STANDARD
    perp = d - (d @ null) * null
    return dict(rank=rank, diff=d, parallel_component=float(d @ null),
                perpendicular=float(np.abs(perp).max()),
                equivalent=bool(np.abs(perp).max() < tol))


def verify_chart_normalization(nsamp=40, seed=3):
    """★ Σ' = −(2−q)Σ + Π 에서 **Π = π/H²** 임을 수치로 확인 (손대수 검증).

    경로 A: 계량에서 직접 얻은 σ̇ 를 τ=ln ℓ, Σ=σ/H 로 변환
    경로 B: 차트 공식 −(2−q)Σ + Π  에 Π = π/H² 대입
    두 값이 같아야 한다.  q 는 Ḣ = −(1+q)H² 로 정의.
    """
    rng = np.random.default_rng(seed)
    worst = 0.0
    for _ in range(nsamp):
        vals = _sample(rng)
        r = evaluate(vals)
        r2 = np.asarray(_F2(*vals), float)
        H, hdot = r["H"], r2[0]
        q = -1.0 - hdot / H ** 2
        pi = r["G_tf"]                              # 무대각합 공간 Einstein = π
        Sig = r["sigma"] / H
        # 경로 A:  Σ' = σ̇/H² + (1+q)Σ
        A = r["sigdot"] / H ** 2 + (1.0 + q) * Sig
        # 경로 B:  −(2−q)Σ + π/H²   (³S = 0 for Bianchi I)
        B = -(2.0 - q) * Sig + pi / H ** 2
        worst = max(worst, float(np.abs(A - B).max() / max(np.abs(A).max(), 1e-300)))
    return worst


if __name__ == "__main__":
    report()
