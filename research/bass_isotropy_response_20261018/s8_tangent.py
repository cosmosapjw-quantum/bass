"""Full source-birth-memory tangent of the frozen S7 manufactured closed model.

The parameter is initial y0 or a simultaneous source-frame b0 gauge offset.
Donor amplitudes and event x coordinates are fixed for both parameters.
No finite differences or measured-forcing histories enter this analytic solver.
"""
from __future__ import annotations
from contextlib import contextmanager
from dataclasses import dataclass
import hashlib
import math
import numpy as np
from scipy.integrate import solve_ivp
import coupled_cohorts as cc
import s8_tangent_math as sm

ALGORITHM_ID = 'BASS_S8_FULL_BIRTH_MEMORY_TANGENT_V1'
CONTROLS = ('full', 'omit_birth_memory', 'omit_mu_b', 'omit_alpha_b')
ORIGINAL_BIRTH_RULE = cc.birth_rule
LINEARIZED_CONSTRAINT_ATOL = 1e-11
TANGENT_ENERGY_ATOL = 1e-11
TANGENT_EVENT_ATOL = 1e-11


@contextmanager
def strict_primal_births():
    """Separate nonlinear FD solver: strict new-birth weights, no tangent data."""
    if cc.birth_rule is not ORIGINAL_BIRTH_RULE:
        raise ValueError('S8_UNEXPECTED_EXISTING_BIRTH_OVERRIDE')
    cc.birth_rule = sm.primal_birth_rule
    try:
        yield
    finally:
        cc.birth_rule = ORIGINAL_BIRTH_RULE


def solve_nonlinear(config):
    with strict_primal_births():
        return cc.solve_history(config)


@dataclass(frozen=True)
class TangentCohort:
    primal: cc.Cohort
    birth_b_theta: np.ndarray
    memory_theta: np.ndarray
    mu_theta: np.ndarray
    alpha_theta: np.ndarray

    def digest(self):
        value = hashlib.sha256(self.primal.digest().encode())
        for array in (self.birth_b_theta, self.memory_theta, self.mu_theta, self.alpha_theta):
            value.update(np.asarray(array, dtype='<f8').tobytes())
        return value.hexdigest()

    def energy_pressure_tangent(self, x, b, b_theta):
        c = self.primal
        R, D, R_d, D_d, R_mu, D_mu = sm.kernel_partials(b-c.b_birth, c.mu)
        delta_d = np.asarray(b_theta)[:, None]-self.memory_theta[:, None]
        factor = c.energy_birth*np.exp(-4*(x-c.u))
        E = factor*np.sum(c.alpha*R)
        Pi = factor*np.sum(c.alpha*D)
        dE = factor*np.sum(self.alpha_theta*R+c.alpha*(R_d*delta_d+R_mu*self.mu_theta), axis=1)
        dPi = factor*np.sum(self.alpha_theta*D+c.alpha*(D_d*delta_d+D_mu*self.mu_theta), axis=1)
        return E, Pi, dE, dPi


class TangentBank:
    def __init__(self, modes):
        self.modes = tuple(modes)
        self.base = cc.Bank()
        self.entries, self.entry_digests = [], []
        self.u = self.bu = self.mu = self.alpha = self.scale = np.array([], dtype=float)
        shape = (len(modes), 0)
        self.memory = np.zeros(shape); self.mu_theta = np.zeros(shape); self.alpha_theta = np.zeros(shape)

    def add(self, cohort, birth_b_theta, mu_b, alpha_b):
        birth_b_theta = np.asarray(birth_b_theta, dtype=float).copy()
        memory = birth_b_theta.copy()
        mu_theta = birth_b_theta[:, None]*np.asarray(mu_b)[None, :]
        alpha_theta = birth_b_theta[:, None]*np.asarray(alpha_b)[None, :]
        for i, mode in enumerate(self.modes):
            if mode == 'omit_birth_memory':
                memory[i] = 0
            elif mode == 'omit_mu_b':
                mu_theta[i] = 0
            elif mode == 'omit_alpha_b':
                alpha_theta[i] = 0
        for array in (birth_b_theta, memory, mu_theta, alpha_theta):
            array.setflags(write=False)
        entry = TangentCohort(cohort, birth_b_theta, memory, mu_theta, alpha_theta)
        self.entries.append(entry); self.entry_digests.append(entry.digest()); self.base.add(cohort)
        n = len(cohort.mu)
        self.u = np.append(self.u, np.full(n, cohort.u))
        self.bu = np.append(self.bu, np.full(n, cohort.b_birth))
        self.mu = np.append(self.mu, cohort.mu); self.alpha = np.append(self.alpha, cohort.alpha)
        self.scale = np.append(self.scale, np.full(n, cohort.energy_birth*math.exp(4*cohort.u)))
        self.memory = np.concatenate((self.memory, np.repeat(memory[:, None], n, axis=1)), axis=1)
        self.mu_theta = np.concatenate((self.mu_theta, mu_theta), axis=1)
        self.alpha_theta = np.concatenate((self.alpha_theta, alpha_theta), axis=1)

    def energy_pressure_tangent(self, x, b, b_theta, active_only=True):
        mask = self.u <= np.real(x) if active_only else slice(None)
        R, D, R_d, D_d, R_mu, D_mu = sm.kernel_partials(b-self.bu[mask], self.mu[mask])
        factor = np.exp(-4*x)*self.scale[mask]
        alpha = self.alpha[mask]
        delta_d = np.asarray(b_theta)[:, None]-self.memory[:, mask]
        E = np.sum(factor*alpha*R); Pi = np.sum(factor*alpha*D)
        dE = np.sum(factor*(self.alpha_theta[:, mask]*R+
                           alpha*(R_d*delta_d+R_mu*self.mu_theta[:, mask])), axis=1)
        dPi = np.sum(factor*(self.alpha_theta[:, mask]*D+
                            alpha*(D_d*delta_d+D_mu*self.mu_theta[:, mask])), axis=1)
        return E, Pi, dE, dPi

    def unchanged(self):
        return self.base.unchanged() and all(e.digest() == h for e, h in zip(self.entries, self.entry_digests))


def tangent_rhs(h, y, Ed, Er, Pi, L, tangent, dEr, dPi):
    """General Raychaudhuri derivative; donor and Lambda parameter derivatives=0."""
    hprime = (-h*h-2*y*y-Ed/2-Er+L)/h
    dh, db, dy = tangent.T
    return np.column_stack(((-2*h*dh-4*y*dy-dEr)/h-hprime*dh/h,
                            dy/h-y*dh/h**2,
                            -3*dy+dPi/h-Pi*dh/h**2))


class TangentHistory:
    def __init__(self, config, parameter, bank, segments, events, births, nfev):
        self.config, self.parameter, self.bank = config, parameter, bank
        self.modes, self.segments, self.events, self.births, self.nfev = bank.modes, segments, events, births, nfev
        self.ends = np.array([s[1] for s in segments])
        primal_segments = [(a, b, (lambda x, dense=dense: dense(x)[:3])) for a, b, dense in segments]
        self.primal = cc.History(config, bank.base, primal_segments, births, events, nfev)

    def state(self, x):
        if x < 0 or x > self.config.x_end:
            raise ValueError('S8_OBSERVATION_DOMAIN')
        j = min(int(np.searchsorted(self.ends, x, side='left')), len(self.segments)-1)
        return self.segments[j][2](x)

    def observe(self, x):
        state = self.state(x)
        h, b, y = map(float, state[:3])
        tangent = state[3:].reshape(len(self.modes), 3)
        primal = self.primal.observe(x)
        _, _, dEr, dPi = self.bank.energy_pressure_tangent(x, b, tangent[:, 1])
        rhs = tangent_rhs(h, y, primal['E_donor'], primal['E_radiation'], primal['Pi'],
                          self.config.cosmological_constant, tangent, dEr, dPi)
        hprime = (-h*h-2*y*y-primal['E_donor']/2-primal['E_radiation']+
                  self.config.cosmological_constant)/h
        yprime = -3*y+primal['Pi']/h
        scale = h*h+y*y+primal['E_donor']+primal['E_radiation']+self.config.cosmological_constant
        rows = {}
        for i, name in enumerate(self.modes):
            dh, db, dy = tangent[i]
            dC = 2*h*dh-2*y*dy-dEr[i]
            dErprime = -4*dEr[i]-2*(primal['bprime']*dPi[i]+rhs[i, 1]*primal['Pi'])
            dCprime = 2*hprime*dh+2*h*rhs[i, 0]-2*yprime*dy-2*y*rhs[i, 2]-dErprime
            rows[name] = {'h': float(dh), 'b': float(db), 'y': float(dy),
                          'E_donor': 0.0, 'E_radiation': float(dEr[i]), 'Pi': float(dPi[i]),
                          'Sigma': float(math.sqrt(3)*(math.copysign(1, y)*dy/h-abs(y)*dh/h**2)) if y != 0 else None,
                          'C': float(dC), 'C_scaled': float(abs(dC)/scale),
                          'constraint_propagation_scaled': float(abs(dCprime+2*dC)/scale),
                          'bprime': float(rhs[i, 1])}
        return {'x': float(x), 'primal': primal, 'tangent': rows}

    def sample(self, xs):
        return [self.observe(float(x)) for x in xs]


def solve_tangent(config, parameter='y0', modes=CONTROLS):
    config.validate(); modes = tuple(modes)
    if parameter not in ('y0', 'b0') or not modes or modes[0] != 'full' or len(set(modes)) != len(modes) or any(m not in CONTROLS for m in modes):
        raise ValueError('S8_PARAMETER_OR_MODE_DOMAIN')
    if config.mode not in ('P24', 'source_frame_GL'):
        raise ValueError('S8_ONLY_P24_OR_SOURCE_FRAME_GL')
    bank = TangentBank(modes)
    old_birth_theta = np.full(len(modes), 1.0 if parameter == 'b0' else 0.0)
    for cohort in cc.initial_bank(config).cohorts:
        zero = np.zeros_like(cohort.mu)
        bank.add(cohort, old_birth_theta, zero, zero)
    h0 = math.sqrt(config.y0**2+config.donor0+config.old_isotropic+config.old_anisotropic+
                   config.cosmological_constant)
    tangent0 = np.tile([config.y0/h0, 0.0, 1.0] if parameter == 'y0' else [0.0, 1.0, 0.0],
                       (len(modes), 1))
    state = np.r_[h0, config.b0, config.y0, tangent0.ravel()]
    births = cc.event_times(config)
    du = config.birth_end/config.K if config.K else 0.0
    segments, events = [], []
    begin, nfev = 0.0, 0
    for transfers, end in enumerate(np.r_[births, config.x_end]):
        exposure = min(transfers, len(births))*du

        def rhs(x, vector):
            h, b, y = vector[:3]
            if h <= 0 or not np.isfinite(vector).all():
                raise ArithmeticError('S8_POSITIVE_FINITE_BACKGROUND_LOSS')
            tangent = vector[3:].reshape(len(modes), 3)
            Ed = config.donor0*math.exp(-3*x-config.decay_lambda*exposure)
            Er, Pi = bank.base.energy_pressure(x, b, active_only=False)
            _, _, dEr, dPi = bank.energy_pressure_tangent(x, b, tangent[:, 1], active_only=False)
            primal_rhs = [(-h*h-2*y*y-Ed/2-Er+config.cosmological_constant)/h, y/h, -3*y+Pi/h]
            differential = tangent_rhs(h, y, Ed, Er, Pi, config.cosmological_constant, tangent, dEr, dPi)
            return np.r_[primal_rhs, differential.ravel()]

        sol = solve_ivp(rhs, (begin, float(end)), state, method='DOP853', rtol=cc.RTOL, atol=cc.ATOL,
                        dense_output=True, max_step=0.08)
        if not sol.success:
            raise ArithmeticError('S8_INTEGRATOR_FAILURE: '+sol.message)
        segments.append((float(begin), float(end), sol.sol))
        nfev += sol.nfev; state = sol.y[:, -1]; begin = float(end)
        if transfers >= len(births):
            break
        u = float(end); h, b, y = map(float, state[:3])
        tangent = state[3:].reshape(len(modes), 3)
        before_E, before_P = bank.base.energy_pressure(u, b, active_only=False)
        _, _, before_dE, before_dP = bank.energy_pressure_tangent(u, b, tangent[:, 1], active_only=False)
        donor_before = config.donor0*math.exp(-3*u-config.decay_lambda*exposure)
        weight = donor_before*(-math.expm1(-config.decay_lambda*du))
        donor_after = donor_before*math.exp(-config.decay_lambda*du)
        if not (weight > 0 and donor_after > 0 and math.isfinite(weight)):
            raise ArithmeticError('S8_POSITIVE_TRANSFER_LOSS')
        try:
            rule = sm.birth_differential(b, config.n, config.mode)
        except (ValueError, ArithmeticError) as error:
            if isinstance(error, sm.TangentDomainError):
                raise
            raise cc.BirthRuleFailure(error, config, u, b) from error
        cohort = cc.Cohort.create(u, b, weight, rule.mu, rule.alpha, 'new_isotropic_'+config.mode)
        bank.add(cohort, tangent[:, 1], rule.mu_b, rule.alpha_b)
        after_E, after_P = bank.base.energy_pressure(u, b, active_only=False)
        _, _, after_dE, after_dP = bank.energy_pressure_tangent(u, b, tangent[:, 1], active_only=False)
        scale = donor_before+before_E
        events.append({'u': u, 'b_birth': b, 'h': h, 'y': y,
                       'donor_before': donor_before, 'donor_after': donor_after, 'energy_birth': weight,
                       'radiation_before': before_E, 'radiation_after': after_E,
                       'Pi_before': before_P, 'Pi_after': after_P, 'energy_jump': donor_after+after_E-donor_before-before_E,
                       'C_before': h*h-y*y-donor_before-before_E-config.cosmological_constant,
                       'C_after': h*h-y*y-donor_after-after_E-config.cosmological_constant,
                       'birth_M2': float(np.dot(rule.alpha, (3*rule.mu**2-1)/2)),
                       'birth_M4': float(np.dot(rule.alpha, (35*rule.mu**4-30*rule.mu**2+3)/8)),
                       'exact_moment_certificate': rule.diagnostics['exact_moment_certificate'],
                       'birth_min_weight': float(np.min(rule.alpha)), 'birth_rule_sha256': cohort.digest(),
                       'birth_differential': {'mu': rule.mu.tolist(), 'alpha': rule.alpha.tolist(),
                                              'mu_b': rule.mu_b.tolist(), 'alpha_b': rule.alpha_b.tolist(),
                                              **rule.diagnostics},
                       'tangent_event': {name: {'birth_b_theta': float(tangent[i, 1]),
                             'energy_jump_theta': float(after_dE[i]-before_dE[i]),
                             'energy_jump_theta_scaled': float(abs(after_dE[i]-before_dE[i])/scale),
                             'pressure_jump_theta': float(after_dP[i]-before_dP[i])}
                                         for i, name in enumerate(modes)}})
    return TangentHistory(config, parameter, bank, segments, events, births, nfev)


def diagnostics(history, sample_count=121):
    primal = cc.diagnostics(history.primal, sample_count)
    xs = [row['x'] for row in primal['trajectory']]
    rows = history.sample(xs)
    max_tangent_energy = 0.0
    for a, b, _ in history.segments:
        x = (a+b)/2
        state = history.state(x); _, b_now, _ = state[:3]
        tangent = state[3:].reshape(len(history.modes), 3)
        observed = history.observe(x)
        bprime = observed['primal']['bprime']
        dbprime = np.array([observed['tangent'][m]['bprime'] for m in history.modes])
        for cohort in history.bank.entries:
            if cohort.primal.u >= x:
                continue
            E, Pi, dE, dPi = cohort.energy_pressure_tangent(x, b_now, tangent[:, 1])
            step = 1e-25
            _, _, complex_dE, _ = cohort.energy_pressure_tangent(x+1j*step, b_now+1j*step*bprime,
                                                               tangent[:, 1]+1j*step*dbprime)
            defect = complex_dE.imag/step+4*dE+2*(bprime*dPi+dbprime*Pi)
            max_tangent_energy = max(max_tangent_energy, float(abs(defect[0])/max(float(E), abs(float(dE[0])), 1e-30)))
    constraint = max(r['tangent']['full']['C_scaled'] for r in rows)
    propagation = max(r['tangent']['full']['constraint_propagation_scaled'] for r in rows)
    event = max((r['tangent_event']['full']['energy_jump_theta_scaled'] for r in history.events), default=0.0)
    jacobians = [e['birth_differential'] for e in history.events if history.config.mode == 'P24']
    gates = dict(primal['gate_results'])
    gates.update({'linearized_constraint': constraint <= LINEARIZED_CONSTRAINT_ATOL,
                  'linearized_constraint_propagation': propagation <= LINEARIZED_CONSTRAINT_ATOL,
                  'per_cohort_tangent_energy': max_tangent_energy <= TANGENT_ENERGY_ATOL,
                  'source_event_tangent_energy': event <= TANGENT_EVENT_ATOL,
                  'frozen_tangent_memory': history.bank.unchanged()})
    return {'schema': 'bass.s8.tangent.diagnostics.v1', 'parameter': history.parameter, 'modes': list(history.modes),
            'gate_results': gates, 'max_linearized_constraint_scaled': constraint,
            'max_linearized_constraint_propagation_scaled': propagation,
            'max_per_cohort_tangent_energy_relative': max_tangent_energy,
            'max_source_event_tangent_energy_scaled': event,
            'max_covariance_condition': max((e['covariance_condition'] for e in jacobians), default=None),
            'min_covariance_eigenvalue': min((min(e['covariance_eigenvalues']) for e in jacobians), default=None),
            'max_birth_moment_derivative_residual': max((max(abs(v) for v in e['moment_derivative_residual'])
                                                        for e in jacobians), default=0.0),
            'primal_diagnostics': {k: v for k, v in primal.items() if k not in ('trajectory', 'events')},
            'old_stock_digests': [e.primal.digest() for e in history.bank.entries if e.primal.role.startswith('old')],
            'tangent_memory_digests': history.bank.entry_digests,
            'nfev': history.nfev, 'trajectory': rows, 'events': history.events}
