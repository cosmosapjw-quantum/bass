"""CE1-K combines PR246 canonical source/path safety with PR247 scale law."""
from __future__ import annotations
from fractions import Fraction
import numpy as np
import pytest

from bianchi.nonperturbative.einstein_tabulated_source import TabulatedRadiation
from bianchi.nonperturbative.einstein_error_budget import rk4_path
from bianchi.nonperturbative.einstein_tabulated_local import certify_local_tabulated_path
from bianchi.nonperturbative.einstein_tabulated_source_canonical import (
    certify_canonical_panel_source, canonical_shifted_box, run_canonical_panel_source,
)


def src(ref=1):
    return TabulatedRadiation([0,.5,1],[0,.25,.75,1],
       [[.1,.25,.05],[.2,.15,.15]],refinement=ref,backend='python_oracle')


def test_original_frozen_same_physics_and_sharper_source():
    a=run_canonical_panel_source(src(),backend='python_oracle')
    assert a['result_status']=='CE1K_CANONICAL_AND_SOURCE_LOCAL_SCOPED'
    assert a['upper_dag']=='9/15'
    assert a['source_error_upper_h'] <= a['ce1i_source_error_upper_h']
    assert a['total_h_upper'] <= a['ce1i_total_h_upper']
    assert a['original_Emax']>=0.9
    assert a['target_h']==1e-5 and a['target_met'] is False
    assert a['production_ready'] is False
    assert all(x['source_upper']<=a['global_source_upper'] for x in a['panel_rows'])
    assert a['panel_rows'][0]['certified_lower_logscale']==0.
    assert any(x['source_upper']<a['global_source_upper'] for x in a['panel_rows'][1:])


def test_canonical_lower_safely_dominates_frozen_fixed_slope():
    a=run_canonical_panel_source(src(),backend='python_oracle')
    for p in a['panel_rows']:
        assert p['certified_lower_logscale']+1e-16 >= 3*p['left_time']/8


def test_shifted_box_rejects_inconsistent_upper():
    with pytest.raises(ValueError,match='geometry box'):
        canonical_shifted_box([0.2,0.01,0.2],0.03)


def test_shifted_box_zero_is_exact():
    assert canonical_shifted_box([0.2,0.01,0.2],0.) == [0.2,0.01,0.2]


def test_mutated_hermite_origin_is_rejected_before_canonical_enclosure():
    s=src();p=rk4_path(s,s.initial_state(),.08,4,backend='python_oracle')
    p.coefficients[0,0,3]+=.01
    with pytest.raises(ValueError,match='origin'):
        certify_canonical_panel_source(s,p)


def test_homogeneity_of_current_discrete_positive_source():
    s=src(); v=np.array([.02,.04,.03]); shift=.017
    _,p=s.moments(v); _,p_shift=s.moments(v+shift)
    np.testing.assert_allclose(p_shift,np.exp(-4*shift)*p,rtol=1e-14,atol=0)


def test_backend_explicit_and_reject_wrong_source_type():
    with pytest.raises(ValueError,match='python_oracle'):
        run_canonical_panel_source(src())
    with pytest.raises(TypeError):
        certify_canonical_panel_source(object(),object())
