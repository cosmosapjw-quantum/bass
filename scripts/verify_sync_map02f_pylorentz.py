#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.metadata
import json
from pathlib import Path

import numpy as np
from pylorentz import Momentum4


def unit_vector(rng: np.random.Generator) -> np.ndarray:
    vector = rng.normal(size=3)
    return vector / np.linalg.norm(vector)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--samples", type=int, default=256)
    args = parser.parse_args()

    rng = np.random.default_rng(20260903)
    max_residuals = {
        "null_norm": 0.0,
        "doppler_energy": 0.0,
        "propagation_direction": 0.0,
        "inverse_round_trip": 0.0,
        "outward_sky_sign_adapter": 0.0,
    }
    minimum_hostile_signal = float("inf")

    for index in range(args.samples):
        e = unit_vector(rng)
        beta_hat = unit_vector(rng)
        beta = float(rng.uniform(1.0e-8, 0.75))
        beta_vector = beta * beta_hat
        gamma = 1.0 / np.sqrt(1.0 - beta * beta)
        energy = float(0.5 + rng.random())

        photon = Momentum4(energy, *(energy * e))
        boosted = photon.boost(*beta_hat, beta=beta)
        components = np.asarray(boosted.components, dtype=float)
        energy_prime = float(components[0])
        momentum_prime = components[1:]

        beta_dot_e = float(np.dot(beta_vector, e))
        doppler_photon = gamma * (1.0 - beta_dot_e)
        expected_energy = energy * doppler_photon
        expected_momentum = energy * e + energy * (
            ((gamma - 1.0) * beta_dot_e / (beta * beta)) - gamma
        ) * beta_vector
        expected_direction = expected_momentum / expected_energy
        observed_direction = momentum_prime / energy_prime

        recovered = boosted.boost(*(-beta_hat), beta=beta)
        recovered_components = np.asarray(recovered.components, dtype=float)
        original_components = np.asarray(photon.components, dtype=float)

        n_sky = -e
        doppler_sky = gamma * (1.0 + float(np.dot(beta_vector, n_sky)))

        max_residuals["null_norm"] = max(
            max_residuals["null_norm"],
            abs(energy_prime * energy_prime - float(np.dot(momentum_prime, momentum_prime))),
        )
        max_residuals["doppler_energy"] = max(
            max_residuals["doppler_energy"],
            abs(energy_prime - expected_energy),
        )
        max_residuals["propagation_direction"] = max(
            max_residuals["propagation_direction"],
            float(np.max(np.abs(observed_direction - expected_direction))),
        )
        max_residuals["inverse_round_trip"] = max(
            max_residuals["inverse_round_trip"],
            float(np.max(np.abs(recovered_components - original_components))),
        )
        max_residuals["outward_sky_sign_adapter"] = max(
            max_residuals["outward_sky_sign_adapter"],
            abs(doppler_sky - doppler_photon),
        )

        wrong_sign_energy = energy * gamma * (1.0 + beta_dot_e)
        hostile_signal = abs(wrong_sign_energy - energy_prime)
        if abs(beta_dot_e) > 1.0e-3:
            minimum_hostile_signal = min(minimum_hostile_signal, hostile_signal)

    tolerance = 2.0e-12
    failed = {name: value for name, value in max_residuals.items() if value > tolerance}
    if failed:
        raise AssertionError(f"pylorentz residuals exceed tolerance: {failed}")
    if not np.isfinite(minimum_hostile_signal) or minimum_hostile_signal <= 1.0e-6:
        raise AssertionError(
            f"wrong-sign hostile mutation is insufficiently separated: {minimum_hostile_signal}"
        )

    version = importlib.metadata.version("pylorentz")
    if version != "0.3.3":
        raise AssertionError(f"unexpected pylorentz version: {version}")

    receipt = {
        "schema_version": "1.0.0",
        "status": "PASS",
        "package": "pylorentz",
        "version": version,
        "authority_effect": "NONE_EXTERNAL_ORACLE",
        "metric_signature_adapter": "package (+---) invariant; project metric (-+++) differs by overall sign",
        "boost_semantics": "frame moving along beta; energy factor gamma*(1-beta.e)",
        "samples": args.samples,
        "tolerance": tolerance,
        "max_residuals": max_residuals,
        "minimum_wrong_sign_hostile_signal": minimum_hostile_signal,
        "claim_boundary": (
            "NULL_FOUR_VECTOR_LORENTZ_KINEMATICS_ONLY_NOT_HARMONIC_"
            "CONSUMER_COLLISION_PROVIDER_OR_SCIENCE_PARITY"
        ),
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
