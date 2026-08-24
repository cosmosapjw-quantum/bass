"""
H'1 · 다성분 tilted class A 차트 (n-대각 게이지) — **합성 정의**, 두 경로 검증.

성분 c = 1..NC 의 γ-법칙 유체 각각 (Ω_c, v_c^a) 를 나른다.  기하는 **총**
T^{μν} = Σ_c T_c 만 본다 (PLAN-NEXT-v5 §4):
    Π_tot = Σ_c Π_c,   q_tot^a = Σ_c q_c^a,   q = 2Σ² + Σ_c q-기여_c.
Codazzi 는 **총 운동량속에만** 걸린다 — 성분별로는 자유, 합이 구속 (시험 박제).

★ F3 (단일유체) 와의 설계 차이 — Ω 를 **소거하지 않는다**:
    단일유체는 Gauss 로 Ω 를 대수 소거했다.  다성분에서 하나만 소거하면 성분
    대칭이 깨지고 환원시험이 뒤틀린다.  여기서는 전 성분 Ω_c 를 dΩ (U4 확정,
    분모 G₊) 로 **진화**시키고 Gauss 1−Σ²−K−ΣΩ_c 를 **잔차**로 감시한다 —
    전파 닫힘 (dGauss/dτ = 0 on-shell) 이 유도·실측 이중 게이트 (D2 방법론).

상태 (8 + 4·NC):
    Σ₊, Σ₋, Σ₁₂, Σ₁₃, Σ₂₃, N₁, N₂, N₃, {Ω_c, v_c1, v_c2, v_c3}_{c=1..NC}
게이지: F3 와 동일 — n-대각 유지가 회전 3개 전부 소모, W_ij = S_ij(N_i+N_j)/(N_i−N_j).
    (게이지는 Σ, N 만의 함수라 성분 수와 무관.)

★ 편타면 (V16 함정 예약의 이행): 성분별 G₋_c = 1 − (γ_c−1)V_c² — 성분마다
    **다른 곳**에 있다.  γ_c < 2 성분은 원리적으로 발화 불가 (G₋ ≥ 2−γ_c),
    γ_c = 2 성분만 유한 τ 관통 (F3 55차 정리 성분별 상속).  이벤트 훅의 Rust
    이월은 H'2/I3 몫 (아래 LIMITATIONS).

LIMITATIONS
  - Rust 미러 없음 — 적분은 Python (시험은 RK4 짧은 궤적).  성분별 편타
    이벤트·커널화는 H'2/I3 이월.
  - 성분간 운동량 교환 없음 (충돌 결합은 H'2) — 각 성분 ∇T_c = 0 독립.
  - routing 미편입: 단일유체 class_a_tilted 가 기본 유지, 본 차트는 명시 opt-in.
  - LRS 축퇴 (N_i=N_j, S_ij≠0) 는 F3 와 동일하게 게이지 불능.
"""
from __future__ import annotations

from bianchi.conventions import SQRT3
from bianchi.matter.fluid import G_minus, G_plus, _safe
from bianchi.optional_dependencies import require_jax_x64, require_optional

_, jnp = require_jax_x64(feature=__name__)
eqx = require_optional("equinox", feature=__name__)

name = "class_a_tilted_multi"
LIMITATIONS = __doc__.split("LIMITATIONS")[1].strip()


class StateATM(eqx.Module):
    """Σ5 = (Σ₊,Σ₋,Σ₁₂,Σ₁₃,Σ₂₃), N3 = (N₁,N₂,N₃), Om = (NC,), V = (NC,3)."""
    Sigma5: jnp.ndarray
    N3: jnp.ndarray
    Om: jnp.ndarray
    V: jnp.ndarray

    @staticmethod
    def of(Sigma5, N3, Om, V):
        return StateATM(jnp.asarray(Sigma5, jnp.float64),
                        jnp.asarray(N3, jnp.float64),
                        jnp.atleast_1d(jnp.asarray(Om, jnp.float64)),
                        jnp.atleast_2d(jnp.asarray(V, jnp.float64)))

    @property
    def nc(self):
        return self.Om.shape[0]

    def as_array(self):
        return jnp.concatenate([self.Sigma5, self.N3,
                                jnp.concatenate([self.Om[:, None], self.V],
                                                axis=1).ravel()])

    @staticmethod
    def from_array(y):
        y = jnp.asarray(y, jnp.float64)
        nc = (y.shape[0] - 8) // 4
        blk = y[8:].reshape(nc, 4)
        return StateATM(y[:5], y[5:8], blk[:, 0], blk[:, 1:])


def shear_matrix(S5):
    r3 = SQRT3
    sp, sm, s12, s13, s23 = S5[0], S5[1], S5[2], S5[3], S5[4]
    return jnp.array([
        [-2.0*sp,      r3*s12,        r3*s13],
        [r3*s12,       sp + r3*sm,    r3*s23],
        [r3*s13,       r3*s23,        sp - r3*sm],
    ])


def aux(y: StateATM, args):
    """성분별 (V²_c, G±_c, SV²_c) + 총량 (q, Π_tot, q_tot, Gauss 잔차)."""
    gam = jnp.asarray(args["gammas"], jnp.float64)
    S = shear_matrix(y.Sigma5)
    s2 = y.Sigma5 @ y.Sigma5
    n1, n2, n3 = y.N3[0], y.N3[1], y.N3[2]
    K = (n1*n1 + n2*n2 + n3*n3 - 2.0*(n1*n2 + n2*n3 + n3*n1)) / 12.0
    V2 = jnp.sum(y.V * y.V, axis=1)                    # (NC,)
    Gp = _safe(G_plus(gam, V2))
    Gm = _safe(G_minus(gam, V2))
    SV2 = jnp.einsum("ab,ca,cb->c", S, y.V, y.V)       # (NC,)
    q = 2.0*s2 + jnp.sum(
        0.5*((3.0*gam - 2.0) + (2.0 - gam)*V2) * y.Om / Gp)
    c_pi = 3.0*gam*y.Om / Gp                           # (NC,)
    Pi_tot = (jnp.einsum("c,ca,cb->ab", c_pi, y.V, y.V)
              - jnp.sum(c_pi*V2)/3.0 * jnp.eye(3))
    q_tot = jnp.einsum("c,ca->a", 3.0*gam*y.Om/Gp, y.V)
    gauss = 1.0 - s2 - K - jnp.sum(y.Om)
    sig = (-2.0*y.Sigma5[0], y.Sigma5[0] + SQRT3*y.Sigma5[1],
           y.Sigma5[0] - SQRT3*y.Sigma5[1])
    return dict(S=S, Sigma2=s2, K=K, V2=V2, Gp=Gp, Gm=Gm, SV2=SV2, q=q,
                Pi_tot=Pi_tot, q_tot=q_tot, gauss=gauss, sig=sig, gam=gam)


def gauge_W(y: StateATM):
    """F3 과 동일 (Σ, N 만의 함수 — 성분 수 무관)."""
    r3 = SQRT3
    s12, s13, s23 = y.Sigma5[2], y.Sigma5[3], y.Sigma5[4]
    n1, n2, n3 = y.N3[0], y.N3[1], y.N3[2]
    w12 = r3*s12 * (n1 + n2) / _safe(n1 - n2)
    w13 = r3*s13 * (n1 + n3) / _safe(n1 - n3)
    w23 = r3*s23 * (n2 + n3) / _safe(n2 - n3)
    return w12, w13, w23


def gauge_R(y: StateATM):
    w12, w13, w23 = gauge_W(y)
    return jnp.stack([-w23, w13, -w12])


def rhs(tau, y: StateATM, args) -> StateATM:
    """경로 1 — 성분별 전개 (F3 rhs 산술의 다성분 일반화 + dΩ 명시식)."""
    a = aux(y, args)
    gam, q = a["gam"], a["q"]
    r3 = SQRT3
    S12, S13, S23 = y.Sigma5[2], y.Sigma5[3], y.Sigma5[4]
    n1, n2, n3 = y.N3[0], y.N3[1], y.N3[2]
    w12, w13, w23 = gauge_W(y)
    s1, s2c, s3c = a["sig"]

    tn = n1 + n2 + n3
    b1 = 2.0*n1*n1 - tn*n1
    b2 = 2.0*n2*n2 - tn*n2
    b3 = 2.0*n3*n3 - tn*n3
    bm = (b1 + b2 + b3) / 3.0
    s3_1, s3_2, s3_3 = b1 - bm, b2 - bm, b3 - bm

    Pi = a["Pi_tot"]
    S12m, S13m, S23m = r3*S12, r3*S13, r3*S23
    c11 = 2.0*(w12*S12m + w13*S13m)
    c22 = 2.0*(-w12*S12m + w23*S23m)
    c33 = 2.0*(-w13*S13m - w23*S23m)
    c12 = w12*(s2c - s1) + w13*S23m + w23*S13m
    c13 = w13*(s3c - s1) + w12*S23m - w23*S12m
    c23 = w23*(s3c - s2c) - w12*S13m - w13*S12m
    d11 = -(2.0 - q)*s1 - s3_1 + Pi[0, 0] + c11
    d22 = -(2.0 - q)*s2c - s3_2 + Pi[1, 1] + c22
    d33 = -(2.0 - q)*s3c - s3_3 + Pi[2, 2] + c33
    d12 = -(2.0 - q)*S12m + Pi[0, 1] + c12
    d13 = -(2.0 - q)*S13m + Pi[0, 2] + c13
    d23 = -(2.0 - q)*S23m + Pi[1, 2] + c23
    dSigma5 = jnp.stack([-d11/2.0, (d22 - d33)/(2.0*r3),
                         d12/r3, d13/r3, d23/r3])
    dN3 = jnp.stack([(q + 2.0*s1)*n1, (q + 2.0*s2c)*n2, (q + 2.0*s3c)*n3])

    # 성분별: dΩ_c (U4 — 분모 G₊, A=0 ⇒ Adv=0), dv_c
    V2, Gp, Gm, SV2 = a["V2"], a["Gp"], a["Gm"], a["SV2"]
    dOm = (y.Om / Gp) * (2.0*q - (3.0*gam - 2.0)
                         + (2.0*q*(gam - 1.0) - (2.0 - gam))*V2
                         - gam*SV2)
    T = ((3.0*gam - 4.0)*(1.0 - V2) + (2.0 - gam)*SV2) / Gm      # (NC,)
    S = a["S"]
    Sv = jnp.einsum("ab,cb->ca", S, y.V)
    Wv = jnp.stack([w12*y.V[:, 1] + w13*y.V[:, 2],
                    -w12*y.V[:, 0] + w23*y.V[:, 2],
                    -w13*y.V[:, 0] - w23*y.V[:, 1]], axis=1)
    Nv = y.V * jnp.array([n1, n2, n3])[None, :]        # (Nv)_ca = N_a v_ca (n 대각)
    P = jnp.cross(y.V, Nv)
    dV = T[:, None]*y.V - Sv + Wv - P
    # H'2: 성분간 운동량 교환 (경로 1 — 닫힌식).  δdΩ = 0 (I⁰=0 유도).
    if args.get("kappa") is not None:
        from bianchi.matter import exchange as EX
        k = EX.validate_kappa(args["kappa"], y.nc)
        R = EX.exchange_R(y.Om, y.V, k)
        dV = dV + EX.delta_dv_closed(gam, y.Om, y.V, R)
    return StateATM(dSigma5, dN3, dOm, dV)


def rhs_via_general(tau, y: StateATM, args) -> StateATM:
    """경로 2 — charts.general + matter.fluid 합성 (독립 산술 경로)."""
    from bianchi.charts import general as G
    from bianchi.matter import fluid as F
    a = aux(y, args)
    S = a["S"]
    N = jnp.diag(y.N3)
    A = jnp.zeros(3)
    R = gauge_R(y)
    fluids = [F.TiltedFluid.of(a["gam"][c], y.Om[c], y.V[c])
              for c in range(y.nc)]
    srcs = [F.sources(f, S, A) for f in fluids]
    q = F.deceleration(a["Sigma2"], [(s, float(a["gam"][c]))
                                     for c, s in enumerate(srcs)])
    Pi_tot = sum(s["Pi"] for s in srcs)
    gargs = dict(gamma=a["gam"][0], q=q, Omega=jnp.sum(y.Om), Pi=Pi_tot, R=R)
    dG = G.rhs(tau, G.StateG(S, N, A), gargs)
    dS = dG.Sigma
    r3 = SQRT3
    dSigma5 = jnp.stack([-dS[0, 0]/2.0, (dS[1, 1] - dS[2, 2])/(2.0*r3),
                         dS[0, 1]/r3, dS[0, 2]/r3, dS[1, 2]/r3])
    dN3 = jnp.stack([dG.N[0, 0], dG.N[1, 1], dG.N[2, 2]])
    dOm = jnp.stack([F.dOmega(f, s, q) for f, s in zip(fluids, srcs)])
    dV = jnp.stack([F.dv_general(f, s, S, N, A, R)
                    for f, s in zip(fluids, srcs)])
    # H'2: 교환 (경로 2 — 야코비안 선형해; 닫힌식 무사용).
    if args.get("kappa") is not None:
        from bianchi.matter import exchange as EX
        k = EX.validate_kappa(args["kappa"], y.nc)
        Rx = EX.exchange_R(y.Om, y.V, k)
        dV = dV + EX.delta_dv_linsolve(a["gam"], y.Om, y.V, Rx)
    return StateATM(dSigma5, dN3, dOm, dV)


def constraints(y: StateATM, args):
    """잔차 2종: Gauss (Ω 비소거 설계의 감시량) + **총** Codazzi."""
    from bianchi.conventions import codazzi_residual
    a = aux(y, args)
    N = jnp.diag(y.N3)
    cod = codazzi_residual(a["S"], N, jnp.zeros(3), a["q_tot"])
    return dict(gauss=a["gauss"], codazzi=cod)


def diagnostics(y: StateATM, args):
    """성분별 진단: G₋_c (편타 여유 — 성분마다 다른 면), V²_c, 게이지 |W|."""
    a = aux(y, args)
    w12, w13, w23 = gauge_W(y)
    return dict(G_minus=a["Gm"], V2=a["V2"],
                gauge_w_max=jnp.max(jnp.abs(jnp.stack([w12, w13, w23]))))


def whiplash_gaps(y: StateATM, gammas):
    """성분별 편타 감시량 (NC,) — G₋_c = 1 − (γ_c−1)V_c²."""
    gam = jnp.asarray(gammas, jnp.float64)
    V2 = jnp.sum(y.V * y.V, axis=1)
    return G_minus(gam, V2)
