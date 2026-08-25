"""
I1d · Einstein-Boltzmann 결합 — tilted 다성분 기하 × n-프레임 운동종 (68차).

★ 통찰 (박제): 무충돌·무질량 운동종은 **n-프레임 (l,i) 다중극이 완비**다 —
종의 '틸트' 는 쌍극 J(1) 이 나르고, 종-프레임 tilted 기계 (J2b/J2c 좌변·질량
행렬) 는 충돌항이 종-프레임에서 단순해지는 B2b 부터 필수가 된다.  따라서
I1d 결합은 질량행렬 선형해 없이 **명시 dJ** 로 간다 (I1c 계층 + 회전항).

구조: 상태 y = [Σ5, N3, lnH, {(Ω_c, v_c)}_{c<NC}, J-격자(i=0)].
  기하 (H'1 합성 경로 재사용 — G.rhs + fluid 모듈):
      q = 2Σ² + Σ_c q-기여_c + Ω_kin        (운동종 무질량)
      Π_tot = Σ_c Π_c + π_kin/H²,   q⃗_tot = Σ_c q⃗_c + q⃗_kin/H²  (Codazzi)
      게이지 R: n-대각 유지 (H'1 gauge_W — Σ·N 만의 함수).
  유체: F.dOmega / F.dv_general (+H'2 κ 교환) — q 는 총 q 사용.
  운동종: dJ = hierarchy_rhs_coeff(H→1, s5=Σ전체) + nterm(N) + **회전항**
      (프레임 co-회전: l=1 이 W@vec 과 일치하도록 부호 핀 — 시험).
  dlnH = −(1+q).

게이트: 운동종=0 ⇒ H'1 rhs 정확 재현; 유체=0·대각·W=0 ⇒ I1c 정확 재현;
총 Codazzi (운동 q 포함) 전파 닫힘; 쌍극 유체극한; CS(II) 고유값 −1/4 (γ=4/3);
회전 공변성 핀; F2 회귀 = 전체 스위트.

LIMITATIONS: 운동종 1개·무질량·i=0 (별칭)·단순절단; 종-프레임 tilted 계층
및 운동-유체 교환은 B2b/I3 몫; Python RK4.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np

from bianchi.backend_policy import require_native
from bianchi.optional_dependencies import require_jax_x64


@lru_cache(maxsize=1)
def _oracle_modules():
    """Load JAX/SymPy-dependent oracle modules only for explicit Python work."""

    _, jnp = require_jax_x64(feature=__name__)
    from bianchi.charts import class_a_tilted_multi as MM
    from bianchi.charts import general as G
    from bianchi.matter import exchange as EX
    from bianchi.matter import fluid as F
    from bianchi.matter import hierarchy_nterm as HN
    from bianchi.matter import pstf_coeff as PC
    from bianchi.matter.coupled_class_a import _AliasJ
    from bianchi.matter.hierarchy_coeff import hierarchy_rhs_coeff

    return jnp, MM, G, EX, F, HN, PC, _AliasJ, hierarchy_rhs_coeff


def jgrid_len(l_max):
    return sum(2 * l + 1 for l in range(l_max + 1))


def pack(S5, N3, lnH, Om, V, Jc, l_max):
    nc = len(Om)
    fl = np.concatenate([np.concatenate([[Om[c]], V[c]]) for c in range(nc)]) \
        if nc else np.zeros(0)
    J = np.concatenate([np.asarray(Jc[(l, 0)], float).ravel()
                        for l in range(l_max + 1)])
    return np.concatenate([S5, N3, [lnH], fl, J])


def unpack(y, nc, l_max):
    y = np.asarray(y, float)
    S5, N3, lnH = y[:5], y[5:8], float(y[8])
    o = 9
    Om = np.zeros(nc)
    V = np.zeros((nc, 3))
    for c in range(nc):
        Om[c] = y[o]
        V[c] = y[o + 1:o + 4]
        o += 4
    Jc = {}
    for l in range(l_max + 1):
        n = 2 * l + 1
        Jc[(l, 0)] = y[o:o + n]
        o += n
    return S5, N3, lnH, Om, V, Jc


def kinetic_sources(Jc, lnH, l_max):
    """(Ω_kin, q⃗_kin_chart(3, cart), π_kin_chart(3,3))."""
    _, _, _, _, _, _, PC, _, _ = _oracle_modules()
    H2 = np.exp(2.0 * lnH)
    rho = float(np.asarray(Jc[(0, 0)]).reshape(1)[0])
    Om = rho / (3.0 * H2)
    qv = np.zeros(3)
    if l_max >= 1:
        qv = np.asarray(PC.from_ccoef(Jc[(1, 0)], 1), float) / H2
    pi = np.zeros((3, 3))
    if l_max >= 2:
        pi = np.asarray(PC.from_ccoef(Jc[(2, 0)], 2), float) / H2
    return Om, qv, pi


def _rot_term(c, l, w_cart, sign=-1.0):
    """프레임 co-회전 항 — l=1 에서 W@vec 재현 (시험 핀).

    ★ 반증 박제 (68차): 1판 sign=+1 이 비율 **정확 −1** 로 적발 —
    rot_block 생성자는 tilted Ω-규약 (W=+ε·w) 방향이라 프레임 co-회전
    (W=−ε·R) 에는 부호 반대.  J2b ω-핀과 동일 사고 패턴 (부호는 유도를
    믿지 않고 핀으로)."""
    if l == 0:
        return np.zeros(1)
    _, _, _, _, _, _, PC, _, _ = _oracle_modules()
    return sign * l * PC.apply_block(PC.rot_block(l), np.asarray(c, float),
                                     np.asarray(w_cart, float))


def coupled_rhs(y, gammas, l_max, kappa=None, nterm_on=True):
    jnp, MM, G, EX, F, HN, PC, _AliasJ, hierarchy_rhs_coeff = _oracle_modules()
    gammas = np.asarray(gammas, float)
    nc = gammas.shape[0]
    S5, N3, lnH, Om, V, Jc = unpack(y, nc, l_max)
    ym = MM.StateATM.of(S5, N3, Om if nc else np.zeros(1),
                        V if nc else np.zeros((1, 3)))
    S = np.asarray(MM.shear_matrix(jnp.asarray(S5)), float)
    Sigma2 = float(S5 @ S5)
    H2 = np.exp(2.0 * lnH)
    # 운동종 소스
    Ok, qk, pik = kinetic_sources(Jc, lnH, l_max)
    # 유체 소스
    fluids, srcs = [], []
    for c in range(nc):
        f = F.TiltedFluid.of(gammas[c], Om[c], V[c])
        fluids.append(f)
        srcs.append(F.sources(f, jnp.asarray(S), jnp.zeros(3)))
    q = 2.0 * Sigma2 + Ok
    for c in range(nc):
        s = srcs[c]
        q += float(0.5 * ((3.0*gammas[c] - 2.0)
                          + (2.0 - gammas[c]) * s["V2"]) * Om[c] / s["Gp"])
    Pi_tot = pik + sum(np.asarray(s["Pi"], float) for s in srcs) \
        if nc else pik
    # 게이지 (H'1 — Σ·N 만의 함수)
    if nc:
        R = np.asarray(MM.gauge_R(ym), float)
    else:
        w12 = w13 = w23 = 0.0
        # 유체 0 이어도 게이지는 Σ·N 에서 옴
        Sm = MM.StateATM.of(S5, N3, np.zeros(1), np.zeros((1, 3)))
        R = np.asarray(MM.gauge_R(Sm), float)
    # 기하 (합성 — G.rhs)
    gargs = dict(gamma=4.0/3.0, q=q, Omega=0.0, Pi=jnp.asarray(Pi_tot),
                 R=jnp.asarray(R))
    dG = G.rhs(0.0, G.StateG(jnp.asarray(S), jnp.diag(jnp.asarray(N3)),
                             jnp.zeros(3)), gargs)
    dS = np.asarray(dG.Sigma, float)
    r3 = np.sqrt(3.0)
    dS5 = np.array([-dS[0, 0]/2.0, (dS[1, 1]-dS[2, 2])/(2.0*r3),
                    dS[0, 1]/r3, dS[0, 2]/r3, dS[1, 2]/r3])
    dN3 = np.array([float(dG.N[0, 0]), float(dG.N[1, 1]), float(dG.N[2, 2])])
    dlnH = -(1.0 + q)
    # 유체 진화 (총 q 사용) + κ 교환
    dOm = np.zeros(nc)
    dV = np.zeros((nc, 3))
    for c in range(nc):
        dOm[c] = float(F.dOmega(fluids[c], srcs[c], q))
        dV[c] = np.asarray(F.dv_general(fluids[c], srcs[c], jnp.asarray(S),
                                        jnp.diag(jnp.asarray(N3)),
                                        jnp.zeros(3), jnp.asarray(R)), float)
    if kappa is not None and nc:
        k = EX.validate_kappa(kappa, nc)
        Rx = EX.exchange_R(jnp.asarray(Om), jnp.asarray(V), k)
        dV = dV + np.asarray(EX.delta_dv_closed(jnp.asarray(gammas),
                                                jnp.asarray(Om),
                                                jnp.asarray(V), Rx), float)
    # 운동종 계층 (τ-시간: H→1)
    A = _AliasJ(Jc, l_max)
    s5 = PC.to_ccoef(S, 2)
    dJ = {}
    for l in range(l_max + 1):
        r = hierarchy_rhs_coeff(A, 1.0, s5, l, 0)
        if nterm_on:
            r = r + HN.nterm_coeff(A, N3, l, 0)
        r = r + _rot_term(Jc[(l, 0)], l, R)
        dJ[(l, 0)] = r
    return pack(dS5, dN3, dlnH, dOm, dV, dJ, l_max)


def rk4_evolve(y0, gammas, l_max, tau, nsteps, kappa=None, nterm_on=True,
               keep=False):
    y = np.asarray(y0, float).copy()
    h = tau / nsteps
    traj = [y.copy()] if keep else None
    for _ in range(nsteps):
        k1 = coupled_rhs(y, gammas, l_max, kappa, nterm_on)
        k2 = coupled_rhs(y + 0.5*h*k1, gammas, l_max, kappa, nterm_on)
        k3 = coupled_rhs(y + 0.5*h*k2, gammas, l_max, kappa, nterm_on)
        k4 = coupled_rhs(y + h*k3, gammas, l_max, kappa, nterm_on)
        y = y + (h/6.0) * (k1 + 2*k2 + 2*k3 + k4)
        if keep:
            traj.append(y.copy())
    return (y, np.stack(traj)) if keep else y


def monitors(y, gammas, l_max):
    """Gauss (총) + 총 Codazzi (운동 q 포함) — 잔차."""
    from bianchi.conventions import codazzi_residual
    jnp, MM, _, _, F, _, _, _, _ = _oracle_modules()
    gammas = np.asarray(gammas, float)
    nc = gammas.shape[0]
    S5, N3, lnH, Om, V, Jc = unpack(y, nc, l_max)
    S = np.asarray(MM.shear_matrix(jnp.asarray(S5)), float)
    Ok, qk, _ = kinetic_sources(Jc, lnH, l_max)
    K = float(MM.aux(MM.StateATM.of(S5, N3, np.zeros(1), np.zeros((1, 3))),
                     dict(gammas=np.ones(1)))["K"])
    gauss = 1.0 - float(S5 @ S5) - K - Ok - float(np.sum(Om))
    qtot = qk.copy()
    for c in range(nc):
        s = F.sources(F.TiltedFluid.of(gammas[c], Om[c], V[c]),
                      jnp.asarray(S), jnp.zeros(3))
        qtot = qtot + np.asarray(s["q_flux"], float)
    cod = np.asarray(codazzi_residual(jnp.asarray(S),
                                      jnp.diag(jnp.asarray(N3)),
                                      jnp.zeros(3), jnp.asarray(qtot)), float)
    return dict(gauss=gauss, codazzi=cod)


# ═══════════════════════════════ I3 · Rust 루프째 래퍼 (69차)
def _u_tables():
    """U-기저 캐리 (좌표-동일): u1 = U₁ (3,3) row-major [a,m];
    u2 = U₂ (9,5) [pq,m] — from_ccoef/to_ccoef 양방향 (직교정규)."""
    from bianchi.matter._pstf_low_rank import u_basis

    u1 = np.asarray(u_basis(1), float)                 # (3, 3) [flat-pq=a, m]
    u2 = np.asarray(u_basis(2), float)                 # (9, 5)
    return np.ascontiguousarray(u1).ravel(), np.ascontiguousarray(u2).ravel()


def _sigma_signs_vec():
    from bianchi.matter.hierarchy import SIGMA_SIGNS
    return np.array([SIGMA_SIGNS["A"], SIGMA_SIGNS["B"], SIGMA_SIGNS["C"]])


def coupled_rhs_rust(y, gammas, l_max, kappa=None, nterm_on=True, nu_bgk=0.0):
    """Rust cp_rhs — Python `coupled_rhs` 의 두-경로 상대 (차등시험 게이트)."""
    rust = require_native("coupled_tilted.coupled_rhs_rust")
    u1, u2 = _u_tables()
    k = None if kappa is None else np.ascontiguousarray(
        np.asarray(kappa, float)).ravel()
    return np.asarray(rust.cp_rhs(np.ascontiguousarray(np.asarray(y, float)),
                                  np.asarray(gammas, float), k, int(l_max),
                                  bool(nterm_on), u1, u2, _sigma_signs_vec(),
                                  float(nu_bgk)))


def rk4_evolve_rust(y0, gammas, l_max, tau, nsteps, kappa=None,
                    nterm_on=True, keep=False, nu_bgk=0.0):
    """Rust cp_evolve — 루프째 (R5b).  반환 Python 판과 동일 형상."""
    rust = require_native("coupled_tilted.rk4_evolve_rust")
    u1, u2 = _u_tables()
    k = None if kappa is None else np.ascontiguousarray(
        np.asarray(kappa, float)).ravel()
    yT, traj = rust.cp_evolve(np.ascontiguousarray(np.asarray(y0, float)),
                              np.asarray(gammas, float), k, int(l_max),
                              float(tau), int(nsteps), bool(nterm_on),
                              bool(keep), u1, u2, _sigma_signs_vec(),
                              float(nu_bgk))
    yT = np.asarray(yT)
    return (yT, np.asarray(traj)) if keep else yT
