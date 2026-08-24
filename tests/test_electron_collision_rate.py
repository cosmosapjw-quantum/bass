"""Focused gate for cold-electron relative-flux and prescribed scheduling.

Run directly so this authority slice does not require the optional JAX/Rust
stack::

    python tests/test_electron_collision_rate.py

Each expectation is derived from a literal four-vector or cgs calculation,
not from the production rate builder.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import types
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RATE_PATH = ROOT / "bianchi" / "q" / "electron_rate.py"
if not RATE_PATH.is_file():
    raise AssertionError(
        "RED: bianchi.q.electron_rate collision authority is not implemented"
    )


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _load_without_optional_stack():
    """Load the exact NumPy seams and the legacy constant owner in isolation."""
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
        thermo_pkg = types.ModuleType("bianchi.thermo")
        thermo_pkg.__path__ = [str(ROOT / "bianchi" / "thermo")]
        sys.modules.update({
            "bianchi": bianchi_pkg,
            "bianchi.q": q_pkg,
            "bianchi.thermo": thermo_pkg,
        })

        # The production rate module imports these existing authorities.  The
        # focused loader supplies only their exact declared values; the normal
        # installed-package gate exercises the real history module later.
        history = types.ModuleType("bianchi.thermo.history_api")
        history.SIGMA_T_CM2 = 6.6524587e-25
        history.C_CM_S = 2.99792458e10
        sys.modules["bianchi.thermo.history_api"] = history

        comoving = types.ModuleType("bianchi.q.comoving")
        comoving.collide_log = lambda *args, **kwargs: (_ for _ in ()).throw(
            RuntimeError("collision kernel is outside this focused rate gate")
        )
        coupled = types.ModuleType("bianchi.q.coupled")
        coupled.mat3 = lambda value: np.asarray(value, float).reshape(3, 3)
        sys.modules["bianchi.q.comoving"] = comoving
        sys.modules["bianchi.q.coupled"] = coupled

        q_pkg.polarization = _load(
            "bianchi.q.polarization", ROOT / "bianchi" / "q" / "polarization.py"
        )
        q_pkg.polstate = _load(
            "bianchi.q.polstate", ROOT / "bianchi" / "q" / "polstate.py"
        )
        q_pkg.boost = _load(
            "bianchi.q.boost", ROOT / "bianchi" / "q" / "boost.py"
        )
        q_pkg.electron = _load(
            "bianchi.q.electron", ROOT / "bianchi" / "q" / "electron.py"
        )
        return q_pkg.electron, _load("bianchi.q.electron_rate", RATE_PATH)
    finally:
        for key in [
            item for item in list(sys.modules)
            if item == "bianchi" or item.startswith("bianchi.")
        ]:
            sys.modules.pop(key, None)
        sys.modules.update(saved)


try:
    from bianchi.q import electron as EF
    from bianchi.q import electron_rate as ER
except ModuleNotFoundError as exc:
    if exc.name not in {
        "bianchi", "jax", "jaxlib", "equinox", "diffrax", "bianchi_rustcore"
    }:
        raise
    EF, ER = _load_without_optional_stack()


ETA = np.diag([-1.0, 1.0, 1.0, 1.0])
PROVENANCE = ER.ElectronScheduleProvenance(
    source_id="unit-test:electron-current-table",
    source_sha256="a" * 64,
)


def _unit(value):
    value = np.asarray(value, float)
    return value / np.linalg.norm(value)


class ElectronCollisionRateTests(unittest.TestCase):
    def test_noncollinear_rate_matches_covariant_scalar_and_rejects_mutations(self):
        beta_f = np.array([0.23, -0.04, 0.07])
        electron = EF.ElectronTestField.independent(
            3.2e6, [-0.16, 0.21, 0.08]
        )
        direction_f = _unit([0.37, -0.81, 0.22])
        context = ER.ElectronCollisionContext(electron)

        got = context.rate_per_fluid_time_s(direction_f, beta_f)

        # Independent literal oracle: p_f=(1,e_f), transform p to the normal
        # tetrad, then D=-U_e.p_normal for E_f=1 and (-,+,+,+).
        p_f = np.concatenate(([1.0], direction_f))
        p_normal = EF.frame_matrix(beta_f, np.zeros(3)) @ p_f
        u_e = EF.normalized_four_velocity(electron.beta_normal)
        doppler_dot = -float(u_e @ ETA @ p_normal)
        base = electron.n_e_free * ER.SIGMA_T_M2 * electron.c_m_s
        expected = base * doppler_dot

        self.assertGreater(doppler_dot, 0.0)
        self.assertGreater(abs(doppler_dot - 1.0), 0.1)
        self.assertLess(abs(got / expected - 1.0), 3e-15)
        # Missing-D and double-D mutations must not match the public result.
        self.assertGreater(abs(got / base - 1.0), 0.1)
        self.assertGreater(abs(got / (base * doppler_dot**2) - 1.0), 0.1)

        # The optical-depth scalar is unchanged under a further global boost.
        probe = EF.lorentz_boost([0.19, -0.11, 0.05])
        invariant_before = float(u_e @ ETA @ p_normal)
        invariant_after = float((probe @ u_e) @ ETA @ (probe @ p_normal))
        self.assertLess(abs(invariant_after - invariant_before), 2e-15)

    def test_comoving_fluid_limit_and_normal_hubble_time_are_distinct(self):
        beta_f = np.array([0.17, -0.08, 0.03])
        density = 7.5e5
        electron = EF.ElectronTestField.comoving(density, beta_f)
        context = ER.ElectronCollisionContext(electron)
        directions = np.asarray([
            _unit([1.0, 2.0, -0.5]),
            _unit([-0.3, 0.4, 0.8]),
        ])
        base = density * ER.SIGMA_T_M2 * electron.c_m_s

        rate_fluid_s = context.rate_per_fluid_time_s(directions, beta_f)
        self.assertTrue(np.array_equal(rate_fluid_s, np.full(2, base)))

        # The Q solver's Hubble time is built from normal-congruence time.
        # Even when u_e=u_fluid, that normal-time opacity is anisotropic for a
        # tilted fluid and must not be replaced by rate_fluid_s/H_normal.
        directions_normal = directions
        gamma = 1.0 / np.sqrt(1.0 - float(beta_f @ beta_f))
        expected_normal = base * gamma * (1.0 - directions_normal @ beta_f)
        rate_normal_s = context.rate_per_normal_time_s(directions_normal)
        self.assertLess(np.max(np.abs(
            rate_normal_s / expected_normal - 1.0
        )), 3e-15)
        self.assertGreater(np.max(np.abs(rate_normal_s / base - 1.0)), 1e-3)

        H_t = 2.3e-14
        self.assertTrue(np.array_equal(
            context.rate_per_normal_hubble_time(directions_normal, H_t),
            rate_normal_s / H_t,
        ))
        for bad_H in [0.0, -1.0, np.inf, np.nan]:
            with self.subTest(H_t=bad_H), self.assertRaises(ValueError):
                context.rate_per_normal_hubble_time(directions_normal, bad_H)

    def test_vacuum_rate_is_exact_representative_independent_noop(self):
        directions = np.asarray([
            _unit([1.0, 0.1, -0.2]),
            _unit([-0.4, 0.7, 0.3]),
        ])
        beta_f = np.array([0.2, 0.0, -0.1])
        states = [
            EF.ElectronTestField.independent(0.0, [0.0, 0.0, 0.0]),
            EF.ElectronTestField.independent(0.0, [0.8, -0.1, 0.2]),
            # Even a vacuum object carrying the old comoving representative
            # cannot make the collision rate depend on that representative.
            EF.ElectronTestField.comoving(0.0, [-0.3, 0.1, 0.2]),
        ]
        for state in states:
            with self.subTest(beta=state.beta_normal, closure=state.closure):
                context = ER.ElectronCollisionContext(state)
                rate = context.rate_per_fluid_time_s(directions, beta_f)
                self.assertTrue(np.array_equal(rate, np.zeros(2)))
                with self.assertRaises(ER.VacuumElectronFrameError):
                    context.relative_flux_factor(directions, beta_f)

    def test_si_and_legacy_cgs_rate_paths_agree(self):
        density_cm3 = 2.5e-4
        density_m3 = ER.density_cm3_to_m3(density_cm3)
        self.assertEqual(density_m3, density_cm3 * 1.0e6)
        self.assertEqual(ER.density_m3_to_cm3(density_m3), density_cm3)

        beta_f = np.array([0.04, -0.02, 0.01])
        electron = EF.ElectronTestField.comoving(density_m3, beta_f)
        got_si = ER.ElectronCollisionContext(electron).rate_per_fluid_time_s(
            _unit([0.2, 0.6, -0.3]), beta_f
        )
        expected_cgs = density_cm3 * ER.SIGMA_T_CM2 * ER.C_CM_S
        self.assertLess(abs(got_si / expected_cgs - 1.0), 3e-15)

    def test_direction_and_context_domain_fail_early(self):
        electron = EF.ElectronTestField.independent(1.0, [0.1, 0.0, 0.0])
        context = ER.ElectronCollisionContext(electron)
        for bad_direction in [[1.0, 1.0, 0.0], [1.0, 0.0], [np.nan, 0.0, 1.0]]:
            with self.subTest(direction=bad_direction), self.assertRaises(ValueError):
                context.rate_per_fluid_time_s(bad_direction, [0.0, 0.0, 0.0])
        with self.assertRaises(TypeError):
            ER.ElectronCollisionContext(object())

    def test_hostile_randomized_observer_chain_and_covariant_oracle(self):
        rng = np.random.default_rng(2026082317)
        maxima = {"fluid": 0.0, "normal": 0.0, "chain": 0.0}
        for _ in range(800):
            def beta():
                axis = _unit(rng.normal(size=3))
                return axis * rng.uniform(0.0, 0.9)

            beta_f = beta()
            beta_e = beta()
            direction_f = _unit(rng.normal(size=3))
            density = 10.0 ** rng.uniform(-2.0, 12.0)
            electron = EF.ElectronTestField.independent(density, beta_e)
            context = ER.ElectronCollisionContext(electron)
            base = density * ER.SIGMA_T_M2 * electron.c_m_s

            p_f = np.concatenate(([1.0], direction_f))
            p_n = EF.frame_matrix(beta_f, np.zeros(3)) @ p_f
            u_e = EF.normalized_four_velocity(beta_e)
            d_fluid = -float(u_e @ ETA @ p_n)
            got_fluid = context.rate_per_fluid_time_s(direction_f, beta_f) / base
            maxima["fluid"] = max(maxima["fluid"], abs(got_fluid / d_fluid - 1.0))

            direction_n = p_n[1:] / p_n[0]
            d_normal = -float(u_e @ ETA @ np.concatenate(([1.0], direction_n)))
            got_normal = context.rate_per_normal_time_s(direction_n) / base
            maxima["normal"] = max(maxima["normal"], abs(got_normal / d_normal - 1.0))

            # dt_f/dt_n=E_f/E_n, so r_n=r_f*(E_f/E_n).
            chain = got_fluid / float(p_n[0])
            maxima["chain"] = max(maxima["chain"], abs(chain / got_normal - 1.0))

        self.assertLess(max(maxima.values()), 3e-14, maxima)

    def test_parallel_head_on_transverse_normal_time_oracle(self):
        electron = EF.ElectronTestField.independent(1.0, [0.6, 0.0, 0.0])
        context = ER.ElectronCollisionContext(electron)
        base = ER.SIGMA_T_M2 * electron.c_m_s
        directions = np.asarray([[1.0, 0.0, 0.0], [-1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
        got = context.rate_per_normal_time_s(directions) / base
        self.assertLess(np.max(np.abs(got - np.array([0.5, 2.0, 1.25]))), 3e-15)


class ElectronScheduleTests(unittest.TestCase):
    def test_number_current_interpolation_quotients_vacuum_velocity(self):
        tau = [0.0, 1.0, 2.0, 3.0]
        density = [0.0, 4.0e6, 7.0e6, 0.0]
        beta = [
            [0.7, 0.0, 0.0],       # irrelevant vacuum representative
            [0.2, -0.1, 0.05],
            [-0.15, 0.22, 0.03],
            [-0.6, 0.1, 0.0],      # irrelevant vacuum representative
        ]
        schedule = ER.PrescribedIndependentElectronSchedule(
            tau, density, beta, provenance=PROVENANCE
        )

        at_vacuum = schedule.at(0.0)
        self.assertEqual(at_vacuum.n_e_free, 0.0)
        self.assertEqual(at_vacuum.beta_normal, (0.0, 0.0, 0.0))

        # Interpolation from zero current to one timelike current retains the
        # positive node's velocity; the arbitrary vacuum beta cannot leak in.
        at_half = schedule.at(0.5)
        self.assertLess(np.max(np.abs(
            np.asarray(at_half.beta_normal) - np.asarray(beta[1])
        )), 3e-15)
        self.assertLess(abs(at_half.n_e_free / (0.5 * density[1]) - 1.0), 3e-15)

        mixed = schedule.at(1.5)
        self.assertGreater(mixed.n_e_free, 0.0)
        self.assertLess(np.dot(mixed.beta_normal, mixed.beta_normal), 1.0)
        self.assertEqual(schedule.support, (0.0, 3.0))
        self.assertEqual(len(schedule.payload_sha256), 64)
        self.assertEqual(schedule.provenance, PROVENANCE)

        changed = ER.PrescribedIndependentElectronSchedule(
            tau, [0.0, 4.0e6, 7.1e6, 0.0], beta, provenance=PROVENANCE
        )
        self.assertNotEqual(schedule.payload_sha256, changed.payload_sha256)

        equivalent_vacuum_representatives = ER.PrescribedIndependentElectronSchedule(
            tau,
            density,
            [[-0.2, 0.3, 0.1], beta[1], beta[2], [0.1, -0.7, 0.2]],
            provenance=PROVENANCE,
        )
        self.assertEqual(
            schedule.payload_sha256,
            equivalent_vacuum_representatives.payload_sha256,
            "vacuum velocity representatives must be quotiented from payload identity",
        )

        signed_zero_equivalent = ER.PrescribedIndependentElectronSchedule(
            tau,
            [-0.0, *density[1:-1], -0.0],
            beta,
            provenance=PROVENANCE,
        )
        self.assertEqual(
            schedule.payload_sha256,
            signed_zero_equivalent.payload_sha256,
            "signed-zero vacuum densities must have one canonical payload identity",
        )

    def test_legacy_schedule_conversion_and_support_guards(self):
        tau = [0.0, 1.0]
        density_cm3 = [1.0e-4, 2.0e-4]
        beta = [[0.0, 0.0, 0.0], [0.1, 0.0, 0.0]]
        schedule = ER.PrescribedIndependentElectronSchedule.from_proper_cm3(
            tau, density_cm3, beta, provenance=PROVENANCE
        )
        self.assertEqual(schedule.input_density_unit, "proper_cm^-3->m^-3")
        self.assertEqual(schedule.at(0.0).n_e_free, 100.0)
        self.assertEqual(schedule.validate_span(0.0, 1.0), (0.0, 1.0))
        for outside in [-1e-12, 1.0 + 1e-12]:
            with self.subTest(tau=outside), self.assertRaises(ValueError):
                schedule.at(outside)
        with self.assertRaises(ValueError):
            schedule.validate_span(-0.1, 0.9)

    def test_schedule_rejects_ambiguous_or_malformed_authority(self):
        with self.assertRaises(ValueError):
            ER.ElectronScheduleProvenance("", "a" * 64)
        with self.assertRaises(ValueError):
            ER.ElectronScheduleProvenance("source", "not-a-sha256")

        bad_cases = [
            ([0.0], [1.0], [[0.0, 0.0, 0.0]]),
            ([0.0, 0.0], [1.0, 1.0], [[0.0, 0.0, 0.0]] * 2),
            ([0.0, 1.0], [1.0, -1.0], [[0.0, 0.0, 0.0]] * 2),
            ([0.0, 1.0], [1.0, 1.0], [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]]),
        ]
        for tau, density, beta in bad_cases:
            with self.subTest(tau=tau, density=density, beta=beta):
                with self.assertRaises(ValueError):
                    ER.PrescribedIndependentElectronSchedule(
                        tau, density, beta, provenance=PROVENANCE
                    )

        with self.assertRaises(ValueError):
            ER.density_cm3_to_m3(np.finfo(float).max)

    def test_schedule_hostile_current_semantics_and_immutable_inputs(self):
        tau = np.array([0.0, 1.0])
        density = np.array([3.0e6, 3.0e6])
        beta = np.array([[0.8, 0.0, 0.0], [-0.8, 0.0, 0.0]])
        schedule = ER.PrescribedIndependentElectronSchedule(
            tau, density, beta, provenance=PROVENANCE
        )
        expected_hash = schedule.payload_sha256
        tau[:] = [5.0, 6.0]
        density[:] = 0.0
        beta[:] = 0.0
        self.assertEqual(schedule.support, (0.0, 1.0))
        self.assertEqual(schedule.payload_sha256, expected_hash)

        # Frozen number-current interpolation: counter-streaming equal proper
        # densities reconstruct gamma*n at the midpoint, not a linear density.
        midpoint = schedule.at(0.5)
        self.assertEqual(midpoint.beta_normal, (0.0, 0.0, 0.0))
        self.assertLess(abs(midpoint.n_e_free / 3.0e6 - 5.0 / 3.0), 3e-15)

        with self.assertRaises(ValueError):
            schedule.at(np.nextafter(0.0, -np.inf))
        with self.assertRaises(ValueError):
            schedule.at(np.nextafter(1.0, np.inf))

        near_light = 1.0 - 1.0e-12
        near_null = ER.PrescribedIndependentElectronSchedule(
            [0.0, 1.0], [2.0, 2.0],
            [[near_light, 0.0, 0.0], [near_light, 0.0, 0.0]],
            provenance=PROVENANCE,
        ).at(0.5)
        self.assertGreater(near_null.n_e_free, 0.0)
        self.assertLess(np.dot(near_null.beta_normal, near_null.beta_normal), 1.0)

        vacuum_rate = ER.ElectronCollisionContext(
            EF.ElectronTestField.independent(0.0, [0.9, 0.0, 0.0])
        ).rate_per_normal_time_s([1.0, 0.0, 0.0])
        self.assertEqual(vacuum_rate, 0.0)
        self.assertFalse(np.signbit(vacuum_rate))

    def test_comoving_schedule_uses_live_fluid_velocity_not_beta_interpolation(self):
        schedule = ER.PrescribedComovingElectronSchedule(
            [0.0, 1.0, 2.0], [0.0, 2.0e6, 4.0e6], provenance=PROVENANCE
        )
        beta_a = np.array([0.2, -0.1, 0.03])
        beta_b = np.array([-0.08, 0.17, 0.04])
        state_a = schedule.at(1.5, beta_fluid=beta_a)
        state_b = schedule.at(1.5, beta_fluid=beta_b)
        self.assertEqual(state_a.closure, "comoving-electron")
        self.assertEqual(state_b.closure, "comoving-electron")
        self.assertTrue(np.array_equal(np.asarray(state_a.beta_normal), beta_a))
        self.assertTrue(np.array_equal(np.asarray(state_b.beta_normal), beta_b))
        self.assertEqual(state_a.n_e_free, state_b.n_e_free)

        # On the vacuum quotient the fluid/electron velocity equality has no
        # physical representative; return the canonical zero-current state.
        vacuum = schedule.at(0.0, beta_fluid=beta_a)
        self.assertEqual(vacuum.n_e_free, 0.0)
        self.assertEqual(vacuum.closure, "independent")
        self.assertEqual(vacuum.beta_normal, (0.0, 0.0, 0.0))

    def test_machine_contract_surfaces_validity_and_nonpromotion(self):
        schedule = ER.PrescribedIndependentElectronSchedule(
            [0.0, 1.0], [0.0, 1.0], [[0.4, 0.0, 0.0], [0.1, 0.0, 0.0]],
            provenance=PROVENANCE,
        )
        metadata = schedule.authority_metadata()
        self.assertEqual(metadata["coordinate"], "hubble_time_tau")
        self.assertEqual(metadata["interpolation"], "linear_number_current")
        self.assertEqual(metadata["vacuum_policy"], "collision_off_velocity_quotient")
        self.assertEqual(metadata["density_unit"], "m^-3")
        self.assertFalse(metadata["legacy_history_density_adapter"])
        self.assertIn("Klein-Nishina", metadata["validity_boundary"])
        self.assertIn("ENERGY_DOMAIN_UNVERIFIED", metadata["validity_boundary"])
        self.assertFalse(metadata["production_runtime_wired"])
        self.assertFalse(metadata["authority_row_promoted"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
