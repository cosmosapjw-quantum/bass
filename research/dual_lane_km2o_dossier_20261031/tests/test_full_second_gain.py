"""KM2O original source-backed full second Thomson gain acceptance and regressions."""
from __future__ import annotations
import hashlib, json, os
from pathlib import Path
import numpy as np
import pytest
from research.dual_lane_km2o_dossier_20261031 import replay_second_gain_full as m

@pytest.fixture(scope='module')
def data():
    p=m.HERE/'KM2O_FULL_SCIENCE.json'
    assert p.exists(), 'real owner-source scientific data must be generated before tests'
    return json.loads(p.read_text())

def test_source_owners_immutable():
    for grid in (12,16):
        z=m.source_ledger(grid)
        assert len(z)==41
        assert all(x['nu']>0 for x in z)

def test_negative_tampered_owner_ledger_refused(monkeypatch):
    monkeypatch.setitem(m.LEDGER_SOURCE_SHA,12,'0'*64)
    with pytest.raises(ArithmeticError,match='SHA256 mismatch'):
        m.source_ledger(12)

def test_unallowable_grid_or_observer_time_refused():
    with pytest.raises(ValueError):m.physics_at(14,8,[])
    with pytest.raises(ValueError):m.physics_at(12,7,[])

def test_real_10_physics_epochs_and_12000_bins(data):
    assert data['actual_physics_epoch_count']==10
    assert data['actual_frequency_rows']==12000
    assert data['new_owner_Einstein_IVPs']==0
    assert {(r['grid'],r['k']) for r in data['measurements']}=={(f'GL{q}',k) for q in (12,16) for k in m.OBS_EPOCHS}

def test_original_real_source_first_one_restored(data):
    for rec in data['measurements']:
        assert rec['rho_first_photon']>0
        assert rec['original_source_ledger_SHA256']==m.LEDGER_SOURCE_SHA[int(rec['grid'][2:])]
        assert rec['second_gain_energy_rate']>0
        assert rec['first_scatter_loss_rate']>0

def test_original_full_10_epoch_numerical_crosswalk(data):
    import csv
    with m.OLD_CSV.open(newline='') as f:older=list(csv.DictReader(f))
    assert len(older)==10
    for rec,prior in zip(data['measurements'],older):
        assert rec['grid']==prior['grid']
        assert abs(rec['second_gain_energy_rate']/float(prior['second_gain_energy_rate'])-1)<3e-12
        assert abs(rec['second_gain_linear_polarization_mean']-float(prior['second_gain_linear_polarization_mean']))<1e-11
        assert abs(rec['normal_frequency_centroid']-float(prior['normal_frequency_centroid']))<1e-11

def test_thomson_original_tensor_gain_and_rest_energy(data):
    for rec in data['measurements']:
        assert rec['rest_frame_elastic_rel_gap']<5e-6
        assert rec['original_P8_gain_parity_relative']<2e-8
        assert rec['frequency_first_remap_error']<3e-11
        assert rec['frequency_second_remap_error']<3e-11

def test_positive_screen_and_physical_polarization(data):
    for rec in data['measurements']:
        assert 0<=rec['second_gain_linear_polarization_mean']<=1
        assert 0<=rec['second_gain_linear_polarization_max']<=1+1e-12
        assert rec['frequency_sigma_logbin']>0

def test_true_observed_frequency_bins_and_sum(data):
    for rec in data['measurements']:
        a=np.asarray(rec['spectral_bins'])
        assert len(a)==1200 and np.all(a>=-1e-22)
        assert abs(a.sum()/rec['second_gain_energy_rate']-1)<3e-12

def test_exact_original_final_frozen_screen_replay():
    for g in (12,16):
        src=m.source_ledger(g)
        from research.dual_lane_km2n_20261031.once_scattered import propagate_one_scatter
        with __import__('tempfile').TemporaryDirectory() as t:
            p=Path(t)/'test.npz';r=propagate_one_scatter(src,40,save_field=p)
            owner=m.ROOT/f'research/dual_lane_km2n_20261031/results/KM2N_ONCE_POL_SCREEN_GL{g}_U40.npz'
            with np.load(p) as x,np.load(owner) as y:
                assert np.array_equal(x['screen_spectral_first_one'],y['screen_spectral_first_one'])

def test_saved_second_gain_polarized_factors_exact(data):
    for rec in data['measurements']:
        if rec['k']!=40:continue
        p=m.HERE/rec['source_factorized_npz']
        assert p.exists()
        assert hashlib.sha256(p.read_bytes()).hexdigest()==rec['source_factorized_SHA256']
        with np.load(p) as z:
            assert z['second_gain_pol_screen'].shape==(int(rec['grid'][2:])**2*2,1200,2,2)
            assert z['electron_rest_source_Me'].shape==(1200,3,3)

def test_DAG_scope_gate_does_not_promote(data):
    assert data['UPPER_DAG']=='9/15' and data['KM2']=='PARTIAL'
    assert data['new_upper_completed']==0
    assert data['no_second_field_time_propagation']
    assert not data['production_ready'] and not data['merge_ready'] and not data['auto_next']
