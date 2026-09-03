"""Receiving-side source authority types for BASS kinetic states.

This bounded protocol records source provenance, physical-time rates, and
representation compatibility. It deliberately does not wire any source into a
solver loop.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import math
import re
from typing import Final

__all__ = [
    "SourceAuthorityBundle",
    "SourceFrequencyKind",
    "SourceRepresentationError",
    "SourceStateKind",
    "require_source_representation_compatibility",
    "required_work_rank",
    "validate_work_rank",
]

_SHA256_RE: Final[re.Pattern[str]] = re.compile(r"[0-9a-f]{64}\Z")
_PAYLOAD_SCHEMA: Final[str] = "bass.source_authority.constant_pair.v1"


class SourceFrequencyKind(str, Enum):
    """Frequency information carried by a source payload."""

    POINTWISE_SPECTRAL = "pointwise_spectral"
    SOURCE_INTEGRATED_WITNESS = "source_integrated_witness"


class SourceStateKind(str, Enum):
    """Numerical state surfaces that must not be silently interchanged."""

    FULL_SPECTRAL_GRID = "full_spectral_grid"
    RADIAL_INTEGRATED_ANGULAR_GRID = "radial_integrated_angular_grid"
    FINITE_SPECTRAL_PSTF = "finite_spectral_pstf"
    FINITE_INTEGRATED_J_HIERARCHY = "finite_integrated_j_hierarchy"


class SourceRepresentationError(ValueError):
    """Raised when a source lacks the information required by a state."""


def _finite_nonnegative(value: object, *, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a real scalar, got {type(value).__name__}")
    result = float(value)
    if not math.isfinite(result) or result < 0.0:
        raise ValueError(f"{name} must be finite and nonnegative, got {value!r}")
    return result


def _finite_positive(value: object, *, name: str) -> float:
    result = _finite_nonnegative(value, name=name)
    if result <= 0.0:
        raise ValueError(f"{name} must be strictly positive, got {value!r}")
    return result


def _named_text(value: object, *, name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")
    result = value.strip()
    if not result:
        raise ValueError(f"{name} must be nonempty")
    return result


def _sha256_text(value: object, *, name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a lowercase SHA-256 string")
    if _SHA256_RE.fullmatch(value) is None:
        raise ValueError(f"{name} must be exactly 64 lowercase hexadecimal characters")
    return value


def _rank(value: object, *, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be a nonnegative integer")
    if value < 0:
        raise ValueError(f"{name} must be nonnegative, got {value}")
    return value


@dataclass(frozen=True, slots=True)
class SourceAuthorityBundle:
    """Immutable constant paired source with explicit provenance."""

    eta_s_inv: float
    kappa_s_inv: float
    frame: str
    channel: str
    source_sha256: str
    frequency_kind: SourceFrequencyKind
    payload_sha256: str

    @classmethod
    def constant_pair(
        cls,
        *,
        eta_s_inv: object,
        kappa_s_inv: object,
        frame: object,
        channel: object,
        source_sha256: object,
        frequency_kind: SourceFrequencyKind,
    ) -> "SourceAuthorityBundle":
        eta = _finite_nonnegative(eta_s_inv, name="eta_s_inv")
        kappa = _finite_nonnegative(kappa_s_inv, name="kappa_s_inv")
        frame_name = _named_text(frame, name="frame")
        channel_name = _named_text(channel, name="channel")
        source_hash = _sha256_text(source_sha256, name="source_sha256")
        if not isinstance(frequency_kind, SourceFrequencyKind):
            raise TypeError("frequency_kind must be a SourceFrequencyKind")

        canonical_payload = {
            "channel": channel_name,
            "eta_s_inv_hex": eta.hex(),
            "frame": frame_name,
            "frequency_kind": frequency_kind.value,
            "kappa_s_inv_hex": kappa.hex(),
            "schema": _PAYLOAD_SCHEMA,
            "source_sha256": source_hash,
        }
        canonical_bytes = json.dumps(
            canonical_payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("ascii")
        payload_hash = hashlib.sha256(canonical_bytes).hexdigest()
        return cls(
            eta_s_inv=eta,
            kappa_s_inv=kappa,
            frame=frame_name,
            channel=channel_name,
            source_sha256=source_hash,
            frequency_kind=frequency_kind,
            payload_sha256=payload_hash,
        )

    @property
    def chi_affine_s_inv(self) -> float:
        """Signed affine coefficient kappa-eta in physical time."""

        return self.kappa_s_inv - self.eta_s_inv

    def rates_per_tau(self, *, H_s_inv: object) -> tuple[float, float]:
        """Convert physical-time rates using d_tau = H_s_inv dt exactly once."""

        hubble_rate = _finite_positive(H_s_inv, name="H_s_inv")
        return self.eta_s_inv / hubble_rate, self.kappa_s_inv / hubble_rate

    def pointwise_action(self, f: object) -> float:
        """Evaluate eta*(1+f)-kappa*f for a finite nonnegative occupation."""

        occupation = _finite_nonnegative(f, name="f")
        return self.eta_s_inv * (1.0 + occupation) - self.kappa_s_inv * occupation


def required_work_rank(*, l_out: object, l_source: object) -> int:
    """Minimum generic work rank for a finite-band angular product."""

    output_rank = _rank(l_out, name="L_out")
    source_rank = _rank(l_source, name="L_source")
    return output_rank + source_rank


def validate_work_rank(*, l_work: object, l_out: object, l_source: object) -> int:
    """Validate a finite-band angular product workspace."""

    work_rank = _rank(l_work, name="L_work")
    output_rank = _rank(l_out, name="L_out")
    source_rank = _rank(l_source, name="L_source")
    required = output_rank + source_rank
    if work_rank < required:
        raise ValueError(
            "insufficient angular product workspace: "
            f"L_work={work_rank}, L_out={output_rank}, "
            f"L_source={source_rank}, required={required}"
        )
    return required


def require_source_representation_compatibility(
    frequency_kind: SourceFrequencyKind,
    state_kind: SourceStateKind,
) -> None:
    """Fail closed when a source and stored state carry different information."""

    if not isinstance(frequency_kind, SourceFrequencyKind):
        raise TypeError("frequency_kind must be a SourceFrequencyKind")
    if not isinstance(state_kind, SourceStateKind):
        raise TypeError("state_kind must be a SourceStateKind")

    pointwise_states = {
        SourceStateKind.FULL_SPECTRAL_GRID,
        SourceStateKind.FINITE_SPECTRAL_PSTF,
    }
    integrated_states = {
        SourceStateKind.RADIAL_INTEGRATED_ANGULAR_GRID,
        SourceStateKind.FINITE_INTEGRATED_J_HIERARCHY,
    }
    admitted_states = (
        pointwise_states
        if frequency_kind is SourceFrequencyKind.POINTWISE_SPECTRAL
        else integrated_states
    )
    if state_kind not in admitted_states:
        raise SourceRepresentationError(
            f"{frequency_kind.value} source is incompatible with "
            f"{state_kind.value} state"
        )
