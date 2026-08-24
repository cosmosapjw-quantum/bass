"""
Bianchi background-solver audit core  (rebuilt 2026-07-29 after container reclaim).

Conventions fixed ONCE here and used everywhere:
  * signature (-,+,+,+), units 8 pi G = c = 1
  * spatial structure constants
        C^a_{bc} = eps_{bcd} n^{da} + a_b delta^a_c - a_c delta^a_b ,
        n^{ab} = n^{ba},   Jacobi:  n^{ab} a_b = 0
  * <ab> = symmetric trace-free part
  * Hubble normalisation (Wainwright-Ellis):
        Sigma_ab = sigma_ab / H,  N_ab = n_ab / H,  A_a = a_a / H,
        Omega = rho / (3 H^2),    d tau / dt = H
  * ROTATION (single convention, "commutator" R_comm):
        a time-dependent frame rotation  e~_a = R_ab e_b  contributes
        W = Rdot R^T ,  W_ab = - eps_abc R^c ,
        so a frame-fixed vector obeys   v~' = - R x v~
        and a frame-fixed tensor obeys  S~' = -(W S - S W) ... see rot_vec/rot_tensor.
"""
import numpy as np
from itertools import product

I3 = range(3)
EPS = np.zeros((3, 3, 3))
for i, j, k in product(I3, I3, I3):
    EPS[i, j, k] = ((i - j) * (j - k) * (k - i)) / 2.0
ID = np.eye(3)

# ---------------------------------------------------------------- basic algebra
def sym(M):
    M = np.asarray(M, float); return .5 * (M + M.T)


def stf(M):
    """symmetric trace-free part <ab>"""
    M = sym(M); return M - np.trace(M) * ID / 3.0


def gamma_of(N, A):
    """C^c_{ab} as g[c,a,b]."""
    N = np.asarray(N, float); A = np.asarray(A, float)
    g = np.zeros((3, 3, 3))
    for c, a, b in product(I3, I3, I3):
        g[c, a, b] = sum(EPS[a, b, d] * N[d, c] for d in I3) + A[a] * (c == b) - A[b] * (c == a)
    return g


def connection3(N, A):
    """Levi-Civita rotation coefficients in the orthonormal frame, as G[c, b, a].

    ★ INDEX CONVENTION (v1.4, debt C -- pinned to remove a latent trap).
      G[c, b, a] = Gamma^c_{ba} = <e^c, nabla_a e_b>  (a = DERIVATIVE slot, LAST).
      This is the TRANSPOSE, in the last two slots, of einstein_frame.connection,
      which stores Gamma^a_{bc} with c = derivative slot.  The frame connection is
      NOT symmetric in its two lower slots (torsion-free but the structure constants
      make Gamma_{[bc]} != 0), so the order MATTERS for any single contraction.

      SAFE USES (order-independent): the double contraction with a symmetric pair,
      e.g. P_a = Gamma^a_{bc} v^b v^c  (used by r5d_tilt_closed, d_transport), which
      only sees the symmetric part.  ricci3() below contracts consistently and is
      pinned by the S^3 anchor.
      UNSAFE: any single contraction (e.g. screen transport) -- use the full 4d
      einstein_frame connection there instead (d_optical does exactly this).
    """
    g = gamma_of(N, A)
    return 0.5 * (g - np.einsum('ijk->kij', g) + np.einsum('jki->kij', g))




def ricci3(N, A):
    """3-Ricci tensor from the structure constants alone (no coordinates).

    Uses connection3's [c, b, a] convention consistently.  Pinned by _pin_connection3().
    """
    g = gamma_of(N, A); G = connection3(N, A)
    return (np.einsum('mjk,iim->jk', G, G) - np.einsum('mik,ijm->jk', G, G)
            - np.einsum('mij,imk->jk', g, G))


def _pin_connection3():
    """Import-time guard (debt C): the unit 3-sphere n = 2*delta, a = 0 must give
    Ric = 2*delta and R = 6.  Fails loudly if the index convention ever drifts."""
    Ric = ricci3(2.0 * ID, np.zeros(3))
    assert np.allclose(Ric, 2.0 * ID, atol=1e-12), Ric
    assert abs(np.trace(Ric) - 6.0) < 1e-12


_pin_connection3()


# ------------------------------------------------------- explicit closed forms
def S3_explicit(N, A):
    """^3S_ab  =  2 N_<a^c N_b>c - (tr N) N_<ab>  +  2 eps_{cd<a} A^c N_b>^d ."""
    N = np.asarray(N, float); A = np.asarray(A, float)
    B = 2.0 * (N @ N) - np.trace(N) * N
    C = np.einsum('cda,c,bd->ab', EPS, A, N)
    return stf(B) + 2.0 * stf(C)


def R3_explicit(N, A):
    """^3R = -(1/2)[ 2 tr(N^2) - (tr N)^2 ] - 6 A.A ."""
    N = np.asarray(N, float); A = np.asarray(A, float)
    return -0.5 * (2.0 * np.trace(N @ N) - np.trace(N) ** 2) - 6.0 * float(A @ A)


# ------------------------------------------------------------------- rotations
def hat(R):
    """W_ab = -eps_abc R^c  (commutator convention)."""
    return -np.einsum('abc,c->ab', EPS, np.asarray(R, float))


def rot_vec(R, v):
    """contribution of a frame rotation to v' :  -(R x v)."""
    return hat(R) @ np.asarray(v, float)


def rot_tensor(R, S):
    """contribution of a frame rotation to S' for a rank-2 frame tensor."""
    W = hat(R); S = np.asarray(S, float)
    return W @ S + S @ W.T


# ---------------------------------------------------------- Jacobi-safe states
def rand_class_b(rng):
    """random (N, A) with n^{ab} a_b = 0 (Jacobi identity satisfied)."""
    N = sym(rng.normal(size=(3, 3)))
    w, V = np.linalg.eigh(N)
    k = int(np.argmin(abs(w))); w[k] = 0.0
    N = V @ np.diag(w) @ V.T
    A = rng.normal() * V[:, k]
    return N, A


def rand_class_a(rng):
    N = sym(rng.normal(size=(3, 3)))
    return N, np.zeros(3)
