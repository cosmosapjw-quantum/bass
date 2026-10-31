"""KM2L: true zero-Thomson-collision escaped Lyalpha tagged spectrum.

Reintegrates the exact source-locked KM2J Einstein/P8/Peebles model for
independent check of original KM2K packet histories. The new observable is
the first-collision loss of a ballistic spectral subset, *not* total
post-scattering radiation or new independent stress energy.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from research.dual_lane_km2j_20261031.coupled_chem_p8 import CoupledChemicalP8
from research.dual_lane_km2k_20261031.escaping_lya import (
    evaluate_grid, exact_parent_sources, HIST_EDGES, SPECTRUM_EPOCHS
)
from research.dual_lane_km2k_20261031.frequency_core import (
    partial_gauss_integration, summarize_packets, gaussian_bin_histogram
)
from research.dual_lane_km2g_20261030.neutral_baryons import (
    SIGMA_T_M2, C_M_S
)

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PARENT_HEAD = "e216d708890c8321d2f6a2e146e60e7e01cea1ce"
SOURCE_BLOBS = {
    "research/dual_lane_km2k_20261031/escaping_lya.py": "d2791cdadeda45cb45d473680cd0333dcea1194d",
    "research/dual_lane_km2k_20261031/frequency_core.py": "ea583b341d46edbb209147152fa7b8ebf72f7bed",
}
N_INTERVALS = 40


def git_blob(path):
    raw = Path(path).read_bytes()
    return hashlib.sha1(("blob %d\0" % len(raw)).encode() + raw).hexdigest()


def original_source_guards():
    result = exact_parent_sources()
    for rel, expected in SOURCE_BLOBS.items():
        found = git_blob(ROOT / rel)
        if found != expected:
            raise ValueError("FROZEN_KM2K_PHYSICAL_SOURCE_CHANGED " + rel)
        result[rel] = found
    return result


def static_green(h, rate, injection, u):
    """Exact positive homogeneous Thomson-vs-free radiation energy."""
    if not (h > 0 and rate >= 0 and injection >= 0 and u >= 0):
        raise ValueError("bad analytic Thomson green control")
    k = 4 * h + rate
    return injection * (-math.expm1(-k * u)) / k


def prepare_opacity(model, sol, samples, order):
    """Compute actual tilted-Thomson hazard along original KM2J ray geodesics."""
    nodes, glweights, partial = partial_gauss_integration(order)
    tedges = np.linspace(0., model.end, N_INTERVALS + 1)
    nt = N_INTERVALS * order
    rays = model.N
    tau_nodes = np.zeros((nt, rays))
    tau_edges = np.zeros((N_INTERVALS + 1, rays))
    hazard_nodes = np.zeros((nt, rays))
    hazard_edges = np.zeros((N_INTERVALS + 1, rays))
    max_nuhazard_error = 0.
    for k, u in enumerate(tedges):
        d = model.fields(float(u), sol.sol(float(u)), False)
        hazard_edges[k] = d["nu"] * d["op"].D
        max_nuhazard_error = max(
            max_nuhazard_error,
            abs(d["nu"] / (d["nH"] * d["x"] *
                            SIGMA_T_M2 * C_M_S * model.parent.Tstar_seconds) - 1.)
        )
        if abs(d["x"] - samples["x_epoch"][k]) > 3e-10:
            raise ArithmeticError("source-locked KM2K x_e trajectory not reproduced")
        if abs(d["rho_gamma"] - samples["full_photon_rho"][k]) > 2e-8:
            raise ArithmeticError("source-locked P8 photon energy not reproduced")
        if np.max(abs(d["n"] - samples["directions_epoch"][k])) > 3e-9:
            raise ArithmeticError("source-locked original photon rays not reproduced")
    for j in range(N_INTERVALS):
        width = tedges[j + 1] - tedges[j]
        node_rates = np.zeros((order, rays))
        for k, node in enumerate(nodes):
            t = tedges[j] + width * (node + 1.) / 2.
            d = model.fields(float(t), sol.sol(float(t)), False)
            v = d["nu"] * d["op"].D
            if not np.all(v > 0):
                raise ArithmeticError("Thomson collision rate must be positive")
            node_rates[k] = v
            hazard_nodes[j * order + k] = v
        tau_nodes[j * order:(j + 1) * order] = (
            tau_edges[j][None, :] + width / 2 * (partial @ node_rates)
        )
        tau_edges[j + 1] = (
            tau_edges[j] + width / 2 * (glweights @ node_rates)
        )
    if np.min(np.diff(tau_edges, axis=0)) <= 0:
        raise ArithmeticError("Thomson integrated optical depths must increase")
    if max_nuhazard_error > 3e-12:
        raise ArithmeticError("SI electron abundance vs original Thomson opacity mismatch")
    return dict(hazard_nodes=hazard_nodes, hazard_edges=hazard_edges,
                tau_nodes=tau_nodes, tau_edges=tau_edges,
                max_SI_opacity_relative_error=float(max_nuhazard_error))


def case_science(ntheta, output_dir, order=8, end=.25):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    # This call itself actually re-solves the source-locked original KM2J
    # Einstein-P8-Peebles IVP, including real KM2K Doppler line emission.
    km2k = evaluate_grid(ntheta, order=order, end=end,
                         output_dir=output_dir,
                         save_packets=True, make_hist=True)
    physical = output_dir / km2k["packet_npz"]
    if hashlib.sha256(physical.read_bytes()).hexdigest() != km2k["packet_npz_sha256"]:
        raise ArithmeticError("KM2K exact packet input identity mismatch")
    parent = CoupledChemicalP8(ntheta=ntheta, end=end, chem_energy=True)
    solution = parent.solve(rtol=1e-11, atol=1.5e-13)
    with np.load(physical, allow_pickle=False) as data:
        sample = {k: data[k].copy() for k in data.files}
    rates = prepare_opacity(parent, solution, sample, order)
    e0 = sample["source_packets"]
    means0 = sample["center_D"]
    widths = sample["doppler_sigma"]
    Rnode = sample["Rnode"]
    Redge = sample["Rend"]
    RnodeH = sample["Rnode_H"]
    RedgeH = sample["Rend_H"]
    directions = sample["directions_epoch"]
    weights = sample["weights_epoch"]
    p8rho = sample["full_photon_rho"]
    tau_nodes = rates["tau_nodes"]
    tau_edges = rates["tau_edges"]
    haz_edge = rates["hazard_edges"]
    scenarios = {}
    for mode in ("shear_thomson", "shear_free", "Honly_thomson"):
        epochs = []
        spectra = []
        for k in range(N_INTERVALS + 1):
            u = float(end * k / N_INTERVALS)
            if k == 0:
                epochs.append({
                    "u": 0., "rho": 0., "q": [0., 0., 0.],
                    "mean_log_nu": None, "std_log_nu": None,
                    "redwing_fraction": None, "quadrupole_frob": None,
                    "ratio_to_P8_rho": 0., "first_collision_energy_rate": 0.,
                    "first_collision_momentum_rate": [0., 0., 0.],
                    "max_packet_thomson_tau": 0., "mean_packet_survival": 1.
                })
                continue
            cut = k * order
            redshift = (Redge[k][None, :] - Rnode[:cut]) if mode != "Honly_thomson" else (
                RedgeH[k] - RnodeH[:cut, None])
            if np.min(redshift) < -2e-12:
                raise ArithmeticError("negative characteristic redshift interval")
            optical = tau_edges[k][None, :] - tau_nodes[:cut]
            if np.min(optical) < -3e-12:
                raise ArithmeticError("negative Thomson optical depth interval")
            optical = np.maximum(optical, 0.)
            survival = np.ones_like(optical) if mode == "shear_free" else np.exp(-optical)
            pkt = e0[:cut] * np.exp(-4 * redshift) * survival
            center = means0[:cut] - redshift
            stat = summarize_packets(center, widths[:cut], pkt, directions[k], weights[k])
            rays = stat.pop("ray_energy")
            if stat["rho"] <= 0 or stat["rho"] >= p8rho[k]:
                raise ArithmeticError("unphysical tagged unscattered radiation density")
            collision_rays = haz_edge[k] * rays if mode != "shear_free" else np.zeros_like(rays)
            event_energy = float(np.dot(weights[k], collision_rays))
            event_momentum = np.einsum("n,ni->i",weights[k] * collision_rays,directions[k])
            free_reference_rays = (e0[:cut] * np.exp(-4 * redshift)).sum(axis=0)
            free_reference = float(weights[k] @ free_reference_rays)
            frac = stat["rho"] / free_reference
            if not -1e-12 <= frac <= 1 + 1e-12:
                raise ArithmeticError("ballistic survival fraction outside physical bounds")
            stat.update({
                "u": u, "ratio_to_P8_rho": stat["rho"] / float(p8rho[k]),
                "first_collision_energy_rate": event_energy,
                "first_collision_momentum_rate": event_momentum.tolist(),
                "max_packet_thomson_tau": float(np.max(optical)),
                "mean_packet_survival": float(min(1., max(0., frac)))
            })
            epochs.append(stat)
            if k in SPECTRUM_EPOCHS:
                hist, gap = gaussian_bin_histogram(center, widths[:cut], pkt,
                                                  weights[k], HIST_EDGES)
                if gap >= 2e-11:
                    raise ArithmeticError("frequency histogram mis-normalized")
                spectra.append({"u": u, "rho": stat["rho"],
                                "histogram_loss_relative": gap,
                                "spectrum_energy_bins": hist.tolist()})
        scenarios[mode] = {"epochs": epochs, "spectra": spectra}
    comparison = []
    for k in range(N_INTERVALS + 1):
        surv = scenarios["shear_thomson"]["epochs"][k]
        free = scenarios["shear_free"]["epochs"][k]
        ctrl = scenarios["Honly_thomson"]["epochs"][k]
        comparison.append({
            "u": surv["u"],
            "unscattered_over_free_energy": None if k == 0 else surv["rho"] / free["rho"],
            "first_scattered_marked_fraction": None if k == 0 else 1 - surv["rho"] / free["rho"],
            "shear_vs_Honly_surviving_centroid": None if k == 0 else surv["mean_log_nu"] - ctrl["mean_log_nu"],
            "survival_minus_free_centroid": None if k == 0 else surv["mean_log_nu"] - free["mean_log_nu"]
        })
    ref = km2k["scenarios"]["shear"]["epochs"][-1]
    calculated = scenarios["shear_free"]["epochs"][-1]
    if abs(ref["rho"] / calculated["rho"] - 1) > 2e-12:
        raise ArithmeticError("zero-scattering KM2K energy limit failed")
    if abs(ref["mean_log_nu"] - calculated["mean_log_nu"]) > 2e-12:
        raise ArithmeticError("zero-scattering KM2K frequency limit failed")
    end_state = comparison[-1]
    if not 0 < end_state["unscattered_over_free_energy"] < 1:
        raise ArithmeticError("live positive Thomson physical effect absent")
    if scenarios["shear_thomson"]["epochs"][-1]["first_collision_energy_rate"] <= 0:
        raise ArithmeticError("nonzero physical first-scatter event rate absent")
    cons = parent.conservation(solution, order=24)
    if max(cons["max_Hamiltonian_norm"], cons["max_momentum_norm"]) > 5e-8:
        raise ArithmeticError("original Einstein/P8 constraint broken")
    # Store complete original ray hazard history for independent arithmetic audit.
    p = output_dir / f"KM2L_THOMSON_OPTICAL_GL{ntheta}_GLT{order}.npz"
    np.savez_compressed(p,**rates)
    return {
        "n_theta": ntheta,
        "original_ray_count": parent.N,
        "joint_original_KM2J_IVP_reintegrations": 2,
        "joint_original_parent_rhs_calls": [int(km2k["parent_joint_ivp_nfev"]), int(solution.nfev)],
        "KM2K_original_packets_file": km2k["packet_npz"],
        "KM2K_original_packets_sha256": km2k["packet_npz_sha256"],
        "thomson_opacity_file": p.name,
        "thomson_opacity_sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
        "max_SI_opacity_relative_error": rates["max_SI_opacity_relative_error"],
        "inherited_initial_J_SHA256": parent.initial_j_sha,
        "reintegrated_KM2J_conservation": cons,
        "source_sobolev_bounding": km2k["line_energy_fraction_range"],
        "scenarios": scenarios,
        "comparisons": comparison
    }


def run_science(output, orders=(12,16), order=8):
    source = original_source_guards()
    output = Path(output)
    output.parent.mkdir(parents=True,exist_ok=True)
    runs = {}
    for n in orders:
        run = case_science(n, output.parent, order=order)
        runs[f"GL{n}"] = run
        a = run["scenarios"]["shear_thomson"]["epochs"][-1]
        b = run["comparisons"][-1]
        print("KM2L_THOMSON_PHYSICS",n,
              "ballistic_rho",a["rho"],
              "surviving_fraction",b["unscattered_over_free_energy"],
              "first_scatter_energy_rate",a["first_collision_energy_rate"],
              "centroid_log_nu",a["mean_log_nu"],
              "tau_end_ray_max",run["scenarios"]["shear_thomson"]["epochs"][-1]["max_packet_thomson_tau"],
              flush=True)
    result = {
        "schema":"bass.km2l.real_geodesic_thomson_no_scatter_lya.v1",
        "immutable_parent_PR":293,"immutable_parent_HEAD":PARENT_HEAD,
        "original_source_blobs":source,
        "scope":"actual KM2J Einstein/P8/Peebles dynamic electron rest opacity times tilted normal-frame Thomson Doppler loss; ballistic tagged escaped Lyalpha only",
        "new_transport":"source-locked time and ray dependent zero-Thomson-scattering characteristic Green damping",
        "separate_Einstein_P8_Peebles_initial_value_problems":len(orders),
        "reintegrations_each":2,
        "new_physical_transport_scenarios_per_original_geometry":3,
        "new_spectral_epoch_count":len(orders)*3*(N_INTERVALS+1),
        "frequency_spectrum_snapshot_count":len(orders)*3*len(SPECTRUM_EPOCHS),
        "frequency_bin_count":len(HIST_EDGES)-1,
        "hist_logfreq_edges":HIST_EDGES.tolist(),
        "cases":runs,
        "upper_dag":"9/15","upper_edges":21,
        "KM2":"PARTIAL","new_completed_upper_nodes":0,
        "KM2L_scoped_status":"PENDING_FINAL_CI",
        "production_ready":False,"merge_ready":False,"auto_next":False,
        "native_subagent":"NOT_RUN","distinct_author_R6_C9":"NOT_RUN",
        "not_implemented":[
            "scattered photon angular gain and repeated Thomson scattering",
            "Thomson frequency Compton redistribution and thermal electron energy transfer",
            "resonant Lyalpha frequency diffusion recoil and 2p population",
            "photoexcitation backreaction on Peebles x_e",
            "new Einstein stress from tagged photons (prohibited double count)",
            "realistic CMB posterior cosmological calibration",
            "angular continuum enclosure"
        ]
    }
    output.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n")
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--output",required=True,type=Path)
    p.add_argument("--orders",default="12,16")
    p.add_argument("--time-order",default=8,type=int)
    a = p.parse_args()
    run_science(a.output,tuple(int(z) for z in a.orders.split(",")),a.time_order)
