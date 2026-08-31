"""RF04-POL-SCHEMA-01 public-boundary RED.

The test imports the retained scalar-v1 native build successfully, then fails
on the three deliberately unregistered v2 symbols.  This distinguishes a
missing polarized capability from an import/packaging failure.
"""

from __future__ import annotations

import numpy as np
import pytest

import bianchi_rustcore


V2_SYMBOLS = (
    "rf04_typeii_polarized_execution_identity_v2",
    "rf04_typeii_polarized_trajectory_v2",
    "rf04_typeii_polarized_batch_v2",
)


def _v1_request() -> tuple[object, ...]:
    directions = np.array(
        [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
        dtype=np.float64,
    )
    return (
        np.ones(3, dtype=np.float64),
        directions,
        np.ones(3, dtype=np.float64),
        np.array([[0.2, 0.04, 0.03, 0.7, 0.08]], dtype=np.float64),
        np.array([[0.21, 0.035, 0.032, 0.69, 0.085]], dtype=np.float64),
        np.array([[0.22, 0.03, 0.034, 0.68, 0.09]], dtype=np.float64),
        np.array([0.2], dtype=np.float64),
        np.array([1.0e-3], dtype=np.float64),
        1.3,
        1.0,
        1,
        "polarized_rank9_v1",
        "fixed_grid_raw_v1",
    )


def test_rf04_polarized_v2_native_symbols_exist() -> None:
    missing = [name for name in V2_SYMBOLS if not hasattr(bianchi_rustcore, name)]
    assert not missing, f"missing RF-04 polarized v2 native symbols: {missing}"


def test_rf04_polarized_v2_v1_route_remains_fail_closed() -> None:
    assert hasattr(bianchi_rustcore, "rf04_typeii_trajectory_v1"), (
        "retained scalar-v1 native build is unavailable; this would be an "
        "import/packaging failure rather than the required capability RED"
    )
    with pytest.raises(bianchi_rustcore.RF04CapabilityError, match="RF04_UNSUPPORTED_CAPABILITY"):
        bianchi_rustcore.rf04_typeii_trajectory_v1(*_v1_request())
