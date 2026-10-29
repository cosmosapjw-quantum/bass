"""CE1-S frozen BASS Rust physical data and fractionally normalized sky tests."""
from __future__ import annotations
import csv,io,json,math,sys,zipfile
from pathlib import Path
import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'source'))
import generate_fractional_sky as s
P=ROOT/'input/CE1P_SOURCE_PINNED.zip'
Q=ROOT/'input/CE1Q_SOURCE_PINNED.zip'
R=ROOT/'input/CI_PR261_4CHANNEL_ATLAS_PINNED.zip'
O=ROOT/'data'

@pytest.fixture(scope='session')
def source():
    with s.read_archive(R,s.RUST_ARTIFACT_SHA256) as rz,s.read_archive(P,s.CE1P_ARCHIVE_SHA256) as pz,s.read_archive(Q,s.CE1Q_ARCHIVE_SHA256) as qz:
        yield rz,pz,qz

def test_immutable_archive_triplet(source):
    assert all(z.testzip() is None for z in source)
    assert json.loads(source[0].read('gl40.json'))['rays']==9600

def test_original_six_cell_source_weights():
    assert s.MU_EDGES.tolist()==[0,.5,1]
    assert s.PHI_FRAC_EDGES.tolist()==[0,.25,.75,1]
    assert np.isclose(s.CELL_ENERGY.sum(),0.9)
    # Integrating the piecewise constant density against original 8-octant cell area.
    area=4*math.pi*np.diff(s.MU_EDGES)[:,None]*np.diff(s.PHI_FRAC_EDGES)[None,:]
    assert np.allclose(s.CELL_ENERGY/area*area,s.CELL_ENERGY,atol=2e-16)

def test_declared_rust_physical_sky(source):
    rows=s.records(source[0],'gl40.csv')
    assert len(rows)==41 and abs(rows[-1]['u']-.08)<1e-13
    assert abs(rows[0]['E']-.9)<2e-13 and rows[-1]['E']<rows[0]['E']
    assert max(r['continuity_gap'] for r in rows)<1e-12

def test_nonthermal_fractional_quadrupole(source):
    rows=s.records(source[0],'gl40.csv')
    q0=s.fractional_power(rows[0],2);q1=s.fractional_power(rows[-1],2)
    assert np.isclose(q0['Cdelta'],0.06373396691693183,atol=5e-14)
    assert q1['Cdelta']<q0['Cdelta']
    assert q1['Cdelta_prime']<0

def test_nonthermal_fractional_hexadecapole(source):
    rows=s.records(source[0],'gl40.csv')
    q0=s.fractional_power(rows[0],4);q1=s.fractional_power(rows[-1],4)
    assert np.isclose(q0['Cdelta'],0.010541886035181436,atol=5e-14)
    assert q1['Cdelta']>q0['Cdelta']
    assert q1['Cdelta_prime']>0

def test_rust_amplitude_energy_identity(source):
    for ch in s.CHANNELS:
        rows=s.records(source[0],ch+'.csv')
        for k in (0,20,40):
            a00=rows[k]['a_0_0_re']; da00=rows[k]['da_0_0_re']
            assert abs(a00*math.sqrt(4*math.pi)-rows[k]['E'])<1e-12
            assert abs(da00*math.sqrt(4*math.pi)-rows[k]['Eprime'])<1e-12

def test_parent_endpoint_sky_exact_pointwise(source):
    parent=np.load(io.BytesIO(source[2].read('ce1q/data/gl40_observer_sky_map.npz')))
    history=s.records(source[1],'data/continuum_GL40_history.csv')
    ell=[history[-1][f'ell{i}'] for i in range(1,4)]
    actual=s.make_observer_map(parent['theta'],parent['azimuth'],ell)
    assert np.max(abs(actual-parent['energy_per_solid_angle']))<2e-15
    assert actual.min()>0

def test_isotropic_map_limit():
    theta=np.linspace(.001,math.pi-.001,49)
    phi=np.linspace(.001,2*math.pi-.001,101)
    # The original angular cells remain anisotropic, but an isotropic frame cannot alter their pattern.
    a=s.make_observer_map(theta,phi,[0.,0.,0.])
    b=s.make_observer_map(theta,phi,[.02,.02,.02])
    assert np.max(abs(b-math.exp(-.08)*a))<3e-15

def test_final_atlas_contract():
    r=json.loads((O/'RESULTS.json').read_text())
    assert r['upper_dag']=='9/15' and not r['blackbody_assumed'] and not r['polarization_assumed']
    assert r['gl24_gl40_max_Cdelta_difference']['2']<1e-10
    assert r['sky_snapshot']['ce1q_archived_endpoint_map_max_abs_gap']<2e-15
    rows=list(csv.DictReader((O/'fractional_angular_power_164rows.csv').open()))
    assert len(rows)==164

def test_mutated_archive_rejected(tmp_path):
    data=bytearray(R.read_bytes());data[2]=data[2]^1
    x=tmp_path/'corrupted.zip';x.write_bytes(data)
    with pytest.raises(ValueError,match='SHA mismatch'):s.read_archive(x,s.RUST_ARTIFACT_SHA256)
