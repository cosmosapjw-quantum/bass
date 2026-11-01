"""CI-replayed, source-bound scientific assertions for CE1AS one FLRW reference."""
from pathlib import Path
import csv,json,math,sys,os
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'source'))
import ce1as_flrw_reference as a

def read(name):
    with (ROOT/'data'/name).open(newline='') as f:return list(csv.DictReader(f))

def result():return json.loads((ROOT/'data'/'CE1AS_RESULTS.json').read_text())

def test_sourced_isotropic_energy_and_original_replay_labels():
    r=result()
    assert abs(r['initial_rho_Bianchi']-.9)<2e-12
    assert 0.0308<r['initial_shear_constraint']<.031
    assert r['input_identity_mode']==('REPLAYED_SAME_OWNER_SEMANTIC_CI' if os.environ.get('BASS_CE1AS_CI_REPLAY')=='1' else 'BYTE_LOCKED_S2')
    assert r['source_sixcell_sha256']==a.ORIGINAL_SIX_CELL_SHA
    assert r['new_original_sixcell_Bianchi_IVPs']==0
    assert r['reused_original_Bianchi_IVPs']==9
    assert r['new_physically_distinct_FLRW_Einstein_Vlasov_IVPs']==1
    assert not r['reference_fully_same_phase_space_source']

def test_standalone_isotropic_radiation_einstein_ivp():
    r=result()
    assert r['flrw_ivp_max_scale_relative']<2e-11
    assert r['flrw_ivp_max_rhoa4_relative']<2e-11
    assert r['flrw_ivp_max_friedmann_abs']<2e-12
    h=read('CE1AS_FLRW_HISTORY.csv');assert len(h)==401
    rho0=r['initial_rho_Bianchi'];H0=r['flrw_initial_H']
    for row in h[::40]:
        u=float(row['u']);rho=float(row['rho_flrw']);aa=float(row['a_flrw'])
        assert abs(aa**2-(1+2*H0*u))<3e-11
        assert abs(rho*aa**4-rho0)<3e-11

def test_replayed_original_Bianchi_fixed_z_observables():
    rows=read('CE1AS_BIANCHI_VS_FLRW.csv')
    assert len(rows)==5562
    assert len(read('CE1AS_SHELL_SOURCE_SKY_SUMMARY.csv'))==54
    assert len(read('CE1AS_FLRW_SHELLS.csv'))==6
    assert set(int(row['GL']) for row in rows)==set(a.ORDERS)
    assert set(float(row['eps']) for row in rows)==set(a.EPS)
    assert set(float(row['z']) for row in rows)==set(a.SHELLS)
    for row in rows:
        da=float(row['D_A_Bianchi']);fr=float(row['D_A_FLRW_E0_matched'])
        assert da>0 and fr>0
        assert abs(da/fr-1-float(row['fractional_DA_difference']))<2e-15

def test_one_FLRW_distance_every_direction_and_epsilon():
    refs={}
    for r in read('CE1AS_BIANCHI_VS_FLRW.csv'):
        z=float(r['z']);da=float(r['D_A_FLRW_E0_matched'])
        if z in refs:assert abs(da-refs[z])<2e-14
        refs[z]=da
    assert len(refs)==6
    Hobs=result()['flrw_observer_H']
    for z in refs:assert abs(refs[z]-z/(Hobs*(1+z)**2))<1e-14

def test_actual_gl24_axes_and_changed_reference():
    rows=read('CE1AS_BIANCHI_VS_FLRW.csv')
    d={r['direction']:r for r in rows if r['GL']=='24' and r['eps']=='0.0' and r['z']=='0.02' and r['direction'] in ('x','y','z')}
    assert len(d)==3
    assert -.267<float(d['x']['fractional_DA_difference'])<-.264
    assert .272<float(d['y']['fractional_DA_difference'])<.275
    assert .115<float(d['z']['fractional_DA_difference'])<.118
    assert -.016<float(d['x']['proxy_fractional_error_to_FLRW'])<-.013
    assert abs(float(d['x']['D_A_Bianchi'])-.028044169626674734)<2e-11

def test_claim_ceiling():
    r=result()
    assert r['BASS_upper_scoped_source_mapped']=='9/15'
    assert r['new_completed_upper_physics_nodes']==0
    assert r['CE1']=='PARTIAL' and r['OB1']=='PARTIAL'
    assert not r['physically_measured_cosmological_data']
    assert not r['merge_ready'] and not r['production_ready'] and not r['auto_next']
