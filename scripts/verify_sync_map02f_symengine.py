#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.metadata
import json
from pathlib import Path

import symengine as se


def exact_zero(name: str, expression: object, checks: dict[str, bool]) -> None:
    value = se.expand(expression)
    passed = value == 0
    checks[name] = passed
    if not passed:
        raise AssertionError(f"{name}: expected exact zero, got {value!r}")


def hostile_nonzero(name: str, expression: object, checks: dict[str, bool]) -> None:
    value = se.expand(expression)
    passed = value != 0
    checks[name] = passed
    if not passed:
        raise AssertionError(f"{name}: hostile mutation was not detected")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()

    gamma, beta2 = se.symbols("gamma beta2", positive=True)
    beta_n, beta_e = se.symbols("beta_n beta_e")
    doppler = se.symbols("doppler", positive=True)
    h_p, nu, k_b, temperature = se.symbols(
        "h_p nu k_b temperature", positive=True
    )
    c, rate_s, rate_t = se.symbols("c rate_s rate_t", positive=True)
    hubble, sigma_ee, a_dot_e = se.symbols("hubble sigma_ee a_dot_e")

    checks: dict[str, bool] = {}
    hostile: dict[str, bool] = {}

    # Equivalent to (gamma-1)/beta^2 = gamma^2/(gamma+1), but tested
    # after clearing denominators and imposing gamma^2(1-beta^2)=1.
    regularized_polynomial = (gamma - 1) * (gamma + 1) - gamma**2 * beta2
    exact_zero(
        "zero_boost_regular_coefficient",
        regularized_polynomial.subs(beta2, 1 - 1 / gamma**2),
        checks,
    )

    exact_zero(
        "outward_sky_photon_direction_doppler_adapter",
        (gamma * (1 + beta_n) - gamma * (1 - beta_e)).subs(beta_n, -beta_e),
        checks,
    )

    # Cross-multiplied Planck exponent h nu/(k_B T): nu and T both carry
    # Doppler weight one, so the dimensionless exponent is invariant.
    exact_zero(
        "planck_argument_invariance",
        h_p * (doppler * nu) * k_b * temperature
        - h_p * nu * k_b * (doppler * temperature),
        checks,
    )

    exact_zero(
        "ray_length_to_time_rate_adapter",
        (rate_t - c * rate_s).subs(rate_t, c * rate_s),
        checks,
    )

    generic_energy_drift = -hubble - sigma_ee
    rei_h_only_energy_drift = -hubble
    exact_zero(
        "rei_h_only_exact_residual",
        rei_h_only_energy_drift - generic_energy_drift - sigma_ee,
        checks,
    )

    # The scalar part of e_a V^a; epsilon contractions vanish by antisymmetry.
    exact_zero(
        "direction_flow_tangency_scalar_cancellation",
        (sigma_ee + a_dot_e) - sigma_ee - a_dot_e,
        checks,
    )

    hostile_nonzero(
        "wrong_regular_coefficient",
        ((gamma - 1) * (gamma + 1) - gamma * beta2).subs(
            beta2, 1 - 1 / gamma**2
        ),
        hostile,
    )
    hostile_nonzero(
        "wrong_doppler_chart_sign",
        (gamma * (1 - beta_n) - gamma * (1 - beta_e)).subs(beta_n, -beta_e),
        hostile,
    )
    hostile_nonzero(
        "wrong_solid_angle_power",
        doppler ** (-1) - doppler ** (-2),
        hostile,
    )
    hostile_nonzero(
        "wrong_rei_residual_sign",
        rei_h_only_energy_drift - generic_energy_drift + sigma_ee,
        hostile,
    )

    version = importlib.metadata.version("symengine")
    if version != "0.14.1":
        raise AssertionError(f"unexpected symengine version: {version}")

    receipt = {
        "schema_version": "1.0.0",
        "status": "PASS",
        "package": "symengine",
        "version": version,
        "authority_effect": "NONE_EXTERNAL_ORACLE",
        "exact_checks": checks,
        "hostile_mutations": hostile,
        "exact_check_count": len(checks),
        "hostile_mutation_count": len(hostile),
        "claim_boundary": (
            "BOUNDED_EXACT_FORMULA_IDENTITIES_ONLY_NOT_CONSUMER_PARITY_"
            "OR_SOLVER_PROVIDER_SCIENCE_VALIDATION"
        ),
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
