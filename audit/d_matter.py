"""
D19, D20, D22 --- electromagnetic sector (E and B together) and the tilted
fluid congruence (expansion, acceleration, vorticity).

  F_{0a} = -E_a ,  F_{ab} = eps_{abc} B^c
  source-free Maxwell:  nabla_a F^{ab} = 0 ,  nabla_{[a} F_{bc]} = 0
  fluid congruence:     u = Gamma (n + v)
"""
import sympy as sp, numpy as np, itertools, json
from einstein_frame import einstein, jacobi_subs, eps, eta, I3, I4, t
from core import EPS, stf, sym

m = einstein(with_rotation=True)
H, n, a, s, R, Gam = m['H'], m['n'], m['a'], m['s'], m['R'], m['G']
js = jacobi_subs(m)
out = {}
ID = sp.eye(3)

# ============================================================ D19 : Maxwell
Ee = sp.Matrix(3, 1, lambda i, j: sp.Function(f'E{i}')(t))
Bb = sp.Matrix(3, 1, lambda i, j: sp.Function(f'B{i}')(t))
F = sp.zeros(4, 4)
for i in I3:
    F[0, i + 1] = -Ee[i]; F[i + 1, 0] = Ee[i]
for i, j in itertools.product(I3, I3):
    F[i + 1, j + 1] = sum(eps[i, j, k] * Bb[k] for k in I3)

Fup = sp.Matrix(4, 4, lambda i, j: sp.expand(
    sum(eta[i, p] * eta[j, q] * F[p, q] for p in I4 for q in I4)))


def div_up(T):
    """nabla_a T^{ab} for a rank-2 tensor with both indices up."""
    o = []
    for b in I4:
        tot = sp.Integer(0)
        for c in I4:
            tot += (sp.diff(T[c, b], t) if c == 0 else 0)
            tot += sum(Gam[c][d][c] * T[d, b] for d in I4)
            tot += sum(Gam[b][d][c] * T[c, d] for d in I4)
        o.append(sp.expand(tot))
    return o


def cov_d(Tlow, aa, bb, cc):
    """nabla_a F_bc  (components; e_alpha(.) = 0)."""
    val = sp.diff(Tlow[bb, cc], t) if aa == 0 else sp.Integer(0)
    val -= sum(Gam[d][bb][aa] * Tlow[d, cc] for d in I4)
    val -= sum(Gam[d][cc][aa] * Tlow[bb, d] for d in I4)
    return sp.expand(val)


amp = [x.subs(js, simultaneous=True) for x in div_up(Fup)]
bianchi_F = {}
for (aa, bb, cc) in itertools.combinations(range(4), 3):
    e = sp.expand(cov_d(F, aa, bb, cc) + cov_d(F, bb, cc, aa) + cov_d(F, cc, aa, bb))
    bianchi_F[(aa, bb, cc)] = e.subs(js, simultaneous=True)

Edot = [sp.Derivative(Ee[i], t) for i in I3]
Bdot = [sp.Derivative(Bb[i], t) for i in I3]

# --- solve: Ampere (spatial part of nabla F = 0) gives Edot; Faraday gives Bdot
sol_E = sp.solve([sp.Eq(x, 0) for x in amp[1:]], Edot, dict=True)
fara = [bianchi_F[k] for k in bianchi_F if 0 in k]
sol_B = sp.solve([sp.Eq(x, 0) for x in fara], Bdot, dict=True)
out['D19_Ampere_solvable'] = bool(sol_E)
out['D19_Faraday_solvable'] = bool(sol_B)

Om_s = sp.Matrix(3, 3, lambda i, j: sum(eps[i, j, k] * R[k] for k in I3))


def claim_dot(X, sign_curl):
    """-2H X + sigma.X + Omega.X + sign_curl * (curl-type structure constant terms)"""
    return [sp.expand(-2 * H * X[i] + sum(s[i, j] * X[j] for j in I3)
                      + sum(Om_s[i, j] * X[j] for j in I3)) for i in I3]


if sol_E:
    Ed = [sp.expand(sol_E[0][d]) for d in Edot]
    resid = [sp.simplify(Ed[i] - claim_dot(Ee, +1)[i]) for i in I3]
    out['D19_Edot_minus_transport_part'] = [str(x) for x in resid]
if sol_B:
    Bd = [sp.expand(sol_B[0][d]) for d in Bdot]
    resid = [sp.simplify(Bd[i] - claim_dot(Bb, -1)[i]) for i in I3]
    out['D19_Bdot_minus_transport_part'] = [str(x) for x in resid]

# --- constraints (the b=0 component of Ampere, and the purely spatial Bianchi)
out['D19_gauss_law_E'] = str(sp.simplify(amp[0]))
spatial_bianchi = [v for k, v in bianchi_F.items() if 0 not in k]
out['D19_gauss_law_B'] = [str(sp.simplify(x)) for x in spatial_bianchi]

# --- E = 0 limit must reproduce the v1.1 magnetic equation
if sol_B:
    zeroE = {Ee[i]: 0 for i in I3}
    Bd0 = [sp.simplify(sp.expand(sol_B[0][Bdot[i]]).subs(zeroE, simultaneous=True))
           for i in I3]
    # v1.3 (감사 F3 판정): 엔진의 R 은 GENERATOR 규약 (R_gen = -R_comm) 이므로
    # v1.1 자기장식의 +(R_comm x B) 는 엔진 변수로 -(R_eng x B) 다.  이전 참조식은
    # 이 변환을 빠뜨려 -2(R x B) 잔차를 만들었다 (엔진도 코드도 옳았음 —
    # adjudicate_d19.py 로 확정: Bdot = -(R_eng x B) = +(R_comm x B)).
    ref = [sp.expand(-2 * H * Bb[i] + sum(s[i, j] * Bb[j] for j in I3)
                     - sum(eps[i, j, k] * R[j] * Bb[k] for j in I3 for k in I3))
           for i in I3]
    diff = [sp.simplify(Bd0[i] - ref[i]) for i in I3]
    out['D19_E0_limit_matches_v11_magnetic'] = [str(x) for x in diff]
    out['D19_E0_limit_max_residual'] = 0.0 if all(x == 0 for x in diff) else 1.0

# ============================================================ D22 : congruence
v = sp.Matrix(3, 1, lambda i, j: sp.Function(f'v{i}')(t))
V2 = sum(v[i] ** 2 for i in I3)
Gm = 1 / sp.sqrt(1 - V2)
u = sp.Matrix(4, 1, [Gm, Gm * v[0], Gm * v[1], Gm * v[2]])          # u^a
ul = sp.Matrix(4, 1, [-Gm, Gm * v[0], Gm * v[1], Gm * v[2]])        # u_a


def nabla_u(b, c):
    """nabla_c u_b."""
    val = sp.diff(ul[b], t) if c == 0 else sp.Integer(0)
    val -= sum(Gam[d][b][c] * ul[d] for d in I4)
    return sp.expand(val)


Du = sp.Matrix(4, 4, lambda b, c: nabla_u(b, c).subs(js, simultaneous=True))
theta_u = sp.expand(sum(eta[b, b] * Du[b, b] for b in I4))
acc = sp.Matrix(4, 1, lambda b, j: sp.expand(sum(u[c] * nabla_u(b, c) for c in I4)))

hproj = sp.Matrix(4, 4, lambda i, j: sp.expand(eta[i, j] + ul[i] * u[j] * 0
                                               + (ul[i] * ul[j] if False else 0)))
# h^a_b = delta^a_b + u^a u_b
hmix = sp.Matrix(4, 4, lambda i, j: sp.expand((1 if i == j else 0) + u[i] * ul[j]))

# vorticity  omega_{mu nu} = h_mu^alpha h_nu^beta nabla_{[beta} u_{alpha]}
# ★ v1.4 (부채 A): 이전엔 mixed 지표 h^d_b 로 짜서 투영이 자명해지고 raw
#   antisym gradient 만 남아 vbardot 에 의존했다.  올바른 투영기는
#   h_mu^rho = delta + u_mu u^rho (mu 하단/자유, rho 상단/더미).  완전 유도·판정은
#   audit/d_vorticity.py 에 있으며, 결론: 유체 vorticity 는 off-shell 에서 vbardot 에
#   **실제로 의존**하고 (v1.2 의 '버그' 라벨은 오개념), on-shell 에서 EOS-무관한
#   깨끗한 관측량이 된다.
P = sp.Matrix(4, 4, lambda mu, rho: sp.expand((1 if mu == rho else 0) + ul[mu] * u[rho]))
Aanti = sp.Matrix(4, 4, lambda sig, rho: sp.expand((Du[sig, rho] - Du[rho, sig]) / 2))
om = sp.Matrix(4, 4, lambda mu, nu: sp.expand(
    sum(P[mu, rho] * P[nu, sig] * Aanti[sig, rho] for rho in I4 for sig in I4)))

nv = {v[i]: 0 for i in I3}
out['D22_theta_at_v0'] = str(sp.simplify(theta_u.subs(nv, simultaneous=True)))
out['D22_acceleration_at_v0'] = [str(sp.simplify(acc[i].subs(nv, simultaneous=True)))
                                 for i in I4]
out['D22_vorticity_at_v0'] = str(sp.simplify(
    sum(om[i, j] ** 2 for i in I4 for j in I4).subs(nv, simultaneous=True)))

# numeric: vorticity is generically non-zero once tilted, and vanishes for v = 0
vd_ = [sp.Derivative(v[i], t) for i in I3]
SYc = [H] + [n[0, 0], n[0, 1], n[0, 2], n[1, 1], n[1, 2], n[2, 2]] \
      + [a[0], a[1], a[2]] + [s[0, 0], s[0, 1], s[0, 2], s[1, 1], s[1, 2]] \
      + [R[0], R[1], R[2]] + [v[0], v[1], v[2]] + vd_
plainc = {x: sp.Symbol('c%d' % i) for i, x in enumerate(SYc)}
f_om = sp.lambdify(list(plainc.values()),
                   [[sp.expand(om[i, j]).subs(plainc, simultaneous=True)
                     for j in I4] for i in I4], 'numpy')
f_th = sp.lambdify(list(plainc.values()),
                   sp.expand(theta_u).subs(plainc, simultaneous=True), 'numpy')
rng = np.random.default_rng(20260729)


def draw():
    N = sym(rng.normal(size=(3, 3)))
    w, V = np.linalg.eigh(N); k = int(np.argmin(abs(w))); w[k] = 0.0
    N = V @ np.diag(w) @ V.T
    A = float(rng.normal()) * V[:, k]
    vv = rng.normal(size=3); vv *= rng.uniform(0.05, 0.7) / np.linalg.norm(vv)
    return (float(rng.uniform(.5, 2.)), N, A, stf(rng.normal(size=(3, 3))),
            rng.normal(size=3), vv)


def fl(Hv, N, A, S, Rv, vv, vd=None):
    if vd is None:
        vd = np.zeros(3)
    return [Hv, N[0, 0], N[0, 1], N[0, 2], N[1, 1], N[1, 2], N[2, 2],
            A[0], A[1], A[2], S[0, 0], S[0, 1], S[0, 2], S[1, 1], S[1, 2],
            Rv[0], Rv[1], Rv[2], vv[0], vv[1], vv[2], vd[0], vd[1], vd[2]]


om0, omt, thv = 0.0, 0.0, []
for _ in range(120):
    Hv, N, A, S, Rv, vv = draw()
    om0 = max(om0, float(np.abs(np.array(f_om(*fl(Hv, N, A, S, Rv,
                                                  np.zeros(3))), float)).max()))
    omt = max(omt, float(np.abs(np.array(f_om(*fl(Hv, N, A, S, Rv, vv)),
                                         float)).max()))
    thv.append(float(f_th(*fl(Hv, N, A, S, Rv, vv))))
out['D22_vorticity_vanishes_for_v0'] = om0
edep = 0.0
for _ in range(60):
    Hv, N, A, S, Rv, vv = draw()
    o1 = np.array(f_om(*fl(Hv, N, A, S, Rv, vv, np.zeros(3))), float)
    o2 = np.array(f_om(*fl(Hv, N, A, S, Rv, vv, rng.normal(size=3))), float)
    edep = max(edep, float(np.abs(o1 - o2).max()))
out['D22_vorticity_independent_of_vdot'] = edep
out['D22_vorticity_typical_when_tilted'] = omt
out['D22_theta_u_range_when_tilted'] = [float(np.min(thv)), float(np.max(thv))]

# ============================================================ D21 : viscosity
# Eckart:  pi_ab = -2 eta sigma_ab ,  p -> p - zeta theta.
# entropy production  T Ds = 2 eta sigma_ab sigma^ab + zeta theta^2 >= 0
etaS, zetaS = sp.symbols('eta_s zeta_s', positive=True)
sig2 = sum(s[i, j] ** 2 for i in I3 for j in I3)
out['D21_entropy_production'] = str(sp.simplify(2 * etaS * sig2 + zetaS * (3 * H) ** 2))
out['D21_note'] = ('Eckart pi_ab = -2 eta sigma_ab feeds the Sigma equation as '
                   'Pi_ab = -2 (eta/H) Sigma_ab, i.e. a pure damping term; the '
                   'Israel-Stewart version promotes Pi_ab to its own variable with '
                   'tau_pi Pi_ab-dot + Pi_ab = -2 eta sigma_ab.')

print(json.dumps(out, indent=2, default=str))
json.dump(out, open('d_matter.json', 'w'), indent=2, default=str)
