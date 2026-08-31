import numpy as np
import pytest
from scipy.linalg import expm
from conftest import candidate

def state():return np.array([[.7,.2+.1j],[.2-.1j,.3]],complex)

def test_remap_checks_weighted_conservation_not_just_rows():
    b=candidate('bass')
    with pytest.raises(ValueError,match='conserv'):b.RemapPlan([[1,0],[.5,.5]],[1,1],[1,1])

def test_positive_common_screen_remap_preserves_trace_and_purity_domain():
    b=candidate('bass');R=np.array([[.75,.25],[.25,.75]]);u=np.tile(np.eye(2,dtype=complex),(2,2,1,1));rot=np.array([[0,-1],[1,0]],complex);u[0,1]=rot;u[1,0]=rot
    p=b.RemapPlan(R,[1,1],[1,1],u);source=np.stack([state(),.3*state().conj()]);old=source.copy();out=p.apply(source)
    assert np.linalg.eigvalsh(out).min()>-1e-14
    assert abs(np.trace(out,axis1=-2,axis2=-1).sum()-np.trace(source,axis1=-2,axis2=-1).sum())<1e-14
    np.testing.assert_array_equal(source,old);assert len(p.content_sha256)==64

@pytest.mark.parametrize('scale',[1e-120,1.,1e120])
def test_psd_guard_is_scale_normalized(scale):
    b=candidate('bass');p=b.RemapPlan([[1]],[1],[1]);out=p.apply(np.array([state()*scale]))
    np.testing.assert_allclose(out/scale,[state()],rtol=2e-15,atol=0)
    with pytest.raises(ValueError,match='positive'):p.apply(np.array([np.diag([1.,-.01])*scale]))

@pytest.mark.parametrize('what',['negative','nan','row','unitary'])
def test_remap_invalid_data_fail_explicitly(what):
    b=candidate('bass');q=np.eye(2);u=None
    if what=='negative':q=np.array([[1.1,-.1],[-.1,1.1]])
    if what=='nan':q[0,0]=np.nan
    if what=='row':q*=2
    if what=='unitary':u=np.tile(np.eye(2)*2,(2,2,1,1))
    with pytest.raises(ValueError):b.RemapPlan(q,[1,1],[1,1],u)

def test_full_generator_uses_correct_noncommuting_physics_without_extra_kato():
    b=candidate('bass');j=state();h=.31;om=.7;g=1.3;t=np.trace(j).real
    x=2*j[0,1].real;y=-2*j[0,1].imag;z=(j[0,0]-j[1,1]).real
    v=expm(h*np.array([[-g,0,om],[0,-g,0],[-om,0,0]]))@np.array([x,y,z])
    expected=np.array([[(t+v[2])/2,(v[0]-1j*v[1])/2],[(v[0]+1j*v[1])/2,(t-v[2])/2]])
    np.testing.assert_allclose(b.coherency_step(j,h,om,g),expected,rtol=5e-13,atol=5e-14)
    np.testing.assert_array_equal(b.coherency_step(j,0,om,g),j)

def test_split_fixed_rate_order_is_not_mislabeled_uniform_stiff_accuracy():
    b=candidate('bass');T=1.5;ref=b.coherency_step(state(),T,.7,1.3);errs=[]
    for n in (8,16,32,64):
        j=state()
        for _ in range(n):j=b.coherency_step(j,T/n,.7,1.3,method='strang_reference')
        errs.append(np.linalg.norm(j-ref))
    assert min(np.log2(np.array(errs[:-1])/errs[1:]))>1.98
    assert b.METHOD_CLAIMS['strang_reference']['uniform_stiff_order2'] is False

def test_bisection_counts_actual_split_nodes_not_depth():
    b=candidate('bass');f=lambda x:-4*x
    out=b.midpoint_panels(np.array([1.]),1.,f,iterations=8,atol=1e-7,max_depth=8)
    assert out.stats.splits>0 and out.stats.leaves==1+out.stats.splits
    assert out.stats.splits>=out.stats.max_depth and out.stats.max_depth<=8
    def plain(y,h,d):
        z=y.copy()
        for _ in range(8):
            new=y+h*f((y+z)/2)
            if np.max(abs(new-z))<=1e-7:return new
            z=new
        if d==8:raise ArithmeticError('depth')
        return plain(plain(y,h/2,d+1),h/2,d+1)
    np.testing.assert_array_equal(out.value,plain(np.array([1.]),1.,0))

def test_midpoint_failure_returns_no_fabricated_success_count():
    b=candidate('bass');x=np.array([1.]);old=x.tobytes()
    with pytest.raises(ArithmeticError):b.midpoint_panels(x,1.,lambda y:4*y,iterations=1,max_depth=0)
    assert x.tobytes()==old

@pytest.mark.parametrize('rate',[0.,1.3,1.4,100.,1e4,1e6,1e8])
def test_bloch_generator_preserves_trace_without_posthoc_renormalization(rate):
    import mpmath as mp
    b=candidate('bass');j=state();mp.mp.dps=85
    A=mp.matrix([[-mp.mpf(rate),mp.mpf(.7)],[-mp.mpf(.7),0]])
    v=mp.expm(mp.mpf(1.5)*A)*mp.matrix([mp.mpf(.4),mp.mpf(float((j[0,0]-j[1,1]).real))])
    off=(float(v[0])+1j*.2*np.exp(-1.5*rate))/2
    expected=np.array([[(1+float(v[1]))/2,off],[off.conjugate(),(1-float(v[1]))/2]])
    out=b.coherency_step(j,1.5,.7,rate,method='bloch_generator')
    np.testing.assert_allclose(out,expected,rtol=4e-13,atol=4e-13)
    assert abs(np.trace(out)-1)<3e-15 and np.linalg.eigvalsh(out).min()>-1e-14
