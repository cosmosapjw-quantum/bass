from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "typeii_polarized_runtime.py"


def load_runtime():
    spec = importlib.util.spec_from_file_location("typeii_polarized_runtime_reconciled", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_canonical_xy_circular_state_has_negative_p8():
    rt = load_runtime()
    e = np.array([[0.0, 0.0, 1.0]])
    stokes = np.array([[2.0, 0.0, 0.0, 0.6]])
    packed = rt.stokes_to_pack(e, stokes).reshape(1, 9)
    np.testing.assert_allclose(packed[0, 8], -0.3, rtol=0.0, atol=1e-15)


def test_stokes_roundtrip_for_generic_directions_and_both_v_signs():
    rt = load_runtime()
    e = np.array(
        [
            [0.0, 0.0, 1.0],
            [1.0, 2.0, 3.0],
            [-2.0, 1.0, 0.5],
        ],
        dtype=float,
    )
    e /= np.linalg.norm(e, axis=1)[:, None]
    stokes = np.array(
        [
            [2.0, 0.4, -0.3, 0.2],
            [1.7, -0.2, 0.5, -0.35],
            [3.0, 0.7, 0.1, 0.0],
        ]
    )
    recovered = rt.pack_to_stokes(e, rt.stokes_to_pack(e, stokes)).reshape(-1, 4)
    np.testing.assert_allclose(recovered, stokes, rtol=0.0, atol=2e-14)


def test_pure_v_collision_preserves_v_parity_and_does_not_mix_stokes_sectors():
    rt = load_runtime()
    e, w = rt.lebedev26()
    stokes = np.zeros((len(e), 4))
    stokes[:, 0] = 2.0
    stokes[:, 3] = 0.3 + 0.1 * e[:, 0]
    y = rt.stokes_to_pack(e, stokes)
    c = rt.pack_to_stokes(e, rt.collision(e, w, 0.0, 1, y)).reshape(-1, 4)
    np.testing.assert_allclose(c[:, 1:3], 0.0, rtol=0.0, atol=3e-14)
    # Thomson collision does not reverse the convention-defined handedness.
    assert np.vdot(stokes[:, 3], c[:, 3]).real < 0.0


def test_superseded_positive_p8_embedding_is_detectably_different():
    rt = load_runtime()
    e = np.array([[0.0, 0.0, 1.0]])
    stokes = np.array([[1.0, 0.0, 0.0, 0.8]])
    canonical = rt.stokes_to_pack(e, stokes).reshape(1, 9)[0, 8]
    legacy_positive = +0.5 * stokes[0, 3]
    assert canonical == -legacy_positive
    assert canonical != legacy_positive
