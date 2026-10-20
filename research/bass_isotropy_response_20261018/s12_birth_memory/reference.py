"""Independent direct chain-rule reference and fixed NEW S12 fixtures.

No S8/S9/S10 campaign is invoked.  The reference differentiates W,V directly,
not the Rust memory-channel decomposition, and never reads a measured forcing.
"""
from __future__ import annotations
from copy import deepcopy
import hashlib
import math
from pathlib import Path
import struct
import sys
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent/'s11_p246'))
import projector as p11


def digest_cohort(c):
    values = [c['u'], c['b_birth'], c['energy_birth'], *c['mu'], *c['alpha']]
    h = hashlib.sha256(b''.join(struct.pack('<d', float(v)) for v in values))
    h.update(c['role'].encode())
    return h.hexdigest()


def gl(n):
    mu, weights = np.polynomial.legendre.leggauss(n)
    if not np.array_equal(mu, -mu[::-1]) or not np.array_equal(weights, weights[::-1]):
        raise ValueError('GL_PARITY')
    return mu, weights


def birth_rule(b, grid, rule='P24'):
    m, w = np.asarray(grid['mu0']), np.asarray(grid['prior0'])
    if rule == 'source_frame_GL':
        mu, alpha = m.copy(), w/math.fsum(w)
        zero = np.zeros_like(mu)
        cert = p11.exact_certificate(mu, alpha, 4)
        if cert['status'] != 'PASS_SCOPED':
            raise ValueError('GL_EXACT_BIRTH')
        return mu, alpha, zero.copy(), zero.copy(), {'certificate': cert}
    rad = np.sqrt(np.exp(2*b)*(1-m*m)+np.exp(-4*b)*m*m)
    mu = m*np.exp(-2*b)/rad
    prior = w/rad**3
    prior /= math.fsum(prior)
    proj = p11.project_birth(mu, prior, order=4, declared_isotropic_birth=True)
    alpha = np.asarray(proj.weights)
    lam = np.asarray([float(v) for v in proj.multipliers])
    mu_b = -3*mu*(1-mu*mu)
    phi = np.column_stack(((3*mu*mu-1)/2, (35*mu**4-30*mu*mu+3)/8))
    phi_b = np.column_stack((3*mu*mu_b, (35*mu**3-15*mu)*mu_b/2))
    mass = math.fsum(alpha)
    average = lambda a: np.sum(alpha[:, None]*a, axis=0)/mass
    mean = average(phi)
    centered = phi-mean
    cov = centered.T @ (alpha[:, None]*centered)/mass
    eig = np.linalg.eigvalsh(cov)
    if eig[0] < 1e-10 or eig[-1]/eig[0] > 1e8:
        raise ValueError('KL_COVARIANCE_DOMAIN')
    score = 6*(phi[:, 0]-np.dot(prior, phi[:, 0])/math.fsum(prior))+phi_b @ lam
    score_bar = np.dot(alpha, score)/mass
    cross = np.sum(alpha[:, None]*centered*(score-score_bar)[:, None], axis=0)/mass
    lam_b = np.linalg.solve(cov, -average(phi_b)-cross)
    alpha_b = alpha*(score-score_bar+centered @ lam_b)
    # A symmetric mathematical input should produce exact parity in this scalar
    # rule; do not repair/asymmetrize an existing physical stock.
    if not np.array_equal(mu_b, -mu_b[::-1]) or not np.array_equal(alpha_b, alpha_b[::-1]):
        raise ValueError('NEW_REFERENCE_DERIVATIVE_PARITY')
    norm = abs(math.fsum(alpha_b))
    moments = np.sum(alpha_b[:, None]*phi+alpha[:, None]*phi_b, axis=0)
    if norm > 1e-12 or np.max(np.abs(moments)) > 1e-11:
        raise ValueError('NEW_REFERENCE_DERIVATIVE_GATE')
    return mu, alpha, mu_b, alpha_b, {'certificate': proj.certificate,
        'covariance_eigenvalues': eig.tolist(), 'covariance_condition': float(eig[-1]/eig[0]),
        'normalization_derivative': norm, 'moment_derivative': moments.tolist()}


def direct_moments(x, b, b_theta, bank):
    """R and numerator variations from W,V; complex-safe for independent CS."""
    E = P = Et = Pt = 0.0
    for c in bank['cohorts']:
        mu, alpha = np.asarray(c['mu']), np.asarray(c['alpha'])
        mt, at = np.asarray(c['mu_theta']), np.asarray(c['alpha_theta'])
        d = b-c['b_birth']
        perp, para = np.exp(2*d), np.exp(-4*d)
        W, V = perp*(1-mu*mu), para*mu*mu
        rad = np.sqrt(W+V)
        numerator = V-W/2
        stress = numerator/rad
        delta = b_theta-c['memory_theta']
        Wt = 2*W*delta-2*perp*mu*mt
        Vt = -4*V*delta+2*para*mu*mt
        Rt = (Wt+Vt)/(2*rad)
        Dt = (Vt-Wt/2)/rad-numerator*Rt/(rad*rad)
        scale = c['energy_birth']*np.exp(-4*(x-c['u']))
        E += scale*np.sum(alpha*rad)
        P += scale*np.sum(alpha*stress)
        Et += scale*np.sum(at*rad+alpha*Rt)
        Pt += scale*np.sum(at*stress+alpha*Dt)
    donor = bank['donor0']*np.exp(-3*x-bank['decay_lambda']*bank['exposure'])
    return np.asarray([E, P, Et, Pt, donor])


def direct_rhs(x, state, bank):
    h, b, y, H, B, Y = state
    E, P, Et, Pt, donor = direct_moments(x, b, B, bank)
    fh = (-h*h-2*y*y-donor/2-E+bank['cosmological_constant'])/h
    return np.asarray([fh, y/h, -3*y+P/h,
        (-2*h*H-4*y*Y-Et)/h-fh*H/h, Y/h-y*H/h**2,
        -3*Y+Pt/h-P*H/h**2])


def complex_derivatives(x, state, bank):
    eps = 1e-28
    jac = np.column_stack([direct_rhs(x, np.asarray(state, complex)+1j*eps*np.eye(6)[j], bank).imag/eps
                           for j in range(6)])
    pt = direct_rhs(x+1j*eps, np.asarray(state, complex), bank).imag/eps
    return jac, pt


def core_fixture():
    m, w = gl(16)
    a = w*(1+0.4*(3*m*m-1)/2)
    a /= math.fsum(a)
    old = {'u': 0., 'b_birth': 0.25, 'energy_birth': 0.03, 'memory_theta': 0.,
           'mu': m.tolist(), 'alpha': a.tolist(), 'mu_theta': [0.]*16, 'alpha_theta': [0.]*16}
    m, w = gl(32)
    grid = {'mu0': m.tolist(), 'prior0': w.tolist()}
    mu, alpha, mb, ab, diag = birth_rule(0.65, grid)
    new = {'u': 0.18, 'b_birth': 0.65, 'energy_birth': 0.07, 'memory_theta': 0.12,
           'mu': mu.tolist(), 'alpha': alpha.tolist(), 'mu_theta': (0.12*mb).tolist(),
           'alpha_theta': (0.12*ab).tolist()}
    bank = {'donor0': 0.8, 'decay_lambda': 0.9, 'exposure': 0.15,
            'cosmological_constant': 0.7, 'cohorts': [old, new]}
    queries = []
    for i in range(24):
        strain = [-0.6, -0.3, -0.1, 0.0, 0.2, 0.6][i % 6]
        state = [0.9+0.03*(i % 4), 0.65+strain, (-1 if i % 2 else 1)*(0.01+0.002*(i % 3)),
                 0.015+0.002*(i % 4), -0.08+0.03*(i % 5), 0.3+0.01*(i % 4)]
        direction = [0.2, -0.3, 0.1, -0.4, 0.25, 0.15]
        queries.append({'x': 0.3+0.01*i, 'state': state, 'direction': direction})
    return bank, queries, diag


def core_protocol(bank, queries):
    fmt = lambda xs: ' '.join(format(float(v), '.17g') for v in xs)
    lines = ['BASS_S12_CORE_V1', 'BANK '+fmt([bank['donor0'], bank['decay_lambda'],
        bank['exposure'], bank['cosmological_constant']])+f" {len(bank['cohorts'])} {len(queries)}"]
    for c in bank['cohorts']:
        lines.append('COHORT '+fmt([c['u'], c['b_birth'], c['energy_birth'], c['memory_theta']])+f" {len(c['mu'])}")
        lines.extend('RAY '+fmt(row) for row in zip(c['mu'], c['alpha'], c['mu_theta'], c['alpha_theta']))
    lines.extend('QUERY '+fmt([q['x'], *q['state'], *q['direction']]) for q in queries)
    return '\n'.join(lines)+'\n'


def history_input(rule='P24', parameter='y0', mode='fused', control='full', arm='small_clock7', extended=False):
    n, k = (64, 16) if extended else (32, 4)
    m, w = gl(n)
    old_m, old_w = gl(128)
    old_a = old_w/math.fsum(old_w)
    old_an = old_w*(1+0.4*(3*old_m**2-1)/2)
    old_an /= math.fsum(old_an)
    c = {'k': k, 'n': n, 'b0': 0.65, 'y0': 0.025, 'donor0': 0.8,
         'old_isotropic': 0.015, 'old_anisotropic': 0.01, 'cosmological_constant': 0.7,
         'decay_lambda': 0.9, 'birth_end': 0.8 if extended else 0.3,
         'x_end': 1.2 if extended else 0.4}
    cohorts = [{'u': 0., 'b_birth': c['b0'], 'energy_birth': energy,
                'mu': old_m.tolist(), 'alpha': alpha.tolist(), 'role': role}
               for energy, alpha, role in [(c['old_isotropic'], old_a, 'old_isotropic'),
                    (c['old_anisotropic'], old_an, 'old_physical_anisotropic')]]
    return {'schema': 'BASS_S12_HISTORY_INPUT_V1', 'config': c,
        'coordinate_grid': {'mu0': m.tolist(), 'prior0': w.tolist()},
        'initial_cohorts': cohorts, 'expected_old_digests': [digest_cohort(a) for a in cohorts],
        'output_times': np.linspace(0., c['x_end'], 17 if not extended else 49).tolist(),
        'parameter': parameter, 'birth_rule': rule, 'mode': mode, 'control': control,
        'solver': {'arm': arm, 'rtol': 3e-13, 'atol': 3e-15, 'initial_step': 0.001,
            'max_step': 0.025, 'max_attempts': 100000, 'linear_rtol': 1e-14, 'linear_atol': 1e-16},
        'provenance': {'unit': 'S12_NEW_CASE', 'completed_campaign_replay': False,
            'old_stock_policy': 'Physical fixed source-frame GL128 and anisotropic stock; never reweighted',
            'spectral_owner': '0e25846433170d0f420c4cda44a0bedbf02cd177',
            'reference_birth_trajectory_in_input': False}}


def python_history(inp):
    """New short independent DOP853 check, explicitly not the old S8 campaign."""
    from scipy.integrate import solve_ivp
    c = inp['config'];gauge = inp['parameter'] == 'b0';bank = {'cohorts': [],
        **{key: c[key] for key in ['donor0', 'decay_lambda', 'cosmological_constant']}, 'exposure': 0.}
    for cohort in inp['initial_cohorts']:
        new = deepcopy(cohort)
        new.update(memory_theta=float(gauge), mu_theta=[0.]*len(new['mu']), alpha_theta=[0.]*len(new['mu']))
        bank['cohorts'].append(new)
    h0 = math.sqrt(c['y0']**2+c['donor0']+c['old_isotropic']+c['old_anisotropic']+c['cosmological_constant'])
    state = np.array([h0, c['b0'], c['y0'], *( [0., 1., 0.] if gauge else [c['y0']/h0, 0., 1.])])
    du = c['birth_end']/c['k'] if c['k'] else 0.
    births = [(j+0.5)*c['birth_end']/c['k'] for j in range(c['k'])] if c['donor0']*c['decay_lambda'] else []
    begin = 0.;rows=[{'x': 0., 'state': state.tolist()}];events=[];nfev=0
    for j, end in enumerate([*births, c['x_end']]):
        times = [float(t) for t in inp['output_times'] if begin < t < end]+[float(end)]
        sol = solve_ivp(lambda x, y: direct_rhs(x, y, bank), (begin, end), state,
                        method='DOP853', rtol=3e-14, atol=3e-16, max_step=0.0125,
                        t_eval=times)
        if not sol.success:
            raise ArithmeticError('S12_NEW_PYTHON_HISTORY:'+sol.message)
        nfev += sol.nfev
        rows.extend({'x': float(x), 'state': y.tolist()} for x, y in zip(sol.t, sol.y.T))
        state = sol.y[:, -1];begin=end
        if j == len(births):break
        before = direct_moments(end, state[1], state[4], bank)
        energy = float(before[4])*(-math.expm1(-c['decay_lambda']*du))
        mu, alpha, mb, ab, diag = birth_rule(float(state[1]), inp['coordinate_grid'], inp['birth_rule'])
        B = float(state[4]);memory = B;mt=mb*B;at=ab*B
        if inp['control'] == 'omit_birth_memory':memory=0.
        elif inp['control'] == 'omit_mu_b':mt*=0
        elif inp['control'] == 'omit_alpha_b':at*=0
        bank['cohorts'].append({'u': end, 'b_birth': float(state[1]), 'energy_birth': energy,
            'mu': mu.tolist(), 'alpha': alpha.tolist(), 'memory_theta': memory,
            'mu_theta': mt.tolist(), 'alpha_theta': at.tolist()})
        bank['exposure']=(j+1)*du
        after=direct_moments(end, state[1], state[4], bank)
        events.append({'x': end, 'state': state.tolist(), 'energy_jump': float(after[0]+after[4]-before[0]-before[4]),
                       'energy_tangent_jump': float(after[2]-before[2]), 'pressure_tangent_jump': float(after[3]-before[3]),
                       'birth': diag})
    return {'schema': 'BASS_S12_NEW_PYTHON_REFERENCE_V1', 'method': 'DOP853',
        'state_rows': rows, 'events': events, 'nfev': nfev, 'final_bank': bank,
        'old_S8_campaign_invoked': False}
