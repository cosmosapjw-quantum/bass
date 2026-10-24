"""Source-derived scalar-history bootstrap parent for PR-05C continuation.

This module does **not** reconstruct missing anisotropic original-HyRec data and
it does not claim a coupled Bianchi--HyRec macro endpoint.  It evaluates the
accepted scalar original-HyRec radiation history at arbitrary COM frequency
points using the source's own free-streaming characteristic rule, then applies
the explicit v0.65 hydrogen-frame isotropic-initial-data axiom.  The resulting
positive angle-frequency state is a provenance-locked bootstrap parent for the
*next* coupled macro interval.

Conventions
-----------
* metric signature ``(-,+,+,+)``;
* ordinary frequency in Hz;
* ``eta = ln(a)`` for the accepted original-HyRec history;
* source tabulated energies are rescaled by ``fsR**2 * meR``;
* no native-cell edges or native-to-COM conservative remap are inferred;
* every query selects the least native source energy strictly above the target,
  exactly as the guarded October-2012 original-HyRec interface diagnostic.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import struct
from typing import Mapping

import numpy as np

from full_bianchi_hyrec.background.sequence import BackgroundSnapshotSequence
from full_bianchi_hyrec.recoil.nonlinear_bose_release import HarmonicGrid
from full_bianchi_hyrec.recoil.nonlinear_bose_runtime import LineBoundaryConfig
from full_bianchi_hyrec.recoil.original_hyrec_native import H_PLANCK_EV_S
from full_bianchi_hyrec.recoil.original_hyrec_physical_flux import (
    OriginalHyRecTrajectorySnapshot,
)
from full_bianchi_hyrec.trajectory.accepted_parent import (
    AcceptedRadiationParent,
    ParentEvidenceClass,
    ProductionParentRequirements,
)
from full_bianchi_hyrec.trajectory.causal_history import (
    AcceptedRadiationHistory,
    CharacteristicInterpolationStencil,
)
from full_bianchi_hyrec.trajectory.direct_thermodynamic import DirectThermodynamicNode
from full_bianchi_hyrec.trajectory.primitive_trajectory import (
    AtomicRadiationState,
    atomic_state_from_source_snapshot,
)


def _is_sha256(value: str) -> bool:
    text = str(value).lower()
    return len(text) == 64 and all(character in "0123456789abcdef" for character in text)


def _canonical_json(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _hash_record(header: Mapping[str, object], arrays: Mapping[str, np.ndarray]) -> str:
    digest = hashlib.sha256()
    encoded = _canonical_json(dict(header))
    digest.update(struct.pack("<Q", len(encoded)))
    digest.update(encoded)
    for name in sorted(arrays):
        array = np.asarray(arrays[name])
        if not np.all(np.isfinite(array)):
            raise ValueError(f"{name} contains nonfinite values")
        canonical = np.ascontiguousarray(array, dtype="<f8")
        label = name.encode("ascii")
        digest.update(struct.pack("<Q", len(label)))
        digest.update(label)
        digest.update(struct.pack("<Q", canonical.ndim))
        digest.update(np.asarray(canonical.shape, dtype="<i8").tobytes())
        digest.update(canonical.tobytes(order="C"))
    return digest.hexdigest()


@dataclass(frozen=True)
class PointCharacteristicSample:
    target_frequency_Hz: float
    target_energy_eV_rescaled: float
    source_index: int
    source_energy_eV_rescaled: float
    eta_target: float
    eta_query: float
    left_index: int | None
    right_index: int | None
    fraction: float
    distortion_occupation: float
    blackbody_occupation: float
    total_occupation: float
    thermal_zero: bool

    def __post_init__(self) -> None:
        for name in (
            "target_frequency_Hz",
            "target_energy_eV_rescaled",
            "source_energy_eV_rescaled",
            "eta_target",
            "eta_query",
            "fraction",
            "distortion_occupation",
            "blackbody_occupation",
            "total_occupation",
        ):
            value = float(getattr(self, name))
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite")
            object.__setattr__(self, name, value)
        if self.target_frequency_Hz <= 0.0 or self.target_energy_eV_rescaled <= 0.0:
            raise ValueError("target frequency/energy must be positive")
        if self.source_index < 0 or self.source_energy_eV_rescaled <= self.target_energy_eV_rescaled:
            raise ValueError("point characteristic requires a strictly higher native source")
        if self.total_occupation <= 0.0 or self.blackbody_occupation < 0.0:
            raise ValueError("physical point occupation must be positive")
        if not 0.0 <= self.fraction < 1.0:
            raise ValueError("interpolation fraction must lie in [0,1)")
        if self.thermal_zero:
            if self.left_index is not None or self.right_index is not None:
                raise ValueError("thermal-zero point cannot own history endpoints")
        else:
            if self.left_index is None or self.right_index != self.left_index + 1:
                raise ValueError("nonthermal point requires adjacent history endpoints")

    def record(self) -> dict[str, object]:
        return {
            "target_frequency_Hz": self.target_frequency_Hz,
            "target_energy_eV_rescaled": self.target_energy_eV_rescaled,
            "source_index": self.source_index,
            "source_energy_eV_rescaled": self.source_energy_eV_rescaled,
            "eta_target": self.eta_target,
            "eta_query": self.eta_query,
            "left_index": self.left_index,
            "right_index": self.right_index,
            "fraction": self.fraction,
            "distortion_occupation": self.distortion_occupation,
            "blackbody_occupation": self.blackbody_occupation,
            "total_occupation": self.total_occupation,
            "thermal_zero": self.thermal_zero,
        }


@dataclass(frozen=True)
class OriginalHyRecPointCharacteristicEvaluator:
    """Evaluate accepted scalar history at a target ordinary frequency."""

    history: AcceptedRadiationHistory
    fsR: float
    meR: float

    def __post_init__(self) -> None:
        fs = float(self.fsR)
        me = float(self.meR)
        if not (math.isfinite(fs) and fs > 0.0 and math.isfinite(me) and me > 0.0):
            raise ValueError("fsR and meR must be positive and finite")
        object.__setattr__(self, "fsR", fs)
        object.__setattr__(self, "meR", me)

    @property
    def energy_rescale(self) -> float:
        return self.fsR**2 * self.meR

    def evaluate(
        self,
        *,
        eta_target: float,
        target_frequency_Hz: float,
        radiation_temperature_eV_rescaled: float,
    ) -> PointCharacteristicSample:
        eta = float(eta_target)
        frequency = float(target_frequency_Hz)
        temperature = float(radiation_temperature_eV_rescaled)
        if not math.isfinite(eta):
            raise ValueError("eta_target must be finite")
        if not (math.isfinite(frequency) and frequency > 0.0):
            raise ValueError("target_frequency_Hz must be positive and finite")
        if not (math.isfinite(temperature) and temperature > 0.0):
            raise ValueError("radiation temperature must be positive and finite")

        target_energy = frequency * H_PLANCK_EV_S / self.energy_rescale
        source_candidates = np.flatnonzero(self.history.grid.energy_eV > target_energy)
        if source_candidates.size == 0:
            raise ValueError("no canonical native source lies above the target frequency")
        source_index = int(source_candidates[0])
        source_energy = float(self.history.grid.energy_eV[source_index])
        redshift_plus_one = math.exp(-eta)
        eta_query = -math.log(redshift_plus_one * source_energy / target_energy)
        stencil = self.history.grid.locate(
            eta_query, accepted_count=self.history.accepted_count
        )
        distortion = stencil.evaluate(self.history.outgoing_virtual[source_index])
        blackbody = 1.0 / math.expm1(target_energy / temperature)
        total = blackbody + distortion
        if not math.isfinite(total) or total <= 0.0:
            raise FloatingPointError("point-characteristic total occupation is not positive")
        return PointCharacteristicSample(
            target_frequency_Hz=frequency,
            target_energy_eV_rescaled=target_energy,
            source_index=source_index,
            source_energy_eV_rescaled=source_energy,
            eta_target=eta,
            eta_query=eta_query,
            left_index=stencil.left_index,
            right_index=stencil.right_index,
            fraction=stencil.fraction,
            distortion_occupation=distortion,
            blackbody_occupation=blackbody,
            total_occupation=total,
            thermal_zero=stencil.thermal_zero,
        )


@dataclass(frozen=True)
class SourceDerivedBootstrapParentResult:
    parent: AcceptedRadiationParent
    requirements: ProductionParentRequirements
    atomic_state: AtomicRadiationState
    samples: tuple[PointCharacteristicSample, ...]
    interface_samples: tuple[PointCharacteristicSample, PointCharacteristicSample]
    activity: np.ndarray
    atomic_state_sha256: str
    background_sequence_sha256: str
    interface_sha256: str
    coupled_macro_endpoint: bool = False

    def __post_init__(self) -> None:
        activity = np.asarray(self.activity, dtype=float)
        if activity.ndim != 1 or not np.all(np.isfinite(activity)) or np.any(activity <= 0.0):
            raise ValueError("activity must be a positive finite vector")
        activity = np.array(activity, copy=True)
        activity.setflags(write=False)
        object.__setattr__(self, "activity", activity)
        if self.coupled_macro_endpoint:
            raise ValueError("bootstrap parent cannot be labelled a coupled macro endpoint")


def hash_background_sequence(sequence: BackgroundSnapshotSequence) -> str:
    return _hash_record(
        {
            "schema": "PR05C_BACKGROUND_SEQUENCE_DIGEST_V1",
            "model_name": sequence.model_name,
            "chart_id": sequence.chart_id,
            "bianchi_type": sequence.bianchi_type,
            "source_path": sequence.source_path,
            "source_sha256": sequence.source_sha256,
            "provenance": dict(sequence.provenance),
            "provider_branch_flags": dict(sequence.provider_branch_flags),
            "constraint_names": sorted(sequence.constraint_residual_series),
        },
        {
            "tau": sequence.tau,
            "cosmic_time_s": sequence.cosmic_time_s,
            "H_s_inv": sequence.H_s_inv,
            "q": sequence.q,
            "sigma_s_inv": sequence.sigma_s_inv,
            "N_s_inv": sequence.N_s_inv,
            "A_s_inv": sequence.A_s_inv,
            "frame_rotation_s_inv": sequence.frame_rotation_s_inv,
            "beta_H": sequence.beta_H,
            "D0_beta_H_s_inv": sequence.D0_beta_H_s_inv,
            **{
                f"constraint:{name}": value
                for name, value in sequence.constraint_residual_series.items()
            },
        },
    )


def hash_atomic_state(
    state: AtomicRadiationState, *, source_snapshot_sha256: str
) -> str:
    source_hash = str(source_snapshot_sha256).lower()
    if not _is_sha256(source_hash):
        raise ValueError("source_snapshot_sha256 must be a SHA-256 digest")
    return _hash_record(
        {
            "schema": "PR05C_ATOMIC_RADIATION_STATE_DIGEST_V1",
            "source_snapshot_sha256": source_hash,
            "x_1s": state.x_1s,
            "x_2s": state.x_2s,
            "x_2p": state.x_2p,
            "x_e": state.x_e,
            "x_HII": state.x_HII,
            "T_m_K": state.T_m_K,
            "classification": state.classification.value,
            "interface_accumulators": dict(state.interface_accumulators),
        },
        {
            "real_departure": state.real_departure,
            "native_departure": state.native_departure,
            "com_occupation": state.com_occupation,
            "beta_H": state.beta_H,
        },
    )


def _interface_digest(samples: tuple[PointCharacteristicSample, ...]) -> str:
    payload = {
        "schema": "PR05C_POINT_CHARACTERISTIC_INTERFACE_V1",
        "samples": [sample.record() for sample in samples],
    }
    return hashlib.sha256(_canonical_json(payload)).hexdigest()


def build_source_derived_bootstrap_parent(
    *,
    history: AcceptedRadiationHistory,
    source_snapshot: OriginalHyRecTrajectorySnapshot,
    source_snapshot_sha256: str,
    network_node: DirectThermodynamicNode,
    angular_grid: HarmonicGrid,
    background_sequence: BackgroundSnapshotSequence,
    background_tau: float,
    branch_id: str,
) -> SourceDerivedBootstrapParentResult:
    """Build the accepted scalar-history bootstrap state for the next macro.

    The last history entry must correspond to ``source_snapshot.iz_local`` and
    to the source snapshot redshift.  The radiation field is evaluated at the
    COM cell centres by the source's point-characteristic rule and lifted
    isotropically in the hydrogen frame.  This is an accepted initial-data
    state under the explicit scalar/unpolarized isotropy axiom, not an accepted
    coupled macro endpoint.
    """

    if history.accepted_count != source_snapshot.iz_local + 1:
        raise ValueError("history must end at the accepted source snapshot index")
    eta_target = float(history.grid.eta[-1])
    expected_eta = -math.log1p(source_snapshot.z)
    if abs(eta_target - expected_eta) > 64.0 * np.finfo(float).eps * max(1.0, abs(expected_eta)):
        raise ValueError("history endpoint and source snapshot redshift disagree")
    source_hash = str(source_snapshot_sha256).lower()
    if not _is_sha256(source_hash):
        raise ValueError("source_snapshot_sha256 must be a SHA-256 digest")
    if background_sequence.bianchi_type != "II":
        raise ValueError("current bootstrap parent is restricted to Bianchi II")
    background = background_sequence.snapshot_at_tau(float(background_tau))
    if background.bianchi_type != "II" or not background.branch_flags.get(
        "provider_validated_bianchi_ii", False
    ):
        raise ValueError("background is not the validated Bianchi-II provider branch")

    line = LineBoundaryConfig.lyman_alpha(
        temperature_K=network_node.temperature_K,
        x_red=-21.25,
        x_blue=21.25,
    )
    evaluator = OriginalHyRecPointCharacteristicEvaluator(
        history=history, fsR=source_snapshot.fsR, meR=source_snapshot.meR
    )
    centre_frequencies = (
        line.nu_abs_Hz + network_node.network.centers * line.Doppler_width_Hz
    )
    samples = tuple(
        evaluator.evaluate(
            eta_target=eta_target,
            target_frequency_Hz=float(frequency),
            radiation_temperature_eV_rescaled=source_snapshot.TR_eV_rescaled,
        )
        for frequency in centre_frequencies
    )
    scalar_occupation = np.asarray(
        [sample.total_occupation for sample in samples], dtype=float
    )
    occupation = np.repeat(scalar_occupation[:, None], angular_grid.n_angle, axis=1)
    atomic_state = atomic_state_from_source_snapshot(
        source_snapshot,
        com_occupation=occupation,
        beta_H=background.beta_H,
    )

    interface_frequencies = tuple(
        line.nu_abs_Hz + x * line.Doppler_width_Hz
        for x in (line.x_red, line.x_blue)
    )
    interface_samples = tuple(
        evaluator.evaluate(
            eta_target=eta_target,
            target_frequency_Hz=float(frequency),
            radiation_temperature_eV_rescaled=source_snapshot.TR_eV_rescaled,
        )
        for frequency in interface_frequencies
    )
    assert len(interface_samples) == 2

    atomic_sha = hash_atomic_state(
        atomic_state, source_snapshot_sha256=source_hash
    )
    background_sha = hash_background_sequence(background_sequence)
    interface_sha = _interface_digest(interface_samples)
    network_sha = network_node.file_sha256
    accepted_index = int(history.grid.source_indices[-1])
    metadata = {
        "canonical_eta": eta_target,
        "target_z": source_snapshot.z,
        "background_tau": float(background_tau),
        "reconstruction": "POINT_CHARACTERISTIC_SCALAR_HISTORY_V1",
        "initial_angular_condition": "ISOTROPIC_HYDROGEN_FRAME_V1",
        "claim_boundary": "BOOTSTRAP_PARENT_NOT_COUPLED_MACRO_ENDPOINT",
        "source_snapshot_sha256": source_hash,
        "network_node_sha256": network_node.node_sha256,
        "angular_point_count": angular_grid.n_angle,
        "frequency_state_count": network_node.network.n_state,
    }
    parent = AcceptedRadiationParent(
        occupation=occupation,
        evidence_class=ParentEvidenceClass.SOURCE_DERIVED_ACCEPTED,
        accepted_history_index=accepted_index,
        accepted_history_sha256=history.sha256,
        atomic_state_sha256=atomic_sha,
        background_sequence_sha256=background_sha,
        network_sha256=network_sha,
        interface_sha256=interface_sha,
        branch_id=str(branch_id),
        metadata=metadata,
    )
    requirements = ProductionParentRequirements(
        accepted_history_index=accepted_index,
        accepted_history_sha256=history.sha256,
        atomic_state_sha256=atomic_sha,
        background_sequence_sha256=background_sha,
        network_sha256=network_sha,
        interface_sha256=interface_sha,
        branch_id=str(branch_id),
    )
    activity_weight = network_node.network.activity_weight
    activity = scalar_occupation / (activity_weight * (1.0 + scalar_occupation))
    return SourceDerivedBootstrapParentResult(
        parent=parent,
        requirements=requirements,
        atomic_state=atomic_state,
        samples=samples,
        interface_samples=(interface_samples[0], interface_samples[1]),
        activity=activity,
        atomic_state_sha256=atomic_sha,
        background_sequence_sha256=background_sha,
        interface_sha256=interface_sha,
        coupled_macro_endpoint=False,
    )


__all__ = [
    "OriginalHyRecPointCharacteristicEvaluator",
    "PointCharacteristicSample",
    "SourceDerivedBootstrapParentResult",
    "build_source_derived_bootstrap_parent",
    "hash_atomic_state",
    "hash_background_sequence",
]
