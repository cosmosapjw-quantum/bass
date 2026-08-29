"""Native boundary acceptance for the raw scalar donor slice.

No skip/xfail and no Python production fallback. Missing native symbols are
boundary RED, NOT proof that a physics mutation was killed. These tests compare
actual state arrays, never production-reported residuals as their own oracle.
"""
from pathlib import Path
import importlib
import importlib.util
import json
import numpy as np
import pytest


def _oracle():
    spec=importlib.util.spec_from_file_location('rf04_independent_reference',Path(__file__).with_name('rf04_dense_oracle.py'))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def _native():
    try: module=importlib.import_module('bianchi_rustcore')
    except ImportError as exc: pytest.fail(f'RF04_NATIVE_BOUNDARY_UNAVAILABLE: {exc}',pytrace=False)
    for name in ('rf04_typeii_execution_identity_v1','rf04_typeii_trajectory_v1','rf04_typeii_batch_v1'):
        assert callable(getattr(module,name,None)),f'RF04_NATIVE_SYMBOL_MISSING: {name}'
    return module


def _case(h_factor=1.,opacity_scale=1.):
    o=_oracle();e,w=o.lebedev26();q1,mid,q3,op,h=o.background_fixture()
    y=np.ascontiguousarray(1+.18*e[:,0]*e[:,1]-.13*e[:,1]*e[:,2]+.09*e[:,0]*e[:,2])
    args=(y,e,w,q1,mid,q3,op,np.ascontiguousarray(h*h_factor),1.3,opacity_scale,1)
    return o,args


@pytest.mark.parametrize('h_factor',[1.,4.])
@pytest.mark.parametrize('opacity_scale',[0.,1.])
def test_public_scalar_raw_history_matches_dense_oracle(h_factor,opacity_scale):
    native=_native();o,args=_case(h_factor,opacity_scale)
    expected=o.scalar_history(*args)
    out=native.rf04_typeii_trajectory_v1(*args,'scalar_intensity_v1','fixed_grid_raw_v1')
    actual=np.asarray(out['radiation_history'])
    assert actual.shape==expected.shape and np.isfinite(actual).all()
    np.testing.assert_array_equal(actual[0],args[0])
    np.testing.assert_allclose(actual,expected,rtol=1e-10,atol=2e-12)
    assert out['schema_id']=='bass-rf04-typeii-public-route/v1'
    assert out['route_id']=='kinetic.typeii.trajectory_v1'
    ident=json.loads(out['execution_identity'])
    assert ident['certificate_scope']=='PROJECTED_RESIDUAL_ONLY_NOT_GLOBAL_FORWARD_ERROR'
    # The complete RF04 suite retains the all-capability milestone gate.
    assert 'scalar_intensity_v1' in ident['carrier_capabilities']
    assert 'fixed_grid_raw_v1' in ident['quadrature_capabilities']
    expected_diagnostics=o.scalar_diagnostics(args[1],args[2],args[4],expected,args[10])
    for name,values in expected_diagnostics.items():
        np.testing.assert_allclose(out['diagnostics'][name],values,rtol=2e-9,atol=3e-12)
    residual=np.asarray(out['diagnostics']['projected_residual_estimate'])
    assert residual.shape==(len(args[7]),) and np.isfinite(residual).all()
    assert np.all((residual>=0)&(residual<=1.0))
    contract_path=Path(__file__).resolve().parents[2]/'docs/rust_first_runtime/rf04_external_review_resume_20260829/CONTRACT.json'
    contract=json.loads(contract_path.read_text())
    assert ident['execution_profile_id']==contract['profile']['execution_profile_id']
    assert ident['execution_profile_sha256']==contract['profile_sha256']
    assert ident['public_route_schema_sha256']==contract['authority']['a1_schema_sha256']
    for key in ('sci_auth_head','sci_auth_tree','sci_auth_manifest_sha256'):
        assert ident[key]==contract['authority'][key]
    assert ident['diagnostic_semantics']['projected_residual_estimate']=='MAX_ACCEPTED_PROJECTED_RESIDUAL_TARGET_RATIO_NOT_FORWARD_ERROR'
    assert ident['diagnostic_semantics']['left_invariant_drift']=='FULL_STEP_MIDPOINT_LEFT_COVECTOR_DRIFT_INCLUDES_TRANSPORT'


def test_public_scalar_raw_batch_matches_independent_reference():
    native=_native();o,args=_case()
    first=args[0];second=np.ascontiguousarray(.75+.31*first[::-1])
    initial=np.ascontiguousarray(np.stack([first,second]));shared=args[1:]
    out=native.rf04_typeii_batch_v1(initial,*shared,'scalar_intensity_v1','fixed_grid_raw_v1')
    expected=np.stack([o.scalar_history(row,*shared)[-1] for row in initial])
    np.testing.assert_allclose(out['final_radiation'],expected,rtol=1e-10,atol=2e-12)
    np.testing.assert_array_equal(out['member_status'],[0,0])
    np.testing.assert_array_equal(out['member_completed_steps'],[2,2])
    assert isinstance(out['member_error_code'],tuple)
    assert out['member_error_code']==(None,None)


def test_public_scalar_raw_one_node_schema_boundary_matches_dense_oracle():
    native=_native();o,args=_case()
    directions=np.ascontiguousarray([[1.,0.,0.]])
    weights=np.ascontiguousarray([4*np.pi])
    initial=np.ascontiguousarray([1.2])
    one=(initial,directions,weights,*args[3:])
    expected=o.scalar_history(*one)
    out=native.rf04_typeii_trajectory_v1(*one,'scalar_intensity_v1','fixed_grid_raw_v1')
    np.testing.assert_allclose(out['radiation_history'],expected,rtol=1e-10,atol=2e-12)


def test_public_scalar_raw_batch_isolates_nonfinite_member():
    native=_native();o,args=_case();initial=np.ascontiguousarray(np.stack([args[0],args[0],.8*args[0]]))
    initial[1,0]=np.nan
    out=native.rf04_typeii_batch_v1(initial,*args[1:],'scalar_intensity_v1','fixed_grid_raw_v1')
    final=np.asarray(out['final_radiation']);status=np.asarray(out['member_status'])
    assert final.shape==initial.shape and status.shape==(3,)
    assert status[0]==status[2]==0 and status[1]!=0
    assert np.isnan(final[1]).all()
    assert out['member_completed_steps'][1]==0
    assert out['member_error_code'][1] is not None
    for i in [0,2]:
        np.testing.assert_allclose(final[i],o.scalar_history(initial[i],*args[1:])[-1],rtol=1e-10,atol=2e-12)
