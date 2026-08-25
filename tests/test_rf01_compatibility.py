"""Mechanical RF-01 compatibility and architecture boundaries."""

from __future__ import annotations

import inspect
from pathlib import Path

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
rust = pytest.importorskip("bianchi_rustcore")


def test_runtime_modules_never_initialize_or_use_the_global_rayon_pool():
    runtime_sources = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((ROOT / "_rustcore/src/runtime").glob("*.rs"))
    )
    assert "build_global" not in runtime_sources
    assert "rayon::current_num_threads" not in runtime_sources
    assert "ThreadPoolBuilder::new" in runtime_sources


def test_new_python_adapter_contains_no_numerical_implementation():
    source = (ROOT / "_rustcore/src/python/runtime.rs").read_text(encoding="utf-8")
    for forbidden in (
        "par_iter",
        "Runge",
        "stencil[",
        "dense_solve[",
        "operator[",
    ):
        assert forbidden not in source


def test_legacy_extension_exports_and_representative_result_are_unchanged():
    for name in (
        "rotation_matrix",
        "tracefree_from_5",
        "trace_rays_batch",
        "chart_rhs",
        "kin_j_moment",
        "th_integrate",
        "qe_evolve",
        "QSphere",
        "QRadial",
        "QPlan",
    ):
        assert hasattr(rust, name)
    np.testing.assert_array_equal(
        rust.rotation_matrix(np.zeros(3, dtype=np.float64)),
        np.zeros((3, 3), dtype=np.float64),
    )


def test_python_frontend_signature_is_stable_and_keyword_only_after_thread_count():
    from bianchi.runtime import RuntimePlan

    signature = inspect.signature(RuntimePlan)
    assert str(signature) == "(thread_count: 'int', *, fixture_size: 'int' = 64, require_finite: 'bool' = True, cpu_variant: 'str' = 'scalar')"
