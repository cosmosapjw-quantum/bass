"""Bounded checks on a prescribed background, not a reionization history solver.

No chemistry, native solver, repository state changes, or science admission.
The exact bounds are proved in manuscripts/REI_THEORY_KO.md.
"""
from __future__ import annotations
import json
from pathlib import Path
from fractions import Fraction
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import solve_ivp

OM, OR, OL = .315, .000092, .684908
ASTAR, AEND = 1/21, .2

def signed_coefficients(q: float, zero, plus, minus, half_plus, half_minus):
    """Five samples at identical declared coordinates; does not align histories.

Returns raw algebraic estimates, not detections. Input uncertainty, interpolation
    error, and response floors must be propagated by the consuming AX11 owner.
    """
    if not np.isfinite(q) or q <= 0: raise ValueError('positive finite q required')
    arr=np.asarray([zero,plus,minus,half_plus,half_minus],dtype=float)
    if not np.isfinite(arr).all():raise ValueError('finite same-shaped samples required')
    x0,xp,xm,xhp,xhm=arr
    ev=(xp+xm)/2-x0;odd=(xp-xm)/2
    evh=(xhp+xhm)/2-x0;oddh=(xhp-xhm)/2
    return {'even':ev,'odd':odd,'linear_leakage':(8*oddh-odd)/(3*q),
            'quadratic':(16*evh-ev)/(3*q*q),'cubic':4*(odd-2*oddh)/(3*q**3)}

def radiation_case(q: float, nmu: int = 64, tol: float = 1e-11):
    mu,w=leggauss(nmu);w=w/2
    def hf(a):return np.sqrt(OR/a**4+OM/a**3+OL)
    def moments(b):
        ap=np.exp(2*b)*(1-mu*mu);az=np.exp(-4*b)*mu*mu
        d=np.sqrt(ap+az)
        return w@d,w@((az-ap/2)/d)
    def rhs(lna,y):
        a=np.exp(lna);s=q*hf(ASTAR)*(ASTAR/a)**3;h=np.hypot(hf(a),s)
        phi,dp=moments(y[0])
        return [s/h,OR/a*dp/h,1/h]
    grid=np.linspace(np.log(ASTAR),np.log(AEND),257)
    sol=solve_ivp(rhs,(grid[0],grid[-1]),[0,0,0],method='DOP853',t_eval=grid,
                  rtol=tol,atol=tol*1e-2)
    if not sol.success:raise RuntimeError(sol.message)
    a=np.exp(sol.t);b,integ,clock=sol.y
    h=np.hypot(hf(a),q*hf(ASTAR)*(ASTAR/a)**3)
    ds=integ/a**3/h
    phi=np.array([moments(bb)[0] for bb in b])
    extra=(phi-1)*OR/a**4/hf(a)**2
    return {'q':q,'b_end':float(b[-1]),'clock_H0_end':float(clock[-1]),
            'max_abs_delta_s_over_H_sampled':float(np.max(abs(ds))),
            'max_extra_radiation_over_background_sampled':float(np.max(extra)),
            'Phi_end':float(phi[-1]),'nfev':sol.nfev},np.column_stack([a,b,ds,extra,clock])

if __name__=='__main__':
    root=Path(__file__).resolve().parents[1];out=root/'evidence'
    q=.01;c=[.5,.03,-.07,.11,.17]
    def poly(v):return sum(x*v**j for j,x in enumerate(c))
    est=signed_coefficients(q,*map(poly,[0,q,-q,q/2,-q/2]))
    analytic_shear=Fraction(23,3750)*Fraction(506,125)*Fraction(6688,1000000)*Fraction(1571,10000)
    analytic_energy=Fraction(23,3750)*Fraction(506,125)*Fraction(5911,1000000)**2
    cases=[];tables=[]
    for qq in [0.,q,-q]:
        case,table=radiation_case(qq);cases.append(case);tables.append(table)
    fine,ft=radiation_case(q,96,2e-13)
    d=float(np.max(np.abs(tables[1]-ft)))
    verdict={
      'quartic_polynomial_linear_recovery':abs(est['linear_leakage']-c[1])<1e-12,
      'quartic_polynomial_quadratic_recovery':abs(est['quadratic']-c[2])<1e-10,
      'quartic_polynomial_cubic_recovery':abs(est['cubic']-c[3])<1e-8,
      'zero_shear_recovered':abs(cases[0]['b_end'])==0 and abs(cases[0]['max_abs_delta_s_over_H_sampled'])<1e-15,
      'clock_even_under_signed_q':abs(cases[1]['clock_H0_end']-cases[2]['clock_H0_end'])<1e-12,
      'b_odd_under_signed_q':abs(cases[1]['b_end']+cases[2]['b_end'])<1e-12,
      'radiation_scalar_not_exactly_even':abs(cases[1]['Phi_end']-cases[2]['Phi_end'])>1e-8,
      'sampled_stress_under_proved_bound':max(v['max_abs_delta_s_over_H_sampled'] for v in cases)<float(analytic_shear),
      'sampled_energy_under_proved_bound':max(v['max_extra_radiation_over_background_sampled'] for v in cases)<float(analytic_energy),
      'prescribed_background_refinement':d<1e-10}
    report={'scope':'analytic theorem arithmetic and prescribed-background empirical check; NO chemistry history',
      'limits_predeclared_in_source':True,'analytic_shear_rational':str(analytic_shear),
      'analytic_energy_rational':str(analytic_energy),'analytic_shear_bound':float(analytic_shear),
      'analytic_energy_bound':float(analytic_energy),'sampled_cases':cases,
      'refinement_max_all_column_difference':d,'signed_coefficients_manufactured':est,
      'verdict':{k:bool(v) for k,v in verdict.items()},'all_checks_passed':all(verdict.values()),
      'full_coupled_geometry_error_bound':None,'abundance_error_bound':None,'scientific_admission':'NOT_ISSUED'}
    (out/'REI_THEORY_CHECKS.json').write_text(json.dumps(report,indent=2))
    np.savez(out/'rei_prescribed_background.npz',zero=tables[0],plus=tables[1],minus=tables[2],
             columns=np.array(['a','b','delta_s_over_H','extra_energy_over_background','H0_elapsed_proper_time']))
    print(json.dumps(report,indent=2));raise SystemExit(0 if all(verdict.values()) else 1)
