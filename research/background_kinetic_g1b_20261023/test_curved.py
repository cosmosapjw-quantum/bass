"""New G1B driver checks, not a replay of G1A physics tests."""
import numpy as np
import pytest
import run_curved as rc
from vendor import core as bg

@pytest.mark.parametrize('family',['V','VIII'])
def test_discrete_initial_data_close_constraints_without_density_fitting(family):
    model,z,info=rc.make_case(family,4,6)
    assert model.ns==2 and info['packets']==4*4*2*6**2+2*6**2
    assert np.max(np.abs(bg.constraints(z[:24],model.lam)))<2e-14
    assert abs(info['initial_rho_m']-1.8)>1e-9
    assert info['photon_reduction']=='exact_N_and_T_radial'
    diag=rc.diagnostics(model,z)
    assert diag['mismatch']<2e-14 and diag['observable'].shape==(52,)
    # Disturbing the independent ledger must not be mistaken for kinetic closure.
    wrong=z.copy();wrong[16]+=.01
    assert rc.diagnostics(model,wrong)['mismatch']>1e-3


def test_envelope_is_explicit_and_failure_does_not_clip_state():
    model,z,info=rc.make_case('V',4,6)
    rc.check_envelope(z)
    bad=z.copy();bad[0]=2.01
    with pytest.raises(ValueError,match='envelope'):rc.check_envelope(bad)
    assert bad[0]==2.01
    with pytest.raises(ValueError):rc.make_case('IX',4,6)


def test_history_comparison_never_divides_by_cancelling_stress():
    a=np.zeros((2,52));b=a.copy();b[0,0]=1e-10
    assert rc.compare_observables(a,b)==1e-10/(1+1e-10)
    with pytest.raises(ValueError):rc.compare_observables(a,b[:1])


def test_near_isotropic_tensor_uses_six_identical_symmetric_components():
    import symmetric_bridge as sb
    import smooth
    from vendor import kinetic as kn
    data=smooth.photon_packets('Planck',6,amplitude=.9)
    rho,f,p,pi=sb.symmetric_moments(*data)
    assert np.array_equal(pi,pi.T)
    bg._symmetric(pi,'pi',tracefree=True)
    T=kn.tensor(*data)
    np.testing.assert_allclose(pi+np.eye(3)*p,T[1:,1:],rtol=0,atol=2e-15)
    model,z,_=rc.make_case('V',4,6)
    assert np.all(np.isfinite(model.rhs(0.,z)))
