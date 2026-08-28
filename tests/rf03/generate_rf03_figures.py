"""Generate the four bounded RF-03 scientific diagnostics.

This script is intentionally deterministic and writes no figures outside the
RF-03 evidence directory.  It also records the raw numerical arrays and the
four required hostile-mutation outcomes for later human readback.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import matplotlib

os.environ.setdefault("JAX_PLATFORMS", "cpu")
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

MODEL_ID = "explicit_gamma_law_tilted_perfect_fluid_v1"
OUTPUT_DIRECTORY = ROOT / "artifacts/rust_first_runtime/rf03/figures"
FIGURES = (
    "native_oracle_force_jvp_residual.png",
    "log_density_vs_log_mean_scale.png",
    "tilt_normalization_and_domain_margin.png",
    "entropy_temperature_invariant.png",
)
PLOT_FLOOR = 1.0e-18


def _native():
    import bianchi_rustcore

    return bianchi_rustcore


def _json_float(value: float) -> float:
    observed = float(value)
    if not np.isfinite(observed):
        raise ValueError(f"nonfinite evidence value: {observed}")
    return observed


def _array(values) -> list[float]:
    return [_json_float(value) for value in np.asarray(values).ravel()]


def _save_figure(figure: plt.Figure, path: Path) -> None:
    figure.savefig(
        path,
        dpi=140,
        bbox_inches="tight",
        metadata={"Software": "BASS RF-03 bounded figure generator"},
    )
    plt.close(figure)


def _force_jvp_diagnostic() -> dict:
    import jax
    import jax.numpy as jnp

    from bianchi.matter.fluid import TiltedFluid, dOmega, dv_general, sources

    jax.config.update("jax_enable_x64", True)
    native = _native()
    gamma = 1.31
    scales = np.geomspace(1.0e-4, 1.0, 17)
    base_state = np.array([0.37, 0.13, -0.08, 0.04], dtype=np.float64)
    direction = np.array([0.07, 0.03, -0.02, 0.04], dtype=np.float64)
    # Deliberately nonsymmetric matrices expose row/column and cross-product
    # orientation errors that symmetric fixtures cannot detect.
    sigma = np.array(
        [[0.07, -0.02, 0.01], [0.04, -0.04, 0.03], [0.01, -0.05, -0.03]],
        dtype=np.float64,
    )
    n = np.array(
        [[0.2, 0.03, -0.01], [-0.02, -0.1, 0.04], [0.06, 0.01, 0.05]],
        dtype=np.float64,
    )
    a = np.array([0.04, -0.03, 0.02], dtype=np.float64)
    r = np.array([-0.02, 0.01, 0.03], dtype=np.float64)
    q = 0.41
    force_residual = []
    jvp_residual = []

    for scale in scales:
        state = scale * base_state

        def oracle(x):
            fluid = TiltedFluid.of(gamma, x[0], x[1:])
            source = sources(fluid, sigma, a)
            return jnp.concatenate(
                (
                    jnp.atleast_1d(dOmega(fluid, source, q)),
                    dv_general(fluid, source, sigma, n, a, r),
                )
            )

        expected_force, expected_jvp = jax.jvp(
            oracle,
            (jnp.asarray(state),),
            (jnp.asarray(direction),),
        )
        observed_force, observed_jvp = native.rf03_matter_force_jvp(
            MODEL_ID,
            gamma,
            np.ascontiguousarray(state),
            direction,
            sigma,
            n,
            a,
            r,
            q,
            2.7255,
        )
        force_residual.append(
            np.max(np.abs(np.asarray(observed_force) - np.asarray(expected_force)))
        )
        jvp_residual.append(
            np.max(np.abs(np.asarray(observed_jvp) - np.asarray(expected_jvp)))
        )

    force_residual = np.asarray(force_residual)
    jvp_residual = np.asarray(jvp_residual)
    figure, axis = plt.subplots(figsize=(6.4, 4.2), constrained_layout=True)
    axis.loglog(
        scales,
        np.maximum(force_residual, PLOT_FLOOR),
        "o-",
        label="force max |native - oracle|",
    )
    axis.loglog(
        scales,
        np.maximum(jvp_residual, PLOT_FLOOR),
        "s-",
        label="JVP max |native - oracle|",
    )
    axis.axhline(
        PLOT_FLOOR,
        color="0.45",
        linestyle=":",
        linewidth=1.0,
        label=f"display floor {PLOT_FLOOR:.0e} (raw zeros in JSON)",
    )
    axis.set_xlabel("state scale s (dimensionless)")
    axis.set_ylabel("maximum absolute residual")
    axis.set_title("RF-03 native/oracle parity (nonsymmetric context)")
    axis.grid(True, which="both", alpha=0.25)
    axis.legend(loc="best", fontsize="small")
    _save_figure(figure, OUTPUT_DIRECTORY / FIGURES[0])
    return {
        "state_scale": _array(scales),
        "force_max_abs_residual": _array(force_residual),
        "jvp_max_abs_residual": _array(jvp_residual),
        "max_force_residual": _json_float(np.max(force_residual)),
        "max_jvp_residual": _json_float(np.max(jvp_residual)),
        "plot_floor": PLOT_FLOOR,
        "units": "dimensionless normalized dynamical variables",
    }


def _density_scale_diagnostic() -> tuple[dict, dict]:
    native = _native()
    gamma = 4.0 / 3.0
    q = 0.5
    omega0 = 0.5
    zero3 = np.zeros(3, dtype=np.float64)
    zero33 = np.zeros((3, 3), dtype=np.float64)
    result = native.rf03_matter_integrate(
        MODEL_ID,
        gamma,
        np.array([omega0, 0.0, 0.0, 0.0], dtype=np.float64),
        zero33,
        zero33,
        zero3,
        zero3,
        q,
        1.0,
        400,
        2.7255,
    )
    if result["status"] != "COMPLETE":
        raise RuntimeError(f"density diagnostic terminated: {result['status']}")
    times = np.asarray(result["times"], dtype=np.float64)
    states = np.asarray(result["states"], dtype=np.float64)
    ell = np.exp(times)
    hubble_over_h0 = np.exp(-(1.0 + q) * times)
    density_over_h0_squared = 3.0 * hubble_over_h0**2 * states[:, 0]
    observed_slope, intercept = np.polyfit(
        np.log(ell), np.log(density_over_h0_squared), 1
    )
    expected_slope = -3.0 * gamma

    correct_coefficient = 2.0 * q - (3.0 * gamma - 2.0)
    mutated_coefficient = -2.0 * q - (3.0 * gamma - 2.0)
    mutated_omega = omega0 * np.exp(mutated_coefficient * times)
    mutated_density = 3.0 * hubble_over_h0**2 * mutated_omega
    mutated_slope = float(
        np.polyfit(np.log(ell), np.log(mutated_density), 1)[0]
    )
    native_initial_force = float(
        native.rf03_matter_force(
            MODEL_ID,
            gamma,
            np.array([omega0, 0.0, 0.0, 0.0], dtype=np.float64),
            zero33,
            zero33,
            zero3,
            zero3,
            q,
            None,
        )[0]
    )
    mutated_initial_force = omega0 * mutated_coefficient
    mutation_residual = abs(native_initial_force - mutated_initial_force)

    figure, axis = plt.subplots(figsize=(6.4, 4.2), constrained_layout=True)
    axis.plot(
        np.log(ell),
        np.log(density_over_h0_squared),
        linewidth=2.0,
        label=f"native slope = {observed_slope:.9f}",
    )
    axis.plot(
        np.log(ell),
        np.log(mutated_density),
        "--",
        linewidth=1.5,
        label=f"hostile sign-flip slope = {mutated_slope:.1f}",
    )
    axis.plot(
        np.log(ell),
        intercept + expected_slope * np.log(ell),
        ":",
        color="black",
        linewidth=1.2,
        label=f"expected -3gamma = {expected_slope:.1f}",
    )
    axis.set_xlabel("log(ell / ell0)")
    axis.set_ylabel("log[rho / (H0 squared)]")
    axis.set_title("RF-03 zero-tilt cooling limit")
    axis.grid(True, alpha=0.25)
    axis.legend(loc="best", fontsize="small")
    _save_figure(figure, OUTPUT_DIRECTORY / FIGURES[1])

    data = {
        "log_ell": _array(np.log(ell)),
        "log_density_over_h0_squared": _array(np.log(density_over_h0_squared)),
        "native_slope": _json_float(observed_slope),
        "expected_slope": _json_float(expected_slope),
        "slope_abs_residual": _json_float(abs(observed_slope - expected_slope)),
        "hostile_sign_flip_slope": _json_float(mutated_slope),
        "units": {
            "ell_over_ell0": "dimensionless",
            "rho_over_h0_squared": "dimensionless",
        },
    }
    mutation = {
        "name": "expansion_term_sign_flip",
        "operation": "replace +2*q in dOmega coefficient by -2*q",
        "native_initial_dOmega": _json_float(native_initial_force),
        "mutated_initial_dOmega": _json_float(mutated_initial_force),
        "max_abs_detection_signal": _json_float(mutation_residual),
        "detected": bool(mutation_residual > 1.0e-6),
    }
    return data, mutation


def _tilt_diagnostic() -> tuple[dict, dict]:
    native = _native()
    sigma = np.array(
        [[0.03, 0.01, -0.02], [-0.015, -0.02, 0.025], [0.005, -0.01, -0.01]],
        dtype=np.float64,
    )
    n = np.array(
        [[0.08, -0.03, 0.015], [0.02, -0.04, 0.01], [-0.025, 0.035, 0.02]],
        dtype=np.float64,
    )
    a = np.array([0.015, -0.01, 0.008], dtype=np.float64)
    r = np.array([-0.012, 0.009, 0.014], dtype=np.float64)
    result = native.rf03_matter_integrate(
        MODEL_ID,
        1.25,
        np.array([0.35, 0.18, -0.09, 0.06], dtype=np.float64),
        sigma,
        n,
        a,
        r,
        0.4,
        1.0,
        400,
        2.7255,
    )
    if result["status"] != "COMPLETE":
        raise RuntimeError(f"tilt diagnostic terminated: {result['status']}")
    times = np.asarray(result["times"], dtype=np.float64)
    states = np.asarray(result["states"], dtype=np.float64)
    invariant_rows = [
        native.rf03_tilt_invariants(float(state[0]), state[1:]) for state in states
    ]
    u_norm_residual = np.abs(
        np.array([row["u_norm_residual"] for row in invariant_rows], dtype=np.float64)
    )
    density_margin = np.array(
        [row["density_margin"] for row in invariant_rows], dtype=np.float64
    )
    tilt_margin = np.array(
        [row["tilt_margin"] for row in invariant_rows], dtype=np.float64
    )
    velocity_squared = np.sum(states[:, 1:] ** 2, axis=1)
    omitted_gamma_residual = velocity_squared

    figure, axis = plt.subplots(figsize=(6.4, 4.2), constrained_layout=True)
    axis.semilogy(
        times,
        np.maximum(u_norm_residual, PLOT_FLOOR),
        label="|u.a u_a + 1| (native)",
        linewidth=1.8,
    )
    axis.semilogy(times, density_margin, label="density margin Omega", linewidth=1.8)
    axis.semilogy(times, tilt_margin, label="tilt margin 1 - |v| squared", linewidth=1.8)
    axis.semilogy(
        times,
        omitted_gamma_residual,
        "--",
        label="hostile Gamma omission residual = |v| squared",
        linewidth=1.3,
    )
    axis.set_xlabel("dimensionless integration time tau")
    axis.set_ylabel("dimensionless residual or domain margin")
    axis.set_title("RF-03 finite-boost normalization and domain")
    axis.grid(True, which="both", alpha=0.25)
    axis.legend(loc="best", fontsize="small")
    _save_figure(figure, OUTPUT_DIRECTORY / FIGURES[2])

    data = {
        "time": _array(times),
        "u_norm_abs_residual": _array(u_norm_residual),
        "density_margin": _array(density_margin),
        "tilt_margin": _array(tilt_margin),
        "max_u_norm_abs_residual": _json_float(np.max(u_norm_residual)),
        "min_density_margin": _json_float(np.min(density_margin)),
        "min_tilt_margin": _json_float(np.min(tilt_margin)),
        "status": result["status"],
        "units": "dimensionless normalized variables",
    }
    mutation = {
        "name": "normalization_gamma_omission",
        "operation": "use u=(1,v) instead of u=Gamma*(1,v)",
        "min_abs_detection_signal": _json_float(np.min(omitted_gamma_residual)),
        "max_abs_detection_signal": _json_float(np.max(omitted_gamma_residual)),
        "detected": bool(np.min(omitted_gamma_residual) > 1.0e-6),
    }
    return data, mutation


def _entropy_temperature_diagnostic() -> dict:
    from bianchi.thermo import dof, temperature

    ell = np.geomspace(0.3, 3.0, 81)
    ell0 = 1.0
    temperature0_gev = 0.2
    temperatures = np.asarray(
        temperature.temperature_of_ell(ell, temperature0_gev, ell0=ell0),
        dtype=np.float64,
    )
    entropy_comoving = dof.g_star_s(temperatures) * temperatures**3 * ell**3
    reference = float(dof.g_star_s(temperature0_gev) * temperature0_gev**3 * ell0**3)
    normalized_invariant = entropy_comoving / reference
    residual = np.abs(normalized_invariant - 1.0)

    figure, (temperature_axis, residual_axis) = plt.subplots(
        2,
        1,
        figsize=(6.4, 5.4),
        sharex=True,
        constrained_layout=True,
        gridspec_kw={"height_ratios": [1.4, 1.0]},
    )
    temperature_axis.loglog(ell, temperatures, linewidth=1.9)
    temperature_axis.axhline(0.2, color="0.5", linestyle=":", linewidth=1.0)
    temperature_axis.set_ylabel("T [GeV]")
    temperature_axis.set_title("RF-03 exogenous thermal history (mean scale only)")
    temperature_axis.grid(True, which="both", alpha=0.25)
    residual_axis.loglog(
        ell,
        np.maximum(residual, PLOT_FLOOR),
        linewidth=1.8,
        label="|g*s(T) T^3 ell^3 / S0 - 1|",
    )
    residual_axis.axhline(PLOT_FLOOR, color="0.45", linestyle=":", linewidth=1.0)
    residual_axis.set_xlabel("ell / ell0 (dimensionless)")
    residual_axis.set_ylabel("invariant residual")
    residual_axis.grid(True, which="both", alpha=0.25)
    residual_axis.legend(loc="best", fontsize="small")
    _save_figure(figure, OUTPUT_DIRECTORY / FIGURES[3])
    return {
        "ell_over_ell0": _array(ell),
        "temperature_gev": _array(temperatures),
        "g_star_s": _array(dof.g_star_s(temperatures)),
        "normalized_entropy_invariant": _array(normalized_invariant),
        "max_abs_invariant_residual": _json_float(np.max(residual)),
        "declared_regime": {
            "ell_over_ell0": [_json_float(ell.min()), _json_float(ell.max())],
            "temperature_gev": [
                _json_float(temperatures.min()),
                _json_float(temperatures.max()),
            ],
            "temperature0_gev": temperature0_gev,
        },
        "units": {"temperature": "GeV", "ell_over_ell0": "dimensionless"},
        "coupling_claim": "NONE; T_gamma is exogenous and is not supplied to the force/JVP diagnostic",
    }


def _domain_and_fallback_mutations() -> tuple[dict, dict]:
    native = _native()
    zero3 = np.zeros(3, dtype=np.float64)
    zero33 = np.zeros((3, 3), dtype=np.float64)
    try:
        native.rf03_matter_force(
            MODEL_ID,
            1.2,
            np.array([0.3, 1.0, 0.0, 0.0], dtype=np.float64),
            zero33,
            zero33,
            zero3,
            zero3,
            0.2,
            None,
        )
    except Exception as error:  # evidence records the typed native exception
        superluminal = {
            "name": "superluminal_tilt_input",
            "operation": "set |v| squared = 1 at the native boundary",
            "exception_type": type(error).__name__,
            "exception_message": str(error),
            "detected": type(error).__name__ == "RF03DomainError",
        }
    else:
        superluminal = {
            "name": "superluminal_tilt_input",
            "operation": "set |v| squared = 1 at the native boundary",
            "exception_type": None,
            "exception_message": "input was incorrectly accepted",
            "detected": False,
        }

    from bianchi.matter import gamma_law_rust

    coercions = []

    class MustNotCoerce:
        def __float__(self):
            coercions.append("float")
            raise AssertionError("numeric coercion preceded model selection")

        def __array__(self, *_args, **_kwargs):
            coercions.append("array")
            raise AssertionError("array coercion preceded model selection")

    poison = MustNotCoerce()
    try:
        gamma_law_rust.force(
            model_id="constant_w",
            gamma=poison,
            state=poison,
            Sigma=poison,
            N=poison,
            A=poison,
            R=poison,
            q=poison,
        )
    except Exception as error:  # evidence records selection-before-coercion
        fallback = {
            "name": "silent_constant_w_fallback_attempt",
            "operation": "request unsupported constant_w with poison numeric inputs",
            "exception_type": type(error).__name__,
            "exception_message": str(error),
            "numeric_coercions": coercions,
            "detected": (
                type(error).__name__ == "RF03ModelSelectionError" and not coercions
            ),
        }
    else:
        fallback = {
            "name": "silent_constant_w_fallback_attempt",
            "operation": "request unsupported constant_w with poison numeric inputs",
            "exception_type": None,
            "exception_message": "fallback attempt was incorrectly accepted",
            "numeric_coercions": coercions,
            "detected": False,
        }
    return superluminal, fallback


def main() -> None:
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    unexpected_png = sorted(
        path.name for path in OUTPUT_DIRECTORY.glob("*.png") if path.name not in FIGURES
    )
    if unexpected_png:
        raise RuntimeError(f"refusing to coexist with extra RF-03 figures: {unexpected_png}")
    for name in FIGURES:
        path = OUTPUT_DIRECTORY / name
        if path.exists():
            path.unlink()

    density_data, sign_mutation = _density_scale_diagnostic()
    tilt_data, normalization_mutation = _tilt_diagnostic()
    superluminal_mutation, fallback_mutation = _domain_and_fallback_mutations()
    data = {
        "schema": "bass-rf03-bounded-plot-data/v1",
        "source_commit": subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True
        ).strip(),
        "model_id": MODEL_ID,
        "figure_count": len(FIGURES),
        "figures": list(FIGURES),
        "diagnostics": {
            "native_oracle_force_jvp_residual": _force_jvp_diagnostic(),
            "log_density_vs_log_mean_scale": density_data,
            "tilt_normalization_and_domain_margin": tilt_data,
            "entropy_temperature_invariant": _entropy_temperature_diagnostic(),
        },
        "hostile_mutations": [
            sign_mutation,
            normalization_mutation,
            superluminal_mutation,
            fallback_mutation,
        ],
        "all_hostile_mutations_detected": all(
            item["detected"]
            for item in (
                sign_mutation,
                normalization_mutation,
                superluminal_mutation,
                fallback_mutation,
            )
        ),
        "claim_boundary": (
            "bounded RF-03 parity/domain/thermodynamic evidence only; no new EOS, "
            "tilted-temperature coupling, performance, or broader scientific claim"
        ),
    }
    (OUTPUT_DIRECTORY / "PLOT_DATA.json").write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    missing = [name for name in FIGURES if not (OUTPUT_DIRECTORY / name).is_file()]
    if missing:
        raise RuntimeError(f"missing required figures: {missing}")
    print(
        json.dumps(
            {
                "figure_count": len(FIGURES),
                "all_hostile_mutations_detected": data[
                    "all_hostile_mutations_detected"
                ],
                "max_force_residual": data["diagnostics"][
                    "native_oracle_force_jvp_residual"
                ]["max_force_residual"],
                "max_jvp_residual": data["diagnostics"][
                    "native_oracle_force_jvp_residual"
                ]["max_jvp_residual"],
                "density_slope_residual": density_data["slope_abs_residual"],
                "max_u_norm_residual": tilt_data["max_u_norm_abs_residual"],
                "max_entropy_residual": data["diagnostics"][
                    "entropy_temperature_invariant"
                ]["max_abs_invariant_residual"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
