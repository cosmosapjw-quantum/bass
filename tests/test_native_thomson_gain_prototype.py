"""Frozen-frame research primitive contract; no coupled/default admission."""
import numpy as np
import pytest
import bianchi_rustcore as rc


def fixture():
    s=rc.QSphere(4,8); r=rc.QRadial(-6.,3.,32)
    m=np.diag([1.3,.85,1/1.105]).ravel()
    e=s.ehat().reshape(-1,3); x=r.ln_p(); q=np.exp(x)
    l=-np.log(np.expm1(q[None,:]/np.exp(.1*e[:,2,None])))+.08*np.cos(3*x)[None,:]*np.exp(-x[None,:]**2)
    return s,r,np.ascontiguousarray(l.ravel()),m


def test_opt_in_native_api_exists():
    assert hasattr(rc,'modeb_thomson_log_gain'), 'new native log-gain primitive is missing'
    assert hasattr(rc,'modeb_thomson_log_step'), 'new native log-step primitive is missing'


def test_zero_identity_owned_and_immutable():
    s,r,l,m=fixture(); old=l.copy(); oldm=m.copy()
    y=rc.modeb_thomson_log_step(s,r,l,m,0.)
    assert y.tobytes()==l.tobytes()
    assert not np.shares_memory(y,l)
    y[0]+=1
    assert np.array_equal(l,old) and np.array_equal(m,oldm)


@pytest.mark.parametrize('h',[-1.,np.nan,np.inf])
def test_bad_exposure(h):
    s,r,l,m=fixture()
    with pytest.raises(ValueError): rc.modeb_thomson_log_step(s,r,l,m,h)


def test_finite_logs_beyond_occupation_dynamic_range():
    s,r,l,m=fixture()
    for offset in [-10000.,10000.]:
        y=rc.modeb_thomson_log_step(s,r,l+offset,m,.1)
        assert np.all(np.isfinite(y))
        np.testing.assert_allclose(y-offset,rc.modeb_thomson_log_step(s,r,l,m,.1),atol=2e-9,rtol=0)


def geometry(s,m):
    q=s.ehat().reshape(-1,3); p=q@m.reshape(3,3).T
    mu=np.linalg.norm(p,axis=1); e=p/mu[:,None]
    w=s.weights()*np.linalg.det(m.reshape(3,3))/mu**3
    return e,mu,w


def independent_gain(s,r,l,m,tail='wien',order=8):
    """Independent NumPy polynomial interpolation and analytic tail closure."""
    e,mu,w=geometry(s,m); logs=l.reshape(s.n,r.n); x=r.ln_p(); d=r.dlnp
    out=np.zeros_like(logs)
    for i in range(s.n):
        for b in range(s.n):
            z=(np.log(mu[i])-np.log(mu[b]))/d
            base=int(np.floor(z)); offsets=np.arange(order)- (order//2-1)+base
            nodes=offsets-base; frac=z-base
            weights=np.array([np.prod([(frac-nodes[c])/(nodes[a]-nodes[c]) for c in range(order) if c!=a]) for a in range(order)])
            vals=[]
            for j in range(r.n):
                v=[]
                for k in j+offsets:
                    if k<0: value=logs[b,0]+(logs[b,1]-logs[b,0])*k
                    elif k>=r.n:
                        gap=k-(r.n-1)
                        if tail=='powerlaw': value=logs[b,-1]+(logs[b,-1]-logs[b,-2])*gap
                        else: value=logs[b,-1]+(logs[b,-1]-logs[b,-2])*np.expm1(gap*d)/(-np.expm1(-d))
                    else: value=logs[b,k]
                    v.append(value)
                vals.append(np.dot(weights,v))
            out[i]+=w[b]*3/(16*np.pi)*(1+np.dot(e[i],e[b])**2)*np.exp(vals)
    return np.log(out).ravel()


@pytest.mark.parametrize('tail',['wien','powerlaw'])
def test_independent_numpy_gain_and_midpoint(tail):
    s,r,l,m=fixture(); g=independent_gain(s,r,l,m,tail)
    actual=rc.modeb_thomson_log_gain(s,r,l,m,tail=tail)
    np.testing.assert_allclose(actual,g,atol=2e-11,rtol=0)
    h=.125; middle=np.logaddexp(l-h/2,g+np.log(-np.expm1(-h/2)))
    gm=independent_gain(s,r,middle,m,tail)
    ref=np.logaddexp(l-h,gm+np.log(-np.expm1(-h)))
    np.testing.assert_allclose(rc.modeb_thomson_log_step(s,r,l,m,h,tail=tail),ref,atol=2e-11,rtol=0)


def test_analytic_energy_matched_powerlaw():
    s,r,_,m=fixture(); e,mu,w=geometry(s,m); x=r.ln_p()
    slopes=-1.-.3*np.arange(s.n)/s.n; amplitude=.1*e[:,0]
    l=(amplitude[:,None]+slopes[:,None]*x).ravel()
    i,j=7,12
    expected=np.sum(w*3/(16*np.pi)*(1+(e@e[i])**2)*np.exp(amplitude+slopes*(x[j]+np.log(mu[i]/mu))))
    actual=rc.modeb_thomson_log_gain(s,r,l,m,tail='powerlaw').reshape(s.n,r.n)[i,j]
    assert abs(actual-np.log(expected))<1e-12


@pytest.mark.parametrize('kwargs',[{'order':0},{'order':1},{'order':17},{'tail':'bad'},{'kernel':'bgk_conservative'},{'v_b':[0.,0.,.1]},{'v_b':[0.,np.nan,0.]},{'v_b':[0.,0.]}])
def test_invalid_scope(kwargs):
    s,r,l,m=fixture()
    with pytest.raises(ValueError): rc.modeb_thomson_log_step(s,r,l,m,0.,**kwargs)


@pytest.mark.parametrize('case',['logs_nan','logs_inf','shape','frame_nan','frame_singular','frame_left','frame_condition','grid_nan','grid_backwards'])
def test_invalid_data_no_mutation(case):
    s,r,l,m=fixture()
    if case=='logs_nan': l[1]=np.nan
    if case=='logs_inf': l[1]=np.inf
    if case=='shape': l=l[:-1]
    if case=='frame_nan': m[0]=np.nan
    if case=='frame_singular': m[0]=0
    if case=='frame_left': m[0]=-1
    if case=='frame_condition': m[0]=1e-12
    if case=='grid_nan': r=rc.QRadial(np.nan,3.,32)
    if case=='grid_backwards': r=rc.QRadial(3.,-6.,32)
    before=l.tobytes(); mb=m.tobytes()
    with pytest.raises(ValueError): rc.modeb_thomson_log_step(s,r,l,m,0.)
    assert l.tobytes()==before and m.tobytes()==mb


def test_tiny_exposure_has_no_roundtrip_floor():
    s,r,l,m=fixture()
    generator_scale=np.max(abs(np.expm1(rc.modeb_thomson_log_gain(s,r,l,m)-l)))
    for h in [2.**-20,2.**-30,2.**-40]:
        a=rc.modeb_thomson_log_step(s,r,l,m,h)
        b=rc.modeb_thomson_log_step(s,r,rc.modeb_thomson_log_step(s,r,l,m,h/2),m,h/2)
        assert np.max(np.abs(a-b))<1e-11
        assert np.max(np.abs(a-l)) < 2*generator_scale*h+1e-11


def test_large_exposure_is_finite_not_stiff_exact_claim():
    s,r,l,m=fixture()
    a=rc.modeb_thomson_log_step(s,r,l,m,1e5)
    gg=rc.modeb_thomson_log_gain(s,r,rc.modeb_thomson_log_gain(s,r,l,m),m)
    assert np.all(np.isfinite(a))
    np.testing.assert_allclose(a,gg,atol=1e-12,rtol=0)


def test_high_precision_analytic_gain():
    from decimal import Decimal,localcontext
    s,r,_,m=fixture(); e,mu,w=geometry(s,m); x=r.ln_p()
    slopes=-1.-.3*np.arange(s.n)/s.n; amps=.1*e[:,0]
    l=(amps[:,None]+slopes[:,None]*x).ravel(); i,j=7,12
    with localcontext() as ctx:
        ctx.prec=70; D=lambda v:Decimal.from_float(float(v))
        pi=Decimal('3.141592653589793238462643383279502884197169399375105820974944592307816')
        total=Decimal(0)
        for b in range(s.n):
            dot=sum(D(e[i,k])*D(e[b,k]) for k in range(3))
            query=D(x[j])+D(mu[i]).ln()-D(mu[b]).ln()
            total+=D(w[b])*Decimal(3)/(16*pi)*(1+dot*dot)*(D(amps[b])+D(slopes[b])*query).exp()
        expected=float(total.ln())
    actual=rc.modeb_thomson_log_gain(s,r,l,m,tail='powerlaw').reshape(s.n,r.n)[i,j]
    assert abs(actual-expected)<2e-12


def test_order_cannot_exceed_nodes():
    s,r,l,m=fixture(); r=rc.QRadial(-6.,3.,4); l=l[:s.n*4].copy()
    with pytest.raises(ValueError): rc.modeb_thomson_log_step(s,r,l,m,0.,order=8)
