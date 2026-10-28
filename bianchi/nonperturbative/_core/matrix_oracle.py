"""Bounded independent full Jones matrix exponential, plus history-assembly check.

The exponential does not call the rank-nine gain or Volterra implementation.
The uncompressed assembly is a separate discrete-history check sharing only the
verified analytic polynomial weights, not an independent physical model.
"""
import numpy as np
from scipy.linalg import expm
from .covariant_oracle import maps4, screen, lorentz

class PairwiseExponential:

    def __init__(self, n, w, J, beta, nu0):
        S, ne, D = maps4(n, beta)
        self.D = D
        self.E = screen(ne)
        self.we = w / D ** 2
        if len(n) > 128:
            raise ValueError('Dense oracle bounded to at most 128 directions')
        Y = D[:, None, None] ** 4 * np.einsum('nik,nkl,njl->nij', S, J, S)
        self.x0 = np.einsum('nia,nij,njb->nab', self.E, Y, self.E).ravel()
        O = np.einsum('nia,mib->nmab', self.E, self.E)
        A = 3 / (8 * np.pi) * np.einsum('nmac,nmbd->nabmcd', O, O)
        A *= (float(nu0) * D)[:, None, None, None, None, None] * self.we[None, None, None, :, None, None]
        self.matrix = A.reshape(4 * len(n), 4 * len(n)) - np.diag(np.repeat(nu0 * D, 4))
        L = lorentz(-np.asarray(beta))
        self.back = L[1:, 1:] - n[:, :, None] * L[0, 1:]

    def carrier(self, t):
        X = (expm(t * self.matrix) @ self.x0).reshape(-1, 2, 2)
        Ye = np.einsum('nia,nab,njb->nij', self.E, X, self.E)
        return np.einsum('nik,nkl,njl->nij', self.back, Ye, self.back) / self.D[:, None, None] ** 4

def uncompressed_source(op, J, nu0, T, panels):
    from .tilted_history import exponential_weights
    h = T / panels
    d = nu0 * op.D
    Y0 = op.to_electron(J)
    R = 3 / (8 * np.pi) * np.einsum('nac,ndb->nabcd', op.Pe, op.Pe).reshape(-1, 9, 9)
    W1 = exponential_weights(d * h, 1.0)
    B = [np.einsum('n,nj,nab->jab', op.we, exponential_weights(d * h, r), R) for r in (0.5, 1.0)]
    A = np.block([[np.eye(9) - B[0][1], -B[0][2]], [-B[1][1], np.eye(9) - B[1][2]]])
    rows = []
    M0 = op.source(J)
    for k in range(panels):
        start = M0 if k == 0 else rows[-1][2]
        rhs = []
        for r, block in zip((0.5, 1.0), B):
            t = (k + r) * h
            y = np.einsum('n,n,nij->ij', op.we, np.exp(-d * t), Y0).ravel()
            for p, stages in enumerate(rows):
                weights = W1 * np.exp(-d * (t - (p + 1) * h))[:, None]
                C = np.einsum('n,nj,nab->jab', op.we, weights, R)
                y += np.einsum('jab,jb->a', C, stages.reshape(3, 9))
            rhs.append(y + block[0] @ start.ravel())
        unknown = np.linalg.solve(A, np.concatenate(rhs)).reshape(2, 3, 3)
        rows.append(np.concatenate([start[None], unknown]))
    return np.array(rows)
