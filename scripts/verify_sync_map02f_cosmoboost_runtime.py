#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.metadata
import json
import math
from pathlib import Path

import numpy as np

# CosmoBoost 1.1.6 predates NumPy's removal of these aliases.  The shims
# preserve Python scalar semantics and are recorded as compatibility-only.
if not hasattr(np, "complex"):
    np.complex = complex  # type: ignore[attr-defined]
if not hasattr(np, "float"):
    np.float = float  # type: ignore[attr-defined]
if not hasattr(np, "int"):
    np.int = int  # type: ignore[attr-defined]

import cosmoboost as cb


def kernel_parameters(*, beta: float, method: str) -> dict[str, object]:
    pars = dict(cb.DEFAULT_PARS)
    pars.update(
        {
            "d": 1,
            "s": 0,
            "beta": beta,
            "lmin": 0,
            "lmax": 12,
            "delta_ell": 4,
            "method": method,
            "frequency_function": "CMB",
            "normalize": True,
        }
    )
    return pars


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()

    version = importlib.metadata.version("cosmoboost")
    if version != "1.1.6":
        raise AssertionError(f"unexpected cosmoboost version: {version}")

    zero_kernel = cb.Kernel(
        kernel_parameters(beta=0.0, method="Bessel"),
        overwrite=True,
        save_kernel=False,
    )
    centre = zero_kernel.delta_ell
    identity_centre_residual = float(
        np.max(np.abs(zero_kernel.mLl[:, centre] - 1.0))
    )
    off_centre = np.delete(zero_kernel.mLl, centre, axis=1)
    identity_off_residual = float(np.max(np.abs(off_centre)))

    beta = 0.00123
    kernel = cb.Kernel(
        kernel_parameters(beta=beta, method="ODE"),
        overwrite=True,
        save_kernel=False,
    )

    # For a pure monopole and d=1, the first-order dipole-to-monopole ratio
    # has magnitude beta/sqrt(3).  The sign is convention dependent and is
    # recorded rather than promoted into BASS authority.
    output_l = 1
    input_l = 0
    row = output_l  # m=0 rows occupy indices L=0,...,lmax.
    column = kernel.delta_ell + input_l - output_l
    monopole_to_dipole = float(kernel.mLl[row, column])
    expected_magnitude = beta / math.sqrt(3.0)
    dipole_magnitude_residual = abs(abs(monopole_to_dipole) - expected_magnitude)

    transfer = np.asarray(kernel.Ll, dtype=float)
    interior = transfer[kernel.delta_ell : kernel.lmax - kernel.delta_ell + 1]
    power_row_sum_residual = float(np.max(np.abs(np.sum(interior, axis=1) - 1.0)))

    tolerances = {
        "beta_zero_identity": 5.0e-14,
        "small_beta_dipole_magnitude": 5.0e-6,
        "interior_power_transfer_row_sum": 5.0e-3,
    }
    residuals = {
        "identity_centre": identity_centre_residual,
        "identity_off_centre": identity_off_residual,
        "small_beta_dipole_magnitude": dipole_magnitude_residual,
        "interior_power_transfer_row_sum": power_row_sum_residual,
    }
    if identity_centre_residual > tolerances["beta_zero_identity"]:
        raise AssertionError(f"beta=0 centre is not identity: {identity_centre_residual}")
    if identity_off_residual > tolerances["beta_zero_identity"]:
        raise AssertionError(f"beta=0 off-diagonal leakage: {identity_off_residual}")
    if dipole_magnitude_residual > tolerances["small_beta_dipole_magnitude"]:
        raise AssertionError(
            "small-beta monopole/dipole magnitude mismatch: "
            f"observed={monopole_to_dipole}, expected |.|={expected_magnitude}"
        )
    if power_row_sum_residual > tolerances["interior_power_transfer_row_sum"]:
        raise AssertionError(
            f"interior d=1 power-transfer normalization drift: {power_row_sum_residual}"
        )

    receipt = {
        "schema_version": "1.0.0",
        "status": "PASS",
        "package": "cosmoboost",
        "version": version,
        "authority_effect": "NONE_EXTERNAL_ORACLE",
        "runtime_scope": "d=1, s=0 harmonic kernel only",
        "parameters": {
            "beta": beta,
            "lmax": kernel.lmax,
            "delta_ell": kernel.delta_ell,
            "method": kernel.method,
        },
        "compatibility_shims": ["numpy.complex", "numpy.float", "numpy.int"],
        "residuals": residuals,
        "tolerances": tolerances,
        "monopole_to_dipole_coefficient": monopole_to_dipole,
        "expected_first_order_magnitude": expected_magnitude,
        "convention_sign": "positive" if monopole_to_dipole >= 0.0 else "negative",
        "claim_boundary": (
            "D1_S0_EXTERNAL_HARMONIC_REGRESSION_ONLY_NOT_BASS_HTT_"
            "SOFTWARE_PARITY_SPECTRAL_POLARIZATION_OR_SOLVER_VALIDATION"
        ),
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
