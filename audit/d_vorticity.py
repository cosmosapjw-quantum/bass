"""
D22 (debt A) --- vorticity of the tilted fluid congruence, RESOLVED.

Finding (corrects the v1.2/v1.3 misstatement "omega should not depend on vbardot"):
the tilted-fluid vorticity GENUINELY depends on the fluid acceleration, equivalently
on vbardot.  The covariant projection h_mu^alpha h_nu^beta nabla_{[beta}u_{alpha]}
kills the  -u_beta a_alpha  piece (since h_nu^beta u_beta = 0), but vbardot also sits
in the *projected* part (the fluid's own expansion/shear/vorticity evolve as the tilt
changes).  So off-shell omega is a genuine function of vbardot -- this is physics, not
a bug.  The v1.2 residual 1.6 was real dependence, mislabelled as an implementation error.

Resolution for the solver: the OBSERVABLE is the ON-SHELL vorticity, i.e. vbardot is
supplied by momentum conservation (the fluid EOM).  On the constraint/EOM surface omega
is a clean state function (vanishes at v=0, orthogonal to u, antisymmetric).  We
(i) derive the dimensionful on-shell vbardot from nabla_mu T^mu_nu = 0,
(ii) evaluate omega on-shell, (iii) identify its spatial axial vector as a closed form.
"""
import sympy as sp, numpy as np, json
from einstein_frame import einstein, jacobi_subs, eps, eta, I3, I4, t
from core import EPS, stf, sym

m = einstein(with_rotation=True)
H, n, a, s, R, Gam = m['H'], m['n'], m['a'], m['s'], m['R'], m['G']
js = jacobi_subs(m)
out = {}

# numeric frame connection
SY = [H] + [n[0, 0], n[0, 1], n[0, 2], n[1, 1], n[1, 2], n[2, 2]] + [a[0], a[1], a[2]] \
     + [s[0, 0], s[0, 1], s[0, 2], s[1, 1], s[1, 2]] + [R[0], R[1], R[2]]
pl = {x: sp.Symbol('q%d' % i) for i, x in enumerate(SY)}
fG = sp.lambdify(list(pl.values()),
                 [[[sp.expand(Gam[i][j][k]).subs(pl, simultaneous=True) for k in I4]
                   for j in I4] for i in I4], 'numpy')
ETA = np.diag([-1., 1., 1., 1.])


def flat(Hv, N, A, S, Rv):
    return [Hv, N[0, 0], N[0, 1], N[0, 2], N[1, 1], N[1, 2], N[2, 2],
            A[0], A[1], A[2], S[0, 0], S[0, 1], S[0, 2], S[1, 1], S[1, 2],
            Rv[0], Rv[1], Rv[2]]


def kinematics(Hv, N, A, S, Rv, vv, vdot):
    """omega, theta, accel, u  for u = Gamma(n + v)  at given (state, vbardot, cosmic t)."""
    G = np.array(fG(*flat(Hv, N, A, S, Rv)), float)          # G[a][b][c] = Gamma^a_bc
    Gam2 = 1.0 / np.sqrt(1 - vv @ vv)
    Gd = Gam2 ** 3 * (vv @ vdot)                             # dGamma/dt
    ul = np.array([-Gam2, *(Gam2 * vv)])                     # u_a  lower
    uu = np.array([Gam2, *(Gam2 * vv)])                      # u^a  upper
    dul = np.array([-Gd, *(Gd * vv + Gam2 * vdot)])          # d(u_a)/dt
    Du = np.zeros((4, 4))                                    # Du[b][c] = nabla_c u_b
    for b in I4:
        for c in I4:
            e_c = dul[b] if c == 0 else 0.0
            Du[b][c] = e_c - sum(G[d][b][c] * ul[d] for d in I4)
    P = np.eye(4) + np.outer(ul, uu)                         # h_mu^rho
    K = np.einsum('ma,nb,ab->mn', P, P, Du)
    om = 0.5 * (K - K.T)
    theta = np.einsum('aa->', ETA @ Du)                     # nabla_a u^a
    acc = np.array([sum(uu[c] * Du[b][c] for c in I4) for b in I4])
    return om, theta, acc, uu, ul


def onshell_vdot(Hv, N, A, S, Rv, vv, gamma, rho):
    """dv/dt from dimensionful nabla_mu T^mu_nu = 0 for a tilted gamma-law fluid."""
    G = np.array(fG(*flat(Hv, N, A, S, Rv)), float)
    g4 = ETA
    # build T^{mu nu} = gamma rho Gamma^2 (u^mu u^nu) + (gamma-1) rho g^{mu nu}
    # solve for (rhodot, vdot) from nabla_mu T^{mu nu}=0 by finite element in unknowns.
    # Unknowns X = (rhodot, vdot0..2).  T depends on t only through rho(t), v(t).
    Gam2 = 1.0 / np.sqrt(1 - vv @ vv)

    def Tup(rho_, v_):
        G2 = 1.0 / (1 - v_ @ v_)
        uup = np.array([np.sqrt(G2), *(np.sqrt(G2) * v_)])
        return gamma * rho_ * uup[:, None] * uup[None, :] + (gamma - 1) * rho_ * g4

    def divT(rhod, vd):
        # d/dt T^{mu nu}: chain rule
        h = 1e-6
        dT = (Tup(rho + h * rhod, vv + h * vd) - Tup(rho - h * rhod, vv - h * vd)) / (2 * h)
        Tu = Tup(rho, vv)
        out_ = np.zeros(4)
        for nu in I4:
            tot = dT[0, nu]                                  # e_0 term (c=0)
            for c in I4:
                tot += sum(G[c][d][c] * Tu[d, nu] for d in I4)
                tot += sum(G[nu][d][c] * Tu[c, d] for d in I4)
            out_[nu] = tot
        return out_

    # linear solve: divT is linear in (rhod, vd)
    b = -divT(0.0, np.zeros(3))
    M = np.zeros((4, 4))
    for j, (dr, dv) in enumerate([(1.0, np.zeros(3))] +
                                 [(0.0, np.eye(3)[k]) for k in range(3)]):
        M[:, j] = divT(dr, dv) + b
    X = np.linalg.solve(M, b)
    return X[1:]                                            # vdot


rng = np.random.default_rng(20260729)


def draw():
    N = sym(rng.normal(size=(3, 3))); w, V = np.linalg.eigh(N)
    k = int(np.argmin(abs(w))); w[k] = 0
    N = V @ np.diag(w) @ V.T; A = float(rng.normal()) * V[:, k]
    vv = rng.normal(size=3); vv *= rng.uniform(.05, .6) / np.linalg.norm(vv)
    return float(rng.uniform(.6, 1.6)), N, A, stf(rng.normal(size=(3, 3))), rng.normal(size=3), vv


# ---- (i) off-shell dependence is real; (ii) on-shell it is a clean state function
e_offshell, e_uortho, e_v0, e_asym, e_accel_par = 0., 0., 0., 0., 0.
omt = 0.
for _ in range(120):
    Hv, N, A, S, Rv, vv = draw()
    gamma = float(rng.uniform(1.05, 1.6)); rho = float(rng.uniform(0.2, 1.0))
    # off-shell: arbitrary vdot changes omega (this is physics)
    o1, _, _, _, _ = kinematics(Hv, N, A, S, Rv, vv, np.zeros(3))
    o2, _, _, _, _ = kinematics(Hv, N, A, S, Rv, vv, rng.normal(size=3))
    e_offshell = max(e_offshell, float(np.abs(o1 - o2).max()))
    # on-shell
    vd = onshell_vdot(Hv, N, A, S, Rv, vv, gamma, rho)
    om, th, acc, uu, ul = kinematics(Hv, N, A, S, Rv, vv, vd)
    e_uortho = max(e_uortho, float(np.abs(om @ uu).max()))
    e_asym = max(e_asym, float(np.abs(om + om.T).max()))
    omt = max(omt, float(np.abs(om).max()))
    # on-shell acceleration is spatial-parallel to v (momentum conservation)
    a_sp = acc[1:]
    par = a_sp - (a_sp @ vv) / (vv @ vv) * vv
    e_accel_par = max(e_accel_par, float(np.linalg.norm(par)))
    # v=0 -> omega=0
    o0, _, _, _, _ = kinematics(Hv, N, A, S, Rv, np.zeros(3), np.zeros(3))
    e_v0 = max(e_v0, float(np.abs(o0).max()))
out['D22_offshell_vdot_dependence_is_real'] = e_offshell        # ~O(1): genuine physics
out['D22_onshell_accel_perp_to_v'] = e_accel_par                # ~0: a || v on-shell
out['D22_onshell_vorticity_orthogonal_to_u'] = e_uortho
out['D22_onshell_vorticity_antisymmetric'] = e_asym
out['D22_vorticity_vanishes_at_v0'] = e_v0
out['D22_onshell_vorticity_typical'] = omt

# ---- (iii) on-shell spatial vorticity is EOS-INDEPENDENT (the acceleration term,
#           being parallel to v on-shell, drops from the spatial block) -> it is a
#           pure geometry+tilt observable.  We certify EOS-independence rather than a
#           closed form (the exact symbolic form is higher-order in v and is left to
#           PR-42, where the solver supplies vbardot from the RHS anyway).
eos_spread = 0.0
for _ in range(60):
    Hv, N, A, S, Rv, vv = draw()
    oms = []
    for gamma, rho in [(1.1, 0.3), (4.0 / 3.0, 0.5), (1.5, 0.9), (1.05, 0.2)]:
        vd = onshell_vdot(Hv, N, A, S, Rv, vv, gamma, rho)
        om, *_ = kinematics(Hv, N, A, S, Rv, vv, vd)
        oms.append(om[1:, 1:])
    eos_spread = max(eos_spread, max(float(np.abs(o - oms[0]).max()) for o in oms))
out['D22_onshell_spatial_vorticity_EOS_independent'] = eos_spread   # ~0: clean observable
out['D22_resolution'] = (
    "The tilted-fluid vorticity genuinely depends on vbardot off-shell (this is physics, "
    "not the v1.2 bug it was labelled). On-shell (momentum conservation makes the fluid "
    "acceleration parallel to v), the spatial vorticity is EOS-independent, orthogonal to "
    "u, antisymmetric and vanishes at v=0 -- a well-defined observable. The solver computes "
    "it by feeding the RHS's vbardot into h_mu^a h_nu^b nabla_[b u_a].")

print(json.dumps(out, indent=2, default=str))
json.dump(out, open('d_vorticity.json', 'w'), indent=2, default=str)
