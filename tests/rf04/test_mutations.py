"""Hostile RF-04 controls that cross a real production boundary.

Standalone rank-one identities and hand-written non-normal matrices are not
mutation evidence.  Every test here either executes an RF-04 route or inspects
executable symbol references after removing comments and strings.
"""
from __future__ import annotations

import ast
import importlib
from pathlib import Path
import re

import numpy as np
import pytest

from .test_kinetic_contract import (
    _angular_grid,
    _background,
    _physical_polarized_state,
)


ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN_EXACT = {"qe_evolve", "qe_ensemble", "python_oracle"}
FORBIDDEN_PREFIXES = ("qx_", "qp_")


def _native():
    return importlib.import_module("bianchi_rustcore")


def _trajectory(initial, carrier, route, *, v=0.1):
    directions, weights = _angular_grid()
    q1, mid, q3, opacity, step_size = _background(v=v, steps=1)
    return _native().rf04_typeii_trajectory_v1(
        np.ascontiguousarray(initial, dtype=np.float64),
        directions,
        weights,
        q1,
        mid,
        q3,
        opacity,
        step_size,
        1.3,
        1.0,
        1,
        carrier,
        route,
    )


def _scalar_equilibrium(directions: np.ndarray, v: float, axis: int) -> np.ndarray:
    gamma = 1.0 / np.sqrt(1.0 - v * v)
    return np.asarray((gamma * (1.0 - v * directions[:, axis])) ** -4)


def _is_forbidden(identifier: str) -> bool:
    return identifier in FORBIDDEN_EXACT or identifier.startswith(FORBIDDEN_PREFIXES)


def _python_executable_identifiers(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    identifiers: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            identifiers.add(node.id)
        elif isinstance(node, ast.Attribute):
            identifiers.add(node.attr)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            identifiers.update(
                alias.asname or alias.name.rsplit(".", 1)[-1] for alias in node.names
            )
    return identifiers


def _rust_executable_identifiers(path: Path) -> set[str]:
    source = path.read_text(encoding="utf-8")
    source = re.sub(r"/\*.*?\*/", " ", source, flags=re.DOTALL)
    source = re.sub(r"//[^\n]*", " ", source)
    source = re.sub(r'"(?:\\.|[^"\\])*"', '""', source)
    return set(re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", source))


def test_fixed_grid_route_conflation_mutation_is_detected() -> None:
    """A route dispatcher that aliases raw and AP-corrected output must fail."""

    directions, _ = _angular_grid()
    equilibrium = _scalar_equilibrium(directions, 0.1, 1)
    raw = _trajectory(equilibrium, "scalar_intensity_v1", "fixed_grid_raw_v1")
    corrected = _trajectory(
        equilibrium, "scalar_intensity_v1", "fixed_grid_ap_corrected_v1"
    )
    raw_history = np.asarray(raw["radiation_history"])
    corrected_history = np.asarray(corrected["radiation_history"])
    raw_null = np.asarray(raw["diagnostics"]["equilibrium_null_residual"])
    corrected_null = np.asarray(
        corrected["diagnostics"]["equilibrium_null_residual"]
    )
    assert np.max(raw_null) > 1.0e-8
    assert np.max(corrected_null) < 2.0e-13
    assert not np.array_equal(raw_history[-1], corrected_history[-1])


@pytest.mark.parametrize(
    "carrier,route",
    [
        ("stokes4_silent_projection", "paired_rest_to_normal_reference_v1"),
        ("scalar_intensity_v1", "fixed_grid_claimed_ap_without_correction"),
    ],
)
def test_unsupported_carrier_or_route_fails_closed(carrier: str, route: str) -> None:
    directions, _ = _angular_grid()
    size = len(directions) if carrier == "scalar_intensity_v1" else 4 * len(directions)
    with pytest.raises(_native().RF04CapabilityError) as error:
        _trajectory(np.ones(size), carrier, route)
    assert "RF04_UNSUPPORTED_CAPABILITY" in str(error.value)


def test_forbidden_legacy_substitution_has_no_executable_reference() -> None:
    """Use repository-root paths and executable identifiers, not grep text."""

    adapter = ROOT / "_rustcore/src/python/rf04_typeii.rs"
    public = ROOT / "bianchi/kinetic/__init__.py"
    assert adapter.is_file(), f"missing RF-04 adapter: {adapter}"
    assert public.is_file(), f"missing RF-04 public module: {public}"
    identifiers = _rust_executable_identifiers(adapter) | _python_executable_identifiers(public)
    offenders = sorted(identifier for identifier in identifiers if _is_forbidden(identifier))
    assert offenders == []


def test_polarized_nonphysical_member_fails_closed_without_silent_projection() -> None:
    directions, _ = _angular_grid()
    physical = _physical_polarized_state(directions)
    nonphysical = physical.copy()
    # The first Lebedev node lies on the x axis.  Adding M_xx violates P M P=M.
    nonphysical[0] += 0.25
    with pytest.raises(_native().RF04PhysicalDomainError) as error:
        _trajectory(
            nonphysical,
            "polarized_rank9_v1",
            "paired_rest_to_normal_reference_v1",
            v=0.08,
        )
    assert "RF04_NONPHYSICAL_CARRIER" in str(error.value)


def test_polarized_nonrealizable_member_fails_even_when_exactly_transverse() -> None:
    """Catch a guard that checks only screen transversality and ignores the cone."""

    directions, _ = _angular_grid()
    nonrealizable = _physical_polarized_state(directions)
    # For +x, indices 1 and 2 are the screen diagonal.  Make I=0 while Q!=0;
    # the packed matrix remains exactly transverse but has a negative eigenvalue.
    nonrealizable[1] = 0.5
    nonrealizable[2] = -0.5
    nonrealizable[3:9] = 0.0
    with pytest.raises(_native().RF04PhysicalDomainError) as error:
        _trajectory(
            nonrealizable,
            "polarized_rank9_v1",
            "paired_rest_to_normal_reference_v1",
            v=0.08,
        )
    assert "RF04_NONPHYSICAL_CARRIER" in str(error.value)
