"""CE1AH scientific and adversarial regression tests, same-context author only."""
import csv,gzip,hashlib,json,math,sys
from pathlib import Path
import numpy as np
import pytest
from scipy.special import sph_harm_y
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ce1ah_tangent as c

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'

def readcsv(path):
    with open(path,newline='') as f:return list(csv.DictReader(f))


def test_exact_input_byte_identity_and_unmodified_parent():
    assert c.frozen_source_identity()==c.SOURCE_SHA
    assert c.SHEAR.dtype==np.dtype('<f8')
    assert abs(c.SHEAR.sum())<1e-17
    assert c.PARENT_HEAD=='4d6a5d9c391bbd5aac1a885ff72b4f33f027e28a'
    raw=(c.ORIG/'input/cellwise_gl_rust.py').read_bytes()
    assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\x00'+raw).hexdigest()=='6d254e9efc95acc1fd2079bd047d40662986d135'


@pytest.mark.parametrize('gl',[6,8])
def test_exact_pressure_jacobian_against_independent_finite_differences(gl):
    rays,mass=c.make_cell_rays(gl);ray2=rays*rays
    ell=np.array([.011,.029,.043])
    E,P,R,*_=c.moment(ray2,mass,ell)
    assert abs(sum(P)-E)<3e-14
    assert np.linalg.eigvalsh(R).min()>-2e-15
    J=c.pressure_jacobian(P,R)
    for k in range(3):
        d=np.zeros(3);d[k]=1.e-6
        _,pp,*_=c.moment(ray2,mass,ell+d)
        _,pm,*_=c.moment(ray2,mass,ell-d)
        np.testing.assert_allclose((pp-pm)/(2e-6),J[:,k],rtol=0,atol=3e-10)
    np.testing.assert_allclose(J.sum(axis=0),-E-P,atol=8e-15,rtol=0)


@pytest.mark.parametrize('gl',[6,8])
def test_real_spherical_harmonic_coefficients_scipy_and_parent_c4(gl):
    rays,mass=c.make_cell_rays(gl);ray2=rays*rays
    ell=np.array([.019,.021,.052])
    E,P,R,x,omega=c.moment(ray2,mass,ell)
    alpha,jac,C2,C4=c.normalized_harmonics_and_gradient(x,omega,E)
    unit=rays*np.exp(-ell)/np.sqrt(np.sum(ray2*np.exp(-2*ell),axis=1))[:,None]
    theta=np.arccos(np.clip(unit[:,2],-1,1));phi=np.arctan2(unit[:,1],unit[:,0])
    for i,(l,m) in enumerate([(2,0),(2,2),(4,0),(4,2),(4,4)]):
        independent=4*math.pi/E*np.sum(omega*sph_harm_y(l,m,theta,phi).real)
        assert abs(alpha[i]-independent)<6e-13,(l,m,alpha[i],independent)
    for k in range(3):
        d=np.zeros(3);d[k]=1e-6
        ap=c.normalized_harmonics_and_gradient(*_harm_inputs(ray2,mass,ell+d))[0]
        am=c.normalized_harmonics_and_gradient(*_harm_inputs(ray2,mass,ell-d))[0]
        np.testing.assert_allclose((ap-am)/(2e-6),jac[:,k],atol=2e-9,rtol=0)
    np.testing.assert_allclose(jac.sum(axis=1),0.,atol=1e-12,rtol=0)  # normalized alpha is invariant under a common spatial scale
    assert C2>0 and C4>0


def _harm_inputs(ray2,mass,ell):
    E,_,_,x,omega=c.moment(ray2,mass,ell)
    return x,omega,E


@pytest.mark.parametrize('mode',list(c.DIRECTIONS))
def test_constrained_perturbed_initial_stein_and_initial_linear_response(mode):
    rays,mass=c.make_cell_rays(6);ray2=rays*rays
    orig=c.initial_state(ray2,mass)
    t=c.tangent_initial(ray2,mass,mode)
    assert np.max(abs(t[:3]))==0
    deriv=(c.initial_state(ray2,mass,1e-5*c.DIRECTIONS[mode])-
           c.initial_state(ray2,mass,-1e-5*c.DIRECTIONS[mode]))/(2e-5)
    np.testing.assert_allclose(t,deriv,rtol=0,atol=2e-11)
    for eps in [-.001,0,.001]:
        actual=c.basic_observables(ray2,mass,c.initial_state(ray2,mass,eps*c.DIRECTIONS[mode]))
        assert abs(actual['C'])<2e-15
    z0=np.r_[orig,c.tangent_initial(ray2,mass,'A_xy'),c.tangent_initial(ray2,mass,'B_axial')]
    diff=c.rhs_full(ray2,mass,z0)
    h=orig[3:]; th=sum(h)
    assert abs((th-h)@t[3:])<3e-15


@pytest.mark.parametrize('gl',[6,8])
def test_full_variational_rhs_not_free_geometry(gl):
    rays,mass=c.make_cell_rays(gl);ray2=rays*rays
    y=np.array([.018,.023,.046,.62,.44,.51]);direction=np.array([.2,-.1,.3,-.07,.12,.02])
    z=np.r_[y,direction,np.zeros(6)]
    ana=c.rhs_full(ray2,mass,z)[6:12]
    eps=1e-6
    fd=(c.rhs_baseline(ray2,mass,y+eps*direction)-c.rhs_baseline(ray2,mass,y-eps*direction))/(2*eps)
    np.testing.assert_allclose(ana,fd,atol=2e-9,rtol=0)


def test_new_files_have_physical_rows_not_only_analytic_curve():
    d=json.loads((DATA/'CE1AH_PHYSICAL_RESPONSE_RESULTS.json').read_text())
    assert d['source_sha256']==c.SOURCE_SHA
    assert d['original_parent_head']==c.PARENT_HEAD
    assert d['baseline_rows']==1203 and d['tangent_rows']==2406 and d['perturbed_rows']==3208
    for name,count,columns in [('CE1AH_BASELINE_PHYSICAL.csv',1203,c.BASE_FIELDS),
           ('CE1AH_TANGENT_PHYSICAL.csv',2406,c.TAN_FIELDS),
           ('CE1AH_FINITE_PERTURBED_PHYSICAL.csv',3208,c.FD_FIELDS)]:
        a=readcsv(DATA/name)
        assert len(a)==count and list(a[0])==columns
        assert all(math.isfinite(float(x)) for row in a for x in row.values() if x not in c.DIRECTIONS)
    assert d['upper_DAG']=='9/15' and d['CE1']=='PARTIAL' and d['new_upper_node']==0
    assert not d['production_ready'] and not d['merge_ready'] and not d['auto_next']


@pytest.mark.parametrize('gl',[6,8,16])
def test_parent_six_cell_physical_histories_numerically_matched(gl):
    orig=c.ORIG/'data/CE1AF_PHYSICAL_TIMELINE.csv.gz'
    with gzip.open(orig,'rt',newline='') as f:ref=[r for r in csv.DictReader(f) if int(r['GL'])==gl]
    b=[r for r in readcsv(DATA/'CE1AH_BASELINE_PHYSICAL.csv') if int(r['GL'])==gl]
    assert len(ref)==len(b)==401
    for old,new in zip(ref,b):
        for pa,ch in [('E','E'),('C2_fractional','C2'),('shear_work','W'),('hamiltonian_constraint','constraint')]:
            assert abs(float(old[pa])-float(new[ch]))<3e-12,(gl,pa,old[pa],new[ch])
    with gzip.open(c.ORIG/'input/CE1AE_PARENT_C4_DENSE.csv.gz','rt',newline='') as f:
        parent=[r for r in csv.DictReader(f) if int(r['GL'])==gl]
    assert len(parent)==401
    for old,new in zip(parent,b):
        assert abs(float(old['C4_fractional'])-float(new['C4']))<6e-12


@pytest.mark.parametrize('gl',[6,8,16])
def test_exact_geometry_and_angular_response_invariants(gl):
    d=json.loads((DATA/'CE1AH_PHYSICAL_RESPONSE_RESULTS.json').read_text())['details'][str(gl)]
    assert d['baseline_constraint_max']<3e-11
    assert d['tangent_constraint_max']<1e-10
    assert d['response_energy_balance_max']<3e-11
    if gl in (6,8):assert d['original_41point_max_state_difference']<5e-13
    for name in c.DIRECTIONS:
        at=d['response_endpoint'][name]
        assert abs(at['dconstraint'])<1e-10
        assert abs(at['dC4'])>1e-5
        assert math.isfinite(at['denergy_ratio'])
    if gl in (6,8):
        assert d['fd_rows']==1604
        assert max(d['fd_max_abs_errors'].values())<3e-8
    else: assert d['fd_rows']==0


def test_gl6_gl8_gl16_response_cross_quadrature_comparison():
    d=json.loads((DATA/'CE1AH_PHYSICAL_RESPONSE_RESULTS.json').read_text())['details']
    for mode in c.DIRECTIONS:
        for key in ['dW','dq','dC2','dC4','dE','denergy_ratio']:
            assert abs(d['6']['response_endpoint'][mode][key]-d['8']['response_endpoint'][mode][key])<2e-8
            assert abs(d['8']['response_endpoint'][mode][key]-d['16']['response_endpoint'][mode][key])<2e-8


def test_source_tamper_not_mistaken_for_accepted_original(monkeypatch):
    monkeypatch.setattr(c,'frozen_source_identity',lambda:'source-drift')
    with pytest.raises(RuntimeError,match='identity changed'):
        c.produce(6,41,with_fd=False)


def test_initial_work_response_anisotropic_not_pure_thermal():
    baseline=[r for r in readcsv(DATA/'CE1AH_BASELINE_PHYSICAL.csv') if int(r['GL'])==8]
    tan=[r for r in readcsv(DATA/'CE1AH_TANGENT_PHYSICAL.csv') if int(r['GL'])==8]
    assert float(baseline[0]['W'])>.007
    assert all(float(r['W'])>0 for r in baseline)
    for name,d in c.DIRECTIONS.items():
        initial=next(r for r in tan if r['mode']==name)
        assert abs(float(initial['dE']))<2e-15
        assert abs(float(initial['dC2']))<2e-15
        assert abs(float(initial['dC4']))<2e-15
        assert abs(float(initial['d_cumulative_q']))<2e-15
        assert abs(float(initial['dW']))>0.01
