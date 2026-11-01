"""Source-bound physical checks for independent massless FLRW reference, not full sky validation."""
import csv, math, sys
from pathlib import Path
import numpy as np
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'source'))
import ce1as_flrw_reference as mod

def records(file):
    with (ROOT/'data'/file).open(newline='') as f:return list(csv.DictReader(f))

def test_provenance_inputs_exact_bytes():
    assert mod.sha(mod.INPUT)==mod.CE1AP_SHA
    assert mod.sha(mod.BEAMS)==mod.CE1AR_BEAMS_SHA

def test_exact_source_owned_bianchi_initial_constraint():
    rho,initial,gap=mod.original_constraint()
    assert len(initial)==12 and abs(rho-.9)<2e-13 and gap<5e-12
    h=np.asarray(next(r['H'] for r in initial if r['GL']==24 and r['eps']==0))
    assert h[0] > h[2] > h[1] > 0
    s=h.mean()
    assert 3*s*s-rho>0
    assert abs(3*s*s-rho-.5*np.sum((h-s)**2))<2e-12

def test_isotropic_massless_distribution_stress_is_perfect_radiation():
    # Angularly isotropized positive massless Vlasov matter, arbitrary positive radial shell.
    mu,w=np.polynomial.legendre.leggauss(24)
    ph=2*np.pi*np.arange(48)/48
    direction=np.stack((np.sqrt(1-mu[:,None]**2)*np.cos(ph),
                        np.sqrt(1-mu[:,None]**2)*np.sin(ph),
                        np.broadcast_to(mu[:,None],(len(mu),len(ph)))),axis=-1)
    # normalized angular average 1/(4pi) integral dmu dphi
    m=np.einsum('i,ijp,ijq->pq',w,direction,direction)/(2*len(ph))
    np.testing.assert_allclose(m,np.eye(3)/3,atol=4e-15,rtol=0)
    assert abs(np.trace(m)-1)<4e-15 # finite 24x48 angular sum roundoff, not physics acceptance

def test_independent_Einstein_Vlasov_ivp_radiation_conservation():
    rho,*_=mod.original_constraint()
    ivp=mod.flrw_ivp(rho)
    assert ivp['max_scale_relative']<2e-12
    assert ivp['max_rhoa4_relative']<2e-12
    assert ivp['max_friedmann_absolute']<2e-15
    for t,a,rr,H,p,rad,cons in ivp['history'][::40]:
        assert abs(3*H*H-rr)<2e-15
        assert abs(p-rr/3)<1e-14
        assert abs(rad-rho)<2e-12
        assert abs(a*a-(1+2*ivp['H0']*t))<2e-12

def test_rad_friedmann_closed_form_and_independent_null_integral():
    rho,*_=mod.original_constraint();ivp=mod.flrw_ivp(rho)
    assert ivp['H_observer']>0
    for z in mod.SHELLS:
        d=mod.shell(rho,ivp,z)
        expected=z/(ivp['H_observer']*(1+z)**2)
        assert abs(d['D_A']-expected)<2e-16
        assert d['ray_abs_gap']<1e-11
        assert d['redshift_abs_gap']<2e-12
        assert 0<d['u_emit']<mod.UO

def test_horizon_and_unphysical_energy_controls():
    rho,*_=mod.original_constraint();ivp=mod.flrw_ivp(rho)
    with pytest.raises(ValueError):mod.shell(rho,ivp,1.,uo=mod.UO)
    with pytest.raises(ValueError):mod.shell(rho,ivp,-.01)
    with pytest.raises(ValueError):mod.flrw_ivp(0.)

def test_outputs_actual_original_sky_and_counts():
    out=mod.OUTPUT
    assert len(records('CE1AS_FLRW_HISTORY.csv'))==401
    assert len(records('CE1AS_FLRW_SHELLS.csv'))==6
    assert len(records('CE1AS_BIANCHI_VS_FLRW.csv'))==5562
    assert len(records('CE1AS_SHELL_SOURCE_SKY_SUMMARY.csv'))==54
    import json
    o=json.loads((out/'CE1AS_RESULTS.json').read_text())
    assert o['new_physically_distinct_FLRW_Einstein_Vlasov_IVPs']==1
    assert o['new_original_sixcell_Bianchi_IVPs']==0
    assert not o['reference_fully_same_phase_space_source']
    assert o['new_completed_upper_physics_nodes']==0
    assert o['BASS_upper_scoped_source_mapped']=='9/15'

def test_energy_matched_flrw_reference_is_common_to_all_models():
    sky=records('CE1AS_BIANCHI_VS_FLRW.csv')
    ref={}
    for r in sky:
        z=float(r['z']);da=float(r['D_A_FLRW_E0_matched'])
        assert r['model_source_multipoles_identical']=='False'
        assert r['comparison_kind']=='ENERGY_MONOPOLE_MATCHED_ISOTROPIZED_COLLISIONLESS_VLASOV'
        if z not in ref:ref[z]=da
        else:assert abs(da-ref[z])<1e-15
    assert len(ref)==6

def test_source_owned_directionality_at_fixed_z():
    sky=records('CE1AS_BIANCHI_VS_FLRW.csv')
    axes={r['direction']:r for r in sky if r['GL']=='24' and r['eps']=='0.0' and r['z']=='0.02' and r['direction'] in ('x','y','z')}
    assert set(axes)==set('xyz')
    fractions={d:float(r['fractional_DA_difference']) for d,r in axes.items()}
    assert fractions['x'] < -.25
    assert fractions['y'] > .25
    assert fractions['z'] > .1
    for d,r in axes.items():
        assert abs((float(r['D_A_Bianchi'])/float(r['D_A_FLRW_E0_matched'])-1)-fractions[d])<2e-16
        assert -.02<float(r['proxy_fractional_error_to_FLRW'])<-.01

def test_adversarial_fake_ancestor_source_rejected(tmp_path):
    p=tmp_path/'ancestor.csv'
    source=mod.INPUT.read_bytes()
    p.write_bytes(source.replace(b'0.7570457790882175',b'0.7570457790882176',1))
    assert mod.sha(p)!=mod.CE1AP_SHA
    with pytest.raises(ArithmeticError,match='SHA'):mod.original_constraint(p)

def test_adversarial_fake_parent_beam_source_rejected(tmp_path):
    p=tmp_path/'beams.csv'
    original=mod.BEAMS.read_bytes()
    p.write_bytes(original.replace(b'0.0072041870017074',b'0.0072041870017073',1))
    assert mod.sha(p)!=mod.CE1AR_BEAMS_SHA
    with pytest.raises(ArithmeticError,match='SHA'):mod.run(mod.INPUT,p,tmp_path/'new')

def test_exact_source_energy_control_does_not_equal_mean_expansion():
    rho,initial,_=mod.original_constraint()
    h=np.array(next(r['H'] for r in initial if r['GL']==24 and r['eps']==0))
    assert abs(h.mean()-math.sqrt(rho/3))>.009
    assert abs(h.mean()**2-rho/3)>.01
