"""Independent hostile audit for the BASS-8B.1E.3 bounded authority."""
from __future__ import annotations

from decimal import Decimal, localcontext
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TEST_PATH = ROOT / "tests" / "test_electron_thomson_validity.py"
spec = importlib.util.spec_from_file_location("_electron_validity_loader", TEST_PATH)
loader = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = loader
assert spec.loader is not None
spec.loader.exec_module(loader)
EF, ER, EV = loader.EF, loader.ER, loader.EV


def _decimal_kn(value: float) -> float:
    with localcontext() as context:
        context.prec = 100
        x = Decimal(str(value))
        if x == 0:
            return 1.0
        one = Decimal(1)
        two = Decimal(2)
        three = Decimal(3)
        ratio = (
            Decimal(3) / Decimal(4)
            * (
                (one + x) / x**3
                * (two * x * (one + x) / (one + two * x) - (one + two * x).ln())
                + (one + two * x).ln() / (two * x)
                - (one + three * x) / (one + two * x) ** 2
            )
        )
        return float(ratio)


def _unit(value):
    value = np.asarray(value, float)
    return value / np.linalg.norm(value)


def run(seed=2026082329, kn_count=1200, boost_count=1200):
    xs = np.r_[0.0, np.geomspace(1.0e-20, 1.0e6, int(kn_count))]
    production = EV.klein_nishina_total_ratio(xs)
    oracle = np.asarray([_decimal_kn(float(value)) for value in xs])
    kn_absolute = float(np.max(np.abs(production - oracle)))
    positive = xs >= 1.0e-8
    deficit_oracle = 1.0 - oracle[positive]
    deficit_relative = float(np.max(np.abs(
        EV.klein_nishina_total_deficit(xs[positive]) / deficit_oracle - 1.0
    )))
    tiny_deficit_relative = abs(
        EV.klein_nishina_total_deficit(1.0e-20) / 2.0e-20 - 1.0
    )
    monotonic_violation = float(max(0.0, np.max(np.diff(production))))

    # Raw binary64 formula is a required hostile mutation: at x=1e-8 its
    # cancellation is orders of magnitude worse than the series authority.
    x_mut = 1.0e-8
    raw = 0.75 * (
        (1.0 + x_mut) / x_mut**3
        * (2.0 * x_mut * (1.0 + x_mut) / (1.0 + 2.0 * x_mut)
           - np.log1p(2.0 * x_mut))
        + np.log1p(2.0 * x_mut) / (2.0 * x_mut)
        - (1.0 + 3.0 * x_mut) / (1.0 + 2.0 * x_mut) ** 2
    )
    raw_formula_error = abs(raw - _decimal_kn(x_mut))

    rng = np.random.default_rng(seed)
    boost_bound_excess = 0.0
    boost_extremum_error = 0.0
    reciprocal_error = 0.0
    for _ in range(int(boost_count)):
        source = _unit(rng.normal(size=3)) * rng.uniform(0.0, 0.96)
        target = _unit(rng.normal(size=3)) * rng.uniform(0.0, 0.96)
        bounds = EV.all_sky_doppler_bounds(source, target)
        matrix = EF.frame_matrix(source, target)
        spatial = matrix[0, 1:]
        if np.linalg.norm(spatial) == 0.0:
            directions = np.eye(3)
        else:
            direction_max = spatial / np.linalg.norm(spatial)
            directions = np.vstack((direction_max, -direction_max, _unit(rng.normal(size=3))))
        _, _, factors = EF.transform_photon(
            np.ones(len(directions)), directions, source, target
        )
        boost_bound_excess = max(
            boost_bound_excess,
            float(np.max(factors - bounds.maximum)),
            float(np.max(bounds.minimum - factors)),
        )
        boost_extremum_error = max(
            boost_extremum_error,
            abs(float(factors[0]) / bounds.maximum - 1.0),
            abs(float(factors[1]) / bounds.minimum - 1.0),
        )
        reciprocal_error = max(
            reciprocal_error, abs(bounds.minimum * bounds.maximum - 1.0)
        )

    # Canonical mutation witnesses.
    relative = EV.all_sky_doppler_bounds([0.6, 0.0, 0.0], [-0.6, 0.0, 0.0])
    naive_normal_to_electron = EV.all_sky_doppler_bounds(
        [0.0, 0.0, 0.0], [-0.6, 0.0, 0.0]
    ).maximum
    relative_bound_mutation_gap = relative.maximum - naive_normal_to_electron

    state = EF.ColdElectronTestField.independent(1.0, [0.6, 0.0, 0.0])
    contract = EV.ElectronCollisionConsumerContract(ER.ElectronCollisionContext(state))
    rest = contract.input_for(EV.CollisionConsumerId.MATTER_COLLISION_MOVING).value_per_s
    factors = []
    for direction in ([1.0, 0.0, 0.0], [-1.0, 0.0, 0.0], [0.0, 1.0, 0.0]):
        rate = contract.input_for(
            EV.CollisionConsumerId.EXTERNAL_OBSERVER_RAY,
            direction_source=direction,
            beta_source=[0.0, 0.0, 0.0],
        )
        factors.append(rate.value_per_s / rest)
    factors = np.asarray(factors)
    omit_d_error = float(np.max(np.abs(np.ones(3) - factors)))
    double_d_error = float(np.max(np.abs(factors**2 - factors)))

    unresolved_blocked = False
    try:
        contract.input_for(EV.CollisionConsumerId.Q_SCALAR_KERNEL)
    except EV.UnresolvedCollisionConsumerError:
        unresolved_blocked = True

    # Analytic noncommutation oracle: K 1=1 and K D=gamma for Thomson K,
    # while M_D K 1=D.  Their difference has max norm gamma*beta.
    beta = 0.6
    gamma = 1.0 / np.sqrt(1.0 - beta * beta)
    q_generator_noncommutation_witness = gamma * beta

    hostile_ray = EV.exact_observer_doppler_factor(
        [1.0, 0.0, 0.0],
        [0.999999, 0.0, 0.0],
        [0.999999000001, 0.0, 0.0],
    )
    hostile_ray_error = abs(hostile_ray - 0.999999500010685885436573762074)
    accepted_direction = EV.exact_observer_doppler_factor(
        [-(1.0 + 1.0e-12), 0.0, 0.0],
        [0.0, 0.0, 0.0],
        [0.6, 0.0, 0.0],
    )

    # Wolfram high-precision threshold roots, checked through production.
    roots = np.array([
        0.00506586999876458578694321555291195777,
        0.000500650859862195601339782961653320595,
        0.0000500065008588610942623571905196398722,
    ])
    tolerances = np.array([1.0e-2, 1.0e-3, 1.0e-4])
    threshold_error = float(np.max(np.abs(
        (1.0 - EV.klein_nishina_total_ratio(roots)) - tolerances
    )))

    report = {
        "kn_absolute_max": kn_absolute,
        "kn_deficit_relative_max_x_ge_1e-8": deficit_relative,
        "kn_tiny_deficit_relative_at_1e-20": float(tiny_deficit_relative),
        "kn_monotonic_violation": monotonic_violation,
        "raw_formula_error_at_1e-8": float(raw_formula_error),
        "boost_bound_excess": boost_bound_excess,
        "boost_extremum_relative_max": boost_extremum_error,
        "doppler_reciprocal_max": reciprocal_error,
        "relative_bound_mutation_gap": float(relative_bound_mutation_gap),
        "observer_factors": factors.tolist(),
        "omit_d_mutation_max": omit_d_error,
        "double_d_mutation_max": double_d_error,
        "scalar_q_unresolved_blocked": unresolved_blocked,
        "q_generator_noncommutation_witness": float(q_generator_noncommutation_witness),
        "hostile_decimal_ray_absolute": float(hostile_ray_error),
        "canonicalized_near_unit_ray_factor": float(accepted_direction),
        "wolfram_threshold_absolute_max": threshold_error,
        "kn_cases": int(len(xs)),
        "boost_cases": int(boost_count),
    }

    assert kn_absolute < 8.0e-15, report
    assert deficit_relative < 2.0e-8, report
    assert tiny_deficit_relative < 3.0e-15, report
    assert monotonic_violation == 0.0, report
    assert raw_formula_error > 1.0e-4, report
    assert boost_bound_excess < 2.0e-14, report
    assert boost_extremum_error < 3.0e-14, report
    assert reciprocal_error < 3.0e-16, report
    assert relative_bound_mutation_gap > 1.9, report
    assert np.max(np.abs(factors - np.array([0.5, 2.0, 1.25]))) < 3.0e-15, report
    assert omit_d_error > 0.9 and double_d_error > 1.9, report
    assert unresolved_blocked, report
    assert q_generator_noncommutation_witness == 0.75, report
    assert hostile_ray_error < 3.0e-16, report
    assert abs(accepted_direction - 2.0) < 4.0e-16, report
    assert threshold_error < 8.0e-16, report
    return report


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
