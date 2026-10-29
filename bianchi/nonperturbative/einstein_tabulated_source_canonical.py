"""CE1-K: opt-in canonical-safe Bianchi-I panel-local source certificate.

Combines canonical CE1-J PR246's current-source/path checks and CE1-I
panelwise positivity with CE1-J PR247's exact common-scale source law.
Same exact-binary Hermite, source, RK4, MPFR192 and target; no production
or program-verification claim.
"""
from __future__ import annotations

from hashlib import sha256
import math

import numpy as np

from .einstein_error_budget import HermitePath, rk4_path
from .einstein_interval import Interval, propagate_interval
from .einstein_tabulated_local import certify_local_tabulated_path
from .einstein_tabulated_source import TabulatedRadiation, certified_tabulated_pressure, certified_tabulated_energy


def canonical_shifted_box(geometry_box, lower_logscale):
    """Outward B-m product box, with proof-premise rejection (no silent clipping)."""
    if len(geometry_box) != 3:
        raise ValueError('Three dimensional geometry box required')
    m = float(lower_logscale)
    if not math.isfinite(m) or m < 0:
        raise ValueError('Finite nonnegative certified lower geometry bound required')
    if m == 0.:
        if any(not math.isfinite(float(v)) or float(v) < 0 for v in geometry_box):
            raise ValueError('Nonnegative finite geometry box required')
        return [float(v) for v in geometry_box]
    shifted=[]
    for v in geometry_box:
        v=float(v)
        if not math.isfinite(v) or v < 0:
            raise ValueError('Nonnegative finite geometry box required')
        # MPFR interval subtraction (not nearest-rounded subtraction).
        d = Interval(v)-Interval(m)
        if d.lower < 0 and d.upper < 0:
            raise ValueError('Inconsistent geometry box: upper below certified lower')
        if v < m:
            raise ValueError('Inconsistent geometry box: upper below certified lower')
        shifted.append(d.upper)
    return shifted


def _current_source_path_sha(source, path):
    """Scoped byte identity used before/after certification, not a formal race proof."""
    h=sha256()
    for a in (source.mu_edges, source.phi_fraction_edges, source.cell_energy,
              source.mass, source.n, path.times, path.states, path.coefficients):
        a=np.asarray(a)
        h.update(repr((a.shape,a.dtype.str)).encode('ascii'))
        h.update(a.tobytes(order='C'))
    return h.hexdigest()


def certify_canonical_panel_source(source: TabulatedRadiation, path: HermitePath,
                                   *, end=.08, shear=(.2,-.13,-.07),subcells=1):
    """Certify same canonical CE1-I initial/time carriers and tighter source forcing.

    The canonical CE1-I routine calls the same single current-source CE1-G
    certification once, including PR244 majorant update and all Hermite origins.
    It also supplies panelwise positive exact/Hermite common lower logscale.
    We recompute the exact source discrepancy on its shifted box (MPFR192),
    then repropagate only that source carrier with the same local pressure caps.
    """
    if not isinstance(source,TabulatedRadiation) or not isinstance(path,HermitePath):
        raise TypeError('Current positive TabulatedRadiation and HermitePath required')
    previous_id = _current_source_path_sha(source,path)
    canonical=certify_local_tabulated_path(source,path,end=end,shear=shear,
                                           subcells=subcells)
    certified_Emax=certified_tabulated_energy(source)['energy_max_upper']
    uniform=Interval(float(canonical['source_pressure_upper']))
    glob=canonical['geometry_box_upper']
    src=[Interval(0),Interval(0)]
    rows=[]
    for j,row in enumerate(canonical['rows']):
        lower=float(row['shared_logscale_lower'])
        shifted=canonical_shifted_box(glob,lower)
        # Recompute current source certificate with no stale positive-ray cache.
        cert=certified_tabulated_pressure(source,shifted)
        if lower == 0:
            scale=Interval(1)
        else:
            scale=(-4*Interval(lower)).exp()
        local_bound=(scale*Interval(float(cert['bound_max']))).upper
        eta=min(uniform.upper,local_bound)
        if eta < 0:
            raise ArithmeticError('Nonnegative pressure discrepancy upper required')
        dt=Interval(float(path.times[j+1]))-Interval(float(path.times[j]))
        # propagate_interval expects E=Pcap (thus internal k=2sqrt(E));
        # L_j=4Pcap by the exact pressure-Jacobian row sum.
        pcap=Interval(float(row['pressure_cap_upper']))
        src=propagate_interval(src,dt,pcap,Interval(0),Interval(eta))
        rows.append({
            'panel':j,'left_time':float(path.times[j]),
            'right_time':float(path.times[j+1]),
            'certified_lower_logscale':lower,
            'shifted_source_box_upper':shifted,
            'raw_source_upper':float(cert['bound_max']),
            'scaled_source_upper':local_bound,
            'source_upper':eta,
            'pressure_upper':row['pressure_cap_upper'],
            'lipschitz_upper':row['lipschitz_upper'],
            'accumulated_source_h_upper':src[1].upper,
        })
    if previous_id != _current_source_path_sha(source,path):
        raise RuntimeError('Source/path binary identity changed during certification')
    initial=[Interval(float(v)) for v in canonical['initial_ell_h_upper']]
    time=[Interval(float(v)) for v in canonical['time_and_jump_ell_h_upper']]
    total=[sum((z[k] for z in (initial,src,time)),Interval(0)).upper for k in range(2)]
    if any(total[k]>canonical['local_total_ell_h_upper'][k] for k in range(2)):
        raise ArithmeticError('Panel-local source certificate exceeds canonical uniform source comparison')
    return {
      'result_status':'CE1K_CANONICAL_AND_SOURCE_LOCAL_SCOPED',
      'source_and_path_sha256':previous_id,
      'original_Emax':certified_Emax,
      'geometry_box_upper':glob,
      'global_source_upper':uniform.upper,
      'panel_rows':rows,
      'source_error_upper_h':src[1].upper,
      'ce1i_source_error_upper_h':canonical['source_ell_h_upper'][1],
      'total_h_upper':total[1],
      'ce1i_total_h_upper':canonical['local_total_ell_h_upper'][1],
      'initial_error_upper_h':canonical['initial_ell_h_upper'][1],
      'time_jump_error_upper_h':canonical['time_and_jump_ell_h_upper'][1],
      'total_ell_h_upper':total,
      'ce1i':canonical,
      'target_h':1.e-5,
      'target_met':total[1]<1.e-5,
      'upper_dag':'9/15',
      'production_ready':False,
      'merge_ready':False,
      'formal_mpfr_program_verified':False,
      'distinct_author_R6_C9':'NOT_RUN',
    }


def run_canonical_panel_source(source, *, backend=None,steps=4,end=.08,
                               shear=(.2,-.13,-.07),subcells=1):
    if backend != 'python_oracle':
        raise ValueError("Explicit backend='python_oracle' required")
    if isinstance(steps,bool) or not isinstance(steps,int) or not 1<=steps<=256:
        raise ValueError('steps must be integer 1..256')
    if not isinstance(source, TabulatedRadiation):
        raise TypeError('Current positive TabulatedRadiation required')
    path=rk4_path(source,source.initial_state(shear),end,steps,backend=backend)
    return certify_canonical_panel_source(source,path,end=end,shear=shear,
                                          subcells=subcells)