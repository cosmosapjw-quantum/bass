"""CE1-J: expanding-path panel-local continuum-versus-ray source bounds.

Opt-in exact-real oracle. Physical source, stored binary path and all residuals
are inherited unchanged. No production solver or formal code proof claim.
"""
from __future__ import annotations
from fractions import Fraction
import numpy as np
from .einstein_interval import Interval, _iv_fraction, propagate_interval
from .einstein_tabulated_source import (
    TabulatedRadiation, certified_tabulated_pressure)
from .einstein_tabulated_sharp import initial_continuum_pressure_cap
from .einstein_tabulated_time import certify_tabulated_computed_path
from .einstein_tabulated_local import _reprop, certify_common_linear_growth, C_SLOPE
from .einstein_error_budget import HermitePath, rk4_path


def certify_local_source_envelope(source: TabulatedRadiation, path: HermitePath,
                                  *, end: float = .08, shear=(.2, -.13, -.07),
                                  subcells: int = 1, slope: Fraction = C_SLOPE) -> dict:
    """Transfer source discrepancy by exact isotropic scale covariance.

    If ell_i(u) >= c*u, for u in panel [t_j,t_{j+1}], put
    x_i=ell_i-c*t_j in [0, B_i-c*t_j].  Both continuum and stored
    binary-ray pressures satisfy P(ell+s*1)=exp(-4*s)P(ell).
    This contracts an ordinary certified_tabulated_pressure source bound
    on the shifted cube; it does not change any physical input.
    """
    if not isinstance(source,TabulatedRadiation) or not isinstance(path,HermitePath):
        raise TypeError('CE1-F source and stored HermitePath required')
    # Explicitly import PR244's independently reproduced P1 origin obligation.
    if not np.array_equal(path.coefficients[:,0,:],path.states[:-1]):
        raise ValueError('Hermite panel-origin / binary stored-knot mismatch')
    growth = certify_common_linear_growth(source,path,end=end,shear=shear,slope=slope)
    original = certify_tabulated_computed_path(source,path,end=end,shear=shear,subcells=subcells)
    pmax=initial_continuum_pressure_cap(source)['pressure_max_upper']
    ce1h,ce1i,jac_caps = _reprop(original,path,source,pmax,shear=shear,slope=slope)
    box=original['geometry_box_upper']
    uniform=Interval(float(original['source_pressure_upper']))
    per_panel_eta=[]; shifted_boxes=[]; shift_lowers=[]
    for j in range(len(original['rows'])):
        t0=_iv_fraction(Fraction(float(path.times[j])))
        shift=(_iv_fraction(slope)*t0).lower
        # Box upper endpoints are outward rounded; subtract a certified lower
        # shift and take the directed upper, never subtract a nearest rounded
        # positive amount as if it were an exact lower bound.
        shifted=[max(0.,(Interval(float(v))-Interval(shift)).upper) for v in box]
        cert=certified_tabulated_pressure(source,shifted)
        scaled=(Interval(float(cert['bound_max']))*(-4*Interval(shift)).exp()).upper
        new_cap=min(uniform.upper,scaled)
        if new_cap<0:raise ArithmeticError('Negative source bound')
        per_panel_eta.append(new_cap)
        shifted_boxes.append(shifted)
        shift_lowers.append(shift)
    src=[Interval(0),Interval(0)]
    rows=[]
    for j,row in enumerate(original['rows']):
        dt=Interval(float(path.times[j+1]))-Interval(float(path.times[j]))
        src=propagate_interval(src,dt,Interval(float(jac_caps[j])),Interval(0),Interval(float(per_panel_eta[j])))
        rows.append({'panel':j,'u_left':float(path.times[j]),
                     'source_upper':per_panel_eta[j],
                     'shift_lower':shift_lowers[j],
                     'shifted_box_upper':shifted_boxes[j],
                     'pressure_jacobian_upper':jac_caps[j]})
    out={
        'initial':[float(v) for v in ce1i['initial']],
        'source':[x.upper for x in src],
        'time_and_jump':[float(v) for v in ce1i['time_and_jump']],
    }
    out['total']=[sum((Interval(out[k][i]) for k in ('initial','source','time_and_jump')),Interval(0)).upper for i in range(2)]
    if any(out['total'][i]>ce1i['total'][i] + 1.e-20 for i in range(2)):
        raise ArithmeticError('New envelope exceeds old under same evidence')
    return {
        'status':'CE1J_SCOPED_SOURCE_LOCAL',
        'growth_certificate':growth,
        'per_panel_source_upper':per_panel_eta,
        'per_panel_source_certificates':rows,
        'constant_source_upper':uniform.upper,
        'geometry_Emax_unchanged':original['Emax_upper'],
        'ce1g_total':original['total_ell_h_upper'],
        'ce1h_total':ce1h['total'],
        'ce1i':ce1i,
        'ce1j':out,
        'target_met':out['total'][1] < 1e-5,
        'frozen_target':1e-5,
        'rays':len(source.n),
        'refinement':source.refinement,
        'production_ready':False,
        'formal_mpfr_implementation_proof':False,
        'distinct_author_review':'NOT_RUN',
    }


def run_local_source_rk4(source, *, steps=4, end=.08,
                           shear=(.2,-.13,-.07),subcells=1,
                           slope:Fraction=C_SLOPE,backend=None):
    if backend!='python_oracle':
        raise ValueError("Explicit backend='python_oracle' required")
    if isinstance(steps,bool) or not isinstance(steps,int) or not 1<=steps<=256:
        raise ValueError('steps 1..256 required')
    p=rk4_path(source,source.initial_state(shear),end,steps,backend=backend)
    return certify_local_source_envelope(source,p,end=end,shear=shear,subcells=subcells,slope=slope)
