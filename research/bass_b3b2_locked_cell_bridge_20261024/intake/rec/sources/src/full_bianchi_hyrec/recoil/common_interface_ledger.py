"""Typed componentwise common ledger for PR-04C3.

The three recombination snapshots are independent source-conditioned operator
lanes.  Their residuals are therefore never summed or averaged.  Every gate is
applied componentwise and the aggregate diagnostic is the maximum normalized
violation.  This prevents an error at one redshift from being hidden by an
opposite-signed error at another.

This module deliberately records the COM state as an operator-verification
state with ``q_activity=1``.  It does not construct or claim a native-derived
COM trajectory, fitted normalization, or direct native-to-COM state remap.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import math
import re
from typing import Iterable, Mapping


_TARGETS = (1300.0, 1100.0, 900.0)
_SIDES = ("red", "blue")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_REL_TOL = 3.0e-14
_ABS_TOL = 1.0e-300


class EvidenceClass(str, Enum):
    """Provenance class of a ledger value."""

    ALGEBRAIC = "algebraic"
    SOURCE_DERIVED = "source_derived"
    SOLVER_DERIVED = "solver_derived"
    DIAGNOSTIC = "diagnostic"


class GateCriterion(str, Enum):
    """Fail-closed scalar acceptance rule."""

    EXACT_ZERO = "exact_zero"
    EXACT_ONE = "exact_one"
    ABS_LE = "abs_le"
    LE = "le"
    GE = "ge"
    GT = "gt"


class StateClassification(str, Enum):
    """Scientific status of the COM interior state."""

    OPERATOR_VERIFICATION = "operator_verification"
    NATIVE_DERIVED_TRAJECTORY = "native_derived_trajectory"


def _finite(value: float, name: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _close(first: float, second: float) -> bool:
    return math.isclose(
        float(first), float(second), rel_tol=_REL_TOL, abs_tol=_ABS_TOL
    )


def _canonical_json(payload: object) -> str:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


@dataclass(frozen=True)
class ProvenanceLock:
    """SHA-256 lock for one load-bearing input or evidence object."""

    name: str
    relative_path: str
    sha256: str
    evidence_class: EvidenceClass

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("provenance name must be nonempty")
        path = self.relative_path.strip()
        if not path or path.startswith("/") or ".." in path.split("/"):
            raise ValueError("provenance path must be safe and repository-relative")
        if not _SHA256.fullmatch(self.sha256):
            raise ValueError("provenance SHA-256 must be 64 lowercase hex digits")
        if not isinstance(self.evidence_class, EvidenceClass):
            raise TypeError("invalid provenance evidence class")

    def to_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "relative_path": self.relative_path,
            "sha256": self.sha256,
            "evidence_class": self.evidence_class.value,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "ProvenanceLock":
        return cls(
            name=str(payload["name"]),
            relative_path=str(payload["relative_path"]),
            sha256=str(payload["sha256"]),
            evidence_class=EvidenceClass(str(payload["evidence_class"])),
        )


@dataclass(frozen=True)
class PacketLedgerRecord:
    """Identity and history-domain record for one red/blue face packet."""

    packet_id: str
    target_z: float
    snapshot_z: float
    side: str
    direction: str
    interface_x: float
    interface_frequency_Hz: float
    n_H_m3: float
    history_index_left: int
    history_index_right: int
    solved_history_index: int
    packet_sha256: str

    def __post_init__(self) -> None:
        if not self.packet_id.strip():
            raise ValueError("packet ID must be nonempty")
        target = _finite(self.target_z, "target_z")
        snapshot = _finite(self.snapshot_z, "snapshot_z")
        if target not in _TARGETS or snapshot <= 0.0:
            raise ValueError("packet target/snapshot redshift is invalid")
        if self.side not in _SIDES:
            raise ValueError("packet side must be red or blue")
        expected_direction = "com_to_native" if self.side == "red" else "native_to_com"
        if self.direction != expected_direction:
            raise ValueError("packet direction is inconsistent with side")
        expected_x = -21.25 if self.side == "red" else 21.25
        if not _close(self.interface_x, expected_x):
            raise ValueError("packet interface face is inconsistent with side")
        if _finite(self.interface_frequency_Hz, "interface_frequency_Hz") <= 0.0:
            raise ValueError("packet frequency must be positive")
        if _finite(self.n_H_m3, "n_H_m3") <= 0.0:
            raise ValueError("packet hydrogen density must be positive")
        if self.history_index_left < 0:
            raise ValueError("history indices must be nonnegative")
        if self.history_index_right < self.history_index_left:
            raise ValueError("history indices must be ordered")
        if self.history_index_right > self.solved_history_index:
            raise ValueError("future history endpoint is forbidden")
        if not _SHA256.fullmatch(self.packet_sha256):
            raise ValueError("packet SHA-256 must be 64 lowercase hex digits")

    def to_dict(self) -> dict[str, object]:
        return {
            "packet_id": self.packet_id,
            "target_z": float(self.target_z),
            "snapshot_z": float(self.snapshot_z),
            "side": self.side,
            "direction": self.direction,
            "interface_x": float(self.interface_x),
            "interface_frequency_Hz": float(self.interface_frequency_Hz),
            "n_H_m3": float(self.n_H_m3),
            "history_index_left": int(self.history_index_left),
            "history_index_right": int(self.history_index_right),
            "solved_history_index": int(self.solved_history_index),
            "packet_sha256": self.packet_sha256,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "PacketLedgerRecord":
        return cls(
            packet_id=str(payload["packet_id"]),
            target_z=float(payload["target_z"]),
            snapshot_z=float(payload["snapshot_z"]),
            side=str(payload["side"]),
            direction=str(payload["direction"]),
            interface_x=float(payload["interface_x"]),
            interface_frequency_Hz=float(payload["interface_frequency_Hz"]),
            n_H_m3=float(payload["n_H_m3"]),
            history_index_left=int(payload["history_index_left"]),
            history_index_right=int(payload["history_index_right"]),
            solved_history_index=int(payload["solved_history_index"]),
            packet_sha256=str(payload["packet_sha256"]),
        )


@dataclass(frozen=True)
class LedgerMetric:
    """One scalar gate with units, provenance class and normalization."""

    name: str
    value: float
    unit: str
    evidence_class: EvidenceClass
    criterion: GateCriterion
    limit: float
    scale: float

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.unit.strip():
            raise ValueError("metric name and unit must be nonempty")
        _finite(self.value, "metric value")
        _finite(self.limit, "metric limit")
        if _finite(self.scale, "metric scale") <= 0.0:
            raise ValueError("metric scale must be positive")
        if not isinstance(self.evidence_class, EvidenceClass):
            raise TypeError("invalid metric evidence class")
        if not isinstance(self.criterion, GateCriterion):
            raise TypeError("invalid metric criterion")
        if self.criterion is GateCriterion.ABS_LE and self.limit < 0.0:
            raise ValueError("absolute threshold must be nonnegative")

    @property
    def passed(self) -> bool:
        value = float(self.value)
        limit = float(self.limit)
        if self.criterion is GateCriterion.EXACT_ZERO:
            return value == 0.0
        if self.criterion is GateCriterion.EXACT_ONE:
            return value == 1.0
        if self.criterion is GateCriterion.ABS_LE:
            return abs(value) <= limit
        if self.criterion is GateCriterion.LE:
            return value <= limit
        if self.criterion is GateCriterion.GE:
            return value >= limit
        if self.criterion is GateCriterion.GT:
            return value > limit
        raise AssertionError(self.criterion)

    @property
    def normalized_violation(self) -> float:
        """Return zero on pass and a positive dimensionless violation on fail."""

        if self.passed:
            return 0.0
        value = float(self.value)
        limit = float(self.limit)
        scale = float(self.scale)
        if self.criterion is GateCriterion.EXACT_ZERO:
            return abs(value) / scale
        if self.criterion is GateCriterion.EXACT_ONE:
            return abs(value - 1.0) / scale
        if self.criterion is GateCriterion.ABS_LE:
            denominator = limit if limit > 0.0 else scale
            return abs(value) / denominator
        if self.criterion is GateCriterion.LE:
            return (value - limit) / scale
        if self.criterion in (GateCriterion.GE, GateCriterion.GT):
            return (limit - value) / scale
        raise AssertionError(self.criterion)

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "value": float(self.value),
            "unit": self.unit,
            "evidence_class": self.evidence_class.value,
            "criterion": self.criterion.value,
            "limit": float(self.limit),
            "scale": float(self.scale),
            "passed": self.passed,
            "normalized_violation": float(self.normalized_violation),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "LedgerMetric":
        return cls(
            name=str(payload["name"]),
            value=float(payload["value"]),
            unit=str(payload["unit"]),
            evidence_class=EvidenceClass(str(payload["evidence_class"])),
            criterion=GateCriterion(str(payload["criterion"])),
            limit=float(payload["limit"]),
            scale=float(payload["scale"]),
        )


@dataclass(frozen=True)
class SnapshotLedger:
    """One independent source-conditioned redshift lane."""

    target_z: float
    snapshot_z: float
    state_classification: StateClassification
    q_activity: float
    packets: tuple[PacketLedgerRecord, ...]
    metrics: tuple[LedgerMetric, ...]
    provenance: tuple[ProvenanceLock, ...]

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        target = _finite(self.target_z, "snapshot target_z")
        if target not in _TARGETS:
            raise ValueError("snapshot target is outside the declared lanes")
        if _finite(self.snapshot_z, "snapshot_z") <= 0.0:
            raise ValueError("snapshot redshift must be positive")
        if self.state_classification is not StateClassification.OPERATOR_VERIFICATION:
            raise ValueError(
                "PR-04C3 permits only the explicit operator-verification state"
            )
        if not _close(self.q_activity, 1.0):
            raise ValueError("q_activity must remain the declared value 1")
        if len(self.packets) != 2:
            raise ValueError("each snapshot must contain exactly two packets")
        packet_sides = tuple(packet.side for packet in self.packets)
        if packet_sides != _SIDES:
            raise ValueError("snapshot packets must be ordered red then blue")
        packet_ids = [packet.packet_id for packet in self.packets]
        if len(set(packet_ids)) != len(packet_ids):
            raise ValueError("duplicate packet ID inside snapshot")
        for packet in self.packets:
            if packet.target_z != target:
                raise ValueError("packet target does not match snapshot target")
            if not _close(packet.snapshot_z, self.snapshot_z):
                raise ValueError("packet redshift does not match snapshot redshift")
        if not _close(self.packets[0].n_H_m3, self.packets[1].n_H_m3):
            raise ValueError("red/blue packets have inconsistent local n_H")
        metric_names = [metric.name for metric in self.metrics]
        if not metric_names or len(set(metric_names)) != len(metric_names):
            raise ValueError("snapshot metric names must be nonempty and unique")
        provenance_names = [item.name for item in self.provenance]
        if not provenance_names or len(set(provenance_names)) != len(provenance_names):
            raise ValueError("snapshot provenance names must be nonempty and unique")

    def metric(self, name: str) -> LedgerMetric:
        matches = [metric for metric in self.metrics if metric.name == name]
        if len(matches) != 1:
            raise KeyError(name)
        return matches[0]

    @property
    def passed(self) -> bool:
        return all(metric.passed for metric in self.metrics)

    @property
    def epsilon(self) -> float:
        return max((metric.normalized_violation for metric in self.metrics), default=0.0)

    def to_dict(self) -> dict[str, object]:
        return {
            "target_z": float(self.target_z),
            "snapshot_z": float(self.snapshot_z),
            "state_classification": self.state_classification.value,
            "q_activity": float(self.q_activity),
            "packets": [packet.to_dict() for packet in self.packets],
            "metrics": [metric.to_dict() for metric in self.metrics],
            "provenance": [item.to_dict() for item in self.provenance],
            "passed": self.passed,
            "epsilon": float(self.epsilon),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "SnapshotLedger":
        packets = payload["packets"]
        metrics = payload["metrics"]
        provenance = payload["provenance"]
        if not isinstance(packets, list) or not isinstance(metrics, list) or not isinstance(provenance, list):
            raise TypeError("snapshot collection fields must be lists")
        return cls(
            target_z=float(payload["target_z"]),
            snapshot_z=float(payload["snapshot_z"]),
            state_classification=StateClassification(
                str(payload["state_classification"])
            ),
            q_activity=float(payload["q_activity"]),
            packets=tuple(PacketLedgerRecord.from_dict(row) for row in packets),
            metrics=tuple(LedgerMetric.from_dict(row) for row in metrics),
            provenance=tuple(ProvenanceLock.from_dict(row) for row in provenance),
        )


@dataclass(frozen=True)
class CommonInterfaceLedger:
    """Ordered componentwise common ledger over the three declared snapshots."""

    schema: str
    snapshots: tuple[SnapshotLedger, ...]
    global_provenance: tuple[ProvenanceLock, ...]
    direct_state_remap_used: bool
    fitted_normalization_used: bool

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        if self.schema != "PR04C3_COMMON_INTERFACE_LEDGER_V1":
            raise ValueError("unsupported common-ledger schema")
        targets = tuple(snapshot.target_z for snapshot in self.snapshots)
        if targets != _TARGETS:
            raise ValueError("common ledger requires the exact ordered target lanes")
        if self.direct_state_remap_used:
            raise ValueError("direct state remap is forbidden")
        if self.fitted_normalization_used:
            raise ValueError("fitted normalization is forbidden")
        packet_ids = self.packet_ids
        if len(packet_ids) != 6 or len(set(packet_ids)) != 6:
            raise ValueError("common ledger requires six unique packet IDs")
        global_names = [item.name for item in self.global_provenance]
        if not global_names or len(set(global_names)) != len(global_names):
            raise ValueError("global provenance locks must be nonempty and unique")
        for snapshot in self.snapshots:
            snapshot.validate()

    @property
    def packet_ids(self) -> tuple[str, ...]:
        return tuple(
            packet.packet_id
            for snapshot in self.snapshots
            for packet in snapshot.packets
        )

    @property
    def componentwise_passed(self) -> bool:
        return all(snapshot.passed for snapshot in self.snapshots)

    @property
    def epsilon_common(self) -> float:
        return max((snapshot.epsilon for snapshot in self.snapshots), default=0.0)

    @property
    def state_classification(self) -> StateClassification:
        classifications = {snapshot.state_classification for snapshot in self.snapshots}
        if classifications != {StateClassification.OPERATOR_VERIFICATION}:
            raise ValueError("mixed or unsupported state classifications")
        return StateClassification.OPERATOR_VERIFICATION

    def failed_components(self) -> list[dict[str, object]]:
        failures: list[dict[str, object]] = []
        for snapshot in self.snapshots:
            for metric in snapshot.metrics:
                if metric.passed:
                    continue
                failures.append(
                    {
                        "target_z": float(snapshot.target_z),
                        "metric": metric.name,
                        "value": float(metric.value),
                        "unit": metric.unit,
                        "criterion": metric.criterion.value,
                        "limit": float(metric.limit),
                        "normalized_violation": float(metric.normalized_violation),
                    }
                )
        return failures

    def to_payload(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "claim_level": "source_conditioned_operator_contract",
            "state_classification": self.state_classification.value,
            "direct_state_remap_used": self.direct_state_remap_used,
            "fitted_normalization_used": self.fitted_normalization_used,
            "global_provenance": [item.to_dict() for item in self.global_provenance],
            "snapshots": [snapshot.to_dict() for snapshot in self.snapshots],
            "componentwise_passed": self.componentwise_passed,
            "epsilon_common": float(self.epsilon_common),
            "failed_components": self.failed_components(),
            "aggregation_policy": "maximum_normalized_component_violation_never_sum",
        }

    @classmethod
    def from_payload(cls, payload: Mapping[str, object]) -> "CommonInterfaceLedger":
        snapshots = payload["snapshots"]
        provenance = payload["global_provenance"]
        if not isinstance(snapshots, list) or not isinstance(provenance, list):
            raise TypeError("common-ledger collection fields must be lists")
        return cls(
            schema=str(payload["schema"]),
            snapshots=tuple(SnapshotLedger.from_dict(row) for row in snapshots),
            global_provenance=tuple(ProvenanceLock.from_dict(row) for row in provenance),
            direct_state_remap_used=bool(payload["direct_state_remap_used"]),
            fitted_normalization_used=bool(payload["fitted_normalization_used"]),
        )

    def canonical_json(self) -> str:
        return _canonical_json(self.to_payload())

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()


def maximum_componentwise_violation(
    ledgers: Iterable[SnapshotLedger],
) -> float:
    """Expose the no-cross-snapshot-cancellation aggregation rule."""

    values = tuple(ledger.epsilon for ledger in ledgers)
    if not values:
        raise ValueError("at least one snapshot ledger is required")
    return max(values)
