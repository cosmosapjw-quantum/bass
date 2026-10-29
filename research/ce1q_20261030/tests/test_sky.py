"""CE1-Q: tests of scientific sky projections, not general EB/CMB acceptance."""
import csv,hashlib,json,math,os,struct,subprocess,sys
from pathlib import Path
import numpy as np
import pytest
from scipy.special import sph_harm_y

HERE=Path(__file__).resolve().parents[1]
DATA=Path(os.environ.get('BASS_CE1Q_DATA',str(HERE/'data')))
PARENT=Path(os.environ.get('BASS_CE1Q_PARENT',str(HERE/'parent_data')))
EXEC=Path(os.environ.get('BASS_CE1Q_RUST',str(HERE/'sky_native')))
sys.path.insert(0,str(HERE))
from produce_sky import sha,harmonics,independently_reintegrated,make_maps,source,gl_source,bits

def read(name):
    with (DATA/name).open(newline='') as f:
        return [{k:float(v) for k,v in row.items()} for row in csv.DictReader(f)]

def res():return json.loads((DATA/'results.json').read_text())

def test_source_contract_exact_binary64():
    assert res()['input_binary64_source_sha256']=='022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035'
    assert res()['source_git_blob']=='fdeb83a65cd424786ba6bb8ddadbcb2b2e2d45bf'

def test_original_ref8_byte_lock():
    s=source()([0,.5,1],[0,.25,.75,1],[[.1,.25,.05],[.2,.15,.15]],refinement=8,backend='python_oracle')
    assert sha(s.n.astype('<f8').tobytes())=='9d46624cdb747a5760eda945d5effeb17f0619ade2b7198ee1700903123455ba'
    assert sha(s.mass.astype('<f8').tobytes())=='c421e8148af743ea44bbb565f32a44090e18299e0e0b15f20eee37fb0a232211'

def test_actual_six_datasets_and_proper_time_grid():
    for c in ('stored_ref1','stored_ref4','stored_ref8','stored_ref16','gl24','gl40'):
        z=read(f'{c}_alm.csv')
        assert len(z)==41
        assert all(abs(z[i]['u']-i*.002)<1e-14 for i in range(41))
        assert set(['E','P1','P2','P3','a_4_4_re','a_4_-4_im']).issubset(z[0])

def test_native_rust_selftest_and_bass_module():
    cp=subprocess.run([str(EXEC),'--selftest'],capture_output=True,text=True,timeout=10)
    assert cp.returncode==0,cp.stderr
    assert 'BASS_CE1Q_NATIVE_RUST_SELFTEST_PASS' in cp.stdout
    assert (HERE/'../../_rustcore/src/kinetic/comoving.rs').exists()

def test_frozen_moment_closure_all_246_records():
    maxdiff=0.0
    for c in res()['channels']:
        z=read(f'{c}_alm.csv')
        for row in z:
            e=row['E']; p=[row[f'P{i}'] for i in (1,2,3)];a=harmonics(row)
            maxdiff=max(maxdiff,abs(sum(p)-e),abs(a[(0,0)]*math.sqrt(4*math.pi)-e))
            assert abs(a[(2,0)]-math.sqrt(5/(16*math.pi))*(3*p[2]-e))<1e-11
            assert abs(a[(2,2)]-math.sqrt(15/(32*math.pi))*(p[0]-p[1]))<1e-11
    assert maxdiff<2e-11

def test_saved_ce1p_histories_not_replaced():
    for k in res()['channels']:
        f=('stored_ref'+k.removeprefix('stored_ref')+'_history.csv') if k.startswith('stored_ref') else ('continuum_GL'+k.removeprefix('gl')+'_history.csv')
        with (PARENT/'data'/f).open(newline='') as fd:prev=list(csv.DictReader(fd))
        new=read(k+'_alm.csv')
        assert len(prev)==len(new)
        for old,row in zip(prev,new):
            for j in ['E','P1','P2','P3']:
                assert abs(float(old[j])-row[j])<5e-11

def test_reflection_parity_and_real_field():
    for k in res()['channels']:
        for row in read(k+'_alm.csv'):
            a=harmonics(row)
            for (l,m),v in a.items():
                if l%2 or m%2: assert abs(v)<5e-13
                if m>0:assert abs(a[(l,-m)]-(-1)**m*v.conjugate())<1e-14

def test_independent_scipy_complex_harmonics():
    g=gl_source(24)
    # The saved CE1-P trajectory provides ell, not the new harmonic CSV.
    with (PARENT/'data/continuum_GL24_history.csv').open(newline='') as f:
        end=list(csv.DictReader(f))[-1]
    independent=independently_reintegrated(g.n,g.mass,[float(end[f'ell{i}']) for i in (1,2,3)])
    rust=harmonics(read('gl24_alm.csv')[-1]);assert max(abs(rust[k]-v) for k,v in independent.items())<5e-11

def test_gl24_gl40_stability_but_no_continuum_certificate():
    x=harmonics(read('gl24_alm.csv')[-1]);y=harmonics(read('gl40_alm.csv')[-1]);
    assert max(abs(x[k]-y[k]) for k in x)<2e-10
    assert res()['scope']=='model-generated collisionless angular energy, NOT observational CMB'

def test_aliasing_16_pole_and_source_refinement():
    s=res()['channels'];ratio=lambda k:s[k]['final_C4']/s['gl40']['final_C4']
    assert ratio('stored_ref1')>30
    assert 1<ratio('stored_ref16')<1.05
    assert ratio('stored_ref1')>ratio('stored_ref4')>ratio('stored_ref8')>ratio('stored_ref16')
    # Initial six-cell source is already anisotropic, even at M=I.
    assert abs(s['gl40']['first_a20_real'])>0.02

def test_positive_continuum_only_sky_map():
    z=np.load(DATA/'gl40_observer_sky_map.npz')
    assert z['energy_per_solid_angle'].shape==(160,320)
    assert float(z['energy_per_solid_angle'].min())>0
    assert float(z['energy_per_solid_angle'].max())>float(z['energy_per_solid_angle'].min())

def test_native_rejects_out_of_contract_inputs():
    def payload(m):
        return '1 1 4\n'+' '.join([bits(m),bits(1.0),bits(0.0),bits(0.0)])+'\n'+' '.join(bits(x) for x in (0.0,0.0,0.0,0.0))+'\n'
    for mass in (-0.9,0.0,float('nan')):
        cp=subprocess.run([str(EXEC)],input=payload(mass),capture_output=True,text=True,timeout=10)
        assert cp.returncode!=0 and 'BASS_CE1Q_REJECT' in cp.stderr
    msg=payload(0.9).replace('1 1 4','1 1 5',1)
    cp=subprocess.run([str(EXEC)],input=msg,capture_output=True,text=True,timeout=10)
    assert cp.returncode!=0

