"""CE1-C RED tests: directed-rounded MPFR arithmetic and interval source bounds."""
import math
import numpy as np
import pytest
from bianchi.nonperturbative.einstein_interval import Interval, pressure_bound_interval, propagate_interval

def test_exact_binary_inputs_and_outward_arithmetic():
    a=Interval(0.1); b=Interval.decimal('0.1')
    assert a.contains(0.1)
    from fractions import Fraction
    assert Fraction.from_float(b.lower) <= Fraction(1,10) <= Fraction.from_float(b.upper)
    assert (a+a-a).contains(0.1)
    thirds=Interval(1)/Interval(3)
    assert Fraction.from_float(thirds.lower) <= Fraction(1,3) <= Fraction.from_float(thirds.upper)

def test_transcendental_rounding():
    from mpmath import mp
    mp.dps=80
    for z in [-2.,-.25,0.,.1,1.7]:
        a=Interval(z).exp()
        assert mp.mpf(a.lower) <= mp.exp(mp.mpf(z)) <= mp.mpf(a.upper)
    for z in [.01,1.,3.]:
        a=Interval(z).sqrt()
        assert mp.mpf(a.lower) <= mp.sqrt(mp.mpf(z)) <= mp.mpf(a.upper)

def test_source_interval_parent_and_box_limits():
    from bianchi.nonperturbative.einstein_error_budget import PolynomialRadiation,source_bound_box
    s=PolynomialRadiation(ntheta=8,backend='python_oracle')
    lo=np.array([.1,.03,.08]);hi=np.array([.34,.18,.21])
    b=pressure_bound_interval(s,lo,hi)
    old=source_bound_box(s,lo,hi)
    assert np.all(np.array(b['bounds'])>=np.asarray(old['pressure_bound'])-1e-12)
    assert b['rounding_method']=='MPFR_DIRECTED'

def test_interval_comparison_propagation():
    prev=[Interval(0),Interval(0)]
    new=propagate_interval(prev,Interval(0.5),Interval(0.9),Interval(0),Interval.decimal('.0001'))
    assert new[0].lower>=0 and new[1].lower>=0
    assert new[1].upper>1.e-4*.5

def test_semidiscrete_interval_residual_contains_heldout_numeric_values():
    from bianchi.nonperturbative.einstein_error_budget import PolynomialRadiation,rk4_path
    from bianchi.nonperturbative.einstein_interval import residual_binary_interval
    s=PolynomialRadiation(ntheta=4,backend='python_oracle')
    p=rk4_path(s,s.initial_state(),.1,2,backend='python_oracle')
    b=residual_binary_interval(s,p,0,subcells=2)
    for t in np.linspace(0,.05,9):
        y=p.at(t);r=p.at(t,derivative=1)-s.rhs(t,y)
        assert max(abs(r[:3]))<=b['ell_defect']
        assert max(abs(r[3:]))<=b['h_defect']
    assert b['status']=='MPFR_OUTWARD_SEMIDISCRETE_RESIDUAL'

def test_interval_audit_preserves_unresolved_continuum_gap():
    from bianchi.nonperturbative.einstein_error_budget import PolynomialRadiation,rk4_path
    from bianchi.nonperturbative.einstein_interval import audit_binary_path,choose_scoped_budget
    s=PolynomialRadiation(ntheta=4,backend='python_oracle')
    p=rk4_path(s,s.initial_state(),.08,2,backend='python_oracle')
    a=audit_binary_path(s,p,subcells=2)
    assert a['semidiscrete_time_envelope'][1]>0
    assert a['combined_continuum_machine_certificate'] is False
    choice=choose_scoped_budget(lambda ntheta:PolynomialRadiation(ntheta=ntheta,backend='python_oracle'),[4],[2],target=1e3,end=.08,subcells=2)
    assert choice['status']=='CONDITIONAL_SELECTION_NOT_CONTINUUM_CERTIFIED'
    assert choice['selected']['continuum_machine_admitted'] is False

def test_rounded_quadrature_includes_known_float_node_weight_mismatch():
    from bianchi.nonperturbative.einstein_error_budget import PolynomialRadiation
    from bianchi.nonperturbative.einstein_interval import source_full_rounding_bound
    s=PolynomialRadiation(ntheta=6,backend='python_oracle')
    b=source_full_rounding_bound(s,[.2,.1,.3],[.2,.1,.3],max_K=3)
    assert b['continuum_source_enclosure'] is True
    assert np.all(np.array(b['bounds'])>=0)
    # Independent high resolution reference, only a falsification check.
    hi=PolynomialRadiation(ntheta=48,backend='python_oracle')
    diff=np.abs(np.array(s.moments([.2,.1,.3])[1])-np.array(hi.moments([.2,.1,.3])[1]))
    assert np.all(diff < b['bounds'])

def test_continuum_interval_audit_reports_positive_bounds():
    from bianchi.nonperturbative.einstein_error_budget import PolynomialRadiation,rk4_path
    from bianchi.nonperturbative.einstein_interval import audit_continuum_binary_path
    s=PolynomialRadiation(ntheta=4,backend='python_oracle')
    p=rk4_path(s,s.initial_state(),.06,2,backend='python_oracle')
    r=audit_continuum_binary_path(s,p,subcells=2,max_K=2)
    assert r['status']=='DIRECTED_ROUNDED_CONTINUUM_ODE_PATH_ENCLOSURE'
    assert r['total_envelope'][1]>r['time_envelope'][1]

def test_taylor_mpfr_bounds_interior_residuals_and_is_tighter():
    from bianchi.nonperturbative.einstein_error_budget import PolynomialRadiation,rk4_path
    from bianchi.nonperturbative.einstein_interval import residual_taylor_mpfr,residual_binary_interval
    s=PolynomialRadiation(ntheta=6,backend='python_oracle')
    p=rk4_path(s,s.initial_state(),.2,4,backend='python_oracle')
    tight=residual_taylor_mpfr(s,p,0,subcells=2)
    loose=residual_binary_interval(s,p,0,subcells=2)
    assert tight['h_defect']<loose['h_defect']
    for t in np.linspace(0,.05,15):
        r=p.at(t,derivative=1)-s.rhs(t,p.at(t))
        assert max(abs(r[:3]))<=tight['ell_defect']
        assert max(abs(r[3:]))<=tight['h_defect']

def test_constraint_initial_roundoff_and_target_selection():
    from bianchi.nonperturbative.einstein_error_budget import PolynomialRadiation,rk4_path
    from bianchi.nonperturbative.einstein_interval import constraint_initial_h_error,select_geometry_tolerance,exact_polynomial_positivity
    source=lambda ntheta:PolynomialRadiation(ntheta=ntheta,backend='python_oracle')
    s=source(4);p=rk4_path(s,s.initial_state(),.1,4,backend='python_oracle')
    delta=constraint_initial_h_error(s,p)
    assert 0<=delta['h_error_bound']<1e-14
    assert exact_polynomial_positivity(s)['strictly_positive']
    selection=select_geometry_tolerance(source,[(4,4)],target_h='.5',end=.1,subcells=2,max_K=2)
    assert selection['status']=='SCOPED_MPFR_ENCLOSED_TOLERANCE_MET'
    assert selection['selected']['initial_h_error_upper']<1e-14


def test_mpfr_interval_cleanup_survives_shutdown_globals():
    """A late destructor must not rely on torn-down module namespace."""
    import subprocess, sys
    program=("import gc\n"
             "from bianchi.nonperturbative.einstein_interval import Interval\n"
             "import bianchi.nonperturbative.einstein_interval as m\n"
             "z=Interval(1)\n"
             "m._lib=None\n"
             "del z\n"
             "gc.collect()\n")
    p=subprocess.run([sys.executable,'-c',program],capture_output=True,text=True,check=False)
    assert p.returncode==0 and 'Exception ignored in' not in p.stderr, p.stderr


def test_outward_sum_and_third_subcell_cover_exact_rationals():
    from fractions import Fraction
    from bianchi.nonperturbative.einstein_interval import exact_component_sum, exact_time_subcell
    z=exact_component_sum([.1,.2,.3]);exact=sum((Fraction.from_float(x) for x in [.1,.2,.3]),Fraction())
    assert Fraction.from_float(z.lower)<=exact<=Fraction.from_float(z.upper)
    cell=exact_time_subcell(0,3)
    assert Fraction.from_float(cell.lower)<=Fraction(0,1)<=Fraction.from_float(cell.upper)
    assert Fraction.from_float(cell.lower)<=Fraction(1,3)<=Fraction.from_float(cell.upper)

def test_derivative_mass_majorant_covers_exact_stored_binary_energy_and_ray_norm():
    from fractions import Fraction
    from bianchi.nonperturbative.einstein_error_budget import PolynomialRadiation
    from bianchi.nonperturbative.einstein_interval import stored_ray_energy_majorant
    s=PolynomialRadiation(ntheta=8,backend='python_oracle')
    cap=stored_ray_energy_majorant(s)
    mass=sum((Fraction.from_float(float(z)) for z in s.mass),Fraction())
    max_norm=max(sum((Fraction.from_float(float(q))**2 for q in n),Fraction()) for n in s.n)
    assert Fraction.from_float(cap)**2>=mass**2*max_norm
    assert cap>0
