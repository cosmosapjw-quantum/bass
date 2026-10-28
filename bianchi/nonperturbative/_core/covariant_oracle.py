"""Independent full-four-vector boost and pairwise Jones Thomson oracle.

Does not import the core boost/gain/source. Explicit O(N^2) pairwise amplitude
matrix; intended only for bounded reference quadratures. Same physical model.
"""
import numpy as np

def lorentz(beta):
    b = np.asarray(beta, float)
    g = 1 / np.sqrt(1 - b @ b)
    L = np.eye(4)
    L[0, 0] = g
    L[0, 1:] = -g * b
    L[1:, 0] = -g * b
    L[1:, 1:] += g * g / (g + 1) * np.outer(b, b)
    return L

def maps4(n, beta):
    L = lorentz(beta)
    p = np.c_[np.ones(len(n)), n] @ L.T
    D = p[:, 0]
    ne = p[:, 1:] / D[:, None]
    S = L[1:, 1:] - ne[:, :, None] * L[0, 1:]
    return (S, ne, D)

def screen(n):
    a = np.eye(3)[np.argmin(abs(n), axis=1)]
    e1 = np.cross(n, a)
    e1 /= np.linalg.norm(e1, axis=1)[:, None]
    return np.stack([e1, np.cross(n, e1)], axis=2)

def pairwise_rhs(n, w, J, beta, nu0):
    S, ne, D = maps4(n, beta)
    we = w / D ** 2
    Je = D[:, None, None] ** 4 * np.einsum('nik,nkl,njl->nij', S, J, S)
    E = screen(ne)
    X = np.einsum('nia,nij,njb->nab', E, Je, E)
    overlap = np.einsum('nia,mib->nmab', E, E)
    gain2 = 3 / (8 * np.pi) * np.einsum('m,nmab,mbc,nmdc->nad', we, overlap, X, overlap, optimize=True)
    Ce = np.einsum('nia,nab,njb->nij', E, gain2 - X, E)
    Lin = lorentz(-np.asarray(beta))
    back = Lin[1:, 1:] - n[:, :, None] * Lin[0, 1:]
    return float(nu0) * D[:, None, None] ** (-3) * np.einsum('nik,nkl,njl->nij', back, Ce, back)
