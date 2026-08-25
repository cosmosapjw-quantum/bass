"""RF-02B typed scalar-chart authority.

The inventory is deliberately narrower than ``bianchi.charts``.  It contains the
fixed-size, non-tilted reduced background charts whose pointwise RHS, exact JVP,
equality constraints, and projection are owned by RF-02B.  Tilted matter belongs to
RF-03; the general tensor charts remain independent formula oracles.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from types import MappingProxyType
from typing import Mapping

from bianchi.geometry_identity import CONVENTION_HASH


@dataclass(frozen=True)
class ScalarChartSpec:
    """One immutable packed-state/operator contract."""

    chart: str
    module: str
    state_class: str
    rhs_function: str
    state_names: tuple[str, ...]
    constraint_names: tuple[str, ...]

    @property
    def nstates(self) -> int:
        return len(self.state_names)


_SPECS = (
    ScalarChartSpec(
        chart="class_a",
        module="bianchi.charts.class_a",
        state_class="StateA",
        rhs_function="rhs",
        state_names=("Sigma_p", "Sigma_m", "N1", "N2", "N3"),
        constraint_names=(),
    ),
    ScalarChartSpec(
        chart="class_b",
        module="bianchi.charts.class_b",
        state_class="StateB",
        rhs_function="rhs",
        state_names=("Sigma_p", "Sigma_tilde", "Delta", "A_tilde", "N_p"),
        constraint_names=("codazzi",),
    ),
    ScalarChartSpec(
        chart="exceptional",
        module="bianchi.charts.exceptional",
        state_class="StateE",
        rhs_function="rhs",
        state_names=("Sigma_p", "Sigma_m", "Sigma_2", "Sigma_x", "N_m", "A"),
        constraint_names=("g",),
    ),
    ScalarChartSpec(
        chart="type_ix_d",
        module="bianchi.charts.type_ix_d",
        state_class="StateD",
        rhs_function="rhs",
        state_names=("H", "S1", "S2", "S3", "N1", "N2", "N3"),
        constraint_names=("definition", "trace"),
    ),
    ScalarChartSpec(
        chart="type_ix_d_future",
        module="bianchi.charts.type_ix_d",
        state_class="StateD",
        rhs_function="rhs_future",
        state_names=("H", "S1", "S2", "S3", "N1", "N2", "N3"),
        constraint_names=("definition", "trace"),
    ),
)

SCALAR_CHART_SPECS: Mapping[str, ScalarChartSpec] = MappingProxyType(
    {spec.chart: spec for spec in _SPECS}
)


def _canonical_payload() -> dict:
    return {
        "version": "rf02b-scalar-chart-schema-v1",
        "geometry_convention_hash": CONVENTION_HASH,
        "excluded_authority_lanes": {
            "class_a_tilted": "RF-03",
            "class_b_tilted": "RF-03",
            "class_a_tilted_multi": "RF-03",
            "general": "tensor_formula_oracle",
            "general_matter": "RF-03",
        },
        "charts": [asdict(spec) for spec in _SPECS],
    }


SCALAR_CHART_SCHEMA_HASH = hashlib.sha256(
    json.dumps(
        _canonical_payload(),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
).hexdigest()


def require_scalar_chart(chart: str) -> ScalarChartSpec:
    """Return the frozen spec or fail before loading a numerical oracle."""

    try:
        return SCALAR_CHART_SPECS[chart]
    except KeyError as exc:
        raise ValueError(
            f"{chart!r} is not an RF-02B scalar chart; supported: "
            f"{', '.join(SCALAR_CHART_SPECS)}"
        ) from exc


def chart_schema_receipt() -> dict:
    """Machine-readable schema receipt; the hash is the authority identifier."""

    payload = _canonical_payload()
    payload["schema_hash"] = SCALAR_CHART_SCHEMA_HASH
    return payload


__all__ = [
    "SCALAR_CHART_SCHEMA_HASH",
    "SCALAR_CHART_SPECS",
    "ScalarChartSpec",
    "chart_schema_receipt",
    "require_scalar_chart",
]
