import numpy as np
from compiler.validation.typeii_polarized_runtime import run_validation

R = run_validation()

def test_paired_finite_v_collision_structure():
    assert max(x['paired_null'] for x in R['quadrature']) < 3e-13
    assert max(x['paired_left'] for x in R['quadrature']) < 3e-13
    # Deliberate negative control: low-order fixed-normal collocation is not silently blessed.
    g=[x for x in R['quadrature'] if x['grid']=='grid6' and x['v']==.1][0]
    assert abs(g['fixed_null']-0.009605220075000013) < 5e-14

def test_v_and_scalar_intensity_generator_gates():
    assert R['V_generated'] < 2e-14
    assert R['I_generator_reduction'] < 3e-13

def test_i_e_feedback_is_second_order_not_aliasing_claim():
    q=R['I_E_feedback_scaling']
    assert max(q['diff']) > 1e-5
    assert 1.85 < q['order'] < 2.10

def test_coherency_cone_and_screen_constraint_survive_deep_collision():
    for q in R['cone'].values():
        assert q['min_eig'] > -2e-12
        assert q['screen_leak'] < 1e-12

def test_polarized_projector_and_kato_connection_identities():
    assert R['P2'] < 3e-13
    assert R['K_comm'] < 5e-13

def test_kato_endpoint_transport_is_second_order():
    q=R['kato_endpoint']
    assert 1.95 < q['order'] < 2.05
    assert q['defect'][-1] < 5e-10

def test_rest_frame_physical_spectrum_is_rank9_thomson_spectrum():
    q=R['rest_spectrum']
    assert q['max_imag'] < 2e-12
    assert q['counts'] == {'0.0':1,'-0.3':5,'-0.5':3,'-1.0':q['dimension']-9}
    assert q['max_cluster_deviation'] < 2e-11

def test_intensity_quadrupole_sources_linear_polarization_but_isotropy_does_not():
    q=R['I_E_quadrupole']
    assert q['isotropic_collision_null'] < 3e-13
    assert q['isotropic_polarization'] < 3e-13
    assert q['quadrupole_polarization'] > 1e-3
