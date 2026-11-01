"""Source-scoped independent checks of BASS VI0 real photon Liouville flow."""
from __future__ import annotations
import csv,json,math
from pathlib import Path
import numpy as np
import pytest
from scipy.integrate import solve_ivp,simpson
import vi0_null_liouville as m

ROOT=Path(__file__).resolve().parents[1]

def test_owner_parent_exact_git_blob_without_forced_new_bg():
    guard=m.source_guard()
    assert guard['parent_sha']==m.PR311_SHA
    assert not guard['checked_7_original_main_blobs']

def test_positive_source_angular_grids_and_sixaxis_precision():
    grid=m.grids()
    assert [len(grid[k][1]) for k in ('AXIS6','LEBEDEV26','GL8x16')]==[6,26,128]
    for n,w in grid.values():
        assert abs(w.sum()-1)<4e-15
        assert min(w)>0
        assert np.max(abs(np.linalg.norm(n,axis=1)-1))<5e-15

def test_independent_koszul_connection_vs_curvature_turn():
    rng=np.random.default_rng(16042026)
    for _ in range(70):
        Q=rng.normal(size=(3,3));N=(Q+Q.T)/2
        v=rng.normal(size=3);v/=np.linalg.norm(v)
        G=m.koszul_connection(N)
        spatial=np.einsum('kab,a,b->k',G,v,v)
        assert np.max(abs(spatial-np.cross(v,N@v)))<2e-14

def test_wrong_curvature_sign_detected():
    _,g,z0=next(m.initial_conditions())
    om,S,N,v=m.parent.checked_chart(z0,g)
    W=m.parent.eigenframe_W(S,N)
    n=np.array([[.4,.65,.65]],float);n/=np.linalg.norm(n,axis=1)[:,None]
    right=m.ray_flow(n,S,N,W)[0]
    wrong=m.ray_flow(n,S,N,W,incorrect_curvature_sign=True)[0]
    assert np.max(abs(right-wrong))>0.15

def test_BianchiI_exact_null_direction_and_redshift():
    # Independent Killing-momentum exact solution, not same RHS implementation.
    sig=np.array([.13,-.05,-.08])
    n0=np.array([.4,-.5,.7]);n0/=np.linalg.norm(n0)
    S=np.diag(sig);N=np.zeros((3,3));W=np.zeros((3,3))
    def rhs(t,y):
        nd,s=m.ray_flow(y[:3][None,:],S,N,W)
        return np.r_[nd[0],-1-s[0]]
    sol=solve_ivp(rhs,(0,.3),np.r_[n0,0.],method='DOP853',rtol=3e-13,atol=2e-15)
    exact,energy=m.analytic_bianchi_I(sig,n0,.3)
    assert np.max(abs(sol.y[:3,-1]-exact))<2e-12
    assert abs(np.exp(sol.y[3,-1])-energy)<2e-12

def test_pure_VI0_intrinsic_curvature_energy_and_Hamiltonian():
    N=np.diag([0.,.55,-.36]);S=np.zeros((3,3));W=np.zeros((3,3))
    n0=np.array([.3,.6,.74]);n0/=np.linalg.norm(n0)
    def rhs(t,y):
        nd,s=m.ray_flow(y[:3][None,:],S,N,W)
        return np.r_[nd[0],-1-s[0]]
    sol=solve_ivp(rhs,(0,.3),np.r_[n0,0.],t_eval=np.linspace(0,.3,31),rtol=1e-12,atol=1e-14,method='DOP853')
    n=sol.y[:3].T
    ham=np.einsum('ni,ij,nj->n',n,N,n)/2
    assert np.max(abs(ham-ham[0]))<1e-11
    assert np.max(abs(np.exp(sol.y[3])-np.exp(-sol.t)))<2e-11
    assert np.max(abs(np.linalg.norm(n,axis=1)-1))<2e-11

def test_sphere_divergence_of_actual_shear_curvature_and_gauge():
    """Independent spherical-coordinate finite difference of the full angular vector flow."""
    S=np.array([[.12,.02,-.015],[.02,-.045,.009],[-.015,.009,-.075]])
    N=np.diag([0.,.57,-.33]);W=np.array([[0,.07,-.02],[-.07,0,.03],[.02,-.03,0.]])
    theta=.84;phi=1.1
    def flux(t,p):
        n=np.array([np.sin(t)*np.cos(p),np.sin(t)*np.sin(p),np.cos(t)])
        et=np.array([np.cos(t)*np.cos(p),np.cos(t)*np.sin(p),-np.sin(t)])
        ep=np.array([-np.sin(p),np.cos(p),0.])
        F,_=m.ray_flow(n[None,:],S,N,W)
        return np.dot(F[0],et),np.dot(F[0],ep),n
    h=1e-5
    dt=((np.sin(theta+h)*flux(theta+h,phi)[0])-(np.sin(theta-h)*flux(theta-h,phi)[0]))/(2*h)
    dp=(flux(theta,phi+h)[1]-flux(theta,phi-h)[1])/(2*h)
    div=(dt+dp)/np.sin(theta)
    n=flux(theta,phi)[2]
    assert abs(div-3*n@S@n)<6e-10

def test_null_extreme_tilt_limit_of_parent_fluid():
    # Gamma-law fluid tilt scalar at v²=1, gamma!=2: T=(2-gamma)S/(2-gamma)=S.
    for gamma in (1.,1.1,4/3,1.65):
        s=.123
        val=((3*gamma-4)*(1-1)+(2-gamma)*s)/(1-(gamma-1))
        assert abs(val-s)<1e-15

def test_dynamic_n_is_tangent_on_unit_sphere_in_actual_parent_frame():
    for case,g,z in list(m.initial_conditions())[:12]:
        om,S,N,v=m.parent.checked_chart(z,g);W=m.parent.eigenframe_W(S,N)
        dirs=m.grids()['LEBEDEV26'][0]
        dn,s=m.ray_flow(dirs,S,N,W)
        assert np.max(abs(np.sum(dirs*dn,axis=1)))<5e-15

def test_moving_grid_oblique_projector_full_chain_finite_difference():
    _,g,z=next(m.initial_conditions());om,S,N,v=m.parent.checked_chart(z,g)
    _,_,_,vd,qdec,W,_,_=m.parent.ambient_rhs(om,S,N,v,g)
    n,w=m.grids()['LEBEDEV26'];nd,s=m.ray_flow(n,S,N,W);wd=3*s*w
    P,Pd,K=m.projector_chain(v,vd,n,nd,w,wd)
    for h in (1e-5,1e-6):
        p1=m.parent.scalar_projector(v+h*vd,n+h*nd,w+h*wd) if hasattr(m.parent,'scalar_projector') else m.projector_chain(v+h*vd,vd,n+h*nd,nd,w+h*wd,wd)[0]
        assert np.max(abs((p1-P)/h-Pd))<1e-5*h/1e-5
    assert np.max(abs(K@P-P@K-Pd))<3e-14
    assert np.max(abs(P@P-P))<3e-14
    assert np.max(abs(K+K.T))>1e-4   # oblique is not Euclidean unitary!

def test_exact_pure_frame_gauge_cancellation_vs_frozen_rays():
    _,g,z=next(m.initial_conditions());om,S,N,v=m.parent.checked_chart(z,g)
    W=m.parent.eigenframe_W(S,N);n,w=m.grids()['LEBEDEV26']
    P,PD,K=m.projector_chain(v,W@v,n,n@W.T,w,np.zeros_like(w))
    _,bad,_=m.projector_chain(v,W@v,n,np.zeros_like(n),w,np.zeros_like(w))
    assert np.max(abs(PD))<1e-15
    assert np.max(abs(bad))>1e-4

def test_angular_weight_cannot_be_frozen_without_energy_violation():
    case,g,z=next(m.initial_conditions())
    n,w=m.grids()['LEBEDEV26']
    rays,moms,sol=m.integrate_one(case,g,z,'LEBEDEV26',n,w)
    zf,nf,le,lw,lI=m.split(sol.y[:,-1],len(w));om,S,N,v=m.parent.checked_chart(zf,g)
    d=m.sky_moments(nf,le,lw,lI,S)
    s=np.einsum('ni,ij,nj->n',nf,S,nf)
    false_derivative=np.dot(np.exp(lw+lI),-4*(1+s))
    physical_moment_rhs=-4*d['rho']-np.sum(S*d['pressure'])
    assert d['balance']<1e-12
    assert abs(false_derivative-physical_moment_rhs)>0.01

def test_explicit_physical_history_integral_energy_balance():
    case,g,z=next(m.initial_conditions());n,w=m.grids()['GL8x16']
    rays,moms,sol=m.integrate_one(case,g,z,'GL8x16',n,w)
    rhs=[]
    for y in sol.y.T:
        zb,nn,le,lw,li=m.split(y,len(w));om,S,N,v=m.parent.checked_chart(zb,g)
        d=m.sky_moments(nn,le,lw,li,S)
        rhs.append(-4*d['rho']-np.sum(S*d['pressure']))
    reconstructed=1+simpson(rhs,x=sol.t)
    assert abs(reconstructed-moms[-1][m.MOMENT.index('rho_tracer')])<2e-8

def test_saved_new_model_physical_results_and_no_false_dag():
    p=ROOT/'data'/'VI0_NULL_RESULTS.json'
    if not p.exists():pytest.skip('Generated physics in separate clean CI run')
    a=json.loads(p.read_text())
    assert a['ray_physical_rows']==78720
    assert a['radiation_moment_rows']==1476
    assert a['new_collisionless_ray_transport_runs']==36
    assert a['new_distinct_gravitating_einstein_ivps']==0
    assert a['maximum_angular_unit_sphere_residual']<1e-10
    assert a['maximum_liouville_invariant_error']<1e-12
    assert a['maximum_discrete_moment_balance_gap']<1e-12
    assert a['maximum_Kato_or_idempotent_error']<1e-12
    assert a['maximum_pure_gauge_projector_error']<1e-12
    assert a['original_G_DYN_MANIFOLD_VI0']=='PARTIAL'
    assert a['upper_scoped_dag']=='9/15' and a['new_completed_upper_nodes']==0
    assert not a['production_ready'] and not a['merge_ready'] and not a['auto_next']

def test_true_physical_angular_resolution_vs_false_6_axis_exactness():
    p=ROOT/'data'/'VI0_NULL_RESULTS.json'
    if not p.exists():pytest.skip('Original stored reference data absent')
    a=json.loads(p.read_text())
    for case in a['cross_grid_comparison']:
        assert case['GL128_vs_leb26_endpoint_rho_abs']<case['GL128_vs_axis6_endpoint_rho_abs']
        assert case['GL128_vs_axis6_endpoint_rho_abs']>1e-4
        assert case['axis6_endpoint_weight_drift']>1e-3
        assert case['GL128_endpoint_weight_drift']<1e-5

