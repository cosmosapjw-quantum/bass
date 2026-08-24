"""
Self-contained coordinate-basis verifier for two disputed Bianchi equation sets.
NOTHING is imported from /home/claude/restore/bianchi-solver (audit or bianchi).

Conventions (fixed by the task):
  signature (-,+,+,+), eps_123 = +1,
  C^a_bc = eps_bcd n^{da} + a_b delta^a_c - a_c delta^a_b   (n symmetric, n.a=0)
  [e0_hat, ea_hat] = -(H delta_a^b + sigma_a^b + Omega_a^b) eb_hat,
  Omega_ab = eps_abc R^c.

Coordinate realization (type VI_h flavor):
  omega^1 = dx, (omega^2, omega^3)^T = exp(x M)(dy,dz)^T,
  M = [[A0, n3], [-n2, A0]],  A0=0.3, n2=0.7, n3=-0.4.
Metric: g = -dt^2 + sum_i b_i(t)^2 omega^i (x) omega^i,
  b(t) = (1+0.3t, 1-0.2t+0.1t^2, 1+0.1t+0.05t^2).
Orthonormal frame: e0_hat = d_t, ea_hat = e_a / b_a  (base frame);
a supplementary time-rotated frame ea'_hat = Lam(t)_ab eb_hat activates R != 0.
"""
import numpy as np
from jax import config
config.update("jax_enable_x64", True)
import jax
import jax.numpy as jnp
from jax import jacfwd, jvp

# ------------------------------------------------------------------ constants
A0, N2, N3 = 0.3, 0.7, -0.4
T0 = 0.2
X0 = jnp.array([0.2, 0.15, 0.30, -0.20])       # test event (t, x, y, z)
X0ALT = jnp.array([0.2, -0.40, 1.10, 0.70])    # same t, different spatial point

_E = np.zeros((3, 3, 3))
for (i, j, k), s in {(0, 1, 2): 1, (1, 2, 0): 1, (2, 0, 1): 1,
                     (0, 2, 1): -1, (2, 1, 0): -1, (1, 0, 2): -1}.items():
    _E[i, j, k] = s
EPS = jnp.asarray(_E)                          # eps_{abc}, eps_123 = +1

ETA = jnp.diag(jnp.array([-1.0, 1.0, 1.0, 1.0]))

maxabs = lambda A: float(jnp.max(jnp.abs(jnp.asarray(A))))

# ------------------------------------------------------- coordinate co-frame
MMAT = jnp.array([[A0, N3], [-N2, A0]])
assert N2 * N3 < 0.0  # hyperbolic branch below

def expxM(x):
    """exp(x M) closed form: M = A0*I + S, S=[[0,n3],[-n2,0]], S^2 = -n2*n3*I > 0."""
    kap = jnp.sqrt(-N2 * N3)
    S = jnp.array([[0.0, N3], [-N2, 0.0]])
    return jnp.exp(A0 * x) * (jnp.cosh(kap * x) * jnp.eye(2)
                              + (jnp.sinh(kap * x) / kap) * S)

def Wmat(x):
    """3x3 co-frame matrix: rows are omega^i in the basis (dx,dy,dz)."""
    W = jnp.zeros((3, 3)).at[0, 0].set(1.0)
    return W.at[1:, 1:].set(expxM(x))

def bvec(t):
    return jnp.array([1.0 + 0.3 * t,
                      1.0 - 0.2 * t + 0.1 * t * t,
                      1.0 + 0.1 * t + 0.05 * t * t])

def bdot(t):
    return jnp.array([0.3, -0.2 + 0.2 * t, 0.1 + 0.1 * t])

# ------------------------------------------------------- orthonormal frames
def Theta_base(X):
    """Orthonormal co-frame, rows theta^A (A=0..3), cols mu: theta^0=dt, theta^a=b_a omega^a."""
    t, x = X[0], X[1]
    Th = jnp.zeros((4, 4)).at[0, 0].set(1.0)
    return Th.at[1:, 1:].set(bvec(t)[:, None] * Wmat(x))

WROT = jnp.array([0.25, -0.35, 0.40])   # supplementary rotation axis*rate

def Lam(t):
    """SO(3) rotation exp(t K(WROT)) via Rodrigues."""
    w = jnp.linalg.norm(WROT)
    k = WROT / w
    K = jnp.array([[0.0, -k[2], k[1]], [k[2], 0.0, -k[0]], [-k[1], k[0], 0.0]])
    th = w * t
    return jnp.eye(3) + jnp.sin(th) * K + (1.0 - jnp.cos(th)) * (K @ K)

def Theta_rot(X):
    """Time-rotated orthonormal co-frame: theta'^a = Lam(t)_ab theta^b (same metric)."""
    t, x = X[0], X[1]
    Th = jnp.zeros((4, 4)).at[0, 0].set(1.0)
    return Th.at[1:, 1:].set(Lam(t) @ (bvec(t)[:, None] * Wmat(x)))

def make_gfun(ThetaFun):
    def gfun(X):
        Th = ThetaFun(X)
        return Th.T @ ETA @ Th
    return gfun

# ------------------------------------- structure constants: extraction tools
def extract_na(C):
    """From C[k,i,j] = C^k_ij (0-based spatial) extract a_b = (1/2) C^a_ba and
    n^{ea} = (1/4)(eps^{ebc} C^a_bc + eps^{abc} C^e_bc)."""
    a = 0.5 * jnp.einsum('aba->b', C)
    t1 = jnp.einsum('ebc,abc->ea', EPS, C)
    n = 0.25 * (t1 + t1.T)
    return n, a

def reconstruct_C(n, a):
    """C^a_bc = eps_bcd n^{da} + a_b delta^a_c - a_c delta^a_b."""
    I3 = jnp.eye(3)
    return (jnp.einsum('bcd,da->abc', EPS, n)
            + jnp.einsum('b,ac->abc', a, I3)
            - jnp.einsum('c,ab->abc', a, I3))

def struct_consts_3d(x3):
    """Numerical Lie brackets of the invariant frame e_i (3D, t absent):
    returns C[k,i,j] with [e_i,e_j] = C^k_ij e_k."""
    fr = lambda q: jnp.linalg.inv(Wmat(q[0]))          # cols = e_i components
    Ev = fr(x3)                                        # Ev[j,i] = e_i^j
    J = jacfwd(fr)(x3)                                 # J[j,i,l] = d_l e_i^j
    br = jnp.einsum('li,mjl->mij', Ev, J) - jnp.einsum('lj,mil->mij', Ev, J)
    return jnp.einsum('km,mij->kij', Wmat(x3[0]), br)

# --------------------------------------------- 4D frame data (all numerical)
def frame_bracket_coeffs(ThetaFun, X):
    """coeff[C,A,B]: [ehat_A, ehat_B] = coeff^C_{AB} ehat_C, brackets by autodiff."""
    inv_fun = lambda Y: jnp.linalg.inv(ThetaFun(Y))    # cols = ehat_A components
    Eh = inv_fun(X)                                    # Eh[mu,A]
    J = jacfwd(inv_fun)(X)                             # J[mu,A,rho]
    br = jnp.einsum('nA,mBn->mAB', Eh, J) - jnp.einsum('nB,mAn->mAB', Eh, J)
    return jnp.einsum('Cm,mAB->CAB', ThetaFun(X), br)

def frame_data(ThetaFun, X):
    """Extract H, sigma, Omega, R, nhat, ahat + consistency residuals at event X."""
    coeff = frame_bracket_coeffs(ThetaFun, X)
    # [e0,ea] = -(H d + sigma + Omega)_a^b eb  => coeff[b,0,a] = -(...)_ab
    K = -coeff[1:, 0, 1:].T                            # K[a,b] = H d_ab + sig_ab + Om_ab
    H = jnp.trace(K) / 3.0
    sig = 0.5 * (K + K.T) - H * jnp.eye(3)
    Om = 0.5 * (K - K.T)                               # Om_ab = eps_abc R^c
    R = 0.5 * jnp.einsum('cab,ab->c', EPS, Om)
    Chat = coeff[1:, 1:, 1:]                           # frame spatial structure fns
    nhat, ahat = extract_na(Chat)
    checks = {
        'e0-component of [e0,ea]': maxabs(coeff[0, 0, 1:]),
        'e0-component of [ea,eb]': maxabs(coeff[0, 1:, 1:]),
        'C(nhat,ahat) - Chat': maxabs(reconstruct_C(nhat, ahat) - Chat),
        'nhat @ ahat': maxabs(nhat @ ahat),
    }
    return dict(H=H, sig=sig, Om=Om, R=R, nhat=nhat, ahat=ahat,
                Chat=Chat, K=K, checks=checks)

# ------------------------------------------------------ geodesics (claim 1)
def make_christoffel(gfun):
    def chris(X):
        ginv = jnp.linalg.inv(gfun(X))
        dg = jacfwd(gfun)(X)                           # dg[m,n,r] = d_r g_mn
        T = jnp.transpose(dg, (0, 2, 1)) + dg - jnp.transpose(dg, (2, 0, 1))
        return 0.5 * jnp.einsum('mn,nab->mab', ginv, T)
    return chris

def metricity_residual(gfun, X):
    """nabla_r g_mn identity check (validates Christoffel index order)."""
    chris = make_christoffel(gfun)
    G = chris(X)
    dg = jacfwd(gfun)(X)
    term = (jnp.einsum('srm,sn->mnr', G, gfun(X))
            + jnp.einsum('srn,ms->mnr', G, gfun(X)))
    return maxabs(dg - term)

def make_geo_rhs(chris):
    def rhs(s):
        X, p = s[:4], s[4:]
        dp = -jnp.einsum('mab,a,b->m', chris(X), p, p)
        return jnp.concatenate([p, dp])
    return rhs

def rk4_step(f, s, h):
    k1 = f(s); k2 = f(s + 0.5 * h * k1); k3 = f(s + 0.5 * h * k2); k4 = f(s + h * k3)
    return s + (h / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)

def Pquad(v, nhat, ahat):
    """P^a(x) = a^a |x|^2 - (a.x) x^a + eps^a_bc x^b (n x)^c."""
    return (ahat * (v @ v) - (ahat @ v) * v
            + jnp.einsum('abc,b,c->a', EPS, v, nhat @ v))

def claim1_test(ThetaFun, X, dirn, E0=1.0, hs=(1e-6, 5e-7)):
    """Numeric d/dt of (E, P^a) along an exact coordinate null geodesic vs CLAIM 1.
    Returns dict of residuals and raw numbers."""
    gfun = make_gfun(ThetaFun)
    chris = make_christoffel(gfun)
    rhs = make_geo_rhs(chris)
    Eh = jnp.linalg.inv(ThetaFun(X))
    p0 = E0 * (Eh[:, 0] + Eh[:, 1:] @ dirn)
    s0 = jnp.concatenate([X, p0])
    null0 = float(p0 @ gfun(X) @ p0)
    proj = lambda s: ThetaFun(s[:4]) @ s[4:]           # (E, P^1..3) frame components
    pf0 = proj(s0)

    fd = frame_data(ThetaFun, X)
    H, sig, Om, R, nhat, ahat = fd['H'], fd['sig'], fd['Om'], fd['R'], fd['nhat'], fd['ahat']
    dE_claim = -pf0[0] * (H + dirn @ sig @ dirn)
    dP_claim = (-(H * jnp.eye(3) + sig - Om) @ pf0[1:]
                - pf0[0] * Pquad(dirn, nhat, ahat))
    claim = jnp.concatenate([jnp.array([dE_claim]), dP_claim])

    # exact derivative along the ray (chain rule through the projection, jax jvp)
    _, dpf = jvp(proj, (s0,), (rhs(s0),))
    exact = dpf / p0[0]                                # d/dt = (1/p^t) d/dlambda

    # finite-difference route: RK4 tiny step +-h, re-project at the NEW event
    fds = {}
    for h in hs:
        sp = rk4_step(rhs, s0, +h)
        sm = rk4_step(rhs, s0, -h)
        fds[h] = (proj(sp) - proj(sm)) / (2.0 * h) / p0[0]
    h1, h2 = hs
    rich = (4.0 * fds[h2] - fds[h1]) / 3.0             # Richardson h, h/2

    return dict(null=null0, pf0=pf0, claim=claim, exact=exact, fds=fds, rich=rich,
                res_exact=maxabs(exact - claim),
                res_fd={h: maxabs(v - claim) for h, v in fds.items()},
                res_rich=maxabs(rich - claim),
                fd_vs_exact={h: maxabs(v - exact) for h, v in fds.items()},
                P_vs_Edirn=maxabs(pf0[1:] - pf0[0] * dirn))

# ------------------------------------------------------- Maxwell (claim 2)
def Fhat_mat(E, B):
    """Frame components: Fhat_{0a} = -E_a, Fhat_{ab} = eps_abc B^c."""
    Z = jnp.zeros((4, 4)).at[0, 1:].set(-E).at[1:, 0].set(E)
    Bm = jnp.array([[0.0, B[2], -B[1]],
                    [-B[2], 0.0, B[0]],
                    [B[1], -B[0], 0.0]])
    return Z.at[1:, 1:].set(Bm)

def make_Ffun(ThetaFun, E0, B0, Ed, Bd, t0):
    """Coordinate F_{mu nu}(X) from frame fields E(t)=E0+Ed(t-t0), B(t)=B0+Bd(t-t0)."""
    def Ffun(X):
        dt = X[0] - t0
        Th = ThetaFun(X)
        return Th.T @ Fhat_mat(E0 + Ed * dt, B0 + Bd * dt) @ Th
    return Ffun

def divF(ThetaFun, Ffun, X):
    """D^nu = (1/s) d_mu (s F^{mu nu}), s = sqrt(-det g)."""
    gfun = make_gfun(ThetaFun)
    def sFup(Y):
        g = gfun(Y)
        gi = jnp.linalg.inv(g)
        s = jnp.sqrt(-jnp.linalg.det(g))
        return s * (gi @ Ffun(Y) @ gi)
    J = jacfwd(sFup)(X)                                # J[m,n,r] = d_r (sF^{mn})
    s0 = jnp.sqrt(-jnp.linalg.det(gfun(X)))
    return jnp.einsum('mnm->n', J) / s0

def dF_comps(Ffun, X, triples):
    """(dF)_{rho mu nu} = d_rho F_{mu nu} + d_mu F_{nu rho} + d_nu F_{rho mu}."""
    J = jacfwd(Ffun)(X)
    return jnp.array([J[m, n, r] + J[n, r, m] + J[r, m, n] for (r, m, n) in triples])

def Edot_solved(ThetaFun, X, E0v, B0v):
    """Solve the nu=spatial components of div F = 0 (linear in Edot) for Edot."""
    def Dspat(Ed):
        F = make_Ffun(ThetaFun, E0v, B0v, Ed, jnp.zeros(3), t0=X[0])
        return divF(ThetaFun, F, X)[1:]
    Nv = Dspat(jnp.zeros(3))
    M = jacfwd(Dspat)(jnp.zeros(3))
    Ed = -jnp.linalg.solve(M, Nv)
    return Ed, M, jnp.max(jnp.abs(Dspat(Ed)))

def Bdot_solved(ThetaFun, X, E0v, B0v):
    """Solve the (dF)_{0ij} components (linear in Bdot) for Bdot."""
    trips = [(0, 1, 2), (0, 1, 3), (0, 2, 3)]
    def Tcom(Bd):
        F = make_Ffun(ThetaFun, E0v, B0v, jnp.zeros(3), Bd, t0=X[0])
        return dF_comps(F, X, trips)
    Nv = Tcom(jnp.zeros(3))
    M = jacfwd(Tcom)(jnp.zeros(3))
    Bd = -jnp.linalg.solve(M, Nv)
    return Bd, M, jnp.max(jnp.abs(Tcom(Bd)))

crossm = lambda w: jnp.einsum('abc,b->ac', EPS, w)     # (w x V)_a = crossm(w) @ V

def claim2_candidates(fd):
    """Candidate evolution matrices. Edot = AE @ E + QX @ B, Bdot = AE @ B + PX @ E.
    NEW: curl X = nhat X + ahat x X ; OLD: curl X = nhat X - ahat x X."""
    H, sig, R, nhat, ahat = fd['H'], fd['sig'], fd['R'], fd['nhat'], fd['ahat']
    AE = -2.0 * H * jnp.eye(3) + sig + crossm(R)
    curl_new = nhat + crossm(ahat)
    curl_old = nhat - crossm(ahat)
    return AE, curl_new, curl_old
