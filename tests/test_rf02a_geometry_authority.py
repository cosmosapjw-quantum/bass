"""RF-02A focused geometry authority and fail-closed detector gates."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from audit import r4_bianchi_constraints as r4
from bianchi.symbolic.geometry_contract import (
    CONVENTION_HASH,
    STATE_SCHEMA_HASH,
    GeometryContractError,
    classify_route,
    validate_geometry_state,
)


def test_bianchi_detector_is_exactly_reduced_and_fail_closed():
    report = r4.compute_report(include_mutation=True)
    assert report["raw_bianchi_identity_vanishes"] is False
    assert report["bianchi_identity_vanishes"] is True
    assert report["bianchi_identity_reduced_vanishes"] is True
    assert report["jacobi_reduction"]["charts_checked"] == [0, 1, 2]
    witness = report["mutation_witness"]["ndot_H_sign_flip"]
    assert witness["reduced_vanishes"] is False
    assert witness["max_nonzero_component"] > 0


def test_detector_report_binds_convention_and_state_schema():
    report = r4.compute_report()
    assert report["convention_hash"] == CONVENTION_HASH
    assert report["state_schema_hash"] == STATE_SCHEMA_HASH
    assert report["manifest_generator"]["version"] == "rf02a-1.0"
    assert report["route_inventory"]["q.group.classify"] == "native_required"


def test_geometry_state_rejects_unknown_and_tilted_routes():
    with pytest.raises(GeometryContractError, match="unknown Bianchi type"):
        validate_geometry_state(np.zeros((3, 3)), np.zeros(3), type_name="X")
    with pytest.raises(GeometryContractError, match="tilted"):
        validate_geometry_state(
            np.zeros((3, 3)), np.zeros(3), type_name="I", tilted=True
        )
    assert classify_route("q.group.curvature") == "native_required"
    with pytest.raises(GeometryContractError, match="unsupported route"):
        classify_route("q.group.not_a_route")


def test_geometry_state_validates_symmetry_jacobi_and_finiteness():
    n = np.diag([0.0, 2.0, -1.0])
    a = np.array([1.0, 0.0, 0.0])
    assert validate_geometry_state(n, a, type_name="VI_h")["type_name"] == "VI_h"
    with pytest.raises(GeometryContractError, match="symmetric"):
        validate_geometry_state(np.array([[0.0, 1.0, 0.0], [0.0, 0.0, 0.0], [0, 0, 0]]), a)
    with pytest.raises(GeometryContractError, match="Jacobi"):
        validate_geometry_state(np.eye(3), a)
    with pytest.raises(GeometryContractError, match="finite"):
        validate_geometry_state(np.full((3, 3), np.nan), np.zeros(3))


def test_run_all_contains_fail_closed_r4_gate_and_generator_identity():
    text = Path("audit/run_all.py").read_text()
    assert "bianchi_identity_reduced_vanishes" in text
    assert "n_failed" in text and "return 1 if failed else 0" in text
    manifest = json.loads(Path("audit/manifest.json").read_text())
    assert manifest["version"] == "1.5"
    assert manifest["generator"]["version"] == "rf02a-1.0"


def test_rf02a_ci_selects_all_geometry_routes_without_full_suite():
    workflow = Path(".github/workflows/rf02a-geometry.yml").read_text()
    for node in (
        "tests/test_rf02a_geometry_authority.py",
        "tests/test_q1_group.py",
        "tests/test_rf00_route_inventory.py",
    ):
        assert node in workflow
    assert "pytest -q" in workflow
    assert "tests/" in workflow
    assert "test_1849" not in workflow
