"""Focused gate for cold-Thomson energy validity and rate ownership.

Run directly so this bounded authority does not require the optional JAX/Rust
stack::

    python tests/test_electron_thomson_validity.py

Numerical reference values are frozen from the independent Wolfram receipt in
the BASS-8B.1E.3 checkpoint.  This gate does not treat a total
Klein--Nishina rate as a polarized differential-kernel or finite-temperature
error bound.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import types
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "bianchi" / "q" / "electron_validity.py"
MACHINE_CONTRACT_PATH = ROOT / "docs" / "electron-thomson-validity-contract.json"
if not MODULE_PATH.is_file():
    raise AssertionError(
        "RED: bianchi.q.electron_validity cold-Thomson authority is absent"
    )


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
        return (
            q_pkg.electron,
            q_pkg.electron_rate,
            _load("bianchi.q.electron_validity", MODULE_PATH),
        )
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
    from bianchi.q import electron_validity as EV
except ModuleNotFoundError as exc:
    if exc.name not in {
        "bianchi", "jax", "jaxlib", "equinox", "diffrax", "bianchi_rustcore"
    }:
        raise
    EF, ER, EV = _load_without_optional_stack()


PROVENANCE = EV.AuthorityProvenance(
    source_id="test:local-spectral-authority",
    source_sha256="a" * 64,
)
POLICY_PROVENANCE = EV.AuthorityProvenance(
    source_id="test:declared-thomson-budget",
    source_sha256="b" * 64,
)
FRAME_PROVENANCE = EV.AuthorityProvenance(
    source_id="test:source-frame", source_sha256="c" * 64
)
STATE_PROVENANCE = EV.AuthorityProvenance(
    source_id="test:electron-state", source_sha256="d" * 64
)
TEMPERATURE_PROVENANCE = EV.AuthorityProvenance(
    source_id="test:electron-temperature", source_sha256="e" * 64
)


def _hard_bound(x_source, *, frame="normal", event="tau=0"):
    return EV.PhotonEnergyBound.hard_finite_j(
        x_source * EV.ELECTRON_REST_ENERGY_J,
        source_frame=frame,
        event_id=event,
        provenance=PROVENANCE,
    )


def _budget(rate_error=1.0e-3, theta=1.0e-4):
    return EV.ColdThomsonBudget(
        max_total_cross_section_relative_error=rate_error,
        max_theta_e=theta,
        provenance=POLICY_PROVENANCE,
    )


def _certify(electron, energy_bound, budget, *, temperature_k, beta_source):
    event = energy_bound.event_id
    return EV.certify_cold_thomson(
        EV.ElectronStateAuthority(
            electron, event_id=event, provenance=STATE_PROVENANCE
        ),
        energy_bound,
        budget,
        EV.ElectronTemperatureAuthority(
            temperature_k, event_id=event, provenance=TEMPERATURE_PROVENANCE
        ),
        EV.ObserverFrameAuthority(
            beta_source,
            frame_id=energy_bound.source_frame,
            event_id=event,
            provenance=FRAME_PROVENANCE,
        ),
    )


class KleinNishinaTests(unittest.TestCase):
    def test_cancellation_safe_total_ratio_matches_wolfram_receipt(self):
        x = np.array([0.0, 1e-20, 1e-12, 1e-8, 1e-6, 1e-4, 1e-2, 1e-1, 1.0, 10.0])
        expected = np.array([
            1.0,
            1.0,
            0.9999999999980000000000052,
            0.9999999800000005199999867,
            0.9999980000051999867000327,
            0.9998000519867032677944659,
            0.9805070192618959545605774,
            0.8413381496314298902932385,
            0.4307278419150432638470158,
            0.1227597642966074015592071,
        ])
        got = EV.klein_nishina_total_ratio(x)
        self.assertLess(np.max(np.abs(got - expected)), 8e-15)
        self.assertEqual(EV.klein_nishina_total_ratio(0.0), 1.0)
        self.assertFalse(np.signbit(1.0 - EV.klein_nishina_total_ratio(0.0)))
        self.assertTrue(np.all(np.diff(got) <= 0.0))

        # The first nontrivial coefficient is exactly -2 in x.
        probe = 1.0e-7
        slope = (EV.klein_nishina_total_ratio(probe) - 1.0) / probe
        self.assertLess(abs(slope + 2.0), 6.0e-7)

    def test_total_deficit_survives_ratio_rounding_and_switch_is_portable(self):
        self.assertEqual(EV.klein_nishina_total_ratio(1.0e-20), 1.0)
        deficit = EV.klein_nishina_total_deficit(1.0e-20)
        self.assertGreater(deficit, 0.0)
        self.assertLess(abs(deficit / 2.0e-20 - 1.0), 3e-15)

        switch = 1.0e-3
        probes = np.array([
            np.nextafter(switch, -np.inf), switch, np.nextafter(switch, np.inf)
        ])
        values = EV.klein_nishina_total_ratio(probes)
        self.assertLess(np.max(values) - np.min(values), 8e-15)
        self.assertLess(
            np.max(np.abs(values - 0.9980051867326081797815260)), 8e-15
        )

    def test_kn_domain_rejects_nonphysical_inputs(self):
        for bad in [-1e-30, np.nan, np.inf, -np.inf]:
            with self.subTest(x=bad), self.assertRaises(ValueError):
                EV.klein_nishina_total_ratio(bad)


class FrameBoundTests(unittest.TestCase):
    def test_relative_all_sky_bounds_are_exact_not_normal_frame_shortcut(self):
        source = np.array([0.6, 0.0, 0.0])
        electron = np.array([-0.6, 0.0, 0.0])
        bounds = EV.all_sky_doppler_bounds(source, electron)
        self.assertLess(abs(bounds.relative_gamma - 17.0 / 8.0), 5e-16)
        self.assertLess(abs(bounds.maximum - 4.0), 8e-16)
        self.assertLess(abs(bounds.minimum - 0.25), 8e-17)
        self.assertLess(abs(bounds.maximum * bounds.minimum - 1.0), 2e-16)

        comoving = EV.all_sky_doppler_bounds(source, source)
        self.assertEqual((comoving.minimum, comoving.maximum), (1.0, 1.0))

    def test_noncollinear_bound_attains_matrix_time_row_and_bounds_sphere(self):
        source = np.array([0.31, -0.22, 0.09])
        electron = np.array([-0.18, 0.27, 0.13])
        bounds = EV.all_sky_doppler_bounds(source, electron)
        matrix = EF.frame_matrix(source, electron)
        direction_max = matrix[0, 1:] / np.linalg.norm(matrix[0, 1:])
        _, _, attained = EF.transform_photon(1.0, direction_max, source, electron)
        self.assertLess(abs(attained / bounds.maximum - 1.0), 4e-15)

        rng = np.random.default_rng(2026082323)
        directions = rng.normal(size=(2000, 3))
        directions /= np.linalg.norm(directions, axis=1)[:, None]
        _, _, sampled = EF.transform_photon(
            np.ones(len(directions)), directions, source, electron
        )
        self.assertGreaterEqual(float(sampled.min()), bounds.minimum)
        self.assertLessEqual(float(sampled.max()), bounds.maximum)

    def test_nearly_comoving_ultrarelativistic_bounds_stay_reciprocal(self):
        source = np.array([0.999999, 0.0, 0.0])
        target = np.array([0.999999000001, 0.0, 0.0])
        bounds = EV.all_sky_doppler_bounds(source, target)
        self.assertGreaterEqual(bounds.relative_gamma, 1.0)
        self.assertLess(abs(bounds.minimum * bounds.maximum - 1.0), 2e-15)
        self.assertLess(abs(bounds.maximum - 1.0), 2e-6)

    def test_hostile_nearly_null_pair_uses_exact_binary64_values(self):
        # Float products round Gamma below/near one for this pair.  The oracle
        # treats each supplied binary64 component as its exact real value and
        # evaluates the invariant at 80 decimal digits.
        source = np.array([
            -0.40499928034712473, 0.19483031443833956, -0.89331782221904
        ])
        target = np.array([
            -0.40499928034731597, 0.19483031443830184, -0.8933178222189615
        ])
        bounds = EV.all_sky_doppler_bounds(source, target)
        self.assertLess(
            abs(bounds.relative_gamma - 1.00068277760978331674084434575), 3e-16
        )
        self.assertLess(
            abs(bounds.maximum - 1.03764250440573048187000712909), 3e-16
        )
        self.assertLess(abs(bounds.minimum * bounds.maximum - 1.0), 2e-16)


class ValidityContractTests(unittest.TestCase):
    def test_hard_local_bound_certifies_only_exact_cold_delta_lane(self):
        electron = EF.ColdElectronTestField.independent(2.0e6, [0.0, 0.0, 0.0])
        result = _certify(
            electron,
            _hard_bound(5.0e-4),
            _budget(),
            temperature_k=0.0,
            beta_source=[0.0, 0.0, 0.0],
        )
        self.assertEqual(result.status, EV.ColdThomsonStatus.CERTIFIED_COLD_DELTA)
        self.assertTrue(result.certified)
        self.assertTrue(result.total_cross_section_pass)
        self.assertTrue(result.temperature_policy_pass)
        self.assertLess(result.total_cross_section_relative_deficit, 1.0e-3)
        self.assertEqual(result.x_max, 5.0e-4)
        metadata = result.authority_metadata()
        self.assertEqual(metadata["claim_scope"], "stationary_electron_total_cross_section_only")
        self.assertEqual(metadata["source_frame"], "normal")
        self.assertEqual(metadata["event_id"], "tau=0")
        self.assertFalse(metadata["polarized_differential_kernel_certified"])
        self.assertFalse(metadata["production_runtime_wired"])
        self.assertEqual(len(metadata["certificate_payload_sha256"]), 64)

    def test_exact_all_sky_boost_can_turn_local_pass_into_rejection(self):
        electron = EF.ColdElectronTestField.independent(2.0e6, [-0.6, 0.0, 0.0])
        result = _certify(
            electron,
            _hard_bound(3.0e-4, frame="source+0.6"),
            _budget(),
            temperature_k=0.0,
            beta_source=[0.6, 0.0, 0.0],
        )
        self.assertLess(abs(result.doppler_max - 4.0), 8e-16)
        self.assertLess(abs(result.x_max - 1.2e-3), 2e-18)
        self.assertFalse(result.total_cross_section_pass)
        self.assertEqual(
            result.status,
            EV.ColdThomsonStatus.REJECTED_TOTAL_CROSS_SECTION_BUDGET,
        )
        self.assertFalse(result.certified)

    def test_zero_and_tight_total_cross_section_budgets_use_direct_deficit(self):
        electron = EF.ColdElectronTestField.independent(1.0, [0.0, 0.0, 0.0])
        zero_budget = _certify(
            electron,
            _hard_bound(1.0e-20),
            _budget(rate_error=0.0),
            temperature_k=0.0,
            beta_source=[0.0, 0.0, 0.0],
        )
        self.assertEqual(
            zero_budget.status,
            EV.ColdThomsonStatus.REJECTED_TOTAL_CROSS_SECTION_BUDGET,
        )
        self.assertGreater(zero_budget.total_cross_section_relative_deficit, 0.0)

        exact = 1.9999999999947998e-12
        just_pass = _certify(
            electron, _hard_bound(1.0e-12),
            _budget(rate_error=np.nextafter(exact, np.inf)),
            temperature_k=0.0, beta_source=[0.0, 0.0, 0.0]
        )
        just_fail = _certify(
            electron, _hard_bound(1.0e-12),
            _budget(rate_error=np.nextafter(exact, -np.inf)),
            temperature_k=0.0, beta_source=[0.0, 0.0, 0.0]
        )
        self.assertTrue(just_pass.total_cross_section_pass)
        self.assertFalse(just_fail.total_cross_section_pass)

    def test_bolometric_unknown_and_effective_tail_bounds_fail_closed(self):
        electron = EF.ColdElectronTestField.independent(1.0, [0.0, 0.0, 0.0])
        supports = [
            EV.PhotonEnergyBound.bolometric(
                source_frame="mode-a", event_id="tau=1", provenance=PROVENANCE
            ),
            EV.PhotonEnergyBound.unknown(
                source_frame="external", event_id="tau=1", provenance=PROVENANCE
            ),
            EV.PhotonEnergyBound.effective_tail_j(
                1.0e-16,
                source_frame="mode-b-grid",
                event_id="tau=1",
                tail_metric="number_fraction",
                tail_error_bound=1.0e-9,
                provenance=PROVENANCE,
            ),
        ]
        for support in supports:
            with self.subTest(kind=support.kind):
                result = _certify(
                    electron, support, _budget(), temperature_k=0.0,
                    beta_source=[0.0, 0.0, 0.0]
                )
                self.assertEqual(
                    result.status, EV.ColdThomsonStatus.UNVERIFIED_ENERGY_SUPPORT
                )
                self.assertFalse(result.certified)
                self.assertIsNone(result.x_max)

    def test_finite_temperature_policy_is_diagnostic_not_tail_certificate(self):
        electron = EF.ColdElectronTestField.independent(1.0, [0.0, 0.0, 0.0])
        temperature = (
            1.0e-5 * EV.ELECTRON_REST_ENERGY_J / EV.BOLTZMANN_CONSTANT_J_K
        )
        result = _certify(
            electron, _hard_bound(1.0e-5), _budget(theta=1.0e-4),
            temperature_k=temperature, beta_source=[0.0, 0.0, 0.0]
        )
        self.assertTrue(result.temperature_policy_pass)
        self.assertEqual(result.theta_e, 1.0e-5)
        self.assertEqual(
            result.status, EV.ColdThomsonStatus.UNVERIFIED_FINITE_TEMPERATURE_TAIL
        )
        self.assertFalse(result.certified)
        self.assertFalse(result.valid_for_requested_budget)
        self.assertTrue(result.declared_scalar_predicates_pass)

        hot = _certify(
            electron, _hard_bound(1.0e-5), _budget(theta=1.0e-6),
            temperature_k=temperature, beta_source=[0.0, 0.0, 0.0]
        )
        self.assertFalse(hot.temperature_policy_pass)
        self.assertEqual(hot.status, EV.ColdThomsonStatus.REJECTED_TEMPERATURE_POLICY)

    def test_vacuum_is_vacuous_collision_off_not_thomson_certified(self):
        electron = EF.ColdElectronTestField.independent(0.0, [0.9, 0.0, 0.0])
        result = _certify(
            electron,
            EV.PhotonEnergyBound.bolometric(
                source_frame="mode-a", event_id="tau=2", provenance=PROVENANCE
            ),
            _budget(),
            temperature_k=1.0e99,
            beta_source=[-0.9, 0.0, 0.0],
        )
        self.assertEqual(result.status, EV.ColdThomsonStatus.VACUOUS_COLLISION_OFF)
        self.assertFalse(result.certified)
        self.assertEqual(result.reasons, ("zero_electron_proper_density",))

    def test_provenance_units_and_budget_are_strict(self):
        with self.assertRaises(ValueError):
            EV.AuthorityProvenance("", "a" * 64)
        with self.assertRaises(ValueError):
            EV.AuthorityProvenance("source", "A" * 64)
        for bad in [-1.0, np.nan, np.inf]:
            with self.subTest(energy=bad), self.assertRaises(ValueError):
                EV.PhotonEnergyBound.hard_finite_j(
                    bad, source_frame="normal", event_id="tau=0", provenance=PROVENANCE
                )
        with self.assertRaises(ValueError):
            EV.PhotonEnergyBound.effective_tail_j(
                1.0, source_frame="grid", event_id="tau=0", tail_metric="",
                tail_error_bound=1e-6, provenance=PROVENANCE
            )
        for bad in [-1e-6, 1.0, np.nan]:
            with self.subTest(rate_budget=bad), self.assertRaises(ValueError):
                EV.ColdThomsonBudget(bad, 1e-4, POLICY_PROVENANCE)
        with self.assertRaises(ValueError):
            EV.PhotonEnergyBound.hard_finite_j(
                1.0, source_frame="a\0b", event_id="c", provenance=PROVENANCE
            )
        positive_zero = EV.PhotonEnergyBound.hard_finite_j(
            0.0, source_frame="normal", event_id="tau=0", provenance=PROVENANCE
        )
        negative_zero = EV.PhotonEnergyBound.hard_finite_j(
            -0.0, source_frame="normal", event_id="tau=0", provenance=PROVENANCE
        )
        self.assertEqual(positive_zero.payload_sha256, negative_zero.payload_sha256)

    def test_positive_underflow_and_overflow_energy_domains_fail_closed(self):
        rest = EF.ColdElectronTestField.independent(1.0, [0.0, 0.0, 0.0])
        subnormal = EV.PhotonEnergyBound.hard_finite_j(
            np.nextafter(0.0, 1.0), source_frame="normal", event_id="tau=7",
            provenance=PROVENANCE
        )
        underflow = _certify(
            rest, subnormal, _budget(rate_error=0.0), temperature_k=0.0,
            beta_source=[0.0, 0.0, 0.0]
        )
        # D_max>=1 and m_e c^2<1 J, so the smallest positive binary64 energy
        # produces a representable positive x rather than underflowing.
        self.assertEqual(
            underflow.status,
            EV.ColdThomsonStatus.REJECTED_TOTAL_CROSS_SECTION_BUDGET,
        )
        self.assertFalse(underflow.certified)
        self.assertGreater(underflow.total_cross_section_relative_deficit, 0.0)

        fast = EF.ColdElectronTestField.independent(1.0, [0.999, 0.0, 0.0])
        enormous = EV.PhotonEnergyBound.hard_finite_j(
            np.finfo(float).max, source_frame="normal", event_id="tau=8",
            provenance=PROVENANCE
        )
        overflow = _certify(
            fast, enormous, _budget(rate_error=0.99), temperature_k=0.0,
            beta_source=[0.0, 0.0, 0.0]
        )
        self.assertEqual(
            overflow.status, EV.ColdThomsonStatus.UNVERIFIED_NUMERIC_DOMAIN
        )

    def test_certificate_binds_frame_state_temperature_and_event(self):
        bound = _hard_bound(1.0e-5, frame="normal", event="tau=4")
        electron = EF.ColdElectronTestField.independent(3.0, [0.1, 0.0, 0.0])
        first = _certify(
            electron, bound, _budget(), temperature_k=0.0,
            beta_source=[0.0, 0.0, 0.0]
        )
        changed_frame = _certify(
            electron, bound, _budget(), temperature_k=0.0,
            beta_source=[0.01, 0.0, 0.0]
        )
        self.assertNotEqual(first.payload_sha256, changed_frame.payload_sha256)

        signed_zero = EV.ObserverFrameAuthority(
            [-0.0, 0.0, -0.0], frame_id="normal", event_id="tau=4",
            provenance=FRAME_PROVENANCE
        )
        positive_zero = EV.ObserverFrameAuthority(
            [0.0, 0.0, 0.0], frame_id="normal", event_id="tau=4",
            provenance=FRAME_PROVENANCE
        )
        self.assertEqual(signed_zero.payload_sha256, positive_zero.payload_sha256)

        with self.assertRaises(ValueError):
            EV.certify_cold_thomson(
                EV.ElectronStateAuthority(
                    electron, event_id="tau=4", provenance=STATE_PROVENANCE
                ),
                bound,
                _budget(),
                EV.ElectronTemperatureAuthority(
                    0.0, event_id="tau=DIFFERENT", provenance=TEMPERATURE_PROVENANCE
                ),
                positive_zero,
            )
        with self.assertRaises(ValueError):
            EV.certify_cold_thomson(
                EV.ElectronStateAuthority(
                    electron, event_id="tau=4", provenance=STATE_PROVENANCE
                ),
                bound,
                _budget(),
                EV.ElectronTemperatureAuthority(
                    0.0, event_id="tau=4", provenance=TEMPERATURE_PROVENANCE
                ),
                EV.ObserverFrameAuthority(
                    [0.0, 0.0, 0.0], frame_id="fluid", event_id="tau=4",
                    provenance=FRAME_PROVENANCE
                ),
            )


class ConsumerOwnershipTests(unittest.TestCase):
    def test_typed_consumer_seam_prevents_omit_and_double_d(self):
        electron = EF.ColdElectronTestField.independent(7.0e5, [0.6, 0.0, 0.0])
        context = ER.ElectronCollisionContext(electron)
        contract = EV.ElectronCollisionConsumerContract(context)
        base = electron.n_e_free * ER.SIGMA_T_M2 * electron.c_m_s

        rest = contract.input_for(EV.CollisionConsumerId.MATTER_COLLISION_MOVING)
        self.assertIsInstance(rest, EV.RestOpacityPerSecond)
        self.assertEqual(rest.value_per_s, context.rest_opacity_per_second())
        self.assertEqual(rest.value_per_s, base)

        expected_d = [0.5, 2.0, 1.25]
        for direction, factor in zip(
            ([1.0, 0.0, 0.0], [-1.0, 0.0, 0.0], [0.0, 1.0, 0.0]), expected_d
        ):
            observer = contract.input_for(
                EV.CollisionConsumerId.EXTERNAL_OBSERVER_RAY,
                direction_source=direction,
                beta_source=[0.0, 0.0, 0.0],
            )
            self.assertIsInstance(observer, EV.ObserverRayRatePerSecond)
            self.assertLess(abs(observer.value_per_s / base - factor), 3e-15)
            self.assertEqual(observer.relative_flux_factor, factor)

        with self.assertRaises(EV.UnresolvedCollisionConsumerError):
            contract.input_for(EV.CollisionConsumerId.Q_SCALAR_KERNEL)
        with self.assertRaises(ValueError):
            contract.input_for(EV.CollisionConsumerId.EXTERNAL_OBSERVER_RAY)
        with self.assertRaises(TypeError):
            contract.validate_input(EV.CollisionConsumerId.MATTER_COLLISION_MOVING, observer)
        with self.assertRaises(TypeError):
            contract.validate_input(EV.CollisionConsumerId.EXTERNAL_OBSERVER_RAY, rest)

    def test_vacuum_typed_rates_are_positive_zero(self):
        context = ER.ElectronCollisionContext(
            EF.ColdElectronTestField.independent(0.0, [0.8, 0.0, 0.0])
        )
        contract = EV.ElectronCollisionConsumerContract(context)
        rest = contract.input_for(EV.CollisionConsumerId.MATTER_COLLISION_MOVING)
        observer = contract.input_for(
            EV.CollisionConsumerId.EXTERNAL_OBSERVER_RAY,
            direction_source=[1.0, 0.0, 0.0], beta_source=[0.0, 0.0, 0.0]
        )
        self.assertEqual(rest.value_per_s, 0.0)
        self.assertEqual(observer.value_per_s, 0.0)
        self.assertFalse(np.signbit(rest.value_per_s))
        self.assertFalse(np.signbit(observer.value_per_s))
        malformed = [
            ([np.nan, 0.0, 0.0], [0.0, 0.0, 0.0]),
            ([1.0, 0.0, 0.0], [2.0, 0.0, 0.0]),
            ([1.0, 1.0, 0.0], [0.0, 0.0, 0.0]),
        ]
        for direction, beta in malformed:
            with self.subTest(direction=direction, beta=beta), self.assertRaises(ValueError):
                contract.input_for(
                    EV.CollisionConsumerId.EXTERNAL_OBSERVER_RAY,
                    direction_source=direction,
                    beta_source=beta,
                )

    def test_observer_rate_uses_decimal_doppler_and_canonical_unit_direction(self):
        electron = EF.ColdElectronTestField.independent(
            1.0, [0.999999000001, 0.0, 0.0]
        )
        contract = EV.ElectronCollisionConsumerContract(
            ER.ElectronCollisionContext(electron)
        )
        expected = [
            0.999999500010685885436573762074,
            1.00000049998956410400264703775,
        ]
        for direction, oracle in zip(
            ([1.0, 0.0, 0.0], [-1.0, 0.0, 0.0]), expected
        ):
            rate = contract.input_for(
                EV.CollisionConsumerId.EXTERNAL_OBSERVER_RAY,
                direction_source=direction,
                beta_source=[0.999999, 0.0, 0.0],
            )
            rest = contract.input_for(
                EV.CollisionConsumerId.MATTER_COLLISION_MOVING
            )
            self.assertLess(abs(rate.value_per_s / rest.value_per_s - oracle), 3e-16)

        ordinary = EV.ElectronCollisionConsumerContract(
            ER.ElectronCollisionContext(
                EF.ColdElectronTestField.independent(1.0, [0.6, 0.0, 0.0])
            )
        )
        accepted_near_unit = ordinary.input_for(
            EV.CollisionConsumerId.EXTERNAL_OBSERVER_RAY,
            direction_source=[-(1.0 + 1.0e-12), 0.0, 0.0],
            beta_source=[0.0, 0.0, 0.0],
        )
        self.assertLess(abs(accepted_near_unit.relative_flux_factor - 2.0), 4e-16)


class MachineContractTests(unittest.TestCase):
    def test_machine_contract_is_parseable_fail_closed_and_nonpromoted(self):
        contract = json.loads(MACHINE_CONTRACT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(contract["schema"], "bass.electron_thomson_validity_contract/v1")
        self.assertEqual(
            contract["total_cross_section_measure"]["denominator"], "sigma_T"
        )
        self.assertEqual(
            contract["numeric_semantics"]["kn_deficit"],
            "direct_not_one_minus_rounded_ratio",
        )
        self.assertEqual(
            contract["integration_orientation"],
            "local_future_ray_rate_only__unverified",
        )
        self.assertFalse(contract["runtime_signature_type_enforced"])
        self.assertFalse(contract["production_runtime_wired"])
        self.assertFalse(contract["authority_row_promoted"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
