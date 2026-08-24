"""
D1, D2, D3, D9, D10, D13, D14 --- transport equations.

Everything is read off the SAME frame connection that produced the v1.1
Einstein tensor, so no new convention is introduced.

  connection():  nabla_c e_b = Gamma^a_{bc} e_a          (einstein_frame.py)
  geodesic:      p^b nabla_b p^a = 0
                 => E d p^a/dt = -Gamma^a_{cb} p^c p^b   (homogeneous: e_alpha(.) = 0)
"""
import sympy as sp, numpy as np, itertools, json
from einstein_frame import einstein, jacobi_subs, eps, eta, I3, I4, t
from core import EPS, stf, sym, connection3

m = einstein(with_rotation=True)
H, n, a, s, R, Gam = m['H'], m['n'], m['a'], m['s'], m['R'], m['G']
out = {}

# ---------------------------------------------------------------- numeric layer
SY = [H] + [n[0, 0], n[0, 1], n[0, 2], n[1, 1], n[1, 2], n[2, 2]] \
     + [a[0], a[1], a[2]] + [s[0, 0], s[0, 1], s[0, 2], s[1, 1], s[1, 2]] \
     + [R[0], R[1], R[2]]
plain = {x: sp.Symbol('q%d' % i) for i, x in enumerate(SY)}
Gp = [[[sp.expand(Gam[i][j][k]).subs(plain, simultaneous=True) for k in I4]
       for j in I4] for i in I4]
fG = sp.lambdify(list(plain.values()), Gp, 'numpy')


def flat(Hv, N, A, S, Rv):
    return [Hv, N[0, 0], N[0, 1], N[0, 2], N[1, 1], N[1, 2], N[2, 2],
            A[0], A[1], A[2], S[0, 0], S[0, 1], S[0, 2], S[1, 1], S[1, 2],
            Rv[0], Rv[1], Rv[2]]


rng = np.random.default_rng(20260729)


def draw():
    N = sym(rng.normal(size=(3, 3)))
    w, V = np.linalg.eigh(N); k = int(np.argmin(abs(w))); w[k] = 0.0
    N = V @ np.diag(w) @ V.T
    A = float(rng.normal()) * V[:, k]
    return float(rng.uniform(0.5, 2.0)), N, A, stf(rng.normal(size=(3, 3))), rng.normal(size=3)


def Om_of(Rv):
    """Omega_ab = eps_abc R^c in ENGINE R.  NOTE (v1.3): the engine R is the\n    GENERATOR-convention vector, R_gen = -R_comm; all closed forms in this file\n    are stated in engine R.  In commutator (report) variables the rotation term\n    of every claim below reads +(R_comm x Y)_a.  See adjudicate_d19.py."""
    return np.einsum('abc,c->ab', EPS, Rv)


# ======================================================= D2 : connection blocks
e0, e1, e2, e3 = 0.0, 0.0, 0.0, 0.0
for _ in range(200):
    Hv, N, A, S, Rv = draw()
    G = np.array(fG(*flat(Hv, N, A, S, Rv)), float)
    K = Hv * np.eye(3) + S                                   # extrinsic curvature
    Om = Om_of(Rv)
    e0 = max(e0, abs(G[0][0][0]))                            # Gamma^0_00
    e1 = max(e1, float(np.abs(np.array([[G[0][i + 1][j + 1] for j in I3]
                                        for i in I3]) - K).max()))       # Gamma^0_ab
    e2 = max(e2, float(np.abs(np.array([[G[i + 1][0][j + 1] for j in I3]
                                        for i in I3]) - K).max()))       # Gamma^a_0b
    e3 = max(e3, float(np.abs(np.array([[G[i + 1][j + 1][0] for j in I3]
                                        for i in I3]) + Om).max()))      # Gamma^a_b0
out['D2_Gamma0_00_is_zero'] = e0
out['D2_Gamma0_ab_equals_K'] = e1
out['D2_Gammaa_0b_equals_K'] = e2
out['D2_Gammaa_b0_equals_minus_Omega'] = e3

# spatial block = 3d Levi-Civita connection
e4a, e4b = 0.0, 0.0
for _ in range(200):
    Hv, N, A, S, Rv = draw()
    G = np.array(fG(*flat(Hv, N, A, S, Rv)), float)
    G3 = np.array([[[G[i + 1][j + 1][k + 1] for k in I3] for j in I3] for i in I3])
    C3 = connection3(N, A)
    e4a = max(e4a, float(np.abs(G3 - C3).max()))
    e4b = max(e4b, float(np.abs(G3 - np.einsum('abc->acb', C3)).max()))
out['D2_spatial_block_vs_core_order_abc'] = e4a
out['D2_spatial_block_vs_core_order_acb'] = e4b
out['D2_spatial_block_is_3d_connection'] = min(e4a, e4b)
out['D2_note'] = ('core.connection3 stores Gamma^c_{ab} with the last two slots in the '
                  'opposite order to einstein_frame.connection (order pinned per-order '
                  'above, v1.3 audit fix F9).  Downstream consumers that need the '
                  'asymmetric single contraction (screen transport) now use the FULL '
                  '4d engine Gamma directly, so the order ambiguity is quarantined '
                  'to core.connection3 whose only uses are symmetric contractions.')

# ======================================================= D9/D13 : geodesic
def geo_rhs(Hv, N, A, S, Rv, E, P):
    """E dp^a/dt = -Gamma^a_{cb} p^c p^b   with p = (E, P)."""
    G = np.array(fG(*flat(Hv, N, A, S, Rv)), float)
    p = np.concatenate([[E], P])
    acc = -np.einsum('acb,c,b->a', G, p, p)
    return acc[0] / E, acc[1:] / E                            # dE/dt, dP/dt


def P_of(N, A, x):
    """^3Gamma^a_{bc} x^b x^c  (verified closed form, v1.1 eq. P_a)."""
    x2 = float(x @ x)
    return A * x2 - float(A @ x) * x + np.einsum('abc,b,c->a', EPS, x, N @ x)


eE, eP, eEm, ePm = 0.0, 0.0, 0.0, 0.0
for _ in range(300):
    Hv, N, A, S, Rv = draw()
    Om = Om_of(Rv)
    # ---- photon
    nh = rng.normal(size=3); nh /= np.linalg.norm(nh)
    E = float(rng.uniform(0.3, 3.0)); Pv = E * nh
    dE, dP = geo_rhs(Hv, N, A, S, Rv, E, Pv)
    eE = max(eE, abs(dE + E * (Hv + nh @ (S @ nh))))
    claim = -(Hv * np.eye(3) + S - Om) @ Pv - E * P_of(N, A, nh)
    eP = max(eP, float(np.abs(dP - claim).max()))
    # ---- massive particle
    mass = float(rng.uniform(0.1, 2.0))
    Pv = rng.normal(size=3)
    Em = np.sqrt(mass ** 2 + Pv @ Pv)
    dEm, dPm = geo_rhs(Hv, N, A, S, Rv, Em, Pv)
    eEm = max(eEm, abs(dEm + (Hv * (Pv @ Pv) + Pv @ (S @ Pv)) / Em))
    claim_m = -(Hv * np.eye(3) + S - Om) @ Pv - P_of(N, A, Pv) / Em
    ePm = max(ePm, float(np.abs(dPm - claim_m).max()))
out['D13_photon_dE_dt'] = eE
out['D13_photon_dP_dt'] = eP
out['D9_massive_dE_dt'] = eEm
out['D9_massive_dP_dt'] = ePm

# ---- |n|=1 preserved, and the direction equation
en, edir = 0.0, 0.0
for _ in range(300):
    Hv, N, A, S, Rv = draw(); Om = Om_of(Rv)
    nh = rng.normal(size=3); nh /= np.linalg.norm(nh)
    E = 1.7; dE, dP = geo_rhs(Hv, N, A, S, Rv, E, E * nh)
    dn = dP / E - nh * dE / E                                  # d n / dt
    en = max(en, abs(nh @ dn))                                 # must be 0
    claim = -(S @ nh - (nh @ (S @ nh)) * nh) + Om @ nh - P_of(N, A, nh) \
        + (nh @ P_of(N, A, nh)) * nh
    edir = max(edir, float(np.abs(dn - claim).max()))
out['D13_norm_preserved'] = en
out['D13_direction_equation'] = edir

# ---- FLRW limit
efl = 0.0
for _ in range(50):
    Hv = float(rng.uniform(0.5, 2.0))
    Z3 = np.zeros((3, 3)); z3 = np.zeros(3)
    nh = rng.normal(size=3); nh /= np.linalg.norm(nh)
    dE, dP = geo_rhs(Hv, Z3, z3, Z3, z3, 1.0, nh)
    efl = max(efl, abs(dE + Hv), float(np.abs(dP + Hv * nh).max()))
out['D13_FLRW_limit'] = efl

# ======================================================= D10/D14 : Bianchi I
# exact: covariant components p_i const in the coordinate basis; check numerically
def bianchi_I_check(nsteps=20000, T=1.5):
    """integrate the frame equations for diagonal Bianchi I and compare with
       the exact solution E(t) = sqrt(sum (p_i/a_i)^2), p_i = const."""
    Sd = np.array([0.4, -0.1, -0.3])
    Hv0 = 1.0
    dt = T / nsteps
    lna = np.zeros(3); Hv = Hv0
    Sig = Sd.copy()
    nh = np.array([0.3, -0.5, 0.81]); nh /= np.linalg.norm(nh)
    E = 1.0
    P = E * nh
    p_cov0 = P * np.exp(lna)                       # p_i = a_i P^i  (Bianchi I)
    worst = 0.0
    for _ in range(nsteps):
        S = np.diag(Sig * Hv)
        dE, dP = geo_rhs(Hv, np.zeros((3, 3)), np.zeros(3), S, np.zeros(3), E, P)
        # vacuum + shear only: Hdot = -H^2 - (1/3) sum sigma_i^2
        sig = Sig * Hv
        Hd = -Hv ** 2 - (sig @ sig) / 3.0
        sd = -3 * Hv * sig                          # ^3S = 0 for type I
        E += dt * dE; P += dt * dP
        lna += dt * (Hv + sig)
        Hv += dt * Hd; sig += dt * sd
        Sig = sig / Hv
        p_cov = P * np.exp(lna)
        worst = max(worst, float(np.abs(p_cov / p_cov0 - 1).max()))
    return worst


out['D10_bianchiI_covariant_momentum_const'] = bianchi_I_check()

# ======================================================= D2/D1 : triad transport
def struct_from_E(Emat, C_inv):
    """C^alpha_{beta gamma} from the invariant-basis C^i_{jk} and the triad."""
    Ei = np.linalg.inv(Emat)
    return np.einsum('ai,jb,kc,ijk->abc', Emat, Ei, Ei, C_inv)


def na_from_C(C):
    A_ = 0.5 * np.einsum('aba->b', C)
    Nn = sym(0.5 * np.einsum('dbg,abg->da', EPS, C))
    return Nn, A_


def make_lie_algebra(Nn, A_):
    """C[a][b][c] = C^a_{bc} = eps_{bcd} n^{da} + a_b d^a_c - a_c d^a_b."""
    return np.array([[[sum(EPS[b, c, d] * Nn[d, aa] for d in I3)
                       + A_[b] * (aa == c) - A_[c] * (aa == b)
                       for c in I3] for b in I3] for aa in I3])


eW = {}
for sign in (+1.0, -1.0):
    worst = 0.0
    for _ in range(120):
        Hv, N0, A0, S, Rv = draw()
        Om = Om_of(Rv)
        C_on = make_lie_algebra(N0, A0)                 # ON-frame structure constants
        Emat = np.eye(3)
        C_inv = C_on.copy()                             # take invariant basis = ON at t=0
        # transport:  dE/dt = (H I + sigma + sign*Omega) E
        h = 1e-6
        Ep = Emat + h * (Hv * np.eye(3) + S + sign * Om) @ Emat
        Em_ = Emat - h * (Hv * np.eye(3) + S + sign * Om) @ Emat
        Np, Ap = na_from_C(struct_from_E(Ep, C_inv))
        Nm, Am = na_from_C(struct_from_E(Em_, C_inv))
        dN = (Np - Nm) / (2 * h); dA = (Ap - Am) / (2 * h)
        # v1.1 verified closed forms
        dN_ref = (-Hv * N0 + (S @ N0 + N0 @ S)
                  + np.einsum('ab,bc->ac', Om, N0) + np.einsum('ac,bc->ab', N0, Om))
        dA_ref = -Hv * A0 - S @ A0 + Om @ A0
        worst = max(worst, float(np.abs(dN - dN_ref).max()),
                    float(np.abs(dA - dA_ref).max()))
    eW[f'W = {sign:+.0f} * Omega'] = worst
out['D2_triad_rotation_sign_scan'] = eW

# det E = e^{3 tau}
d3 = 0.0
for _ in range(100):
    Hv, N0, A0, S, Rv = draw(); Om = Om_of(Rv)
    M = Hv * np.eye(3) + S + Om
    d3 = max(d3, abs(np.trace(M) - 3 * Hv))
out['D1_trace_of_transport_is_3H'] = d3

print(json.dumps(out, indent=2, default=str))
json.dump(out, open('d_transport.json', 'w'), indent=2, default=str)
