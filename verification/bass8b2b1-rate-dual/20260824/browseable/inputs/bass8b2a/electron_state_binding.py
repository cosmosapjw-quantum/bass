"""Typed electron-state binding and exact segment-time jets for BASS-8B.2A.

This module is a bounded authority candidate.  It wraps the public E1--E4
schedule view contract without altering the schedule owner's interpolation
semantics.  It does not bind the direction-dependent opacity, finite radiation
carrier, collision projector, paired left functional, solver, JAX/Rust ABI, or
production runtime.

Conventions
-----------
* metric signature ``(-,+,+,+)``;
* ``tau_Q`` is dimensionless and increases to the physical future;
* electron number current components are normal-tetrad components
  ``N^A = n_e U_e^A``;
* ``n_e`` is proper free-electron density in ``m^-3``;
* ``beta`` and ``d beta / d tau_Q`` are dimensionless;
* exact vacuum is a collision-off quotient and retains no electron velocity.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, localcontext
from enum import Enum
from fractions import Fraction
import hashlib
import json
import math
import re
from types import MappingProxyType
from typing import Any, Mapping


_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_C_LIGHT_M_S = 299_792_458.0
_DECIMAL_PRECISION = 100
_CANONICAL_PLASMA_MODEL = "cold-ionized-baryon-electron-plasma"


def _text(value: Any, name: str) -> str:
    out = str(value).strip()
    if not out or "\0" in out:
        raise ValueError(f"{name} must be non-empty and contain no NUL")
    return out


def _sha(value: Any, name: str) -> str:
    out = str(value)
    if _SHA256.fullmatch(out) is None:
        raise ValueError(f"{name} must be lowercase 64-hex SHA-256")
    return out


def _finite(value: Any, name: str) -> float:
    out = float(value)
    if not math.isfinite(out):
        raise ValueError(f"{name} must be finite")
    return out


def _vec3(value: Any, name: str) -> tuple[float, float, float]:
    try:
        out = tuple(float(component) for component in value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a finite length-3 vector") from exc
    if len(out) != 3 or not all(math.isfinite(component) for component in out):
        raise ValueError(f"{name} must be a finite length-3 vector")
    return out


def _validate_beta(value: Any, name: str) -> tuple[float, float, float]:
    out = _vec3(value, name)
    norm2 = sum(component * component for component in out)
    if norm2 >= 1.0:
        raise ValueError(f"{name} must satisfy |beta|<1")
    return out


def _fraction(value: Any, name: str) -> Fraction:
    out = _finite(value, name)
    return Fraction.from_float(out)


def _sqrt_fraction(value: Fraction) -> float:
    if value < 0:
        raise ValueError("cannot take square root of a negative exact fraction")
    if value == 0:
        return 0.0
    with localcontext() as ctx:
        ctx.prec = _DECIMAL_PRECISION
        decimal_value = Decimal(value.numerator) / Decimal(value.denominator)
        result = decimal_value.sqrt()
    out = float(result)
    if not math.isfinite(out):
        raise ValueError("exact square root overflowed binary64")
    return out


def _canonical_hash(schema: str, payload: Mapping[str, Any]) -> str:
    raw = json.dumps(
        {"schema": schema, **payload},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True, slots=True)
class HashRef:
    source_id: str
    source_sha256: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "source_id", _text(self.source_id, "source_id"))
        object.__setattr__(
            self, "source_sha256", _sha(self.source_sha256, "source_sha256")
        )


@dataclass(frozen=True, slots=True)
class QHubbleTimeAuthority:
    origin_event: str
    provenance: HashRef
    coordinate_kind: str = "q_hubble_time_tau"
    mapping: str = "identity"
    unit: str = "dimensionless"
    future_direction: int = 1

    def __post_init__(self) -> None:
        object.__setattr__(self, "origin_event", _text(self.origin_event, "origin_event"))
        if not isinstance(self.provenance, HashRef):
            raise TypeError("provenance must be a HashRef")
        if self.coordinate_kind != "q_hubble_time_tau":
            raise ValueError("coordinate_kind must be q_hubble_time_tau")
        if self.mapping != "identity":
            raise ValueError("only an identity Q-time binding is allowed")
        if self.unit != "dimensionless" or self.future_direction != 1:
            raise ValueError("tau_Q must be dimensionless and future increasing")

    @property
    def payload_sha256(self) -> str:
        return _canonical_hash(
            "bass.q_hubble_time_authority/v1",
            {
                "origin_event": self.origin_event,
                "coordinate_kind": self.coordinate_kind,
                "mapping": self.mapping,
                "unit": self.unit,
                "future_direction": self.future_direction,
                "source_id": self.provenance.source_id,
                "source_sha256": self.provenance.source_sha256,
            },
        )


@dataclass(frozen=True, slots=True)
class PlasmaIdentity:
    species_id: str
    plasma_model: str
    provenance: HashRef

    def __post_init__(self) -> None:
        object.__setattr__(self, "species_id", _text(self.species_id, "species_id"))
        object.__setattr__(self, "plasma_model", _text(self.plasma_model, "plasma_model"))
        if not isinstance(self.provenance, HashRef):
            raise TypeError("provenance must be a HashRef")


@dataclass(frozen=True, slots=True)
class VelocityEqualityProof:
    species_id: str
    statement: str
    proof_sha256: str
    authority: HashRef

    def __post_init__(self) -> None:
        object.__setattr__(self, "species_id", _text(self.species_id, "species_id"))
        object.__setattr__(self, "statement", _text(self.statement, "statement"))
        object.__setattr__(self, "proof_sha256", _sha(self.proof_sha256, "proof_sha256"))
        if not isinstance(self.authority, HashRef):
            raise TypeError("authority must be a HashRef")


@dataclass(frozen=True, slots=True)
class SpeciesKinematicJet:
    species_id: str
    beta_normal: tuple[float, float, float]
    dbeta_normal_dtau: tuple[float, float, float]
    tau: float
    coordinate_sha256: str
    provenance: HashRef

    def __post_init__(self) -> None:
        object.__setattr__(self, "species_id", _text(self.species_id, "species_id"))
        object.__setattr__(
            self, "beta_normal", _validate_beta(self.beta_normal, "beta_normal")
        )
        object.__setattr__(
            self,
            "dbeta_normal_dtau",
            _vec3(self.dbeta_normal_dtau, "dbeta_normal_dtau"),
        )
        object.__setattr__(self, "tau", _finite(self.tau, "tau"))
        object.__setattr__(
            self,
            "coordinate_sha256",
            _sha(self.coordinate_sha256, "coordinate_sha256"),
        )
        if not isinstance(self.provenance, HashRef):
            raise TypeError("provenance must be a HashRef")


class DerivativeSide(Enum):
    INTERIOR = "interior"
    LEFT = "left"
    RIGHT = "right"


@dataclass(frozen=True, slots=True)
class IndependentElectronState:
    proper_density_m3: float
    beta_normal: tuple[float, float, float]
    schedule_payload_sha256: str
    source: HashRef
    closure: str = field(init=False, default="independent-electron-test-field")


@dataclass(frozen=True, slots=True)
class ComovingWithMatterSpecies:
    proper_density_m3: float
    beta_normal: tuple[float, float, float]
    species_id: str
    plasma_identity_sha256: str
    equality_proof_sha256: str
    schedule_payload_sha256: str
    closure: str = field(init=False, default="comoving-with-named-plasma-species")


@dataclass(frozen=True, slots=True)
class CollisionOff:
    reason: str
    schedule_payload_sha256: str
    kappa: float = field(init=False, default=0.0)
    beta_normal: None = field(init=False, default=None)
    closure: str = field(init=False, default="collision-off")

    def __post_init__(self) -> None:
        object.__setattr__(self, "reason", _text(self.reason, "reason"))
        object.__setattr__(
            self,
            "schedule_payload_sha256",
            _sha(self.schedule_payload_sha256, "schedule_payload_sha256"),
        )


@dataclass(frozen=True, slots=True)
class ElectronStateJet:
    tau: float
    proper_density_m3: float
    beta_normal: tuple[float, float, float]
    dproper_density_dtau: float
    dbeta_normal_dtau: tuple[float, float, float]
    segment_index: int
    derivative_side: DerivativeSide
    closure: str
    schedule_payload_sha256: str


@dataclass(frozen=True, slots=True)
class ElectronBindingCertificate:
    state: IndependentElectronState | ComovingWithMatterSpecies | CollisionOff
    jet: ElectronStateJet | None
    coordinate_sha256: str
    binding_sha256: str
    metadata: Mapping[str, Any]

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "coordinate_sha256", _sha(self.coordinate_sha256, "coordinate_sha256")
        )
        object.__setattr__(
            self, "binding_sha256", _sha(self.binding_sha256, "binding_sha256")
        )
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


@dataclass(frozen=True, slots=True)
class _ScheduleView:
    nodes: tuple[float, ...]
    interpolation: str
    number_currents: tuple[tuple[float, float, float, float], ...] | None
    densities: tuple[float, ...] | None
    source: HashRef
    payload_sha256: str


def _read_schedule_view(schedule: Any) -> _ScheduleView:
    if not hasattr(schedule, "trajectory_view") or not callable(schedule.trajectory_view):
        raise TypeError("schedule must expose trajectory_view()")
    if not hasattr(schedule, "payload_sha256"):
        raise TypeError("schedule must expose payload_sha256")
    view = schedule.trajectory_view()

    payload = _sha(schedule.payload_sha256, "schedule.payload_sha256")
    view_payload = _sha(view.schedule_payload_sha256, "view.schedule_payload_sha256")
    if payload != view_payload:
        raise ValueError("schedule payload does not match trajectory-view payload")
    if getattr(view, "coordinate_kind", None) != "q_hubble_time_tau":
        raise ValueError("schedule view must use q_hubble_time_tau")
    if float(getattr(view, "c_m_s", math.nan)) != _C_LIGHT_M_S:
        raise ValueError("schedule view must retain exact SI c")

    raw_nodes = tuple(_finite(value, "trajectory node") for value in view.nodes_ascending)
    if len(raw_nodes) < 2:
        raise ValueError("trajectory needs at least two nodes")
    if any(right <= left for left, right in zip(raw_nodes[:-1], raw_nodes[1:])):
        raise ValueError("trajectory nodes must be strictly increasing")

    interpolation = _text(view.interpolation, "interpolation")
    source = HashRef(
        _text(view.source_id, "view.source_id"),
        _sha(view.source_sha256, "view.source_sha256"),
    )

    if interpolation == "linear_number_current_v1":
        if view.number_current_nodes is None or view.density_nodes_m3 is not None:
            raise ValueError("independent schedule view has inconsistent carrier fields")
        currents: list[tuple[float, float, float, float]] = []
        for row in view.number_current_nodes:
            values = tuple(_finite(value, "number-current component") for value in row)
            if len(values) != 4:
                raise ValueError("number-current rows must have four components")
            currents.append(values)  # type: ignore[arg-type]
        if len(currents) != len(raw_nodes):
            raise ValueError("number-current knots must match trajectory nodes")
        return _ScheduleView(raw_nodes, interpolation, tuple(currents), None, source, payload)

    if interpolation == "linear_proper_density_live_fluid_beta":
        if view.density_nodes_m3 is None or view.number_current_nodes is not None:
            raise ValueError("comoving schedule view has inconsistent carrier fields")
        densities = tuple(_finite(value, "proper-density knot") for value in view.density_nodes_m3)
        if len(densities) != len(raw_nodes):
            raise ValueError("density knots must match trajectory nodes")
        if any(value < 0.0 for value in densities):
            raise ValueError("proper-density knots must be non-negative")
        return _ScheduleView(raw_nodes, interpolation, None, densities, source, payload)

    raise ValueError(f"unsupported interpolation: {interpolation}")


def _select_segment(
    nodes: tuple[float, ...], tau: float, side: DerivativeSide | None
) -> tuple[int, DerivativeSide]:
    query = _finite(tau, "tau")
    if query < nodes[0] or query > nodes[-1]:
        raise ValueError(
            f"tau={query} lies outside closed support [{nodes[0]}, {nodes[-1]}]"
        )
    if side is not None and not isinstance(side, DerivativeSide):
        raise TypeError("side must be a DerivativeSide")

    knot = next((index for index, value in enumerate(nodes) if query == value), None)
    if knot is None:
        if side not in (None, DerivativeSide.INTERIOR):
            raise ValueError("LEFT/RIGHT side is valid only at an exact knot")
        for index, (left, right) in enumerate(zip(nodes[:-1], nodes[1:])):
            if left < query < right:
                return index, DerivativeSide.INTERIOR
        raise RuntimeError("failed to locate open trajectory segment")

    if knot == 0:
        if side is not DerivativeSide.RIGHT:
            raise ValueError("the first knot requires explicit RIGHT derivative side")
        return 0, DerivativeSide.RIGHT
    if knot == len(nodes) - 1:
        if side is not DerivativeSide.LEFT:
            raise ValueError("the last knot requires explicit LEFT derivative side")
        return len(nodes) - 2, DerivativeSide.LEFT
    if side not in (DerivativeSide.LEFT, DerivativeSide.RIGHT):
        raise ValueError("an interior knot requires explicit LEFT or RIGHT derivative side")
    return (knot - 1, side) if side is DerivativeSide.LEFT else (knot, side)


def _affine_fraction(
    left: float, right: float, node_left: float, node_right: float, tau: float
) -> tuple[Fraction, Fraction]:
    t0 = _fraction(node_left, "node_left")
    t1 = _fraction(node_right, "node_right")
    query = _fraction(tau, "tau")
    width = t1 - t0
    if width <= 0:
        raise ValueError("segment width must be positive")
    slope = (_fraction(right, "right value") - _fraction(left, "left value")) / width
    value = _fraction(left, "left value") + (query - t0) * slope
    return value, slope


def _independent_jet(
    view: _ScheduleView,
    tau: float,
    segment: int,
    derivative_side: DerivativeSide,
) -> tuple[IndependentElectronState | CollisionOff, ElectronStateJet | None]:
    assert view.number_currents is not None
    left = view.number_currents[segment]
    right = view.number_currents[segment + 1]
    values: list[Fraction] = []
    slopes: list[Fraction] = []
    for component_left, component_right in zip(left, right):
        value, slope = _affine_fraction(
            component_left,
            component_right,
            view.nodes[segment],
            view.nodes[segment + 1],
            tau,
        )
        values.append(value)
        slopes.append(slope)

    if all(value == 0 for value in values):
        return (
            CollisionOff("exact-vacuum-electron-current", view.payload_sha256),
            None,
        )

    temporal = values[0]
    spatial = values[1:]
    if temporal <= 0:
        raise ValueError("electron number current must be future-timelike with N0>0")
    norm2 = temporal * temporal - sum(component * component for component in spatial)
    if norm2 <= 0:
        raise ValueError("electron number current must be future-timelike")

    density = _sqrt_fraction(norm2)
    beta_fraction = tuple(component / temporal for component in spatial)
    beta = tuple(float(component) for component in beta_fraction)
    _validate_beta(beta, "derived beta_normal")

    numerator = temporal * slopes[0] - sum(
        component * slope for component, slope in zip(spatial, slopes[1:])
    )
    dn = float(numerator) / density
    dbeta_fraction = tuple(
        (slope * temporal - component * slopes[0]) / (temporal * temporal)
        for component, slope in zip(spatial, slopes[1:])
    )
    dbeta = tuple(float(component) for component in dbeta_fraction)
    if not math.isfinite(dn) or not all(math.isfinite(value) for value in dbeta):
        raise ValueError("state-jet conversion overflowed binary64")

    state = IndependentElectronState(
        proper_density_m3=density,
        beta_normal=beta,
        schedule_payload_sha256=view.payload_sha256,
        source=view.source,
    )
    jet = ElectronStateJet(
        tau=float(tau),
        proper_density_m3=density,
        beta_normal=beta,
        dproper_density_dtau=dn,
        dbeta_normal_dtau=dbeta,
        segment_index=segment,
        derivative_side=derivative_side,
        closure=state.closure,
        schedule_payload_sha256=view.payload_sha256,
    )
    return state, jet


def _validate_comoving_proofs(
    *,
    species_jet: SpeciesKinematicJet | None,
    plasma_identity: PlasmaIdentity | None,
    equality_proof: VelocityEqualityProof | None,
    coordinate: QHubbleTimeAuthority,
    tau: float,
) -> tuple[SpeciesKinematicJet, PlasmaIdentity, VelocityEqualityProof]:
    if species_jet is None:
        raise ValueError("positive-density comoving binding requires species_jet")
    if plasma_identity is None:
        raise ValueError("positive-density comoving binding requires plasma_identity")
    if equality_proof is None:
        raise ValueError("positive-density comoving binding requires equality_proof")
    if not isinstance(species_jet, SpeciesKinematicJet):
        raise TypeError("species_jet must be a SpeciesKinematicJet")
    if not isinstance(plasma_identity, PlasmaIdentity):
        raise TypeError("plasma_identity must be a PlasmaIdentity")
    if not isinstance(equality_proof, VelocityEqualityProof):
        raise TypeError("equality_proof must be a VelocityEqualityProof")
    ids = {species_jet.species_id, plasma_identity.species_id, equality_proof.species_id}
    if len(ids) != 1:
        raise ValueError("species_id mismatch across comoving authority objects")
    if equality_proof.statement != "u_e_equals_u_species":
        raise ValueError("equality proof must state u_e_equals_u_species")
    if plasma_identity.plasma_model != _CANONICAL_PLASMA_MODEL:
        raise ValueError(
            "comoving branch requires cold-ionized-baryon-electron-plasma identity"
        )
    if species_jet.coordinate_sha256 != coordinate.payload_sha256:
        raise ValueError("species jet coordinate authority mismatch")
    if species_jet.tau != float(tau):
        raise ValueError("species jet tau must equal electron-state query tau exactly")
    return species_jet, plasma_identity, equality_proof


def _comoving_jet(
    view: _ScheduleView,
    tau: float,
    segment: int,
    derivative_side: DerivativeSide,
    *,
    coordinate: QHubbleTimeAuthority,
    species_jet: SpeciesKinematicJet | None,
    plasma_identity: PlasmaIdentity | None,
    equality_proof: VelocityEqualityProof | None,
) -> tuple[ComovingWithMatterSpecies | CollisionOff, ElectronStateJet | None]:
    assert view.densities is not None
    density_fraction, density_slope = _affine_fraction(
        view.densities[segment],
        view.densities[segment + 1],
        view.nodes[segment],
        view.nodes[segment + 1],
        tau,
    )
    if density_fraction < 0:
        raise ValueError("interpolated proper density became negative")
    if density_fraction == 0:
        return CollisionOff("exact-vacuum-proper-density", view.payload_sha256), None

    species, identity, proof = _validate_comoving_proofs(
        species_jet=species_jet,
        plasma_identity=plasma_identity,
        equality_proof=equality_proof,
        coordinate=coordinate,
        tau=tau,
    )
    density = float(density_fraction)
    dn = float(density_slope)
    if not math.isfinite(density) or not math.isfinite(dn):
        raise ValueError("comoving density jet overflowed binary64")

    identity_hash = _canonical_hash(
        "bass.plasma_identity/v1",
        {
            "species_id": identity.species_id,
            "plasma_model": identity.plasma_model,
            "source_id": identity.provenance.source_id,
            "source_sha256": identity.provenance.source_sha256,
        },
    )
    state = ComovingWithMatterSpecies(
        proper_density_m3=density,
        beta_normal=species.beta_normal,
        species_id=species.species_id,
        plasma_identity_sha256=identity_hash,
        equality_proof_sha256=proof.proof_sha256,
        schedule_payload_sha256=view.payload_sha256,
    )
    jet = ElectronStateJet(
        tau=float(tau),
        proper_density_m3=density,
        beta_normal=species.beta_normal,
        dproper_density_dtau=dn,
        dbeta_normal_dtau=species.dbeta_normal_dtau,
        segment_index=segment,
        derivative_side=derivative_side,
        closure=state.closure,
        schedule_payload_sha256=view.payload_sha256,
    )
    return state, jet


def _certificate_metadata(state: Any, jet: ElectronStateJet | None) -> Mapping[str, Any]:
    has_jet = jet is not None
    return {
        "schema": "bass.electron_state_binding_certificate/v1",
        "metric_signature": "(-,+,+,+)",
        "coordinate": "q_hubble_time_tau",
        "generic_three_vector_schema": True,
        "typeii_special_case_implemented": False,
        "typed_decision_union": True,
        "state_jet_present": has_jet,
        "ad_jvp_certified": has_jet,
        "ad_jvp_scope": (
            "analytic_q_time_tangent_of_declared_affine_segment_or_explicit_knot_side"
            if has_jet
            else "none_on_collision_off_quotient"
        ),
        "generic_solver_jvp_certified": False,
        "direction_dependent_rate_bound": False,
        "finite_radiation_carrier_bound": False,
        "projector_bound": False,
        "paired_left_functional_bound": False,
        "production_runtime_wired": False,
        "authority_row_promoted": False,
        "state_closure": state.closure,
    }


def bind_electron_state(
    schedule: Any,
    *,
    tau: float,
    coordinate: QHubbleTimeAuthority,
    binding_provenance: HashRef,
    side: DerivativeSide | None = None,
    species_jet: SpeciesKinematicJet | None = None,
    plasma_identity: PlasmaIdentity | None = None,
    equality_proof: VelocityEqualityProof | None = None,
) -> ElectronBindingCertificate:
    """Bind one E1--E4 schedule state to a typed decision and exact time jet.

    The function consumes only the public ``trajectory_view`` and payload hash.
    It does not call or replace private interpolation routines.  The derivative
    is selected from the exact declared affine segment.  At a knot, the caller
    must select a one-sided derivative; exact vacuum returns ``CollisionOff``.
    """
    if not isinstance(coordinate, QHubbleTimeAuthority):
        raise TypeError("coordinate must be a QHubbleTimeAuthority")
    if not isinstance(binding_provenance, HashRef):
        raise TypeError("binding_provenance must be a HashRef")

    query = _finite(tau, "tau")
    view = _read_schedule_view(schedule)
    segment, derivative_side = _select_segment(view.nodes, query, side)

    if view.interpolation == "linear_number_current_v1":
        if any(value is not None for value in (species_jet, plasma_identity, equality_proof)):
            raise ValueError("independent schedule rejects comoving species authority objects")
        state, jet = _independent_jet(view, query, segment, derivative_side)
    elif view.interpolation == "linear_proper_density_live_fluid_beta":
        state, jet = _comoving_jet(
            view,
            query,
            segment,
            derivative_side,
            coordinate=coordinate,
            species_jet=species_jet,
            plasma_identity=plasma_identity,
            equality_proof=equality_proof,
        )
    else:  # guarded by _read_schedule_view
        raise RuntimeError("unreachable interpolation branch")

    metadata = _certificate_metadata(state, jet)
    payload: dict[str, Any] = {
        "coordinate_sha256": coordinate.payload_sha256,
        "binding_source_id": binding_provenance.source_id,
        "binding_source_sha256": binding_provenance.source_sha256,
        "schedule_payload_sha256": view.payload_sha256,
        "schedule_source_id": view.source.source_id,
        "schedule_source_sha256": view.source.source_sha256,
        "tau_hex": query.hex(),
        "state_closure": state.closure,
        "segment_index": None if jet is None else jet.segment_index,
        "derivative_side": None if jet is None else jet.derivative_side.value,
        "proper_density_hex": (
            None if jet is None else float(jet.proper_density_m3).hex()
        ),
        "beta_hex": None if jet is None else [float(x).hex() for x in jet.beta_normal],
        "dn_hex": None if jet is None else float(jet.dproper_density_dtau).hex(),
        "dbeta_hex": (
            None if jet is None else [float(x).hex() for x in jet.dbeta_normal_dtau]
        ),
        "metadata": dict(metadata),
    }
    binding_sha = _canonical_hash("bass.electron_state_binding/v1", payload)
    return ElectronBindingCertificate(
        state=state,
        jet=jet,
        coordinate_sha256=coordinate.payload_sha256,
        binding_sha256=binding_sha,
        metadata=metadata,
    )


__all__ = [
    "CollisionOff",
    "ComovingWithMatterSpecies",
    "DerivativeSide",
    "ElectronBindingCertificate",
    "ElectronStateJet",
    "HashRef",
    "IndependentElectronState",
    "PlasmaIdentity",
    "QHubbleTimeAuthority",
    "SpeciesKinematicJet",
    "VelocityEqualityProof",
    "bind_electron_state",
]
