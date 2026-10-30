import csv,hashlib,json,math,sys
from fractions import Fraction
from pathlib import Path
import numpy as np
import pytest
from scipy.special import sph_harm_y
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'source'))
sys.path.insert(0,str(ROOT/'original_source'))
from initial_jet_certificate import SOURCE_EXPECT, I, moment, moment_symbol, certify,det3,PI,SQ2
from l4_kinematic_history import jets,run,make_cell_rays,HISTORY_SHA
from cellwise_gl_rust import frozen_source_identity,CELL_E,SHEAR

@pytest.mark.parametrize('n',[6,8])
def test_exact_original_source_and_history_sha(n):
    assert frozen_source_identity()==SOURCE_EXPECT
    f=ROOT/'input'/f'GL{n}_DOP853_coupled_41epochs.csv'
    assert hashlib.sha256(f.read_bytes()).hexdigest()==HISTORY_SHA[n]
    assert sum(Fraction.from_float(float(x)) for x in SHEAR)==0


def test_exact_cell_moment_zeroth_and_trace():
    expected=sum((Fraction.from_float(float(q)) for q in CELL_E.flatten()),Fraction(0))
    assert I.rat(expected).l<=moment(0,0,0).l<=moment(0,0,0).h<=I.rat(expected).h+2
    trace=sum((moment(*(int(i==j) for i in range(3))) for j in range(3)),I.z())-moment(0,0,0)
    assert trace.l<=0<=trace.h
    # Exact polynomial moment bridge: no sampled angular quadrature in this carrier.
    assert moment_symbol(0,0,0)[1:] == (0,0)


def test_certified_pi_and_sqrt2():
    assert PI.l>3*10**80 and PI.h<4*10**80
    assert SQ2.l*SQ2.l <=2*10**160 <= SQ2.h*SQ2.h
    assert PI.width()<=2


def test_positive_initial_exact_continuum_rank3_jet():
    d=certify()
    assert d['moments_evaluated']>=35 and d['moment_max_degree']==4
    assert d['strict_positive_determinant']
    assert int(d['interval_det_dyadic_lower_as_integer_times_1e_minus_80'])>0
    lo,hi=map(float,d['interval_det_of_unscaled_l4_jet'])
    assert 1.3e-5<lo<=hi<1.32e-5
    assert d['CE1']=='PARTIAL' and d['DAG_upper']=='9/15'


@pytest.mark.parametrize('n',[6,8,16,32,64])
def test_numeric_GL_original_angles_jet_agrees_with_exact_initial_interval(n):
    ray,mass=make_cell_rays(n)
    E=float(np.sum(mass*np.sqrt(np.sum(ray*ray,axis=1))))
    shear=np.array(SHEAR)
    h=np.sqrt((E+0.5*shear@shear)/3)+shear
    v=jets(ray,mass,np.zeros(3),h)
    fac=4*np.pi*np.array([3/(16*np.sqrt(np.pi)),3/8*np.sqrt(5/(2*np.pi)),3/16*np.sqrt(35/(2*np.pi))])
    fac*=np.array([1.,np.sqrt(2),np.sqrt(2)])/3
    mat=np.array([v['X'],v['dX_du'],v['d2X_du2']])/fac[None,:]
    det=float(np.linalg.det(mat))
    expected=1.3102168598091874e-5
    if n in (6,8):assert abs(det-expected)<5e-11
    else:assert abs(det-expected)<1e-13

@pytest.mark.parametrize('n',[6,8])
def test_spherical_harmonic_convention_on_original_rays(n):
    ray,mass=make_cell_rays(n)
    ell=np.array([.018,.025,.052]); h=np.array([.70,.42,.46])
    v=jets(ray,mass,ell,h)
    q=ray*np.exp(-ell);r=np.linalg.norm(q,axis=1);y=q/r[:,None]
    theta=np.arccos(y[:,2]);phi=np.arctan2(y[:,1],y[:,0])
    alpha=np.array([4*np.pi*np.dot(mass*r,sph_harm_y(4,m,theta,phi).real)/np.sum(mass*r) for m in (0,2,4)])
    np.testing.assert_allclose(v['alpha'],alpha,rtol=0,atol=2e-14)

@pytest.mark.parametrize('n',[6,8])
def test_independent_time_derivative_fd(n):
    ray,mass=make_cell_rays(n)
    ell=np.array([.018,.025,.052]);h=np.array([.70,.42,.46]);v=jets(ray,mass,ell,h)
    a=np.asarray(v['hprime']); step=2e-4
    fplus=jets(ray,mass,ell+step*h+0.5*step**2*a,h+step*a)
    fminus=jets(ray,mass,ell-step*h+0.5*step**2*a,h-step*a)
    x0=np.array(v['X']);fp=(np.array(fplus['X'])-np.array(fminus['X']))/(2*step)
    fpp=(np.array(fplus['X'])+np.array(fminus['X'])-2*x0)/step**2
    np.testing.assert_allclose(fp,v['dX_du'],rtol=0,atol=7e-8)
    np.testing.assert_allclose(fpp,v['d2X_du2'],rtol=0,atol=1e-7)

@pytest.mark.parametrize('n',[6,8])
def test_new_41_epoch_1681_pair_physics_and_energy_normalization(n):
    d=json.loads((ROOT/'data'/f'GL{n}_L4_TIMEJET_SUMMARY.json').read_text())
    with (ROOT/'data'/f'GL{n}_ORIGINAL_L4_TIMEJET_41.csv').open() as f:rows=list(csv.DictReader(f))
    with (ROOT/'data'/f'GL{n}_ORIGINAL_L4_K4_TIME_DERIV_1681.csv').open() as f:pairs=list(csv.DictReader(f))
    with (ROOT/'input'/f'GL{n}_DOP853_coupled_41epochs.csv').open() as f:old=list(csv.DictReader(f))
    assert len(rows)==len(old)==41 and len(pairs)==1681
    assert d['sampled_Gram_third_eigenvalue_status']=='NUMERICAL_ONLY_NOT_CONTINUUM_CERTIFIED'
    assert d['sampled_Gram_eigenvalues_numeric'][2]>0
    assert d['max_K4_symmetry_gap']<1e-15
    for k in [0,10,20,40]:
        r,source=rows[k],old[k]
        E=float(r['E']);Ce=float(source['C4']); Cf=float(r['C4']);Cpf=float(r['C4prime']);Ep=float(source['Eprime'])
        predicted=(E/(4*math.pi))**2 * Cf
        predictedprime=(E/(4*math.pi))**2*(Cpf+2*Ep/E*Cf)
        assert abs(predicted-Ce)<5e-16
        assert abs(predictedprime-float(source['C4prime']))<5e-15
    assert float(rows[-1]['C4'])>float(rows[0]['C4'])
    assert float(old[-1]['C4'])<float(old[0]['C4'])


def test_negative_control_invert_jet_orientation():
    v=I.rat(1)
    assert det3([[v,0,0],[0,v,0],[0,0,v]]).l>0
    assert det3([[-v,0,0],[0,v,0],[0,0,v]]).h<0
