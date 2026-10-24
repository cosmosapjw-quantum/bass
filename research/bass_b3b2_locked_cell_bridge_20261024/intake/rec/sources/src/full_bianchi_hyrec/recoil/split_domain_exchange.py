"""Conservative split-domain exchange primitives for PR-04C.

The original-HyRec transport representation and the 35-state COM--KHW
collision representation remain independent.  This module owns only the two
cross-interface transfers at ``x=+-21.25`` in the local hydrogen tetrad.

Conventions
-----------
* metric signature ``(-,+,+,+)``;
* ordinary frequency in Hz;
* positive packet magnitude follows its declared ``direction``;
* photon number flux has units photons H^-1 s^-1;
* transported photon-energy flux has units W H^-1;
* a pure representation interface has no atomic source term;
* the same packet is evaluated once and applied to the two subdomain ledgers
  with opposite signs.

This bounded v0.55 primitive deliberately does not distribute a packet over
COM--KHW cells.  That deposition belongs to PR-04C1B/C2.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import math
from typing import Iterable

import numpy as np
from scipy.constants import h


_INTERFACE_ABS_X = 21.25
_REL_TOL = 3.0e-14
_ABS_TOL = 1.0e-300


class OperatorOwner(str, Enum):
    """Single owner of one physical operator term."""

    NATIVE_TRANSPORT = "native_transport"
    COM_COLLISION = "com_collision"
    COM_LIOUVILLE = "com_liouville"
    ANALYTIC_BACKGROUND = "analytic_background"
    INTERFACE = "interface"


class InterfaceSide(str, Enum):
    RED = "red"
    BLUE = "blue"


class ExchangeDirection(str, Enum):
    NATIVE_TO_COM = "native_to_com"
    COM_TO_NATIVE = "com_to_native"


@dataclass(frozen=True)
class ProcessOwnership:
    process: str
    owner: OperatorOwner
    support: str

    def __post_init__(self) -> None:
        if not self.process or not self.process.strip():
            raise ValueError("process name must be nonempty")
        if not self.support or not self.support.strip():
            raise ValueError("process support must be nonempty")


@dataclass(frozen=True)
class OwnershipRegistry:
    processes: tuple[ProcessOwnership, ...]
    required_processes: tuple[str, ...]

    def validate(self) -> None:
        names = [item.process for item in self.processes]
        duplicates = sorted({name for name in names if names.count(name) > 1})
        if duplicates:
            raise ValueError(f"duplicate process ownership: {duplicates}")
        required = set(self.required_processes)
        present = set(names)
        missing = sorted(required - present)
        if missing:
            raise ValueError(f"unowned required processes: {missing}")
        extra = sorted(present - required)
        if extra:
            raise ValueError(f"undeclared process ownership: {extra}")
        if any(not isinstance(item.owner, OperatorOwner) for item in self.processes):
            raise ValueError("every process must have exactly one valid owner")

    def owner_of(self, process: str) -> OperatorOwner:
        self.validate()
        matches = [item.owner for item in self.processes if item.process == process]
        if len(matches) != 1:
            raise KeyError(process)
        return matches[0]


def default_ownership_registry() -> OwnershipRegistry:
    """Return the fail-closed PR-04C0 ownership matrix."""

    processes = (
        ProcessOwnership(
            "native_free_streaming",
            OperatorOwner.NATIVE_TRANSPORT,
            "original-HyRec full native frequency support outside interfaces",
        ),
        ProcessOwnership(
            "native_line_escape",
            OperatorOwner.NATIVE_TRANSPORT,
            "original-HyRec native line/virtual-state support",
        ),
        ProcessOwnership(
            "native_real_virtual_algebra",
            OperatorOwner.NATIVE_TRANSPORT,
            "original-HyRec 2 real + 311 virtual states",
        ),
        ProcessOwnership(
            "local_com_khw_collision",
            OperatorOwner.COM_COLLISION,
            "35-state x in [-21.25,21.25]",
        ),
        ProcessOwnership(
            "local_stimulated_bose",
            OperatorOwner.COM_COLLISION,
            "35-state x in [-21.25,21.25]",
        ),
        ProcessOwnership(
            "local_recoil_four_force",
            OperatorOwner.COM_COLLISION,
            "same-event 35-state collision ledger",
        ),
        ProcessOwnership(
            "com_internal_liouville",
            OperatorOwner.COM_LIOUVILLE,
            "inside x in [-21.25,21.25] excluding cross-interface transfer",
        ),
        ProcessOwnership(
            "analytic_blackbody_reference",
            OperatorOwner.ANALYTIC_BACKGROUND,
            "Planck reference field used by original-HyRec distortion variables",
        ),
        ProcessOwnership(
            "cross_interface_red",
            OperatorOwner.INTERFACE,
            "x=-21.25",
        ),
        ProcessOwnership(
            "cross_interface_blue",
            OperatorOwner.INTERFACE,
            "x=+21.25",
        ),
    )
    registry = OwnershipRegistry(
        processes=processes,
        required_processes=tuple(item.process for item in processes),
    )
    registry.validate()
    return registry


def _close(first: float, second: float) -> bool:
    return math.isclose(first, second, rel_tol=_REL_TOL, abs_tol=_ABS_TOL)


@dataclass(frozen=True)
class ExchangePacket:
    """One unresolved positive interface packet.

    ``total = reference + distortion`` is retained explicitly so original
    HyRec's signed nonthermal distortion can be audited without pretending it
    is itself a positive photon population.
    """

    side: InterfaceSide
    direction: ExchangeDirection
    interface_x: float
    interface_frequency_Hz: float
    total_number_flux_per_H_s: float
    reference_number_flux_per_H_s: float
    distortion_number_flux_per_H_s: float
    photon_energy_flux_W_per_H: float
    reference_photon_energy_flux_W_per_H: float
    distortion_photon_energy_flux_W_per_H: float
    atom_energy_flux_W_per_H: float
    source_snapshot_z: float

    def __post_init__(self) -> None:
        finite = {
            name: float(getattr(self, name))
            for name in (
                "interface_x",
                "interface_frequency_Hz",
                "total_number_flux_per_H_s",
                "reference_number_flux_per_H_s",
                "distortion_number_flux_per_H_s",
                "photon_energy_flux_W_per_H",
                "reference_photon_energy_flux_W_per_H",
                "distortion_photon_energy_flux_W_per_H",
                "atom_energy_flux_W_per_H",
                "source_snapshot_z",
            )
        }
        if not all(math.isfinite(value) for value in finite.values()):
            raise ValueError("packet fields must be finite")
        if self.total_number_flux_per_H_s <= 0.0:
            raise ValueError("total packet number flux must be positive")
        if self.reference_number_flux_per_H_s < 0.0:
            raise ValueError("reference packet number flux must be nonnegative")
        if self.interface_frequency_Hz <= 0.0 or self.source_snapshot_z <= 0.0:
            raise ValueError("frequency and source snapshot redshift must be positive")
        if not _close(
            self.total_number_flux_per_H_s,
            self.reference_number_flux_per_H_s
            + self.distortion_number_flux_per_H_s,
        ):
            raise ValueError("number components do not add to total")
        if self.photon_energy_flux_W_per_H <= 0.0:
            raise ValueError("photon energy flux must be positive")
        if self.reference_photon_energy_flux_W_per_H < 0.0:
            raise ValueError("reference photon energy flux must be nonnegative")
        if not _close(
            self.photon_energy_flux_W_per_H,
            self.reference_photon_energy_flux_W_per_H
            + self.distortion_photon_energy_flux_W_per_H,
        ):
            raise ValueError("photon-energy components do not add to total")
        if not _close(self.atom_energy_flux_W_per_H, 0.0):
            raise ValueError("pure representation interface atom energy flux must be zero")
        if not _close(
            self.photon_energy_flux_W_per_H,
            h * self.interface_frequency_Hz * self.total_number_flux_per_H_s,
        ):
            raise ValueError("packet photon energy is inconsistent with frequency")
        if not _close(
            self.reference_photon_energy_flux_W_per_H,
            h * self.interface_frequency_Hz * self.reference_number_flux_per_H_s,
        ):
            raise ValueError("reference photon energy is inconsistent")
        if not _close(
            self.distortion_photon_energy_flux_W_per_H,
            h * self.interface_frequency_Hz * self.distortion_number_flux_per_H_s,
        ):
            raise ValueError("distortion photon energy is inconsistent")

        expected_x = _INTERFACE_ABS_X if self.side is InterfaceSide.BLUE else -_INTERFACE_ABS_X
        if not _close(self.interface_x, expected_x):
            raise ValueError("interface x is inconsistent with declared side")
        expected_direction = (
            ExchangeDirection.NATIVE_TO_COM
            if self.side is InterfaceSide.BLUE
            else ExchangeDirection.COM_TO_NATIVE
        )
        if self.direction is not expected_direction:
            raise ValueError("direction is inconsistent with FLRW interface side")

    @property
    def frequency_centroid_Hz(self) -> float:
        return self.photon_energy_flux_W_per_H / (
            h * self.total_number_flux_per_H_s
        )

    def to_dict(self) -> dict[str, float | str]:
        return {
            "side": self.side.value,
            "direction": self.direction.value,
            "interface_x": self.interface_x,
            "interface_frequency_Hz": self.interface_frequency_Hz,
            "total_number_flux_per_H_s": self.total_number_flux_per_H_s,
            "reference_number_flux_per_H_s": self.reference_number_flux_per_H_s,
            "distortion_number_flux_per_H_s": self.distortion_number_flux_per_H_s,
            "photon_energy_flux_W_per_H": self.photon_energy_flux_W_per_H,
            "reference_photon_energy_flux_W_per_H": self.reference_photon_energy_flux_W_per_H,
            "distortion_photon_energy_flux_W_per_H": self.distortion_photon_energy_flux_W_per_H,
            "atom_energy_flux_W_per_H": self.atom_energy_flux_W_per_H,
            "source_snapshot_z": self.source_snapshot_z,
        }

    @classmethod
    def from_dict(cls, values: dict[str, float | str]) -> "ExchangePacket":
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


def packet_from_original_hyrec_boundary_sample(
    sample: object,
    *,
    source_snapshot_z: float,
) -> "ExchangePacket":
    """Convert one source-identical original-HyRec interface sample.

    The conversion preserves the positive total photon packet and its
    reference/distortion decomposition exactly.  Crossing a computational
    representation interface is not a new atomic event, so its atomic source
    term is identically zero.  Atomic recoil remains owned by the local
    collision operators in the ownership registry.
    """

    from .original_hyrec_physical_flux import OriginalHyRecBoundarySample

    if not isinstance(sample, OriginalHyRecBoundarySample):
        raise TypeError("sample must be an OriginalHyRecBoundarySample")
    side = InterfaceSide(sample.side)
    direction = (
        ExchangeDirection.NATIVE_TO_COM
        if side is InterfaceSide.BLUE
        else ExchangeDirection.COM_TO_NATIVE
    )
    return ExchangePacket(
        side=side,
        direction=direction,
        interface_x=sample.interface_x,
        interface_frequency_Hz=sample.interface_frequency_Hz,
        total_number_flux_per_H_s=sample.total_number_flux_per_H_s,
        reference_number_flux_per_H_s=sample.reference_number_flux_per_H_s,
        distortion_number_flux_per_H_s=sample.distortion_number_flux_per_H_s,
        photon_energy_flux_W_per_H=sample.total_photon_energy_flux_W_per_H,
        reference_photon_energy_flux_W_per_H=sample.reference_photon_energy_flux_W_per_H,
        distortion_photon_energy_flux_W_per_H=sample.distortion_photon_energy_flux_W_per_H,
        atom_energy_flux_W_per_H=0.0,
        source_snapshot_z=source_snapshot_z,
    )


@dataclass(frozen=True)
class ExchangeLedger:
    evaluation_count: int
    native_application_count: int
    com_application_count: int
    native_number_flux_per_H_s: float
    com_number_flux_per_H_s: float
    native_photon_energy_flux_W_per_H: float
    com_photon_energy_flux_W_per_H: float
    photon_energy_flux_W_per_H: float
    atom_energy_flux_W_per_H: float

    @property
    def number_residual_per_H_s(self) -> float:
        return self.native_number_flux_per_H_s + self.com_number_flux_per_H_s

    @property
    def photon_energy_residual_W_per_H(self) -> float:
        return (
            self.native_photon_energy_flux_W_per_H
            + self.com_photon_energy_flux_W_per_H
        )

    @property
    def total_energy_residual_W_per_H(self) -> float:
        return (
            self.native_photon_energy_flux_W_per_H
            + self.com_photon_energy_flux_W_per_H
            + self.atom_energy_flux_W_per_H
        )

    @property
    def energy_residual_W_per_H(self) -> float:
        """Total split-domain energy residual including any atomic source."""
        return self.total_energy_residual_W_per_H

    def validate(self, *, enabled: bool) -> None:
        expected = (1, 1, 1) if enabled else (0, 0, 0)
        actual = (
            self.evaluation_count,
            self.native_application_count,
            self.com_application_count,
        )
        if actual != expected:
            raise ValueError(f"invalid interface evaluation/application counts: {actual}")
        if self.number_residual_per_H_s != 0.0:
            raise ValueError("interface number ledger does not cancel exactly")
        if self.photon_energy_residual_W_per_H != 0.0:
            raise ValueError("interface photon-energy ledger does not cancel exactly")
        if self.total_energy_residual_W_per_H != 0.0:
            raise ValueError("split-domain total energy ledger does not cancel")


@dataclass(frozen=True)
class SplitDomainExchangeResult:
    native_state: np.ndarray
    com_state: np.ndarray
    ledger: ExchangeLedger


class SplitDomainExchangeOperator:
    """PR-04C0/C1A single-owner packet ledger.

    The state arrays are intentionally unchanged in this bounded stage.  Their
    actual implicit packet deposition/removal is PR-04C1B/C2.  Returning copies
    prevents an accidental alias from being mistaken for a completed update.
    """

    def __init__(self, *, enabled: bool = True) -> None:
        self.enabled = bool(enabled)
        self.ownership = default_ownership_registry()

    def evaluate_packet(self, packet: ExchangePacket, *, bianchi_type: str) -> ExchangePacket:
        if not isinstance(packet, ExchangePacket):
            raise TypeError("packet must be an ExchangePacket")
        if not isinstance(bianchi_type, str) or not bianchi_type:
            raise ValueError("bianchi_type must be a nonempty audit label")
        # Local hydrogen-frame microphysics and the scalar interface packet do
        # not depend on the Bianchi label at fixed local state.
        return packet

    def apply(
        self,
        packet: ExchangePacket,
        *,
        native_state: Iterable[float],
        com_state: Iterable[float],
        dt_s: float,
    ) -> SplitDomainExchangeResult:
        if not math.isfinite(dt_s) or dt_s <= 0.0:
            raise ValueError("dt_s must be positive and finite")
        native = np.array(native_state, dtype=float, copy=True)
        com = np.array(com_state, dtype=float, copy=True)
        if not np.all(np.isfinite(native)) or not np.all(np.isfinite(com)):
            raise ValueError("states must be finite")

        if not self.enabled:
            ledger = ExchangeLedger(
                evaluation_count=0,
                native_application_count=0,
                com_application_count=0,
                native_number_flux_per_H_s=0.0,
                com_number_flux_per_H_s=0.0,
                native_photon_energy_flux_W_per_H=0.0,
                com_photon_energy_flux_W_per_H=0.0,
                photon_energy_flux_W_per_H=0.0,
                atom_energy_flux_W_per_H=0.0,
            )
            ledger.validate(enabled=False)
            return SplitDomainExchangeResult(native, com, ledger)

        sign_native = -1.0 if packet.direction is ExchangeDirection.NATIVE_TO_COM else 1.0
        sign_com = -sign_native
        ledger = ExchangeLedger(
            evaluation_count=1,
            native_application_count=1,
            com_application_count=1,
            native_number_flux_per_H_s=sign_native
            * packet.total_number_flux_per_H_s,
            com_number_flux_per_H_s=sign_com * packet.total_number_flux_per_H_s,
            native_photon_energy_flux_W_per_H=sign_native
            * packet.photon_energy_flux_W_per_H,
            com_photon_energy_flux_W_per_H=sign_com
            * packet.photon_energy_flux_W_per_H,
            photon_energy_flux_W_per_H=packet.photon_energy_flux_W_per_H,
            atom_energy_flux_W_per_H=packet.atom_energy_flux_W_per_H,
        )
        ledger.validate(enabled=True)
        return SplitDomainExchangeResult(native, com, ledger)


__all__ = [
    "OperatorOwner",
    "InterfaceSide",
    "ExchangeDirection",
    "ProcessOwnership",
    "OwnershipRegistry",
    "default_ownership_registry",
    "ExchangePacket",
    "packet_from_original_hyrec_boundary_sample",
    "ExchangeLedger",
    "SplitDomainExchangeResult",
    "SplitDomainExchangeOperator",
]
