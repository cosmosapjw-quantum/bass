"""CE1-D behavioral tests, written before new implementation."""
from fractions import Fraction
import numpy as np
import pytest
from scipy.integrate import solve_ivp
from numpy.polynomial.legendre import leggauss
from bianchi.nonperturbative.einstein_error_budget import PolynomialRadiation
from bianchi.nonperturbative.einstein_input_enclosure import (
    enclose_physical_inputs, combine_nominal_path_budget,
    angular_absolute_basis_bounds,
)


def base():
    return PolynomialRadiation(ntheta=12,backend='python_oracle')


def test_basis_means_have_proved_rational_upper_bounds():
    cap=angular_absolute_basis_bounds()
    z,w=leggauss(512)
    p2=(3*z*z-1)/2
    p4=(35*z**4-30*z*z+3)/8
    assert sum(w*abs(p2))/2 < float(cap['P2'])
    assert sum(w*abs(p4))/2 < float(cap['P4'])
    assert 4/(3*np.pi) < float(cap['T'])
    assert cap=={'P2':Fraction(2,5),'T':Fraction(4,9),'P4':Fraction(1,3)}


def test_tiny_decimal_box_includes_nonexact_binary_centers():
    a=enclose_physical_inputs(base(), energy=('0.9','0'),
           coefficients=(('0.6','0'),('0.25','0'),('0.2','0')),
           shear=(('0.2','0'),('-0.13','0')), u_end='1', backend='python_oracle')
    assert a['status']=='ADMITTED_POSITIVE_EXPANDING_INPUT_BOX'
    # Decimal inputs are not identical to binary reference floats.
    assert a['eta_source_upper']>0
    assert a['initial_h_upper']>0
    assert a['input_h_upper']>0


def test_reasonable_box_is_admitted_and_large_box_rejected():
    s=base()
    a=enclose_physical_inputs(s,energy=('0.9','1e-8'),
      coefficients=(('0.6','1e-7'),('0.25','1e-7'),('0.2','1e-7')),
      shear=(('0.2','1e-8'),('-0.13','1e-8')),u_end='1',backend='python_oracle')
    assert a['eta_source_upper']<1e-6
    assert a['input_h_upper']<2e-6
    assert a['initial_h_upper']>0
    assert a['source_h_upper']>0
    assert a['positivity_margin_lower']>0
    with pytest.raises(ValueError,match='positiv'):
        enclose_physical_inputs(s,energy=('0.9','1e-8'),
        coefficients=(('0.6','4'),('0.25','4'),('0.2','4')),
        shear=(('0.2','0'),('-0.13','0')),u_end='1',backend='python_oracle')
    with pytest.raises(ValueError,match='expan'):
        enclose_physical_inputs(s,energy=('0.9','0'),
        coefficients=(('0.6','0'),('0.25','0'),('0.2','0')),
        shear=(('0.2','1'),('-0.13','1')),u_end='1',backend='python_oracle')


def test_physical_box_covers_nontrivial_nonlinear_realization():
    s=base()
    box=enclose_physical_inputs(s,energy=('0.9','1e-5'),
       coefficients=(('0.6','2e-5'),('0.25','1e-5'),('0.2','2e-5')),
       shear=(('0.2','1e-5'),('-0.13','1e-5')),u_end='1',backend='python_oracle')
    sp=PolynomialRadiation(energy=.9+8e-6, coefficients=(.6+1.5e-5,.25-9e-6,.2+1.2e-5),ntheta=24,backend='python_oracle')
    shear=(.2+8e-6,-.13-7e-6, -.07-1e-6)
    ref=solve_ivp(s.rhs,(0,1),s.initial_state(),rtol=1e-12,atol=2e-14,method='DOP853')
    alt=solve_ivp(sp.rhs,(0,1),sp.initial_state(shear),rtol=1e-12,atol=2e-14,method='DOP853')
    assert ref.success and alt.success
    difference=np.max(abs(ref.y[3:,-1]-alt.y[3:,-1]))
    assert 0<difference<box['input_h_upper']


def test_nominal_plus_input_budget_can_admit_or_reject_target_without_clipping():
    s=base()
    a=enclose_physical_inputs(s,energy=('0.9','1e-8'),
      coefficients=(('0.6','1e-7'),('0.25','1e-7'),('0.2','1e-7')),
      shear=(('0.2','1e-8'),('-0.13','1e-8')),u_end='1',backend='python_oracle')
    tiny=combine_nominal_path_budget(7.3457959948804625e-6,a,target_h='1e-5',backend='python_oracle')
    assert tiny['combined_h_upper']>=7.3457959948804625e-6
    assert tiny['status']=='SCOPED_TARGET_MET'
    big=combine_nominal_path_budget(7.3457959948804625e-6,a,target_h='1e-6',backend='python_oracle')
    assert big['status']=='SCOPED_TARGET_NOT_MET'
    with pytest.raises(ValueError,match='backend'):
        combine_nominal_path_budget(1e-6,a,target_h='1e-5')
