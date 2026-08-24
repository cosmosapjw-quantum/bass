"""Focused stdlib gate for the independent cold-electron test field.

Run directly so this narrow gate does not require the repository's optional
JAX/Rust/pytest stack::

    python tests/test_electron_test_field.py

The module under test is loaded by file path for the same reason.  Production
imports continue to use ``bianchi.q.electron``.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import types
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "bianchi" / "q" / "electron.py"
if not MODULE_PATH.is_file():
    raise AssertionError(
        "RED: bianchi.q.electron state/frame adapter has not been implemented"
    )


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _load_without_optional_stack():
    """Load only NumPy seams, restoring ``sys.modules`` after the fallback."""
    saved = {
        key: value for key, value in sys.modules.items()
        if key == "bianchi" or key.startswith("bianchi.")
    }
    for key in list(saved):
        sys.modules.pop(key, None)
    try:
        bianchi_pkg = types.ModuleType("bianchi")
        bianchi_pkg.__path__ = [str(ROOT / "bianchi")]
        q_pkg = types.ModuleType("bianchi.q")
        q_pkg.__path__ = [str(ROOT / "bianchi" / "q")]
        sys.modules["bianchi"] = bianchi_pkg
        sys.modules["bianchi.q"] = q_pkg

        comoving_stub = types.ModuleType("bianchi.q.comoving")
        comoving_stub.collide_log = lambda *args, **kwargs: (_ for _ in ()).throw(
            RuntimeError("collision kernel is outside this focused frame gate")
        )
        sys.modules["bianchi.q.comoving"] = comoving_stub

        coupled_stub = types.ModuleType("bianchi.q.coupled")
        coupled_stub.mat3 = lambda value: np.asarray(value, float).reshape(3, 3)
        sys.modules["bianchi.q.coupled"] = coupled_stub

        polarization = _load(
            "bianchi.q.polarization", ROOT / "bianchi" / "q" / "polarization.py"
        )
        q_pkg.polarization = polarization
        q_pkg.polstate = _load(
            "bianchi.q.polstate", ROOT / "bianchi" / "q" / "polstate.py"
        )
        q_pkg.boost = _load("bianchi.q.boost", ROOT / "bianchi" / "q" / "boost.py")
        return _load("bianchi.q.electron", MODULE_PATH)
    finally:
        for key in [
            item for item in list(sys.modules)
            if item == "bianchi" or item.startswith("bianchi.")
        ]:
            sys.modules.pop(key, None)
        sys.modules.update(saved)


try:
    from bianchi.q import electron as EF
except ModuleNotFoundError as exc:
    # The scratch host intentionally lacks the project's optional JAX/Rust
    # stack.  A real package error other than those dependencies must surface.
    if exc.name not in {
        "bianchi", "jax", "jaxlib", "equinox", "diffrax", "bianchi_rustcore"
    }:
        raise
    EF = _load_without_optional_stack()
ORACLE = _load(
    "_electron_frame_oracle", ROOT / "audit" / "electron_frame_adapter.py"
)


ETA = np.diag([-1.0, 1.0, 1.0, 1.0])


def _directions():
    raw = np.array([[0.2, -0.7, 0.4], [-0.5, 0.3, 0.8], [0.1, 0.9, -0.2]])
    return raw / np.linalg.norm(raw, axis=1)[:, None]


def _coherency_shapes(e):
    rng = np.random.default_rng(20260823)
    out = []
    for direction in e:
        projector = np.eye(3) - np.outer(direction, direction)
        seed = rng.standard_normal((3, 3))
        carrier = projector @ seed @ seed.T @ projector
        out.append(carrier / np.trace(carrier))
    return np.asarray(out)


class ElectronStateTests(unittest.TestCase):
    def test_independent_state_and_exact_comoving_restriction(self):
        beta_f = np.array([0.11, -0.07, 0.03])
        independent = EF.ElectronTestField.independent(
            n_e_free=2.5e6, beta_normal=[-0.04, 0.09, 0.02]
        )
        comoving = EF.ElectronTestField.comoving(
            n_e_free=7.0e5, beta_fluid=beta_f
        )

        self.assertEqual(independent.closure, "independent")
        self.assertEqual(comoving.closure, "comoving-electron")
        self.assertTrue(comoving.is_comoving_with(beta_f))
        self.assertTrue(np.array_equal(np.asarray(comoving.beta_normal), beta_f))
        self.assertEqual(comoving.relative_gamma(beta_f), 1.0)
        self.assertGreater(independent.relative_gamma(beta_f), 1.0)
        # Velocity closure does not invent a density/composition closure.
        self.assertEqual(comoving.n_e_free, 7.0e5)

    def test_state_rejects_invalid_density_and_velocity(self):
        bad = [
            dict(n_e_free=-1.0, beta_normal=[0.0, 0.0, 0.0]),
            dict(n_e_free=np.nan, beta_normal=[0.0, 0.0, 0.0]),
            dict(n_e_free=1.0, beta_normal=[1.0, 0.0, 0.0]),
            dict(n_e_free=1.0, beta_normal=[0.0, np.inf, 0.0]),
            dict(n_e_free=1.0, beta_normal=[0.0, 0.0]),
        ]
        for kwargs in bad:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                EF.ElectronTestField.independent(**kwargs)

    def test_comoving_label_cannot_be_forged_by_public_constructor(self):
        with self.assertRaises((TypeError, ValueError)):
            EF.ElectronTestField(
                1.0, (0.4, 0.0, 0.0), "comoving-electron"
            )

    def test_comoving_adapter_rejects_a_different_fluid_representative(self):
        beta_f = np.array([0.2, -0.1, 0.05])
        wrong = np.zeros(3)
        state = EF.ElectronTestField.comoving(1.0, beta_f)
        direction = _directions()
        carrier = _coherency_shapes(direction)
        calls = [
            lambda: state.relative_gamma(wrong),
            lambda: state.fluid_to_electron_matrix(wrong),
            lambda: state.electron_to_fluid_matrix(wrong),
            lambda: state.fluid_to_electron_photon(np.ones(3), direction, wrong),
            lambda: state.electron_to_fluid_photon(np.ones(3), direction, wrong),
            lambda: state.fluid_to_electron_polarization(carrier, direction, wrong),
            lambda: state.electron_to_fluid_polarization(carrier, direction, wrong),
            lambda: state.fluid_to_electron_mode_a(
                np.zeros(3), np.zeros(3), direction, wrong
            ),
            lambda: state.electron_to_fluid_mode_a(
                np.zeros(3), np.zeros(3), direction, wrong
            ),
        ]
        for call in calls:
            with self.subTest(call=call), self.assertRaises(ValueError):
                call()

    def test_explicit_c_four_velocity_normalization(self):
        state = EF.ElectronTestField.independent(1.0, [0.31, -0.17, 0.08])
        normalized = state.normalized_four_velocity()
        physical = state.four_velocity()
        self.assertAlmostEqual(float(normalized @ ETA @ normalized), -1.0, places=14)
        residual = float(physical @ ETA @ physical + EF.C_LIGHT_M_S**2)
        self.assertLessEqual(abs(residual) / EF.C_LIGHT_M_S**2, 8e-16)
        self.assertTrue(np.array_equal(physical, EF.C_LIGHT_M_S * normalized))

        rebuilt = EF.ElectronTestField.from_physical_velocity(
            1.0, state.physical_velocity_normal_m_s, c_m_s=EF.C_LIGHT_M_S
        )
        self.assertTrue(np.array_equal(rebuilt.beta_normal, state.beta_normal))

    def test_authority_boundary_is_machine_readable(self):
        state = EF.ElectronTestField.independent(0.0, [0.4, -0.1, 0.2])
        metadata = state.authority_metadata()
        self.assertEqual(metadata["model"], "H2_WITH_COMOVING_RESTRICTION")
        self.assertTrue(metadata["test_field"])
        self.assertTrue(metadata["cold_electrons"])
        self.assertFalse(metadata["background_backreaction"])
        self.assertFalse(metadata["canonical_receipt_complete"])
        self.assertFalse(metadata["authority_row_promoted"])
        self.assertEqual(state.density_unit, "m^-3")
        self.assertEqual(metadata["density_unit"], "m^-3")
        self.assertEqual(state.n_e_free, 0.0)


class ElectronFrameTests(unittest.TestCase):
    def setUp(self):
        self.beta_f = np.array([0.23, -0.04, 0.07])
        self.state = EF.ElectronTestField.independent(
            3.0e6, [-0.06, 0.19, 0.11]
        )

    def test_noncollinear_frame_composition_is_lorentz_and_invertible(self):
        forward = EF.frame_matrix(self.beta_f, self.state.beta_normal)
        inverse = EF.frame_matrix(self.state.beta_normal, self.beta_f)
        self.assertLess(np.max(np.abs(forward.T @ ETA @ forward - ETA)), 2e-14)
        self.assertLess(np.max(np.abs(inverse @ forward - np.eye(4))), 2e-14)
        # A pair of non-collinear boosts is not the naive pure boost v_e-v_f.
        naive = EF.lorentz_boost(np.asarray(self.state.beta_normal) - self.beta_f)
        self.assertGreater(np.max(np.abs(forward - naive)), 1e-3)

    def test_zero_source_velocity_is_existing_single_boost_path(self):
        direction = _directions()
        energy = np.array([0.8, 1.3, 4.2])
        carrier = _coherency_shapes(direction)
        velocity = np.asarray(self.state.beta_normal)

        expected_d, expected_direction = EF.doppler(direction, velocity)
        got_energy, got_direction, got_d = EF.transform_photon(
            energy, direction, np.zeros(3), velocity
        )
        self.assertTrue(np.array_equal(got_d, expected_d))
        self.assertTrue(np.array_equal(got_direction, expected_direction))
        self.assertTrue(np.array_equal(got_energy, energy * expected_d))

        expected_shape, expected_e, expected_pd = EF.boost_shape(
            carrier, velocity, direction
        )
        got_shape, got_e, got_pd = EF.transform_polarization_shape(
            carrier, direction, np.zeros(3), velocity
        )
        self.assertTrue(np.array_equal(got_shape, expected_shape))
        self.assertTrue(np.array_equal(got_e, expected_e))
        self.assertTrue(np.array_equal(got_pd, expected_pd))

    def test_photon_four_momentum_roundtrip_and_nullness(self):
        energy = np.array([1.7e-22, 3.2e-21, 8.1e-20])
        direction = _directions()
        ep, np_dir, doppler = self.state.fluid_to_electron_photon(
            energy, direction, self.beta_f
        )
        eb, nb, inverse_doppler = self.state.electron_to_fluid_photon(
            ep, np_dir, self.beta_f
        )

        self.assertTrue(np.all(ep > 0.0))
        self.assertTrue(np.all(doppler > 0.0))
        self.assertLess(np.max(np.abs(np.linalg.norm(np_dir, axis=1) - 1.0)), 4e-15)
        self.assertLess(np.max(np.abs(eb / energy - 1.0)), 5e-15)
        self.assertLess(np.max(np.abs(nb - direction)), 5e-15)
        self.assertLess(np.max(np.abs(doppler * inverse_doppler - 1.0)), 5e-15)
        p0 = ep / EF.C_LIGHT_M_S
        p = p0[:, None] * np_dir
        null_residual = -p0**2 + np.einsum("ai,ai->a", p, p)
        scale = np.maximum(p0**2, np.finfo(float).tiny)
        self.assertLess(np.max(np.abs(null_residual) / scale), 8e-15)

    def test_polarization_screen_psd_and_roundtrip(self):
        direction = _directions()
        carrier = _coherency_shapes(direction)
        transformed, ep, _ = self.state.fluid_to_electron_polarization(
            carrier, direction, self.beta_f
        )
        recovered, eb, _ = self.state.electron_to_fluid_polarization(
            transformed, ep, self.beta_f
        )

        leak = np.einsum("aij,aj->ai", transformed, ep)
        self.assertLess(np.max(np.abs(leak)), 5e-15)
        self.assertLess(np.max(np.abs(np.trace(transformed, axis1=1, axis2=2) - 1.0)), 5e-15)
        self.assertGreaterEqual(np.min(np.linalg.eigvalsh(transformed)), -5e-15)
        self.assertLess(np.max(np.abs(eb - direction)), 5e-15)
        self.assertLess(np.max(np.abs(recovered - carrier)), 8e-15)

    def test_circular_polarization_antisymmetric_carrier_roundtrip(self):
        direction = _directions()
        carrier = []
        for e in direction:
            projector = np.eye(3) - np.outer(e, e)
            cross = np.array([
                [0.0, -e[2], e[1]],
                [e[2], 0.0, -e[0]],
                [-e[1], e[0], 0.0],
            ])
            carrier.append(0.5 * projector + 0.17 * cross)
        carrier = np.asarray(carrier)
        transformed, ep, _ = self.state.fluid_to_electron_polarization(
            carrier, direction, self.beta_f
        )
        recovered, eb, _ = self.state.electron_to_fluid_polarization(
            transformed, ep, self.beta_f
        )
        self.assertLess(np.max(np.abs(recovered - carrier)), 8e-15)
        self.assertLess(np.max(np.abs(eb - direction)), 5e-15)
        self.assertLess(
            np.max(np.abs(np.linalg.norm(
                transformed - transformed.swapaxes(1, 2), axis=(1, 2)
            ) - np.linalg.norm(
                carrier - carrier.swapaxes(1, 2), axis=(1, 2)
            ))),
            5e-15,
        )

    def test_mode_a_adapter_and_comoving_path(self):
        e = _directions()
        lw = np.log(np.array([0.2, 0.3, 0.5]))
        lG = np.array([-1.2, 0.4, 2.1])
        lw_e, lG_e, e_e, doppler = self.state.fluid_to_electron_mode_a(
            lw, lG, e, self.beta_f
        )
        lw_b, lG_b, e_b, _ = self.state.electron_to_fluid_mode_a(
            lw_e, lG_e, e_e, self.beta_f
        )
        self.assertLess(np.max(np.abs(lw_b - lw)), 5e-15)
        self.assertLess(np.max(np.abs(lG_b - lG)), 5e-15)
        self.assertLess(np.max(np.abs(e_b - e)), 5e-15)
        self.assertTrue(np.all(doppler > 0.0))

        comoving = EF.ElectronTestField.comoving(9.0e5, self.beta_f)
        lw_c, lG_c, e_c, d_c = comoving.fluid_to_electron_mode_a(
            lw, lG, e, self.beta_f
        )
        self.assertTrue(np.array_equal(lw_c, lw))
        self.assertTrue(np.array_equal(lG_c, lG))
        self.assertTrue(np.array_equal(e_c, e))
        self.assertTrue(np.array_equal(d_c, np.ones_like(d_c)))

        energy = np.array([1.0, 2.0, 3.0])
        energy_c, photon_e_c, photon_d_c = comoving.fluid_to_electron_photon(
            energy, e, self.beta_f
        )
        carrier = _coherency_shapes(e)
        carrier_c, carrier_e_c, carrier_d_c = \
            comoving.fluid_to_electron_polarization(carrier, e, self.beta_f)
        self.assertTrue(np.array_equal(energy_c, energy))
        self.assertTrue(np.array_equal(photon_e_c, e))
        self.assertTrue(np.array_equal(photon_d_c, np.ones(3)))
        self.assertTrue(np.array_equal(carrier_c, carrier))
        self.assertTrue(np.array_equal(carrier_e_c, e))
        self.assertTrue(np.array_equal(carrier_d_c, np.ones(3)))

    def test_hostile_randomized_direct_four_vector_oracle(self):
        result = ORACLE.run(EF, n=400, seed=20260823, vmax=0.85)
        for name in (
            "metric",
            "inverse",
            "gamma",
            "photon_energy",
            "photon_direction",
            "photon_roundtrip",
            "polarization",
            "polarization_roundtrip",
            "screen_leak",
            "trace",
        ):
            self.assertLess(result[name], 2e-12, (name, result))
        # Confirms the randomized set actually exercised non-collinear rotation.
        self.assertGreater(result["wigner_spatial_asymmetry"], 1e-3, result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
