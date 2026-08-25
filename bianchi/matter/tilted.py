"""
H5-c · tilted 합동 계층 — boost 사틀, 운동학, 그리고 **질량행렬** M(v)·J̇ = F.

법선합동(u = e₀)에서는 ω = u̇ = 0 이고 균질성으로 D_a 도 죽어서 계층이 명시적 RHS
(`hierarchy.hierarchy_rhs`) 로 닫힌다.  tilted (u ≠ n) 에서는 세 가지가 달라진다:

1. **ω, u̇ 항이 살아난다** — 부호는 H5-b 에서 ∇_μT^{μν}=0 오라클로 확정:
   (A,B,C,D,E,Ω,div-con,div-free) = (+1,−1,−1,+1,−1,+1,+1,−1),  유일성 마진 1.4e14 배.
2. **공간미분이 살아난다** — 균질성은 *법선* 합동의 초곡면에 대한 것이고 tilted
   관측자의 초곡면은 다르다.  순수 boost 사틀에서 E_A^t = γ v_A 이므로
   스칼라조차  D_A ρ = γ v_A ρ̇ ≠ 0.
3. 따라서 **계층이 음함수(질량행렬) ODE 가 된다** — D 항이 이웃 l 의 시간미분을
   품는다.  dJ/dt 를 바로 반환하는 형태로는 구현할 수 없다.

★ 발견된 닫힌형 (l ≤ 1 블록):

        M = γ (I + e₀ vᵀ),        M⁻¹ = γ⁻¹ (I − e₀ vᵀ)

  l=0 행이 γ(ρ̇ + v·q̇) 인 것은 ⊥ρ̇ = γρ̇ 와 D^aq_a 의 γv_B q̇_B 가 합쳐진 결과다.
  l=1 행은 γq̇_A 뿐 — D^bπ_ba 는 π̇ (이 블록 밖) 로 가므로 q̇ 결합이 없다.
  ⇒ **상삼각**이라 선형해가 필요 없고, cond(M) ≤ 2.4 (|v| ≤ 0.9) 로 온순하다.

★ 설계 원칙 1 — 질량행렬을 **손으로 옮겨 적지 않는다.**
  좌변은 미지 시간미분 (ρ̇, q̇_A) 에 대해 **정확히 아핀**이므로

        F = −EQ(0),      M[:, c] = EQ(e_c) − EQ(0)

  로 5회 평가만에 M, F 를 **정확히** 뽑는다 (유한차분 오차 없음).
  아핀성 자체를 시험으로 못 박는다 (`test_equation_is_affine_in_time_derivatives`).

★ 설계 원칙 2 — 기호계산은 **기본량에만**, 축약은 numpy 로.
  초기 판은 방정식 전체를 하나의 sympy 식으로 세워 lambdify 했는데, D^bπ_ba 가
  4중 합(192항)이고 그 위에 편미분이 얹혀 표현식이 조합폭발했다:
  **임포트 148 초 · 호출 107 ms** (cse=True 로도 개선 안 됨).  사틀·접속 같은 작은
  닫힌형만 기호로 두고 지표축약을 numpy 로 옮겨 두 자리 이상 줄였다.

★ 정직한 범위: 여기서 조립하는 것은 **l ≤ 1 블록**이다.  자체로 닫히지 않는다
  (ṗ = J̇^(1)/3 와 π̇_ab 가 외부 입력).  일반 l 에서는 (div-con) 이 l+1, (div-free) 가
  l−1 (그리고 i+1) 로 결합하므로 M 은 l 에 대해 **삼중대각**이 되고 상삼각성이 깨진다.
  l ≥ 2 는 H5-d 의 boosted 구적 오라클로 검증한 뒤 확장한다 — 보존법칙은 l ≤ 1 만
  통제하기 때문.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np

from bianchi.optional_dependencies import require_optional

# ═══════════════════════════════════════ 확정 부호 (H5-b)
#: `out -= SIGN * (논문 대괄호식)` 규약.  +1 = 논문 부호 그대로, −1 = 뒤집힘.
SIGNS = dict(A=+1.0, B=-1.0, C=-1.0, D=+1.0, E=-1.0, Omega=+1.0,
             divcon=+1.0, divfree=-1.0)


# ═══════════════════════════════════════ 기호: 사틀과 그 시간미분만
@lru_cache(maxsize=1)
def _tetrad_fn():
    """(u^μ, u_μ, E_A^μ, E_Aμ) 와 그 t-도함수를 lambdify.

    ★ 이 네 묶음만 기호로 만든다 — 각 성분이 작은 닫힌형이라 즉시 컴파일된다.
      나머지(접속·축약·발산)는 numpy 에서 지표계산으로 처리한다.
    """
    sp = require_optional("sympy", feature=f"{__name__}._tetrad_fn")

    names = ["a1", "a2", "a3", "v1", "v2", "v3"]
    S = {n: sp.Symbol(n, real=True) for n in names}
    D = {n: sp.Symbol("d" + n, real=True) for n in names}
    args = [S[n] for n in names] + [D[n] for n in names]

    def dt(e):
        return sp.Add(*[sp.diff(sp.sympify(e), S[n]) * D[n] for n in names])

    a = [S["a1"], S["a2"], S["a3"]]
    v = [S["v1"], S["v2"], S["v3"]]
    g = sp.diag(-1, a[0] ** 2, a[1] ** 2, a[2] ** 2)
    gam = 1 / sp.sqrt(1 - (v[0] ** 2 + v[1] ** 2 + v[2] ** 2))
    ehat = [[sp.Integer(0)] * 4 for _ in range(3)]
    for i in range(3):
        ehat[i][i + 1] = 1 / a[i]

    uup = [gam] + [gam * v[i] / a[i] for i in range(3)]
    #: 순수 boost:  E_A = γv_A n + [δ_AB + (γ−1)v_Av_B/v²] ê_B,  (γ−1)/v² = γ²/(γ+1)
    #: ★ E_A^t = γ v_A  ← tilted 에서 D_a 가 죽지 않는 이유가 바로 이 성분이다.
    kk = gam ** 2 / (gam + 1)
    eup = [[gam * v[A]] + [ehat[A][m] + kk * v[A] * sum(v[B] * ehat[B][m]
                                                        for B in range(3))
                           for m in range(1, 4)] for A in range(3)]
    udn = [sum(g[m, n] * uup[n] for n in range(4)) for m in range(4)]
    edn = [[sum(g[m, n] * E[n] for n in range(4)) for m in range(4)] for E in eup]

    flat = (uup + udn + [c for E in eup for c in E] + [c for E in edn for c in E])
    out = flat + [dt(c) for c in flat]
    return sp.lambdify(args, out, "numpy")


def _geometry(a_vec, da_vec, v, dv):
    """사틀·접속·운동학을 numpy 로 조립 → dict."""
    a = np.asarray(a_vec, float)
    da = np.asarray(da_vec, float)
    vv = np.asarray(v, float)
    dvv = np.asarray(dv, float)
    r = np.asarray(_tetrad_fn()(*a, *vv, *da, *dvv), float)
    half = len(r) // 2
    cur, dot = r[:half], r[half:]

    def unpack(z):
        uup = z[0:4]
        udn = z[4:8]
        eup = z[8:20].reshape(3, 4)
        edn = z[20:32].reshape(3, 4)
        return uup, udn, eup, edn

    uup, udn, eup, edn = unpack(cur)
    duup, dudn, deup, dedn = unpack(dot)

    g = np.diag(np.r_[-1.0, a ** 2])
    ginv = np.diag(np.r_[-1.0, 1.0 / a ** 2])
    dg = np.diag(np.r_[0.0, 2.0 * a * da])

    # 접속 (대각·t-의존 계량의 닫힌형):  Γ^0_ii = a_i ȧ_i,  Γ^i_{0i} = Γ^i_{i0} = ȧ_i/a_i
    G = np.zeros((4, 4, 4))                       # G[l][m][n] = Γ^l_{mn}
    for i in range(3):
        G[0, i + 1, i + 1] = a[i] * da[i]
        G[i + 1, 0, i + 1] = G[i + 1, i + 1, 0] = da[i] / a[i]

    # ∇_μ u_ν
    nab_u = np.zeros((4, 4))
    nab_u[0] += dudn
    nab_u -= np.einsum("lmn,l->mn", G, udn)
    theta = float(np.einsum("mn,mn->", ginv, nab_u))
    H = theta / 3.0
    udot = np.einsum("m,mn->n", uup, nab_u)

    hmix = np.eye(4) + np.outer(uup, udn)         # h^μ_ν
    hdn = g + np.outer(udn, udn)
    du = np.einsum("ci,dj,cd->ij", hmix, hmix, nab_u)
    sig_t = 0.5 * (du + du.T) - H * hdn
    omg_t = 0.5 * (du - du.T)

    sig = np.einsum("am,bn,mn->ab", eup, eup, sig_t)
    omg = np.einsum("am,bn,mn->ab", eup, eup, omg_t)
    udot_a = np.einsum("am,m->a", eup, udot)
    return dict(a=a, da=da, g=g, ginv=ginv, dg=dg, G=G, uup=uup, udn=udn,
                eup=eup, edn=edn, deup=deup, hmix=hmix,
                H=H, sigma=sig, omega=omg, udot=udot_a,
                ortho=_ortho_residual(g, uup, eup))


def _ortho_residual(g, uup, eup):
    """u·u=−1, u·E_A=0, E_A·E_B=δ 의 최대 잔차 (사틀 자기검증)."""
    w = [abs(float(uup @ g @ uup) + 1.0)]
    for A in range(3):
        w.append(abs(float(uup @ g @ eup[A])))
        for B in range(3):
            w.append(abs(float(eup[A] @ g @ eup[B]) - (1.0 if A == B else 0.0)))
    return max(w)


def _pi_matrix(pi5):
    """5 성분 → 3x3 대칭 무대각합 (conventions.tracefree_from_5 규약)."""
    s00, s11, s01, s02, s12 = (float(z) for z in pi5)
    return np.array([[s00, s01, s02], [s01, s11, s12], [s02, s12, -s00 - s11]])


def _matter_terms(geo, rho, drho, p, dp, q, dq, pi, dpi):
    """⊥q̇_A, D^aq_a, D^bπ_ba, D_a p — tilted 에서 살아나는 항들."""
    g, ginv, dg, G = geo["g"], geo["ginv"], geo["dg"], geo["G"]
    eup, edn, deup, hmix, uup = geo["eup"], geo["edn"], geo["deup"], geo["hmix"], geo["uup"]

    # q^μ 와 그 t-도함수 (사틀이 t-의존이므로 두 항)
    qup = np.einsum("a,am->m", q, eup)
    dqup = np.einsum("a,am->m", dq, eup) + np.einsum("a,am->m", q, deup)
    qdn = g @ qup
    dqdn = dg @ qup + g @ dqup

    # ⊥q̇^μ = h^μ_ν u^λ∇_λ q^ν  (상첨자 판)
    nab_qup = np.zeros((4, 4))
    nab_qup[0] += dqup
    nab_qup += np.einsum("nml,l->mn", G, qup)
    qdot_up = np.einsum("mn,l,ln->m", hmix, uup, nab_qup)
    qdot_a = np.einsum("am,m->a", edn, qdot_up)

    # D^a q_a  (하첨자 판의 공변미분을 사틀로 두 번 사영)
    nab_qdn = np.zeros((4, 4))
    nab_qdn[0] += dqdn
    nab_qdn -= np.einsum("lmn,l->mn", G, qdn)
    div_q = float(np.einsum("am,an,mn->", eup, eup, nab_qdn))

    # π^{μν} 와 t-도함수 → 하첨자 → D^bπ_{ba}
    piup = np.einsum("ab,am,bn->mn", pi, eup, eup)
    dpiup = (np.einsum("ab,am,bn->mn", dpi, eup, eup)
             + np.einsum("ab,am,bn->mn", pi, deup, eup)
             + np.einsum("ab,am,bn->mn", pi, eup, deup))
    pidn = g @ piup @ g
    dpidn = dg @ piup @ g + g @ dpiup @ g + g @ piup @ dg
    nab_pi = np.zeros((4, 4, 4))                  # nab_pi[m][n][l] = ∇_μ π_{νλ}
    nab_pi[0] += dpidn
    nab_pi -= np.einsum("rmn,rl->mnl", G, pidn)
    nab_pi -= np.einsum("rml,nr->mnl", G, pidn)
    div_pi = np.einsum("bm,bn,al,mnl->a", eup, eup, eup, nab_pi)

    grad_p = eup[:, 0] * float(dp)                # D_a p = E_A^t ṗ  (= γ v_A ṗ)
    rho_dot = float(uup[0]) * float(drho)         # ⊥ρ̇ = u^μ∂_μρ = γ ρ̇
    return dict(rho_dot=rho_dot, q_dot=qdot_a, div_q=div_q, div_pi=div_pi,
                grad_p=grad_p)


# ═══════════════════════════════════════ 계층 좌변 (l=0,i=0 / l=1,i=0)
def _equation(geo, rho, drho, p, dp, q, dq, pi, dpi):
    """계층 좌변 4성분.

    l=0,i=0 (n=0):  (A),(C),(D),(Ω) 은 l 인자로 소멸;  (B) 는 (l−n)=0 이라
                    J^(−1) 이 죽고 −π_ab σ^ab 만 남는다.
    l=1,i=0 (n=1):  (1−n)J^(1)_a = 0 (★ J^(1)_a 소멸);  (A) 의 (2−2n)=0;
                    **(B) 는 (l−n)=(n−1)=0 이라 완전 소멸**;  (C) 는 l≥2 전용.
    """
    m = _matter_terms(geo, rho, drho, p, dp, q, dq, pi, dpi)
    H, sig, omg, ud = geo["H"], geo["sigma"], geo["omega"], geo["udot"]
    s = SIGNS
    eq0 = (m["rho_dot"] + 3.0 * H * (rho + p)
           + s["divcon"] * m["div_q"]
           + s["E"] * (-2.0 * float(q @ ud))
           + s["B"] * (-float((pi * sig).sum())))
    eq1 = (m["q_dot"] + 4.0 * H * q
           + s["divcon"] * m["div_pi"]
           + s["divfree"] * (-m["grad_p"])
           + s["Omega"] * (-omg @ q)
           + s["D"] * (rho + p) * ud
           + s["E"] * (-pi @ ud)
           + s["A"] * (sig @ q))
    return np.r_[eq0, eq1], m


# ═══════════════════════════════════════ 공개 API
_DEF = dict(a_vec=(1.0, 0.9, 1.2), da_vec=(0.3, 0.25, 0.35), v=(0.1, -0.05, 0.15),
            dv=(0.02, 0.01, -0.03), rho=1.0, drho=-0.4, p=0.3, dp=-0.1,
            q=(0.05, -0.02, 0.03), dq=(0.01, -0.01, 0.02),
            pi5=(0.04, -0.02, 0.01, -0.03, 0.02), dpi5=(0.01,) * 5)


def state(**kw):
    """전 항목 평가 → dict(H, sigma, omega, udot, div_*, M, F, eq, ortho).

    기본값은 비등방·다축 tilt (ω ≠ 0 인 설정 — 축정렬 tilt 는 ω 를 켜지 못한다).
    """
    o = dict(_DEF); o.update(kw)
    geo = _geometry(o["a_vec"], o["da_vec"], o["v"], o["dv"])
    pi = _pi_matrix(o["pi5"])
    dpi = _pi_matrix(o["dpi5"])
    q = np.asarray(o["q"], float)
    dq = np.asarray(o["dq"], float)
    args = (o["rho"], o["p"], o["dp"], q, pi, dpi)

    def ev(drho_, dq_):
        e, m = _equation(geo, args[0], drho_, args[1], args[2], q, dq_, pi, dpi)
        return e, m

    eq, mt = ev(o["drho"], dq)
    # ★ 좌변이 (ρ̇, q̇) 에 대해 정확히 아핀 ⇒ 5회 평가로 M, F 를 오차 없이 뽑는다
    e0, _ = ev(0.0, np.zeros(3))
    cols = [ev(1.0, np.zeros(3))[0] - e0]
    for B in range(3):
        u = np.zeros(3); u[B] = 1.0
        cols.append(ev(0.0, u)[0] - e0)
    M = np.column_stack(cols)
    return dict(H=geo["H"], sigma=geo["sigma"], omega=geo["omega"], udot=geo["udot"],
                div_q=mt["div_q"], div_pi=mt["div_pi"], grad_p=mt["grad_p"],
                rho_dot=mt["rho_dot"], q_dot=mt["q_dot"],
                M=M, F=-e0, eq=eq, ortho=geo["ortho"])


def kinematics(a_vec=_DEF["a_vec"], da_vec=_DEF["da_vec"], v=_DEF["v"], dv=_DEF["dv"]):
    """tilted 합동의 (H, σ_AB, ω_AB, u̇_A) — 물질과 무관한 순수 기하."""
    geo = _geometry(a_vec, da_vec, v, dv)
    return dict(H=geo["H"], sigma=geo["sigma"], omega=geo["omega"],
                udot=geo["udot"], ortho=geo["ortho"])


def mass_matrix(**kw):
    """M(v) — 행 = (l=0, l=1×3), 열 = (ρ̇, q̇₁, q̇₂, q̇₃).

    ★ 손 전사가 아니라 아핀성으로 **뽑아낸** 값.  닫힌형: M = γ(I + e₀vᵀ) (상삼각).
    v→0 에서 M → I ⇒ 명시적 RHS (= H1 형태) 로 정확히 환원.
    """
    return state(**kw)["M"]


def mass_matrix_closed_form(v):
    """발견된 닫힌형 M = γ(I + e₀ vᵀ) — 조립값과 대조하기 위한 독립 표현."""
    v = np.asarray(v, float)
    gam = 1.0 / np.sqrt(1.0 - float(v @ v))
    return gam * (np.eye(4) + np.outer(np.eye(4)[0], np.r_[0.0, v]))


def solve_jdot(**kw):
    """M·(ρ̇, q̇_A) = F 를 풀어 시간미분을 반환.

    ★ l ≤ 1 블록은 자체로 닫히지 않는다: ṗ, π̇_ab, ȧ, v̇ 는 **입력**이다
      (ṗ 는 (l=0,i=1) 이, π̇ 는 (l=2,i=0) 이 준다 → H5-d 이후 확장).
    반환 dict(rho_dot, q_dot, cond, M, F).
    """
    s = state(**kw)
    x = np.linalg.solve(s["M"], s["F"])
    return dict(rho_dot=float(x[0]), q_dot=x[1:].copy(),
                cond=float(np.linalg.cond(s["M"])), M=s["M"], F=s["F"])


def residual(**kw):
    """계층 좌변 자체.

    ★ off-shell 에서 0 이 아닌 것이 정상이다 — H5-b 가 보인 것은 이 좌변이
      ∇_μT^{μν} 의 사영과 **항등적으로** 같다는 것이지 0 이라는 게 아니다.
    """
    return state(**kw)["eq"]


def vanishing_tilt_recovers_normal(a_vec=_DEF["a_vec"], da_vec=_DEF["da_vec"]):
    """v = 0 게이트: ω = u̇ = D = 0 이고 M = I 여야 한다 (법선합동 환원)."""
    s = state(a_vec=a_vec, da_vec=da_vec, v=(0.0, 0.0, 0.0), dv=(0.0, 0.0, 0.0))
    return dict(omega=float(np.abs(s["omega"]).max()),
                udot=float(np.abs(s["udot"]).max()),
                div=float(max(abs(s["div_q"]), np.abs(s["div_pi"]).max(),
                              np.abs(s["grad_p"]).max())),
                M_minus_I=float(np.abs(s["M"] - np.eye(4)).max()))


def tilt_scan(vmax=0.9, n=10, **kw):
    """|v| 를 키우며 cond(M), max|ω| 측정 — **유효 tilt 범위를 조용히 쓰지 않고 보고**."""
    out = []
    direction = np.array([1.0, -0.5, 1.5])
    direction /= np.linalg.norm(direction)
    for f in np.linspace(0.0, vmax, n):
        kk = dict(kw); kk["v"] = tuple(direction * f)
        s = state(**kk)
        out.append((float(f), float(np.linalg.cond(s["M"])),
                    float(np.abs(s["omega"]).max())))
    return out
