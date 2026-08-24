"""Hostile replay for the bounded E4 trajectory authority."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SUPPORT_PATH = ROOT / "tests" / "test_electron_trajectory_authority.py"
spec = importlib.util.spec_from_file_location("e4_test_support", SUPPORT_PATH)
support = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = support
assert spec.loader is not None
spec.loader.exec_module(support)

ER, ET, EV = support.ER, support.ET, support.EV


def _beta(rng, maximum=0.97):
    direction = rng.normal(size=3)
    direction /= np.linalg.norm(direction)
    return direction * rng.uniform(0.0, maximum)


def _near_null_beta(rng):
    direction = rng.normal(size=3)
    direction /= np.linalg.norm(direction)
    magnitude = 1.0 - 10.0 ** rng.uniform(-12.0, -4.0)
    out = direction * magnitude
    while float(out @ out) >= 1.0:
        out = np.nextafter(out, np.zeros(3))
    return out


def _profile_set(coordinate, tau, source_beta, energy_x):
    rest = EV.ELECTRON_REST_ENERGY_J
    return {
        "photon_energy": ET.ScalarTrajectoryProfile.hard_photon_energy_j(
            tau,
            np.asarray(energy_x) * rest,
            source_frame="source",
            coordinate=coordinate,
            provenance=support.ENERGY_PROVENANCE,
        ),
        "electron_temperature": ET.ScalarTrajectoryProfile.electron_temperature_k(
            tau, np.zeros(len(tau)), coordinate=coordinate,
            provenance=support.TEMPERATURE_PROVENANCE,
        ),
        "source_frame": ET.BetaTrajectoryProfile.source_frame(
            tau, source_beta, frame_id="source", coordinate=coordinate,
            provenance=support.FRAME_PROVENANCE,
        ),
        "normal_hubble": ET.ScalarTrajectoryProfile.normal_hubble_per_s(
            tau, np.exp(np.linspace(-2.0, 2.0, len(tau))),
            coordinate=coordinate, provenance=support.HUBBLE_PROVENANCE,
        ),
        "local_ray_rate": ET.ScalarTrajectoryProfile.local_ray_rate_per_tau(
            tau, np.linspace(0.0, 3.0, len(tau)), coordinate=coordinate,
            provenance=support.RATE_PROVENANCE,
        ),
    }


def _check_certificate(result, binding, profiles, fluid=None):
    max_doppler_ratio = 0.0
    max_x_ratio = 0.0
    for witness in result.segments:
        if witness.vacuum:
            continue
        if witness.status == "unverified_numeric_domain":
            if result.certified:
                raise AssertionError("numeric-domain witness produced certification")
            continue
        samples = set(
            float(value)
            for value in np.linspace(witness.tau_start, witness.tau_end, 41)
        )
        samples.add(float(np.nextafter(witness.tau_start, witness.tau_end)))
        samples.add(float(np.nextafter(witness.tau_end, witness.tau_start)))
        for tau in sorted(samples):
            source_beta = profiles["source_frame"].at(tau)
            if fluid is None:
                electron = binding.schedule.at(tau)
            else:
                electron = binding.schedule.at(tau, beta_fluid=fluid.at(tau))
            actual = EV.all_sky_doppler_bounds(
                source_beta, electron.beta_normal
            ).maximum
            max_doppler_ratio = max(
                max_doppler_ratio, actual / witness.doppler_max_upper
            )
            energy = profiles["photon_energy"].at(tau)
            actual_x = energy * actual / EV.ELECTRON_REST_ENERGY_J
            max_x_ratio = max(max_x_ratio, actual_x / witness.x_max_upper)
    if max_doppler_ratio > 1.0 + 2.0e-14 or max_x_ratio > 1.0 + 2.0e-14:
        raise AssertionError(
            f"segment bound violated: D={max_doppler_ratio}, x={max_x_ratio}"
        )
    return max_doppler_ratio, max_x_ratio


def _deterministic_numeric_falsifiers(coordinate):
    fail_closed = 0

    # Reviewer falsifier 1: exact vacuum to a moving near-null current.
    direction = np.array([-0.61, 0.78, 0.085])
    direction /= np.linalg.norm(direction)
    near = direction * np.sqrt(1.0 - 1.0e-10)
    binding = support._independent_binding(
        coordinate,
        density=(0.0, 1.0),
        beta=((0.0, 0.0, 0.0), near),
    )
    profiles = support._profiles(coordinate, energy_x=1.0e-8)
    result = support._certify(
        binding,
        profiles,
        budget=support._budget(error=0.003979310610035255),
    )
    if result.status is not ET.TrajectoryStatus.UNVERIFIED_NUMERIC_DOMAIN:
        raise AssertionError("vacuum/near-null falsifier did not fail closed")
    fail_closed += 1

    # Reviewer falsifier 2: over 100 decades of current scale separation.
    binding = support._independent_binding(
        coordinate,
        density=(1.0e101, 1.0),
        beta=((0.0, 0.0, 0.0), (0.999999, 0.0, 0.0)),
    )
    profiles = support._profiles(coordinate, energy_x=1.0e-15)
    result = support._certify(
        binding,
        profiles,
        budget=support._budget(error=1.0e-13, theta=1.0e-20),
    )
    if result.status is not ET.TrajectoryStatus.UNVERIFIED_NUMERIC_DOMAIN:
        raise AssertionError("scale-separation falsifier did not fail closed")
    fail_closed += 1

    # Finite current knots whose live proper-density reconstruction overflows.
    binding = support._independent_binding(
        coordinate,
        density=(np.finfo(float).max, np.finfo(float).max),
        beta=((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)),
    )
    profiles = support._profiles(coordinate, energy_x=0.0, temp=0.0)
    result = support._certify(
        binding, profiles, budget=support._budget(error=0.0, theta=0.0)
    )
    if result.status is not ET.TrajectoryStatus.UNVERIFIED_NUMERIC_DOMAIN:
        raise AssertionError("live density-overflow falsifier did not fail closed")
    fail_closed += 1

    binding = support._independent_binding(
        coordinate,
        density=(1.0e-200, 1.0e-200),
        beta=((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)),
    )
    profiles = support._profiles(coordinate, energy_x=0.0, temp=0.0)
    result = support._certify(
        binding, profiles, budget=support._budget(error=0.0, theta=0.0)
    )
    if result.status is not ET.TrajectoryStatus.UNVERIFIED_NUMERIC_DOMAIN:
        raise AssertionError("live density-underflow falsifier did not fail closed")
    fail_closed += 1

    for density in (1.0e-200, np.finfo(float).max):
        binding = support._independent_binding(
            coordinate,
            density=(0.0, density),
            beta=((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)),
        )
        result = support._certify(
            binding,
            profiles,
            budget=support._budget(error=0.0, theta=0.0),
        )
        if result.status is not ET.TrajectoryStatus.UNVERIFIED_NUMERIC_DOMAIN:
            raise AssertionError("zero-touching rest-current domain bypass")
        fail_closed += 1

    schedule = ER.PrescribedComovingElectronSchedule(
        [0.0, 1.0], [np.finfo(float).max] * 2,
        provenance=support.SCHEDULE_PROVENANCE,
    )
    binding = ET.ElectronScheduleBinding.bind(
        schedule, coordinate=coordinate,
        provenance=support.BINDING_PROVENANCE,
    )
    fluid = ET.BetaTrajectoryProfile.live_fluid(
        [0.0, 1.0], np.zeros((2, 3)), frame_id="fluid",
        coordinate=coordinate, provenance=support.FLUID_PROVENANCE,
    )
    result = support._certify(binding, profiles, fluid_frame=fluid)
    if result.status is not ET.TrajectoryStatus.UNVERIFIED_NUMERIC_DOMAIN:
        raise AssertionError("comoving density-overflow falsifier did not fail closed")
    fail_closed += 1

    maximum = np.finfo(float).max
    with np.errstate(over="ignore"):
        schedule = ER.PrescribedIndependentElectronSchedule(
            [-maximum, maximum], [1.0, 1.0], np.zeros((2, 3)),
            provenance=support.SCHEDULE_PROVENANCE,
        )
    try:
        ET.ElectronScheduleBinding.bind(
            schedule, coordinate=coordinate,
            provenance=support.BINDING_PROVENANCE,
        )
    except ValueError:
        fail_closed += 1
    else:
        raise AssertionError("overflowing binary64 node interval was accepted")

    # Equal-density near-null knots remain certifiable only if the live endpoint
    # is below the exported bound.
    binding = support._independent_binding(
        coordinate,
        density=(1.0, 1.0),
        beta=((0.0, 0.0, 0.0), (0.999999999999, 0.0, 0.0)),
    )
    profiles = support._profiles(coordinate, energy_x=1.0e-16)
    result = support._certify(binding, profiles)
    witness = result.segments[0]
    actual = EV.all_sky_doppler_bounds(
        (0.0, 0.0, 0.0), binding.schedule.at(1.0).beta_normal
    ).maximum
    if witness.doppler_max_upper < actual:
        raise AssertionError("equal-density near-null live endpoint escaped bound")

    # Scalar affine arithmetic can exceed equal endpoint floats by one ULP.
    binding = support._independent_binding(coordinate)
    profiles = support._profiles(coordinate, energy_x=0.0)
    profiles["photon_energy"] = ET.ScalarTrajectoryProfile.hard_photon_energy_j(
        [0.0, 1.0], [1.0e-316, 1.0e-316], source_frame="source",
        coordinate=coordinate, provenance=support.ENERGY_PROVENANCE,
    )
    result = support._certify(binding, profiles)
    if result.segments[0].source_energy_max_j < profiles["photon_energy"].at(0.1):
        raise AssertionError("scalar interpolation overshoot escaped energy bound")

    # Exact cold zero remains exact even under zero caller budgets.
    binding = support._independent_binding(coordinate)
    profiles = support._profiles(coordinate, energy_x=0.0, temp=0.0)
    result = support._certify(
        binding, profiles, budget=support._budget(error=0.0, theta=0.0)
    )
    witness = result.segments[0]
    if not result.certified or (
        witness.x_max_upper,
        witness.theta_max_upper,
        witness.total_cross_section_relative_deficit_upper,
    ) != (0.0, 0.0, 0.0):
        raise AssertionError("exact-zero cold limit was not preserved")

    return fail_closed


def _independent_exact_integral(profile, lo, hi):
    knots = [lo]
    knots.extend(value for value in profile.tau_nodes if lo < value < hi)
    knots.append(hi)
    total = 0.0
    for left, right in zip(knots[:-1], knots[1:]):
        total += 0.5 * (right - left) * (profile.at(left) + profile.at(right))
    return total


def main():
    rng = np.random.default_rng(2026082347)
    coordinate = support._coordinate("hostile-origin")
    max_doppler_ratio = 0.0
    max_x_ratio = 0.0
    stationary_count = 0
    numeric_domain_fail_closed = _deterministic_numeric_falsifiers(coordinate)

    for _ in range(180):
        tau = (0.0, rng.uniform(0.15, 0.85), 1.0)
        density = 10.0 ** rng.uniform(-4.0, 12.0, size=3)
        beta_e = np.asarray([_beta(rng) for _ in tau])
        schedule = ER.PrescribedIndependentElectronSchedule(
            tau, density, beta_e, provenance=support.SCHEDULE_PROVENANCE
        )
        binding = ET.ElectronScheduleBinding.bind(
            schedule, coordinate=coordinate, provenance=support.BINDING_PROVENANCE
        )
        source_beta = np.asarray([_beta(rng) for _ in tau])
        energy_x = 10.0 ** rng.uniform(-12.0, -4.0, size=3)
        profiles = _profile_set(coordinate, tau, source_beta, energy_x)
        result = support._certify(binding, profiles)
        ratios = _check_certificate(result, binding, profiles)
        max_doppler_ratio = max(max_doppler_ratio, ratios[0])
        max_x_ratio = max(max_x_ratio, ratios[1])
        stationary_count += sum(
            len(item.electron_gamma_stationary_fractions)
            for item in result.segments
        )

    for _ in range(120):
        tau = (0.0, rng.uniform(0.2, 0.8), 1.0)
        density = 10.0 ** rng.uniform(-4.0, 12.0, size=3)
        schedule = ER.PrescribedComovingElectronSchedule(
            tau, density, provenance=support.SCHEDULE_PROVENANCE
        )
        binding = ET.ElectronScheduleBinding.bind(
            schedule, coordinate=coordinate, provenance=support.BINDING_PROVENANCE
        )
        source_beta = np.asarray([_beta(rng) for _ in tau])
        fluid_beta = np.asarray([_beta(rng) for _ in tau])
        profiles = _profile_set(
            coordinate, tau, source_beta,
            10.0 ** rng.uniform(-12.0, -4.0, size=3),
        )
        fluid = ET.BetaTrajectoryProfile.live_fluid(
            tau, fluid_beta, frame_id="fluid", coordinate=coordinate,
            provenance=support.FLUID_PROVENANCE,
        )
        result = support._certify(binding, profiles, fluid_frame=fluid)
        ratios = _check_certificate(result, binding, profiles, fluid)
        max_doppler_ratio = max(max_doppler_ratio, ratios[0])
        max_x_ratio = max(max_x_ratio, ratios[1])

    near_null_schedules = 0
    for lane in ("independent", "comoving"):
        for _ in range(50):
            tau = (0.0, rng.uniform(0.25, 0.75), 1.0)
            source_beta = np.asarray([_near_null_beta(rng) for _ in tau])
            profiles = _profile_set(
                coordinate, tau, source_beta, [1.0e-16] * len(tau)
            )
            if lane == "independent":
                schedule = ER.PrescribedIndependentElectronSchedule(
                    tau,
                    [1.0, 1.0, 1.0],
                    np.asarray([_near_null_beta(rng) for _ in tau]),
                    provenance=support.SCHEDULE_PROVENANCE,
                )
                fluid = None
            else:
                schedule = ER.PrescribedComovingElectronSchedule(
                    tau, [1.0, 1.0, 1.0],
                    provenance=support.SCHEDULE_PROVENANCE,
                )
                fluid = ET.BetaTrajectoryProfile.live_fluid(
                    tau,
                    np.asarray([_near_null_beta(rng) for _ in tau]),
                    frame_id="fluid",
                    coordinate=coordinate,
                    provenance=support.FLUID_PROVENANCE,
                )
            binding = ET.ElectronScheduleBinding.bind(
                schedule,
                coordinate=coordinate,
                provenance=support.BINDING_PROVENANCE,
            )
            result = support._certify(binding, profiles, fluid_frame=fluid)
            if result.status is ET.TrajectoryStatus.UNVERIFIED_NUMERIC_DOMAIN:
                numeric_domain_fail_closed += 1
            ratios = _check_certificate(result, binding, profiles, fluid)
            max_doppler_ratio = max(max_doppler_ratio, ratios[0])
            max_x_ratio = max(max_x_ratio, ratios[1])
            near_null_schedules += 1

    exponent_span_schedules = 0
    for _ in range(100):
        tau = (0.0, rng.uniform(0.2, 0.8), 1.0)
        density = 10.0 ** rng.uniform(-300.0, 300.0, size=3)
        beta_e = np.asarray([_near_null_beta(rng) for _ in tau])
        schedule = ER.PrescribedIndependentElectronSchedule(
            tau, density, beta_e, provenance=support.SCHEDULE_PROVENANCE
        )
        binding = ET.ElectronScheduleBinding.bind(
            schedule, coordinate=coordinate,
            provenance=support.BINDING_PROVENANCE,
        )
        profiles = _profile_set(
            coordinate,
            tau,
            np.asarray([_beta(rng) for _ in tau]),
            [1.0e-18] * len(tau),
        )
        result = support._certify(binding, profiles)
        if result.status is ET.TrajectoryStatus.UNVERIFIED_NUMERIC_DOMAIN:
            numeric_domain_fail_closed += 1
        ratios = _check_certificate(result, binding, profiles)
        max_doppler_ratio = max(max_doppler_ratio, ratios[0])
        max_x_ratio = max(max_x_ratio, ratios[1])
        exponent_span_schedules += 1

    max_integral_relative_error = 0.0
    for _ in range(400):
        nodes = np.sort(np.concatenate(([0.0, 1.0], rng.uniform(0.0, 1.0, 4))))
        values = 10.0 ** rng.uniform(-8.0, 4.0, size=len(nodes))
        profile = ET.ScalarTrajectoryProfile.local_ray_rate_per_tau(
            nodes, values, coordinate=coordinate,
            provenance=support.RATE_PROVENANCE,
        )
        first, last = sorted(rng.uniform(0.0, 1.0, size=2))
        expected = _independent_exact_integral(profile, first, last)
        future = ET.integrate_optical_depth(
            profile, first, last, ET.IntegrationOrientation.FUTURE_KINETIC_IVP
        )
        past = ET.integrate_optical_depth(
            profile, last, first,
            ET.IntegrationOrientation.PAST_LIGHT_CONE_ACCUMULATION,
        )
        if future.depth_increment != past.depth_increment:
            raise AssertionError("paired traversal depths are not bit-identical")
        scale = max(expected, np.finfo(float).tiny)
        max_integral_relative_error = max(
            max_integral_relative_error,
            abs(future.depth_increment - expected) / scale,
        )
        if future.derivative_sign != 1 or past.derivative_sign != -1:
            raise AssertionError("orientation derivative sign mismatch")

    if max_integral_relative_error > 8.0e-14:
        raise AssertionError(
            f"piecewise-linear integral mismatch {max_integral_relative_error}"
        )

    report = {
        "schema": "bass.e4_trajectory_hostile_audit/v1",
        "status": "PASS",
        "independent_schedules": 180,
        "comoving_schedules": 120,
        "sampled_points_per_segment_max": 43,
        "edge_neighbor_samples_per_segment": 2,
        "orientation_trials": 400,
        "near_null_schedules": near_null_schedules,
        "exponent_span_schedules": exponent_span_schedules,
        "numeric_domain_fail_closed": numeric_domain_fail_closed,
        "interior_stationary_candidates_seen": stationary_count,
        "max_actual_over_doppler_upper": max_doppler_ratio,
        "max_actual_over_x_upper": max_x_ratio,
        "max_integral_relative_error": max_integral_relative_error,
        "q_collision_generator_wired": False,
        "production_runtime_wired": False,
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
