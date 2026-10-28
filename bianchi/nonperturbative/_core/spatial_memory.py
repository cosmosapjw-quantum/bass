"""BF3-B: independent retarded spatial-source solver at fixed Fourier cutoff.

Prescribed homogeneous diagonal Bianchi I; one periodic coordinate, beta=0,
cold elastic bolometric Thomson. Rates use u=t/T_star; cbar=c*T_star/L_star.

The loss-only propagator is a matrix in retained spatial Fourier modes. It is
NOT P_K exp(-path optical depth) P_K: projection and attenuation do not commute.
At increasing spatial resolution it approximates the retarded continuum flow.
Unknown source M(t,x) is solved by causal quadratic product integration. No
PhysicalHistory/CharacteristicHistory or radiation RHS is called here.
No angular/state/weight renormalization, clipping, matter or Einstein feedback.
"""
from __future__ import annotations
from functools import lru_cache
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import solve_ivp
from scipy.linalg import solve
from .source_memory import ALPHA

def fft_field(field):
    """Spatial Fourier coefficients in numpy ordering, with 1/N normalization."""
    f = np.asarray(field)
    if not np.isfinite(f).all():
        raise ValueError('Finite spatial field required')
    return np.fft.fft(f, axis=0) / f.shape[0]

def real_field(coeff):
    """Inverse transform with a reality check, never discard material imaginary data."""
    a = np.asarray(coeff)
    f = np.fft.ifft(a, axis=0) * len(a)
    if np.max(abs(f.imag)) > 2e-10 * max(1.0, float(np.max(abs(f.real)))):
        raise ArithmeticError('Fourier reality constraint failed')
    return f.real

def lagrange(v):
    return np.array([2 * (v - 0.5) * (v - 1), 4 * v * (1 - v), 2 * v * (v - 0.5)])

class LossPropagator:
    """Known streaming/loss evolution; no radiation initial condition or history.

    Phi_q' = [-i k v_q(t) - V(t)] Phi_q, Phi_q(0)=I,
    V_kl=nu_(k-l), with no modular wrap. U(t,s)=Phi(t) Phi(s)^-1.
    Bounded inverse conditioning is measured; no long/stiff-history guarantee.
    """

    def __init__(self, op, rtol=2e-12, atol=2e-14, condition_limit=20.0):
        self.op = op
        self.nx = op.line.n
        self.nq = op.nq
        self.k = np.rint(op.line.k).astype(int)
        self.condition_limit = float(condition_limit)
        if not np.isfinite(condition_limit) or condition_limit <= 1:
            raise ValueError('Condition limit must be finite and greater than one')
        initial = np.broadcast_to(np.eye(self.nx, dtype=complex), (self.nq, self.nx, self.nx)).copy()

        def rhs(t, y):
            phi = y.reshape(initial.shape)
            adv = -1j * op.velocity(t)[:, None] * self.k[None, :]
            return (adv[:, :, None] * phi - np.einsum('kl,qlm->qkm', self.opacity_matrix(t), phi, optimize=True)).ravel()
        self.solution = solve_ivp(rhs, (0.0, op.end), initial.ravel(), method='DOP853', rtol=rtol, atol=atol, dense_output=True)
        if not self.solution.success:
            raise RuntimeError(self.solution.message)
        self.max_sampled_condition = max((float(np.max(np.linalg.cond(self.phi(float(t))))) for t in np.linspace(0, op.end, 5)))
        if self.max_sampled_condition > self.condition_limit:
            raise ArithmeticError('Loss fundamental matrix exceeds bounded conditioning contract')

    def opacity_matrix(self, t):
        coeff = self.op.opacity.coefficients(float(t))
        delta = self.k[:, None] - self.k[None, :]
        out = np.zeros((self.nx, self.nx), complex)
        for m, c in coeff.items():
            out[delta == m] = c
        if np.max(abs(out - out.conj().T)) > 2e-13:
            raise ValueError('Real opacity requires a Hermitian Galerkin multiplier')
        return out

    @lru_cache(maxsize=48)
    def phi(self, t):
        t = self.op.geo._time(t)
        return self.solution.sol(t).reshape(self.nq, self.nx, self.nx)

    @lru_cache(maxsize=48)
    def inverse(self, t):
        return np.linalg.solve(self.phi(float(t)), np.broadcast_to(np.eye(self.nx), (self.nq, self.nx, self.nx)))

    def transition(self, t, s):
        t = self.op.geo._time(t)
        s = self.op.geo._time(s)
        if s > t + 1e-14:
            raise ValueError('Retarded transition requires s<=t')
        return self.phi(t) @ self.inverse(s)

    def evolve(self, t, s, X):
        return np.einsum('qkl,lqab->kqab', self.transition(t, s), X, optimize=True)

class SpatialMemory:
    """Full initial carrier plus 9*Nx-component retarded source operator."""

    def __init__(self, loss: LossPropagator, J0):
        self.loss = loss
        self.op = loss.op
        self.nx = loss.nx
        self.nq = loss.nq
        self.X0 = fft_field(self.op.pull(0.0, self.op.check(J0)))
        self.source_shape = (self.nx, 3, 3)
        self.size = self.nx * 9

    def source_from_screen(self, t, X):
        z = self.op.geo.at(t)
        E = z['screen']
        return np.einsum('q,qia,kqab,qjb->kij', z['v'], E, X, E, optimize=True)

    def state_from_screen(self, t, X):
        return self.op.push(t, real_field(X))

    def initial_hat(self, t):
        return self.source_from_screen(t, self.loss.evolve(t, 0.0, self.X0))

    def initial_term(self, t):
        return real_field(self.initial_hat(t))

    def kernel(self, t, s):
        """M_hat(s)->M_hat(t) rate matrix; spatial and tensor couplings retained."""
        if s > t + 1e-14:
            raise ValueError('Kernel must be retarded')
        zt, zs = (self.op.geo.at(t), self.op.geo.at(s))
        UV = self.loss.transition(t, s) @ self.loss.opacity_matrix(s)
        Z = np.einsum('qia,qja->qij', zt['screen'], zs['screen'])
        R = np.einsum('qia,qjb->qijab', Z, Z).reshape(self.nq, 81)
        w = ALPHA * zt['v'] / zs['mu'] ** 4
        blocks = (UV * w[:, None, None]).reshape(self.nq, self.nx * self.nx).T @ R
        return blocks.reshape(self.nx, self.nx, 3, 3, 3, 3).transpose(0, 2, 3, 1, 4, 5).reshape(self.size, self.size)

    def gain_to_screen(self, t, s, M):
        """Propagate the source at s into pulled screen carrier at t."""
        zs = self.op.geo.at(s)
        E = zs['screen']
        gain = ALPHA * np.einsum('qia,kij,qjb->kqab', E, M, E, optimize=True) / zs['mu'][None, :, None, None] ** 4
        UV = self.loss.transition(t, s) @ self.loss.opacity_matrix(s)
        return np.einsum('qkl,lqab->kqab', UV, gain, optimize=True)

class SpatialVolterra:
    """Independent causal block product integration of unknown M(t,x).

    Two unknown source matrices per spatial mode in each panel; 18*Nx complex
    linear system. Fourier conjugate symmetry ensures physical outputs are real.
    Only known geometry/loss matrices and already solved sources enter the solve.
    Past contributions are stored as a full angular screen field, not discarded.
    """

    def __init__(self, memory: SpatialMemory, panels: int, order: int=4, end=None):
        if not isinstance(panels, int) or panels < 1:
            raise ValueError('Positive integer panel count required')
        if not isinstance(order, int) or order < 2:
            raise ValueError('Kernel quadrature order>=2 required')
        self.mem = memory
        self.op = memory.op
        self.end = self.op.end if end is None else self.op.geo._time(end)
        if self.end <= 0:
            raise ValueError('Positive end required')
        self.times = np.linspace(0.0, self.end, panels + 1)
        self.order = order
        self.qx, self.qw = leggauss(order)
        self.states = [memory.X0.copy()]
        self.sources = []
        self.max_endpoint_source_residual = 0.0
        self.max_panel_condition = 0.0
        self.linear_residual = 0.0
        self.linear_solves = 0
        n = memory.size
        identity = np.eye(n, dtype=complex)
        for a, b in zip(self.times[:-1], self.times[1:]):
            h = b - a
            Xa = self.states[-1]
            Ma = memory.source_from_screen(a, Xa)
            mats = []
            rhs = []
            for target in (a + h / 2, b):
                W = np.zeros((3, n, n), complex)
                for s, ws in self.quadrature(a, target):
                    K = memory.kernel(target, s)
                    W += ws * lagrange((s - a) / h)[:, None, None] * K[None]
                mats.append(W)
                rhs.append(memory.source_from_screen(target, memory.loss.evolve(target, a, Xa)).ravel() + W[0] @ Ma.ravel())
            block = np.block([[identity - mats[0][1], -mats[0][2]], [-mats[1][1], identity - mats[1][2]]])
            right = np.concatenate(rhs)
            answer = solve(block, right, check_finite=True)
            self.linear_solves += 1
            self.linear_residual = max(self.linear_residual, float(np.max(abs(block @ answer - right))))
            if len(self.sources) == 0 or b == self.end:
                cond = float(np.linalg.cond(block))
                self.max_panel_condition = max(self.max_panel_condition, cond)
                if cond > 20.0:
                    raise ArithmeticError('Current panel exceeds fixed conditioning contract')
            local = np.stack([Ma, answer[:n].reshape(memory.source_shape), answer[n:].reshape(memory.source_shape)])
            self.sources.append(local)
            Xb = self.reconstruct_panel(b, len(self.sources) - 1, Xa)
            residual = float(np.max(abs(memory.source_from_screen(b, Xb) - local[2])))
            self.max_endpoint_source_residual = max(self.max_endpoint_source_residual, residual)
            self.states.append(Xb)
        self.states = np.asarray(self.states)
        self.sources = np.asarray(self.sources)

    def quadrature(self, a, b):
        return zip(a + (b - a) * (self.qx + 1) / 2, (b - a) * self.qw / 2)

    def _index(self, t):
        t = float(t)
        if not np.isfinite(t) or t < 0 or t > self.end + 1e-14:
            raise ValueError('Time outside solved history')
        t = min(t, self.end)
        return (t, min(len(self.times) - 2, max(0, int(np.searchsorted(self.times, t, side='right') - 1))))

    def reconstruct_panel(self, t, i, Xa=None):
        a, b = (self.times[i], self.times[i + 1])
        Xa = self.states[i] if Xa is None else Xa
        X = self.mem.loss.evolve(t, a, Xa)
        for s, ws in self.quadrature(a, t):
            M = np.einsum('j,jkab->kab', lagrange((s - a) / (b - a)), self.sources[i])
            X = X + ws * self.mem.gain_to_screen(t, s, M)
        return X

    def screen(self, t):
        t, i = self._index(t)
        if t == self.end:
            return self.states[-1]
        if t == self.times[i]:
            return self.states[i]
        return self.reconstruct_panel(t, i)

    def state(self, t):
        t, _ = self._index(t)
        return self.mem.state_from_screen(t, self.screen(t))

    def source(self, t):
        t, _ = self._index(t)
        return real_field(self.mem.source_from_screen(t, self.screen(t)))

    def source_polynomial(self, t):
        t, i = self._index(t)
        a, b = self.times[i:i + 2]
        return real_field(np.einsum('j,jkab->kab', lagrange((t - a) / (b - a)), self.sources[i]))

    def full_history_source(self, t):
        """Independent explicit sum over every past panel, using solved sources."""
        t, i = self._index(t)
        out = self.mem.initial_hat(t).ravel()
        for j in range(i + 1):
            a, b = self.times[j:j + 2]
            for s, ws in self.quadrature(a, min(b, t)):
                M = np.einsum('r,rkab->kab', lagrange((s - a) / (b - a)), self.sources[j])
                out = out + ws * (self.mem.kernel(t, s) @ M.ravel())
        return real_field(out.reshape(self.mem.source_shape))
