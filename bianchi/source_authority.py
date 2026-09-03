"""Receiving-side source authority types for BASS kinetic states.

This bounded protocol records source provenance, physical-time rates, particle
statistics, and representation compatibility.  It deliberately does not wire
any source into a solver loop.
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
    "IntegratedMomentMapBinding",
    "SourceArithmeticError",
    "SourceAuthorityBundle",
    "SourceFrequencyKind",
    "SourceRepresentationError",
    "SourceSpecies",
    "SourceStateKind",
    "SourceStatistics",
    "require_source_representation_compatibility",
    "required_work_rank",
    "validate_work_rank",
]

_SHA256_RE: Final[re.Pattern[str]] = re.compile(r"[0-9a-f]{64}\Z")
_CONSTANT_PAIR_SCHEMA: Final[str] = "bass.source_authority.constant_pair.v2"
_INTEGRATED_BINDING_SCHEMA: Final[str] = (
    "bass.source_authority.integrated_moment_map_binding.v1"
)


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


class SourceSpecies(str, Enum):
    """Particle species whose occupation law the source implements."""

    PHOTON = "photon"


class SourceStatistics(str, Enum):
    """Quantum-statistics sign encoded by the source action."""

    BOSON = "boson"


class SourceRepresentationError(ValueError):
    """Raised when a source lacks the information required by a state."""


class SourceArithmeticError(ArithmeticError):
    """Raised when a finite source input produces a nonfinite binary64 result."""


def _finite_nonnegative(value: object, *, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a real scalar, got {type(value).__name__}")
    result = float(value)
    if not math.isfinite(result) or result < 0.0:
        raise ValueError(f"{name} must be finite and nonnegative, got {value!r}")
    # IEEE-754 signed zero has no physical distinction for a nonnegative rate or
    # occupation.  Canonicalizing here makes physical and byte identity agree.
    return 0.0 if result == 0.0 else result


def _finite_positive(value: object, *, name: str) -> float:
    result = _finite_nonnegative(value, name=name)
    if result <= 0.0:
        raise ValueError(f"{name} must be strictly positive, got {value!r}")
    return result


def _finite_result(value: float, *, operation: str) -> float:
    if not math.isfinite(value):
        raise SourceArithmeticError(
            f"{operation} produced a nonfinite binary64 result"
        )
    return value


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


def _payload_sha256(payload: dict[str, str]) -> str:
    canonical_bytes = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    return hashlib.sha256(canonical_bytes).hexdigest()


def _reject_public_constructor(type_name: str) -> TypeError:
    return TypeError(f"use a validated {type_name} factory")


@dataclass(frozen=True, slots=True, init=False)
class SourceAuthorityBundle:
    """Validated photon/boson constant paired source with explicit provenance."""

    eta_s_inv: float
    kappa_s_inv: float
    frame: str
    channel: str
    source_sha256: str
    frequency_kind: SourceFrequencyKind
    species: SourceSpecies
    statistics: SourceStatistics
    payload_schema: str
    payload_sha256: str

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Block unvalidated construction and caller-forged payload identities."""

        raise _reject_public_constructor("SourceAuthorityBundle")

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
        if frequency_kind is not SourceFrequencyKind.POINTWISE_SPECTRAL:
            raise SourceRepresentationError(
                "a constant pointwise pair cannot represent a source-integrated "
                "moment witness"
            )

        species = SourceSpecies.PHOTON
        statistics = SourceStatistics.BOSON
        canonical_payload = {
            "channel": channel_name,
            "eta_s_inv_hex": eta.hex(),
            "frame": frame_name,
            "frequency_kind": frequency_kind.value,
            "kappa_s_inv_hex": kappa.hex(),
            "schema": _CONSTANT_PAIR_SCHEMA,
            "source_sha256": source_hash,
            "species": species.value,
            "statistics": statistics.value,
        }
        payload_hash = _payload_sha256(canonical_payload)

        instance = object.__new__(cls)
        object.__setattr__(instance, "eta_s_inv", eta)
        object.__setattr__(instance, "kappa_s_inv", kappa)
        object.__setattr__(instance, "frame", frame_name)
        object.__setattr__(instance, "channel", channel_name)
        object.__setattr__(instance, "source_sha256", source_hash)
        object.__setattr__(instance, "frequency_kind", frequency_kind)
        object.__setattr__(instance, "species", species)
        object.__setattr__(instance, "statistics", statistics)
        object.__setattr__(instance, "payload_schema", _CONSTANT_PAIR_SCHEMA)
        object.__setattr__(instance, "payload_sha256", payload_hash)
        return instance

    @property
    def chi_affine_s_inv(self) -> float:
        """Signed affine coefficient kappa-eta in physical time."""

        return self.kappa_s_inv - self.eta_s_inv

    def rates_per_tau(self, *, H_s_inv: object) -> tuple[float, float]:
        """Convert physical-time rates using d_tau = H_s_inv dt exactly once."""

        hubble_rate = _finite_positive(H_s_inv, name="H_s_inv")
        try:
            eta_per_tau = self.eta_s_inv / hubble_rate
            kappa_per_tau = self.kappa_s_inv / hubble_rate
        except OverflowError as exc:
            raise SourceArithmeticError(
                "physical-time to Q-time rate conversion overflowed binary64"
            ) from exc
        return (
            _finite_result(eta_per_tau, operation="eta_s_inv/H_s_inv"),
            _finite_result(kappa_per_tau, operation="kappa_s_inv/H_s_inv"),
        )

    def pointwise_action(self, f: object) -> float:
        """Evaluate the photon/boson affine source for one occupation value."""

        occupation = _finite_nonnegative(f, name="f")
        # The affine form is algebraically identical to eta*(1+f)-kappa*f and
        # avoids a needless inf-inf intermediate when eta and kappa are close.
        try:
            result = self.eta_s_inv - self.chi_affine_s_inv * occupation
        except OverflowError as exc:
            raise SourceArithmeticError(
                "photon/boson pointwise source overflowed binary64"
            ) from exc
        return _finite_result(result, operation="photon/boson pointwise source")


@dataclass(frozen=True, slots=True, init=False)
class IntegratedMomentMapBinding:
    """Immutable authority binding for one source-integrated state map."""

    target_state_kind: SourceStateKind
    moment_map_sha256: str
    radial_weight_family_sha256: str
    source_sha256: str
    binding_schema: str
    binding_sha256: str

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Block unvalidated construction and caller-forged binding identities."""

        raise _reject_public_constructor("IntegratedMomentMapBinding")

    @classmethod
    def create(
        cls,
        *,
        target_state_kind: SourceStateKind,
        moment_map_sha256: object,
        radial_weight_family_sha256: object,
        source_sha256: object,
    ) -> "IntegratedMomentMapBinding":
        if not isinstance(target_state_kind, SourceStateKind):
            raise TypeError("target_state_kind must be a SourceStateKind")
        integrated_states = {
            SourceStateKind.RADIAL_INTEGRATED_ANGULAR_GRID,
            SourceStateKind.FINITE_INTEGRATED_J_HIERARCHY,
        }
        if target_state_kind not in integrated_states:
            raise SourceRepresentationError(
                "an integrated moment-map binding requires an integrated target state"
            )

        moment_map_hash = _sha256_text(
            moment_map_sha256,
            name="moment_map_sha256",
        )
        radial_weight_hash = _sha256_text(
            radial_weight_family_sha256,
            name="radial_weight_family_sha256",
        )
        source_hash = _sha256_text(source_sha256, name="source_sha256")
        canonical_payload = {
            "moment_map_sha256": moment_map_hash,
            "radial_weight_family_sha256": radial_weight_hash,
            "schema": _INTEGRATED_BINDING_SCHEMA,
            "source_sha256": source_hash,
            "target_state_kind": target_state_kind.value,
        }
        binding_hash = _payload_sha256(canonical_payload)

        instance = object.__new__(cls)
        object.__setattr__(instance, "target_state_kind", target_state_kind)
        object.__setattr__(instance, "moment_map_sha256", moment_map_hash)
        object.__setattr__(
            instance,
            "radial_weight_family_sha256",
            radial_weight_hash,
        )
        object.__setattr__(instance, "source_sha256", source_hash)
        object.__setattr__(instance, "binding_schema", _INTEGRATED_BINDING_SCHEMA)
        object.__setattr__(instance, "binding_sha256", binding_hash)
        return instance


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
    *,
    integrated_binding: IntegratedMomentMapBinding | None = None,
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

    if frequency_kind is SourceFrequencyKind.POINTWISE_SPECTRAL:
        if integrated_binding is not None:
            raise SourceRepresentationError(
                "a pointwise spectral source must not carry an integrated binding"
            )
        if state_kind not in pointwise_states:
            raise SourceRepresentationError(
                f"{frequency_kind.value} source is incompatible with "
                f"{state_kind.value} state"
            )
        return

    if state_kind not in integrated_states:
        raise SourceRepresentationError(
            f"{frequency_kind.value} source is incompatible with "
            f"{state_kind.value} state"
        )
    if not isinstance(integrated_binding, IntegratedMomentMapBinding):
        raise SourceRepresentationError(
            "a source-integrated witness requires an IntegratedMomentMapBinding"
        )
    if integrated_binding.target_state_kind is not state_kind:
        raise SourceRepresentationError(
            "integrated source binding target does not match the requested state: "
            f"binding={integrated_binding.target_state_kind.value}, "
            f"requested={state_kind.value}"
        )
