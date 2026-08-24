"""Focused gate for trajectory support and optical-depth orientation authority.

Run directly so this bounded authority does not require a production Q/Rust
collision generator::

    python tests/test_electron_trajectory_authority.py
"""
from pathlib import Path
from dataclasses import replace
from decimal import localcontext
import importlib.util
import json
import sys
import types
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "bianchi" / "q" / "electron_trajectory.py"
MACHINE_CONTRACT_PATH = ROOT / "docs" / "electron-trajectory-authority-contract.json"
if not MODULE_PATH.is_file():
    raise AssertionError(
        "RED: bianchi.q.electron_trajectory trajectory authority is absent"
    )
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _load_without_optional_stack():
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
        physical_pkg = types.ModuleType("bianchi.physical")
        physical_pkg.__path__ = [str(ROOT / "bianchi" / "physical")]
        sys.modules.update({
            "bianchi": bianchi_pkg,
            "bianchi.q": q_pkg,
            "bianchi.thermo": thermo_pkg,
            "bianchi.physical": physical_pkg,
        })
        history = types.ModuleType("bianchi.thermo.history_api")
        history.SIGMA_T_CM2 = 6.6524587e-25
        history.C_CM_S = 2.99792458e10
        sys.modules["bianchi.thermo.history_api"] = history
        comoving = types.ModuleType("bianchi.q.comoving")
        comoving.collide_log = lambda *args, **kwargs: (_ for _ in ()).throw(
            RuntimeError("collision kernel is outside this focused gate")
        )
        coupled = types.ModuleType("bianchi.q.coupled")
        coupled.mat3 = lambda value: np.asarray(value, float).reshape(3, 3)
        sys.modules["bianchi.q.comoving"] = comoving
        sys.modules["bianchi.q.coupled"] = coupled

        physical_pkg.units = _load(
            "bianchi.physical.units", ROOT / "bianchi" / "physical" / "units.py"
        )
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
        q_pkg.electron_rate = _load(
            "bianchi.q.electron_rate", ROOT / "bianchi" / "q" / "electron_rate.py"
        )
        q_pkg.electron_validity = _load(
            "bianchi.q.electron_validity", ROOT / "bianchi" / "q" / "electron_validity.py"
        )
        return (
            q_pkg.electron_rate,
            _load("bianchi.q.electron_trajectory", MODULE_PATH),
            q_pkg.electron_validity,
        )
    finally:
        for key in [
            item for item in list(sys.modules)
            if item == "bianchi" or item.startswith("bianchi.")
        ]:
            sys.modules.pop(key, None)
        sys.modules.update(saved)


try:
    from bianchi.q import electron_rate as ER  # noqa: E402
    from bianchi.q import electron_trajectory as ET  # noqa: E402
    from bianchi.q import electron_validity as EV  # noqa: E402
except ModuleNotFoundError as exc:
    if exc.name not in {
        "bianchi", "jax", "jaxlib", "equinox", "diffrax", "bianchi_rustcore"
    }:
        raise
    ER, ET, EV = _load_without_optional_stack()


def _provenance(letter: str, label: str) -> EV.AuthorityProvenance:
    return EV.AuthorityProvenance(
        source_id=f"test:{label}", source_sha256=letter * 64
    )


COORDINATE_PROVENANCE = _provenance("a", "coordinate")
BINDING_PROVENANCE = _provenance("b", "schedule-binding")
ENERGY_PROVENANCE = _provenance("c", "energy")
TEMPERATURE_PROVENANCE = _provenance("d", "temperature")
FRAME_PROVENANCE = _provenance("e", "source-frame")
FLUID_PROVENANCE = _provenance("f", "fluid-frame")
HUBBLE_PROVENANCE = _provenance("1", "hubble")
RATE_PROVENANCE = _provenance("2", "ray-rate")
BUDGET_PROVENANCE = _provenance("3", "budget")
SCHEDULE_PROVENANCE = ER.ElectronScheduleProvenance(
    source_id="test:electron-schedule", source_sha256="4" * 64
)


def _coordinate(origin="tau-origin"):
    return ET.QHubbleTimeCoordinate(
        origin_event=origin, provenance=COORDINATE_PROVENANCE
    )


def _budget(error=1.0e-3, theta=1.0e-4):
    return EV.ColdThomsonBudget(error, theta, BUDGET_PROVENANCE)


def _profiles(coordinate, tau=(0.0, 1.0), *, energy_x=1.0e-5, temp=0.0):
    rest = EV.ELECTRON_REST_ENERGY_J
    return {
        "photon_energy": ET.ScalarTrajectoryProfile.hard_photon_energy_j(
            tau,
            [energy_x * rest] * len(tau),
            source_frame="source",
            coordinate=coordinate,
            provenance=ENERGY_PROVENANCE,
        ),
        "electron_temperature": ET.ScalarTrajectoryProfile.electron_temperature_k(
            tau, [temp] * len(tau), coordinate=coordinate,
            provenance=TEMPERATURE_PROVENANCE,
        ),
        "source_frame": ET.BetaTrajectoryProfile.source_frame(
            tau, np.zeros((len(tau), 3)), frame_id="source",
            coordinate=coordinate, provenance=FRAME_PROVENANCE,
        ),
        "normal_hubble": ET.ScalarTrajectoryProfile.normal_hubble_per_s(
            tau, [2.0] * len(tau), coordinate=coordinate,
            provenance=HUBBLE_PROVENANCE,
        ),
        "local_ray_rate": ET.ScalarTrajectoryProfile.local_ray_rate_per_tau(
            tau, [0.25] * len(tau), coordinate=coordinate,
            provenance=RATE_PROVENANCE,
        ),
    }


def _independent_binding(
    coordinate,
    tau=(0.0, 1.0),
    density=(1.0e6, 1.0e6),
    beta=((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)),
):
    schedule = ER.PrescribedIndependentElectronSchedule(
        tau, density, beta, provenance=SCHEDULE_PROVENANCE
    )
    return ET.ElectronScheduleBinding.bind(
        schedule, coordinate=coordinate, provenance=BINDING_PROVENANCE
    )


def _certify(binding, profiles, *, start=0.0, end=1.0, fluid_frame=None, budget=None):
    return ET.certify_cold_thomson_trajectory(
        electron_binding=binding,
        photon_energy=profiles["photon_energy"],
        electron_temperature=profiles["electron_temperature"],
        source_frame=profiles["source_frame"],
        normal_hubble=profiles["normal_hubble"],
        local_ray_rate=profiles["local_ray_rate"],
        live_fluid_frame=fluid_frame,
        budget=_budget() if budget is None else budget,
        tau_start=start,
        tau_end=end,
    )


class ScheduleViewAndCoordinateTests(unittest.TestCase):
    def test_schedule_views_are_immutable_and_closure_specific(self):
        coordinate = _coordinate()
        independent = _independent_binding(
            coordinate,
            density=(0.0, 2.0e6),
            beta=((0.8, 0.0, 0.0), (0.2, 0.0, 0.0)),
        )
        view = independent.view
        self.assertEqual(view.nodes_ascending, (0.0, 1.0))
        self.assertEqual(view.interpolation, "linear_number_current_v1")
        self.assertIsNotNone(view.number_current_nodes)
        self.assertIsNone(view.density_nodes_m3)
        self.assertEqual(view.number_current_nodes[0], (0.0, 0.0, 0.0, 0.0))
        with self.assertRaises(TypeError):
            view.nodes_ascending[0] = 2.0

        schedule = ER.PrescribedComovingElectronSchedule(
            [0.0, 1.0], [0.0, 2.0e6], provenance=SCHEDULE_PROVENANCE
        )
        comoving = ET.ElectronScheduleBinding.bind(
            schedule, coordinate=coordinate, provenance=BINDING_PROVENANCE
        )
        self.assertEqual(
            comoving.view.interpolation,
            "linear_proper_density_live_fluid_beta",
        )
        self.assertIsNone(comoving.view.number_current_nodes)
        self.assertEqual(comoving.view.density_nodes_m3, (0.0, 2.0e6))

    def test_binding_rejects_payload_substitution(self):
        coordinate = _coordinate()
        schedule = ER.PrescribedIndependentElectronSchedule(
            [0.0, 1.0], [1.0, 1.0], np.zeros((2, 3)),
            provenance=SCHEDULE_PROVENANCE,
        )
        with self.assertRaises(ValueError):
            ET.ElectronScheduleBinding(
                schedule=schedule,
                coordinate=coordinate,
                provenance=BINDING_PROVENANCE,
                schedule_payload_sha256="9" * 64,
            )

    def test_overflowing_binary64_node_interval_fails_closed(self):
        maximum = np.finfo(float).max
        with np.errstate(over="ignore"):
            schedule = ER.PrescribedIndependentElectronSchedule(
                [-maximum, maximum],
                [1.0, 1.0],
                np.zeros((2, 3)),
                provenance=SCHEDULE_PROVENANCE,
            )
        with self.assertRaises(ValueError):
            ET.ElectronScheduleBinding.bind(
                schedule,
                coordinate=_coordinate(),
                provenance=BINDING_PROVENANCE,
            )
        with self.assertRaises(ValueError):
            ET.ScalarTrajectoryProfile.electron_temperature_k(
                [-maximum, maximum],
                [0.0, 0.0],
                coordinate=_coordinate(),
                provenance=TEMPERATURE_PROVENANCE,
            )

    def test_only_identity_q_hubble_coordinate_is_accepted(self):
        with self.assertRaises(ValueError):
            ET.QHubbleTimeCoordinate(
                origin_event="z=0",
                provenance=COORDINATE_PROVENANCE,
                coordinate_kind="redshift_z",
            )
        with self.assertRaises(ValueError):
            ET.QHubbleTimeCoordinate(
                origin_event="tau=0",
                provenance=COORDINATE_PROVENANCE,
                mapping="affine_rescale",
            )


class SupportAndClosureTests(unittest.TestCase):
    def test_closed_intersection_and_one_ulp_escape_fail_without_clamp(self):
        coordinate = _coordinate()
        binding = _independent_binding(coordinate, tau=(0.0, 3.0))
        profiles = _profiles(coordinate, tau=(1.0, 2.0))
        result = _certify(binding, profiles, start=1.0, end=2.0)
        self.assertEqual(result.common_support, (1.0, 2.0))
        self.assertTrue(result.certified)
        with self.assertRaises(ValueError):
            _certify(binding, profiles, start=np.nextafter(1.0, -np.inf), end=2.0)
        with self.assertRaises(ValueError):
            _certify(binding, profiles, start=1.0, end=np.nextafter(2.0, np.inf))
        with self.assertRaises(ValueError):
            _certify(binding, profiles, start=1.5, end=1.5)

    def test_coordinate_hash_mismatch_fails_before_evaluation(self):
        coordinate = _coordinate("origin-a")
        other = _coordinate("origin-b")
        binding = _independent_binding(coordinate)
        profiles = _profiles(coordinate)
        profiles["normal_hubble"] = ET.ScalarTrajectoryProfile.normal_hubble_per_s(
            [0.0, 1.0], [1.0, 1.0], coordinate=other,
            provenance=HUBBLE_PROVENANCE,
        )
        with self.assertRaises(ValueError):
            _certify(binding, profiles)

    def test_independent_and_comoving_closures_are_not_interchanged(self):
        coordinate = _coordinate()
        profiles = _profiles(coordinate)
        independent = _independent_binding(coordinate)
        fluid = ET.BetaTrajectoryProfile.live_fluid(
            [0.0, 1.0], [[0.2, 0.0, 0.0], [0.3, 0.0, 0.0]],
            frame_id="fluid", coordinate=coordinate,
            provenance=FLUID_PROVENANCE,
        )
        with self.assertRaises(ValueError):
            _certify(independent, profiles, fluid_frame=fluid)

        schedule = ER.PrescribedComovingElectronSchedule(
            [0.0, 1.0], [1.0e6, 1.0e6], provenance=SCHEDULE_PROVENANCE
        )
        binding = ET.ElectronScheduleBinding.bind(
            schedule, coordinate=coordinate, provenance=BINDING_PROVENANCE
        )
        with self.assertRaises(ValueError):
            _certify(binding, profiles)
        result = _certify(binding, profiles, fluid_frame=fluid)
        self.assertTrue(result.certified)
        self.assertTrue(all(item.closure == "comoving" for item in result.segments))

    def test_profile_syntax_and_units_fail_closed(self):
        coordinate = _coordinate()
        with self.assertRaises(ValueError):
            ET.ScalarTrajectoryProfile.normal_hubble_per_s(
                [0.0, 1.0], [1.0, 0.0], coordinate=coordinate,
                provenance=HUBBLE_PROVENANCE,
            )
        with self.assertRaises(ValueError):
            ET.ScalarTrajectoryProfile.local_ray_rate_per_tau(
                [0.0, 0.0], [1.0, 1.0], coordinate=coordinate,
                provenance=RATE_PROVENANCE,
            )
        with self.assertRaises(ValueError):
            ET.BetaTrajectoryProfile.source_frame(
                [0.0, 1.0], [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]],
                frame_id="source", coordinate=coordinate,
                provenance=FRAME_PROVENANCE,
            )

        with self.assertRaises(ValueError):
            ET.ScalarTrajectoryProfile.normal_hubble_per_s(
                [0.0, 1.0],
                [np.nextafter(0.0, np.inf)] * 2,
                coordinate=coordinate,
                provenance=HUBBLE_PROVENANCE,
            )


class SegmentSupremumTests(unittest.TestCase):
    def test_hostile_varying_frames_defeat_synchronized_endpoint_doppler(self):
        coordinate = _coordinate()
        binding = _independent_binding(
            coordinate,
            density=(1.0, 1.0),
            beta=((0.0, 0.0, 0.0), (0.8, 0.0, 0.0)),
        )
        profiles = _profiles(coordinate)
        profiles["source_frame"] = ET.BetaTrajectoryProfile.source_frame(
            [0.0, 1.0], [[0.0, 0.0, 0.0], [0.8, 0.0, 0.0]],
            frame_id="source", coordinate=coordinate,
            provenance=FRAME_PROVENANCE,
        )
        result = _certify(binding, profiles)
        witness = result.segments[0]
        endpoint = [
            EV.all_sky_doppler_bounds(
                profiles["source_frame"].at(t), binding.schedule.at(t).beta_normal
            ).maximum
            for t in (0.0, 1.0)
        ]
        middle = EV.all_sky_doppler_bounds(
            profiles["source_frame"].at(0.5),
            binding.schedule.at(0.5).beta_normal,
        ).maximum
        self.assertEqual(endpoint, [1.0, 1.0])
        self.assertGreater(middle, 1.13)
        self.assertGreaterEqual(witness.doppler_max_upper, middle)

    def test_independent_current_stationary_candidate_is_recorded_and_bound_is_hostile_safe(self):
        coordinate = _coordinate()
        binding = _independent_binding(
            coordinate,
            density=(1.0, 1.0),
            beta=((-0.8, 0.0, 0.0), (0.8, 0.0, 0.0)),
        )
        profiles = _profiles(coordinate)
        profiles["source_frame"] = ET.BetaTrajectoryProfile.source_frame(
            [0.0, 1.0], [[0.1, 0.2, 0.0], [-0.2, 0.1, 0.0]],
            frame_id="source", coordinate=coordinate,
            provenance=FRAME_PROVENANCE,
        )
        result = _certify(binding, profiles)
        witness = result.segments[0]
        self.assertEqual(witness.electron_gamma_stationary_fractions, (0.5,))

        rng = np.random.default_rng(2026082341)
        sampled = []
        for tau in rng.uniform(0.0, 1.0, size=800):
            source = profiles["source_frame"].at(tau)
            electron = binding.schedule.at(tau)
            sampled.append(EV.all_sky_doppler_bounds(
                source, electron.beta_normal
            ).maximum)
        self.assertGreaterEqual(
            witness.doppler_max_upper,
            max(sampled) * (1.0 - 2.0e-14),
        )

    def test_vacuum_segment_does_not_erase_adjacent_nonvacuum_budget(self):
        coordinate = _coordinate()
        binding = _independent_binding(
            coordinate,
            tau=(0.0, 1.0, 2.0),
            density=(0.0, 0.0, 1.0e6),
            beta=np.zeros((3, 3)),
        )
        profiles = _profiles(coordinate, tau=(0.0, 1.0, 2.0))
        rest = EV.ELECTRON_REST_ENERGY_J
        profiles["photon_energy"] = ET.ScalarTrajectoryProfile.hard_photon_energy_j(
            [0.0, 1.0, 2.0], [10.0 * rest, 1.0e-5 * rest, 1.0e-5 * rest],
            source_frame="source", coordinate=coordinate,
            provenance=ENERGY_PROVENANCE,
        )
        result = _certify(binding, profiles, start=0.0, end=2.0)
        self.assertTrue(result.certified)
        self.assertTrue(result.segments[0].vacuum)
        self.assertFalse(result.segments[1].vacuum)
        edge_state = binding.schedule.at(np.nextafter(1.0, 2.0))
        self.assertGreater(edge_state.n_e_free, 0.0)
        self.assertTrue(np.isfinite(edge_state.n_e_free))

        profiles["photon_energy"] = ET.ScalarTrajectoryProfile.hard_photon_energy_j(
            [0.0, 1.0, 2.0], [10.0 * rest, 10.0 * rest, 1.0e-5 * rest],
            source_frame="source", coordinate=coordinate,
            provenance=ENERGY_PROVENANCE,
        )
        rejected = _certify(binding, profiles, start=0.0, end=2.0)
        self.assertEqual(
            rejected.status,
            ET.TrajectoryStatus.REJECTED_TOTAL_CROSS_SECTION_BUDGET,
        )

    def test_unsupported_spectrum_and_positive_temperature_remain_unverified(self):
        coordinate = _coordinate()
        binding = _independent_binding(coordinate)
        profiles = _profiles(coordinate)
        profiles["photon_energy"] = ET.ScalarTrajectoryProfile.bolometric_photon_energy(
            [0.0, 1.0], source_frame="source", coordinate=coordinate,
            provenance=ENERGY_PROVENANCE,
        )
        result = _certify(binding, profiles)
        self.assertEqual(result.status, ET.TrajectoryStatus.UNVERIFIED_ENERGY_SUPPORT)

        profiles = _profiles(coordinate, temp=1.0)
        result = _certify(binding, profiles)
        self.assertEqual(
            result.status,
            ET.TrajectoryStatus.UNVERIFIED_FINITE_TEMPERATURE_TAIL,
        )

    def test_decimal_authority_is_independent_of_ambient_context(self):
        coordinate = _coordinate()
        binding = _independent_binding(
            coordinate,
            density=(1.0, 1.0),
            beta=((0.0, 0.0, 0.0), (0.999999, 0.0, 0.0)),
        )
        profiles = _profiles(coordinate, energy_x=1.0e-12)
        reference = _certify(binding, profiles)
        with localcontext() as context:
            context.prec = 6
            hostile = _certify(binding, profiles)
        self.assertEqual(
            reference.segments[0].doppler_max_upper,
            hostile.segments[0].doppler_max_upper,
        )

    def test_near_null_live_schedule_and_beta_profile_are_inside_exported_bounds(self):
        coordinate = _coordinate()
        beta = np.array([0.999999999999, 0.0, 0.0])
        binding = _independent_binding(
            coordinate,
            density=(1.0, 1.0),
            beta=((0.0, 0.0, 0.0), beta),
        )
        profiles = _profiles(coordinate, energy_x=1.0e-16)
        result = _certify(binding, profiles)
        witness = result.segments[0]
        actual_endpoint = EV.all_sky_doppler_bounds(
            [0.0, 0.0, 0.0], binding.schedule.at(1.0).beta_normal
        ).maximum
        self.assertGreaterEqual(witness.doppler_max_upper, actual_endpoint)

        direction = np.array([-0.61, 0.78, 0.085])
        direction /= np.linalg.norm(direction)
        near = direction * np.sqrt(1.0 - 1.0e-10)
        profiles["source_frame"] = ET.BetaTrajectoryProfile.source_frame(
            [0.0, 1.0], [near, near], frame_id="source",
            coordinate=coordinate, provenance=FRAME_PROVENANCE,
        )
        result = _certify(binding, profiles)
        witness = result.segments[0]
        for tau in (0.000145, 0.5, 0.9999):
            actual_gamma = EV.all_sky_doppler_bounds(
                [0.0, 0.0, 0.0], profiles["source_frame"].at(tau)
            ).relative_gamma
            self.assertGreaterEqual(witness.source_gamma_max_upper, actual_gamma)

    def test_extreme_current_scale_separation_fails_closed_or_bounds_live_endpoint(self):
        coordinate = _coordinate()
        schedule = ER.PrescribedIndependentElectronSchedule(
            [0.0, 0.8, 1.0],
            [2.0 ** 300, 2.0 ** -100, 2.0 ** -75],
            [[0.0, 0.0, 0.0], [0.9999, 0.0, 0.0], [0.999999, 0.0, 0.0]],
            provenance=SCHEDULE_PROVENANCE,
        )
        binding = ET.ElectronScheduleBinding.bind(
            schedule, coordinate=coordinate, provenance=BINDING_PROVENANCE
        )
        profiles = _profiles(coordinate, energy_x=1.0e-18)
        try:
            result = _certify(binding, profiles)
        except ValueError:
            return
        if result.status is ET.TrajectoryStatus.UNVERIFIED_NUMERIC_DOMAIN:
            return
        for witness in result.segments:
            actual = EV.all_sky_doppler_bounds(
                [0.0, 0.0, 0.0], schedule.at(witness.tau_end).beta_normal
            ).maximum
            self.assertGreaterEqual(witness.doppler_max_upper, actual)

    def test_vacuum_to_near_null_binary64_false_positive_fails_closed(self):
        coordinate = _coordinate()
        direction = np.array([-0.61, 0.78, 0.085])
        direction /= np.linalg.norm(direction)
        near = direction * np.sqrt(1.0 - 1.0e-10)
        binding = _independent_binding(
            coordinate,
            density=(0.0, 1.0),
            beta=((0.0, 0.0, 0.0), near),
        )
        profiles = _profiles(coordinate, energy_x=1.0e-8)
        result = _certify(
            binding,
            profiles,
            budget=_budget(error=0.003979310610035255),
        )
        self.assertFalse(result.certified)
        self.assertEqual(
            result.status, ET.TrajectoryStatus.UNVERIFIED_NUMERIC_DOMAIN
        )

    def test_scale_separation_kn_false_positive_fails_closed(self):
        coordinate = _coordinate()
        binding = _independent_binding(
            coordinate,
            density=(1.0e101, 1.0),
            beta=((0.0, 0.0, 0.0), (0.999999, 0.0, 0.0)),
        )
        profiles = _profiles(coordinate, energy_x=1.0e-15)
        result = _certify(
            binding,
            profiles,
            budget=_budget(error=1.0e-13, theta=1.0e-20),
        )
        self.assertFalse(result.certified)
        self.assertEqual(
            result.status, ET.TrajectoryStatus.UNVERIFIED_NUMERIC_DOMAIN
        )

    def test_live_density_reconstruction_overflow_fails_closed(self):
        coordinate = _coordinate()
        maximum = np.finfo(float).max
        binding = _independent_binding(
            coordinate,
            density=(maximum, maximum),
            beta=((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)),
        )
        profiles = _profiles(coordinate, energy_x=0.0, temp=0.0)
        result = _certify(
            binding, profiles, budget=_budget(error=0.0, theta=0.0)
        )
        self.assertFalse(result.certified)
        self.assertEqual(
            result.status, ET.TrajectoryStatus.UNVERIFIED_NUMERIC_DOMAIN
        )

    def test_live_density_reconstruction_underflow_fails_closed(self):
        coordinate = _coordinate()
        binding = _independent_binding(
            coordinate,
            density=(1.0e-200, 1.0e-200),
            beta=((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)),
        )
        profiles = _profiles(coordinate, energy_x=0.0, temp=0.0)
        result = _certify(
            binding, profiles, budget=_budget(error=0.0, theta=0.0)
        )
        self.assertFalse(result.certified)
        self.assertEqual(
            result.status, ET.TrajectoryStatus.UNVERIFIED_NUMERIC_DOMAIN
        )

    def test_zero_touching_rest_current_cannot_bypass_density_domain(self):
        coordinate = _coordinate()
        profiles = _profiles(coordinate, energy_x=0.0, temp=0.0)
        for density in (1.0e-200, np.finfo(float).max):
            binding = _independent_binding(
                coordinate,
                density=(0.0, density),
                beta=((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)),
            )
            result = _certify(
                binding, profiles, budget=_budget(error=0.0, theta=0.0)
            )
            self.assertFalse(result.certified)
            self.assertEqual(
                result.status, ET.TrajectoryStatus.UNVERIFIED_NUMERIC_DOMAIN
            )

    def test_comoving_density_interpolation_overflow_fails_closed(self):
        coordinate = _coordinate()
        profiles = _profiles(coordinate, energy_x=0.0, temp=0.0)
        schedule = ER.PrescribedComovingElectronSchedule(
            [0.0, 1.0],
            [np.finfo(float).max] * 2,
            provenance=SCHEDULE_PROVENANCE,
        )
        binding = ET.ElectronScheduleBinding.bind(
            schedule, coordinate=coordinate, provenance=BINDING_PROVENANCE
        )
        fluid = ET.BetaTrajectoryProfile.live_fluid(
            [0.0, 1.0], np.zeros((2, 3)), frame_id="fluid",
            coordinate=coordinate, provenance=FLUID_PROVENANCE,
        )
        result = _certify(binding, profiles, fluid_frame=fluid)
        self.assertFalse(result.certified)
        self.assertEqual(
            result.status, ET.TrajectoryStatus.UNVERIFIED_NUMERIC_DOMAIN
        )

    def test_exact_zero_energy_temperature_and_zero_budget_are_preserved(self):
        coordinate = _coordinate()
        binding = _independent_binding(coordinate)
        profiles = _profiles(coordinate, energy_x=0.0, temp=0.0)
        result = _certify(binding, profiles, budget=_budget(error=0.0, theta=0.0))
        self.assertTrue(result.certified)
        witness = result.segments[0]
        self.assertEqual(witness.x_max_upper, 0.0)
        self.assertEqual(witness.theta_max_upper, 0.0)
        self.assertEqual(witness.total_cross_section_relative_deficit_upper, 0.0)

    def test_binary64_scalar_interpolation_overshoot_is_inside_energy_bound(self):
        coordinate = _coordinate()
        binding = _independent_binding(coordinate)
        profiles = _profiles(coordinate, energy_x=0.0)
        value = 1.0e-316
        profiles["photon_energy"] = (
            ET.ScalarTrajectoryProfile.hard_photon_energy_j(
                [0.0, 1.0],
                [value, value],
                source_frame="source",
                coordinate=coordinate,
                provenance=ENERGY_PROVENANCE,
            )
        )
        live = profiles["photon_energy"].at(0.1)
        self.assertGreater(live, value)
        self.assertGreaterEqual(
            profiles["photon_energy"].maximum_on(0.0, 1.0), live
        )
        result = _certify(binding, profiles)
        self.assertGreaterEqual(result.segments[0].source_energy_max_j, live)

        peaked = ET.ScalarTrajectoryProfile.local_ray_rate_per_tau(
            [0.0, 1.0, 2.0], [1.0, 3.0, 2.0], coordinate=coordinate,
            provenance=RATE_PROVENANCE,
        )
        self.assertGreaterEqual(peaked.maximum_on(0.0, 2.0), 3.0)


class OrientationTests(unittest.TestCase):
    def test_paired_traversals_have_equal_depth_and_opposite_derivative_signs(self):
        coordinate = _coordinate()
        rate = ET.ScalarTrajectoryProfile.local_ray_rate_per_tau(
            [0.0, 1.0, 2.0], [1.0, 3.0, 2.0],
            coordinate=coordinate, provenance=RATE_PROVENANCE,
        )
        before_hash = rate.payload_sha256
        future = ET.integrate_optical_depth(
            rate, 0.25, 1.75, ET.IntegrationOrientation.FUTURE_KINETIC_IVP
        )
        past = ET.integrate_optical_depth(
            rate, 1.75, 0.25,
            ET.IntegrationOrientation.PAST_LIGHT_CONE_ACCUMULATION,
        )
        self.assertEqual(future.derivative_sign, 1)
        self.assertEqual(past.derivative_sign, -1)
        self.assertGreater(future.coordinate_integral, 0.0)
        self.assertLess(past.coordinate_integral, 0.0)
        self.assertEqual(future.depth_increment, past.depth_increment)
        self.assertGreater(future.depth_increment, 0.0)
        self.assertEqual(rate.tau_nodes, (0.0, 1.0, 2.0))
        self.assertEqual(rate.payload_sha256, before_hash)
        with self.assertRaises(ValueError):
            replace(future, derivative_sign=-1)

    def test_invalid_role_direction_and_one_ulp_support_fail(self):
        coordinate = _coordinate()
        rate = ET.ScalarTrajectoryProfile.local_ray_rate_per_tau(
            [0.0, 1.0], [1.0, 1.0], coordinate=coordinate,
            provenance=RATE_PROVENANCE,
        )
        with self.assertRaises(ValueError):
            ET.integrate_optical_depth(
                rate, 1.0, 0.0, ET.IntegrationOrientation.FUTURE_KINETIC_IVP
            )
        with self.assertRaises(ValueError):
            ET.integrate_optical_depth(
                rate, 0.0, 1.0,
                ET.IntegrationOrientation.PAST_LIGHT_CONE_ACCUMULATION,
            )
        with self.assertRaises(ValueError):
            ET.integrate_optical_depth(
                rate, np.nextafter(0.0, -np.inf), 1.0,
                ET.IntegrationOrientation.FUTURE_KINETIC_IVP,
            )


class ContractAndIdentityTests(unittest.TestCase):
    def test_certificate_hash_binds_orientation_inputs_and_metadata_stops(self):
        coordinate = _coordinate()
        binding = _independent_binding(coordinate)
        profiles = _profiles(coordinate)
        first = _certify(binding, profiles)
        changed = dict(profiles)
        changed["local_ray_rate"] = ET.ScalarTrajectoryProfile.local_ray_rate_per_tau(
            [0.0, 1.0], [0.25, np.nextafter(0.25, np.inf)],
            coordinate=coordinate, provenance=RATE_PROVENANCE,
        )
        second = _certify(binding, changed)
        self.assertNotEqual(first.payload_sha256, second.payload_sha256)
        metadata = first.authority_metadata()
        self.assertEqual(metadata["coordinate"], "q_hubble_time_tau")
        self.assertEqual(metadata["array_order"], "strictly_increasing")
        self.assertFalse(metadata["q_collision_generator_wired"])
        self.assertFalse(metadata["production_runtime_wired"])
        self.assertFalse(metadata["authority_row_promoted"])

    def test_machine_contract_is_parseable_bounded_and_nonpromoted(self):
        contract = json.loads(MACHINE_CONTRACT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(
            contract["status"], "BOUNDED_PYTHON_AUTHORITY_NOT_PROMOTED"
        )
        self.assertEqual(contract["coordinate"]["accepted_mapping"], "identity_only")
        self.assertFalse(contract["orientation"]["canonical_arrays_reversed"])
        self.assertFalse(contract["q_collision_generator_wired"])
        self.assertFalse(contract["production_runtime_wired"])
        self.assertFalse(contract["authority_row_promoted"])

    def test_certificate_status_cannot_be_forged_with_dataclass_replace(self):
        coordinate = _coordinate()
        binding = _independent_binding(coordinate)
        profiles = _profiles(coordinate, temp=1.0)
        result = _certify(binding, profiles)
        self.assertEqual(
            result.status,
            ET.TrajectoryStatus.UNVERIFIED_FINITE_TEMPERATURE_TAIL,
        )
        with self.assertRaises((TypeError, ValueError)):
            replace(
                result,
                status=ET.TrajectoryStatus.CERTIFIED_COLD_DELTA_TRAJECTORY,
                certified=True,
                reasons=(
                    "all_nonvacuum_segments_within_hard_cold_total_rate_budget",
                ),
            )
        forged_segment = replace(
            result.segments[0],
            status="certified_cold_delta",
            temperature_max_k=0.0,
            theta_max_upper=0.0,
        )
        with self.assertRaises((TypeError, ValueError)):
            replace(
                result,
                segments=(forged_segment,),
                status=ET.TrajectoryStatus.CERTIFIED_COLD_DELTA_TRAJECTORY,
                certified=True,
                reasons=(
                    "all_nonvacuum_segments_within_hard_cold_total_rate_budget",
                ),
            )


if __name__ == "__main__":
    unittest.main()
