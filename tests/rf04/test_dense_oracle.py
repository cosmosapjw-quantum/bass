"""Independent, offline RF04 reference tests; never a native PASS certificate."""
from pathlib import Path
import importlib.util
import numpy as np
import pytest

PATH = Path(__file__).with_name('rf04_dense_oracle.py')

def oracle():
    assert PATH.is_file(), 'RF04 independent dense oracle has not been implemented'
    spec = importlib.util.spec_from_file_location('rf04_dense_oracle', PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_quadrature_resolves_full_quadrupole_and_fourth_moments():
    o = oracle(); e, w = o.lebedev26()
    x, y, z = e.T
    b = np.column_stack([x*x-y*y, 2*z*z-x*x-y*y, x*y, x*z, y*z])
    assert np.linalg.matrix_rank(b, tol=1e-13) == 5
    d = np.eye(3)
    exact = 4*np.pi/15*(np.einsum('ij,kl->ijkl', d,d)+np.einsum('ik,jl->ijkl', d,d)+np.einsum('il,jk->ijkl',d,d))
    np.testing.assert_allclose(np.einsum('n,ni,nj,nk,nl->ijkl',w,e,e,e,e), exact, rtol=0,atol=4e-15)


def test_scalar_thomson_quadrupole_is_not_silently_lost():
    o = oracle(); e, w = o.lebedev26(); c = o.scalar_collision(e,w,0.0)
    for xy in [(0,1),(0,2),(1,2)]:
        y=e[:,xy[0]]*e[:,xy[1]]
        np.testing.assert_allclose(c@y, -0.9*y, rtol=0,atol=5e-15)
    np.testing.assert_allclose(c@np.ones(len(w)),0,rtol=0,atol=5e-15)


def test_paired_grid_conserves_independent_rate_dual_not_naive_weights():
    o = oracle(); er, wr = o.lebedev26(); e,w = o.paired_grid(er,wr,0.23)
    c=o.scalar_collision(e,w,0.23); p,r,left=o.projector(e,w,0.23)
    np.testing.assert_allclose(c@r,0,rtol=0,atol=1e-13)
    np.testing.assert_allclose(left@c,0,rtol=0,atol=1e-13)
    assert np.max(np.abs(w@c))>1e-4
    np.testing.assert_allclose(p@p,p,rtol=0,atol=5e-15)


def test_kato_complex_step_derivative_matches_finite_difference():
    o=oracle();e,w=o.lebedev26();v=0.17;vd=-0.031;h=2e-5
    p=o.projector(e,w,v)[0]
    dp=(o.projector(e,w,v+h)[0]-o.projector(e,w,v-h)[0])/(2*h)
    np.testing.assert_allclose(o.kato(e,w,v,vd),vd*(dp@p-p@dp),rtol=3e-8,atol=3e-11)


def test_phi1_has_correct_singular_zero_limit():
    o=oracle();b=np.array([0.7,-0.2,1.1])
    np.testing.assert_array_equal(o.phi1_action(np.zeros((3,3)),b,0),b)
    np.testing.assert_allclose(o.phi1_action(np.zeros((3,3)),b,0.23),b,rtol=0,atol=2e-15)


def test_scalar_aem2_converges_to_A_plus_C_without_extra_K():
    o=oracle();e,w=o.lebedev26();state=np.array([0.25,0.05,1/30,0.8,0.12]);g=1.3
    y=1+0.1*e[:,0]*e[:,1];T=0.03
    c=o.scalar_collision(e,w,state[4]);a=o.scalar_transport(e,state)
    from scipy.linalg import expm
    exact=expm(T*(a+0.31*c))@y
    errs=[]
    for count in [4,8,16]:
        h=T/count;z=y.copy()
        for _ in range(count): z=o.scalar_step(e,w,state,state,state,0.31,h,g,1.0,z)
        errs.append(np.linalg.norm(z-exact))
    assert errs[0]/errs[1]>3.5 and errs[1]/errs[2]>3.5, errs
    k=o.kato(e,w,state[4],o.tilt_rate(state,g))
    assert np.linalg.norm(expm(T*(a+0.31*c+k))@y-exact)>1e-5


def test_rank9_rest_collision_and_complex_hermitian_psd():
    o=oracle();e,w=o.lebedev26();p=np.eye(3)[None]-e[:,:,None]*e[:,None,:]
    j=o.pack9(0.5*p)
    np.testing.assert_allclose(o.polarized_rest_action(e,w,j),0,rtol=0,atol=3e-15)
    s=o.polarized_fixture(e)
    assert np.min(o.normalized_metrics(e,s)['minimum_eigenvalue'])>0
    # An independent Hermitian eigensolver, not the real nonsymmetric encoding.
    assert np.max(np.abs(o.unpack9(s)-np.swapaxes(o.unpack9(s),1,2)))>1e-3


@pytest.mark.parametrize('scale',[1e-120,1.0,1e120])
def test_realizability_and_transversality_are_scale_free(scale):
    o=oracle();e,w=o.lebedev26();s=o.polarized_fixture(e)
    base=o.normalized_metrics(e,s);got=o.normalized_metrics(e,scale*s)
    for k in base: np.testing.assert_allclose(got[k],base[k],rtol=0,atol=8e-15)
    bad=s.copy();bad[0,:]=0;bad[0,1]=1;bad[0,2]=-0.2
    assert np.min(o.normalized_metrics(e,bad*scale)['minimum_eigenvalue'])<0


def test_rest_polarized_action_detects_real_operator_coefficient_mutation():
    o=oracle();e,w=o.lebedev26();s=o.polarized_fixture(e)
    good=o.polarized_rest_action(e,w,s)
    mutant=o.polarized_rest_action(e,w,s,gain_multiplier=1.01)
    assert np.max(np.abs(good-mutant))>1e-3


def test_stage_samples_and_opacity_act_on_numerical_output():
    o=oracle();e,w=o.lebedev26();q1,mid,q3,op,h=o.background_fixture()
    y=1+0.18*e[:,0]*e[:,1]-0.13*e[:,1]*e[:,2]
    good=o.scalar_history(y,e,w,q1,mid,q3,op,h,1.3,1.0)
    no_c=o.scalar_history(y,e,w,q1,mid,q3,np.zeros_like(op),h,1.3,1.0)
    collapsed=o.scalar_history(y,e,w,q1,q1,q1,op,h,1.3,1.0)
    assert np.max(np.abs(good[-1]-no_c[-1]))>1e-6
    assert np.max(np.abs(good[-1]-collapsed[-1]))>1e-6
    np.testing.assert_array_equal(good[0],y)


@pytest.mark.parametrize('bad',['nan','axis','weights','shape','velocity'])
def test_bad_oracle_inputs_fail_explicitly(bad):
    o=oracle();e,w=o.lebedev26();axis=1;v=0.1
    if bad=='nan': e[0,0]=np.nan
    if bad=='axis': axis=3
    if bad=='weights': w[0]=-1
    if bad=='shape': e=e[:-1]
    if bad=='velocity': v=1.0
    with pytest.raises(ValueError): o.scalar_collision(e,w,v,axis=axis)


def test_raw_diagnostics_do_not_fabricate_zero_null_or_transport_drift():
    o=oracle();e,w=o.lebedev26();q1,mid,q3,op,h=o.background_fixture()
    y=1+.18*e[:,0]*e[:,1]-.13*e[:,1]*e[:,2]
    history=o.scalar_history(y,e,w,q1,mid,q3,op,h,1.3,1.)
    d=o.scalar_diagnostics(e,w,mid,history)
    assert np.max(d['right_kernel_residual'])>1e-8
    assert np.min(d['left_invariant_drift'])>1e-4
    np.testing.assert_array_equal(d['positivity_margin'],history.min(axis=1))


def test_history_rejects_scalar_initial_value_instead_of_broadcasting():
    o=oracle();e,w=o.lebedev26();q1,mid,q3,op,h=o.background_fixture()
    with pytest.raises(ValueError,match='finite node vector'):
        o.scalar_history(1.,e,w,q1,mid,q3,op,h,1.3,1.)
