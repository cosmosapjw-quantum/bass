"""Actual package/PolQState integration, not a replay of science campaigns."""
from __future__ import annotations
import json
import subprocess
import sys
import numpy as np
import pytest
from bianchi.backend_policy import BackendPolicy, BackendPolicyError
from bianchi.nonperturbative import load_kernel, normal_time_collision_step
from bianchi.q.coupled import QState
from bianchi.q.polstate import PolQState

ORACLE = BackendPolicy.PYTHON_ORACLE


def real_state():
    """Initialize real QState storage on an oracle grid, without claiming Rust."""
    pd = load_kernel('polarized_dictionary', backend=ORACLE)
    tc = load_kernel('tilted_collision', backend=ORACLE)
    grid = pd.Grid(10, 20)
    # Choose mapped electron quadrature; it exactly integrates low rest moments.
    _, nodes, invD = tc.boost_map(grid.n, [-0.3, 0.2, -0.1])
    weights = grid.w / invD**2
    X = pd.synthesize(grid, {('I',0,0):2*np.sqrt(4*np.pi),
                            ('I',2,0):.15, ('E',2,1):.03,
                            ('B',3,1):.02, ('V',1,0):.02})
    op = tc.TiltedThomson(nodes, weights, [0.3,-0.2,0.1])
    J = np.einsum('nki,nkl,nlj->nij',op.S,X,op.S)/op.D[:,None,None]**4
    I = np.trace(J, axis1=1, axis2=2)
    st = QState.__new__(QState)
    st.sph = None; st.qhat = nodes.copy(); st.w_com = weights.copy()
    st.S6 = np.zeros(6); st.N6 = np.zeros(6); st.A3 = np.zeros(3)
    st.lnH = 0.; st.M = np.eye(3); st.lG = np.log(I)
    st.rot = np.zeros(3); st.residual = False; st.jac_min = 1e-4
    ps=PolQState.__new__(PolQState)
    ps.st=st; ps.Jhat=J/I[:,None,None]
    return ps, J, op


def test_package_root_lazy_and_no_global_aliases():
    code = "import sys,bianchi,bianchi.nonperturbative; assert not any(x in sys.modules for x in ('scipy','sympy','jax','tilted_collision','source_memory'))"
    subprocess.run([sys.executable, '-c', code], check=True)


def test_explicit_oracle_policy_and_unknown_kernel():
    with pytest.raises(BackendPolicyError): load_kernel('tilted_history')
    with pytest.raises(BackendPolicyError): load_kernel('tilted_history',backend='rust_required')
    with pytest.raises(KeyError): load_kernel('../../bad',backend=ORACLE)


def test_all_catalog_modules_import_without_path_mutation():
    from bianchi.nonperturbative import catalog
    before = list(sys.path)
    for name in catalog():
        m = load_kernel(name,backend=ORACLE)
        assert m.__name__.startswith('bianchi.nonperturbative._core.')
    assert sys.path == before


def test_packaged_p8_is_the_real_bass_module():
    from bianchi.q import polarization
    assert load_kernel('source_memory',backend=ORACLE).P8 is polarization
    assert load_kernel('spatial_transport',backend=ORACLE).P8 is polarization


def test_new_polqstate_path_matches_packaged_source_and_invariant():
    ps,J,op = real_state()
    history = load_kernel('tilted_history',backend=ORACLE)
    ref = history.VolterraHistory(op,J,1.3,.3,32).carrier(.3)
    before_M=ps.st.M.copy(); before_w=ps.st.w_com.copy()
    returned = ps.collide_normal_time(.3,1.3,beta=[.3,-.2,.1],panels=32,backend=ORACLE)
    actual=np.exp(ps.st.lG)[:,None,None]*ps.Jhat
    assert returned is ps
    assert np.max(abs(actual-ref))<2e-11
    assert abs(history.invariant(op,actual)-history.invariant(op,J))<2e-9
    assert np.array_equal(before_M,ps.st.M)
    assert np.array_equal(before_w,ps.st.w_com)


def test_wrapper_matches_direct_and_has_no_hidden_rate_factor():
    _,J,op = real_state()
    out=normal_time_collision_step(op.n,op.w,J,dt_s=.2,rest_rate_s=1.3,
                                  beta=[.3,-.2,.1],panels=64,backend=ORACLE)
    ref=load_kernel('tilted_history',backend=ORACLE).DirectHistory(op,J,1.3,.2).carrier(.2)
    assert np.max(abs(out-ref))<2e-9


@pytest.mark.parametrize('dt,rate',[(0.,1.3),(.3,0.)])
def test_exact_zero_step_identity(dt,rate):
    ps,_,_=real_state(); a=ps.st.lG.copy(); b=ps.Jhat.copy()
    ps.collide_normal_time(dt,rate,beta=[.3,-.2,.1],panels=8,backend=ORACLE)
    assert np.array_equal(a,ps.st.lG) and np.array_equal(b,ps.Jhat)


@pytest.mark.parametrize('bad',[{'dt_s':-.1},{'rest_rate_s':-1},
                                {'beta':[1,0,0]},{'panels':True},
                                {'backend':'rust_required'}])
def test_failed_call_is_atomic(bad):
    ps,_,_=real_state(); a=ps.st.lG.copy(); b=ps.Jhat.copy()
    kw=dict(dt_s=.1,rest_rate_s=1.3,beta=[.3,-.2,.1],panels=8,backend=ORACLE)
    kw.update(bad)
    with pytest.raises((ValueError,BackendPolicyError)):
        ps.collide_normal_time(**kw)
    assert np.array_equal(a,ps.st.lG) and np.array_equal(b,ps.Jhat)


def test_rejects_nonphysical_shape_without_clipping():
    ps,_,_=real_state(); ps.Jhat[0]+=np.outer(ps.st.qhat[0],ps.st.qhat[0])
    a=ps.st.lG.copy(); b=ps.Jhat.copy()
    with pytest.raises(ValueError): ps.collide_normal_time(.1,1.,beta=[0,0,0],panels=8,backend=ORACLE)
    assert np.array_equal(a,ps.st.lG) and np.array_equal(b,ps.Jhat)


def test_log_scaling_and_all_vacuum():
    ps,_,_=real_state(); ps.st.lG+=900
    ps.collide_normal_time(.1,1.,beta=[.3,-.2,.1],panels=16,backend=ORACLE)
    assert np.isfinite(ps.st.lG).all()
    ps.st.lG[:]=-np.inf; before=ps.Jhat.copy()
    ps.collide_normal_time(.1,1.,beta=[.3,-.2,.1],panels=16,backend=ORACLE)
    assert np.isneginf(ps.st.lG).all() and np.array_equal(ps.Jhat,before)


def test_packaged_projector_and_collision_correlation():
    sp=load_kernel('spatial_projection',backend=ORACLE)
    P=sp.SpatialProjector(np.ones(4))
    J=np.arange(12,dtype=float).reshape(4,3)
    bg,fl=P.split(J)
    assert np.max(abs(P.mean(fl)))<1e-14
    assert np.max(abs(bg+fl-J))<1e-14

@pytest.mark.parametrize('which',['carrier','beta','directions','weights'])
def test_public_step_rejects_complex_storage(which):
    _,J,op=real_state()
    values=dict(n=op.n,weights=op.w,carrier=J,beta=np.array([.3,-.2,.1]))
    key={'directions':'n'}.get(which,which)
    values[key]=values[key].astype(complex)+1j*1e-3
    with pytest.raises(ValueError,match='real'):
        normal_time_collision_step(**values,dt_s=.1,rest_rate_s=1.,panels=8,backend=ORACLE)


def test_nonidentity_q_geometry_bridge():
    from bianchi.nonperturbative.polq_bridge import oracle_q_geometry
    ps,_,_=real_state()
    ps.st.M=np.diag([.8,1.1,1.3])
    n,lw=oracle_q_geometry(ps)
    P=np.eye(3)-np.einsum('ni,nj->nij',n,n)
    ps.Jhat=P/2
    J=np.exp(ps.st.lG)[:,None,None]*ps.Jhat
    ref=normal_time_collision_step(n,np.exp(lw),J,dt_s=.1,rest_rate_s=.7,
                                  beta=[.2,0,0],panels=16,backend=ORACLE)
    ps.collide_normal_time(.1,.7,beta=[.2,0,0],panels=16,backend=ORACLE)
    assert np.max(abs(ref-np.exp(ps.st.lG)[:,None,None]*ps.Jhat))<2e-11
