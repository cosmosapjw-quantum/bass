"""BF3-D: new scoped field tests, not a replay of parent science campaigns."""
import numpy as np
import pytest
from bianchi.nonperturbative.lapse_field import (
    FieldGrid, InverseMap, LapseField, stokes, from_stokes,
    stationary, smooth_initial, physical_screen, interpolate,
)
from bianchi.nonperturbative._core.lapse_transport import PeriodicLapse, TetradHistory
from bianchi.q import polarization as P8

OPT={'backend':'python_oracle'}


def test_explicit_backend_and_invalid_inputs():
    g=FieldGrid(9,6,8);m=PeriodicLapse(.35)
    with pytest.raises(ValueError):LapseField(g,m,.7)
    with pytest.raises(ValueError):FieldGrid(8,6,8)
    with pytest.raises(ValueError):LapseField(g,m,-.1,**OPT)
    with pytest.raises(ValueError):LapseField(g,m,.7,**OPT).split(stationary(g),-.1,4)


def test_source_uses_final_angles_and_common_screen():
    g=FieldGrid(9,8,8);m=PeriodicLapse(.55);s=LapseField(g,m,.7,**OPT)
    Y=stationary(g,2.)
    J=s.carrier(Y)
    M=s.source(Y)
    expected=(4*np.pi/3*m.N(g.x)**-4*2)[:,None,None]*np.eye(3)
    assert np.max(abs(M-expected))<2e-11
    assert np.max(abs(np.einsum('xaij,aj->xai',J,g.n)))<2e-11


def test_fourier_barycentric_interpolation_exact_polynomial():
    g=FieldGrid(13,8,8)
    y=(np.cos(2*g.x)[:,None]+.1*g.mu[None,:]**3)
    y=np.broadcast_to(y[:,:,None,None,None],(g.nx,g.nmu,g.nphi,2,2)).copy()
    xd=np.broadcast_to(g.x[:,None]-.17,(g.nx,g.nmu));md=np.broadcast_to(.8*g.mu[None,:],xd.shape)
    out=interpolate(g,y,xd,md)
    target=np.cos(2*xd)+.1*md**3
    assert np.max(abs(out-target[:,:,None,None,None]))<2e-11


def test_inverse_map_roundtrip_and_redshift():
    g=FieldGrid(9,6,8);m=PeriodicLapse(.55)
    inv=InverseMap(g,m,.2,**OPT)
    d=inv.departure
    hist=TetradHistory(m,d['x'],d['n'],.2,screen0=d['screen'])
    f=hist.at(.2)
    assert np.max(abs(f['x'][:,0]-inv.final_x))<8e-10
    assert np.max(abs(f['n']-inv.final_n))<8e-10
    assert np.max(abs(f['r']*d['r']-1))<8e-10


def test_free_flat_translation_and_stationary_lapse():
    g=FieldGrid(17,12,8)
    flat=InverseMap(g,PeriodicLapse(0),.23,**OPT)
    y=smooth_initial(g.x[:,None,None],g.mu[None,:,None],g.phi[None,None,:])
    expect=smooth_initial(g.x[:,None,None]-.23*g.mu[None,:,None],g.mu[None,:,None],g.phi[None,None,:])
    assert np.max(abs(flat.apply(y)-expect))<2e-11
    curved=InverseMap(g,PeriodicLapse(.55),.3,**OPT)
    assert np.max(abs(curved.apply(stationary(g))-stationary(g)))<4e-10


def test_local_collision_coordinate_clock_against_p8():
    g=FieldGrid(9,8,8);m=PeriodicLapse(.55);s=LapseField(g,m,lambda x:1.1+.2*np.cos(x),**OPT)
    y=smooth_initial(g.x[:,None,None],g.mu[None,:,None],g.phi[None,None,:])
    out=s.collision(y,.17)
    J=s.screen_to_cartesian(y)
    ref=np.stack([P8.collide(g.n,g.w,J[i],.17*s.rate[i]) for i in range(g.nx)])
    assert np.max(abs(s.screen_to_cartesian(out)-ref))<2e-11
    wrong=np.stack([P8.collide(g.n,g.w,J[i],.17*s.nu[i]) for i in range(g.nx)])
    assert np.max(abs(ref-wrong))>1e-3


def test_constant_lapse_scatter_exact_semigroup():
    g=FieldGrid(9,8,8);m=PeriodicLapse(0,offset=.4);s=LapseField(g,m,.7,**OPT)
    y=np.broadcast_to(smooth_initial(np.array(0),g.mu[None,:,None],g.phi[None,None,:]),(g.nx,g.nmu,g.nphi,2,2)).copy()
    expected=s.collision(y,.23)
    actual=s.split(y,.23,4).at(.23)
    assert np.max(abs(actual-expected))<2e-11


def test_full_equilibrium_and_input_unchanged():
    g=FieldGrid(13,10,8);m=PeriodicLapse(.55);s=LapseField(g,m,lambda x:1+.3*np.sin(x),**OPT)
    y=stationary(g);copy=y.copy()
    out=s.split(y,.25,8).at(.25)
    assert np.array_equal(y,copy)
    assert np.max(abs(out-y))<4e-10
    assert np.max(abs(s.rhs(0,y)))<2e-11


def test_nonzero_collision_initial_gradient_and_local_balance():
    g=FieldGrid(25,12,8);s=LapseField(g,PeriodicLapse(.35),lambda x:1.1+.3*np.sin(x),**OPT)
    y=smooth_initial(g.x[:,None,None],g.mu[None,:,None],g.phi[None,None,:])
    bal=s.balance(y,s.rhs(0,y))
    assert abs(bal['Killing_derivative'])<2e-8
    assert bal['collision_energy_max']<2e-11


def test_split_direct_finite_time_same_physics():
    g=FieldGrid(25,16,8);s=LapseField(g,PeriodicLapse(.35),lambda x:1+.25*np.sin(x),**OPT)
    y=smooth_initial(g.x[:,None,None],g.mu[None,:,None],g.phi[None,None,:])
    d=s.direct(y,.2).at(.2)
    a=s.split(y,.2,32).at(.2)
    assert np.max(abs(a-d))<2e-4
    assert physical_screen(a).min()>0


def test_periodic_origin_and_linear_signed_difference():
    g=FieldGrid(13,10,8);s=LapseField(g,PeriodicLapse(.35),.7,**OPT)
    b=stationary(g);d=from_stokes(.1*np.cos(g.x[:,None,None])*(3*g.mu[None,:,None]**2-1)/2,0,0,0)
    d=np.broadcast_to(d,b.shape).copy()
    inv=InverseMap(g,s.metric,.11,**OPT)
    assert np.max(abs(inv.apply(b+d)-inv.apply(b)-inv.apply(d)))<2e-11
    assert np.max(abs(inv.apply(b)-b))<4e-10


def test_zero_time_noop_and_physical_input_checks():
    g=FieldGrid(9,6,8);s=LapseField(g,PeriodicLapse(.2),0.,**OPT)
    y=stationary(g)
    assert np.array_equal(s.split(y,0,2).at(0),y)
    with pytest.raises(ValueError):s.split(y,.1,0)
    bad=y.astype(complex)
    with pytest.raises(ValueError):s.direct(bad,.1)
    bad=y.copy();bad[0,0,0,0,0]=-2
    with pytest.raises(ValueError):s.direct(bad,.1)
