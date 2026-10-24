"""REC-LOCAL-02 source-authority diagnostic.

This module deliberately records why the currently available source inputs do
not admit a physical split-domain reference.  It does not construct a face
closure, select a Doppler convention, or supply any part of a coupled JVP.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import numpy as np
from scipy.constants import c, electron_volt

from full_bianchi_hyrec.recoil.nonlinear_bose_release import HarmonicGrid
from full_bianchi_hyrec.recoil.nonlinear_bose_runtime import LineBoundaryConfig
from full_bianchi_hyrec.recoil.original_hyrec_physical_flux import (
    boundary_sample_reconstruction_residuals,
    parse_original_hyrec_boundary_snapshot_csv,
)
from full_bianchi_hyrec.recoil.original_hyrec_native import H_PLANCK_EV_S
from full_bianchi_hyrec.trajectory.full_coupled_adaptive import (
    audit_full_coupling_identifiability,
)


CLAIM = "NO_PASS_REC_PHYSICAL_SPLIT"
STATUS = "BLOCKED_REC_PHYSICAL_INTERFACE_DEFECT"
CLASSIFICATION = "EXPLORATORY_NONAUTHORITATIVE"
NATIVE_INTERIOR_INDICES = tuple(range(136, 144))
NATIVE_INTERFACE_EDGES = ((135, 136), (143, 144))
TRACKED_INPUTS = {
    "boundary_snapshot": (
        "archive/expanded/Full_Bianchi_HyRec_PR04C0C1A_split_domain_boundary_v0_55/pr04c_z1100.csv",
        "147ba6e6cfdae9c06530a0983161e769198b3bb5ad56c0c4d820b0a3f5d3e7b5",
    ),
    "original_hyrec": (
        "archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip",
        "48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27",
    ),
    "network": (
        "data/z1100_direct_network_node.npz",
        "e6a28194d183658a87f0974afe3f46323106382970a85338f9ce94c20c7b5736",
    ),
    "direction_grid": (
        "data/pr01c_background_snapshots_v048.npz",
        "df136bca7c120054cc45cf2b4fc2bd52acc3d60e6159b0f63c2622de03f2f03c",
    ),
    "scalar_history": (
        "data/pr05b2_source_history_v060.npz",
        "d4f82542e13fed4ff0bb60b17865d8b9de5e090a2366108169c3da7a21fcb4b1",
    ),
    "source_parent": (
        "data/pr05c2c1b2b1e0_source_derived_parent_v073.npz",
        "c74a2a0e69d6d34c338d19af2f123d1eb32130ac103a68e4494a2c9542eaa958",
    ),
    "single_com_root": (
        "data/pr05c2c1b2b1e1a_single_com_macro_v074.npz",
        "b05e227e7ff8ffd64639e4a432a5789fff08cc89b8bbd63adbcec5fc2da3903c",
    ),
    "two_photon_raman": (
        "data/pr05c2c1b2a_two_photon_raman_source_v068.npz",
        "536154894ce3779cc877a04b490a6e2b4501826d98efd9a12a4a6568dd0eabad",
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_tracked_inputs(root: Path) -> dict[str, dict[str, str | bool]]:
    """Return the fixed eight-input identity check without substituting data."""
    result: dict[str, dict[str, str | bool]] = {}
    for name, (relative, expected) in TRACKED_INPUTS.items():
        actual = sha256(root / relative)
        result[name] = {
            "path": relative,
            "expected_sha256": expected,
            "actual_sha256": actual,
            "match": actual == expected,
        }
    return result


def _network_energy_coordinates_eV(
    network: Any, *, source_energy_rescale: float
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    locked_energy = (
        np.asarray(network["momentum_scale"], dtype=float) * c / electron_volt
    )
    temperature_K = float(network["temperature_K"])
    line = LineBoundaryConfig.lyman_alpha(
        temperature_K=temperature_K, x_red=-21.25, x_blue=21.25
    )
    intervals = np.asarray(network["state_intervals"], dtype=float)
    face_frequency = line.nu_abs_Hz + intervals * line.Doppler_width_Hz
    lower = face_frequency[:, 0]
    upper = face_frequency[:, 1]
    physical_centroid_frequency = (
        0.75 * (upper**4 - lower**4) / (upper**3 - lower**3)
    )
    point_frequency = line.nu_abs_Hz + np.mean(intervals, axis=1) * line.Doppler_width_Hz
    interval_centroid_energy = (
        H_PLANCK_EV_S
        * physical_centroid_frequency
        / float(source_energy_rescale)
    )
    point_energy = (
        H_PLANCK_EV_S * point_frequency / float(source_energy_rescale)
    )
    return locked_energy, point_energy, interval_centroid_energy


def adjacent_energy_feasibility(
    target_energy_eV: np.ndarray, source_energy_eV: np.ndarray
) -> dict[str, Any]:
    """Certificate for a nonnegative 35x8 number/energy map.

    For ``B[target, source]``, each source column is feasible exactly when its
    energy lies in the convex hull of the target COM energies.  The sparse
    two-target witness below is exploratory evidence only: it is not selected
    as a physical deposition map or promoted to source authority.
    """
    targets = np.asarray(target_energy_eV, dtype=float)
    sources = np.asarray(source_energy_eV, dtype=float)
    if targets.shape != (35,) or sources.shape != (8,):
        raise ValueError(
            "REC-LOCAL-02 requires the actual 35-state and 8-native energies"
        )
    if not np.all(np.isfinite(targets)) or not np.all(np.isfinite(sources)):
        raise ValueError("target and source energies must be finite")
    if len(np.unique(targets)) != len(targets):
        raise ValueError("target COM energies must be distinct")
    if not np.all(np.diff(sources) > 0.0):
        raise ValueError("native source energies must be strictly increasing")
    order = np.argsort(targets, kind="stable")
    sorted_targets = targets[order]
    bad = np.flatnonzero(
        (sources < sorted_targets[0]) | (sources > sorted_targets[-1])
    )
    result: dict[str, Any] = {
        "classification": CLASSIFICATION,
        "map_shape": [35, 8],
        "orientation": "B[target_com_cell,source_native_index]",
        "source_native_indices": list(NATIVE_INTERIOR_INDICES),
        "source_energy_range_eV": [float(sources[0]), float(sources[-1])],
        "target_energy_range_eV": [
            float(sorted_targets[0]),
            float(sorted_targets[-1]),
        ],
        "infeasible_source_columns": [int(index) for index in bad],
        "source_strictly_inside_target_hull": bool(
            np.all(sources > sorted_targets[0])
            and np.all(sources < sorted_targets[-1])
        ),
        "physical_map_selected": False,
        "physical_map": None,
        "native_spikes_used_as_finite_cells": False,
    }
    if bad.size:
        result.update(
            {
                "number_and_energy_exact": False,
                "nonnegative": False,
                "feasible": False,
                "reason": "source energy lies outside the target COM energy hull",
                "exploratory_sparse_witness": [],
                "witness_sha256": None,
            }
        )
        return result
    matrix = np.zeros((35, 8), dtype=float)
    sparse_witness: list[dict[str, Any]] = []
    for column, energy in enumerate(sources):
        right_sorted = int(np.searchsorted(sorted_targets, energy, side="left"))
        if right_sorted == 0:
            target_indices = [int(order[0])]
            fractions = [1.0]
        elif right_sorted == len(sorted_targets):
            target_indices = [int(order[-1])]
            fractions = [1.0]
        elif energy == sorted_targets[right_sorted]:
            target_indices = [int(order[right_sorted])]
            fractions = [1.0]
        else:
            left_sorted = right_sorted - 1
            left_energy = sorted_targets[left_sorted]
            right_energy = sorted_targets[right_sorted]
            right_fraction = (energy - left_energy) / (
                right_energy - left_energy
            )
            target_indices = [
                int(order[left_sorted]),
                int(order[right_sorted]),
            ]
            fractions = [float(1.0 - right_fraction), float(right_fraction)]
        matrix[target_indices, column] = fractions
        sparse_witness.append(
            {
                "source_column": column,
                "source_native_index": NATIVE_INTERIOR_INDICES[column],
                "target_indices": target_indices,
                "number_fractions": fractions,
            }
        )
    number_residual = np.sum(matrix, axis=0) - 1.0
    energy_residual = targets @ matrix - sources
    nonzero = matrix[matrix > 0.0]
    result.update(
        {
            "number_and_energy_exact": True,
            "nonnegative": bool(np.all(matrix >= 0.0)),
            "feasible": True,
            "reason": "all source energies lie inside the target COM energy hull",
            "max_abs_number_residual": float(np.max(np.abs(number_residual))),
            "max_abs_energy_residual_eV": float(np.max(np.abs(energy_residual))),
            "max_relative_energy_residual": float(
                np.max(np.abs(energy_residual) / sources)
            ),
            "minimum_nonzero_fraction": float(np.min(nonzero)),
            "exploratory_sparse_witness": sparse_witness,
            "witness_sha256": hashlib.sha256(
                np.asarray(matrix, dtype="<f8").tobytes(order="C")
            ).hexdigest(),
        }
    )
    return result


def build_rec_local02_diagnostic(root: str | Path) -> dict[str, Any]:
    """Evaluate only the bounded source-authority no-go gates."""
    repository = Path(root).resolve()
    hashes = verify_tracked_inputs(repository)
    if not all(bool(item["match"]) for item in hashes.values()):
        raise ValueError("fixed REC-LOCAL-02 authority input hash mismatch")

    network_path = repository / TRACKED_INPUTS["network"][0]
    grid_path = repository / TRACKED_INPUTS["direction_grid"][0]
    parent_path = repository / TRACKED_INPUTS["source_parent"][0]
    history_path = repository / TRACKED_INPUTS["scalar_history"][0]
    boundary_path = repository / TRACKED_INPUTS["boundary_snapshot"][0]
    with (
        np.load(network_path, allow_pickle=False) as network,
        np.load(grid_path, allow_pickle=False) as grid_data,
        np.load(parent_path, allow_pickle=False) as parent,
        np.load(history_path, allow_pickle=False) as history,
    ):
        directions = np.asarray(grid_data["directions"], dtype=float)
        angular_weights = np.asarray(grid_data["angular_weights"], dtype=float)
        occupation = np.asarray(parent["occupation"], dtype=float)
        scalar_occupation = np.asarray(parent["scalar_occupation"], dtype=float)
        parent_source_indices = np.asarray(parent["source_indices"], dtype=int)
        mode_measure = np.asarray(network["mode_measure_m3"], dtype=float)
        network_intervals = np.asarray(network["state_intervals"], dtype=float)
        parent_intervals = np.asarray(parent["state_intervals"], dtype=float)
        history_outgoing = np.asarray(history["outgoing_virtual"], dtype=float)
        if (
            occupation.shape != (35, 26)
            or scalar_occupation.shape != (35,)
            or mode_measure.shape != (35,)
            or directions.shape != (26, 3)
            or angular_weights.shape != (26,)
            or history_outgoing.shape != (311, 7489)
        ):
            raise ValueError("actual source parent/COM grid does not have required 35x26 shape")
        if (
            np.any(occupation <= 0.0)
            or np.any(mode_measure <= 0.0)
            or np.any(angular_weights <= 0.0)
        ):
            raise ValueError("actual source occupation and COM measure must be positive")
        interval_residual = float(np.max(np.abs(parent_intervals - network_intervals)))
        isotropy_residual = float(
            np.max(np.abs(occupation - scalar_occupation[:, None]))
        )
        directional_measure = mode_measure[:, None] * angular_weights[None, :]
        harmonic_grid = HarmonicGrid.from_directions(directions, angular_weights, ell_max=3)
        identifiability = audit_full_coupling_identifiability(harmonic_grid)
        boundary = parse_original_hyrec_boundary_snapshot_csv(boundary_path)
        source_energy_rescale = float(
            boundary.trajectory.fsR**2 * boundary.trajectory.meR
        )
        parent_point_energy = np.asarray(
            parent["target_energies_eV_rescaled"], dtype=float
        )
        (
            target_energy,
            computed_point_energy,
            computed_interval_centroid_energy,
        ) = _network_energy_coordinates_eV(
            network, source_energy_rescale=source_energy_rescale
        )
        parent_point_formula_residual = float(
            np.max(np.abs(parent_point_energy - computed_point_energy))
        )
        point_to_locked_owner_difference = float(
            np.max(np.abs(parent_point_energy - target_energy))
        )
        interval_centroid_to_locked_owner_difference = float(
            np.max(np.abs(computed_interval_centroid_energy - target_energy))
        )
        history_energy = np.asarray(history["energy_eV"], dtype=float)
        source_energy = history_energy[list(NATIVE_INTERIOR_INDICES)]
        feasibility = adjacent_energy_feasibility(target_energy, source_energy)
        residuals = {
            sample.side: boundary_sample_reconstruction_residuals(
                sample,
                H_s_inv=boundary.trajectory.H_s_inv,
                nH_cm3=boundary.trajectory.nH_cm3,
                TR_eV_rescaled=boundary.trajectory.TR_eV_rescaled,
                fsR=boundary.trajectory.fsR,
                meR=boundary.trajectory.meR,
                energy_grid_eV=history_energy,
            )
            for sample in boundary.boundaries
        }
        csv_width_Hz = float(
            boundary.boundaries[0].doppler_width_eV
            * source_energy_rescale
            / H_PLANCK_EV_S
        )
        node_temperature_K = float(network["temperature_K"])
        modern_line = LineBoundaryConfig.lyman_alpha(
            temperature_K=node_temperature_K, x_red=-21.25, x_blue=21.25
        )
        modern_width_Hz = modern_line.Doppler_width_Hz
        default_line = LineBoundaryConfig.lyman_alpha(
            temperature_K=3000.0, x_red=-21.25, x_blue=21.25
        )
        intervals = np.asarray(network["state_intervals"], dtype=float)
        default_frequency = (
            default_line.nu_abs_Hz + intervals * default_line.Doppler_width_Hz
        )
        default_measure = (
            8.0
            * np.pi
            * (default_frequency[:, 1] ** 3 - default_frequency[:, 0] ** 3)
            / (3.0 * c**3)
        )
        default_measure_mismatch = float(
            np.max(np.abs(default_measure - mode_measure) / mode_measure)
        )
        direct_frequency = (
            modern_line.nu_abs_Hz + intervals * modern_line.Doppler_width_Hz
        )
        direct_measure = (
            8.0
            * np.pi
            * (direct_frequency[:, 1] ** 3 - direct_frequency[:, 0] ** 3)
            / (3.0 * c**3)
        )
        direct_measure_mismatch = float(
            np.max(np.abs(direct_measure - mode_measure) / mode_measure)
        )
        witness_direction = directions[:, 0] - float(np.sum(angular_weights * directions[:, 0]))
        amplitude = 0.5 / float(np.max(np.abs(witness_direction)))
        field_a = 1.0 + amplitude * witness_direction
        field_b = 1.0 - amplitude * witness_direction
        weighted_a = float(np.sum(angular_weights * field_a))
        weighted_b = float(np.sum(angular_weights * field_b))
        distinct = bool(np.max(np.abs(field_a - field_b)) > 0.0)
    return {
        "schema": "REC_LOCAL_02_SOURCE_BOUND_GATE_V1",
        "status": STATUS,
        "claim": CLAIM,
        "tracked_inputs": hashes,
        "source_representation": {
            "occupation_shape": [35, 26],
            "occupation_minimum": float(np.min(occupation)),
            "occupation_isotropic_max_abs_residual": isotropy_residual,
            "mode_measure_shape": [35],
            "mode_measure_units": "m^-3",
            "mode_measure_minimum_m3": float(np.min(mode_measure)),
            "angular_weight_sum": float(np.sum(angular_weights)),
            "directional_measure_shape": [35, 26],
            "directional_measure_minimum_m3": float(np.min(directional_measure)),
            "direction_shape": [26, 3],
            "weight_count": 26,
            "parent_network_interval_max_abs_residual": interval_residual,
            "scalar_history_outgoing_virtual_shape": [311, 7489],
            "scalar_history_angular_rank": 1,
            "native_interior_indices": list(NATIVE_INTERIOR_INDICES),
            "native_interface_edges": [list(edge) for edge in NATIVE_INTERFACE_EDGES],
            "native_spikes_define_cells": False,
            "net_source_jump_is_total_interface_crossing_flux": False,
            "source_parent_uses_index_144": bool(144 in parent_source_indices),
            "source_parent_source_index_144_target_rows": [
                int(index)
                for index in np.flatnonzero(parent_source_indices == 144)
            ],
        },
        "source_flux_parity_residuals": residuals,
        "adjacent_energy_moment_feasibility": feasibility,
        "target_energy_binding": {
            "source": "tracked CollisionNetwork.momentum_scale",
            "units": "eV",
            "source_energy_rescale": source_energy_rescale,
            "momentum_scale_units": "kg m s^-1",
            "physical_cell_energy_definition": "momentum_scale*c/electron_volt",
            "locked_target_energy_sha256": hashlib.sha256(
                np.asarray(target_energy, dtype="<f8").tobytes(order="C")
            ).hexdigest(),
            "legacy_interval_centroid_definition": (
                "H_PLANCK_EV_S*0.75*(nu_hi^4-nu_lo^4)/"
                "(nu_hi^3-nu_lo^3)/(fsR^2*meR)"
            ),
            "legacy_interval_centroid_is_authoritative": False,
            "legacy_interval_centroid_to_locked_owner_max_abs_difference_eV": (
                interval_centroid_to_locked_owner_difference
            ),
            "source_parent_point_energy_definition": (
                "point-characteristic evaluation at arithmetic x centre"
            ),
            "source_parent_point_formula_max_abs_residual_eV": (
                parent_point_formula_residual
            ),
            "source_parent_point_to_locked_owner_max_abs_difference_eV": (
                point_to_locked_owner_difference
            ),
        },
        "doppler_width_reconciliation": {
            "direct_node_temperature_K": node_temperature_K,
            "direct_node_line_x": [-21.25, 21.25],
            "csv_boundary_width_Hz": csv_width_Hz,
            "modern_line_boundary_width_Hz": modern_width_Hz,
            "difference_Hz": modern_width_Hz - csv_width_Hz,
            "relative_difference": (modern_width_Hz - csv_width_Hz)
            / csv_width_Hz,
            "relative_difference_denominator": "csv_boundary_width_Hz",
            "selected_definition": "NONE_BLOCKED_NO_SILENT_SELECTION",
            "csv_definition": "doppler_width_eV*fsR^2*meR/H_PLANCK_EV_S",
            "modern_definition": (
                "LineBoundaryConfig.lyman_alpha(temperature_K=direct-node "
                "temperature)"
            ),
            "direct_node_network_measure_max_relative_mismatch": direct_measure_mismatch,
            "default_3000K_network_measure_max_relative_mismatch": default_measure_mismatch,
            "default_3000K_from_network_permitted": False,
            "default_3000K_from_network_status": "INCOMPATIBLE_WITH_DIRECT_NODE_MEASURE",
        },
        "full_coupling_identifiability": {
            "native_history_angular_rank": identifiability.native_history_angular_rank,
            "required_angular_rank": identifiability.required_angular_rank,
            "com_face_trace_source_defined": identifiability.com_face_trace_source_defined,
            "bounded_no_go": identifiability.bounded_no_go,
        },
        "positive_nonidentifiability_witness": {
            "field_a_minimum": float(np.min(field_a)),
            "field_b_minimum": float(np.min(field_b)),
            "weighted_mean_a": weighted_a,
            "weighted_mean_b": weighted_b,
            "weighted_mean_residual": abs(weighted_a - weighted_b),
            "fields_distinct": distinct,
            "source_defined_face_reconstruction": False,
        },
        "conventions_if_unblocked": {
            "metric_signature": "(-,+,+,+)",
            "frame": "hydrogen orthonormal frame",
            "frequency": "ordinary frequency in Hz",
            "energy": "joule for physical ledgers",
            "time_variable": "eta=ln(a), d/dt=H*d/deta",
        },
        "blocking_conditions": [
            "SOURCE_DEFINED_26_DIRECTION_FACE_RECONSTRUCTION_ABSENT",
        ],
        "stop_after_gate": "SOURCE_DEFINED_26_DIRECTION_FACE_RECONSTRUCTION_ABSENT",
        "not_run": [
            "deposition_map_selection",
            "full_moving_map_jvp",
            "photon_and_atomic_four_force_assembly",
            "number_energy_four_force_balance",
            "thermal_and_spectral_response",
            "independent_directional_jvp",
            "restart_and_history_transactions",
            "physical_reference_tests",
        ],
    }
