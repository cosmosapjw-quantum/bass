"""Dependency-light receiving adapters for a constant photon source pair.

The adapters apply one immutable pointwise-spectral source authority to either
an explicit full spectral/angular grid or a caller-declared spectral
PSTF/harmonic coefficient vector. They do not wire a source into an evolution
loop and they do not define an integrated-state closure.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import math
import re
from typing import Final

from bianchi.source_authority import (
    SourceArithmeticError,
    SourceAuthorityBundle,
    SourceFrequencyKind,
    SourceRepresentationError,
    SourceSpecies,
    SourceStateKind,
    SourceStatistics,
    require_source_representation_compatibility,
    validate_work_rank,
)

__all__ = [
    "SourceAdapterError",
    "SourceApplicationReceipt",
    "SourceApplicationResult",
    "SourceTimeBasis",
    "apply_constant_pair_to_full_spectral_grid",
    "apply_constant_pair_to_spectral_pstf",
    "require_dual_adapter_target",
]

_SHA256_RE: Final[re.Pattern[str]] = re.compile(r"[0-9a-f]{64}\Z")
_RECEIPT_SCHEMA: Final[str] = "bass.source_adapters.constant_pair_application.v1"


class SourceTimeBasis(str, Enum):
    """Independent variable with respect to which a source value is returned."""

    PHYSICAL_TIME = "physical_time"
    Q_TIME = "q_time"
    RAY_LENGTH = "ray_length"


class SourceAdapterError(ValueError):
    """Raised when an adapter input is ambiguous or representation-incompatible."""


@dataclass(frozen=True, slots=True)
class SourceApplicationReceipt:
    """Immutable identity record for one representation-specific source action."""

    receipt_schema: str
    state_kind: SourceStateKind
    time_basis: SourceTimeBasis
    source_payload_sha256: str
    state_parent_sha256: str
    representation_sha256: str
    projection_contract_sha256: str
    rate_divisor_hex: str
    output_sha256: str


@dataclass(frozen=True, slots=True)
class SourceApplicationResult:
    """Numerical source values together with their application receipt."""

    values: tuple[float, ...]
    receipt: SourceApplicationReceipt


def _sha256_text(value: object, *, name: str) -> str:
    if not isinstance(value, str) or _SHA256_RE.fullmatch(value) is None:
        raise SourceAdapterError(
            f"{name} must be exactly 64 lowercase hexadecimal characters"
        )
    return value


def _finite_scalar(value: object, *, name: str, nonnegative: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SourceAdapterError(f"{name} must be a real scalar")
    try:
        result = float(value)
    except (OverflowError, ValueError) as exc:
        raise SourceAdapterError(f"{name} is not representable as binary64") from exc
    if not math.isfinite(result):
        raise SourceAdapterError(f"{name} must be finite")
    if nonnegative and result < 0.0:
        raise SourceAdapterError(f"{name} must be nonnegative")
    return 0.0 if result == 0.0 else result


def _finite_sequence(
    values: object,
    *,
    name: str,
    nonnegative: bool,
) -> tuple[float, ...]:
    if isinstance(values, (str, bytes, bytearray)):
        raise SourceAdapterError(f"{name} must be an iterable of real scalars")
    try:
        raw = tuple(values)  # type: ignore[arg-type]
    except TypeError as exc:
        raise SourceAdapterError(
            f"{name} must be an iterable of real scalars"
        ) from exc
    if not raw:
        raise SourceAdapterError(f"{name} must be nonempty")
    return tuple(
        _finite_scalar(
            value,
            name=f"{name}[{index}]",
            nonnegative=nonnegative,
        )
        for index, value in enumerate(raw)
    )


def _positive_divisor(value: object, *, name: str) -> float:
    result = _finite_scalar(value, name=name)
    if result <= 0.0:
        raise SourceAdapterError(f"{name} must be strictly positive")
    return result


def _validated_bundle(bundle: object) -> SourceAuthorityBundle:
    if not isinstance(bundle, SourceAuthorityBundle):
        raise SourceAdapterError("source must be a SourceAuthorityBundle")
    if bundle.frequency_kind is not SourceFrequencyKind.POINTWISE_SPECTRAL:
        raise SourceAdapterError("dual adapters require a pointwise spectral source")
    if bundle.species is not SourceSpecies.PHOTON:
        raise SourceAdapterError("dual adapters currently accept photon sources only")
    if bundle.statistics is not SourceStatistics.BOSON:
        raise SourceAdapterError("dual adapters currently accept bosonic sources only")
    return bundle


def _rate_divisor(
    *,
    time_basis: object,
    H_s_inv: object | None,
    c_m_s: object | None,
) -> tuple[SourceTimeBasis, float]:
    if not isinstance(time_basis, SourceTimeBasis):
        raise SourceAdapterError("time_basis must be a SourceTimeBasis")

    if time_basis is SourceTimeBasis.PHYSICAL_TIME:
        if H_s_inv is not None or c_m_s is not None:
            raise SourceAdapterError(
                "physical-time action must not receive H_s_inv or c_m_s"
            )
        return time_basis, 1.0

    if time_basis is SourceTimeBasis.Q_TIME:
        if H_s_inv is None or c_m_s is not None:
            raise SourceAdapterError(
                "Q-time action requires H_s_inv and forbids c_m_s"
            )
        return time_basis, _positive_divisor(H_s_inv, name="H_s_inv")

    if H_s_inv is not None or c_m_s is None:
        raise SourceAdapterError(
            "ray-length action requires c_m_s and forbids H_s_inv"
        )
    return time_basis, _positive_divisor(c_m_s, name="c_m_s")


def require_dual_adapter_target(state_kind: object) -> None:
    """Admit only source surfaces retaining pointwise spectral information."""

    if not isinstance(state_kind, SourceStateKind):
        raise SourceAdapterError("state_kind must be a SourceStateKind")
    try:
        require_source_representation_compatibility(
            SourceFrequencyKind.POINTWISE_SPECTRAL,
            state_kind,
        )
    except (TypeError, ValueError, SourceRepresentationError) as exc:
        raise SourceAdapterError(
            f"pointwise source cannot target {state_kind.value}"
        ) from exc


def _application_hash(
    *,
    values: tuple[float, ...],
    state_kind: SourceStateKind,
    time_basis: SourceTimeBasis,
    rate_divisor: float,
    source_payload_sha256: str,
    state_parent_sha256: str,
    representation_sha256: str,
    projection_contract_sha256: str,
    adapter_parameters: dict[str, str],
) -> str:
    payload = {
        "adapter_parameters": adapter_parameters,
        "output_values_hex": [value.hex() for value in values],
        "projection_contract_sha256": projection_contract_sha256,
        "rate_divisor_hex": rate_divisor.hex(),
        "representation_sha256": representation_sha256,
        "schema": _RECEIPT_SCHEMA,
        "source_payload_sha256": source_payload_sha256,
        "state_kind": state_kind.value,
        "state_parent_sha256": state_parent_sha256,
        "time_basis": time_basis.value,
    }
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    return hashlib.sha256(canonical).hexdigest()


def _receipt(
    *,
    values: tuple[float, ...],
    state_kind: SourceStateKind,
    time_basis: SourceTimeBasis,
    rate_divisor: float,
    source: SourceAuthorityBundle,
    state_parent_sha256: object,
    representation_sha256: object,
    projection_contract_sha256: object,
    adapter_parameters: dict[str, str],
) -> SourceApplicationReceipt:
    state_parent = _sha256_text(
        state_parent_sha256,
        name="state_parent_sha256",
    )
    representation = _sha256_text(
        representation_sha256,
        name="representation_sha256",
    )
    projection = _sha256_text(
        projection_contract_sha256,
        name="projection_contract_sha256",
    )
    output_hash = _application_hash(
        values=values,
        state_kind=state_kind,
        time_basis=time_basis,
        rate_divisor=rate_divisor,
        source_payload_sha256=source.payload_sha256,
        state_parent_sha256=state_parent,
        representation_sha256=representation,
        projection_contract_sha256=projection,
        adapter_parameters=adapter_parameters,
    )
    return SourceApplicationReceipt(
        receipt_schema=_RECEIPT_SCHEMA,
        state_kind=state_kind,
        time_basis=time_basis,
        source_payload_sha256=source.payload_sha256,
        state_parent_sha256=state_parent,
        representation_sha256=representation,
        projection_contract_sha256=projection,
        rate_divisor_hex=rate_divisor.hex(),
        output_sha256=output_hash,
    )


def _scaled_finite(value: float, *, divisor: float, name: str) -> float:
    result = value / divisor
    if not math.isfinite(result):
        raise SourceAdapterError(f"{name} produced a nonfinite binary64 result")
    return 0.0 if result == 0.0 else result


def apply_constant_pair_to_full_spectral_grid(
    source: SourceAuthorityBundle,
    occupations: object,
    *,
    state_parent_sha256: object,
    representation_sha256: object,
    projection_contract_sha256: object,
    time_basis: SourceTimeBasis,
    H_s_inv: object | None = None,
    c_m_s: object | None = None,
) -> SourceApplicationResult:
    """Apply one constant source pair to explicit spectral/angular samples."""

    bundle = _validated_bundle(source)
    state_kind = SourceStateKind.FULL_SPECTRAL_GRID
    require_dual_adapter_target(state_kind)
    samples = _finite_sequence(
        occupations,
        name="occupations",
        nonnegative=True,
    )
    basis, divisor = _rate_divisor(
        time_basis=time_basis,
        H_s_inv=H_s_inv,
        c_m_s=c_m_s,
    )
    try:
        physical = tuple(bundle.pointwise_action(value) for value in samples)
    except (TypeError, ValueError, SourceArithmeticError) as exc:
        raise SourceAdapterError("full-grid source evaluation failed") from exc
    values = tuple(
        _scaled_finite(value, divisor=divisor, name="full-grid source")
        for value in physical
    )
    receipt = _receipt(
        values=values,
        state_kind=state_kind,
        time_basis=basis,
        rate_divisor=divisor,
        source=bundle,
        state_parent_sha256=state_parent_sha256,
        representation_sha256=representation_sha256,
        projection_contract_sha256=projection_contract_sha256,
        adapter_parameters={"adapter": "full_spectral_grid"},
    )
    return SourceApplicationResult(values=values, receipt=receipt)


def apply_constant_pair_to_spectral_pstf(
    source: SourceAuthorityBundle,
    coefficients: object,
    *,
    unit_field_coefficients: object,
    l_out: object,
    l_work: object,
    state_parent_sha256: object,
    representation_sha256: object,
    projection_contract_sha256: object,
    time_basis: SourceTimeBasis,
    H_s_inv: object | None = None,
    c_m_s: object | None = None,
) -> SourceApplicationResult:
    """Apply a constant source in a caller-declared spectral coefficient basis."""

    bundle = _validated_bundle(source)
    state_kind = SourceStateKind.FINITE_SPECTRAL_PSTF
    require_dual_adapter_target(state_kind)
    state_coefficients = _finite_sequence(
        coefficients,
        name="coefficients",
        nonnegative=False,
    )
    unit_coefficients = _finite_sequence(
        unit_field_coefficients,
        name="unit_field_coefficients",
        nonnegative=False,
    )
    if len(state_coefficients) != len(unit_coefficients):
        raise SourceAdapterError(
            "coefficients and unit_field_coefficients must have equal length"
        )

    if isinstance(l_out, bool) or not isinstance(l_out, int) or l_out < 0:
        raise SourceAdapterError("l_out must be a nonnegative integer")
    if isinstance(l_work, bool) or not isinstance(l_work, int) or l_work < 0:
        raise SourceAdapterError("l_work must be a nonnegative integer")
    try:
        validate_work_rank(l_work=l_work, l_out=l_out, l_source=0)
    except (TypeError, ValueError) as exc:
        raise SourceAdapterError("insufficient constant-source work rank") from exc

    basis, divisor = _rate_divisor(
        time_basis=time_basis,
        H_s_inv=H_s_inv,
        c_m_s=c_m_s,
    )
    eta = bundle.eta_s_inv
    chi = bundle.chi_affine_s_inv
    physical_values: list[float] = []
    for index, (coefficient, unit_coefficient) in enumerate(
        zip(state_coefficients, unit_coefficients, strict=True)
    ):
        value = eta * unit_coefficient - chi * coefficient
        if not math.isfinite(value):
            raise SourceAdapterError(
                f"spectral-PSTF source[{index}] is nonfinite"
            )
        physical_values.append(value)
    values = tuple(
        _scaled_finite(value, divisor=divisor, name="spectral-PSTF source")
        for value in physical_values
    )
    receipt = _receipt(
        values=values,
        state_kind=state_kind,
        time_basis=basis,
        rate_divisor=divisor,
        source=bundle,
        state_parent_sha256=state_parent_sha256,
        representation_sha256=representation_sha256,
        projection_contract_sha256=projection_contract_sha256,
        adapter_parameters={
            "adapter": "spectral_pstf",
            "l_out": str(l_out),
            "l_source": "0",
            "l_work": str(l_work),
        },
    )
    return SourceApplicationResult(values=values, receipt=receipt)
