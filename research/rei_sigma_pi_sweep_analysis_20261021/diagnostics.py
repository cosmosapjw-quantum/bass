"""Cancellation-aware diagnostics of saved signed LRS observables only."""
from __future__ import annotations
import math
import numpy as np

ARITHMETIC_FACTOR = float(128 * np.finfo(np.float64).eps)


def cancellation(p, r):
    """Vectorized, initialized masked divisions; divergent values use null."""
    p, r = np.broadcast_arrays(np.asarray(p, dtype=np.float64), np.asarray(r, dtype=np.float64))
    scale = np.abs(p) + np.abs(r)
    total = np.abs(p+r)
    ratio = np.full(scale.shape, np.nan)
    condition = np.full(scale.shape, np.nan)
    np.divide(total, scale, out=ratio, where=scale > 0)
    np.divide(scale, total, out=condition, where=(scale > 0) & (total > 0))
    statuses = np.full(scale.shape, 'FINITE', dtype=object)
    statuses[scale == 0] = 'ZERO_COMPONENT_SCALE'
    statuses[(scale > 0) & (total == 0)] = 'EXACT_CANCELLATION'
    def nullable(value):
        return [float(v) if math.isfinite(float(v)) else None for v in value.flat]
    return {'component_scale': scale.reshape(-1).tolist(), 'residual_fraction': nullable(ratio),
            'cancellation_fraction': nullable(1-ratio), 'condition': nullable(condition),
            'cancellation_status': statuses.reshape(-1).tolist()}


def arithmetic_check(actual, expected, scale):
    residual = abs(actual-expected)
    limit = ARITHMETIC_FACTOR * scale
    return {'residual': residual, 'component_scale': scale, 'limit': limit,
            'pass': residual <= limit if scale > 0 else residual == 0}


def row_diagnostics(row, kappa_time=None):
    """Preserve original redundant fields and report component-scaled residuals."""
    p, r, sigma = (float(row[k]) for k in ('signed_Pi_m', 'signed_Pi_r', 'signed_Sigma'))
    data = {k: v[0] for k, v in cancellation([p], [r]).items()}
    total = p+r
    scale = abs(p)+abs(r)
    checks = {'signed_total': arithmetic_check(row['signed_Pi_total'], total, scale)}
    for label, value in (('m', p), ('r', r), ('total', total)):
        relevant = abs(value) if label != 'total' else scale
        checks['half_norm_'+label] = arithmetic_check(row['Pi_'+label+'_half'], abs(value), relevant)
        checks['frobenius_'+label] = arithmetic_check(row['Pi_'+label+'_frobenius'], math.sqrt(2)*abs(value), math.sqrt(2)*relevant)
        data['normalized_work_'+label] = 2*sigma*value
    checks['shear_norm'] = arithmetic_check(row['Sigma_half'], abs(sigma), abs(sigma))
    checks['shear_frobenius'] = arithmetic_check(row['Sigma_frobenius'], math.sqrt(2)*abs(sigma), math.sqrt(2)*abs(sigma))
    checks['total_half_alias'] = arithmetic_check(row['Pi_half'], abs(total), scale)
    checks['total_frobenius_alias'] = arithmetic_check(row['Pi_frobenius'], math.sqrt(2)*abs(total), math.sqrt(2)*scale)
    checks['signed_total_alias'] = arithmetic_check(row['signed_Pi'], total, scale)
    checks['component_norm_sum'] = arithmetic_check(row['Pi_component_norm_sum'], scale, scale)
    dm, dr = row['D_m_Pa'], row['D_r_Pa']
    dscale = abs(dm)+abs(dr)
    radiation_parts = (row['Pi_gamma'], row['Pi_nu'], row['Pi_UV'])
    checks['massive_pressure'] = arithmetic_check(dm, row['Pi_massive'], abs(dm))
    checks['radiation_pressure'] = arithmetic_check(dr, sum(radiation_parts), sum(abs(v) for v in radiation_parts))
    checks['physical_total'] = arithmetic_check(row['D_total_Pa'], dm+dr, dscale)
    checks['physical_total_alias'] = arithmetic_check(row['D_physical_Pa'], dm+dr, dscale)
    for label, value in (('m', dm), ('r', dr), ('total', dm+dr)):
        wscale = 2*abs(row['s_inv_s'])*(abs(value) if label != 'total' else dscale)
        checks['physical_work_'+label] = arithmetic_check(row['shear_work_'+label+'_J_m3_s'], 2*row['s_inv_s']*value, wscale)
    checks['total_work_alias'] = arithmetic_check(row['shear_work_J_m3_s'], 2*row['s_inv_s']*(dm+dr), 2*abs(row['s_inv_s'])*dscale)
    checks['work_sum'] = arithmetic_check(row['shear_work_m_J_m3_s']+row['shear_work_r_J_m3_s'],
                                          row['shear_work_total_J_m3_s'], 2*abs(row['s_inv_s'])*dscale)
    if kappa_time is not None:
        factor = kappa_time/(math.sqrt(3)*row['H']*row['H'])
        checks['signed_massive_conversion'] = arithmetic_check(p, factor*dm, abs(factor)*dscale)
        checks['signed_radiation_conversion'] = arithmetic_check(r, factor*dr, abs(factor)*dscale)
        checks['signed_shear_conversion'] = arithmetic_check(sigma, math.sqrt(3)*row['s_inv_s']/row['H'], abs(sigma))
        for label in ('m', 'r', 'total'):
            physical = row['shear_work_'+label+'_J_m3_s']*kappa_time/(row['H']**3)
            checks['normalized_work_'+label] = arithmetic_check(physical, data['normalized_work_'+label], 2*abs(sigma)*scale)
    data['arithmetic_pass'] = all(item['pass'] for item in checks.values())
    return {'diag_'+k: value for k, value in data.items()}, checks


def matched_controls(cases):
    """Exact requested shear and same numerical cohort; no nearest borrowing."""
    controls = {}
    for case in cases:
        if case['signed_Pi_m_requested'] == 0 and case['signed_Pi_r_requested'] == 0:
            key = (case['signed_Sigma_requested'], case['cohort_id'])
            controls[key] = case
    for case in cases:
        case['raw_delta_signed_Sigma'] = case['final_signed_Sigma']-case['initial_signed_Sigma']
        control = controls.get((case['signed_Sigma_requested'], case['cohort_id']))
        case['control_case_id'] = control['case_id'] if control else None
        case['control_status'] = 'MATCHED' if control else 'MISSING_CONTROL'
        case['control_subtracted_final_signed_Sigma'] = (case['final_signed_Sigma']-control['final_signed_Sigma'] if control else None)
