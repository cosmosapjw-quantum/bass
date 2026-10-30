"""CE1-AF bounded source-locked physics and adversarial validation, same-context review."""
from pathlib import Path
import csv,math,json,sys,hashlib
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import shear_work_physics as p

ROOT=p.ROOT

@pytest.mark.parametrize('gl',[6,8,16,64])
def test_original_six_cells(gl):
    assert p.frozen_source_identity()==p.SOURCE_SHA
    rays,mass=p.make_cell_rays(gl)
    assert len(mass)==6*gl*gl
    assert np.all(mass>0)
    assert abs(mass.sum()-.9)<4e-13

@pytest.mark.parametrize('gl',[6,8])
def test_immutable_frozen_history_hash(gl):
    f=ROOT/'input'/f'GL{gl}_DOP853_coupled_41epochs.csv'
    assert hashlib.sha256(f.read_bytes()).hexdigest()==p.HISTORY_SHA[gl]

@pytest.mark.parametrize('gl',[6,8])
def test_moment_rank4_exact_identities(gl):
    rays,mass=p.make_cell_rays(gl)
    E,P,R,*_=p.sky_moments(rays*rays,mass,np.array([.017,.024,.05]))
    assert abs(P.sum()-E)<3e-15
    np.testing.assert_allclose(R,R.T,atol=4e-16,rtol=0)
    np.testing.assert_allclose(R.sum(axis=1),P,atol=8e-16,rtol=0)
    assert abs(R.sum()-E)<5e-15
    assert np.min(np.linalg.eigvalsh(R))>-1e-14

@pytest.mark.parametrize('gl',[6,8])
def test_quadrupole_independent_spherical_harmonic(gl):
    rays,mass=p.make_cell_rays(gl)
    ell=np.array([.018,.039,.051]);Q=(rays*rays*np.exp(-2*ell)).sum(axis=1);r=np.sqrt(Q)
    n=rays*np.exp(-ell)/r[:,None]
    vol=np.exp(-ell.sum());U=vol*mass*r;E=U.sum()
    y20=np.sqrt(5/(16*np.pi))*(3*n[:,2]**2-1)
    y22=np.sqrt(15/(32*np.pi))*(n[:,0]**2-n[:,1]**2)
    a20=4*np.pi*(U@y20)/E;a22=4*np.pi*(U@y22)/E
    _,_,_,a20_impl,a22_impl,*_=p.sky_moments(rays*rays,mass,ell)
    np.testing.assert_allclose([a20_impl,a22_impl],[a20,a22],atol=6e-14,rtol=0)

@pytest.mark.parametrize('gl',[6,8])
def test_instantaneous_transport_fd(gl):
    rays,mass=p.make_cell_rays(gl);ray2=rays*rays
    ell=np.array([.018,.037,.064]);h=np.array([.72,.36,.47]);eps=1e-6
    E,P,R,*_=p.sky_moments(ray2,mass,ell)
    Eplus,Pplus,*_=p.sky_moments(ray2,mass,ell+eps*h)
    Eminus,Pminus,*_=p.sky_moments(ray2,mass,ell-eps*h)
    Edot=-(sum(h)*E+h@P)
    Pdot=-(sum(h)+2*h)*P+R@h
    assert abs((Eplus-Eminus)/(2*eps)-Edot)<5e-10
    np.testing.assert_allclose((Pplus-Pminus)/(2*eps),Pdot,atol=4e-10,rtol=0)

@pytest.mark.parametrize('gl',[6,8])
def test_quadrupole_shear_work_algebra(gl):
    rays,mass=p.make_cell_rays(gl)
    z=p.physical_snapshot(rays*rays,mass,.02,np.array([.01,.03,.02,.7,.42,.48]))
    assert abs(z['quadrupole_to_work_gap'])<2e-14
    assert abs(z['conservation_residual'])<2e-14
    assert abs(z['shear_cancellation_residual'])<2e-14
    sigma_prime=-3*z['H']*z['sigma']+z['Pi']
    np.testing.assert_allclose(z['sigma_prime'],sigma_prime,atol=3e-16,rtol=0)
    assert abs(z['shear_energy_prime']+6*z['H']*z['shear_energy']-z['shear_work'])<3e-16

@pytest.mark.parametrize('gl',[6,8])
def test_isotropic_hubble_kinematic_limit(gl):
    rays,mass=p.make_cell_rays(gl);ray2=rays*rays
    ell=np.array([.015,.025,.035]);h=np.array([.3,.3,.3]);E,P,R,*_=p.sky_moments(ray2,mass,ell)
    z=p.physical_snapshot(ray2,mass,.01,np.r_[ell,h])
    assert abs(z['shear_work'])<1e-20
    np.testing.assert_allclose(z['dP_du'],-4*.3*P,atol=2e-14,rtol=0)
    assert abs(z['dE_du']+4*.3*E)<2e-14


def load_rows():
    with (ROOT/'data/CE1AF_PHYSICAL_TIMELINE.csv').open(newline='') as f:
        rows=list(csv.DictReader(f))
    return rows


def test_all_four_original_coupled_physics():
    reports=json.loads((ROOT/'data/CE1AF_SHEAR_QUADRUPOLE_RESULTS.json').read_text())
    rows=load_rows()
    assert len(rows)==1604 and len(rows[0])==43
    assert reports['source_sha256']==p.SOURCE_SHA
    assert reports['upstream_dag']=='9/15' and reports['ce1']=='PARTIAL'
    assert reports['new_upper_nodes']==0 and not reports['production_ready'] and not reports['merge_ready']
    for n in (6,8,16,64):
        s=reports['orders'][str(n)]
        assert s['epochs']==401 and s['nfev']==47
        assert s['max_abs_constraint']<3e-11
        assert s['max_abs_energy_law_residual']<4e-14
        assert s['max_abs_fourth_moment_trace']<4e-14
        assert s['max_abs_quadrupole_work_gap']<1e-13
        assert s['max_abs_log_balance_residual']<1e-11
        assert s['C2_final']<s['C2_initial']
        assert s['integrated_work_over_E']>0
        assert s['volume_compensated_E_ratio']<1
        assert s['shear_work_sign_changes']==0
        assert abs(math.log(s['volume_compensated_E_ratio'])+s['integrated_work_over_E'])<1e-11
        assert len([r for r in rows if int(r['GL'])==n])==401


def test_numerical_GL_convergence_not_rigorous_source_bound():
    d=json.loads((ROOT/'data/CE1AF_SHEAR_QUADRUPOLE_RESULTS.json').read_text())['orders']
    for k in ['C2_final','integrated_work_over_E','volume_compensated_E_ratio','E_end','shear_work_final']:
        assert abs(d['16'][k]-d['64'][k])<4e-12
    # This numerical convergence does not certify an exact-continuum six-cell angular integral.


def test_negative_tamper_control(monkeypatch):
    monkeypatch.setattr(p,'frozen_source_identity',lambda:'invalid-sha')
    with pytest.raises(RuntimeError,match='source identity drift'):
        p.evolve(6,41)


def test_explicit_not_cmb_or_production():
    r=json.loads((ROOT/'data/CE1AF_SHEAR_QUADRUPOLE_RESULTS.json').read_text())
    assert 'nonthermal' in r['scientific_problem']
    assert r['auto_next'] is False


def test_exact_positive_initial_continuum_source_work():
    from certify_initial_shear_work import compute
    v=compute()
    from fractions import Fraction as F
    assert F(v['strict_lower_exact'])>F(7,1000)
    assert v['full_horizon_positive_work_NOT_certified']
    assert F(v['E0_exact'])>F(89,100)
    assert F(v['D_exact'])>0
    assert v['source_sha256']==p.SOURCE_SHA


def test_true_continuum_initial_vs_GL_limit():
    from certify_initial_shear_work import compute
    v=compute()
    from fractions import Fraction as F
    initial=F(v['A_exact'])+F(v['B_exact'])*2*math.sqrt(2)/math.pi*F(v['D_exact'])
    d=json.loads((ROOT/'data/CE1AF_SHEAR_QUADRUPOLE_RESULTS.json').read_text())['orders']
    for n in (6,8,16,64):
        assert abs(d[str(n)]['shear_work_initial']-initial)<6e-12


def test_physical_shear_energy_transfer_data():
    rows=load_rows()
    for n in (6,8,16,64):
        s=[r for r in rows if int(r['GL'])==n]
        for r in (s[0],s[len(s)//2],s[-1]):
            sig=np.array([float(r[f'sigma{i}']) for i in (1,2,3)])
            pi=np.array([float(r[f'Pi{i}']) for i in (1,2,3)])
            H=float(np.mean([float(r[f'h{i}']) for i in (1,2,3)]))
            work=float(r['shear_work'])
            sigma_prime=np.array([float(r[f'sigma{i}_prime']) for i in (1,2,3)])
            np.testing.assert_allclose(sigma_prime,-3*H*sig+pi,atol=7e-14,rtol=0)
            assert abs(float(r['shear_energy_prime'])+6*H*float(r['shear_energy'])-work)<3e-14


def test_frozen_gl_physics_snapshot_scientific_identity_not_byte_identity():
    import gzip
    archive=ROOT/'data'/'CE1AF_PHYSICAL_TIMELINE.csv.gz'
    assert hashlib.sha256(archive.read_bytes()).hexdigest()=='10947bc1f442e46ee11fd9d2522aa1bc5eaa806211e10d5ab492566da08fb9ca'
    with gzip.open(archive,'rt',newline='') as f:
        frozen=list(csv.DictReader(f))
    generated=load_rows()
    assert len(frozen)==len(generated)==1604
    for old,new in zip(frozen,generated):
        assert old.keys()==new.keys()
        for field in old:
            assert abs(float(old[field])-float(new[field]))<3e-12,(field,old[field],new[field])
