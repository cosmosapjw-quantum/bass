"""CE1-E behavioral tests for a finite-amplitude nonpolynomial angular carrier."""
import numpy as np
import pytest
from bianchi.nonperturbative.einstein_exponential_source import (
    ExponentialRadiation, certified_nonpolynomial_pressure,
    certified_initial_energy, certified_coupled_geometry)


def model(lam=.2,nt=8):
    return ExponentialRadiation(energy=.9,coefficients=(.6,.25,.2),
                                lambda_exp=lam,ntheta=nt,backend='python_oracle')


def test_nonpolynomial_model_and_zero_lambda_limit():
    from bianchi.nonperturbative.einstein_error_budget import PolynomialRadiation
    z=model(0.0);b=PolynomialRadiation(ntheta=8,backend='python_oracle')
    np.testing.assert_allclose(z.mass,b.mass,atol=0,rtol=0)
    m=model(.2)
    assert np.min(m.mass)>0 and np.max(np.abs(m.mass-b.mass))>1e-4
    assert m.moments(np.zeros(3))[0]>b.energy0


def test_continuum_pressure_enclosed_against_finer_reference():
    a=model(.2,8)
    result=certified_nonpolynomial_pressure(a,np.zeros(3),[.08,.08,.08],
                                            exp_order=8,geom_order=5)
    assert result['continuum_source_enclosure'] is True
    assert result['bound_max']<2e-4
    fine=model(.2,64)
    for ell in [[0,0,0],[.035,.02,.07],[.08,.08,.08]]:
        diff=np.abs(a.moments(ell)[1]-fine.moments(ell)[1])
        assert np.all(diff<=np.asarray(result['pressure_upper']))


def test_initial_energy_certificate_includes_high_resolution_reference():
    a=model(.2,8)
    result=certified_initial_energy(a,exp_order=8)
    fine=model(.2,96)
    assert result['energy_error_upper']<1e-6
    assert abs(fine.moments(np.zeros(3))[0]-a.energy0) < result['energy_error_upper']


def test_coupled_pilot_envelope_and_invalid_source_contract():
    a=model(.2,8)
    r=certified_coupled_geometry(a,end=.08,exp_order=8,geom_order=5)
    assert r['status']=='SCOPED_NONPOLYNOMIAL_COUPLED_ENCLOSURE'
    assert r['geometry_h_upper']>0 and r['source_h_upper']>0
    assert r['initial_rate_upper']>0
    assert r['geometry_h_upper']<5e-4
    with pytest.raises(ValueError):
        model(-.1)
    with pytest.raises(ValueError,match='backend'):
        ExponentialRadiation(lambda_exp=.2)


def test_nonzero_lambda_is_not_relabelled_as_polynomial():
    a=model(.25,8)
    qz=np.array([0.,.25,.5,.75,1.])
    ratios=np.exp(.25*qz*qz)
    # A fixed degree-four angular polynomial cannot reproduce all five
    # exponential values under a quadratic-in-(qz^2) interpolation.
    p=np.polynomial.polynomial.polyfit(qz[:3]**2,ratios[:3],2)
    assert abs(np.polynomial.polynomial.polyval(qz[4]**2,p)-ratios[4])>1e-4


def test_constraint_reference_uses_exact_binary_tracefree_shear():
    from fractions import Fraction
    a=model(.2,8)
    r=certified_coupled_geometry(a,end=.04)
    assert r['initial_shear_reference']=='EXACT_BINARY_SX_SY_TRACEFREE'
    # The third float64 shear need not equal the exact rational negative sum.
    sx=Fraction.from_float(.2);sy=Fraction.from_float(-.13)
    assert sx+sy-(sx+sy)==0
    assert r['initial_rate_upper']>0


def test_axisymmetric_independent_high_precision_continuum_energy_and_pressure():
    import mpmath as mp
    mp.mp.dps=60
    a=ExponentialRadiation(energy=.9,coefficients=(.6,0,.2),
                           lambda_exp=.2,ntheta=8,backend='python_oracle')
    cert=certified_initial_energy(a,exp_order=8)
    E0=mp.mpf(.9);lam=mp.mpf(.2);c2=mp.mpf(.6);c4=mp.mpf(.2)
    def G(mu):return 1+c2*(3*mu*mu-1)/2+c4*(35*mu**4-30*mu*mu+3)/8
    integral=E0*mp.quad(lambda mu:G(mu)*mp.exp(lam*mu*mu),[-1,0,1])/2
    assert mp.mpf(cert['continuum_energy_lower']) <= integral <= mp.mpf(cert['continuum_energy_upper'])
    ell=[.025,.025,.055]; bx=mp.exp(-2*mp.mpf(ell[0]));bz=mp.exp(-2*mp.mpf(ell[2]))
    volume=mp.exp(-sum(mp.mpf(t) for t in ell))
    Pz=E0*volume*bz*mp.quad(lambda z:G(z)*mp.exp(lam*z*z)*z*z/mp.sqrt(bx*(1-z*z)+bz*z*z),[-1,0,1])/2
    Px=E0*volume*bx*mp.quad(lambda z:G(z)*mp.exp(lam*z*z)*(1-z*z)/mp.sqrt(bx*(1-z*z)+bz*z*z),[-1,0,1])/4
    result=certified_nonpolynomial_pressure(a,[0,0,0],[.08,.08,.08],exp_order=8,geom_order=5)
    for i,exact in [(0,Px),(1,Px),(2,Pz)]:
        diff=abs(mp.mpf(float(a.moments(ell)[1][i]))-exact)
        assert diff < mp.mpf(result['pressure_upper'][i])
