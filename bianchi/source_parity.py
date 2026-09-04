"""Certified finite-rank scalar angular projection for BASS source parity.

This module supplies one bounded, dependency-light bridge between the qualified
R8 full-grid and spectral-coefficient source adapters.  It fixes a real,
orthonormal, Condon--Shortley spherical-harmonic convention on ``dOmega`` and a
Gauss--Legendre x uniform-azimuth quadrature that is sufficient for an
angularly constant source at the declared finite work rank.

The implementation does not wire a source into a solver, does not multiply by
an angularly varying source, and does not define a radial, integrated-state, or
polarized closure.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import math
import re
from typing import Final

from bianchi.source_adapters import (
    SourceApplicationReceipt,
    SourceTimeBasis,
    apply_constant_pair_to_full_spectral_grid,
    apply_constant_pair_to_spectral_pstf,
)
from bianchi.source_authority import SourceAuthorityBundle

__all__ = [
    "RealSphericalHarmonicConvention",
    "SourceTimeBasis",
    "SphereQuadrature",
    "SourceParityContract",
    "SourceParityError",
    "SourceParityReport",
    "build_gauss_legendre_uniform_phi_quadrature",
    "canonical_real_harmonic_modes",
    "compare_constant_pair_grid_and_pstf",
    "project_real_spherical_harmonics",
    "synthesize_real_spherical_harmonics",
    "unit_field_coefficients",
]

_SHA256_RE: Final[re.Pattern[str]] = re.compile(r"[0-9a-f]{64}\Z")
_QUADRATURE_SCHEMA: Final[str] = "bass.source_parity.sphere_quadrature.v1"
_CONTRACT_SCHEMA: Final[str] = "bass.source_parity.contract.v1"
_REPORT_SCHEMA: Final[str] = "bass.source_parity.report.v1"
_MODE_M0: Final[str] = "m0"
_MODE_COS: Final[str] = "cos"
_MODE_SIN: Final[str] = "sin"

RealHarmonicMode = tuple[int, int, str]


class SourceParityError(ValueError):
    """Raised when a finite-rank parity contract is invalid or violated."""


class RealSphericalHarmonicConvention(str, Enum):
    """Scalar real-harmonic convention implemented by this bounded bridge."""

    ORTHONORMAL_DOMEGA_CONDON_SHORTLEY = (
        "real_orthonormal_domega_condon_shortley"
    )


def _nonnegative_integer(value: object, *, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise SourceParityError(f"{name} must be a nonnegative integer")
    if value < 0:
        raise SourceParityError(f"{name} must be nonnegative")
    return value


def _positive_integer(value: object, *, name: str) -> int:
    result = _nonnegative_integer(value, name=name)
    if result == 0:
        raise SourceParityError(f"{name} must be positive")
    return result


def _finite_scalar(
    value: object,
    *,
    name: str,
    nonnegative: bool = False,
) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SourceParityError(f"{name} must be a real scalar")
    try:
        result = float(value)
    except (OverflowError, ValueError) as exc:
        raise SourceParityError(f"{name} is not representable as binary64") from exc
    if not math.isfinite(result):
        raise SourceParityError(f"{name} must be finite")
    if nonnegative and result < 0.0:
        raise SourceParityError(f"{name} must be nonnegative")
    return 0.0 if result == 0.0 else result


def _finite_vector(
    values: object,
    *,
    name: str,
    expected_length: int | None = None,
) -> tuple[float, ...]:
    if isinstance(values, (str, bytes, bytearray)):
        raise SourceParityError(f"{name} must be an iterable of real scalars")
    try:
        raw = tuple(values)  # type: ignore[arg-type]
    except TypeError as exc:
        raise SourceParityError(
            f"{name} must be an iterable of real scalars"
        ) from exc
    if expected_length is not None and len(raw) != expected_length:
        raise SourceParityError(
            f"{name} must contain exactly {expected_length} values, got {len(raw)}"
        )
    if not raw:
        raise SourceParityError(f"{name} must be nonempty")
    return tuple(
        _finite_scalar(value, name=f"{name}[{index}]")
        for index, value in enumerate(raw)
    )


def _sha256_text(value: object, *, name: str) -> str:
    if not isinstance(value, str) or _SHA256_RE.fullmatch(value) is None:
        raise SourceParityError(
            f"{name} must be exactly 64 lowercase hexadecimal characters"
        )
    return value


def _canonical_sha256(payload: object) -> str:
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    return hashlib.sha256(canonical).hexdigest()


def canonical_real_harmonic_modes(l_max: object) -> tuple[RealHarmonicMode, ...]:
    """Return the locked real-harmonic coefficient order through ``l_max``."""

    maximum = _nonnegative_integer(l_max, name="l_max")
    modes: list[RealHarmonicMode] = []
    for ell in range(maximum + 1):
        modes.append((ell, 0, _MODE_M0))
        for order in range(1, ell + 1):
            modes.append((ell, order, _MODE_COS))
            modes.append((ell, order, _MODE_SIN))
    expected = (maximum + 1) ** 2
    if len(modes) != expected:
        raise SourceParityError("internal real-harmonic mode count is inconsistent")
    return tuple(modes)


def unit_field_coefficients(l_max: object) -> tuple[float, ...]:
    """Coefficients of the constant field one in the locked ``dOmega`` basis."""

    maximum = _nonnegative_integer(l_max, name="l_max")
    values = [0.0] * ((maximum + 1) ** 2)
    values[0] = math.sqrt(4.0 * math.pi)
    return tuple(values)


def _gauss_legendre_rule(order: int) -> tuple[tuple[float, ...], tuple[float, ...]]:
    """Compute a deterministic Gauss--Legendre rule on [-1,1]."""

    n = _positive_integer(order, name="n_mu")
    nodes = [0.0] * n
    weights = [0.0] * n
    half = (n + 1) // 2

    for index in range(half):
        root = math.cos(math.pi * (index + 0.75) / (n + 0.5))
        converged = False
        for _ in range(100):
            p_nm2 = 1.0
            p_nm1 = root
            if n == 1:
                p_n = root
                p_n_minus_1 = 1.0
            else:
                for degree in range(2, n + 1):
                    p_n = (
                        (2.0 * degree - 1.0) * root * p_nm1
                        - (degree - 1.0) * p_nm2
                    ) / degree
                    p_nm2, p_nm1 = p_nm1, p_n
                p_n_minus_1 = p_nm2
            derivative = n * (root * p_n - p_n_minus_1) / (root * root - 1.0)
            updated = root - p_n / derivative
            if abs(updated - root) <= 4.0 * math.ulp(1.0):
                root = updated
                converged = True
                break
            root = updated
        if not converged:
            raise SourceParityError("Gauss--Legendre root iteration did not converge")

        p_nm2 = 1.0
        p_nm1 = root
        if n == 1:
            p_n = root
            p_n_minus_1 = 1.0
        else:
            for degree in range(2, n + 1):
                p_n = (
                    (2.0 * degree - 1.0) * root * p_nm1
                    - (degree - 1.0) * p_nm2
                ) / degree
                p_nm2, p_nm1 = p_nm1, p_n
            p_n_minus_1 = p_nm2
        derivative = n * (root * p_n - p_n_minus_1) / (root * root - 1.0)
        weight = 2.0 / ((1.0 - root * root) * derivative * derivative)

        if abs(root) <= 8.0 * math.ulp(1.0):
            root = 0.0
        nodes[index] = -root
        nodes[n - 1 - index] = root
        weights[index] = weight
        weights[n - 1 - index] = weight

    paired = sorted(zip(nodes, weights, strict=True), key=lambda item: item[0])
    return (
        tuple(0.0 if node == 0.0 else node for node, _ in paired),
        tuple(weight for _, weight in paired),
    )


def _associated_legendre(ell: int, order: int, mu: float) -> float:
    """Condon--Shortley associated Legendre function P_ell^order(mu)."""

    if order < 0 or order > ell:
        raise SourceParityError("associated-Legendre order is outside its rank")
    one_minus_mu2 = max(0.0, 1.0 - mu * mu)
    p_mm = 1.0
    if order > 0:
        factor = -1.0
        root = math.sqrt(one_minus_mu2)
        for _ in range(1, order + 1):
            p_mm *= factor * root
            factor -= 2.0
    if ell == order:
        return p_mm
    p_m1m = mu * (2.0 * order + 1.0) * p_mm
    if ell == order + 1:
        return p_m1m
    p_lm2 = p_mm
    p_lm1 = p_m1m
    for degree in range(order + 2, ell + 1):
        p_lm = (
            (2.0 * degree - 1.0) * mu * p_lm1
            - (degree + order - 1.0) * p_lm2
        ) / (degree - order)
        p_lm2, p_lm1 = p_lm1, p_lm
    return p_lm1


def _complex_harmonic_normalization(ell: int, order: int) -> float:
    log_ratio = math.lgamma(ell - order + 1.0) - math.lgamma(
        ell + order + 1.0
    )
    return math.sqrt((2.0 * ell + 1.0) / (4.0 * math.pi)) * math.exp(
        0.5 * log_ratio
    )


def _real_harmonic(mode: RealHarmonicMode, mu: float, phi: float) -> float:
    ell, order, component = mode
    radial = _complex_harmonic_normalization(
        ell, order
    ) * _associated_legendre(ell, order, mu)
    if order == 0:
        if component != _MODE_M0:
            raise SourceParityError("m=0 modes must use the m0 component label")
        return radial
    if component == _MODE_COS:
        return math.sqrt(2.0) * radial * math.cos(order * phi)
    if component == _MODE_SIN:
        return math.sqrt(2.0) * radial * math.sin(order * phi)
    raise SourceParityError("positive-m modes must use cos or sin component labels")


@dataclass(frozen=True, slots=True, init=False)
class SphereQuadrature:
    """Hash-bound tensor-product rule for one declared finite work rank."""

    convention: RealSphericalHarmonicConvention
    l_work: int
    n_mu: int
    n_phi: int
    mu: tuple[float, ...]
    mu_weights: tuple[float, ...]
    phi: tuple[float, ...]
    phi_weights: tuple[float, ...]
    projection_contract_sha256: str

    def __init__(self, *args: object, **kwargs: object) -> None:
        raise TypeError("use SphereQuadrature.create")

    @classmethod
    def create(
        cls,
        *,
        l_work: object,
        n_mu: object,
        n_phi: object,
    ) -> "SphereQuadrature":
        work = _nonnegative_integer(l_work, name="l_work")
        latitude_count = _positive_integer(n_mu, name="n_mu")
        azimuth_count = _positive_integer(n_phi, name="n_phi")
        required_mu = work + 1
        required_phi = 2 * work + 1
        if latitude_count < required_mu:
            raise SourceParityError(
                "underresolved Gauss--Legendre rule: "
                f"n_mu={latitude_count}, required>={required_mu}"
            )
        if azimuth_count < required_phi:
            raise SourceParityError(
                "underresolved azimuth rule: "
                f"n_phi={azimuth_count}, required>={required_phi}"
            )

        mu, mu_weights = _gauss_legendre_rule(latitude_count)
        phi = tuple(
            2.0 * math.pi * index / azimuth_count
            for index in range(azimuth_count)
        )
        phi_weight = 2.0 * math.pi / azimuth_count
        phi_weights = tuple(phi_weight for _ in range(azimuth_count))
        convention = (
            RealSphericalHarmonicConvention.ORTHONORMAL_DOMEGA_CONDON_SHORTLEY
        )
        modes = canonical_real_harmonic_modes(work)
        unit = unit_field_coefficients(work)
        payload = {
            "convention": convention.value,
            "l_work": work,
            "measure": "dOmega",
            "mode_order": [list(mode) for mode in modes],
            "mu_hex": [value.hex() for value in mu],
            "mu_rule": "gauss_legendre",
            "mu_weight_hex": [value.hex() for value in mu_weights],
            "n_mu": latitude_count,
            "n_phi": azimuth_count,
            "phi_hex": [value.hex() for value in phi],
            "phi_rule": "uniform_periodic",
            "phi_weight_hex": [value.hex() for value in phi_weights],
            "schema": _QUADRATURE_SCHEMA,
            "unit_field_hex": [value.hex() for value in unit],
        }
        identity = _canonical_sha256(payload)

        instance = object.__new__(cls)
        object.__setattr__(instance, "convention", convention)
        object.__setattr__(instance, "l_work", work)
        object.__setattr__(instance, "n_mu", latitude_count)
        object.__setattr__(instance, "n_phi", azimuth_count)
        object.__setattr__(instance, "mu", mu)
        object.__setattr__(instance, "mu_weights", mu_weights)
        object.__setattr__(instance, "phi", phi)
        object.__setattr__(instance, "phi_weights", phi_weights)
        object.__setattr__(instance, "projection_contract_sha256", identity)
        return instance


def build_gauss_legendre_uniform_phi_quadrature(
    *,
    l_work: object,
) -> SphereQuadrature:
    """Build the minimal sufficient tensor-product rule at ``l_work``."""

    work = _nonnegative_integer(l_work, name="l_work")
    return SphereQuadrature.create(
        l_work=work,
        n_mu=work + 1,
        n_phi=2 * work + 1,
    )


def _validated_quadrature(
    quadrature: object,
    *,
    minimum_rank: int,
) -> SphereQuadrature:
    if not isinstance(quadrature, SphereQuadrature):
        raise SourceParityError("quadrature must be a SphereQuadrature")
    if quadrature.l_work < minimum_rank:
        raise SourceParityError(
            "quadrature work rank is smaller than the requested harmonic rank"
        )
    if len(quadrature.mu) != quadrature.n_mu or len(
        quadrature.mu_weights
    ) != quadrature.n_mu:
        raise SourceParityError("quadrature latitude arrays are inconsistent")
    if len(quadrature.phi) != quadrature.n_phi or len(
        quadrature.phi_weights
    ) != quadrature.n_phi:
        raise SourceParityError("quadrature azimuth arrays are inconsistent")
    return quadrature


def synthesize_real_spherical_harmonics(
    coefficients: object,
    *,
    l_max: object,
    quadrature: SphereQuadrature,
) -> tuple[float, ...]:
    """Synthesize locked real-harmonic coefficients on a certified grid."""

    maximum = _nonnegative_integer(l_max, name="l_max")
    rule = _validated_quadrature(quadrature, minimum_rank=maximum)
    modes = canonical_real_harmonic_modes(maximum)
    vector = _finite_vector(
        coefficients,
        name="coefficients",
        expected_length=len(modes),
    )
    samples: list[float] = []
    for mu in rule.mu:
        for phi in rule.phi:
            value = math.fsum(
                coefficient * _real_harmonic(mode, mu, phi)
                for coefficient, mode in zip(vector, modes, strict=True)
            )
            if not math.isfinite(value):
                raise SourceParityError("harmonic synthesis produced a nonfinite value")
            samples.append(0.0 if value == 0.0 else value)
    return tuple(samples)


def project_real_spherical_harmonics(
    samples: object,
    *,
    l_max: object,
    quadrature: SphereQuadrature,
) -> tuple[float, ...]:
    """Project grid samples onto the locked real-harmonic coefficients."""

    maximum = _nonnegative_integer(l_max, name="l_max")
    rule = _validated_quadrature(quadrature, minimum_rank=maximum)
    values = _finite_vector(
        samples,
        name="samples",
        expected_length=rule.n_mu * rule.n_phi,
    )
    modes = canonical_real_harmonic_modes(maximum)
    coefficients: list[float] = []
    for mode in modes:
        terms: list[float] = []
        sample_index = 0
        for mu, mu_weight in zip(rule.mu, rule.mu_weights, strict=True):
            for phi, phi_weight in zip(
                rule.phi, rule.phi_weights, strict=True
            ):
                terms.append(
                    values[sample_index]
                    * _real_harmonic(mode, mu, phi)
                    * mu_weight
                    * phi_weight
                )
                sample_index += 1
        coefficient = math.fsum(terms)
        if not math.isfinite(coefficient):
            raise SourceParityError("harmonic projection produced a nonfinite value")
        coefficients.append(0.0 if coefficient == 0.0 else coefficient)
    return tuple(coefficients)


@dataclass(frozen=True, slots=True)
class SourceParityContract:
    """Canonical identity of one finite-rank parity comparison."""

    contract_schema: str
    convention: RealSphericalHarmonicConvention
    l_out: int
    l_work: int
    compared_coefficients: int
    projection_contract_sha256: str
    state_parent_sha256: str
    grid_representation_sha256: str
    pstf_representation_sha256: str
    source_payload_sha256: str
    atol_hex: str
    rtol_hex: str
    contract_sha256: str


@dataclass(frozen=True, slots=True)
class SourceParityReport:
    """Numerical comparison and immutable provenance for the two R8 routes."""

    report_schema: str
    contract: SourceParityContract
    time_basis: SourceTimeBasis
    rate_divisor_hex: str
    compared_coefficients: int
    grid_projected: tuple[float, ...]
    pstf_values: tuple[float, ...]
    residuals: tuple[float, ...]
    max_abs_residual: float
    max_rel_residual: float
    pass_parity: bool
    grid_receipt: SourceApplicationReceipt
    pstf_receipt: SourceApplicationReceipt
    report_sha256: str


def _build_contract(
    *,
    source: SourceAuthorityBundle,
    l_out: int,
    l_work: int,
    quadrature: SphereQuadrature,
    state_parent_sha256: str,
    grid_representation_sha256: str,
    pstf_representation_sha256: str,
    atol: float,
    rtol: float,
) -> SourceParityContract:
    payload = {
        "atol_hex": atol.hex(),
        "compared_coefficients": (l_out + 1) ** 2,
        "convention": quadrature.convention.value,
        "grid_representation_sha256": grid_representation_sha256,
        "l_out": l_out,
        "l_work": l_work,
        "projection_contract_sha256": quadrature.projection_contract_sha256,
        "pstf_representation_sha256": pstf_representation_sha256,
        "rtol_hex": rtol.hex(),
        "schema": _CONTRACT_SCHEMA,
        "source_payload_sha256": source.payload_sha256,
        "state_parent_sha256": state_parent_sha256,
    }
    identity = _canonical_sha256(payload)
    return SourceParityContract(
        contract_schema=_CONTRACT_SCHEMA,
        convention=quadrature.convention,
        l_out=l_out,
        l_work=l_work,
        compared_coefficients=(l_out + 1) ** 2,
        projection_contract_sha256=quadrature.projection_contract_sha256,
        state_parent_sha256=state_parent_sha256,
        grid_representation_sha256=grid_representation_sha256,
        pstf_representation_sha256=pstf_representation_sha256,
        source_payload_sha256=source.payload_sha256,
        atol_hex=atol.hex(),
        rtol_hex=rtol.hex(),
        contract_sha256=identity,
    )


def compare_constant_pair_grid_and_pstf(
    source: SourceAuthorityBundle,
    coefficients: object,
    *,
    l_out: object,
    l_work: object,
    state_parent_sha256: object,
    grid_representation_sha256: object,
    pstf_representation_sha256: object,
    time_basis: SourceTimeBasis,
    H_s_inv: object | None = None,
    c_m_s: object | None = None,
    quadrature: SphereQuadrature | None = None,
    projection_contract_sha256: object | None = None,
    unit_field_coefficients: object | None = None,
    atol: object = 2.0e-13,
    rtol: object = 2.0e-13,
    require_pass: bool = True,
) -> SourceParityReport:
    """Compare grid-project and direct-coefficient actions of one source pair."""

    if not isinstance(source, SourceAuthorityBundle):
        raise SourceParityError("source must be a SourceAuthorityBundle")
    output_rank = _nonnegative_integer(l_out, name="l_out")
    work_rank = _nonnegative_integer(l_work, name="l_work")
    if work_rank < output_rank:
        raise SourceParityError("l_work must be at least l_out")
    expected_count = (output_rank + 1) ** 2
    state_coefficients = _finite_vector(
        coefficients,
        name="coefficients",
        expected_length=expected_count,
    )
    parent_identity = _sha256_text(
        state_parent_sha256,
        name="state_parent_sha256",
    )
    grid_identity = _sha256_text(
        grid_representation_sha256,
        name="grid_representation_sha256",
    )
    pstf_identity = _sha256_text(
        pstf_representation_sha256,
        name="pstf_representation_sha256",
    )
    if grid_identity == pstf_identity:
        raise SourceParityError("grid and PSTF representation identities must differ")
    absolute_tolerance = _finite_scalar(atol, name="atol", nonnegative=True)
    relative_tolerance = _finite_scalar(rtol, name="rtol", nonnegative=True)
    if not isinstance(require_pass, bool):
        raise SourceParityError("require_pass must be bool")

    rule = (
        build_gauss_legendre_uniform_phi_quadrature(l_work=work_rank)
        if quadrature is None
        else _validated_quadrature(quadrature, minimum_rank=work_rank)
    )
    if rule.l_work != work_rank:
        raise SourceParityError(
            "quadrature l_work must equal the comparison work rank"
        )
    if projection_contract_sha256 is not None:
        supplied_projection = _sha256_text(
            projection_contract_sha256,
            name="projection_contract_sha256",
        )
        if supplied_projection != rule.projection_contract_sha256:
            raise SourceParityError(
                "projection contract identity does not match the supplied quadrature"
            )

    if unit_field_coefficients is None:
        unit = globals()["unit_field_coefficients"](output_rank)
    else:
        unit = _finite_vector(
            unit_field_coefficients,
            name="unit_field_coefficients",
            expected_length=expected_count,
        )

    samples = synthesize_real_spherical_harmonics(
        state_coefficients,
        l_max=output_rank,
        quadrature=rule,
    )
    if min(samples) < 0.0:
        raise SourceParityError(
            "the bounded full-grid route requires nonnegative occupation samples"
        )

    common_time = {
        "time_basis": time_basis,
        "H_s_inv": H_s_inv,
        "c_m_s": c_m_s,
    }
    grid_result = apply_constant_pair_to_full_spectral_grid(
        source,
        samples,
        state_parent_sha256=parent_identity,
        representation_sha256=grid_identity,
        projection_contract_sha256=rule.projection_contract_sha256,
        **common_time,
    )
    grid_projected = project_real_spherical_harmonics(
        grid_result.values,
        l_max=output_rank,
        quadrature=rule,
    )
    pstf_result = apply_constant_pair_to_spectral_pstf(
        source,
        state_coefficients,
        unit_field_coefficients=unit,
        l_out=output_rank,
        l_work=work_rank,
        state_parent_sha256=parent_identity,
        representation_sha256=pstf_identity,
        projection_contract_sha256=rule.projection_contract_sha256,
        **common_time,
    )

    residuals = tuple(
        grid_value - pstf_value
        for grid_value, pstf_value in zip(
            grid_projected, pstf_result.values, strict=True
        )
    )
    max_abs = max(abs(value) for value in residuals)
    relative_terms = tuple(
        abs(residual)
        / max(1.0, abs(grid_value), abs(pstf_value))
        for residual, grid_value, pstf_value in zip(
            residuals,
            grid_projected,
            pstf_result.values,
            strict=True,
        )
    )
    max_rel = max(relative_terms)
    pass_parity = all(
        abs(residual)
        <= absolute_tolerance
        + relative_tolerance * max(abs(grid_value), abs(pstf_value))
        for residual, grid_value, pstf_value in zip(
            residuals,
            grid_projected,
            pstf_result.values,
            strict=True,
        )
    )

    contract = _build_contract(
        source=source,
        l_out=output_rank,
        l_work=work_rank,
        quadrature=rule,
        state_parent_sha256=parent_identity,
        grid_representation_sha256=grid_identity,
        pstf_representation_sha256=pstf_identity,
        atol=absolute_tolerance,
        rtol=relative_tolerance,
    )
    if grid_result.receipt.rate_divisor_hex != pstf_result.receipt.rate_divisor_hex:
        raise SourceParityError("grid and PSTF routes used different rate divisors")
    report_payload = {
        "contract_sha256": contract.contract_sha256,
        "grid_output_sha256": grid_result.receipt.output_sha256,
        "grid_projected_hex": [value.hex() for value in grid_projected],
        "max_abs_residual_hex": max_abs.hex(),
        "max_rel_residual_hex": max_rel.hex(),
        "pass_parity": pass_parity,
        "pstf_output_sha256": pstf_result.receipt.output_sha256,
        "pstf_values_hex": [value.hex() for value in pstf_result.values],
        "rate_divisor_hex": grid_result.receipt.rate_divisor_hex,
        "residual_hex": [value.hex() for value in residuals],
        "schema": _REPORT_SCHEMA,
        "time_basis": time_basis.value,
    }
    report_hash = _canonical_sha256(report_payload)
    report = SourceParityReport(
        report_schema=_REPORT_SCHEMA,
        contract=contract,
        time_basis=time_basis,
        rate_divisor_hex=grid_result.receipt.rate_divisor_hex,
        compared_coefficients=expected_count,
        grid_projected=grid_projected,
        pstf_values=pstf_result.values,
        residuals=residuals,
        max_abs_residual=max_abs,
        max_rel_residual=max_rel,
        pass_parity=pass_parity,
        grid_receipt=grid_result.receipt,
        pstf_receipt=pstf_result.receipt,
        report_sha256=report_hash,
    )
    if require_pass and not pass_parity:
        raise SourceParityError(
            "full-grid projection and direct PSTF source action exceed the "
            f"declared tolerances: max_abs_residual={max_abs!r}"
        )
    return report
