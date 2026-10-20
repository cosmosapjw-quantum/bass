#!/usr/bin/env python3
"""Read-only S12 history receipt observer; no integration or projection calls.

The observer recomputes energy and its parameter differential from W,V directly.
Its PASS is scoped to one receipt's internal, ownership and fixed-event gates.
FD, independent Python/Rust comparison, driver agreement and omission
identification are separate ensemble checks in run_history_validation.py.
"""
from __future__ import annotations
import argparse
import cmath
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import struct

ALGORITHM = 'BASS_S12_FIXED_EVENT_FULL_BIRTH_MEMORY_V1'
VIGILODE = 'a21d573980f66fe02891bd216153443b5352f921'
OWNER = '0e25846433170d0f420c4cda44a0bedbf02cd177'
PROJECTOR = '1f937f16dcb5a7dbdce92a66881d45276b67b202c56bdc232c1d281ad7fc6fcb'
GATE = 1e-11
EXACT_GATE = Fraction(3, 10**15)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def finite(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def clean(value):
    if isinstance(value, float) and not math.isfinite(value):
        return repr(value)
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(v) for v in value]
    return value


def bits(x):
    return struct.unpack('<Q', struct.pack('<d', float(x)))[0]


def physical_digest(c):
    values = [c['u'], c['b_birth'], c['energy_birth'], *c['mu'], *c['alpha']]
    h = hashlib.sha256(b''.join(struct.pack('<d', float(x)) for x in values))
    h.update(c['role'].encode())
    return h.hexdigest()


def memory_digest(c):
    h = hashlib.sha256(c['physical_sha256'].encode())
    values = [c['birth_b_theta'], c['memory_theta'], *c['mu_b'], *c['alpha_b'],
              *c['mu_theta'], *c['alpha_theta']]
    h.update(b''.join(struct.pack('<d', float(x)) for x in values))
    return h.hexdigest()


def exact_moments(mu, alpha):
    norm = m2 = m4 = Fraction(0)
    for m, a in zip(mu, alpha):
        z = Fraction.from_float(float(m))**2
        a = Fraction.from_float(float(a))
        norm += a
        m2 += a*(3*z-1)/2
        m4 += a*(35*z*z-30*z+3)/8
    return norm-1, m2, m4


def scaled(a, b):
    if len(a) != len(b) or not a:
        raise ValueError('SCALED_ARRAY_SHAPE')
    if not all(finite(x) for x in [*a, *b]):
        raise ValueError('SCALED_NONFINITE')
    denominators = [1+max(abs(x), abs(y)) for x, y in zip(a, b)]
    if not all(math.isfinite(d) and d > 0 for d in denominators):
        raise ValueError('SCALED_DENOMINATOR')
    return max(abs(x-y)/d for x, y, d in zip(a, b, denominators))


def direct_observe(x, state, cohorts, config, exposure):
    """Direct W,V variation, independent of Rust ME/MP/L decomposition."""
    h, b, y, H, B, Y = state
    if not finite(x) or not all(finite(v) for v in state) or h <= 0:
        raise ValueError('OBSERVER_STATE_DOMAIN')
    fields = [[] for _ in range(4)]
    for c in cohorts:
        p = c['physical']
        if x < p['u']:
            raise ValueError('OBSERVER_FUTURE_COHORT')
        perp, para = math.exp(2*(b-p['b_birth'])), math.exp(-4*(b-p['b_birth']))
        delta = B-c['memory_theta']
        terms = [[] for _ in range(4)]
        for m, a, mt, at in zip(p['mu'], p['alpha'], c['mu_theta'], c['alpha_theta']):
            W, V = perp*(1-m*m), para*m*m
            R = math.sqrt(W+V)
            N = V-W/2
            Wt = 2*W*delta-2*perp*m*mt
            Vt = -4*V*delta+2*para*m*mt
            Rt = (Wt+Vt)/(2*R)
            Dt = (Vt-Wt/2)/R-N*Rt/(R*R)
            for target, value in zip(terms, [a*R, a*N/R, at*R+a*Rt, at*N/R+a*Dt]):
                target.append(value)
        factor = p['energy_birth']*math.exp(-4*(x-p['u']))
        for target, values in zip(fields, terms):
            target.append(factor*math.fsum(values))
    E, P, Et, Pt = [math.fsum(v) for v in fields]
    Ed = config['donor0']*math.exp(-3*x-config['decay_lambda']*exposure)
    L = config['cosmological_constant']
    fh = (-h*h-2*y*y-Ed/2-E+L)/h
    rhs = [fh, y/h, -3*y+P/h,
           (-2*h*H-4*y*Y-Et)/h-fh*H/h, Y/h-y*H/h**2,
           -3*Y+Pt/h-P*H/h**2]
    C = h*h-y*y-Ed-E-L
    Ct = 2*h*H-2*y*Y-Et
    scale = h*h+y*y+Ed+E+L
    Et_prime = -4*Et-2*(rhs[1]*Pt+rhs[4]*P)
    Ct_prime = 2*rhs[0]*H+2*h*rhs[3]-2*rhs[2]*Y-2*y*rhs[5]-Et_prime
    propagation = Ct_prime+2*Ct
    if not all(finite(v) for v in [E, P, Et, Pt, Ed, C, Ct, scale, propagation, *rhs]) or scale <= 0:
        raise ValueError('OBSERVER_FINITE_POSITIVE_DENOMINATOR')
    return {'E': E, 'P': P, 'Et': Et, 'Pt': Pt, 'Ed': Ed, 'C': C, 'Ct': Ct,
            'scale': scale, 'propagation': propagation, 'rhs': rhs}


def cohort_energy_complex_step(x, state, cohort, b_prime, B_prime):
    """Differentiate direct W,V along the actual background/tangent flow.

    Frozen birth coordinates, amplitudes and derivative companions remain real
    constants. No conservation right-hand side is used to obtain E' or Et'.
    """
    eps = 1e-28
    xc = complex(x, eps)
    b = complex(state[1], eps*b_prime)
    B = complex(state[4], eps*B_prime)
    p = cohort['physical']
    perp = cmath.exp(2*(b-p['b_birth']));para = cmath.exp(-4*(b-p['b_birth']))
    delta = B-cohort['memory_theta']
    terms = [[] for _ in range(4)]
    for m, a, mt, at in zip(p['mu'], p['alpha'], cohort['mu_theta'], cohort['alpha_theta']):
        W, V = perp*(1-m*m), para*m*m
        R = cmath.sqrt(W+V);N = V-W/2
        Wt = 2*W*delta-2*perp*m*mt
        Vt = -4*V*delta+2*para*m*mt
        Rt = (Wt+Vt)/(2*R)
        Dt = (Vt-Wt/2)/R-N*Rt/(R*R)
        for target, value in zip(terms, [a*R, a*N/R, at*R+a*Rt, at*N/R+a*Dt]):
            target.append(value)
    factor = p['energy_birth']*cmath.exp(-4*(xc-p['u']))
    values = [factor*complex(math.fsum(v.real for v in term), math.fsum(v.imag for v in term))
              for term in terms]
    if not all(math.isfinite(v.real) and math.isfinite(v.imag) for v in values):
        raise ValueError('COHORT_COMPLEX_STEP_NONFINITE')
    E, P, Et, Pt = [v.real for v in values]
    E_prime, Et_prime = values[0].imag/eps, values[2].imag/eps
    primal_residual = E_prime+4*E+2*b_prime*P
    tangent_residual = Et_prime+4*Et+2*(b_prime*Pt+B_prime*P)
    primal_den = max(abs(E), 1e-30)
    tangent_den = max(abs(E), abs(Et), 1e-30)
    if not all(finite(v) for v in [E_prime, Et_prime, primal_residual, tangent_residual,
                                   primal_den, tangent_den]) or min(primal_den, tangent_den) <= 0:
        raise ValueError('COHORT_COMPLEX_STEP_DENOMINATOR')
    return {'epsilon': eps, 'E_prime': E_prime, 'Et_prime': Et_prime,
            'primal_residual': primal_residual, 'tangent_residual': tangent_residual,
            'primal_denominator': primal_den, 'tangent_denominator': tangent_den,
            'primal_relative': abs(primal_residual)/primal_den,
            'tangent_relative': abs(tangent_residual)/tangent_den}


def assess(inp, receipt, *, input_sha256, source_commit=None, binary_sha256=None):
    checks, metrics = [], {}
    def check(name, passed, *, category='structure', **details):
        checks.append({'name': name, 'category': category, 'pass': bool(passed), **clean(details)})
    def numerical(name, value, gate, **details):
        check(name, finite(value) and value <= gate, category='numerical',
              value=value, gate=gate, **details)
    control = inp.get('control')
    externally_bound = source_commit is not None and binary_sha256 is not None
    try:
        check('receipt_schema', receipt.get('schema') == 'BASS_S12_HISTORY_RUN_V1')
        check('execution_completed', receipt.get('status') == 'completed' and receipt.get('failure') is None)
        check('algorithm_and_owners', receipt.get('algorithm') == ALGORITHM
              and receipt.get('vigilode_source') == VIGILODE and receipt.get('spectral_owner') == OWNER
              and receipt.get('projector_sha256') == PROJECTOR)
        check('input_roundtrip', receipt.get('input') == inp)
        binding = receipt['binding']
        check('exact_input_hash', binding.get('input_sha256') == input_sha256)
        check('source_binding', source_commit is not None and binding.get('source_commit') == source_commit,
              expected=source_commit, actual=binding.get('source_commit'))
        check('binary_binding', binary_sha256 is not None and binding.get('binary_sha256') == binary_sha256,
              expected=binary_sha256, actual=binding.get('binary_sha256'))
        check('no_pending_birth', receipt.get('pending_birth') is None)
        c = inp['config']
        k = c['k']
        du = c['birth_end']/k if k else 0.
        births = [(j+0.5)*c['birth_end']/k for j in range(k)] if c['donor0']*c['decay_lambda'] else []
        endpoints = births+[c['x_end']]
        events, segments, cohorts = receipt['events'], receipt['segments'], receipt['final_cohorts']
        old = inp['initial_cohorts'];old_n = len(old);gauge = inp['parameter'] == 'b0'
        expected_old = [physical_digest(p) for p in old]
        check('old_input_owner_digests', expected_old == inp['expected_old_digests']
              == receipt['old_stock_digests'])
        check('completed_cardinality', len(events) == len(births) and len(segments) == len(endpoints)
              and len(cohorts) == old_n+len(births), events=len(events), segments=len(segments),
              cohorts=len(cohorts), expected_events=len(births))
        if len(events) != len(births) or len(cohorts) != old_n+len(births):
            raise ValueError('INCOMPLETE_COHORT_PREFIX')
        exact_max = 0.
        derivative_norm_max = derivative_moment_max = 0.
        for i, cohort in enumerate(cohorts):
            p = cohort['physical'];mu, alpha = p['mu'], p['alpha'];n = len(mu)
            arrays = [alpha, cohort['mu_b'], cohort['alpha_b'], cohort['mu_theta'], cohort['alpha_theta']]
            shape = n >= 2 and all(len(a) == n for a in arrays)
            check(f'cohort_{i}_shape', shape)
            if not shape:
                raise ValueError('COHORT_SHAPE')
            check(f'cohort_{i}_finite_positive', all(finite(v) for a in [mu, *arrays] for v in a)
                  and all(a > 0 for a in alpha) and all(abs(m) <= 1 for m in mu)
                  and finite(p['energy_birth']) and p['energy_birth'] > 0
                  and all(finite(cohort[v]) for v in ['birth_b_theta', 'memory_theta']))
            check(f'cohort_{i}_strict_support', all(a < b for a, b in zip(mu, mu[1:])))
            check(f'cohort_{i}_exact_parity', mu == [-m for m in reversed(mu)]
                  and alpha == alpha[::-1]
                  and cohort['mu_b'] == [-v for v in reversed(cohort['mu_b'])]
                  and cohort['alpha_b'] == cohort['alpha_b'][::-1]
                  and cohort['mu_theta'] == [-v for v in reversed(cohort['mu_theta'])]
                  and cohort['alpha_theta'] == cohort['alpha_theta'][::-1])
            check(f'cohort_{i}_frozen_digests', physical_digest(p) == cohort['physical_sha256']
                  and memory_digest(cohort) == cohort['memory_sha256'])
            numerical(f'cohort_{i}_physical_norm', abs(math.fsum(alpha)-1), 3e-15)
            dnorm = abs(math.fsum(cohort['alpha_theta']))
            derivative_norm_max = max(derivative_norm_max, dnorm)
            numerical(f'cohort_{i}_frozen_derivative_norm', dnorm, 1e-12)
            if i < old_n:
                check(f'old_{i}_physical_bytes', physical_digest(p) == expected_old[i])
                check(f'old_{i}_memory_contract', cohort['birth_b_theta'] == float(gauge)
                      and cohort['memory_theta'] == float(gauge)
                      and all(v == 0 for name in ['mu_b', 'alpha_b', 'mu_theta', 'alpha_theta']
                              for v in cohort[name]))
                continue
            j = i-old_n;event = events[j]
            residuals = exact_moments(mu, alpha)
            exact_max = max(exact_max, *(float(abs(v)) for v in residuals))
            check(f'birth_{j}_exact_norm_P24', all(abs(v) <= EXACT_GATE for v in residuals),
                  category='numerical', residual_exact=list(map(str, residuals)), gate=str(EXACT_GATE))
            cert = event['exact_moment_certificate']
            check(f'birth_{j}_certificate_readback', cert['pass'] is True
                  and Fraction(cert['sum_alpha_exact'])-1 == residuals[0]
                  and Fraction(cert['m2_exact']) == residuals[1] and Fraction(cert['m4_exact']) == residuals[2])
            state = event['state'];B = state[4]
            check(f'birth_{j}_fixed_coordinates', p['u'] == event['u'] == births[j]
                  and p['b_birth'] == state[1] and cohort['birth_b_theta'] == B)
            expected_B = 0. if control == 'omit_birth_memory' else B
            expected_mt = [0. if control == 'omit_mu_b' else v*B for v in cohort['mu_b']]
            expected_at = [0. if control == 'omit_alpha_b' else v*B for v in cohort['alpha_b']]
            check(f'birth_{j}_frozen_memory_rule', cohort['memory_theta'] == expected_B
                  and cohort['mu_theta'] == expected_mt and cohort['alpha_theta'] == expected_at)
            check(f'birth_{j}_event_digest_and_admission', event.get('admitted') is True
                  and event.get('physical_sha256') == cohort['physical_sha256']
                  and event.get('memory_sha256') == cohort['memory_sha256']
                  and event.get('previous_physical_and_memory_digests_unchanged') is True
                  and event.get('control') == control)
            if inp['birth_rule'] == 'source_frame_GL':
                check(f'birth_{j}_source_frame_fixed', mu == inp['coordinate_grid']['mu0']
                      and all(v == 0 for v in [*cohort['mu_b'], *cohort['alpha_b']]))
                prior = inp['coordinate_grid']['prior0'];mass = math.fsum(prior)
                numerical(f'birth_{j}_fresh_GL_only', scaled(alpha, [v/mass for v in prior]), 3e-15)
            else:
                mb = [-3*m*(1-m*m) for m in mu]
                numerical(f'birth_{j}_moving_support_derivative', scaled(cohort['mu_b'], mb), GATE)
                phi = [[(3*m*m-1)/2, (35*m**4-30*m*m+3)/8] for m in mu]
                phib = [[3*m*d, (35*m**3-15*m)*d/2] for m, d in zip(mu, cohort['mu_b'])]
                norm_b = abs(math.fsum(cohort['alpha_b']))
                moments_b = [math.fsum(ab*f[q]+a*fb[q] for ab, a, f, fb in
                                      zip(cohort['alpha_b'], alpha, phi, phib)) for q in range(2)]
                derivative_moment_max = max(derivative_moment_max, *map(abs, moments_b))
                numerical(f'birth_{j}_implicit_norm_derivative', norm_b, 1e-12)
                numerical(f'birth_{j}_implicit_moment_derivative', max(map(abs, moments_b)), GATE)
                mass = math.fsum(alpha)
                means = [math.fsum(a*f[q] for a, f in zip(alpha, phi))/mass for q in range(2)]
                centered = [[f[q]-means[q] for q in range(2)] for f in phi]
                aa = math.fsum(a*f[0]*f[0] for a, f in zip(alpha, centered))/mass
                cc = math.fsum(a*f[1]*f[1] for a, f in zip(alpha, centered))/mass
                off = math.fsum(a*f[0]*f[1] for a, f in zip(alpha, centered))/mass
                high = (aa+cc+math.hypot(aa-cc, 2*off))/2
                low = (aa*cc-off*off)/high
                condition = high/low
                check(f'birth_{j}_implicit_covariance', finite(low) and low >= 1e-10
                      and finite(condition) and condition <= 1e8, category='numerical',
                      minimum_eigenvalue=low, condition=condition)
        metrics.update(exact_new_birth_max_residual=exact_max,
                       frozen_derivative_norm_max=derivative_norm_max,
                       implicit_moment_derivative_max=derivative_moment_max)

        # Preserve and compare the complete physical+memory prefix per segment.
        trace = []
        previous_state = None
        for j, segment in enumerate(segments):
            begin = 0. if j == 0 else endpoints[j-1];end = endpoints[j]
            expected_times = [begin]+[x for x in inp['output_times'] if begin < x < end]+[end]
            raw_t, raw_y = segment['raw_times'], segment['raw_states']
            size = 6 if inp['solver']['arm'] == 'mf_into_ls6' else 7
            check(f'segment_{j}_identity', segment['index'] == j and segment['begin'] == begin
                  and segment['end'] == end and segment['arm'] == inp['solver']['arm']
                  and segment['mode'] == inp['mode'] and segment['exposure'] == j*du)
            check(f'segment_{j}_completed_schedule', segment['success'] is True
                  and segment['status'] == 'returned_success' and raw_t == expected_times
                  and segment['output_times'] == expected_times
                  and len(raw_y) == len(raw_t) and all(len(z) == size for z in raw_y))
            if len(raw_y) != len(raw_t) or any(len(z) != size for z in raw_y):
                raise ValueError('RAW_SEGMENT_SHAPE')
            check(f'segment_{j}_raw_bits', segment['raw_time_bits'] == [bits(x) for x in raw_t]
                  and segment['raw_state_bits'] == [[bits(v) for v in z] for z in raw_y])
            pairs = [[a['physical_sha256'], a['memory_sha256']] for a in cohorts[:old_n+j]]
            check(f'segment_{j}_frozen_prefix', segment['cohort_count'] == old_n+j
                  and segment['physical_and_memory_digests'] == pairs
                  and segment['fresh_driver'] is True and segment['fresh_immutable_bank'] is True)
            check(f'segment_{j}_restart_state', segment['start_state'] == raw_y[0][:6]
                  and (previous_state is None or raw_y[0][:6] == previous_state))
            if j == 0:
                trace.append((raw_t[0], raw_y[0][:6]))
            trace.extend((x, z[:6]) for x, z in zip(raw_t[1:], raw_y[1:]))
            previous_state = raw_y[-1][:6]
            if size == 7:
                numerical(f'segment_{j}_clock', max(abs(z[6]-x) for x, z in zip(raw_t, raw_y)), GATE)
        observations = receipt['observations']
        h0 = math.sqrt(c['y0']**2+c['donor0']+c['old_isotropic']+c['old_anisotropic']+c['cosmological_constant'])
        initial = [h0, c['b0'], c['y0'], *([0., 1., 0.] if gauge else [c['y0']/h0, 0., 1.])]
        check('fixed_initial_primal_and_tangent', bool(observations) and observations[0]['state'] == initial)
        check('observations_raw_identity', [(o['x'], o['state']) for o in observations] == trace)
        check('observation_final_time', bool(observations) and observations[0]['x'] == 0.
              and observations[-1]['x'] == c['x_end']
              and all(a['x'] < b['x'] for a, b in zip(observations, observations[1:])))
        maxima = {key: 0. for key in ['C_relative', 'Ctheta_relative', 'propagation_relative',
                                      'reported_observer_scaled', 'gauge_absolute', 'clock_absolute',
                                      'independent_cohort_energy_relative',
                                      'independent_cohort_tangent_energy_relative']}
        min_denominator = math.inf
        for i, o in enumerate(observations):
            x, state = o['x'], o['state']
            admitted = sum(u <= x for u in births)
            direct = direct_observe(x, state, cohorts[:old_n+admitted], c, admitted*du)
            den = direct['scale'];min_denominator = min(min_denominator, den)
            cv, ct, propagation = abs(direct['C'])/den, abs(direct['Ct'])/den, abs(direct['propagation'])/den
            actual = [o['e_radiation'], o['pi'], o['e_theta'], o['pi_theta'], o['e_donor'], o['c'], o['c_theta']]
            expected = [direct[v] for v in ['E', 'P', 'Et', 'Pt', 'Ed', 'C', 'Ct']]
            consistency = scaled(actual, expected)
            for name, value in [('C_relative', cv), ('Ctheta_relative', ct),
                                ('propagation_relative', propagation), ('reported_observer_scaled', consistency),
                                ('clock_absolute', abs(o['clock_error']))]:
                maxima[name] = max(maxima[name], value)
            numerical(f'observation_{i}_C', cv, GATE, denominator=den)
            numerical(f'observation_{i}_Ctheta', ct, GATE, denominator=den)
            numerical(f'observation_{i}_algebraic_Ctheta_consistency', propagation, GATE, denominator=den)
            numerical(f'observation_{i}_reported_readback', consistency, GATE)
            numerical(f'observation_{i}_clock', abs(o['clock_error']), GATE)
            for j, cohort in enumerate(cohorts[:old_n+admitted]):
                energy = cohort_energy_complex_step(x, state, cohort, direct['rhs'][1], direct['rhs'][4])
                maxima['independent_cohort_energy_relative'] = max(
                    maxima['independent_cohort_energy_relative'], energy['primal_relative'])
                maxima['independent_cohort_tangent_energy_relative'] = max(
                    maxima['independent_cohort_tangent_energy_relative'], energy['tangent_relative'])
                numerical(f'observation_{i}_cohort_{j}_independent_energy', energy['primal_relative'], GATE,
                          derivative=energy['E_prime'], residual=energy['primal_residual'],
                          denominator=energy['primal_denominator'], complex_step=energy['epsilon'])
                numerical(f'observation_{i}_cohort_{j}_independent_tangent_energy', energy['tangent_relative'], GATE,
                          derivative=energy['Et_prime'], residual=energy['tangent_residual'],
                          denominator=energy['tangent_denominator'], complex_step=energy['epsilon'])
            if gauge:
                gv = max(abs(state[3]), abs(state[5]), abs(state[4]-1))
                maxima['gauge_absolute'] = max(maxima['gauge_absolute'], gv)
                numerical(f'observation_{i}_source_frame_gauge', gv, GATE)
        metrics.update(maxima, minimum_constraint_denominator=min_denominator)

        jump_max = {'energy': 0., 'energy_theta': 0., 'pi_theta': 0.}
        event_den_min = math.inf
        for j, event in enumerate(events):
            x, state = event['u'], event['state']
            before = direct_observe(x, state, cohorts[:old_n+j], c, j*du)
            after = direct_observe(x, state, cohorts[:old_n+j+1], c, (j+1)*du)
            den = before['Ed']+before['E']
            check(f'event_{j}_positive_denominator', finite(den) and den > 0, denominator=den)
            if not finite(den) or den <= 0:
                raise ValueError('EVENT_DENOMINATOR')
            event_den_min = min(event_den_min, den)
            transfer = before['Ed']*(-math.expm1(-c['decay_lambda']*du))
            p = cohorts[old_n+j]['physical']
            numerical(f'event_{j}_fixed_donor_transfer', abs(p['energy_birth']-transfer)/den, GATE, denominator=den)
            check(f'event_{j}_no_state_jump', event['state_jump'] == [0.]*6
                  and event['state'] == segments[j]['raw_states'][-1][:6])
            jumps = {'energy': after['Ed']+after['E']-before['Ed']-before['E'],
                     'energy_theta': after['Et']-before['Et'], 'pi_theta': after['Pt']-before['Pt']}
            for name, value in jumps.items():
                ratio = abs(value)/den;jump_max[name] = max(jump_max[name], ratio)
                numerical(f'event_{j}_{name}_continuity', ratio, GATE, residual=value, denominator=den)
                numerical(f'event_{j}_{name}_reported', abs(event[name+'_jump']-value)/den, GATE, denominator=den)
            for side, values in [('before', before), ('after', after)]:
                reported = event[side]['moments']
                numerical(f'event_{j}_{side}_direct_moments',
                          scaled([reported[q] for q in [0, 1, 8, 9, 7]],
                                 [values[q] for q in ['E', 'P', 'Et', 'Pt', 'Ed']]), GATE)
                numerical(f'event_{j}_{side}_direct_rhs', scaled(event[side]['rhs'], values['rhs']), GATE)
        metrics.update(event_jump_relative=jump_max,
                       minimum_event_denominator=event_den_min if events else None,
                       observation_count=len(observations), event_count=len(events), segment_count=len(segments))
    except Exception as exc:
        check('assessment_exception', False, exception_type=type(exc).__name__, error=str(exc))
    structural = all(c['pass'] for c in checks if c['category'] == 'structure')
    numerical_pass = bool([c for c in checks if c['category'] == 'numerical']) and all(
        c['pass'] for c in checks if c['category'] == 'numerical')
    completed = receipt.get('status') == 'completed' and receipt.get('failure') is None
    scoped_pass = completed and structural and numerical_pass and externally_bound and control == 'full'
    if control != 'full':
        status = 'OMISSION_CONTROL_OBSERVED' if completed and structural else 'OMISSION_CONTROL_INVALID'
    else:
        status = 'PASS_SCOPED_INTERNAL_GATES' if scoped_pass else 'FAIL'
    return clean({'schema': 'BASS_S12_HISTORY_ASSESSMENT_V1', 'status': status,
        'scope': 'Single-receipt fixed-event internal gates; ensemble FD/reference/driver checks remain separate; no continuum/native spectral certificate',
        'execution_completed': completed, 'external_binding_verified': externally_bound and structural,
        'structural_pass': structural, 'numerical_gates_pass': numerical_pass,
        'full_scientific_pass': scoped_pass, 'control': control,
        'omission_is_not_a_full_physics_pass': control != 'full',
        'checks_passed': sum(c['pass'] for c in checks), 'checks_total': len(checks),
        'checks': checks, 'metrics': metrics})


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input', type=Path, required=True);p.add_argument('--receipt', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True);p.add_argument('--source-commit')
    p.add_argument('--binary', type=Path)
    a = p.parse_args()
    data = a.input.read_bytes();raw = a.receipt.read_bytes()
    result = assess(json.loads(data), json.loads(raw), input_sha256=sha(data),
                    source_commit=a.source_commit, binary_sha256=sha(a.binary.read_bytes()) if a.binary else None)
    result['input_file_sha256'] = sha(data);result['receipt_file_sha256'] = sha(raw)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
    print(json.dumps({k: result[k] for k in ['status', 'checks_passed', 'checks_total', 'control']}))
    return 0 if result['full_scientific_pass'] or result['status'] == 'OMISSION_CONTROL_OBSERVED' else 1


if __name__ == '__main__':
    raise SystemExit(main())

