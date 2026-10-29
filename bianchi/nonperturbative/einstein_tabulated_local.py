"""CE1-I research oracle: panelwise decaying pressure-Jacobian enclosure.

Scope: same positive original-cell continuum, expanding diagonal collisionless
Bianchi I, exact stored binary64 RK4/Hermite path, no production promotion.
The *only* change relative to CE1-H is the nonlinear comparison coefficient.
"""
from __future__ import annotations

from fractions import Fraction
from .einstein_interval import Interval, _iv_fraction, propagate_interval
from .einstein_tabulated_source import TabulatedRadiation, _q, _real
from .einstein_error_budget import HermitePath, rk4_path
from .einstein_tabulated_time import certify_tabulated_computed_path
from .einstein_tabulated_sharp import initial_continuum_pressure_cap, _initial_constraint_mismatch


C_SLOPE = Fraction(3, 8)  # fixed frozen fixture, exact rational; full growth certificate required


def certify_common_linear_growth(source: TabulatedRadiation, path: HermitePath,
                                 *, end: float = .08, shear=(.2, -.13, -.07),
                                 slope: Fraction = C_SLOPE) -> dict:
    """Prove ell_exact_i(u), ell_Hermite_i(u) >= slope*u, 0<=u<=T.

    Exact flow uses Hamiltonian constraint and positivity of P_i, giving
    theta'<=-2/3 theta^2, h_i'>=-theta h_i. For the piecewise real
    binary-coefficient cubic, use *exact rational* Bernstein inequalities
    on ell_i(v)-slope*(t_left+v*dt), including jump endpoints.
    """
    if not isinstance(source, TabulatedRadiation) or not isinstance(path, HermitePath):
        raise TypeError('CE1-F source and HermitePath required')
    if not isinstance(slope, Fraction) or slope <= 0:
        raise ValueError('Positive exact rational slope required')
    if not (0 < end <= .2) or path.times[-1] != end or path.times[0] != 0:
        raise ValueError('Frozen positive time domain expected')
    shear_f = _real(shear, (3,))
    sx,sy = (_iv_fraction(Fraction(float(_q(x)))) for x in shear_f[:2])
    s = [sx,sy,-(sx+sy)]
    E = _iv_fraction(source.continuum_energy)
    Hbar=((E + sum((z*z for z in s),Interval(0))/2)/3).sqrt()
    h0=[Hbar + z for z in s]
    if min(z.lower for z in h0) <= 0:
        raise ValueError('Exact expanding initial sector not certified')
    theta0=3*Hbar
    denom=(Interval(1)+(Interval(2)/3)*theta0*Interval(float(end))).sqrt()**3
    exact_slope_lower=min((hi/denom).lower for hi in h0)
    # Rigorous comparison: exact represented rational vs outward binary64 bound.
    if _iv_fraction(slope).upper >= exact_slope_lower:
        raise ValueError('Candidate slope fails exact Einstein lower bound')
    slack = []
    zero = Fraction(0)
    for j in range(len(path.times)-1):
        t0=Fraction(float(path.times[j]));t1=Fraction(float(path.times[j+1]))
        if t1<=t0:raise ValueError('Nonpositive time panel')
        rows=[]
        for i in range(3):
            a=[Fraction(float(path.coefficients[j,k,i])) for k in range(4)]
            a[0] -= slope*t0
            a[1] -= slope*(t1-t0)
            # Exact power->Bernstein degree-3 transform.
            B=(a[0],a[0]+a[1]/3,a[0]+2*a[1]/3+a[2]/3,sum(a))
            if min(B)<zero:
                raise ValueError(f'Exact-binary Hermite growth fails: panel={j},axis={i}')
            rows.append(min(B))
        slack.append([float(v) for v in rows])
    return {
        'status':'EXACT_RATIONAL_PATH_AND_MPFR_FLOW_GROWTH_CERTIFIED',
        'slope_numerator':slope.numerator,'slope_denominator':slope.denominator,
        'exact_flow_slope_lower':exact_slope_lower,
        'path_min_bernstein_slack_per_panel':slack,
        'hermite_check':'exact rational Bernstein of stored binary coefficients',
        'exact_flow_check':'positive h0, Hamiltonian constraint, Raychaudhuri inequality',
        'formal_python_mpfr_verified':False,
    }


def _reprop(baseline, path, source, pcap, *, shear, slope):
    Emax=baseline['Emax_upper']
    constant=min(float(pcap),float(Emax))
    eta=Interval(float(baseline['source_pressure_upper']))
    comparison=[Interval(constant) for _ in baseline['rows']]
    decay=[]
    ci=_iv_fraction(slope)
    for j in range(len(baseline['rows'])):
        tleft=Interval(float(path.times[j]))
        cap=Interval(constant)*(-4*ci*tleft).exp()
        decay.append(Interval(min(constant,cap.upper)))
    def propagate(caps):
        init=[Interval(0),Interval(_initial_constraint_mismatch(source,path,shear))]
        src=[Interval(0),Interval(0)];tim=[Interval(0),Interval(0)]
        for j,row in enumerate(baseline['rows']):
            dt=Interval(float(path.times[j+1]))-Interval(float(path.times[j]))
            init=propagate_interval(init,dt,caps[j],Interval(0),Interval(0))
            src=propagate_interval(src,dt,caps[j],Interval(0),eta)
            tim=propagate_interval(tim,dt,caps[j],Interval(row['ell_defect_upper']),
                                   Interval(row['h_defect_upper']))
            tim=[tim[0]+Interval(row['knot_jump_ell_upper']),
                 tim[1]+Interval(row['knot_jump_h_upper'])]
        total=[sum((e[k] for e in (init,src,tim)),Interval(0)).upper for k in range(2)]
        return {'initial':[z.upper for z in init], 'source':[z.upper for z in src],
                'time_and_jump':[z.upper for z in tim], 'total':total}
    return propagate(comparison), propagate(decay), [x.upper for x in decay]


def certify_pathlocal_tabulated_path(source: TabulatedRadiation, path: HermitePath,
                                      *, end: float=.08, shear=(.2,-.13,-.07),
                                      subcells: int=1, slope: Fraction=C_SLOPE) -> dict:
    """Fresh inherited whole-panel residuals + CE1-I panelwise Dini comparison."""
    growth=certify_common_linear_growth(source,path,end=end,shear=shear,slope=slope)
    baseline=certify_tabulated_computed_path(source,path,end=end,shear=shear,subcells=subcells)
    pressure=initial_continuum_pressure_cap(source)
    old,new,caps=_reprop(baseline,path,source,pressure['pressure_max_upper'],shear=shear,slope=slope)
    if any(new['total'][k]>old['total'][k]+1e-20 for k in range(2)):
        raise ArithmeticError('CE1-I exceeds CE1-H comparison on same evidence')
    return {
        'status':'SCOPED_CE1I_PATH_LOCAL_COMPARISON',
        'growth_certificate':growth,
        'constant_ce1h':old, 'decaying_ce1i':new,
        'ce1g_total_ell_h_upper':baseline['total_ell_h_upper'],
        'per_panel_pressure_cap_upper':caps,
        'source_pressure_upper_unchanged':baseline['source_pressure_upper'],
        'Emax_upper_unchanged':baseline['Emax_upper'],
        'refinement':source.refinement, 'rays':len(source.n),
        'target_h':1e-5, 'target_met':new['total'][1]<1e-5,
        'production_ready':False, 'formal_mpfr_program_verified':False,
    }


def run_pathlocal_tabulated_rk4(source, *, steps=4, end=.08,
                                shear=(.2,-.13,-.07),subcells=1,
                                backend=None):
    if backend!='python_oracle':
        raise ValueError("Explicit backend='python_oracle' required")
    if isinstance(steps,bool) or not isinstance(steps,int) or not 1<=steps<=256:
        raise ValueError('steps must be integer 1..256')
    p=rk4_path(source,source.initial_state(shear),end,steps,backend=backend)
    return certify_pathlocal_tabulated_path(source,p,end=end,shear=shear,subcells=subcells)
