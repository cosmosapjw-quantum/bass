"""Byte-level contracts for generated Rust data that previously drifted."""

from __future__ import annotations

from pathlib import Path
import re

import numpy as np
import pytest

from scripts import codegen_coeff_tables as coeff_codegen
from scripts import codegen_pstf as pstf_codegen
from scripts import codegen_riemann_rust as riemann_codegen
from scripts import codegen_thermo_tables as thermo_codegen


ROOT = Path(__file__).resolve().parents[1]


def test_coefficient_generator_canonicalizes_zero_and_matches_checked_source():
    generated = coeff_codegen.generate()
    checked = (ROOT / "_rustcore/src/kinetic/coeff_tables.rs").read_text()

    assert generated == checked
    assert re.search(r"(?<![\d.])-0\.0(?=[,\]])", generated) is None


@pytest.mark.parametrize("ell", range(2, pstf_codegen.L_MAX_RUST + 1))
def test_pstf_generator_uses_the_unique_exact_trace_subspace_projector(ell):
    raw_basis = pstf_codegen.H._trace_subspace(ell)
    basis = pstf_codegen.canonical_trace_basis(raw_basis)
    left_inverse = pstf_codegen.exact_left_inverse(basis)
    projector = basis @ left_inverse

    np.testing.assert_allclose(basis, raw_basis, rtol=0.0, atol=5.0e-16)
    np.testing.assert_allclose(
        left_inverse @ basis,
        np.eye(basis.shape[1]),
        rtol=0.0,
        atol=2.0e-15,
    )
    np.testing.assert_allclose(projector, projector.T, rtol=0.0, atol=1.0e-15)
    np.testing.assert_allclose(
        projector @ projector, projector, rtol=0.0, atol=2.0e-15
    )


def test_pstf_generator_matches_checked_source():
    generated = pstf_codegen.generate()
    checked = (ROOT / "_rustcore/src/kinetic/pstf_gen.rs").read_text()

    assert generated == checked


@pytest.mark.parametrize(
    ("generator", "relative"),
    [
        (riemann_codegen.generate, "_rustcore/src/rays/riemann_gen.rs"),
        (thermo_codegen.generate, "_rustcore/src/thermo/dof_table.rs"),
    ],
)
def test_other_generated_rust_matches_checked_source(generator, relative):
    assert generator() == (ROOT / relative).read_text()
