"""CE1-AB source-locked physical contract and independent finite-difference checks."""
import sys,json,csv,hashlib,math
from pathlib import Path
import numpy as np
import pytest
ROOT=Path(__file__).resolve().parents[1]
ORIGINAL=(ROOT/'ce1aa_input') if (ROOT/'ce1aa_input').is_dir() else ROOT.parent/'ce1aa_20261030'
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ORIGINAL/'source'))
from replay_dop853 import run,angular,init,rhs,SOURCE,ORIGINAL
from mpfr_defect import physical_source_jac,pstate,defect,IV,abs_up,rays
from mpfr_angular_transport import jac_alpha
from mpfr192_sky import constants
from cellwise_gl_rust import make_cell_rays,frozen_source_identity

def read(n,name):return json.loads((ROOT/'results'/f'GL{n}_{name}').read_text())

@pytest.mark.parametrize('n',[6,8])
def test_identity_and_replay(n):
    assert SOURCE==frozen_source_identity()
    a=read(n,'REPLAY_DOP853_DENSE.json')
    assert a['replay_target_status']=='EXACT'
    assert a['num_binary64_equal_saved_states']==246
    assert a['n_steps']==3 and a['nfev']==47
    assert a['source_sha256']==SOURCE
    raw=ORIGINAL/'input'/f'GL{n}_DOP853_coupled_41epochs.csv'
    assert hashlib.sha256(raw.read_bytes()).hexdigest()==a['frozen_reference_csv_sha256']
    assert len(a['steps'])==3
    for step in a['steps']:
        a0=pstate(step,IV.val(0))[0]
        assert max(abs_up(z-IV.val(float.fromhex(x))) for z,x in zip(a0,step['y_old_hex'])) < 1e-50

@pytest.mark.parametrize('n',[6,8])
def test_pressure_jacobian_independent_numpy_fd(n):
    ray,mass=make_cell_rays(n); ell=np.array([.018,.044,.061])
    P,J=physical_source_jac([IV.val(float(x)) for x in ell],rays(n))
    Jv=np.array([[float(sum(v.pair())/2) for v in row] for row in J])
    for j in range(3):
        ep=ell.copy();em=ell.copy();ep[j]+=1e-6;em[j]-=1e-6
        fd=(angular(ray,mass,ep)[1]-angular(ray,mass,em)[1])/(2e-6)
        assert np.max(abs(fd-Jv[:,j]))<2e-9
    assert max(abs(P[i].pair()[0]-angular(ray,mass,ell)[1][i]) for i in range(3))<3e-14

def independently_normalized_alpha(ray,mass,ell):
    q=ray**2*np.exp(-2*np.asarray(ell)[None,:]);Q=q.sum(axis=1)
    x=q/Q[:,None];xx,yy,zz=x.T;w=mass*np.sqrt(Q)
    polynomials=np.array([35*zz**2-30*zz+3,(xx-yy)*(7*zz-1),xx**2-6*xx*yy+yy**2])
    cof=np.array([3/(16*np.sqrt(np.pi)),(3/8)*np.sqrt(5/(2*np.pi)),(3/16)*np.sqrt(35/(2*np.pi))])
    return (4*np.pi)*cof*(polynomials@w)/w.sum()

@pytest.mark.parametrize('n',[6,8])
def test_angular_jacobian_independent_fd(n):
    ray,mass=make_cell_rays(n); ell=np.array([.019,.026,.054]);eps=2e-6
    alpha,D=jac_alpha([IV.val(float(x)) for x in ell],rays(n),constants())
    a=np.array([sum(z.pair())/2 for z in alpha]);a0=independently_normalized_alpha(ray,mass,ell)
    np.testing.assert_allclose(a,a0,atol=3e-14,rtol=0)
    for j in range(3):
        ee=np.zeros(3);ee[j]=eps
        fd=(independently_normalized_alpha(ray,mass,ell+ee)-independently_normalized_alpha(ray,mass,ell-ee))/(2*eps)
        der=np.array([sum(z.pair())/2 for z in [row[j] for row in D]])
        np.testing.assert_allclose(der,fd,atol=5e-10,rtol=0)

@pytest.mark.parametrize('n',[6,8])
def test_actual_scientific_claim_and_bounds(n):
    a=read(n,'MPFR192_DOP853_DEFECT_N32.json')
    b=read(n,'CE1AB_RANK2_N32.json')
    assert a['mpfr_precision_bits']==192 and a['subdivisions_per_step']==32
    assert len(a['steps'])==3 and a['tube_self_consistent']
    assert a['Grönwall_global_infty_error_upper']<1e-5
    assert a['saved_states_vs_exact_dense_max_upper']<1e-14
    assert b['rank_at_least_two'] and b['Gram_weyl_delta_upper']<2e-5
    from fractions import Fraction
    assert Fraction(b['strict_original_continuum_rank2_lambda2_lower_margin_floor_decimal'])>0
    assert b['upper_DAG']=='9/15' and b['CE1']=='PARTIAL'
    assert not b['production_ready'] and not b['merge_ready'] and not b['auto_next']
    with (ROOT/'results'/f'GL{n}_ANGULAR_JACOBIAN_41.csv').open() as fd: rows=list(csv.DictReader(fd))
    assert len(rows)==41

@pytest.mark.parametrize('n',[6,8])
def test_original_binary_cell_source_tamper_guard(n,monkeypatch):
    import mpfr192_sky
    monkeypatch.setattr(mpfr192_sky,'SOURCE_SHA','0'*64)
    with pytest.raises(AssertionError):mpfr192_sky.rays(n)

@pytest.mark.parametrize('n',[6,8])
def test_defect_at_saved_midpoint_is_bounded(n):
    a=read(n,'REPLAY_DOP853_DENSE.json')
    b=read(n,'MPFR192_DOP853_DEFECT_N32.json')
    pp=rays(n)
    for i,step in enumerate(a['steps']):
        r,_=defect(step,pp,IV.val(.5),False)
        assert max(map(abs_up,r))<=max(b['steps'][i]['defect_sup_abs_upper'])
