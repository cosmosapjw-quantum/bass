"""CE1-U four-panel MPFR192 comparison for original-cell GL4/6/8.

Unlike the parent's midpoint certificate, this uses ONLY CE1-U certified
positive ideal-GL and binary-ray pressure discrepancy. The time residual is
recomputed for the actual new stored GL source by CE1-C/G's MPFR192 Taylor
majorant over each original RK4/Hermite panel with all binary knot jumps.
"""
from __future__ import annotations
from fractions import Fraction as Q
import json
import math
import numpy as np

from bianchi.nonperturbative.einstein_error_budget import rk4_path, HermitePath
from bianchi.nonperturbative.einstein_interval import (
    Interval as I, _iv_fraction as iv, _bernstein_box_binary,
    residual_taylor_mpfr, propagate_interval,
)
from bianchi.nonperturbative.einstein_tabulated_time import _panel_endpoint_jump
from research.ce1u_20261030.certified_gl_source import (
    sample_gl_source, certify_gl_source, B, absmax,
)

HORIZON=.08
SHEAR=(.2,-.13,-.07)


def certify_gl_coupled(order: int, *, subcells: int=1) -> dict:
    if order not in (4,6,8):raise ValueError('Only GL4/6/8 frozen positive source')
    if isinstance(subcells,bool) or not isinstance(subcells,int) or subcells not in (1,2):
        raise ValueError('S0/S1 bounded subcells 1 or 2 only')
    source=sample_gl_source(order)
    cert=certify_gl_source(order,source)
    path=rk4_path(source,source.initial_state(SHEAR),HORIZON,4,backend='python_oracle')
    if not isinstance(path,HermitePath) or len(path.times)!=5 or path.times[0]!=0 or path.times[-1]!=HORIZON:
        raise ValueError('Original four-panel time/path contract violated')
    if not np.array_equal(path.coefficients[:,0,:],path.states[:-1]):
        raise ValueError('Exact binary Hermite origins must match stored left knots')
    if not np.array_equal(path.states[0],source.initial_state(SHEAR)):
        raise ValueError('Original GL proper-time initial state altered')
    if abs(sum(SHEAR))>1e-14:
        raise ValueError('Trace-free physical shear input required')
    # Exact source E0 and sigma0; third shear is exact -(sx+sy).
    sx,sy=Q.from_float(SHEAR[0]),Q.from_float(SHEAR[1])
    sig=[iv(sx),iv(sy),iv(-sx-sy)]
    em=iv(source.continuum_energy)
    hbar=((em+sum((s*s for s in sig),I(0))/2)/3).sqrt()
    hexact=[hbar+s for s in sig]
    if any(x.lower<=0 or x.upper>=.8 for x in hexact):
        raise ValueError('Certified analytic continuum expanding h0<.8 required')
    if any(float(x)<=0 or x>=.8 for x in path.states[0,3:]):
        raise ValueError('Stored expanding h0<.8 required')
    assert source.energy0<1 and float(source.continuum_energy)<1
    global_upper=.07
    for panel in range(4):
        low,high=_bernstein_box_binary(path,panel)
        if min(low)<0 or max(high[:3])>=global_upper or min(low[3:])<0:
            raise ValueError('Entire exact binary Hermite panel not inside certified positive geometry box')
    delta0=max(absmax(hexact[k]-I(float(path.states[0,3+k]))) for k in range(3))
    initial=[I(0),I(delta0)]
    source_error=[I(0),I(0)]
    time_error=[I(0),I(0)]
    eta=I(cert['total_pressure_error_upper'])
    rows=[]
    for j in range(4):
        defect=residual_taylor_mpfr(source,path,j,subcells=subcells)
        dt=I(float(path.times[j+1]))-I(float(path.times[j]))
        initial=propagate_interval(initial,dt,I(1),I(0),I(0))
        source_error=propagate_interval(source_error,dt,I(1),I(0),eta)
        time_error=propagate_interval(time_error,dt,I(1),I(float(defect['ell_defect'])),I(float(defect['h_defect'])))
        jell,jh=_panel_endpoint_jump(path,j)
        time_error=[time_error[0]+I(jell),time_error[1]+I(jh)]
        rows.append({'panel':j,'time_start':float(path.times[j]),'time_end':float(path.times[j+1]),
             'ell_defect_upper':defect['ell_defect'],'h_defect_upper':defect['h_defect'],
             'knot_ell_upper':jell,'knot_h_upper':jh,
             'initial_h_upper':initial[1].upper,'source_h_upper':source_error[1].upper,
             'time_jump_h_upper':time_error[1].upper})
    total=[sum((z[k] for z in (initial,source_error,time_error)),I(0)).upper for k in (0,1)]
    return {'schema':'bass.ce1u.gl_coupled_mpfr192.v1','order':order,
        'rays':len(source.n),'subcells':subcells, 'steps':4,'u_end':HORIZON,
        'source':cert,'exact_initial_h_difference_upper':delta0,
        'initial_h_upper':initial[1].upper,'source_h_upper':source_error[1].upper,
        'time_jump_h_upper':time_error[1].upper,
        'final_ell_upper':total[0],'final_h_upper':total[1],
        'fixed_target_h':1e-5,'target_met':total[1]<1e-5,
        'rows':rows,'upper_dag':'9/15','production_ready':False,'merge_ready':False,
        'time_note':'Fresh actual 4-panel GL binary RK4 Hermite defect and exact endpoint jumps, MPFR192',
        'rigor_note':'Conditional on original CE1-C/G residual_taylor_mpfr positive-source fourth-derivative lemma and actual MPFR code',
        'native_rust_role':'Independent binary64 E/P/J only; not interval proof'}

if __name__=='__main__':
    import sys
    for n in map(int,sys.argv[1:] or (6,8)):
        out=certify_gl_coupled(n)
        print(json.dumps(out,indent=2))
