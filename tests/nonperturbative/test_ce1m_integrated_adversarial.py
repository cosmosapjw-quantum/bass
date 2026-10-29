"""CE1-M: PR249 opt-in source bound on PR251 physical table and positivity locks.

These tests separate invalid physical/topological inputs from valid same-cardinality
positive stored ray/mass recertification.
"""
from __future__ import annotations

import numpy as np
import pytest

from bianchi.nonperturbative.einstein_error_budget import rk4_path
from bianchi.nonperturbative.einstein_tabulated_source import TabulatedRadiation
from bianchi.nonperturbative.einstein_tabulated_source_canonical import (
    certify_canonical_panel_source, canonical_shifted_box,
)


def source(ref=1):
    return TabulatedRadiation(
        [0,.5,1], [0,.25,.75,1], [[.1,.25,.05],[.2,.15,.15]],
        refinement=ref, backend='python_oracle',
    )


def path_from(source):
    return rk4_path(source, source.initial_state(), .08, 4, backend='python_oracle')


def test_frozen_physical_cell_rebinding_fails_before_panel_source_certificate():
    s=source()
    p=path_from(s)
    s.cells=tuple(list(s.cells))
    with pytest.raises(ValueError,match='Immutable physical'):
        certify_canonical_panel_source(s,p)


def test_continuum_energy_rebinding_fails_closed():
    s=source()
    p=path_from(s)
    s.continuum_energy=s.continuum_energy*2
    with pytest.raises(ValueError,match='Immutable physical'):
        certify_canonical_panel_source(s,p)


def test_binary_original_cell_table_mutation_rejected():
    s=source()
    p=path_from(s)
    s.cell_energy=s.cell_energy.copy()
    s.cell_energy[0,0]+=0.1
    with pytest.raises(ValueError,match='Immutable physical'):
        certify_canonical_panel_source(s,p)


def test_current_negative_ray_mass_rejected_before_residual_bound():
    s=source()
    p=path_from(s)
    s.mass=s.mass.copy()
    s.mass[0]=-1.0
    with pytest.raises(ValueError,match='Positive|Nonnegative'):
        certify_canonical_panel_source(s,p)


def test_cardinality_mismatch_rejected_on_panel_certificate():
    s=source()
    p=path_from(s)
    s.n=np.concatenate([s.n,s.n[0:1]],axis=0)
    s.mass=np.concatenate([s.mass,s.mass[0:1]],axis=0)
    with pytest.raises(ValueError,match='cardinality'):
        certify_canonical_panel_source(s,p)


def test_same_cardinality_positive_ray_mass_rebinding_preserves_valid_cap():
    s=source()
    p=path_from(s)
    s.mass=s.mass.copy()*1.005
    s.n=s.n.copy()*1.002
    out=certify_canonical_panel_source(s,p)
    assert out['source_error_upper_h']>0
    assert out['source_error_upper_h']<=out['ce1i_source_error_upper_h']
    assert out['total_h_upper']<=out['ce1i_total_h_upper']
    assert all(row['source_upper']<=out['global_source_upper'] for row in out['panel_rows'])


def test_comparison_uses_strict_monotonic_shifted_boxes():
    s=source()
    p=path_from(s)
    out=certify_canonical_panel_source(s,p)
    for row in out['panel_rows']:
        m=row['certified_lower_logscale']
        assert all(v>=m for v in out['geometry_box_upper'])
        assert all(0<=q<=B for q,B in zip(
            row['shifted_source_box_upper'],out['geometry_box_upper']))
        assert row['source_upper']<=out['global_source_upper']
    assert out['panel_rows'][-1]['source_upper']<out['panel_rows'][0]['source_upper']


def test_shifted_box_never_clips_inconsistent_positive_panel_minimum():
    with pytest.raises(ValueError,match='upper below certified lower'):
        canonical_shifted_box([0.03,0.02,0.04],0.025)
