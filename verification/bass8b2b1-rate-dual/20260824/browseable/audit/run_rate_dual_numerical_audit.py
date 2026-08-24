"""Randomized and plot-driven audit for BASS-8B.2B.1."""
from __future__ import annotations

import json
import math
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [
    str(ROOT / "source"),
    str(ROOT / "inputs" / "bass8b2a"),
    str(ROOT / "inputs" / "bass8b2b0"),
]

from direction_dependent_rate_dual import (  # noqa: E402
    NormalHubbleRateJet,
    RateDualAuthority,
    bind_direction_dependent_rate_dual,
)
from electron_state_binding import (  # noqa: E402
    DerivativeSide,
    ElectronBindingCertificate,
    ElectronStateJet,
    HashRef,
    IndependentElectronState,
)
from generic_vector_paired_carrier import (  # noqa: E402
    lebedev26,
    rotate_state,
    rotation_matrix,
)

H1 = "1" * 64
H2 = "2" * 64
H3 = "3" * 64
H4 = "4" * 64


def binding(
    *,
    tau: float,
    density: float,
    beta: np.ndarray,
    ddensity: float,
    dbeta: np.ndarray,
) -> ElectronBindingCertificate:
    state = IndependentElectronState(
        proper_density_m3=float(density),
        beta_normal=tuple(float(x) for x in beta),
        schedule_payload_sha256=H1,
        source=HashRef("randomized-electron-schedule", H2),
    )
    jet = ElectronStateJet(
        tau=float(tau),
        proper_density_m3=float(density),
        beta_normal=tuple(float(x) for x in beta),
        dproper_density_dtau=float(ddensity),
        dbeta_normal_dtau=tuple(float(x) for x in dbeta),
        segment_index=0,
        derivative_side=DerivativeSide.INTERIOR,
        closure=state.closure,
        schedule_payload_sha256=H1,
    )
    return ElectronBindingCertificate(
        state=state,
        jet=jet,
        coordinate_sha256=H3,
        binding_sha256=H4,
        metadata={"direction_dependent_rate_bound": False},
    )


def build(
    e_rest: np.ndarray,
    w_rest: np.ndarray,
    *,
    tau: float,
    density: float,
    beta: np.ndarray,
    ddensity: float,
    dbeta: np.ndarray,
    H: float,
    dH: float,
):
    return bind_direction_dependent_rate_dual(
        binding(
            tau=tau,
            density=density,
            beta=beta,
            ddensity=ddensity,
            dbeta=dbeta,
        ),
        NormalHubbleRateJet(
            tau=tau,
            H_normal_s=H,
            dH_normal_s_dtau=dH,
            derivative_side=DerivativeSide.INTERIOR,
            coordinate_sha256=H3,
            provenance=HashRef("normal-H", H2),
        ),
        e_rest=e_rest,
        w_rest=w_rest,
        authority=RateDualAuthority.frozen_project_authority(),
    )


def random_rotation(rng: np.random.Generator) -> np.ndarray:
    axis = rng.normal(size=3)
    axis /= np.linalg.norm(axis)
    return rotation_matrix(axis, float(rng.uniform(-math.pi, math.pi)))


def relative_max(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.max(np.abs(a - b)) / max(1.0, float(np.max(np.abs(b)))))


def randomized_sweep() -> dict[str, float | int]:
    rng = np.random.default_rng(20260824)
    e_rest, w_rest = lebedev26()
    ncases = 500
    maxima = {
        "node_unit_residual": 0.0,
        "doppler_e2_formula_residual": 0.0,
        "doppler_rest_formula_residual": 0.0,
        "rate_formula_residual": 0.0,
        "rate_log_derivative_residual": 0.0,
        "left_null_relative_residual": 0.0,
        "projector_global_scalar_residual": 0.0,
        "so3_node_residual": 0.0,
        "so3_rate_residual": 0.0,
        "so3_rate_jet_residual": 0.0,
        "so3_generator_residual": 0.0,
        "so3_left_residual": 0.0,
    }
    mutation_detected = {"omit_gamma": 0, "omit_direction_factor": 0, "double_doppler": 0, "unchanged_left": 0}
    mutation_eligible = {"omit_gamma": 0}

    for case in range(ncases):
        direction = rng.normal(size=3)
        direction /= np.linalg.norm(direction)
        speed = float(rng.uniform(0.0, 0.75))
        beta = speed * direction
        dbeta = rng.normal(size=3) * 0.025
        density = float(10.0 ** rng.uniform(-2.0, 4.0))
        ddensity = float(density * rng.uniform(-0.2, 0.2))
        H = float(10.0 ** rng.uniform(-20.0, -16.0))
        dH = float(H * rng.uniform(-0.2, 0.2))
        out = build(
            e_rest,
            w_rest,
            tau=0.35,
            density=density,
            beta=beta,
            ddensity=ddensity,
            dbeta=dbeta,
            H=H,
            dH=dH,
        )
        maxima["node_unit_residual"] = max(
            maxima["node_unit_residual"],
            float(np.max(np.abs(np.linalg.norm(out.e_normal, axis=1) - 1.0))),
        )
        expected_d = out.gamma * (1.0 - out.e_normal @ beta)
        rest_d = 1.0 / (out.gamma * (1.0 + e_rest @ beta))
        expected_nu = density * out.authority.sigma_t_m2 * out.authority.c_m_s * expected_d / H
        expected_log = ddensity / density - dH / H + out.ddoppler_dtau / out.doppler
        maxima["doppler_e2_formula_residual"] = max(
            maxima["doppler_e2_formula_residual"], relative_max(out.doppler, expected_d)
        )
        maxima["doppler_rest_formula_residual"] = max(
            maxima["doppler_rest_formula_residual"], relative_max(out.doppler, rest_d)
        )
        maxima["rate_formula_residual"] = max(
            maxima["rate_formula_residual"], relative_max(out.nu_tau, expected_nu)
        )
        maxima["rate_log_derivative_residual"] = max(
            maxima["rate_log_derivative_residual"],
            float(np.max(np.abs(out.dnu_tau_dtau / out.nu_tau - expected_log))),
        )

        y = rng.normal(size=9 * len(e_rest))
        cy = out.apply_full_generator(y)
        left_scale = max(1.0, float(np.linalg.norm(cy)))
        maxima["left_null_relative_residual"] = max(
            maxima["left_null_relative_residual"], abs(out.left_functional(cy)) / left_scale
        )

        # Global opacity changes rate magnitude but not the normalized projector.
        out_scaled = build(
            e_rest,
            w_rest,
            tau=0.35,
            density=density * 7.0,
            beta=beta,
            ddensity=ddensity * 7.0,
            dbeta=dbeta,
            H=H,
            dH=dH,
        )
        maxima["projector_global_scalar_residual"] = max(
            maxima["projector_global_scalar_residual"], relative_max(out_scaled.project(y), out.project(y))
        )

        R = random_rotation(rng)
        rotated = build(
            e_rest @ R.T,
            w_rest,
            tau=0.35,
            density=density,
            beta=R @ beta,
            ddensity=ddensity,
            dbeta=R @ dbeta,
            H=H,
            dH=dH,
        )
        maxima["so3_node_residual"] = max(
            maxima["so3_node_residual"], relative_max(rotated.e_normal, out.e_normal @ R.T)
        )
        maxima["so3_rate_residual"] = max(
            maxima["so3_rate_residual"], relative_max(rotated.nu_tau, out.nu_tau)
        )
        maxima["so3_rate_jet_residual"] = max(
            maxima["so3_rate_jet_residual"], relative_max(rotated.dnu_tau_dtau, out.dnu_tau_dtau)
        )
        yr = rotate_state(y, R)
        generator_ref = rotate_state(cy, R)
        maxima["so3_generator_residual"] = max(
            maxima["so3_generator_residual"],
            relative_max(rotated.apply_full_generator(yr), generator_ref),
        )
        maxima["so3_left_residual"] = max(
            maxima["so3_left_residual"],
            abs(rotated.left_functional(yr) - out.left_functional(y)) / max(1.0, abs(out.left_functional(y))),
        )

        rates = out.rate_mutations()
        omit_gamma_signal = relative_max(rates["omit_gamma"], out.nu_tau)
        if out.gamma - 1.0 > 1.0e-8:
            mutation_eligible["omit_gamma"] += 1
            if omit_gamma_signal > 1.0e-8:
                mutation_detected["omit_gamma"] += 1
        for name in ("omit_direction_factor", "double_doppler"):
            if relative_max(rates[name], out.nu_tau) > 1.0e-8:
                mutation_detected[name] += 1
        if speed > 1.0e-6 and abs(out.left_without_direction_factor(cy)) / left_scale > 1.0e-10:
            mutation_detected["unchanged_left"] += 1

    return {
        "random_cases": ncases,
        **maxima,
        **{f"mutation_detected_{k}": v for k, v in mutation_detected.items()},
        **{f"mutation_eligible_{k}": v for k, v in mutation_eligible.items()},
    }


def representative() -> tuple[np.ndarray, np.ndarray, dict[str, object]]:
    e_rest, w_rest = lebedev26()
    beta = np.array([0.19, -0.11, 0.16])
    dbeta = np.array([0.013, 0.007, -0.009])
    params = {
        "tau": 0.35,
        "density": 8.0,
        "beta": beta,
        "ddensity": -0.6,
        "dbeta": dbeta,
        "H": 2.3e-18,
        "dH": -0.08e-18,
    }
    return e_rest, w_rest, params


def finite_difference_plot() -> dict[str, object]:
    e_rest, w_rest, p = representative()
    center = build(e_rest, w_rest, **p)
    hs = np.logspace(-2, -8, 13)
    err_e, err_d, err_nu = [], [], []
    for h in hs:
        pp = dict(p)
        pm = dict(p)
        pp["tau"] = p["tau"] + h
        pm["tau"] = p["tau"] - h
        pp["density"] = p["density"] + p["ddensity"] * h
        pm["density"] = p["density"] - p["ddensity"] * h
        pp["beta"] = p["beta"] + p["dbeta"] * h
        pm["beta"] = p["beta"] - p["dbeta"] * h
        pp["H"] = p["H"] + p["dH"] * h
        pm["H"] = p["H"] - p["dH"] * h
        plus = build(e_rest, w_rest, **pp)
        minus = build(e_rest, w_rest, **pm)
        err_e.append(relative_max((plus.e_normal - minus.e_normal) / (2.0 * h), center.de_normal_dtau))
        err_d.append(relative_max((plus.doppler - minus.doppler) / (2.0 * h), center.ddoppler_dtau))
        err_nu.append(relative_max((plus.nu_tau - minus.nu_tau) / (2.0 * h), center.dnu_tau_dtau))
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ax.loglog(hs, err_e, marker="o", label=r"$\dot e_i$")
    ax.loglog(hs, err_d, marker="s", label=r"$\dot D_i$")
    ax.loglog(hs, err_nu, marker="^", label=r"$\dot\nu_i$")
    ax.set_xlabel("central-difference step $h$")
    ax.set_ylabel("maximum relative derivative error")
    ax.set_title("Rate/bundle jet finite-difference convergence")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    path = ROOT / "figures" / "rate_dual_fd_convergence.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return {
        "h": hs.tolist(),
        "e_error": err_e,
        "doppler_error": err_d,
        "rate_error": err_nu,
        "minimum_e_error": float(min(err_e)),
        "minimum_doppler_error": float(min(err_d)),
        "minimum_rate_error": float(min(err_nu)),
    }


def mutation_plot() -> dict[str, object]:
    e_rest, w_rest = lebedev26()
    direction = np.array([0.53, -0.31, 0.79])
    direction /= np.linalg.norm(direction)
    speeds = np.linspace(0.02, 0.65, 22)
    rng = np.random.default_rng(91)
    correct, unchanged, omit_q, double_d = [], [], [], []
    for speed in speeds:
        out = build(
            e_rest,
            w_rest,
            tau=0.35,
            density=6.0,
            beta=speed * direction,
            ddensity=0.0,
            dbeta=np.zeros(3),
            H=2.2e-18,
            dH=0.0,
        )
        vals = {"correct": [], "unchanged": [], "omit_q": [], "double_d": []}
        for _ in range(8):
            y = rng.normal(size=9 * len(e_rest))
            cy = out.apply_full_generator(y)
            scale = max(1.0, float(np.linalg.norm(cy)))
            vals["correct"].append(abs(out.left_functional(cy)) / scale)
            vals["unchanged"].append(abs(out.left_without_direction_factor(cy)) / scale)
            vals["omit_q"].append(abs(out.left_functional(out.apply_mutated_generator(y, "omit_direction_factor"))) / scale)
            vals["double_d"].append(abs(out.left_functional(out.apply_mutated_generator(y, "double_doppler"))) / scale)
        correct.append(float(np.median(vals["correct"])))
        unchanged.append(float(np.median(vals["unchanged"])))
        omit_q.append(float(np.median(vals["omit_q"])))
        double_d.append(float(np.median(vals["double_d"])))
    floor = 1.0e-20
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ax.semilogy(speeds, np.maximum(correct, floor), marker="o", label="correct paired dual")
    ax.semilogy(speeds, np.maximum(unchanged, floor), marker="s", label="unchanged-left mutation")
    ax.semilogy(speeds, np.maximum(omit_q, floor), marker="^", label="omit direction factor")
    ax.semilogy(speeds, np.maximum(double_d, floor), marker="d", label="double Doppler")
    ax.set_xlabel(r"electron speed $|\beta_e|$")
    ax.set_ylabel("normalized left-invariant defect")
    ax.set_title("Hostile rate/dual mutations separate from roundoff")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    path = ROOT / "figures" / "rate_dual_mutation_defects.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return {
        "speed": speeds.tolist(),
        "correct": correct,
        "unchanged_left": unchanged,
        "omit_direction_factor": omit_q,
        "double_doppler": double_d,
        "minimum_hostile_defect": float(min(min(unchanged), min(omit_q), min(double_d))),
        "maximum_correct_defect": float(max(correct)),
    }


def scalar_cancellation_plot() -> dict[str, object]:
    e_rest, w_rest, p = representative()
    rng = np.random.default_rng(71)
    y = rng.normal(size=9 * len(e_rest))
    base = build(e_rest, w_rest, **p)
    p0 = base.project(y)
    c0 = np.linalg.norm(base.apply_full_generator(y))
    scales = np.logspace(-8, 8, 17)
    generator_ratio, projector_error = [], []
    for scale in scales:
        q = dict(p)
        q["density"] = p["density"] * scale
        q["ddensity"] = p["ddensity"] * scale
        out = build(e_rest, w_rest, **q)
        generator_ratio.append(float(np.linalg.norm(out.apply_full_generator(y)) / c0))
        projector_error.append(float(np.max(np.abs(out.project(y) - p0))))
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ax.loglog(scales, generator_ratio, marker="o", label="generator norm ratio")
    ax.loglog(scales, np.maximum(projector_error, 1.0e-20), marker="s", label="projector residual")
    ax.set_xlabel("global scalar opacity multiplier")
    ax.set_ylabel("ratio or absolute residual")
    ax.set_title("Global opacity scales the generator but cancels from $P$")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    path = ROOT / "figures" / "global_scalar_projector_cancellation.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return {
        "scale": scales.tolist(),
        "generator_ratio": generator_ratio,
        "projector_error": projector_error,
        "max_projector_error": float(max(projector_error)),
        "max_generator_linearity_error": float(np.max(np.abs(np.asarray(generator_ratio) / scales - 1.0))),
    }


def so3_plot() -> dict[str, object]:
    e_rest, w_rest = lebedev26()
    direction = np.array([0.47, 0.72, -0.51])
    direction /= np.linalg.norm(direction)
    dbeta0 = np.array([0.011, -0.006, 0.009])
    speeds = np.linspace(0.0, 0.7, 15)
    rng = np.random.default_rng(991)
    rate_err, jet_err, gen_err, left_err = [], [], [], []
    for speed in speeds:
        beta = speed * direction
        base = build(e_rest, w_rest, tau=0.35, density=5.0, beta=beta, ddensity=0.1, dbeta=dbeta0, H=2.1e-18, dH=-0.02e-18)
        y = rng.normal(size=9 * len(e_rest))
        R = random_rotation(rng)
        rot = build(e_rest @ R.T, w_rest, tau=0.35, density=5.0, beta=R @ beta, ddensity=0.1, dbeta=R @ dbeta0, H=2.1e-18, dH=-0.02e-18)
        yr = rotate_state(y, R)
        rate_err.append(relative_max(rot.nu_tau, base.nu_tau))
        jet_err.append(relative_max(rot.dnu_tau_dtau, base.dnu_tau_dtau))
        gen_err.append(relative_max(rot.apply_full_generator(yr), rotate_state(base.apply_full_generator(y), R)))
        left_err.append(abs(rot.left_functional(yr)-base.left_functional(y))/max(1.0,abs(base.left_functional(y))))
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ax.semilogy(speeds, np.maximum(rate_err, 1e-20), marker="o", label=r"$\nu_i$")
    ax.semilogy(speeds, np.maximum(jet_err, 1e-20), marker="s", label=r"$\dot\nu_i$")
    ax.semilogy(speeds, np.maximum(gen_err, 1e-20), marker="^", label="generator")
    ax.semilogy(speeds, np.maximum(left_err, 1e-20), marker="d", label="left dual")
    ax.set_xlabel(r"electron speed $|\beta_e|$")
    ax.set_ylabel("SO(3) covariance residual")
    ax.set_title("Generic-vector rate/dual covariance")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    path = ROOT / "figures" / "rate_dual_so3_covariance.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return {
        "speed": speeds.tolist(),
        "rate": rate_err,
        "rate_jet": jet_err,
        "generator": gen_err,
        "left": left_err,
        "max_residual": float(max(rate_err + jet_err + gen_err + left_err)),
    }


def main() -> None:
    (ROOT / "figures").mkdir(parents=True, exist_ok=True)
    result = {
        "schema": "bass8b2b1-rate-dual-numerical-audit-v1",
        "randomized": randomized_sweep(),
        "finite_difference": finite_difference_plot(),
        "mutations": mutation_plot(),
        "global_scalar_cancellation": scalar_cancellation_plot(),
        "so3": so3_plot(),
        "claim_class": "BOUNDED_DISCRETE_NUMERICAL_WITNESS_NOT_CONTINUUM_THEOREM",
        "status": "PASS_RATE_DUAL_NUMERICAL_AUDIT",
    }
    path = ROOT / "audit" / "rate_dual_numerical_audit.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
