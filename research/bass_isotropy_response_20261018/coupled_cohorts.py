"""S7 manufactured closed donor + collisionless radiation + Lambda histories.

Non-tilted LRS Bianchi I, (-,+,+,+); a_perp=a exp(-b), a_parallel=a exp(2b).
x=ln(a/a_ref), h=H/H*, y=s/H*, E=8*pi*G*U/(3*c^2*H*^2), Pi=k*DeltaP/H*^2.
The background h is independently evolved by Raychaudhuri. The Hamiltonian
constraint is diagnosed, never used to overwrite h after initialization.
Only new explicitly isotropic birth rules are projected. Old isotropic and
physical anisotropic stock and all previously born cohorts stay frozen.
This is a manufactured donor transfer, not the MD14/native spectral owner.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from fractions import Fraction
import hashlib
import math
import numpy as np
from scipy.integrate import solve_ivp
from angular_balance import lrs_rule, project as project_p2
from angular_p24 import feasibility, project as project_p24

ALGORITHM_ID = 'BASS_S7_CLOSED_COUPLED_COHORTS_V1'
RTOL = 5e-13
ATOL = 5e-15
GATES = {'hamiltonian_relative': 1e-11, 'cohort_energy_relative': 1e-11,
         'event_energy_relative': 1e-13, 'moment_abs': 3e-15,
         'parity_abs': 0.0, 'donor_endpoint_relative': 3e-14}
MOMENT_GATE_EXACT = Fraction(3, 10**15)


@lru_cache(maxsize=4096)
def _exact_moment_sums(mu, alpha):
    """Exact dyadic-input polynomial sums; no transcendental kernel is certified."""
    norm = m2 = m4 = Fraction(0)
    for m, w in zip(mu, alpha):
        fm, fw = Fraction.from_float(m), Fraction.from_float(w)
        z = fm*fm
        norm += fw
        m2 += fw*(3*z-1)/2
        m4 += fw*(35*z*z-30*z+3)/8
    return norm, m2, m4


def exact_birth_moment_certificate(mu, alpha, mode):
    """Certify the same sum(alpha P_l) functional against exactly 3/10^15.

    The original S7 observer evaluated this polynomial in binary64 and used a
    BLAS dot product. Near its gate, polynomial ordering alone changed verdicts.
    This observer computes the polynomial of the actual binary64 inputs exactly.
    Normalization remains a separate criterion; normalized moments are diagnostic.
    It neither changes nodes/weights nor certifies continuum angular accuracy.
    """
    mu, alpha = np.asarray(mu, dtype=float), np.asarray(alpha, dtype=float)
    if mu.ndim != 1 or alpha.shape != mu.shape or not len(mu) or not np.isfinite(mu).all() or not np.isfinite(alpha).all() or np.any(alpha <= 0):
        raise ValueError('COUPLED_EXACT_MOMENT_INPUT')
    norm, m2, m4 = _exact_moment_sums(tuple(map(float, mu)), tuple(map(float, alpha)))
    constrained = mode in ('P2', 'P24')
    passed = (abs(m2) <= MOMENT_GATE_EXACT and (mode != 'P24' or abs(m4) <= MOMENT_GATE_EXACT)) if constrained else True
    return {'criterion': 'Exact sum(alpha_i P_l(mu_i)) on the actual binary64 inputs',
            'gate_rational': str(MOMENT_GATE_EXACT), 'applies': constrained, 'pass': bool(passed),
            'sum_alpha_exact': str(norm), 'M2_exact': str(m2), 'M4_exact': str(m4),
            'M2': float(m2), 'M4': float(m4),
            'normalized_M2_exact': str(m2/norm), 'normalized_M4_exact': str(m4/norm)}


@dataclass(frozen=True)
class Config:
    K: int = 64
    n: int = 16
    mode: str = 'P24'
    b0: float = 0.3
    y0: float = 0.08
    donor0: float = 0.7
    old_isotropic: float = 0.16
    old_anisotropic: float = 0.04
    eta: float = 0.4
    cosmological_constant: float = 0.1
    decay_lambda: float = 0.7
    birth_end: float = 0.8
    x_end: float = 1.2
    old_n: int = 128

    def validate(self):
        if isinstance(self.K, bool) or not isinstance(self.K, int) or not 0 <= self.K <= 2048:
            raise ValueError('COUPLED_K_DOMAIN')
        if isinstance(self.n, bool) or not isinstance(self.n, int) or not 4 <= self.n <= 512 or self.n % 2:
            raise ValueError('COUPLED_N_DOMAIN')
        if self.mode not in ('prior', 'P2', 'P24', 'source_frame_GL'):
            raise ValueError('COUPLED_MODE_DOMAIN')
        vals = (self.b0, self.y0, self.donor0, self.old_isotropic, self.old_anisotropic,
                self.eta, self.cosmological_constant, self.decay_lambda, self.birth_end, self.x_end)
        if not all(math.isfinite(v) for v in vals):
            raise ValueError('COUPLED_NONFINITE_INPUT')
        if min(self.donor0, self.old_isotropic, self.old_anisotropic,
               self.cosmological_constant, self.decay_lambda) < 0:
            raise ValueError('COUPLED_NEGATIVE_ENERGY_INPUT')
        if not -1 < self.eta < 2 or not 0 < self.birth_end <= self.x_end <= 8:
            raise ValueError('COUPLED_HISTORY_DOMAIN')
        if isinstance(self.old_n, bool) or not isinstance(self.old_n, int) or not 8 <= self.old_n <= 512 or self.old_n % 2:
            raise ValueError('COUPLED_OLD_GRID_DOMAIN')
        if self.K == 0 and self.donor0 * self.decay_lambda != 0:
            raise ValueError('COUPLED_K0_REQUIRES_NO_SOURCE')
        if self.y0**2+self.donor0+self.old_isotropic+self.old_anisotropic+self.cosmological_constant <= 0:
            raise ValueError('COUPLED_H0_DOMAIN')


@lru_cache(maxsize=16)
def source_frame_gl(n):
    mu, alpha = np.polynomial.legendre.leggauss(n)
    # Reflection pairs are represented exactly; this is the initial rule,
    # never an observation-time transformation of an existing cohort.
    mu = (mu-mu[::-1])/2
    alpha = (alpha+alpha[::-1])/4
    alpha /= math.fsum(alpha)
    mu.setflags(write=False); alpha.setflags(write=False)
    return mu, alpha


def birth_rule(b, n, mode):
    if mode == 'source_frame_GL':
        return source_frame_gl(n)
    mu, q = lrs_rule(float(b), n)
    if mode == 'prior':
        alpha = q
    elif mode == 'P2':
        alpha = project_p2(mu, q).weights
    elif mode == 'P24':
        alpha = project_p24(mu, q).weights
    else:
        raise ValueError('COUPLED_MODE_DOMAIN')
    return mu, alpha


class BirthRuleFailure(ArithmeticError):
    def __init__(self, cause, config, u, b):
        mu, _ = lrs_rule(float(b), config.n)
        self.record = {'kind': 'feasibility' if str(cause).startswith('INFEASIBLE') else 'numerical',
                       'error': str(cause), 'u': float(u), 'b_birth': float(b),
                       'mode': config.mode, 'n': config.n,
                       'p2_range': [float(np.min((3*mu*mu-1)/2)), float(np.max((3*mu*mu-1)/2))],
                       'p24_feasibility': asdict(feasibility(mu)), 'mu': mu.tolist()}
        super().__init__(str(cause))


@dataclass(frozen=True)
class Cohort:
    u: float
    b_birth: float
    energy_birth: float
    mu: np.ndarray
    alpha: np.ndarray
    role: str

    @classmethod
    def create(cls, u, b_birth, energy_birth, mu, alpha, role):
        mu, alpha = np.array(mu, dtype=float, copy=True), np.array(alpha, dtype=float, copy=True)
        if (mu.ndim != 1 or alpha.shape != mu.shape or not len(mu) or
            not np.all(np.isfinite(mu)) or not np.all(np.isfinite(alpha)) or
            not np.all(np.abs(mu) <= 1) or not np.all(alpha > 0) or
            not math.isfinite(energy_birth) or energy_birth <= 0 or
            not math.isfinite(u) or not math.isfinite(b_birth)):
            raise ValueError('COUPLED_COHORT_POSITIVE_DOMAIN')
        if np.max(np.abs(mu+mu[::-1])) != 0 or np.max(np.abs(alpha-alpha[::-1])) != 0:
            raise ValueError('COUPLED_COHORT_REFLECTION')
        if abs(math.fsum(alpha)-1) > 3e-15:
            raise ValueError('COUPLED_COHORT_NORMALIZATION')
        mu.setflags(write=False); alpha.setflags(write=False)
        return cls(float(u), float(b_birth), float(energy_birth), mu, alpha, role)

    def digest(self):
        h = hashlib.sha256()
        h.update(np.array([self.u, self.b_birth, self.energy_birth], dtype='<f8').tobytes())
        h.update(self.mu.astype('<f8').tobytes()); h.update(self.alpha.astype('<f8').tobytes())
        h.update(self.role.encode())
        return h.hexdigest()

    def energy_pressure(self, x, b):
        z = self.mu*self.mu
        d = b-self.b_birth
        perp, para = np.exp(2*d)*(1-z), np.exp(-4*d)*z
        R = np.sqrt(perp+para)
        f = self.energy_birth*np.exp(-4*(x-self.u))
        return f*np.sum(self.alpha*R), f*np.sum(self.alpha*(para-perp/2)/R)

    def identity_relative(self, x, b, bprime):
        # Local complex step along the actual solution tangent, avoiding a
        # numerical derivative of the separately coded real pressure kernel.
        epsilon = 1e-25
        Ec, _ = self.energy_pressure(x+1j*epsilon, b+1j*epsilon*bprime)
        E, Pi = self.energy_pressure(x, b)
        return float(abs(Ec.imag/epsilon+4*E+2*bprime*Pi)/E)


class Bank:
    def __init__(self):
        self.cohorts = []
        self.birth_digests = []
        self.u = self.perp = self.para = self.amplitude = np.array([], dtype=float)

    def add(self, cohort):
        self.cohorts.append(cohort); self.birth_digests.append(cohort.digest())
        z = cohort.mu**2
        self.u = np.append(self.u, np.full(len(z), cohort.u))
        self.perp = np.append(self.perp, np.exp(-2*cohort.b_birth)*(1-z))
        self.para = np.append(self.para, np.exp(4*cohort.b_birth)*z)
        self.amplitude = np.append(self.amplitude, cohort.energy_birth*np.exp(4*cohort.u)*cohort.alpha)

    def energy_pressure(self, x, b, active_only=True):
        if not len(self.u):
            return 0.0, 0.0
        mask = self.u <= x if active_only else slice(None)
        perp = math.exp(2*b)*self.perp[mask]
        para = math.exp(-4*b)*self.para[mask]
        R = np.sqrt(perp+para)
        f = math.exp(-4*x)*self.amplitude[mask]
        return float(np.dot(f, R)), float(np.dot(f, (para-perp/2)/R))

    def unchanged(self):
        return all(c.digest() == h for c, h in zip(self.cohorts, self.birth_digests))


def initial_bank(config):
    bank = Bank()
    mu, weights = source_frame_gl(config.old_n)
    if config.old_isotropic > 0:
        bank.add(Cohort.create(0, config.b0, config.old_isotropic, mu, weights, 'old_isotropic'))
    if config.old_anisotropic > 0:
        physical = weights*(1+config.eta*(3*mu**2-1)/2)
        physical /= math.fsum(physical)
        bank.add(Cohort.create(0, config.b0, config.old_anisotropic, mu, physical, 'old_physical_anisotropic'))
    return bank


def event_times(config):
    if config.K == 0 or config.decay_lambda == 0 or config.donor0 == 0:
        return np.array([], dtype=float)
    return (np.arange(config.K)+0.5)*config.birth_end/config.K


class History:
    def __init__(self, config, bank, segments, births, events, nfev):
        self.config, self.bank, self.segments = config, bank, segments
        self.births, self.events, self.nfev = births, events, nfev
        self.ends = np.array([s[1] for s in segments])

    def state(self, x):
        if not 0 <= x <= self.config.x_end:
            raise ValueError('COUPLED_OBSERVATION_DOMAIN')
        i = min(int(np.searchsorted(self.ends, x, side='left')), len(self.segments)-1)
        return self.segments[i][2](x)

    def donor(self, x):
        count = int(np.searchsorted(self.births, x, side='right'))
        exposure = count*self.config.birth_end/self.config.K if self.config.K else 0
        return self.config.donor0*math.exp(-3*x-self.config.decay_lambda*exposure)

    def observe(self, x):
        h, b, y = map(float, self.state(x))
        E, Pi = self.bank.energy_pressure(x, b)
        Ed = self.donor(x)
        scale = h*h+y*y+Ed+E+self.config.cosmological_constant
        C = h*h-y*y-Ed-E-self.config.cosmological_constant
        return {'x': float(x), 'h': h, 'b': b, 'y': y, 'E_donor': Ed,
                'E_radiation': E, 'Pi': Pi, 'A': Pi/E if E > 0 else 0.0,
                'Sigma': math.sqrt(3)*abs(y)/h, 'C': C, 'C_relative': abs(C)/scale,
                'bprime': y/h}

    def sample(self, xs):
        return [self.observe(float(x)) for x in xs]


def solve_history(config, *, donor_subtraction=True):
    """Evolve the model. donor_subtraction=False is an explicit invalid control.

    Each smooth interval has a fixed bank. A source event transfers positive
    donor energy to a new cohort and preserves h,b,y. No existing ray changes.
    """
    config.validate()
    bank = initial_bank(config)
    h0 = math.sqrt(config.y0**2+config.donor0+config.old_isotropic+
                   config.old_anisotropic+config.cosmological_constant)
    state = np.array([h0, config.b0, config.y0])
    births = event_times(config)
    endpoints = np.r_[births, config.x_end]
    segments, events = [], []
    begin, transfers, nfev = 0.0, 0, 0
    du = config.birth_end/config.K if config.K else 0
    for end in endpoints:
        exposure = transfers*du if donor_subtraction else 0.0

        def rhs(x, values):
            h, b, y = values
            if h <= 0 or not np.all(np.isfinite(values)):
                raise ArithmeticError('COUPLED_BACKGROUND_DOMAIN')
            E, Pi = bank.energy_pressure(x, b, active_only=False)
            Ed = config.donor0*math.exp(-3*x-config.decay_lambda*exposure)
            L = config.cosmological_constant
            return [(-h*h-2*y*y-0.5*Ed-E+L)/h, y/h, -3*y+Pi/h]

        sol = solve_ivp(rhs, (float(begin), float(end)), state, method='DOP853',
                        rtol=RTOL, atol=ATOL, dense_output=True, max_step=0.08)
        if not sol.success:
            raise ArithmeticError('COUPLED_INTEGRATOR_FAILURE: '+sol.message)
        segments.append((float(begin), float(end), sol.sol))
        nfev += sol.nfev
        state = sol.y[:, -1]
        begin = float(end)
        if transfers >= len(births):
            break
        u = float(end); h, b, y = map(float, state)
        before_E, before_P = bank.energy_pressure(u, b, active_only=False)
        donor_before = config.donor0*math.exp(-3*u-config.decay_lambda*exposure)
        weight = donor_before*(-math.expm1(-config.decay_lambda*du))
        donor_after = donor_before*math.exp(-config.decay_lambda*du) if donor_subtraction else donor_before
        if not (weight > 0 and donor_after > 0 and math.isfinite(weight)):
            raise ArithmeticError('COUPLED_POSITIVE_TRANSFER_LOSS')
        try:
            mu, alpha = birth_rule(b, config.n, config.mode)
        except (ValueError, ArithmeticError) as error:
            raise BirthRuleFailure(error, config, u, b) from error
        bank.add(Cohort.create(u, b, weight, mu, alpha, 'new_isotropic_'+config.mode))
        after_E, after_P = bank.energy_pressure(u, b, active_only=False)
        C_before = h*h-y*y-donor_before-before_E-config.cosmological_constant
        C_after = h*h-y*y-donor_after-after_E-config.cosmological_constant
        events.append({'u': u, 'b_birth': b, 'h': h, 'y': y,
                       'donor_before': donor_before, 'donor_after': donor_after,
                       'energy_birth': weight, 'radiation_before': before_E,
                       'radiation_after': after_E, 'Pi_before': before_P, 'Pi_after': after_P,
                       'energy_jump': donor_after+after_E-donor_before-before_E,
                       'C_before': C_before, 'C_after': C_after,
                       'birth_M2': float(np.dot(alpha, (3*mu**2-1)/2)),
                       'birth_M4': float(np.dot(alpha, (35*mu**4-30*mu**2+3)/8)),
                       'exact_moment_certificate': exact_birth_moment_certificate(mu, alpha, config.mode),
                       'birth_min_weight': float(np.min(alpha)),
                       'birth_rule_sha256': bank.birth_digests[-1]})
        transfers += 1
    history = History(config, bank, segments, births, events, nfev)
    if not donor_subtraction:
        # The deliberately wrong donor history is part of the negative control,
        # not an alternate production/configuration mode exposed by the runner.
        history.donor = lambda x: config.donor0*math.exp(-3*x)
    return history


def diagnostics(history, sample_count=241):
    config = history.config
    xs = np.unique(np.r_[np.linspace(0, config.x_end, sample_count), history.births])
    rows = history.sample(xs)
    max_identity = 0.0
    # Identity is evaluated between events; the source impulse itself is
    # tested separately by the donor/radiation jump check.
    for a, b, _ in history.segments:
        x = (a+b)/2
        _, b_now, _ = history.state(x)
        obs = history.observe(x)
        for cohort in history.bank.cohorts:
            if cohort.u < x:
                max_identity = max(max_identity, cohort.identity_relative(x, b_now, obs['bprime']))
    event_error = max((abs(e['energy_jump'])/(e['donor_before']+e['radiation_before'])
                       for e in history.events), default=0.0)
    constraint = max(r['C_relative'] for r in rows)
    legacy_moment = max((max(abs(e['birth_M2']), abs(e['birth_M4']) if config.mode == 'P24' else 0)
                  for e in history.events), default=0.0) if config.mode in ('P2', 'P24') else None
    moment = max((max(abs(e['exact_moment_certificate']['M2']), abs(e['exact_moment_certificate']['M4']) if config.mode == 'P24' else 0)
                  for e in history.events), default=0.0) if config.mode in ('P2', 'P24') else None
    expected_donor = config.donor0*math.exp(-3*config.x_end-config.decay_lambda*config.birth_end) if len(history.births) else config.donor0*math.exp(-3*config.x_end)
    donor_error = abs(history.donor(config.x_end)-expected_donor)/expected_donor if expected_donor else 0.0
    gates = {'hamiltonian': constraint <= GATES['hamiltonian_relative'],
             'cohort_energy': max_identity <= GATES['cohort_energy_relative'],
             'event_energy': event_error <= GATES['event_energy_relative'],
             'birth_moments': all(e['exact_moment_certificate']['pass'] for e in history.events),
             'frozen_all_stock': history.bank.unchanged(),
             'positive_all_stock': all(c.energy_birth > 0 and np.all(c.alpha > 0) for c in history.bank.cohorts),
             'reflection_all_stock': all(np.array_equal(c.mu, -c.mu[::-1]) and np.array_equal(c.alpha, c.alpha[::-1]) for c in history.bank.cohorts),
             'donor_endpoint': donor_error <= GATES['donor_endpoint_relative'],
             'background_positive': all(r['h'] > 0 and all(math.isfinite(v) for v in r.values()) for r in rows)}
    return {'gate_results': {k: bool(v) for k, v in gates.items()},
            'max_hamiltonian_relative': constraint, 'max_cohort_energy_relative': max_identity,
            'max_event_energy_relative': event_error, 'max_birth_moment_abs': moment,
            'max_legacy_f64_birth_moment_abs': legacy_moment,
            'donor_endpoint_relative': donor_error, 'cohorts': len(history.bank.cohorts),
            'nfev': history.nfev, 'old_stock_digests': history.bank.birth_digests[:sum(c.role.startswith('old') for c in history.bank.cohorts)],
            'trajectory': rows, 'events': history.events}


def forcing_comparison(history, reference, order=12):
    """Measured difference Duhamel identity and two forcing approximations.

    This exact difference identity is a numerical consistency check, not an
    independent linearized Einstein validation. Neither forcing approximation
    is the full tangent system of the birth/history quadrature.
    """
    if history.config.x_end != reference.config.x_end:
        raise ValueError('COUPLED_FORCING_ENDPOINT')
    boundaries = np.unique(np.r_[0.0, history.births, reference.births, history.config.x_end])
    nodes, weights = np.polynomial.legendre.leggauss(order)
    integrals = np.zeros(3)
    xend = history.config.x_end
    for a, b in zip(boundaries[:-1], boundaries[1:]):
        for xi, wi in zip((a+b)/2+(b-a)*nodes/2, weights*(b-a)/2):
            A, R = history.observe(float(xi)), reference.observe(float(xi))
            dh, dp = A['h']-R['h'], A['Pi']-R['Pi']
            exact = A['Pi']/A['h']-R['Pi']/R['h']
            fixed = dp/R['h']
            first_H = fixed-R['Pi']*dh/R['h']**2
            integrals += wi*math.exp(-3*(xend-xi))*np.array([exact, fixed, first_H])
    dy0 = history.config.y0-reference.config.y0
    integrals += math.exp(-3*xend)*dy0
    actual = history.observe(xend)['y']-reference.observe(xend)['y']
    return {'actual_delta_y': actual, 'exact_duhamel': float(integrals[0]),
            'measured_deltaPi_over_referenceH': float(integrals[1]), 'forcing_with_first_H_term': float(integrals[2]),
            'exact_identity_abs': abs(actual-integrals[0]),
            'fixed_background_discrepancy': float(actual-integrals[1]),
            'first_H_discrepancy': float(actual-integrals[2]),
            'measured_forcing_over_actual': float(integrals[1]/actual) if abs(actual) > 1e-13 else None,
            'quadrature_order': order,
            'scope': 'DeltaPi is measured on the two evolved coupled histories; division by reference H is a forcing approximation. This is neither a prescribed-background rule response nor the full tangent solution. Exact Duhamel agreement is numerical consistency only.'}
