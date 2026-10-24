"""Conservative far-boundary coupling for PR-04C1B/C2.

The original-HyRec radiation representation and the 35-state COM--KHW
collision representation remain distinct.  A source-derived interface packet
changes only the exact outer COM state (`FR00` or `FB02`) through a finite-volume
number flux.  Exact face-frequency energy is retained independently from the
finite-cell energy centroid so a representation boundary cannot manufacture an
atomic recoil source.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from typing import Mapping

import numpy as np
from scipy.constants import c, h
from scipy.sparse.linalg import LinearOperator, gmres

from full_bianchi_hyrec.background.branch_events import piecewise_linear_roots

from .nonlinear_bose_release import (
    HarmonicGrid,
    apply_nonlinear_bose_jvp,
    apply_nonlinear_bose_operator,
    bose_free_energy,
    bose_photon_number,
)
from .nonlinear_bose_runtime import CollisionNetwork, implicit_bose_step
from .split_domain_exchange import (
    ExchangeDirection,
    ExchangePacket,
    InterfaceSide,
)


_REL_TOL = 3.0e-14
_ABS_TOL = 1.0e-300


def _close(first: float, second: float) -> bool:
    return math.isclose(float(first), float(second), rel_tol=_REL_TOL, abs_tol=_ABS_TOL)


@dataclass(frozen=True)
class FarBoundaryCell:
    """Exact COM--KHW cell adjacent to one physical interface face."""

    side: InterfaceSide
    label: str
    index: int
    interval: tuple[float, float]
    face_x: float
    mode_measure_m3: float
    equilibrium_weight_m3: float
    centroid_frequency_Hz: float

    def __post_init__(self) -> None:
        left, right = self.interval
        if not (math.isfinite(left) and math.isfinite(right) and right > left):
            raise ValueError("boundary interval must be finite and ordered")
        if self.index < 0 or not self.label:
            raise ValueError("boundary state identity is invalid")
        if self.mode_measure_m3 <= 0.0 or self.equilibrium_weight_m3 <= 0.0:
            raise ValueError("boundary measures must be positive")
        if self.centroid_frequency_Hz <= 0.0:
            raise ValueError("boundary centroid frequency must be positive")
        expected_label = "FR00" if self.side is InterfaceSide.RED else "FB02"
        expected_face = -21.25 if self.side is InterfaceSide.RED else 21.25
        expected_interval_face = left if self.side is InterfaceSide.RED else right
        if self.label != expected_label:
            raise ValueError("boundary label is inconsistent with interface side")
        if not _close(self.face_x, expected_face) or not _close(
            expected_interval_face, expected_face
        ):
            raise ValueError("boundary interval does not meet the declared face")


@dataclass(frozen=True)
class FarBoundaryAdapter:
    """Byte-derived ownership adapter for `FR00` and `FB02`."""

    network: CollisionNetwork
    red: FarBoundaryCell
    blue: FarBoundaryCell

    @classmethod
    def from_network(cls, network: CollisionNetwork) -> "FarBoundaryAdapter":
        if not isinstance(network, CollisionNetwork):
            raise TypeError("network must be a CollisionNetwork")
        labels = network.state_labels.astype(str).tolist()

        def build(side: InterfaceSide, label: str) -> FarBoundaryCell:
            matches = [index for index, value in enumerate(labels) if value == label]
            if len(matches) != 1:
                raise ValueError(f"expected exactly one {label} boundary state")
            index = matches[0]
            interval = tuple(float(value) for value in network.state_intervals[index])
            face_x = -21.25 if side is InterfaceSide.RED else 21.25
            centroid = float(network.momentum_scale[index] * c / h)
            return FarBoundaryCell(
                side=side,
                label=label,
                index=index,
                interval=interval,
                face_x=face_x,
                mode_measure_m3=float(network.mode_measure[index]),
                equilibrium_weight_m3=float(network.equilibrium_weight[index]),
                centroid_frequency_Hz=centroid,
            )

        return cls(
            network=network,
            red=build(InterfaceSide.RED, "FR00"),
            blue=build(InterfaceSide.BLUE, "FB02"),
        )

    def for_side(self, side: InterfaceSide) -> FarBoundaryCell:
        side = InterfaceSide(side)
        return self.red if side is InterfaceSide.RED else self.blue

    def occupation_increment(
        self,
        accumulator: "BoundaryTransferAccumulator",
        *,
        n_H_m3: float,
        angular_weights: np.ndarray,
    ) -> np.ndarray:
        """Return the integrated uniform-angular COM occupation increment.

        The unique scalar conversion is

        ``Delta f = sigma n_H q / g_cell``

        where ``q`` is the integrated packet number per H and the normalized
        angular weights sum to one.
        """

        if not isinstance(accumulator, BoundaryTransferAccumulator):
            raise TypeError("accumulator must be a BoundaryTransferAccumulator")
        if not math.isfinite(n_H_m3) or n_H_m3 <= 0.0:
            raise ValueError("n_H_m3 must be positive and finite")
        weights = np.asarray(angular_weights, dtype=float)
        if weights.ndim != 1 or len(weights) == 0:
            raise ValueError("angular_weights must be one-dimensional")
        if np.any(weights <= 0.0) or not np.all(np.isfinite(weights)):
            raise ValueError("angular_weights must be finite and positive")
        if not math.isclose(float(np.sum(weights)), 1.0, rel_tol=3e-14, abs_tol=3e-15):
            raise ValueError("angular_weights must sum to one")

        cell = self.for_side(accumulator.side)
        expected_direction = (
            ExchangeDirection.COM_TO_NATIVE
            if accumulator.side is InterfaceSide.RED
            else ExchangeDirection.NATIVE_TO_COM
        )
        if accumulator.direction is not expected_direction:
            raise ValueError("accumulator direction is inconsistent with side")
        sign_com = -1.0 if accumulator.side is InterfaceSide.RED else 1.0
        increment = np.zeros((self.network.n_state, len(weights)), dtype=float)
        increment[cell.index, :] = (
            sign_com * float(n_H_m3) * accumulator.number_per_H / cell.mode_measure_m3
        )
        return increment


@dataclass(frozen=True)
class BoundaryTransferAccumulator:
    """Positive integrated transfer magnitude for one source-derived packet."""

    side: InterfaceSide
    direction: ExchangeDirection
    interface_x: float
    interface_frequency_Hz: float
    number_per_H: float
    reference_number_per_H: float
    distortion_number_per_H: float
    energy_J_per_H: float
    reference_energy_J_per_H: float
    distortion_energy_J_per_H: float
    atom_energy_J_per_H: float
    source_snapshot_z: float
    dt_s: float

    def __post_init__(self) -> None:
        values = (
            self.interface_x,
            self.interface_frequency_Hz,
            self.number_per_H,
            self.reference_number_per_H,
            self.distortion_number_per_H,
            self.energy_J_per_H,
            self.reference_energy_J_per_H,
            self.distortion_energy_J_per_H,
            self.atom_energy_J_per_H,
            self.source_snapshot_z,
            self.dt_s,
        )
        if not all(math.isfinite(float(value)) for value in values):
            raise ValueError("accumulator fields must be finite")
        if self.dt_s <= 0.0:
            raise ValueError("dt_s must be positive")
        if self.number_per_H <= 0.0 or self.energy_J_per_H <= 0.0:
            raise ValueError("integrated number and energy must be positive")
        if self.reference_number_per_H < 0.0 or self.reference_energy_J_per_H < 0.0:
            raise ValueError("reference components must be nonnegative")
        if not _close(
            self.number_per_H,
            self.reference_number_per_H + self.distortion_number_per_H,
        ):
            raise ValueError("number components do not add to total")
        if not _close(
            self.energy_J_per_H,
            self.reference_energy_J_per_H + self.distortion_energy_J_per_H,
        ):
            raise ValueError("energy components do not add to total")
        if not _close(self.atom_energy_J_per_H, 0.0):
            raise ValueError("pure interface transfer must have zero atom energy")
        if not _close(
            self.energy_J_per_H,
            h * self.interface_frequency_Hz * self.number_per_H,
        ):
            raise ValueError("integrated energy is inconsistent with face frequency")
        expected_x = -21.25 if self.side is InterfaceSide.RED else 21.25
        expected_direction = (
            ExchangeDirection.COM_TO_NATIVE
            if self.side is InterfaceSide.RED
            else ExchangeDirection.NATIVE_TO_COM
        )
        if not _close(self.interface_x, expected_x):
            raise ValueError("interface x is inconsistent with side")
        if self.direction is not expected_direction:
            raise ValueError("direction is inconsistent with interface side")

    @classmethod
    def from_packet(
        cls,
        packet: ExchangePacket,
        *,
        dt_s: float,
    ) -> "BoundaryTransferAccumulator":
        if not isinstance(packet, ExchangePacket):
            raise TypeError("packet must be an ExchangePacket")
        if not math.isfinite(dt_s) or dt_s <= 0.0:
            raise ValueError("dt_s must be positive and finite")
        return cls(
            side=packet.side,
            direction=packet.direction,
            interface_x=packet.interface_x,
            interface_frequency_Hz=packet.interface_frequency_Hz,
            number_per_H=packet.total_number_flux_per_H_s * dt_s,
            reference_number_per_H=packet.reference_number_flux_per_H_s * dt_s,
            distortion_number_per_H=packet.distortion_number_flux_per_H_s * dt_s,
            energy_J_per_H=packet.photon_energy_flux_W_per_H * dt_s,
            reference_energy_J_per_H=packet.reference_photon_energy_flux_W_per_H * dt_s,
            distortion_energy_J_per_H=packet.distortion_photon_energy_flux_W_per_H * dt_s,
            atom_energy_J_per_H=packet.atom_energy_flux_W_per_H * dt_s,
            source_snapshot_z=packet.source_snapshot_z,
            dt_s=float(dt_s),
        )

    def scaled(self, factor: float) -> "BoundaryTransferAccumulator":
        """Return the same transfer with every extensive component scaled."""
        if not math.isfinite(factor) or factor <= 0.0:
            raise ValueError("accumulator scale factor must be positive and finite")
        return BoundaryTransferAccumulator(
            side=self.side,
            direction=self.direction,
            interface_x=self.interface_x,
            interface_frequency_Hz=self.interface_frequency_Hz,
            number_per_H=self.number_per_H * factor,
            reference_number_per_H=self.reference_number_per_H * factor,
            distortion_number_per_H=self.distortion_number_per_H * factor,
            energy_J_per_H=self.energy_J_per_H * factor,
            reference_energy_J_per_H=self.reference_energy_J_per_H * factor,
            distortion_energy_J_per_H=self.distortion_energy_J_per_H * factor,
            atom_energy_J_per_H=self.atom_energy_J_per_H * factor,
            source_snapshot_z=self.source_snapshot_z,
            dt_s=self.dt_s,
        )

    def to_dict(self) -> dict[str, float | str]:
        return {
            "side": self.side.value,
            "direction": self.direction.value,
            "interface_x": self.interface_x,
            "interface_frequency_Hz": self.interface_frequency_Hz,
            "number_per_H": self.number_per_H,
            "reference_number_per_H": self.reference_number_per_H,
            "distortion_number_per_H": self.distortion_number_per_H,
            "energy_J_per_H": self.energy_J_per_H,
            "reference_energy_J_per_H": self.reference_energy_J_per_H,
            "distortion_energy_J_per_H": self.distortion_energy_J_per_H,
            "atom_energy_J_per_H": self.atom_energy_J_per_H,
            "source_snapshot_z": self.source_snapshot_z,
            "dt_s": self.dt_s,
        }

    @classmethod
    def from_dict(
        cls, values: Mapping[str, float | str]
    ) -> "BoundaryTransferAccumulator":
        payload = dict(values)
        payload["side"] = InterfaceSide(str(payload["side"]))
        payload["direction"] = ExchangeDirection(str(payload["direction"]))
        return cls(**payload)  # type: ignore[arg-type]

    @property
    def sha256(self) -> str:
        payload = json.dumps(
            self.to_dict(), sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True)
class CoupledResidualMetrics:
    """Net residual and normwise backward-error diagnostics."""

    scaled_relative: float
    backward_error_relative: float
    raw_residual_inf: float
    equation_scale: float
    gross_collision_scale: float
    transfer_residual_inf: float
    number_relative_residual: float


@dataclass(frozen=True)
class CoupledInterfaceProblem:
    """Source-conditioned monolithic collision/interface residual.

    Resolved occupations use ``f=exp(u)``.  Each positive integrated packet is
    multiplied by ``rho=exp(v)`` and constrained by ``rho-1=0`` in the same
    residual, which keeps the transfer block nonsingular while retaining the
    packet as an explicit nonlinear unknown.
    """

    network: CollisionNetwork
    grid: HarmonicGrid
    packets: tuple[ExchangePacket, ...]
    n_H_m3: float
    dt_s: float
    enabled: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.network, CollisionNetwork):
            raise TypeError("network must be a CollisionNetwork")
        if not isinstance(self.grid, HarmonicGrid):
            raise TypeError("grid must be a HarmonicGrid")
        if not math.isfinite(self.n_H_m3) or self.n_H_m3 <= 0.0:
            raise ValueError("n_H_m3 must be positive and finite")
        if not math.isfinite(self.dt_s) or self.dt_s <= 0.0:
            raise ValueError("dt_s must be positive and finite")
        if not self.enabled and self.packets:
            # Guard-off is represented by an empty transfer block.  This avoids
            # a logarithm of an exact zero accumulator.
            object.__setattr__(self, "packets", tuple())
        if self.enabled and not self.packets:
            raise ValueError("enabled interface requires at least one packet")
        if len({packet.side for packet in self.packets}) != len(self.packets):
            raise ValueError("at most one packet per interface side is allowed")
        ordered = tuple(
            sorted(
                self.packets,
                key=lambda packet: 0 if packet.side is InterfaceSide.RED else 1,
            )
        )
        if ordered and len({packet.source_snapshot_z for packet in ordered}) != 1:
            raise ValueError("coupled packets must come from one source snapshot")
        object.__setattr__(self, "packets", ordered)
        object.__setattr__(self, "adapter", FarBoundaryAdapter.from_network(self.network))
        object.__setattr__(
            self,
            "base_accumulators",
            tuple(
                BoundaryTransferAccumulator.from_packet(packet, dt_s=self.dt_s)
                for packet in ordered
            ),
        )

    @property
    def n_transfer(self) -> int:
        return len(self.base_accumulators)  # type: ignore[attr-defined]

    @property
    def occupation_shape(self) -> tuple[int, int]:
        return (self.network.n_state, self.grid.n_angle)

    @property
    def vector_size(self) -> int:
        return self.network.n_state * self.grid.n_angle + self.n_transfer

    def pack(self, log_occupation: np.ndarray, log_rho: np.ndarray) -> np.ndarray:
        log_f = np.asarray(log_occupation, dtype=float)
        log_rho = np.asarray(log_rho, dtype=float)
        if log_f.shape != self.occupation_shape:
            raise ValueError("log occupation shape mismatch")
        if log_rho.shape != (self.n_transfer,):
            raise ValueError("log transfer multiplier shape mismatch")
        if not np.all(np.isfinite(log_f)) or not np.all(np.isfinite(log_rho)):
            raise ValueError("log variables must be finite")
        return np.concatenate((log_f.ravel(), log_rho))

    def unpack(self, vector: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        values = np.asarray(vector, dtype=float)
        if values.shape != (self.vector_size,):
            raise ValueError("coupled vector size mismatch")
        split = self.network.n_state * self.grid.n_angle
        return values[:split].reshape(self.occupation_shape), values[split:]

    def unpack_residual(self, vector: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        return self.unpack(vector)

    def _base_increments(self) -> tuple[np.ndarray, ...]:
        adapter: FarBoundaryAdapter = self.adapter  # type: ignore[attr-defined]
        return tuple(
            adapter.occupation_increment(
                accumulator,
                n_H_m3=self.n_H_m3,
                angular_weights=self.grid.weights,
            )
            for accumulator in self.base_accumulators  # type: ignore[attr-defined]
        )

    def interface_increment(self, log_rho: np.ndarray) -> np.ndarray:
        log_rho = np.asarray(log_rho, dtype=float)
        if log_rho.shape != (self.n_transfer,):
            raise ValueError("log transfer multiplier shape mismatch")
        rho = np.exp(log_rho)
        increment = np.zeros(self.occupation_shape, dtype=float)
        for scale, base in zip(rho, self._base_increments()):
            increment += float(scale) * base
        return increment

    def interface_number_change_m3(self, log_rho: np.ndarray) -> float:
        log_rho = np.asarray(log_rho, dtype=float)
        if log_rho.shape != (self.n_transfer,):
            raise ValueError("log transfer multiplier shape mismatch")
        rho = np.exp(log_rho)
        total = 0.0
        for scale, accumulator in zip(
            rho, self.base_accumulators  # type: ignore[attr-defined]
        ):
            sign_com = -1.0 if accumulator.side is InterfaceSide.RED else 1.0
            total += (
                sign_com
                * self.n_H_m3
                * accumulator.number_per_H
                * float(scale)
            )
        return float(total)

    def _validated_old(self, old_occupation: np.ndarray) -> np.ndarray:
        old = np.asarray(old_occupation, dtype=float)
        if old.shape != self.occupation_shape:
            raise ValueError("old occupation shape mismatch")
        if np.any(old <= 0.0) or not np.all(np.isfinite(old)):
            raise ValueError("old occupation must be finite and strictly positive")
        return old

    def _occupation_scale(self, old_occupation: np.ndarray) -> np.ndarray:
        old = self._validated_old(old_occupation)
        interface_scale = np.zeros_like(old)
        for base in self._base_increments():
            interface_scale += np.abs(base)
        return np.maximum(np.maximum(np.abs(old), interface_scale), 1.0e-300)

    def unscaled_residual(
        self, vector: np.ndarray, old_occupation: np.ndarray
    ) -> np.ndarray:
        old = self._validated_old(old_occupation)
        log_f, log_rho = self.unpack(vector)
        if np.max(log_f) > 700.0 or np.min(log_f) < -745.0:
            raise FloatingPointError("log occupation is outside finite exponential range")
        if np.max(log_rho, initial=0.0) > 700.0 or np.min(log_rho, initial=0.0) < -745.0:
            raise FloatingPointError("log transfer multiplier is outside range")
        occupation = np.exp(log_f)
        rho = np.exp(log_rho)
        action = apply_nonlinear_bose_operator(
            occupation,
            mode_measure=self.network.mode_measure,
            equilibrium_weight=self.network.equilibrium_weight,
            pair_moments=self.network.pair_moments,
            same_cell_rates=self.network.same_cell_rates,
            grid=self.grid,
            photon_momentum_scale=self.network.momentum_scale,
        ).occupation_action
        residual_f = (
            occupation
            - old
            - self.dt_s * action
            - self.interface_increment(log_rho)
        )
        residual_rho = rho - 1.0
        return self.pack(residual_f, residual_rho)

    def scaled_residual(
        self, vector: np.ndarray, old_occupation: np.ndarray
    ) -> np.ndarray:
        raw_f, raw_rho = self.unpack_residual(
            self.unscaled_residual(vector, old_occupation)
        )
        return self.pack(raw_f / self._occupation_scale(old_occupation), raw_rho)

    def residual_metrics(
        self, vector: np.ndarray, old_occupation: np.ndarray
    ) -> CoupledResidualMetrics:
        """Return both the net residual and a gross-term backward error.

        Near a dilute Bose--Einstein state, the physical collision action is a
        difference of much larger forward and reverse terms.  The net residual
        divided only by ``f`` can therefore reach a float64 cancellation floor
        even when the backward error with respect to the terms actually summed
        in the equation is at machine precision.  ``gross_action_scale`` is
        carried by the collision operator specifically for this normalization.
        """

        old = self._validated_old(old_occupation)
        raw_f, raw_rho = self.unpack_residual(
            self.unscaled_residual(vector, old)
        )
        log_f, log_rho = self.unpack(vector)
        occupation = np.exp(log_f)
        action = apply_nonlinear_bose_operator(
            occupation,
            mode_measure=self.network.mode_measure,
            equilibrium_weight=self.network.equilibrium_weight,
            pair_moments=self.network.pair_moments,
            same_cell_rates=self.network.same_cell_rates,
            grid=self.grid,
            photon_momentum_scale=self.network.momentum_scale,
        )
        interface = self.interface_increment(log_rho)
        minimum_weight = max(float(np.min(self.grid.weights)), 1.0e-300)
        minimum_measure = max(float(np.min(self.network.mode_measure)), 1.0e-300)
        gross_collision_scale = (
            self.dt_s
            * float(action.gross_action_scale)
            / (minimum_measure * minimum_weight)
        )
        equation_scale = max(
            float(np.max(np.abs(old))),
            float(np.max(np.abs(occupation))),
            float(np.max(np.abs(interface), initial=0.0)),
            gross_collision_scale,
            1.0e-300,
        )
        raw_inf = float(np.max(np.abs(raw_f), initial=0.0))
        transfer_inf = float(np.max(np.abs(raw_rho), initial=0.0))
        scaled_relative = float(
            np.max(np.abs(raw_f / self._occupation_scale(old)), initial=0.0)
        )
        backward = max(raw_inf / equation_scale, transfer_inf)
        number_before = bose_photon_number(
            old, mode_measure=self.network.mode_measure, grid=self.grid
        )
        number_after = bose_photon_number(
            occupation, mode_measure=self.network.mode_measure, grid=self.grid
        )
        expected_number = number_before + self.interface_number_change_m3(log_rho)
        number_relative = abs(number_after - expected_number) / max(
            abs(number_before), abs(expected_number), 1.0e-300
        )
        return CoupledResidualMetrics(
            scaled_relative=scaled_relative,
            backward_error_relative=float(backward),
            raw_residual_inf=raw_inf,
            equation_scale=float(equation_scale),
            gross_collision_scale=float(gross_collision_scale),
            transfer_residual_inf=transfer_inf,
            number_relative_residual=float(number_relative),
        )

    def jvp(
        self,
        vector: np.ndarray,
        direction: np.ndarray,
        old_occupation: np.ndarray,
        *,
        scaled: bool = True,
    ) -> np.ndarray:
        self._validated_old(old_occupation)
        log_f, log_rho = self.unpack(vector)
        du, dv = self.unpack(direction)
        occupation = np.exp(log_f)
        rho = np.exp(log_rho)
        d_occupation = occupation * du
        action_jvp = apply_nonlinear_bose_jvp(
            occupation,
            d_occupation,
            mode_measure=self.network.mode_measure,
            equilibrium_weight=self.network.equilibrium_weight,
            pair_moments=self.network.pair_moments,
            same_cell_rates=self.network.same_cell_rates,
            grid=self.grid,
        ).occupation_action_jvp
        d_interface = np.zeros_like(occupation)
        for scale, scalar_direction, base in zip(
            rho, dv, self._base_increments()
        ):
            d_interface += float(scale * scalar_direction) * base
        result_f = d_occupation - self.dt_s * action_jvp - d_interface
        result_rho = rho * dv
        if scaled:
            result_f = result_f / self._occupation_scale(old_occupation)
        return self.pack(result_f, result_rho)


@dataclass(frozen=True)
class SideTransferLedger:
    """One side of the exact number/transported-energy exchange ledger."""

    side: InterfaceSide
    direction: ExchangeDirection
    native_number_change_per_H: float
    com_number_change_per_H: float
    native_energy_change_J_per_H: float
    com_energy_change_J_per_H: float
    atom_energy_change_J_per_H: float
    cell_centroid_energy_proxy_J_per_H: float
    unresolved_energy_correction_J_per_H: float

    @property
    def number_residual_per_H(self) -> float:
        return self.native_number_change_per_H + self.com_number_change_per_H

    @property
    def transported_energy_residual_J_per_H(self) -> float:
        return self.native_energy_change_J_per_H + self.com_energy_change_J_per_H

    def validate(self) -> None:
        if self.number_residual_per_H != 0.0:
            raise ValueError("side number ledger does not cancel exactly")
        if self.transported_energy_residual_J_per_H != 0.0:
            raise ValueError("side transported-energy ledger does not cancel exactly")
        if self.atom_energy_change_J_per_H != 0.0:
            raise ValueError("pure representation crossing has nonzero atom source")
        reconstructed = (
            self.cell_centroid_energy_proxy_J_per_H
            + self.unresolved_energy_correction_J_per_H
        )
        if not _close(reconstructed, self.com_energy_change_J_per_H):
            raise ValueError("cell proxy plus unresolved correction is inconsistent")


@dataclass(frozen=True)
class InterfaceTransferLedger:
    """Global exact exchange ledger for one coupled interface step."""

    n_H_m3: float
    sides: tuple[SideTransferLedger, ...]
    native_number_change_per_H: float
    com_number_change_per_H: float
    native_energy_change_J_per_H: float
    com_energy_change_J_per_H: float
    atom_energy_change_J_per_H: float

    @classmethod
    def from_accumulators(
        cls,
        adapter: FarBoundaryAdapter,
        accumulators: tuple[BoundaryTransferAccumulator, ...],
        *,
        n_H_m3: float,
    ) -> "InterfaceTransferLedger":
        if not isinstance(adapter, FarBoundaryAdapter):
            raise TypeError("adapter must be a FarBoundaryAdapter")
        if not math.isfinite(n_H_m3) or n_H_m3 <= 0.0:
            raise ValueError("n_H_m3 must be positive and finite")
        if len({accumulator.side for accumulator in accumulators}) != len(accumulators):
            raise ValueError("at most one accumulator per interface side is allowed")

        side_ledgers: list[SideTransferLedger] = []
        for accumulator in accumulators:
            if not isinstance(accumulator, BoundaryTransferAccumulator):
                raise TypeError("all accumulators must be BoundaryTransferAccumulator")
            cell = adapter.for_side(accumulator.side)
            sign_com = -1.0 if accumulator.side is InterfaceSide.RED else 1.0
            com_number = sign_com * accumulator.number_per_H
            native_number = -com_number
            com_energy = sign_com * accumulator.energy_J_per_H
            native_energy = -com_energy
            cell_proxy = (
                sign_com
                * h
                * cell.centroid_frequency_Hz
                * accumulator.number_per_H
            )
            correction = com_energy - cell_proxy
            row = SideTransferLedger(
                side=accumulator.side,
                direction=accumulator.direction,
                native_number_change_per_H=native_number,
                com_number_change_per_H=com_number,
                native_energy_change_J_per_H=native_energy,
                com_energy_change_J_per_H=com_energy,
                atom_energy_change_J_per_H=accumulator.atom_energy_J_per_H,
                cell_centroid_energy_proxy_J_per_H=cell_proxy,
                unresolved_energy_correction_J_per_H=correction,
            )
            row.validate()
            side_ledgers.append(row)

        result = cls(
            n_H_m3=float(n_H_m3),
            sides=tuple(side_ledgers),
            native_number_change_per_H=float(
                sum(row.native_number_change_per_H for row in side_ledgers)
            ),
            com_number_change_per_H=float(
                sum(row.com_number_change_per_H for row in side_ledgers)
            ),
            native_energy_change_J_per_H=float(
                sum(row.native_energy_change_J_per_H for row in side_ledgers)
            ),
            com_energy_change_J_per_H=float(
                sum(row.com_energy_change_J_per_H for row in side_ledgers)
            ),
            atom_energy_change_J_per_H=float(
                sum(row.atom_energy_change_J_per_H for row in side_ledgers)
            ),
        )
        result.validate()
        return result

    @property
    def number_residual_per_H(self) -> float:
        return self.native_number_change_per_H + self.com_number_change_per_H

    @property
    def transported_energy_residual_J_per_H(self) -> float:
        return self.native_energy_change_J_per_H + self.com_energy_change_J_per_H

    @property
    def number_residual_m3(self) -> float:
        return self.n_H_m3 * self.number_residual_per_H

    @property
    def transported_energy_residual_J_m3(self) -> float:
        return self.n_H_m3 * self.transported_energy_residual_J_per_H

    def validate(self) -> None:
        for row in self.sides:
            row.validate()
        if self.number_residual_per_H != 0.0:
            raise ValueError("global interface number ledger does not cancel exactly")
        if self.transported_energy_residual_J_per_H != 0.0:
            raise ValueError("global transported-energy ledger does not cancel exactly")
        if self.atom_energy_change_J_per_H != 0.0:
            raise ValueError("global interface atom source must be zero")


@dataclass(frozen=True)
class BoundarySpeedAudit:
    red_roots: np.ndarray
    blue_roots: np.ndarray
    red_positive_integral: float
    red_negative_integral: float
    blue_positive_integral: float
    blue_negative_integral: float
    red_exact_signed_integral: float
    blue_exact_signed_integral: float
    red_endpoint_heuristic_integral: float
    blue_endpoint_heuristic_integral: float
    red_endpoint_heuristic_error: float
    blue_endpoint_heuristic_error: float

    @property
    def red_total_absolute_integral(self) -> float:
        return self.red_positive_integral + self.red_negative_integral

    @property
    def blue_total_absolute_integral(self) -> float:
        return self.blue_positive_integral + self.blue_negative_integral


def _validated_speed_series(
    times: np.ndarray, values: np.ndarray, name: str
) -> tuple[np.ndarray, np.ndarray]:
    time = np.asarray(times, dtype=float)
    speed = np.asarray(values, dtype=float)
    if time.ndim != 1 or speed.shape != time.shape or len(time) < 2:
        raise ValueError(f"{name} must be one-dimensional and match times")
    if not np.all(np.isfinite(time)) or not np.all(np.isfinite(speed)):
        raise ValueError("boundary speed histories must be finite")
    if np.any(np.diff(time) <= 0.0):
        raise ValueError("boundary speed times must be strictly increasing")
    return time, speed


def _positive_linear_integral(y0: float, y1: float, duration: float) -> float:
    if y0 >= 0.0 and y1 >= 0.0:
        return 0.5 * duration * (y0 + y1)
    if y0 <= 0.0 and y1 <= 0.0:
        return 0.0
    fraction = -y0 / (y1 - y0)
    if y0 > 0.0:
        return 0.5 * duration * fraction * y0
    return 0.5 * duration * (1.0 - fraction) * y1


def _signed_piecewise_integrals(
    times: np.ndarray, values: np.ndarray
) -> tuple[float, float]:
    positive = 0.0
    negative = 0.0
    for left, right, y0, y1 in zip(
        times[:-1], times[1:], values[:-1], values[1:]
    ):
        duration = float(right - left)
        positive += _positive_linear_integral(float(y0), float(y1), duration)
        negative += _positive_linear_integral(float(-y0), float(-y1), duration)
    return float(positive), float(negative)


def _endpoint_heuristic(values: np.ndarray, total_absolute: float) -> float:
    # This intentionally models the forbidden shortcut: use one endpoint sign
    # for the whole step and discard all internal branch changes.
    sign_source = float(values[0])
    if sign_source == 0.0:
        sign_source = float(values[-1])
    return math.copysign(float(total_absolute), sign_source) if sign_source else 0.0


def audit_boundary_speed_history(
    times: np.ndarray,
    red_speed: np.ndarray,
    blue_speed: np.ndarray,
) -> BoundarySpeedAudit:
    """Audit exact piecewise-linear red/blue branch localization.

    Positive and negative portions are integrated separately after every zero.
    The endpoint heuristic is retained only as an adversarial diagnostic and is
    never used to apply a flux.
    """

    time, red = _validated_speed_series(times, red_speed, "red_speed")
    _, blue = _validated_speed_series(times, blue_speed, "blue_speed")
    red_positive, red_negative = _signed_piecewise_integrals(time, red)
    blue_positive, blue_negative = _signed_piecewise_integrals(time, blue)
    red_exact = red_positive - red_negative
    blue_exact = blue_positive - blue_negative
    red_heuristic = _endpoint_heuristic(red, red_positive + red_negative)
    blue_heuristic = _endpoint_heuristic(blue, blue_positive + blue_negative)
    return BoundarySpeedAudit(
        red_roots=piecewise_linear_roots(time, red),
        blue_roots=piecewise_linear_roots(time, blue),
        red_positive_integral=red_positive,
        red_negative_integral=red_negative,
        blue_positive_integral=blue_positive,
        blue_negative_integral=blue_negative,
        red_exact_signed_integral=red_exact,
        blue_exact_signed_integral=blue_exact,
        red_endpoint_heuristic_integral=red_heuristic,
        blue_endpoint_heuristic_integral=blue_heuristic,
        red_endpoint_heuristic_error=red_heuristic - red_exact,
        blue_endpoint_heuristic_error=blue_heuristic - blue_exact,
    )


@dataclass(frozen=True)
class CoupledInterfaceRestartState:
    """Portable restart state for one coupled interface step."""

    occupation: np.ndarray
    accumulators: tuple[BoundaryTransferAccumulator, ...]
    dt_s: float
    interface_enabled: bool

    def __post_init__(self) -> None:
        occupation = np.asarray(self.occupation, dtype=float)
        if occupation.ndim != 2 or occupation.size == 0:
            raise ValueError("restart occupation must be a nonempty two-dimensional array")
        if not np.all(np.isfinite(occupation)) or np.any(occupation <= 0.0):
            raise ValueError("restart occupation must be finite and strictly positive")
        if not math.isfinite(self.dt_s) or self.dt_s <= 0.0:
            raise ValueError("restart dt_s must be positive and finite")
        if not isinstance(self.interface_enabled, bool):
            raise TypeError("restart interface_enabled must be boolean")
        accumulators = tuple(self.accumulators)
        if not all(isinstance(item, BoundaryTransferAccumulator) for item in accumulators):
            raise TypeError("restart accumulators must be BoundaryTransferAccumulator values")
        occupation = occupation.copy()
        occupation.setflags(write=False)
        object.__setattr__(self, "occupation", occupation)
        object.__setattr__(self, "accumulators", accumulators)

    @classmethod
    def from_payload(cls, payload: Mapping[str, object]) -> "CoupledInterfaceRestartState":
        if not isinstance(payload, Mapping):
            raise TypeError("restart payload must be a mapping")
        required = {"occupation", "accumulators", "dt_s", "interface_enabled"}
        if set(payload) != required:
            raise ValueError("restart payload keys do not match the declared schema")
        accumulator_payload = payload["accumulators"]
        if not isinstance(accumulator_payload, list):
            raise TypeError("restart accumulators must be a list")
        return cls(
            occupation=np.asarray(payload["occupation"], dtype=float),
            accumulators=tuple(
                BoundaryTransferAccumulator.from_dict(item)
                for item in accumulator_payload
            ),
            dt_s=float(payload["dt_s"]),
            interface_enabled=payload["interface_enabled"],
        )

    def to_payload(self) -> dict[str, object]:
        return {
            "occupation": self.occupation.tolist(),
            "accumulators": [item.to_dict() for item in self.accumulators],
            "dt_s": self.dt_s,
            "interface_enabled": self.interface_enabled,
        }


@dataclass(frozen=True)
class CoupledInterfaceStepResult:
    occupation: np.ndarray
    accumulators: tuple[BoundaryTransferAccumulator, ...]
    ledger: InterfaceTransferLedger
    converged: bool
    newton_iterations: int
    total_gmres_iterations: int
    dt_s: float
    residual_relative: float
    backward_error_relative: float
    convergence_basis: str
    raw_residual_inf: float
    equation_scale: float
    minimum_occupation: float
    explicit_trial_minimum: float
    number_before_m3: float
    number_after_m3: float
    expected_number_after_m3: float
    number_relative_residual: float
    free_energy_before: float
    free_energy_after: float
    collision_entropy_production: float
    interface_enabled: bool

    def restart_payload(self) -> dict[str, object]:
        return CoupledInterfaceRestartState(
            occupation=self.occupation,
            accumulators=self.accumulators,
            dt_s=self.dt_s,
            interface_enabled=self.interface_enabled,
        ).to_payload()


def solve_coupled_interface(
    old_occupation: np.ndarray,
    problem: CoupledInterfaceProblem,
    *,
    nonlinear_rtol: float = 1.0e-11,
    max_newton: int = 16,
    gmres_rtol: float = 2.0e-9,
    gmres_restart: int = 40,
    gmres_maxiter: int = 160,
) -> CoupledInterfaceStepResult:
    """Solve the positive backward-Euler collision/interface residual."""

    if not isinstance(problem, CoupledInterfaceProblem):
        raise TypeError("problem must be a CoupledInterfaceProblem")
    old = problem._validated_old(old_occupation)
    if nonlinear_rtol <= 0.0 or gmres_rtol <= 0.0:
        raise ValueError("solver tolerances must be positive")

    if not problem.enabled:
        baseline = implicit_bose_step(
            old,
            dt_s=problem.dt_s,
            network=problem.network,
            grid=problem.grid,
            nonlinear_rtol=nonlinear_rtol,
            max_newton=max_newton,
            gmres_rtol=gmres_rtol,
            gmres_restart=gmres_restart,
            gmres_maxiter=gmres_maxiter,
        )
        final_action = apply_nonlinear_bose_operator(
            baseline.occupation,
            mode_measure=problem.network.mode_measure,
            equilibrium_weight=problem.network.equilibrium_weight,
            pair_moments=problem.network.pair_moments,
            same_cell_rates=problem.network.same_cell_rates,
            grid=problem.grid,
            photon_momentum_scale=problem.network.momentum_scale,
        )
        adapter: FarBoundaryAdapter = problem.adapter  # type: ignore[attr-defined]
        ledger = InterfaceTransferLedger.from_accumulators(
            adapter, tuple(), n_H_m3=problem.n_H_m3
        )
        return CoupledInterfaceStepResult(
            occupation=baseline.occupation,
            accumulators=tuple(),
            ledger=ledger,
            converged=baseline.converged,
            newton_iterations=baseline.newton_iterations,
            total_gmres_iterations=baseline.total_gmres_iterations,
            dt_s=problem.dt_s,
            residual_relative=baseline.residual_relative,
            backward_error_relative=baseline.residual_relative,
            convergence_basis="scaled_residual",
            raw_residual_inf=baseline.residual_relative
            * max(float(np.max(np.abs(old))), 1.0e-300),
            equation_scale=max(float(np.max(np.abs(old))), 1.0e-300),
            minimum_occupation=baseline.minimum_occupation,
            explicit_trial_minimum=baseline.explicit_trial_minimum,
            number_before_m3=baseline.number_before,
            number_after_m3=baseline.number_after,
            expected_number_after_m3=baseline.number_before,
            number_relative_residual=baseline.number_relative_change,
            free_energy_before=baseline.free_energy_before,
            free_energy_after=baseline.free_energy_after,
            collision_entropy_production=final_action.entropy_production,
            interface_enabled=False,
        )

    old_action = apply_nonlinear_bose_operator(
        old,
        mode_measure=problem.network.mode_measure,
        equilibrium_weight=problem.network.equilibrium_weight,
        pair_moments=problem.network.pair_moments,
        same_cell_rates=problem.network.same_cell_rates,
        grid=problem.grid,
        photon_momentum_scale=problem.network.momentum_scale,
    )
    explicit_trial = (
        old
        + problem.dt_s * old_action.occupation_action
        + problem.interface_increment(np.zeros(problem.n_transfer))
    )
    vector = problem.pack(np.log(old), np.zeros(problem.n_transfer))
    total_gmres = 0
    converged = False
    final_norm = math.inf
    final_backward = math.inf
    convergence_basis = "none"
    completed_iterations = 0

    for iteration in range(max_newton + 1):
        residual = problem.scaled_residual(vector, old)
        metrics = problem.residual_metrics(vector, old)
        final_norm = metrics.scaled_relative
        final_backward = metrics.backward_error_relative
        completed_iterations = iteration
        if final_norm <= nonlinear_rtol:
            converged = True
            convergence_basis = "scaled_residual"
            break
        if iteration == max_newton:
            break

        log_f, log_rho = problem.unpack(vector)
        occupation = np.exp(log_f)
        rho = np.exp(log_rho)
        scale_f = problem._occupation_scale(old)
        inverse_f_diagonal = (scale_f / np.maximum(occupation, 1.0e-300)).ravel()
        inverse_rho_diagonal = 1.0 / np.maximum(rho, 1.0e-300)
        inverse_diagonal = np.concatenate((inverse_f_diagonal, inverse_rho_diagonal))

        operator = LinearOperator(
            (problem.vector_size, problem.vector_size),
            matvec=lambda direction: problem.jvp(
                vector, np.asarray(direction, dtype=float), old, scaled=True
            ),
            dtype=float,
        )
        preconditioner = LinearOperator(
            (problem.vector_size, problem.vector_size),
            matvec=lambda value: inverse_diagonal * np.asarray(value, dtype=float),
            dtype=float,
        )
        counter = [0]

        def callback(_value):
            counter[0] += 1

        step, info = gmres(
            operator,
            -residual,
            M=preconditioner,
            rtol=gmres_rtol,
            atol=0.0,
            restart=gmres_restart,
            maxiter=gmres_maxiter,
            callback=callback,
            callback_type="pr_norm",
        )
        total_gmres += counter[0]
        if info != 0 or not np.all(np.isfinite(step)):
            raise RuntimeError(f"GMRES failed in coupled interface solve (info={info})")

        accepted = False
        damping = 1.0
        for _ in range(24):
            trial = vector + damping * step
            trial_log_f, trial_log_rho = problem.unpack(trial)
            if (
                np.max(trial_log_f) > 700.0
                or np.min(trial_log_f) < -745.0
                or np.max(trial_log_rho, initial=0.0) > 700.0
                or np.min(trial_log_rho, initial=0.0) < -745.0
            ):
                damping *= 0.5
                continue
            trial_residual = problem.scaled_residual(trial, old)
            trial_norm = float(np.max(np.abs(trial_residual)))
            if trial_norm < final_norm:
                vector = trial
                accepted = True
                break
            damping *= 0.5
        if not accepted:
            stalled = problem.residual_metrics(vector, old)
            if (
                stalled.backward_error_relative <= nonlinear_rtol
                and stalled.number_relative_residual <= nonlinear_rtol
            ):
                converged = True
                convergence_basis = "gross_backward_error"
                final_norm = stalled.scaled_relative
                final_backward = stalled.backward_error_relative
                break
            raise RuntimeError("coupled interface Newton line search failed")

    log_f, log_rho = problem.unpack(vector)
    occupation = np.exp(log_f)
    rho = np.exp(log_rho)
    final_metrics = problem.residual_metrics(vector, old)
    final_norm = final_metrics.scaled_relative
    final_backward = final_metrics.backward_error_relative
    accumulators = tuple(
        accumulator.scaled(float(scale))
        for accumulator, scale in zip(
            problem.base_accumulators, rho  # type: ignore[attr-defined]
        )
    )
    adapter = problem.adapter  # type: ignore[attr-defined]
    ledger = InterfaceTransferLedger.from_accumulators(
        adapter, accumulators, n_H_m3=problem.n_H_m3
    )
    number_before = bose_photon_number(
        old, mode_measure=problem.network.mode_measure, grid=problem.grid
    )
    number_after = bose_photon_number(
        occupation, mode_measure=problem.network.mode_measure, grid=problem.grid
    )
    expected_number = number_before + problem.n_H_m3 * ledger.com_number_change_per_H
    number_relative = abs(number_after - expected_number) / max(
        abs(number_before), abs(expected_number), 1.0e-300
    )
    free_before = bose_free_energy(
        old,
        mode_measure=problem.network.mode_measure,
        equilibrium_weight=problem.network.equilibrium_weight,
        grid=problem.grid,
    )
    free_after = bose_free_energy(
        occupation,
        mode_measure=problem.network.mode_measure,
        equilibrium_weight=problem.network.equilibrium_weight,
        grid=problem.grid,
    )
    final_action = apply_nonlinear_bose_operator(
        occupation,
        mode_measure=problem.network.mode_measure,
        equilibrium_weight=problem.network.equilibrium_weight,
        pair_moments=problem.network.pair_moments,
        same_cell_rates=problem.network.same_cell_rates,
        grid=problem.grid,
        photon_momentum_scale=problem.network.momentum_scale,
    )
    return CoupledInterfaceStepResult(
        occupation=occupation,
        accumulators=accumulators,
        ledger=ledger,
        converged=converged,
        newton_iterations=completed_iterations,
        total_gmres_iterations=total_gmres,
        dt_s=problem.dt_s,
        residual_relative=final_norm,
        backward_error_relative=final_backward,
        convergence_basis=convergence_basis,
        raw_residual_inf=final_metrics.raw_residual_inf,
        equation_scale=final_metrics.equation_scale,
        minimum_occupation=float(np.min(occupation)),
        explicit_trial_minimum=float(np.min(explicit_trial)),
        number_before_m3=number_before,
        number_after_m3=number_after,
        expected_number_after_m3=expected_number,
        number_relative_residual=float(number_relative),
        free_energy_before=free_before,
        free_energy_after=free_after,
        collision_entropy_production=final_action.entropy_production,
        interface_enabled=True,
    )


__all__ = [
    "FarBoundaryCell",
    "FarBoundaryAdapter",
    "BoundaryTransferAccumulator",
    "CoupledResidualMetrics",
    "CoupledInterfaceProblem",
    "SideTransferLedger",
    "InterfaceTransferLedger",
    "BoundarySpeedAudit",
    "audit_boundary_speed_history",
    "CoupledInterfaceRestartState",
    "CoupledInterfaceStepResult",
    "solve_coupled_interface",
]
