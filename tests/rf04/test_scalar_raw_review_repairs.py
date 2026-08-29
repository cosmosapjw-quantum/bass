"""Focused regressions for the single external-review repair pass.

Kept outside the immutable delivery payload so handoff validation remains an
exact check of the published inputs.
"""
from pathlib import Path
import importlib
import importlib.util

import numpy as np
import pytest


def _load_sibling(name: str):
    path = Path(__file__).with_name(name + ".py")
    spec = importlib.util.spec_from_file_location("rf04_review_" + name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _native():
    try:
        return importlib.import_module("bianchi_rustcore")
    except ImportError as exc:
        pytest.fail(f"RF04_NATIVE_BOUNDARY_UNAVAILABLE: {exc}", pytrace=False)


def test_scalar_raw_member_error_codes_use_frozen_tuple_schema():
    public = _load_sibling("test_public_dense_differential")
    _, args = public._case()
    initial = np.ascontiguousarray(np.stack([args[0], 0.75 + 0.31 * args[0][::-1]]))
    out = _native().rf04_typeii_batch_v1(
        initial,
        *args[1:],
        "scalar_intensity_v1",
        "fixed_grid_raw_v1",
    )
    assert isinstance(out["member_error_code"], tuple)
    assert out["member_error_code"] == (None, None)


def test_scalar_raw_one_node_schema_boundary_matches_dense_oracle():
    public = _load_sibling("test_public_dense_differential")
    oracle, args = public._case()
    directions = np.ascontiguousarray([[1.0, 0.0, 0.0]])
    weights = np.ascontiguousarray([4.0 * np.pi])
    initial = np.ascontiguousarray([1.2])
    one = (initial, directions, weights, *args[3:])
    expected = oracle.scalar_history(*one)
    out = _native().rf04_typeii_trajectory_v1(
        *one,
        "scalar_intensity_v1",
        "fixed_grid_raw_v1",
    )
    np.testing.assert_allclose(
        out["radiation_history"], expected, rtol=1.0e-10, atol=2.0e-12
    )
