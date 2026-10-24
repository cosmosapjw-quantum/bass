"""Fail-closed ownership audit for a dynamic atomic/native/COM macro.

The v0.74 COM root is a valid collision--transport subproblem, but it cannot be
combined naively with the complete original-HyRec real/virtual algebra.  The
canonical native block contains Ly-alpha diffusion and real--virtual source
couplings on frequencies that lie inside the 35-state COM domain.  Activating
both representations on the same support would count the same physical
processes twice.

This module does not implement the missing split-domain Schur/replacement
operator.  It identifies the exact z~1100 point-spike support overlap and blocks
production construction until the interior/exterior/source/interface owners
are explicit in one residual, JVP, conservation ledger, and restart state.

Conventions
-----------
* metric signature ``(-,+,+,+)`` is inherited from the surrounding project;
* ordinary photon frequency is used, while the canonical virtual registry is
  expressed in eV;
* the COM interface is ``x=+-21.25`` in hydrogen-frame Doppler coordinates;
* original-HyRec virtual states are zero-width point spikes, not inferred
  finite-volume cells;
* no fitted normalization or centre-derived native cell width is introduced.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Literal

import numpy as np

from full_bianchi_hyrec.recoil.original_hyrec_native import NVIRT
from full_bianchi_hyrec.recoil.original_hyrec_physical_flux import (
    OriginalHyRecTrajectorySnapshot,
)
from full_bianchi_hyrec.trajectory.primitive_rates import LYMAN_ALPHA_ENERGY_EV


NativeSupport = Literal["full", "exterior_only", "disabled"]
ComSupport = Literal["interior", "disabled"]
CompletedTvvSupport = Literal["full", "exterior_schur", "disabled"]
CrossEdgeOwner = Literal["split_domain_interface", "original_hyrec_native", "com_khw", "unowned"]
ScalarHistoryOwner = Literal["typed_characteristic_history", "canonical_callback", "both", "unowned"]


class DynamicMacroOwnershipError(RuntimeError):
    """Raised when a full dynamic macro would duplicate or omit an operator."""


@dataclass(frozen=True)
class DynamicMacroOwnershipConfig:
    """Declared support/owner configuration for one dynamic macro.

    ``contract_witness_only`` marks the mathematically admissible target
    configuration.  It is not evidence that the exterior Schur replacement has
    already been implemented.
    """

    native_diffusion_support: NativeSupport
    com_collision_support: ComSupport
    native_atomic_source_support: NativeSupport
    com_atomic_source_support: ComSupport
    completed_tvv_support: CompletedTvvSupport
    cross_edge_owner: CrossEdgeOwner
    scalar_history_owner: ScalarHistoryOwner
    replacement_complete: bool
    contract_witness_only: bool = False

    def __post_init__(self) -> None:
        allowed_native = {"full", "exterior_only", "disabled"}
        allowed_com = {"interior", "disabled"}
        allowed_tvv = {"full", "exterior_schur", "disabled"}
        allowed_cross = {
            "split_domain_interface",
            "original_hyrec_native",
            "com_khw",
            "unowned",
        }
        allowed_history = {
            "typed_characteristic_history",
            "canonical_callback",
            "both",
            "unowned",
        }
        if self.native_diffusion_support not in allowed_native:
            raise ValueError("invalid native diffusion support")
        if self.native_atomic_source_support not in allowed_native:
            raise ValueError("invalid native atomic-source support")
        if self.com_collision_support not in allowed_com:
            raise ValueError("invalid COM collision support")
        if self.com_atomic_source_support not in allowed_com:
            raise ValueError("invalid COM atomic-source support")
        if self.completed_tvv_support not in allowed_tvv:
            raise ValueError("invalid completed-Tvv support")
        if self.cross_edge_owner not in allowed_cross:
            raise ValueError("invalid cross-edge owner")
        if self.scalar_history_owner not in allowed_history:
            raise ValueError("invalid scalar-history owner")
        if self.contract_witness_only and not self.replacement_complete:
            raise ValueError("a contract witness requires replacement_complete")


def current_v074_ownership_config() -> DynamicMacroOwnershipConfig:
    """Configuration inherited by the source-conditioned v0.74 COM subproblem."""

    return DynamicMacroOwnershipConfig(
        native_diffusion_support="full",
        com_collision_support="interior",
        native_atomic_source_support="full",
        com_atomic_source_support="disabled",
        completed_tvv_support="full",
        cross_edge_owner="split_domain_interface",
        scalar_history_owner="typed_characteristic_history",
        replacement_complete=False,
    )


def naive_dynamic_atomic_ownership_config() -> DynamicMacroOwnershipConfig:
    """The forbidden configuration obtained by simply adding COM atomic source."""

    return DynamicMacroOwnershipConfig(
        native_diffusion_support="full",
        com_collision_support="interior",
        native_atomic_source_support="full",
        com_atomic_source_support="interior",
        completed_tvv_support="full",
        cross_edge_owner="split_domain_interface",
        scalar_history_owner="typed_characteristic_history",
        replacement_complete=False,
    )


def resolved_split_domain_contract_witness() -> DynamicMacroOwnershipConfig:
    """Admissible target ownership contract, not an implementation claim."""

    return DynamicMacroOwnershipConfig(
        native_diffusion_support="exterior_only",
        com_collision_support="interior",
        native_atomic_source_support="exterior_only",
        com_atomic_source_support="interior",
        completed_tvv_support="exterior_schur",
        cross_edge_owner="split_domain_interface",
        scalar_history_owner="typed_characteristic_history",
        replacement_complete=True,
        contract_witness_only=True,
    )


@dataclass(frozen=True)
class DynamicAtomicMacroOwnershipAudit:
    native_virtual_count: int
    interface_abs_x: float
    com_interior_native_count: int
    com_interior_native_indices: tuple[int, ...]
    minimum_interior_x: float
    maximum_interior_x: float
    left_exterior_x: float
    right_exterior_x: float
    diffusion_inside_edge_count: int
    diffusion_cross_edge_count: int
    diffusion_outside_edge_count: int
    diffusion_cross_edges: tuple[tuple[int, int], ...]
    diffusion_cross_rate_s_inv: float
    canonical_up_rate_interior_fraction: float
    canonical_down_rate_interior_fraction: float
    real_to_virtual_abs_interior_fraction: float
    virtual_to_real_abs_interior_fraction: float
    overlap_count: int
    unowned_process_count: int
    unresolved_processes: tuple[str, ...]
    cross_edge_owner: str
    scalar_history_owner: str
    replacement_complete: bool
    contract_witness_only: bool
    dynamic_atomic_macro_ready: bool

    def __post_init__(self) -> None:
        if self.native_virtual_count != NVIRT:
            raise ValueError("native virtual count differs from the canonical registry")
        if self.com_interior_native_count != len(self.com_interior_native_indices):
            raise ValueError("interior count/index mismatch")
        if self.diffusion_cross_edge_count != len(self.diffusion_cross_edges):
            raise ValueError("cross-edge count mismatch")
        for name in (
            "interface_abs_x",
            "minimum_interior_x",
            "maximum_interior_x",
            "left_exterior_x",
            "right_exterior_x",
            "diffusion_cross_rate_s_inv",
            "canonical_up_rate_interior_fraction",
            "canonical_down_rate_interior_fraction",
            "real_to_virtual_abs_interior_fraction",
            "virtual_to_real_abs_interior_fraction",
        ):
            value = float(getattr(self, name))
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite")
            object.__setattr__(self, name, value)
        for name in (
            "canonical_up_rate_interior_fraction",
            "canonical_down_rate_interior_fraction",
            "real_to_virtual_abs_interior_fraction",
            "virtual_to_real_abs_interior_fraction",
        ):
            value = float(getattr(self, name))
            if not 0.0 <= value <= 1.0 + 1.0e-14:
                raise ValueError(f"{name} must be a fraction")
        if self.overlap_count < 0 or self.unowned_process_count < 0:
            raise ValueError("ownership counts must be nonnegative")


def _fraction_inside(values: np.ndarray, inside: np.ndarray) -> float:
    array = np.abs(np.asarray(values, dtype=float))
    total = float(np.sum(array))
    if total == 0.0:
        return 0.0
    if array.ndim == 1:
        part = float(np.sum(array[inside]))
    elif array.ndim == 2:
        part = float(np.sum(array[:, inside]))
    else:
        raise ValueError("rate array must be one- or two-dimensional")
    return part / total


def audit_dynamic_atomic_macro_ownership(
    snapshot: OriginalHyRecTrajectorySnapshot,
    *,
    doppler_width_eV: float,
    config: DynamicMacroOwnershipConfig,
    interface_abs_x: float = 21.25,
    zero_tolerance_s_inv: float = 0.0,
) -> DynamicAtomicMacroOwnershipAudit:
    """Audit exact point-spike overlap at one source-conditioned snapshot."""

    width = float(doppler_width_eV)
    boundary = float(interface_abs_x)
    tolerance = float(zero_tolerance_s_inv)
    if not math.isfinite(width) or width <= 0.0:
        raise ValueError("doppler_width_eV must be positive and finite")
    if not math.isfinite(boundary) or boundary <= 0.0:
        raise ValueError("interface_abs_x must be positive and finite")
    if not math.isfinite(tolerance) or tolerance < 0.0:
        raise ValueError("zero_tolerance_s_inv must be finite and nonnegative")

    energy = np.asarray(snapshot.energy_eV, dtype=float)
    if energy.shape != (NVIRT,) or not np.all(np.isfinite(energy)):
        raise ValueError("invalid canonical virtual-energy registry")
    x = (energy - LYMAN_ALPHA_ENERGY_EV) / width
    inside = np.abs(x) <= boundary
    indices = tuple(int(i) for i in np.flatnonzero(inside))
    if not indices:
        raise DynamicMacroOwnershipError("COM domain contains no canonical native point spike")
    left = int(indices[0])
    right = int(indices[-1])
    if left == 0 or right == NVIRT - 1:
        raise DynamicMacroOwnershipError("COM support touches the edge of the native registry")

    inside_edges = 0
    outside_edges = 0
    cross_edges: list[tuple[int, int]] = []
    cross_rate = 0.0
    for index in range(NVIRT - 1):
        forward = abs(float(snapshot.Tvv[2, index]))
        reverse = abs(float(snapshot.Tvv[1, index + 1]))
        rate = max(forward, reverse)
        if rate <= tolerance:
            continue
        left_inside = bool(inside[index])
        right_inside = bool(inside[index + 1])
        if left_inside and right_inside:
            inside_edges += 1
        elif left_inside != right_inside:
            cross_edges.append((index, index + 1))
            cross_rate += forward + reverse
        else:
            outside_edges += 1

    overlaps: list[str] = []
    unowned: list[str] = []
    unresolved: list[str] = []

    if (
        config.native_diffusion_support == "full"
        and config.com_collision_support == "interior"
        and indices
    ):
        overlaps.append("native_A1s_diffusion_inside")
    if (
        config.native_atomic_source_support == "full"
        and config.com_atomic_source_support == "interior"
        and indices
    ):
        overlaps.append("atomic_real_virtual_source_inside")
    if config.completed_tvv_support == "full" and (
        config.com_collision_support == "interior"
        or config.com_atomic_source_support == "interior"
    ):
        overlaps.append("completed_Tvv_inside")

    split_requested = (
        config.native_diffusion_support == "exterior_only"
        or config.native_atomic_source_support == "exterior_only"
        or config.completed_tvv_support == "exterior_schur"
    )
    if split_requested and config.cross_edge_owner != "split_domain_interface":
        unowned.append("native_COM_cross_edges")
    if config.cross_edge_owner == "unowned":
        unowned.append("native_COM_cross_edges")
    if config.scalar_history_owner == "unowned":
        unowned.append("scalar_Dfplus_history")
    elif config.scalar_history_owner == "both":
        overlaps.append("scalar_Dfplus_history")
    elif config.scalar_history_owner != "typed_characteristic_history":
        unresolved.append("typed_history_owner_not_promoted")

    if not config.replacement_complete:
        unresolved.append("split_domain_residual_JVP_ledger_restart_incomplete")
    if config.completed_tvv_support == "disabled":
        unowned.append("native_exterior_real_virtual_algebra")
    if config.native_diffusion_support == "disabled" and config.com_collision_support == "disabled":
        unowned.append("elastic_frequency_redistribution")
    if config.native_atomic_source_support == "disabled" and config.com_atomic_source_support == "disabled":
        unowned.append("atomic_real_virtual_source")

    unresolved_all = tuple(dict.fromkeys(overlaps + unowned + unresolved))
    ready = bool(
        not overlaps
        and not unowned
        and not unresolved
        and config.replacement_complete
        and config.scalar_history_owner == "typed_characteristic_history"
        and config.cross_edge_owner == "split_domain_interface"
    )

    return DynamicAtomicMacroOwnershipAudit(
        native_virtual_count=NVIRT,
        interface_abs_x=boundary,
        com_interior_native_count=len(indices),
        com_interior_native_indices=indices,
        minimum_interior_x=float(np.min(x[inside])),
        maximum_interior_x=float(np.max(x[inside])),
        left_exterior_x=float(x[left - 1]),
        right_exterior_x=float(x[right + 1]),
        diffusion_inside_edge_count=inside_edges,
        diffusion_cross_edge_count=len(cross_edges),
        diffusion_outside_edge_count=outside_edges,
        diffusion_cross_edges=tuple(cross_edges),
        diffusion_cross_rate_s_inv=float(cross_rate),
        canonical_up_rate_interior_fraction=_fraction_inside(snapshot.Aup_s_inv, inside),
        canonical_down_rate_interior_fraction=_fraction_inside(snapshot.Adn_s_inv, inside),
        real_to_virtual_abs_interior_fraction=_fraction_inside(snapshot.Tvr, inside),
        virtual_to_real_abs_interior_fraction=_fraction_inside(snapshot.Trv, inside),
        overlap_count=len(overlaps),
        unowned_process_count=len(unowned),
        unresolved_processes=unresolved_all,
        cross_edge_owner=config.cross_edge_owner,
        scalar_history_owner=config.scalar_history_owner,
        replacement_complete=bool(config.replacement_complete),
        contract_witness_only=bool(config.contract_witness_only),
        dynamic_atomic_macro_ready=ready,
    )


def require_dynamic_atomic_macro_ready(
    audit: DynamicAtomicMacroOwnershipAudit,
) -> None:
    """Fail closed before constructing a full atomic/native/COM macro."""

    if audit.contract_witness_only:
        raise DynamicMacroOwnershipError(
            "dynamic atomic/native/COM macro is not admissible: "
            "contract witness is not implementation evidence"
        )
    if not audit.dynamic_atomic_macro_ready:
        details = ", ".join(audit.unresolved_processes) or "unknown ownership defect"
        raise DynamicMacroOwnershipError(
            "dynamic atomic/native/COM macro is not admissible: " + details
        )


__all__ = [
    "DynamicMacroOwnershipConfig",
    "DynamicAtomicMacroOwnershipAudit",
    "DynamicMacroOwnershipError",
    "audit_dynamic_atomic_macro_ownership",
    "current_v074_ownership_config",
    "naive_dynamic_atomic_ownership_config",
    "resolved_split_domain_contract_witness",
    "require_dynamic_atomic_macro_ready",
]
