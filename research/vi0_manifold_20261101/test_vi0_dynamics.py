"""Bounded VI0 theory tests; no production or independent-author claims."""
import csv
import json
from pathlib import Path

import numpy as np
import pytest
import sympy as sp

import vi0_dynamics as vi

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
WITNESS=np.array([.09,-.03,.55,.36,.12,-.10,.07])
GAMMA=4/3


def state():return vi.checked_chart(WITNESS,GAMMA)


def test_exact_class_A_momentum_polynomial_and_curvature_propagation():
    o=vi.symbolic_class_a_certificate()
    assert o['class_A_momentum_polynomial_residuals']==[0,0,0]
    assert o['class_A_curvature_polynomial_residual']=='0'
    assert o['gamma_law_Q_evolution_symbolic_residual']=='0'


def test_source_lock_identity_and_immutable_integration_parent():
    assert vi.PARENT_PR==310
    assert vi.PARENT_HEAD=='71adfbb2948f6c23725a01dfc048e90623a9eab5'
    assert len(vi.ORIGINAL_BLOBS)==7
    if (ROOT/'bianchi'/'conventions.py').exists():
        assert vi.original_source_guard(ROOT)==7
    else:
        pytest.skip('Original seven BASS owner files absent locally, independently tested in clean GitHub checkout')


def test_positive_exact_7D_codazzi_gauss_and_nonzero_covariant_rotation():
    om,S,N,v=state()
    assert 0<om<1 and 0<np.dot(v,v)<1
    assert np.max(abs(vi.residuals(om,S,N,v,GAMMA)))<1e-14
    W=vi.eigenframe_W(S,N)
    assert np.max(abs(W+W.T))<2e-14
    assert np.max(abs(W))>1e-5
    assert np.isclose(W[0,1],-S[0,1]) and np.isclose(W[0,2],-S[0,2])


def test_source_geometric_frame_keeps_curvature_eigenvectors():
    om,S,N,v=state()
    od,Sd,Nd,vd,qdec,W,Pi,Q=vi.ambient_rhs(om,S,N,v,GAMMA)
    assert np.max(abs(Nd-np.diag(np.diag(Nd))))<2e-14
    assert np.isclose(Nd[1,1],(qdec+2*S[1,1])*N[1,1])
    assert np.isclose(Nd[2,2],(qdec+2*S[2,2])*N[2,2])


def test_exact_constrained_tangent_belongs_to_physical_ambient_vector_field():
    assert vi.chart_tangency(WITNESS,GAMMA)<5e-14


def test_gauss_and_momentum_propagation_pointwise_without_projection():
    om,S,N,v=state()
    diff,actual,predicted=vi.propagation_residual(om,S,N,v,GAMMA)
    assert max(abs(diff))<8e-14
    assert max(abs(actual))<8e-14


def test_hostile_negative_control_missing_frame_rotation_in_velocity():
    om,S,N,v=state()
    diff,actual,_=vi.propagation_residual(om,S,N,v,GAMMA,wrong_frame=True)
    assert np.max(abs(diff[1:]))>1e-4, 'Missing W v must destroy original Codazzi transport'


def test_hostile_negative_control_missing_epsilon_curvature_torque():
    om,S,N,v=state()
    diff,actual,_=vi.propagation_residual(om,S,N,v,GAMMA,drop_torque=True)
    assert np.max(abs(diff[1:]))>1e-4, 'Removing v cross N v must destroy Codazzi propagation'


def test_co_rotated_grid_must_cancel_pure_frame_rotation():
    om,S,N,v=state();W=vi.eigenframe_W(S,N)
    P,Pd,K=vi.projector_lift(v,W@v,vi.AXES,vi.AXES@W.T)
    assert np.max(abs(Pd))<1e-14
    assert np.max(abs(K))<1e-14


def test_hostile_freezing_angular_ray_labels_gives_spurious_kato_connection():
    om,S,N,v=state();W=vi.eigenframe_W(S,N)
    _,Pd,_=vi.projector_lift(v,W@v,vi.AXES,np.zeros_like(vi.AXES))
    assert np.max(abs(Pd))>1e-3
    _,wrong,_=vi.projector_lift(v,W@v,vi.AXES,-vi.AXES@W.T)
    assert np.max(abs(wrong))>1e-3


def test_total_projector_gauge_covariance_and_kato_intertwiner():
    om,S,N,v=state();W=vi.eigenframe_W(S,N)
    od,Sd,Nd,vd,*_=vi.ambient_rhs(om,S,N,v,GAMMA)
    P,Pd,K=vi.projector_lift(v,vd,vi.AXES,vi.AXES@W.T)
    _,Pphysical,_=vi.projector_lift(v,vd-W@v,vi.AXES,np.zeros_like(vi.AXES))
    assert np.max(abs(Pd-Pphysical))<5e-14
    assert np.max(abs(P@P-P))<5e-14
    assert np.max(abs(K@P-P@K-Pd))<5e-14


def test_invariant_limit_v_zero_is_three_directional_tangent_in_full_space():
    z=WITNESS.copy();z[4:]=0
    om,S,N,v=vi.checked_chart(z,GAMMA)
    assert np.max(abs(vi.residuals(om,S,N,v,GAMMA)))<1e-14
    assert np.max(abs(vi.reduced_rhs(0,z,GAMMA)[4:]))<1e-14
    P=vi.scalar_projector(v)
    assert np.linalg.matrix_rank(P,tol=1e-10)==1
    n=vi.AXES;vv=np.array([.001,0,0]);assert np.max(abs(P-vi.scalar_projector(vv,n)))>1e-5


def test_boundary_p_zero_q_zero_exactly_refused_not_called_vi0():
    for j in (2,3):
        z=WITNESS.copy();z[j]=0
        with pytest.raises(ValueError,match='Outside regular'):vi.checked_chart(z,GAMMA)


def test_real_12_source_owned_trajectories_and_492_physical_epochs():
    rows,summary=vi.physical_histories()
    assert len(rows)==492 and len(summary)==12
    assert max(x['max_Gauss'] for x in summary)<2e-13
    assert max(x['max_Codazzi'] for x in summary)<2e-13
    assert max(x['max_constraint_propagation_residual'] for x in summary)<2e-12
    assert min(x['endpoint_Omega'] for x in summary)>0
    assert min(min(x['endpoint_curvature_parameters']) for x in summary)>0


def test_generated_replay_matches_json_and_csv_and_has_no_fraudulent_DAG_admission(tmp_path):
    run=vi.run(tmp_path)
    assert run['time_sampled_physical_states']==492
    assert run['upper_BASS_DAG_scoped_source_mapped']=='9/15'
    assert run['G_DYN_MANIFOLD_VI0_FULL']=='PARTIAL'
    assert run['JOIN_J1']=='HOLD'
    assert run['new_fully_completed_upper_nodes']==0
    assert not run['production_ready'] and not run['merge_ready'] and not run['auto_next']
    with (tmp_path/'VI0_DYNAMIC_PHYSICAL_HISTORIES.csv').open() as f:
        assert len(list(csv.DictReader(f)))==492
    assert json.loads((tmp_path/'VI0_DYNAMIC_RESULTS.json').read_text())==run


def test_analytic_scalar_projector_reparametrization_rank3():
    # Differential witness directly checks local injectivity at nonzero tilt.
    v=np.array([.12,-.10,.07]);h=1e-7
    m=np.column_stack([((vi.scalar_projector(v+np.eye(3)[k]*h)-
                         vi.scalar_projector(v-np.eye(3)[k]*h))/(2*h)).ravel()
                       for k in range(3)])
    assert np.linalg.matrix_rank(m,tol=1e-8)==3


def test_hostile_nonorthogonal_scalar_projector_kato_not_unitary():
    # Crucial adversarial guard: collision projector is oblique, not Hermitian.
    # Therefore the scalar Kato commutator does not imply unitary transport.
    om,S,N,v=state();W=vi.eigenframe_W(S,N)
    od,Sd,Nd,vd,*_=vi.ambient_rhs(om,S,N,v,GAMMA)
    P,Pd,K=vi.projector_lift(v,vd,vi.AXES,vi.AXES@W.T)
    assert np.max(abs(P-P.T))>0.05
    assert np.max(abs(K+K.T))>0.05
    assert np.max(abs(K@P-P@K-Pd))<5e-14
