"""Focused RF-02B scalar operator closure.

These selectors are pointwise by design.  Integrators, events, transitions, batches,
timing, tilted matter, and Wolfram authority belong to later work units.
"""

from __future__ import annotations

import importlib

import numpy as np
import pytest

from bianchi import backend
from bianchi.scalar_charts import (
    SCALAR_CHART_SCHEMA_HASH,
    SCALAR_CHART_SPECS,
    chart_schema_receipt,
)
from bianchi.geometry_identity import CONVENTION_HASH


CORPUS = {
    "class_a": (np.array([0.21, -0.17, 0.31, 0.13, -0.29]), 1.3, 0.0),
    "class_b": (np.array([0.19, 0.24, 0.08, 0.11, 0.37]), 1.25, -1.0),
    "exceptional": (np.array([0.18, -0.09, 0.12, 0.05, 0.27, 0.08]), 1.2, 0.0),
    "type_ix_d": (np.array([0.43, 0.11, -0.27, 0.16, 0.91, 1.07, 0.83]), 1.1, 0.0),
    "type_ix_d_future": (
        np.array([0.43, 0.11, -0.27, 0.16, 0.91, 1.07, 0.83]),
        1.1,
        0.0,
    ),
}


def test_scalar_inventory_is_frozen_and_excludes_later_authority_lanes():
    assert tuple(SCALAR_CHART_SPECS) == (
        "class_a",
        "class_b",
        "exceptional",
        "type_ix_d",
        "type_ix_d_future",
    )
    for excluded in (
        "class_a_tilted",
        "class_b_tilted",
        "class_a_tilted_multi",
        "general",
        "general_matter",
    ):
        assert excluded not in SCALAR_CHART_SPECS
    receipt = chart_schema_receipt()
    assert receipt["geometry_convention_hash"] == CONVENTION_HASH
    assert receipt["schema_hash"] == SCALAR_CHART_SCHEMA_HASH


@pytest.mark.parametrize("chart", tuple(CORPUS))
def test_rhs_and_exact_jvp_match_the_explicit_python_oracle(chart):
    pytest.importorskip("jax")
    y, gamma, kappa = CORPUS[chart]
    v = np.linspace(-0.31, 0.23, y.size)
    np.testing.assert_allclose(
        backend.chart_rhs(chart, y, gamma, kappa, policy="rust_required"),
        backend.chart_rhs(chart, y, gamma, kappa, policy="python_oracle"),
        rtol=2e-14,
        atol=2e-14,
    )
    np.testing.assert_allclose(
        backend.chart_jvp(chart, y, v, gamma, kappa, policy="rust_required"),
        backend.chart_jvp(chart, y, v, gamma, kappa, policy="python_oracle"),
        rtol=4e-14,
        atol=4e-14,
    )
    assert np.array_equal(
        backend.chart_jvp(
            chart, y, np.zeros_like(y), gamma, kappa, policy="rust_required"
        ),
        np.zeros_like(y),
    )


@pytest.mark.parametrize("chart", tuple(CORPUS))
def test_native_schema_receipt_matches_the_python_authority(chart):
    native = pytest.importorskip("bianchi_rustcore")
    y, gamma, kappa = CORPUS[chart]
    del y
    state_names, constraint_names = native.scalar_chart_schema(chart, gamma, kappa)
    spec = SCALAR_CHART_SPECS[chart]
    assert tuple(state_names) == spec.state_names
    assert tuple(constraint_names) == spec.constraint_names


def test_packed_order_swap_mutation_is_detected_by_the_independent_oracle():
    pytest.importorskip("jax")
    y, gamma, kappa = CORPUS["class_a"]
    permutation = np.array([1, 0, 2, 3, 4])
    oracle = backend.chart_rhs(
        "class_a", y, gamma, kappa, policy="python_oracle"
    )
    mutated = backend.chart_rhs(
        "class_a", y[permutation], gamma, kappa, policy="rust_required"
    )[permutation]
    assert not np.allclose(mutated, oracle, rtol=1e-8, atol=1e-10)


@pytest.mark.parametrize("chart", tuple(CORPUS))
def test_signed_constraints_and_projection_match_python_authority(chart):
    pytest.importorskip("jax")
    pytest.importorskip("lineax")
    y, gamma, kappa = CORPUS[chart]
    native_c = backend.chart_constraints(
        chart, y, gamma, kappa, policy="rust_required"
    )
    oracle_c = backend.chart_constraints(
        chart, y, gamma, kappa, policy="python_oracle"
    )
    assert tuple(native_c) == SCALAR_CHART_SPECS[chart].constraint_names
    assert tuple(oracle_c) == tuple(native_c)
    np.testing.assert_allclose(
        list(native_c.values()), list(oracle_c.values()), rtol=2e-14, atol=2e-14
    )

    native_y = backend.chart_project(
        chart, y, gamma, kappa, policy="rust_required"
    )
    oracle_y = backend.chart_project(
        chart, y, gamma, kappa, policy="python_oracle"
    )
    np.testing.assert_allclose(native_y, oracle_y, rtol=2e-12, atol=2e-12)
    after = backend.chart_constraints(
        chart, native_y, gamma, kappa, policy="rust_required"
    )
    assert max(map(abs, after.values()), default=0.0) <= max(
        map(abs, native_c.values()), default=0.0
    )


def test_exact_limits_and_conditional_ix_identity_are_pointwise():
    flrw = np.zeros(5)
    assert np.array_equal(
        backend.chart_rhs("class_a", flrw, 4.0 / 3.0, policy="python_oracle"),
        flrw,
    )
    kasner = np.array([0.6, 0.8, 0.0, 0.0, 0.0])
    assert np.max(np.abs(backend.chart_rhs(
        "class_a", kasner, 1.3, policy="python_oracle"
    ))) < 1e-15
    y, gamma, kappa = CORPUS["type_ix_d"]
    past = backend.chart_rhs("type_ix_d", y, gamma, kappa, policy="python_oracle")
    future = backend.chart_rhs(
        "type_ix_d_future", y, gamma, kappa, policy="python_oracle"
    )
    np.testing.assert_array_equal(future, -past)


def test_rust_required_pointwise_routes_never_touch_python_oracles(monkeypatch):
    calls = []

    class Native:
        @staticmethod
        def chart_rhs(_chart, y, _gamma, _kappa):
            calls.append("rhs")
            return np.asarray(y) * 0.0

        @staticmethod
        def chart_jvp(_chart, _y, v, _gamma, _kappa):
            calls.append("jvp")
            return np.asarray(v) * 0.0

        @staticmethod
        def chart_constraints(_chart, _y, _gamma, _kappa):
            calls.append("constraints")
            return np.array([])

        @staticmethod
        def chart_project(_chart, y, _gamma, _kappa, _iters, _damping):
            calls.append("project")
            return np.asarray(y)

    monkeypatch.setattr(backend, "_native_for", lambda *_a, **_kw: Native)

    def forbidden_import(*_args, **_kwargs):
        raise AssertionError("rust_required touched a Python numerical oracle")

    monkeypatch.setattr(importlib, "import_module", forbidden_import)
    y = np.zeros(5)
    backend.chart_rhs("class_a", y, 1.3, policy="rust_required")
    backend.chart_jvp("class_a", y, y, 1.3, policy="rust_required")
    backend.chart_constraints("class_a", y, 1.3, policy="rust_required")
    backend.chart_project("class_a", y, 1.3, policy="rust_required")
    assert calls == ["rhs", "jvp", "constraints", "project"]


def test_existing_tilted_rhs_remains_native_first_without_oracle_import(monkeypatch):
    called = []

    class Native:
        @staticmethod
        def chart_rhs(chart, y, _gamma, _kappa):
            called.append(chart)
            return np.zeros_like(y)

    monkeypatch.setattr(backend, "_native_for", lambda *_a, **_kw: Native)

    def forbidden_import(*_args, **_kwargs):
        raise AssertionError("tilted rust_required RHS touched a Python oracle")

    monkeypatch.setattr(importlib, "import_module", forbidden_import)
    result = backend.chart_rhs(
        "class_a_tilted", np.zeros(11), 1.3, policy="rust_required"
    )
    assert result.shape == (11,)
    assert called == ["class_a_tilted"]


def test_unknown_and_excluded_chart_routes_fail_closed_before_oracle_import():
    for chart in ("unknown", "class_a_tilted", "general_matter"):
        with pytest.raises(ValueError, match="RF-02B scalar chart"):
            backend.chart_rhs(chart, np.zeros(5), 1.3, policy="python_oracle")


def test_scalar_parameter_domains_fail_closed_without_changing_the_routing_tolerance():
    y = np.zeros(5)
    for gamma, kappa in ((np.nan, 0.0), (1.3, np.inf)):
        with pytest.raises(ValueError, match="parameters must be finite"):
            backend.chart_jvp(
                "class_a", y, y, gamma, kappa, policy="python_oracle"
            )
    with pytest.raises(ValueError, match="degenerate near kappa = -9"):
        backend.chart_constraints(
            "class_b", y, 1.3, -9.0 + 0.5e-9, policy="python_oracle"
        )
