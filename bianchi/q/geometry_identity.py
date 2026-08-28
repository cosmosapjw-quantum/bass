"""Dependency-light identity for RF-02C public geometry dispatch."""
from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping

from bianchi.geometry_identity import CONVENTION_HASH
from bianchi.scalar_charts import SCALAR_CHART_SCHEMA_HASH, SCALAR_CHART_SPECS


GEOMETRY_STATE_SCHEMA_HASH = (
    "9fa370fa32a5e0d7af7e8d97263db947a579d80c793e2818212b339a4b15e0f1"
)
EXECUTION_CONTRACT_V2_HASH = (
    "804826b9d5ce2f3333de0558447e351a8050dc8147d268e8a6055b6c5669e51c"
)
EVENT_REGISTRY_HASH = (
    "8b3d342328b4549c797fca1c106181657f832a07fafed29eb498450465b43918"
)
NATIVE_PAYLOAD_IDENTITY = "bass-rf02c-native-background-execution-v2"
NATIVE_CAPABILITIES = {
    "builtin_event_language": [
        "state",
        "parameter",
        "const_f64_bits",
        "add",
        "sub",
        "mul",
        "neg",
    ],
    "projection_routes": ["chart_project", "chart_project_checked"],
    "trajectory_routes": [
        "integrate_background_history",
        "restart_background_history",
        "integrate_background_batch_history",
    ],
    "trajectory_ownership": "one_native_call_per_complete_trajectory",
}
NATIVE_CAPABILITY_RECEIPT = hashlib.sha256(
    json.dumps(
        NATIVE_CAPABILITIES,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
).hexdigest()
ROUTING = {
    "class_b_exceptional_kappa": -9.0,
    "class_b_exceptional_routing_tolerance": 1e-9,
}
ROUTING_FINGERPRINT = hashlib.sha256(
    json.dumps(ROUTING, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
).hexdigest()


class GeometryRouteIdentityError(RuntimeError):
    """The loaded native geometry route does not attest the frozen identity."""


def _scalar_state_order() -> list[dict[str, object]]:
    return [
        {
            "chart": spec.chart,
            "state_names": list(spec.state_names),
            "constraint_names": list(spec.constraint_names),
        }
        for spec in SCALAR_CHART_SPECS.values()
    ]


def geometry_route_identity() -> dict[str, object]:
    """Return the complete identity expected from every public geometry call."""

    return {
        "identity_schema": "bass-rf02c-public-execution-route/v2",
        "convention_hash": CONVENTION_HASH,
        "state_schema_hash": GEOMETRY_STATE_SCHEMA_HASH,
        "scalar_chart_schema_hash": SCALAR_CHART_SCHEMA_HASH,
        "supported_chart_labels": list(SCALAR_CHART_SPECS),
        "scalar_state_order": _scalar_state_order(),
        "routing": dict(ROUTING),
        "routing_fingerprint": ROUTING_FINGERPRINT,
        "execution_contract_v2_hash": EXECUTION_CONTRACT_V2_HASH,
        "event_registry_hash": EVENT_REGISTRY_HASH,
        "native_payload_identity": NATIVE_PAYLOAD_IDENTITY,
        "native_capabilities": dict(NATIVE_CAPABILITIES),
        "native_capability_receipt": NATIVE_CAPABILITY_RECEIPT,
    }


def validate_native_geometry_identity(value: object) -> None:
    """Reject a native extension whose public-route identity differs exactly."""

    if isinstance(value, bytes):
        value = value.decode("ascii")
    if isinstance(value, str):
        try:
            observed = json.loads(value)
        except json.JSONDecodeError as exc:
            raise GeometryRouteIdentityError("native geometry identity is not JSON") from exc
    elif isinstance(value, Mapping):
        observed = dict(value)
    else:
        raise GeometryRouteIdentityError("native geometry identity has an unsupported type")
    expected = geometry_route_identity()
    if observed == expected:
        return
    mismatches = sorted(
        key for key in set(expected) | set(observed) if expected.get(key) != observed.get(key)
    )
    raise GeometryRouteIdentityError(
        "native geometry identity mismatch: " + ", ".join(mismatches)
    )


__all__ = [
    "EVENT_REGISTRY_HASH",
    "EXECUTION_CONTRACT_V2_HASH",
    "GEOMETRY_STATE_SCHEMA_HASH",
    "NATIVE_CAPABILITIES",
    "NATIVE_CAPABILITY_RECEIPT",
    "NATIVE_PAYLOAD_IDENTITY",
    "GeometryRouteIdentityError",
    "ROUTING",
    "ROUTING_FINGERPRINT",
    "geometry_route_identity",
    "validate_native_geometry_identity",
]
