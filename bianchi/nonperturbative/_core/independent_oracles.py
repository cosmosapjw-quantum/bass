"""Independent canonical/coordinate and variational checks for BF3-C.

Only the lapse coefficient and input validation are shared with the tetrad
provider. These oracles never call its RHS or radiation/screen history.
Canonical p uses physical spatial momentum up to a constant L_star factor.
Coordinate 4-vector uses x^0=ct/L_star=cbar*u and metric diag(-N^2,1,1,1).
"""
from __future__ import annotations
import numpy as np
from .lapse_transport import DenseHistory, checked_ray_data

class HamiltonianHistory(DenseHistory):
    """Hamiltonian H_u=cbar*N(x)*|p| with optional full6D tangent matrix."""

    def __init__(self, model, x0, p0, t_end, tangent=False, rtol=2e-12, atol=2e-14):
        x = np.atleast_2d(np.asarray(x0, float))
        p = np.atleast_2d(np.asarray(p0, float))
        if x.shape != p.shape or x.shape[1] != 3 or (not np.isfinite(x).all()) or (not np.isfinite(p).all()) or np.any(np.linalg.norm(p, axis=1) <= 0):
            raise ValueError('Finite matching phase coordinates and nonzero momentum required')
        self.model = model
        self.tangent = bool(tangent)
        m = len(x)
        y0 = np.concatenate((x, p), axis=1)
        if tangent:
            y0 = np.concatenate((y0, np.broadcast_to(np.eye(6), (m, 6, 6)).reshape(m, 36)), axis=1)

        def fun(t, y):
            x = y[:, :3]
            p = y[:, 3:6]
            mag = np.linalg.norm(p, axis=1)
            n = p / mag[:, None]
            N = model.N(x[:, 0])
            g = np.zeros_like(x)
            g[:, 0] = model.dN(x[:, 0])
            c = model.cbar
            dx = c * N[:, None] * n
            dp = -c * mag[:, None] * g
            ans = np.concatenate((dx, dp), axis=1)
            if tangent:
                jac = np.zeros((m, 6, 6))
                P = np.eye(3) - np.einsum('ni,nj->nij', n, n)
                jac[:, :3, :3] = c * np.einsum('ni,nj->nij', n, g)
                jac[:, :3, 3:] = c * (N / mag)[:, None, None] * P
                jac[:, 3, 0] = -c * mag * model.ddN(x[:, 0])
                jac[:, 3:, 3:] = -c * np.einsum('ni,nj->nij', g, n)
                dT = jac @ y[:, 6:].reshape(m, 6, 6)
                ans = np.concatenate((ans, dT.reshape(m, 36)), axis=1)
            return ans
        self._solve(y0, fun, t_end, rtol, atol)

    def at(self, t):
        y = self._raw(t)
        z = {'x': y[:, :3], 'p': y[:, 3:6]}
        if self.tangent:
            z['tangent'] = y[:, 6:].reshape(-1, 6, 6)
        return z

class CoordinateParallelHistory(DenseHistory):
    """4D geodesic and parallel polarization vectors from Christoffels.

    Only after integration is the temporal photon-gauge component removed.
    No tetrad normal-acceleration or minimal-screen formula is called.
    """

    def __init__(self, model, x0, n0, t_end, screen0=None, rtol=2e-12, atol=2e-14):
        x, n, E = checked_ray_data(x0, n0, screen0)
        m = len(x)
        self.model = model
        k = np.column_stack((1 / model.N(x[:, 0]), n))
        W = np.zeros((m, 4, 2))
        W[:, 1:] = E
        y0 = np.concatenate((x, k, W.reshape(m, 8)), axis=1)

        def fun(t, y):
            x = y[:, :3]
            k = y[:, 3:7]
            W = y[:, 7:].reshape(m, 4, 2)
            N = model.N(x[:, 0])
            dN = model.dN(x[:, 0])
            Gam = np.zeros((m, 4, 4, 4))
            Gam[:, 0, 0, 1] = dN / N
            Gam[:, 0, 1, 0] = dN / N
            Gam[:, 1, 0, 0] = N * dN
            a = model.cbar / k[:, 0]
            dk = -a[:, None] * np.einsum('nabc,nb,nc->na', Gam, k, k)
            dW = -a[:, None, None] * np.einsum('nabc,nb,ncj->naj', Gam, k, W)
            dx = a[:, None] * k[:, 1:]
            return np.concatenate((dx, dk, dW.reshape(m, 8)), axis=1)
        self._solve(y0, fun, t_end, rtol, atol)

    def at(self, t):
        y = self._raw(t)
        x = y[:, :3]
        k = y[:, 3:7]
        W = y[:, 7:].reshape(-1, 4, 2)
        N = self.model.N(x[:, 0])
        energy = N * k[:, 0]
        n = k[:, 1:] / energy[:, None]
        screen = W[:, 1:] - np.einsum('ni,nj->nij', k[:, 1:], W[:, 0] / k[:, 0, None])
        norm = -N ** 2 * k[:, 0] ** 2 + np.sum(k[:, 1:] ** 2, axis=1)
        orth = -N[:, None] ** 2 * k[:, 0, None] * W[:, 0] + np.einsum('ni,nij->nj', k[:, 1:], W[:, 1:])
        gram = np.einsum('nia,nib->nab', W[:, 1:], W[:, 1:]) - N[:, None, None] ** 2 * np.einsum('na,nb->nab', W[:, 0], W[:, 0])
        return {'x': x, 'n': n, 'r': energy, 'screen': screen, 'k': k, 'parallel_W': W, 'null_error': float(np.max(abs(norm))), 'orthogonality_error': float(np.max(abs(orth))), 'parallel_gram_error': float(np.max(abs(gram - np.eye(2))))}

class ReducedMeasureHistory(DenseHistory):
    """Coupled (x,mu=n_x) variation. Phi determinant is the x-Omega measure.

    y,z are ignorable translations and azimuth is constant, so their diagonal
    tangent blocks are identity. This is NOT an angular-only Jacobian.
    """

    def __init__(self, model, x0, mu0, t_end, rtol=2e-12, atol=2e-14):
        x, mu = np.broadcast_arrays(np.asarray(x0, float), np.asarray(mu0, float))
        x = x.ravel()
        mu = mu.ravel()
        m = len(x)
        if not np.isfinite(x).all() or not np.isfinite(mu).all() or np.any(abs(mu) >= 1):
            raise ValueError('Finite x and strictly interior |mu|<1 required for chart')
        self.model = model
        y0 = np.concatenate((x[:, None], mu[:, None], np.zeros((m, 1)), np.broadcast_to(np.eye(2), (m, 2, 2)).reshape(m, 4)), axis=1)

        def fun(t, y):
            x = y[:, 0]
            mu = y[:, 1]
            N = model.N(x)
            dN = model.dN(x)
            c = model.cbar
            A = np.zeros((m, 2, 2))
            A[:, 0, 0] = c * dN * mu
            A[:, 0, 1] = c * N
            A[:, 1, 0] = -c * model.ddN(x) * (1 - mu ** 2)
            A[:, 1, 1] = 2 * c * dN * mu
            v = np.column_stack((c * N * mu, -c * dN * (1 - mu ** 2), -c * dN * mu))
            return np.concatenate((v, (A @ y[:, 3:].reshape(m, 2, 2)).reshape(m, 4)), axis=1)
        self._solve(y0, fun, t_end, rtol, atol)

    def at(self, t):
        y = self._raw(t)
        return {'x': y[:, 0], 'mu': y[:, 1], 'r': np.exp(y[:, 2]), 'tangent': y[:, 3:].reshape(-1, 2, 2)}
