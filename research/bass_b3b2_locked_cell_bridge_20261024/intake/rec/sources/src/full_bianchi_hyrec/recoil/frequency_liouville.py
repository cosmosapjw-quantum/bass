"""Conservative direction-resolved frequency Liouville/interface operator.

The 35-state COM--KHW representation remains local to the collision subsystem.
This module performs an upwind finite-volume transport in the locked Doppler
coordinate and exchanges only outer-face photon flux with the scalar native
boundary.  No native-to-COM state remap or fitted normalization is introduced.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

import numpy as np
from scipy.constants import c, h

from full_bianchi_hyrec.background.characteristics import (
    doppler_coordinate_speed,
    hydrogen_frame_characteristic,
    normal_frame_characteristic,
)

from .nonlinear_bose_release import HarmonicGrid
from .nonlinear_bose_runtime import CollisionNetwork, LineBoundaryConfig


def _readonly(value: np.ndarray) -> np.ndarray:
    result = np.array(value, copy=True)
    result.setflags(write=False)
    return result


def _boundary_field(value: float | Sequence[float], n_angle: int, name: str) -> np.ndarray:
    array = np.asarray(value, dtype=float)
    if array.ndim == 0:
        array = np.full(n_angle, float(array))
    if array.shape != (n_angle,) or not np.all(np.isfinite(array)) or np.any(array < 0.0):
        raise ValueError(f"{name} must be nonnegative finite scalar or (n_angle,) array")
    return array


@dataclass(frozen=True)
class FrequencyLiouvilleResult:
    occupation_action: np.ndarray
    number_action: np.ndarray
    face_flux_m3_s: np.ndarray
    native_number_action_m3_s: np.ndarray
    global_number_residual_m3_s: float
    com_energy_action_W_m3: float
    exact_interface_energy_action_W_m3: float
    outer_centroid_correction_W_m3: float
    cosmological_redshift_work_W_m3: float
    energy_identity_residual_W_m3: float
    energy_identity_relative_residual: float
    interface_atom_source_W_m3: float
    interface_four_momentum_com: np.ndarray
    interface_four_momentum_native: np.ndarray
    interface_four_momentum_residual: np.ndarray


@dataclass(frozen=True)
class FrequencyLiouvilleJVPResult:
    occupation_action_jvp: np.ndarray
    number_action_jvp: np.ndarray
    face_flux_jvp_m3_s: np.ndarray
    global_number_residual_jvp_m3_s: float


@dataclass(frozen=True)
class AngularScalarizationNoGoWitness:
    field_a: np.ndarray
    field_b: np.ndarray
    scalarized_value_a: float
    scalarized_value_b: float
    monopole_residual: float
    momentum_a: np.ndarray
    momentum_b: np.ndarray
    no_unique_scalar_momentum_preserving_map: bool


@dataclass(frozen=True)
class ConservativeFrequencyLiouville:
    network: CollisionNetwork
    reference_line: LineBoundaryConfig
    sorted_indices: np.ndarray
    inverse_indices: np.ndarray
    x_faces: np.ndarray
    face_frequency_Hz: np.ndarray
    face_mode_density_m3: np.ndarray
    cell_centroid_frequency_Hz: np.ndarray
    network_mode_measure_residual: float

    @classmethod
    def from_network(
        cls,
        network: CollisionNetwork,
        reference_line: LineBoundaryConfig | None = None,
    ) -> "ConservativeFrequencyLiouville":
        if not isinstance(network, CollisionNetwork):
            raise TypeError("network must be a CollisionNetwork")
        intervals = np.asarray(network.state_intervals, dtype=float)
        order = np.argsort(intervals[:, 0], kind="stable")
        sorted_intervals = intervals[order]
        if np.max(np.abs(sorted_intervals[:-1, 1] - sorted_intervals[1:, 0])) > 2.0e-12:
            raise ValueError("network intervals must form a contiguous frequency domain")
        faces = np.concatenate(([sorted_intervals[0, 0]], sorted_intervals[:, 1]))
        if np.any(np.diff(faces) <= 0.0):
            raise ValueError("frequency faces must be strictly increasing")
        line = reference_line
        if line is None:
            line = LineBoundaryConfig.lyman_alpha(
                temperature_K=3000.0,
                x_red=float(faces[0]),
                x_blue=float(faces[-1]),
            )
        if not math.isclose(line.x_red, float(faces[0]), rel_tol=0.0, abs_tol=2.0e-12) or not math.isclose(
            line.x_blue, float(faces[-1]), rel_tol=0.0, abs_tol=2.0e-12
        ):
            raise ValueError("reference line outer faces do not match the network")
        frequency = line.nu_abs_Hz + faces * line.Doppler_width_Hz
        if np.any(frequency <= 0.0):
            raise ValueError("all face frequencies must be positive")
        density = 8.0 * math.pi * frequency**2 * line.Doppler_width_Hz / c**3
        lo = frequency[:-1]
        hi = frequency[1:]
        computed_mode = 8.0 * math.pi * (hi**3 - lo**3) / (3.0 * c**3)
        locked_mode = np.asarray(network.mode_measure, dtype=float)[order]
        residual = float(np.max(np.abs(computed_mode - locked_mode) / locked_mode))
        if residual > 2.0e-8:
            raise ValueError(
                "reference_line is inconsistent with the locked network mode measure; "
                "a changed Doppler grid requires a recompiled collision network or explicit remap"
            )
        centroid = 0.75 * (hi**4 - lo**4) / (hi**3 - lo**3)
        inverse = np.empty_like(order)
        inverse[order] = np.arange(order.size)
        return cls(
            network=network,
            reference_line=line,
            sorted_indices=_readonly(order),
            inverse_indices=_readonly(inverse),
            x_faces=_readonly(faces),
            face_frequency_Hz=_readonly(frequency),
            face_mode_density_m3=_readonly(density),
            cell_centroid_frequency_Hz=_readonly(centroid),
            network_mode_measure_residual=residual,
        )

    @property
    def n_face(self) -> int:
        return self.network.n_state + 1

    def face_speeds_from_snapshot(
        self,
        snapshot,
        *,
        grid: HarmonicGrid,
        line: LineBoundaryConfig | None = None,
    ) -> np.ndarray:
        coordinate = self.reference_line if line is None else line
        compatible = (
            math.isclose(
                coordinate.nu_abs_Hz,
                self.reference_line.nu_abs_Hz,
                rel_tol=3.0e-14,
                abs_tol=0.0,
            )
            and math.isclose(
                coordinate.Doppler_width_Hz,
                self.reference_line.Doppler_width_Hz,
                rel_tol=3.0e-14,
                abs_tol=0.0,
            )
            and math.isclose(
                coordinate.x_red, self.reference_line.x_red, rel_tol=0.0, abs_tol=2.0e-12
            )
            and math.isclose(
                coordinate.x_blue, self.reference_line.x_blue, rel_tol=0.0, abs_tol=2.0e-12
            )
        )
        if not compatible:
            raise ValueError(
                "line coordinates must match the fixed COM frequency grid; "
                "a moving local Doppler grid requires an explicit remap or recompiled network"
            )
        R = np.empty(grid.n_angle, dtype=float)
        for index, direction in enumerate(grid.directions):
            normal = normal_frame_characteristic(snapshot, direction)
            hydrogen = hydrogen_frame_characteristic(snapshot, normal)
            R[index] = hydrogen.R_hydrogen_s_inv
        return np.asarray(
            doppler_coordinate_speed(
                R[None, :],
                self.x_faces[:, None],
                nu_abs_Hz=coordinate.nu_abs_Hz,
                Doppler_width_Hz=coordinate.Doppler_width_Hz,
            ),
            dtype=float,
        )

    def _validated(
        self,
        occupation: np.ndarray,
        speeds: np.ndarray,
        grid: HarmonicGrid,
    ) -> tuple[np.ndarray, np.ndarray]:
        f = np.asarray(occupation, dtype=float)
        a = np.asarray(speeds, dtype=float)
        if f.shape != (self.network.n_state, grid.n_angle):
            raise ValueError("occupation shape mismatch")
        if a.shape != (self.n_face, grid.n_angle):
            raise ValueError("face speed shape mismatch")
        if np.any(f < 0.0) or not np.all(np.isfinite(f)) or not np.all(np.isfinite(a)):
            raise ValueError("occupation and speeds must be finite; occupation nonnegative")
        return f, a

    def _face_flux(
        self,
        sorted_occupation: np.ndarray,
        speeds: np.ndarray,
        native_red: np.ndarray,
        native_blue: np.ndarray,
    ) -> np.ndarray:
        n_state, n_angle = sorted_occupation.shape
        left = np.empty((n_state + 1, n_angle), dtype=float)
        right = np.empty_like(left)
        left[0] = native_red
        right[0] = sorted_occupation[0]
        left[1:n_state] = sorted_occupation[:-1]
        right[1:n_state] = sorted_occupation[1:]
        left[n_state] = sorted_occupation[-1]
        right[n_state] = native_blue
        upwind = np.where(speeds >= 0.0, left, right)
        return speeds * self.face_mode_density_m3[:, None] * upwind

    def evaluate(
        self,
        occupation: np.ndarray,
        *,
        face_speeds_x_s_inv: np.ndarray,
        native_red_occupation: float | Sequence[float],
        native_blue_occupation: float | Sequence[float],
        grid: HarmonicGrid,
        directions_hydrogen: np.ndarray | None = None,
    ) -> FrequencyLiouvilleResult:
        f, speeds = self._validated(occupation, face_speeds_x_s_inv, grid)
        red = _boundary_field(native_red_occupation, grid.n_angle, "native_red_occupation")
        blue = _boundary_field(native_blue_occupation, grid.n_angle, "native_blue_occupation")
        sorted_f = f[self.sorted_indices]
        flux = self._face_flux(sorted_f, speeds, red, blue)
        number_sorted = flux[:-1] - flux[1:]
        number = np.empty_like(number_sorted)
        number[self.sorted_indices] = number_sorted
        occupation_action = number / self.network.mode_measure[:, None]
        native_number = -flux[0] + flux[-1]
        # The telescoping identity is evaluated in extended precision.  The
        # physical fluxes may be O(1e16) m^-3 s^-1 while the exact residual is
        # zero, so a float64 diagnostic can otherwise report an O(1) artefact.
        flux_long = np.asarray(flux, dtype=np.longdouble)
        number_long = flux_long[:-1] - flux_long[1:]
        native_long = -flux_long[0] + flux_long[-1]
        weights_long = np.asarray(grid.weights, dtype=np.longdouble)
        angle_residual = np.sum(number_long, axis=0) + native_long
        number_residual = float(np.sum(weights_long * angle_residual))

        energies_long = np.longdouble(h) * np.asarray(
            self.cell_centroid_frequency_Hz, dtype=np.longdouble
        )
        face_energies_long = np.longdouble(h) * np.asarray(
            self.face_frequency_Hz, dtype=np.longdouble
        )
        com_energy_long = np.sum(
            weights_long * np.sum(energies_long[:, None] * number_long, axis=0)
        )
        exact_interface_long = np.sum(
            weights_long
            * (
                face_energies_long[0] * flux_long[0]
                - face_energies_long[-1] * flux_long[-1]
            )
        )
        outer_correction_long = np.sum(
            weights_long
            * (
                (energies_long[0] - face_energies_long[0]) * flux_long[0]
                - (energies_long[-1] - face_energies_long[-1]) * flux_long[-1]
            )
        )
        internal_work_long = np.sum(
            weights_long
            * np.sum(
                (energies_long[1:] - energies_long[:-1])[:, None]
                * flux_long[1:-1],
                axis=0,
            )
        )
        energy_residual_long = (
            com_energy_long
            - exact_interface_long
            - outer_correction_long
            - internal_work_long
        )
        com_energy = float(com_energy_long)
        exact_interface = float(exact_interface_long)
        outer_correction = float(outer_correction_long)
        internal_work = float(internal_work_long)
        energy_residual = float(energy_residual_long)
        energy_scale = max(
            abs(com_energy),
            abs(exact_interface),
            abs(outer_correction),
            abs(internal_work),
            1.0e-300,
        )
        energy_relative = abs(energy_residual) / energy_scale
        energies = np.asarray(energies_long, dtype=float)
        face_energies = np.asarray(face_energies_long, dtype=float)

        directions = grid.directions if directions_hydrogen is None else np.asarray(directions_hydrogen, dtype=float)
        if directions.shape != (grid.n_angle, 3):
            raise ValueError("directions_hydrogen shape mismatch")
        p_red = (face_energies[0] / c) * np.column_stack((np.ones(grid.n_angle), directions))
        p_blue = (face_energies[-1] / c) * np.column_stack((np.ones(grid.n_angle), directions))
        com_four = np.sum(
            grid.weights[:, None] * (flux[0, :, None] * p_red - flux[-1, :, None] * p_blue),
            axis=0,
        )
        native_four = -com_four
        return FrequencyLiouvilleResult(
            occupation_action=_readonly(occupation_action),
            number_action=_readonly(number),
            face_flux_m3_s=_readonly(flux),
            native_number_action_m3_s=_readonly(native_number),
            global_number_residual_m3_s=float(number_residual),
            com_energy_action_W_m3=com_energy,
            exact_interface_energy_action_W_m3=exact_interface,
            outer_centroid_correction_W_m3=outer_correction,
            cosmological_redshift_work_W_m3=internal_work,
            energy_identity_residual_W_m3=float(energy_residual),
            energy_identity_relative_residual=float(energy_relative),
            interface_atom_source_W_m3=0.0,
            interface_four_momentum_com=_readonly(com_four),
            interface_four_momentum_native=_readonly(native_four),
            interface_four_momentum_residual=_readonly(com_four + native_four),
        )

    def jvp(
        self,
        occupation: np.ndarray,
        occupation_direction: np.ndarray,
        *,
        face_speeds_x_s_inv: np.ndarray,
        grid: HarmonicGrid,
    ) -> FrequencyLiouvilleJVPResult:
        f, speeds = self._validated(occupation, face_speeds_x_s_inv, grid)
        direction = np.asarray(occupation_direction, dtype=float)
        if direction.shape != f.shape or not np.all(np.isfinite(direction)):
            raise ValueError("occupation_direction shape mismatch or nonfinite")
        sorted_direction = direction[self.sorted_indices]
        zero = np.zeros(grid.n_angle)
        flux_jvp = self._face_flux(sorted_direction, speeds, zero, zero)
        number_sorted = flux_jvp[:-1] - flux_jvp[1:]
        number = np.empty_like(number_sorted)
        number[self.sorted_indices] = number_sorted
        native = -flux_jvp[0] + flux_jvp[-1]
        residual = float(
            np.sum(number_sorted * grid.weights[None, :])
            + np.sum(native * grid.weights)
        )
        return FrequencyLiouvilleJVPResult(
            occupation_action_jvp=_readonly(number / self.network.mode_measure[:, None]),
            number_action_jvp=_readonly(number),
            face_flux_jvp_m3_s=_readonly(flux_jvp),
            global_number_residual_jvp_m3_s=residual,
        )


def angular_scalarization_no_go_witness(grid: HarmonicGrid) -> AngularScalarizationNoGoWitness:
    directions = np.asarray(grid.directions, dtype=float)
    weights = np.asarray(grid.weights, dtype=float)
    weighted_mean = np.sum(weights[:, None] * directions, axis=0)
    variances = np.sum(weights[:, None] * (directions - weighted_mean) ** 2, axis=0)
    axis = int(np.argmax(variances))
    mode = directions[:, axis] - float(weighted_mean[axis])
    amplitude = 0.90 / max(float(np.max(np.abs(mode))), 1.0e-300)
    a = 1.0 + amplitude * mode
    b = 1.0 - amplitude * mode
    scalar_a = float(np.sum(weights * a))
    scalar_b = float(np.sum(weights * b))
    momentum_a = np.sum(weights[:, None] * a[:, None] * directions, axis=0)
    momentum_b = np.sum(weights[:, None] * b[:, None] * directions, axis=0)
    monopole = scalar_a - scalar_b
    no_go = bool(
        abs(monopole) < 2.0e-15
        and np.linalg.norm(momentum_a - momentum_b) > 1.0e-12
    )
    return AngularScalarizationNoGoWitness(
        field_a=_readonly(a),
        field_b=_readonly(b),
        scalarized_value_a=scalar_a,
        scalarized_value_b=scalar_b,
        monopole_residual=float(monopole),
        momentum_a=_readonly(momentum_a),
        momentum_b=_readonly(momentum_b),
        no_unique_scalar_momentum_preserving_map=no_go,
    )


__all__ = [
    "AngularScalarizationNoGoWitness",
    "ConservativeFrequencyLiouville",
    "FrequencyLiouvilleJVPResult",
    "FrequencyLiouvilleResult",
    "angular_scalarization_no_go_witness",
]
