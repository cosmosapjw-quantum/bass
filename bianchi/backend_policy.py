"""Typed backend selection and native capability diagnostics.

RF-00 makes implementation identity an explicit contract.  This module contains
no numerical code: it classifies public routes, loads the extension lazily, and
turns missing or incompatible native inputs into typed errors.  A Python path is
selected only by an explicit oracle request or a statically inventoried
``legacy_python_transitional`` route domain.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
import hashlib
import importlib
from importlib import machinery
from importlib import metadata
import json
import os
from pathlib import Path
import platform
import sysconfig
from types import MappingProxyType, ModuleType
from typing import Any, Callable, Mapping, NoReturn
import warnings


NATIVE_MODULE_NAME = "bianchi_rustcore"
NATIVE_DISTRIBUTION_NAME = "bianchi-rustcore"
EXPECTED_EXTENSION_VERSION = "0.1.0"
DEVELOPMENT_OVERRIDE_ENV = "BASS_ALLOW_UNVERIFIED_NATIVE_DEV"
EXPECTED_CARGO_LOCK_SHA256 = (
    "d500208e9353ade1cb74693918598846628219e6e7bd2e2bce9ec85e29eb6310"
)
REFERENCE_NATIVE_BUILD = MappingProxyType(
    {
        "status": "rf01_r4_wheel_and_installed_payload_fingerprint",
        "artifact_branch": "artifact/native-repro-bundle-20260825-r4",
        "wheel_sha256": (
            "c912ac94adef60b724af3ba892d7865d0148c77fa578be6c28ef021cce3b7482"
        ),
        "cargo_lock_sha256": EXPECTED_CARGO_LOCK_SHA256,
        "rustc_version": "1.94.1",
        "build_profile": "release",
        "cpu_arch": "x86_64",
        "simd_variant": "portable_default_target_no_target_cpu_override",
        "optional_features": ("cpu", "pyo3/extension-module"),
        "formula_manifest_sha256": (
            "5a8f05b917a7134584052167d5ece0c787a1f2683f347316ec6260844a5d19f4"
        ),
    }
)

_REFERENCE_NATIVE_INSTALLED_FILES = (
    (
        "bianchi_rustcore-0.1.0.dist-info/METADATA",
        210,
        "49324bfc75b7eade2973357d9be08074dcacad314bd58eada90bca87b4e0dd0c",
    ),
    (
        "bianchi_rustcore-0.1.0.dist-info/WHEEL",
        109,
        "c0053d72faa7b329ed4dfa6f979194fb32238ecafd12a729d8bf45b3e1e2e29c",
    ),
    (
        "bianchi_rustcore-0.1.0.dist-info/sboms/bianchi_rustcore.cyclonedx.json",
        150_086,
        "a6d303cea4a49d8cffd6bdaec74b8cfa746fbb8118896c4196e0cff4598546c7",
    ),
    (
        "bianchi_rustcore/__init__.py",
        147,
        "372239081d35fb39ffbe0d5c46e32c2e749b754245ec0e1cb036750fe223b591",
    ),
    (
        "bianchi_rustcore/bianchi_rustcore.cpython-312-x86_64-linux-gnu.so",
        3_143_152,
        "6bc27c610106996d7e3ba0c87c3df1e8e825b1f123dfbc8df71754b9c7ee4d7b",
    ),
)


class BackendPolicy(str, Enum):
    """Caller-visible backend modes fixed by the RF-00 specification."""

    RUST_REQUIRED = "rust_required"
    PYTHON_ORACLE = "python_oracle"
    LEGACY_PYTHON_TRANSITIONAL = "legacy_python_transitional"
    AUTO_DIAGNOSTIC = "auto_diagnostic"


class NativeLoadState(str, Enum):
    AVAILABLE = "available"
    MISSING_EXTENSION = "missing_extension"
    INCOMPATIBLE_EXTENSION = "incompatible_extension"


class PublicRouteState(str, Enum):
    """Committed RF-00 states for backend-touching public compute routes."""

    NATIVE_REQUIRED = "native_required"
    PYTHON_ORACLE = "python_oracle"
    LEGACY_PYTHON_TRANSITIONAL = "legacy_python_transitional"
    UNSUPPORTED = "unsupported"


class BackendError(RuntimeError):
    """Base class for actionable backend contract failures."""

    def __init__(self, route_id: str, message: str):
        super().__init__(message)
        self.route_id = route_id


class MissingNativeExtensionError(BackendError):
    """The required top-level extension module is not installed."""


class IncompatibleNativeExtensionError(BackendError):
    """The installed extension cannot load or lacks a required route symbol."""


class BackendPolicyError(BackendError):
    """A policy or route/domain combination is invalid."""


class UnverifiedNativePayloadError(BackendError):
    """A loadable native module is not the verified installed payload."""


class UnverifiedNativeDevelopmentWarning(RuntimeWarning):
    """An explicit development override admitted an unverified native build."""


@dataclass(frozen=True)
class NativeLoadResult:
    state: NativeLoadState
    module: ModuleType | None
    cause: ImportError | OSError | None
    detail: str | None

    @property
    def available(self) -> bool:
        return self.state is NativeLoadState.AVAILABLE


NativeDomainPredicate = Callable[[Mapping[str, Any]], bool]


def _always_native(_domain: Mapping[str, Any]) -> bool:
    return True


def _int_in_range(domain: Mapping[str, Any], key: str, low: int, high: int) -> bool:
    try:
        value = int(domain[key])
    except (KeyError, TypeError, ValueError):
        return False
    return low <= value <= high


def _encoded_moment_domain(domain: Mapping[str, Any]) -> bool:
    return (
        _int_in_range(domain, "l", 0, 5)
        and _int_in_range(domain, "i", -1, 2**31 - 1)
        and domain.get("f0_supported") is True
    )


def _encoded_tilted_moments_domain(domain: Mapping[str, Any]) -> bool:
    return domain.get("f0_supported") is True


def _builtin_background_domain(domain: Mapping[str, Any]) -> bool:
    return domain.get("builtin_background") is True


def _type_v_evolve_domain(domain: Mapping[str, Any]) -> bool:
    return domain.get("l_max") == 2 and domain.get("i_max") == 1


def _type_v_push_domain(domain: Mapping[str, Any]) -> bool:
    return domain.get("has_exact_rate") is True


def _tilted_integrate_domain(domain: Mapping[str, Any]) -> bool:
    return domain.get("mode", "ratio") in {
        "frozen",
        "ratio",
        "ratio_scalar",
        "zero",
        "phys_sqrt",
        "phys_5w",
        "phys_interp",
    }


@dataclass(frozen=True)
class RouteCapability:
    route_id: str
    required_symbols: tuple[str, ...]
    native_domain: NativeDomainPredicate = _always_native
    transitional_reason: str | None = None
    python_oracle_supported: bool = True

    def supports_native(self, domain: Mapping[str, Any]) -> bool:
        return bool(self.native_domain(domain))


def _route(
    route_id: str,
    *symbols: str,
    native_domain: NativeDomainPredicate = _always_native,
    transitional_reason: str | None = None,
    python_oracle_supported: bool = True,
) -> RouteCapability:
    return RouteCapability(
        route_id,
        tuple(symbols),
        native_domain,
        transitional_reason,
        python_oracle_supported,
    )


# The matrix covers every existing Python public/compatibility route that makes a
# backend choice.  Numerical implementation remains in its current module.
ROUTE_CAPABILITIES: Mapping[str, RouteCapability] = MappingProxyType(
    {
        capability.route_id: capability
        for capability in (
            _route("ray.final_z_batch", "trace_rays_batch"),
            _route("ray.optical_batch", "trace_optical_batch"),
            _route("background.integrate", "integrate_background"),
            _route("background.integrate_batch", "integrate_batch"),
            _route("background.chart_rhs", "chart_rhs"),
            _route("kinetic.j_moment", "kin_j_moment"),
            _route("kinetic.moments", "kin_moments"),
            _route(
                "kinetic.hierarchy_integrate",
                "kin_integrate",
                "kin_integrate_collisional",
            ),
            _route(
                "kinetic.thomson_eigenvalue",
                "kin_thomson_eigenvalue",
                "kin_thomson_eigenvalue_numeric",
            ),
            _route("kinetic.thomson_viscosity", "kin_thomson_viscosity"),
            _route("kinetic.thomson_stiffness", "kin_stiffness_ratio"),
            _route("kinetic.transport_coefficients", "kin_transport_coefficients"),
            _route("kinetic.viscous_cross_validate", "kin_cross_validate"),
            _route("tilted.j_moment", "kin_j_moment_tilted"),
            _route("tilted.moments", "kin_moments_tilted"),
            _route("tilted.boost_shell_residual", "kin_boost_shell_residual"),
            _route("observable.cmb_pattern_diag", "trace_rays_batch"),
            _route(
                "mixmaster.bounce_sequence",
                "mx_bounce_sequence",
                "mx_bounce_sequence_log",
            ),
            _route(
                "tilted.integrate",
                "th_integrate",
                native_domain=_tilted_integrate_domain,
                transitional_reason="unported closure mode",
            ),
            _route(
                "tilted.rhs",
                "th_rhs",
                native_domain=_tilted_integrate_domain,
                transitional_reason="unported closure mode",
            ),
            _route(
                "tilted.force_and_matrix",
                "th_force_and_matrix",
                native_domain=_tilted_integrate_domain,
                transitional_reason="unported closure mode",
            ),
            _route(
                "tilted.trajectory_error",
                "th_integrate",
                native_domain=_tilted_integrate_domain,
                transitional_reason="unported closure mode",
            ),
            _route("tilted_terms.perp_dot", "tt_perp_dot"),
            _route("tilted_terms.spatial_derivative", "tt_spatial_derivative"),
            _route("tilted_terms.div_contracted", "tt_div_contracted"),
            _route("tilted_terms.div_free_index", "tt_div_free_raw"),
            _route("type_v.forward_vs_backward", "tv_push_nodes"),
            _route(
                "type_v.evolve_coupled",
                "tv_evolve",
                native_domain=_type_v_evolve_domain,
                transitional_reason="only (l_max, i_max) == (2, 1) is migrated",
            ),
            _route(
                "type_v.back_trace",
                "tv_back_trace",
                native_domain=_builtin_background_domain,
                transitional_reason="custom background callback is not migrated",
            ),
            _route(
                "type_v.push_nodes",
                "tv_push_nodes",
                native_domain=_type_v_push_domain,
                transitional_reason="generic background callback is not migrated",
            ),
            _route(
                "hierarchy.J_moment",
                "kin_j_moment",
                native_domain=_encoded_moment_domain,
                transitional_reason="rank or distribution is not encodable by the native route",
            ),
            _route(
                "tilted_moments.J_moment_tilted",
                "kin_j_moment_tilted",
                native_domain=_encoded_moment_domain,
                transitional_reason="rank or distribution is not encodable by the native route",
            ),
            _route(
                "tilted_moments.moments_tilted",
                "kin_moments_tilted",
                native_domain=_encoded_tilted_moments_domain,
                transitional_reason="distribution is not encodable by the native route",
            ),
            _route("q.polstate.collide_modeb", "qp_collide_modeb"),
            # Native-only public wrappers.  They have no independent Python
            # implementation, so an explicit oracle request is unsupported
            # rather than a disguised fallback.
            _route(
                "collision_ladder.thomson_matrix_rust",
                "gc_thomson",
                python_oracle_supported=False,
            ),
            _route(
                "collision_ladder.collide_rust",
                "gc_expm_apply",
                python_oracle_supported=False,
            ),
            _route(
                "collision_ladder.strang_evolve_rust",
                "gc_strang",
                python_oracle_supported=False,
            ),
            _route(
                "coupled_tilted.coupled_rhs_rust",
                "cp_rhs",
                python_oracle_supported=False,
            ),
            _route(
                "coupled_tilted.rk4_evolve_rust",
                "cp_evolve",
                python_oracle_supported=False,
            ),
            _route("coeff_kernel.lhs_grid", "coeff_lhs_grid", python_oracle_supported=False),
            _route("coeff_kernel.mass_blocks", "coeff_mass_blocks", python_oracle_supported=False),
            _route("coeff_kernel.rhs_grid", "coeff_rhs_grid", python_oracle_supported=False),
            _route("q.characteristics.rhs_p", "qc_rhs_p", python_oracle_supported=False),
            _route("q.characteristics.rhs_split", "qc_rhs_split", python_oracle_supported=False),
            _route("q.characteristics.direction_map", "qc_direction_map", python_oracle_supported=False),
            _route("q.collide.kernel_eigenvalues", "qx_kernel_eigenvalues", python_oracle_supported=False),
            _route("q.collide.collide", "qx_collide", python_oracle_supported=False),
            _route("q.collide.collide_modeb", "qx_collide_modeb", python_oracle_supported=False),
            _route("q.comoving.frame", "QFrame", python_oracle_supported=False),
            _route("q.comoving.frame_from", "QFrame", python_oracle_supported=False),
            _route("q.comoving.moments_log", "qm_moments_log", python_oracle_supported=False),
            _route("q.comoving.collide_log", "qm_collide_log", python_oracle_supported=False),
            _route("q.fast.reduce_det", "qe_reduce_det", python_oracle_supported=False),
            _route("q.fast.evolve", "qe_evolve", python_oracle_supported=False),
            _route("q.fast.diagnostics", "qe_diagnostics", python_oracle_supported=False),
            _route("q.fast.ensemble", "qe_ensemble", python_oracle_supported=False),
            _route("q.fast.residual_mode_b", "qe_residual_mode_b", python_oracle_supported=False),
            _route("q.group.classify", "qg_classify", python_oracle_supported=False),
            _route("q.group.jacobi_residual", "qg_jacobi", python_oracle_supported=False),
            _route("q.group.structure_constants", "qg_structure_constants", python_oracle_supported=False),
            _route("q.group.ricci3", "qg_ricci3", python_oracle_supported=False),
            _route("q.group.curvature", "qg_curvature", python_oracle_supported=False),
            _route("q.group.kappa", "qg_kappa", python_oracle_supported=False),
            _route("q.modeb.evolve", "qe_evolve", python_oracle_supported=False),
            _route("q.modeb.diagnostics", "qe_diagnostics", python_oracle_supported=False),
            _route("q.polstate.residual_step", "qt_plan_from_points", python_oracle_supported=False),
            _route("q.residual.residual_step", "qt_plan_from_points", python_oracle_supported=False),
            _route("q.sphere.sphere", "QSphere", python_oracle_supported=False),
            _route("q.transport.radial", "QRadial", python_oracle_supported=False),
            _route("q.transport.plan", "qt_plan_step", python_oracle_supported=False),
            _route("routing.ic_template", "chart_aux", python_oracle_supported=False),
            _route("routing.roundtrip", "integrate_background", python_oracle_supported=False),
            _route(
                "runtime.plan",
                "RuntimePlan",
                "Workspace",
                python_oracle_supported=False,
            ),
        )
    }
)


@dataclass(frozen=True)
class PublicRouteInventoryRecord:
    """Machine-readable classification for one backend-touching public route."""

    route_id: str
    supported_state: PublicRouteState
    explicit_oracle_state: PublicRouteState
    outside_native_domain_state: PublicRouteState
    required_symbols: tuple[str, ...]
    transitional_reason: str | None


PUBLIC_ROUTE_INVENTORY: Mapping[str, PublicRouteInventoryRecord] = MappingProxyType(
    {
        route_id: PublicRouteInventoryRecord(
            route_id=route_id,
            supported_state=PublicRouteState.NATIVE_REQUIRED,
            explicit_oracle_state=(
                PublicRouteState.PYTHON_ORACLE
                if capability.python_oracle_supported
                else PublicRouteState.UNSUPPORTED
            ),
            outside_native_domain_state=(
                PublicRouteState.LEGACY_PYTHON_TRANSITIONAL
                if capability.transitional_reason is not None
                else PublicRouteState.UNSUPPORTED
            ),
            required_symbols=capability.required_symbols,
            transitional_reason=capability.transitional_reason,
        )
        for route_id, capability in ROUTE_CAPABILITIES.items()
    }
)


def public_route_inventory() -> dict[str, dict[str, Any]]:
    """Return the committed backend-touching route inventory as plain values."""

    return {
        route_id: {
            "supported_state": record.supported_state.value,
            "explicit_oracle_state": record.explicit_oracle_state.value,
            "outside_native_domain_state": record.outside_native_domain_state.value,
            "required_symbols": list(record.required_symbols),
            "transitional_reason": record.transitional_reason,
        }
        for route_id, record in PUBLIC_ROUTE_INVENTORY.items()
    }


def _native_extension_origin(module: ModuleType) -> str | None:
    """Locate the actual shared object for direct and maturin-package layouts."""

    nested = getattr(module, NATIVE_MODULE_NAME, None)
    for candidate in (nested, module):
        if candidate is None:
            continue
        spec = getattr(candidate, "__spec__", None)
        origin = getattr(spec, "origin", None) or getattr(candidate, "__file__", None)
        if isinstance(origin, str) and any(
            origin.endswith(suffix) for suffix in machinery.EXTENSION_SUFFIXES
        ):
            return origin
    return None


@lru_cache(maxsize=1)
def load_native() -> NativeLoadResult:
    """Load the extension once without suppressing arbitrary initialization errors."""

    try:
        module = importlib.import_module(NATIVE_MODULE_NAME)
    except ModuleNotFoundError as exc:
        if exc.name == NATIVE_MODULE_NAME:
            return NativeLoadResult(
                NativeLoadState.MISSING_EXTENSION, None, exc, str(exc)
            )
        return NativeLoadResult(
            NativeLoadState.INCOMPATIBLE_EXTENSION, None, exc, str(exc)
        )
    except (ImportError, OSError) as exc:
        return NativeLoadResult(
            NativeLoadState.INCOMPATIBLE_EXTENSION, None, exc, str(exc)
        )

    installed_version, version_source = _distribution_version()
    if (
        version_source == "installed_distribution_metadata"
        and installed_version != EXPECTED_EXTENSION_VERSION
    ):
        detail = (
            f"installed distribution version {installed_version!r} does not match "
            f"required {EXPECTED_EXTENSION_VERSION!r}"
        )
        error = ImportError(detail)
        return NativeLoadResult(
            NativeLoadState.INCOMPATIBLE_EXTENSION, None, error, detail
        )

    origin = _native_extension_origin(module)
    ext_suffix = sysconfig.get_config_var("EXT_SUFFIX")
    soabi = sysconfig.get_config_var("SOABI")
    if origin is None:
        detail = (
            f"imported {NATIVE_MODULE_NAME!r}, but neither the module nor its "
            "maturin nested module exposes a native extension origin"
        )
        error = ImportError(detail)
        return NativeLoadResult(
            NativeLoadState.INCOMPATIBLE_EXTENSION, None, error, detail
        )
    if ext_suffix and not origin.endswith(ext_suffix):
        detail = (
            f"native shared object {origin!r} does not match runtime EXT_SUFFIX "
            f"{ext_suffix!r} (SOABI {soabi or 'unknown'})"
        )
        error = ImportError(detail)
        return NativeLoadResult(
            NativeLoadState.INCOMPATIBLE_EXTENSION, None, error, detail
        )
    if origin is not None and not ext_suffix and soabi and soabi not in origin:
        detail = (
            f"native shared object {origin!r} does not identify runtime SOABI {soabi!r}"
        )
        error = ImportError(detail)
        return NativeLoadResult(
            NativeLoadState.INCOMPATIBLE_EXTENSION, None, error, detail
        )
    if not callable(getattr(module, "rayon_thread_pool_size", None)):
        detail = (
            f"installed {NATIVE_MODULE_NAME!r} lacks the RF-00 runtime capability "
            "symbol 'rayon_thread_pool_size'; install the documented RF-01 r4 wheel"
        )
        error = ImportError(detail)
        return NativeLoadResult(
            NativeLoadState.INCOMPATIBLE_EXTENSION, None, error, detail
        )
    return NativeLoadResult(NativeLoadState.AVAILABLE, module, None, None)


def _reset_native_loader_for_tests() -> None:
    """Clear only the lazy import cache; production code must not dispatch on this."""

    load_native.cache_clear()
    clear_payload_cache = getattr(_installed_native_payload_matches, "cache_clear", None)
    if clear_payload_cache is not None:
        clear_payload_cache()


@dataclass(frozen=True)
class BackendSelection:
    route_id: str
    policy: BackendPolicy
    native_module: ModuleType | None
    load_state: NativeLoadState | None
    transitional_reason: str | None = None
    installed_payload_verified: bool | None = None
    development_override: bool = False
    diagnostic: str | None = None

    @property
    def uses_rust(self) -> bool:
        return self.policy is BackendPolicy.RUST_REQUIRED


def _policy_value(route_id: str, value: BackendPolicy | str) -> BackendPolicy:
    if isinstance(value, BackendPolicy):
        return value
    try:
        return BackendPolicy(value)
    except (TypeError, ValueError) as exc:
        choices = ", ".join(policy.value for policy in BackendPolicy)
        raise BackendPolicyError(
            route_id, f"unknown backend policy {value!r}; expected one of: {choices}"
        ) from exc


def _missing_error(route_id: str, load: NativeLoadResult) -> NoReturn:
    message = (
        f"route {route_id!r} requires {NATIVE_MODULE_NAME}, but the extension is "
        "not installed. Install this project through its documented native-wheel "
        "entry point for the active Python interpreter, or explicitly select "
        "policy='python_oracle' for validation/debugging."
    )
    error = MissingNativeExtensionError(route_id, message)
    if load.cause is not None:
        raise error from load.cause
    raise error


def _incompatible_error(
    route_id: str, load: NativeLoadResult, missing_symbols: tuple[str, ...] = ()
) -> NoReturn:
    soabi = sysconfig.get_config_var("SOABI") or "unknown"
    if missing_symbols:
        detail = f"missing required symbols: {', '.join(missing_symbols)}"
        cause: BaseException | None = AttributeError(detail)
    else:
        detail = load.detail or "native extension load failed"
        cause = load.cause
    message = (
        f"route {route_id!r} requires a compatible {NATIVE_MODULE_NAME} extension "
        f"for Python SOABI {soabi}; {detail}. Reinstall the locked native wheel for "
        "this interpreter and retry. Python fallback is not automatic."
    )
    error = IncompatibleNativeExtensionError(route_id, message)
    if cause is not None:
        raise error from cause
    raise error


def _native_if_compatible(
    capability: RouteCapability, load: NativeLoadResult
) -> tuple[ModuleType | None, tuple[str, ...]]:
    if not load.available or load.module is None:
        return None, ()
    missing = tuple(
        symbol for symbol in capability.required_symbols if not hasattr(load.module, symbol)
    )
    return (None if missing else load.module), missing


def _development_override(
    route_id: str, explicit: bool | None
) -> bool:
    """Resolve the only supported unverified-build escape hatch.

    The override is deliberately noisy and development-only.  Production calls
    neither infer it from importability nor accept truthy spellings other than
    the exact value ``1``.
    """

    if explicit is not None:
        if not isinstance(explicit, bool):
            raise BackendPolicyError(
                route_id, "development_override must be an explicit boolean"
            )
        return explicit
    raw = os.environ.get(DEVELOPMENT_OVERRIDE_ENV)
    if raw is None:
        return False
    if raw != "1":
        raise BackendPolicyError(
            route_id,
            f"{DEVELOPMENT_OVERRIDE_ENV} must be exactly '1' when used; "
            f"observed {raw!r}",
        )
    return True


def _unverified_payload_error(
    route_id: str, native_origin: str | None, reason: str
) -> NoReturn:
    origin = native_origin or "unavailable"
    raise UnverifiedNativePayloadError(
        route_id,
        f"route {route_id!r} refuses native dispatch because the loaded payload "
        f"is not the verified installed RF-00 artifact ({reason}; origin={origin!r}). "
        f"Install the documented immutable native wheel. For an intentional local "
        f"source-build experiment only, set {DEVELOPMENT_OVERRIDE_ENV}=1 and retain "
        "the emitted development diagnostic; this is not production provenance.",
    )


def select_backend(
    route_id: str,
    *,
    policy: BackendPolicy | str | None = None,
    force_python: bool = False,
    development_override: bool | None = None,
    **domain: Any,
) -> BackendSelection:
    """Resolve one route without using extension importability as fallback authority."""

    try:
        capability = ROUTE_CAPABILITIES[route_id]
    except KeyError as exc:
        raise BackendPolicyError(route_id, f"unregistered backend route {route_id!r}") from exc

    requested = None if policy is None else _policy_value(route_id, policy)
    if force_python:
        if requested not in (None, BackendPolicy.PYTHON_ORACLE):
            raise BackendPolicyError(
                route_id,
                "force_python=True conflicts with the requested backend policy; "
                "use policy='python_oracle' alone",
            )
        if not capability.python_oracle_supported:
            raise BackendPolicyError(
                route_id,
                "python_oracle is unsupported for this native-only public route",
            )
        return BackendSelection(route_id, BackendPolicy.PYTHON_ORACLE, None, None)

    native_domain = capability.supports_native(domain)
    if requested is BackendPolicy.PYTHON_ORACLE:
        if not capability.python_oracle_supported:
            raise BackendPolicyError(
                route_id,
                "python_oracle is unsupported for this native-only public route",
            )
        return BackendSelection(route_id, BackendPolicy.PYTHON_ORACLE, None, None)

    if requested is BackendPolicy.LEGACY_PYTHON_TRANSITIONAL:
        if native_domain:
            raise BackendPolicyError(
                route_id,
                "legacy_python_transitional is reserved for statically inventoried "
                "unmigrated route domains",
            )
        warnings.warn(
            f"{route_id}: legacy_python_transitional ({capability.transitional_reason})",
            RuntimeWarning,
            stacklevel=2,
        )
        return BackendSelection(
            route_id,
            BackendPolicy.LEGACY_PYTHON_TRANSITIONAL,
            None,
            None,
            capability.transitional_reason,
        )

    if not native_domain:
        if requested is BackendPolicy.RUST_REQUIRED:
            raise BackendPolicyError(
                route_id,
                f"route domain is not native-supported: {capability.transitional_reason}",
            )
        warnings.warn(
            f"{route_id}: legacy_python_transitional ({capability.transitional_reason})",
            RuntimeWarning,
            stacklevel=2,
        )
        return BackendSelection(
            route_id,
            BackendPolicy.LEGACY_PYTHON_TRANSITIONAL,
            None,
            None,
            capability.transitional_reason,
        )

    load = load_native()
    module, missing_symbols = _native_if_compatible(capability, load)
    if requested is BackendPolicy.AUTO_DIAGNOSTIC:
        fallback = (
            "python_oracle"
            if capability.python_oracle_supported
            else "rust_required_fail_closed"
        )
        warnings.warn(
            f"{route_id}: auto_diagnostic is interactive-only and selected "
            f"{'rust_required' if module is not None else fallback}",
            RuntimeWarning,
            stacklevel=2,
        )
        if module is None and capability.python_oracle_supported:
            return BackendSelection(
                route_id, BackendPolicy.PYTHON_ORACLE, None, load.state
            )

    if load.state is NativeLoadState.MISSING_EXTENSION:
        _missing_error(route_id, load)
    if load.state is NativeLoadState.INCOMPATIBLE_EXTENSION:
        _incompatible_error(route_id, load)
    if module is None:
        _incompatible_error(route_id, load, missing_symbols)

    native_origin = _native_extension_origin(module)
    payload_verified, payload_reason = _installed_native_payload_matches(native_origin)
    override = _development_override(route_id, development_override)
    diagnostic = None
    if not payload_verified:
        if not override:
            _unverified_payload_error(route_id, native_origin, payload_reason)
        diagnostic = (
            "UNVERIFIED_DEVELOPMENT_NATIVE_PAYLOAD:"
            f"route={route_id};reason={payload_reason};origin={native_origin or 'unavailable'}"
        )
        warnings.warn(
            diagnostic,
            UnverifiedNativeDevelopmentWarning,
            stacklevel=2,
        )
    return BackendSelection(
        route_id,
        BackendPolicy.RUST_REQUIRED,
        module,
        NativeLoadState.AVAILABLE,
        installed_payload_verified=payload_verified,
        development_override=override,
        diagnostic=diagnostic,
    )


def require_native(
    route_id: str,
    *,
    development_override: bool | None = None,
    **domain: Any,
) -> ModuleType:
    """Return a route-bound native module or raise one typed RF-00 error."""

    selected = select_backend(
        route_id,
        policy=BackendPolicy.RUST_REQUIRED,
        development_override=development_override,
        **domain,
    )
    assert selected.native_module is not None
    return selected.native_module


def _distribution_version() -> tuple[str | None, str]:
    try:
        return metadata.version(NATIVE_DISTRIBUTION_NAME), "installed_distribution_metadata"
    except metadata.PackageNotFoundError:
        return None, "unavailable"


def _installed_wheel_sha256() -> tuple[str | None, str]:
    """Read pip's PEP 610 archive hash when the installed wheel exposes it."""

    try:
        distribution = metadata.distribution(NATIVE_DISTRIBUTION_NAME)
    except metadata.PackageNotFoundError:
        return None, "unavailable"
    raw = distribution.read_text("direct_url.json")
    if raw is None:
        return None, "direct_url_metadata_absent"
    try:
        payload = json.loads(raw)
        value = payload["archive_info"]["hashes"]["sha256"]
    except (KeyError, TypeError, json.JSONDecodeError):
        return None, "direct_url_sha256_absent_or_invalid"
    if not isinstance(value, str) or len(value) != 64:
        return None, "direct_url_sha256_invalid"
    return value.lower(), "installed_distribution_direct_url"


@lru_cache(maxsize=8)
def _installed_native_payload_matches(native_origin: str | None) -> tuple[bool, str]:
    """Bind the loaded extension to the RF-01 r4 installed-file receipt."""

    if native_origin is None:
        return False, "loaded_native_extension_origin_unavailable"

    try:
        distribution = metadata.distribution(NATIVE_DISTRIBUTION_NAME)
    except metadata.PackageNotFoundError:
        return False, "distribution_unavailable"

    distribution_native_path: Path | None = None
    for relative, expected_size, expected_sha256 in _REFERENCE_NATIVE_INSTALLED_FILES:
        path = Path(distribution.locate_file(relative))
        try:
            if not path.is_file() or path.stat().st_size != expected_size:
                return False, f"installed_file_size_mismatch:{relative}"
            observed_sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError:
            return False, f"installed_file_unreadable:{relative}"
        if observed_sha256 != expected_sha256:
            return False, f"installed_file_sha256_mismatch:{relative}"
        if any(relative.endswith(suffix) for suffix in machinery.EXTENSION_SUFFIXES):
            distribution_native_path = path

    if distribution_native_path is None:
        return False, "distribution_native_extension_not_in_reference_fingerprint"
    try:
        loaded_path = Path(native_origin).resolve(strict=True)
        owned_path = distribution_native_path.resolve(strict=True)
    except (OSError, RuntimeError):
        return False, "loaded_or_distribution_native_extension_unresolvable"
    if loaded_path != owned_path:
        return False, "loaded_native_extension_not_distribution_owned"
    return True, "rf01_r4_loaded_distribution_file_fingerprint"


def _configured_threads() -> tuple[int | None, str]:
    raw = os.environ.get("RAYON_NUM_THREADS")
    if raw is None:
        return None, "not_configured"
    try:
        value = int(raw)
    except ValueError:
        return None, "invalid_RAYON_NUM_THREADS"
    if value <= 0:
        return None, "invalid_RAYON_NUM_THREADS"
    return value, "RAYON_NUM_THREADS"


def _native_rayon_threads(load: NativeLoadResult) -> tuple[int | None, str]:
    """Read the initialized Rayon pool size from the extension when exposed."""

    if not load.available or load.module is None:
        return None, "native_extension_unavailable"
    probe = getattr(load.module, "rayon_thread_pool_size", None)
    if not callable(probe):
        return None, "native_extension_thread_pool_size_not_exposed"
    try:
        value = probe()
        if isinstance(value, bool):
            raise TypeError("boolean is not a thread-pool size")
        size = int(value)
    except (OverflowError, TypeError, ValueError) as exc:
        return None, f"native_extension_thread_pool_size_invalid:{type(exc).__name__}"
    if size <= 0:
        return None, "native_extension_thread_pool_size_invalid:nonpositive"
    return size, "native_extension.rayon_thread_pool_size"


def capability_report(
    policy: BackendPolicy | str = BackendPolicy.RUST_REQUIRED,
    *,
    probe_legacy_global_pool: bool = True,
) -> dict[str, Any]:
    """Return runtime/build capabilities and installed-payload dispatch authority.

    ``probe_legacy_global_pool`` exists only for the explicit RF-00 diagnostic.
    RuntimePlan construction disables it because a private plan pool is the sole
    authoritative threading owner for RF-01 operations.
    """

    selected_policy = _policy_value("capability_report", policy)
    load = load_native()
    version, version_source = _distribution_version()
    wheel_sha256, wheel_source = _installed_wheel_sha256()
    native_origin = (
        _native_extension_origin(load.module) if load.module is not None else None
    )
    payload_matches_reference, payload_source = _installed_native_payload_matches(
        native_origin
    )
    reference_bound = (
        load.available
        and version == EXPECTED_EXTENSION_VERSION
        and payload_matches_reference
    )
    development_override_raw = os.environ.get(DEVELOPMENT_OVERRIDE_ENV)
    development_override_active = development_override_raw == "1"
    if reference_bound:
        native_dispatch_provenance_state = "verified_installed_payload"
    elif load.available:
        native_dispatch_provenance_state = "unverified_development_payload"
    else:
        native_dispatch_provenance_state = "native_unavailable"
    exact_reference_wheel_observed = (
        wheel_sha256 == REFERENCE_NATIVE_BUILD["wheel_sha256"]
    )
    configured_threads, thread_source = _configured_threads()
    if probe_legacy_global_pool:
        actual_threads, actual_thread_source = _native_rayon_threads(load)
    else:
        actual_threads = None
        actual_thread_source = "not_probed_runtimeplan_private_pool_authority"
    configured_build_profile = os.environ.get("BASS_RUST_BUILD_PROFILE")
    configured_cpu_variant = os.environ.get("BASS_RUST_CPU_DISPATCH")
    feature_text = os.environ.get("BASS_RUST_OPTIONAL_FEATURES", "")
    configured_features = sorted(
        feature.strip() for feature in feature_text.split(",") if feature.strip()
    )
    module_path = getattr(load.module, "__file__", None) if load.module is not None else None
    functions = (
        sorted(name for name in dir(load.module) if not name.startswith("_"))
        if load.module is not None
        else []
    )
    reference_native_build = dict(REFERENCE_NATIVE_BUILD)
    reference_native_build["optional_features"] = list(
        REFERENCE_NATIVE_BUILD["optional_features"]
    )
    return {
        "backend_policy": selected_policy.value,
        "extension_state": load.state.value,
        "extension_version": version,
        "required_extension_version": EXPECTED_EXTENSION_VERSION,
        "extension_module_path": module_path,
        "native_shared_object_origin": native_origin,
        "python_abi": sysconfig.get_config_var("SOABI") or "unknown",
        "rustc_version": (
            REFERENCE_NATIVE_BUILD["rustc_version"] if reference_bound else None
        ),
        "cargo_lock_sha256": (
            REFERENCE_NATIVE_BUILD["cargo_lock_sha256"] if reference_bound else None
        ),
        "wheel_sha256": wheel_sha256,
        "build_profile": (
            REFERENCE_NATIVE_BUILD["build_profile"] if reference_bound else None
        ),
        "cpu_arch": (
            REFERENCE_NATIVE_BUILD["cpu_arch"] if reference_bound
            else (platform.machine() or "unknown")
        ),
        "simd_variant": (
            REFERENCE_NATIVE_BUILD["simd_variant"] if reference_bound else None
        ),
        "rayon_threads": actual_threads,
        "optional_features": (
            list(REFERENCE_NATIVE_BUILD["optional_features"])
            if reference_bound else []
        ),
        "formula_manifest_sha256": (
            REFERENCE_NATIVE_BUILD["formula_manifest_sha256"]
            if reference_bound else None
        ),
        "cargo_lock_binding_verified": reference_bound,
        "installed_native_build_verified": reference_bound,
        "installed_native_payload_fingerprint_verified": reference_bound,
        "production_native_dispatch_permitted": reference_bound,
        "native_dispatch_provenance_state": native_dispatch_provenance_state,
        "development_override_environment": DEVELOPMENT_OVERRIDE_ENV,
        "development_override_active": development_override_active,
        "development_override_value_valid": development_override_raw in (None, "1"),
        "development_override_diagnostic": (
            None
            if reference_bound or not development_override_active
            else "UNVERIFIED_DEVELOPMENT_NATIVE_PAYLOAD"
        ),
        "exact_native_wheel_archive_observed": exact_reference_wheel_observed,
        "expected_cargo_lock_sha256": EXPECTED_CARGO_LOCK_SHA256,
        "configured_build_profile": configured_build_profile,
        "cpu_dispatch_variant": configured_cpu_variant,
        "thread_pool_size": actual_threads,
        "configured_rayon_threads": configured_threads,
        "enabled_optional_features": configured_features if feature_text else None,
        "functions": functions,
        "load_error_type": type(load.cause).__name__ if load.cause is not None else None,
        "load_error": load.detail,
        "provenance": {
            "backend_policy": "caller_selected_report_mode",
            "extension_version": version_source,
            "required_extension_version": "RF-00_package_contract",
            "native_shared_object_origin": (
                "runtime_module_spec" if native_origin else "not_observable"
            ),
            "python_abi": "runtime_sysconfig",
            "rustc_version": (
                payload_source
                if reference_bound else "not_exposed_by_installed_extension"
            ),
            "cargo_lock_sha256": (
                payload_source
                if reference_bound else "source_contract_expected_unverified"
            ),
            "wheel_sha256": wheel_source,
            "build_profile": (
                payload_source
                if reference_bound else "not_exposed_by_installed_extension"
            ),
            "cpu_arch": (
                payload_source
                if reference_bound else "runtime_platform_not_build_target_attestation"
            ),
            "simd_variant": (
                payload_source
                if reference_bound else "not_exposed_by_installed_extension"
            ),
            "rayon_threads": actual_thread_source,
            "optional_features": (
                payload_source
                if reference_bound else "not_exposed_by_installed_extension"
            ),
            "formula_manifest_sha256": (
                payload_source
                if reference_bound else "not_exposed_by_installed_extension"
            ),
            "expected_cargo_lock_sha256": "source_contract_reference_only",
            "configured_build_profile": (
                "BASS_RUST_BUILD_PROFILE" if configured_build_profile else "not_configured"
            ),
            "cpu_dispatch_variant": (
                "BASS_RUST_CPU_DISPATCH" if configured_cpu_variant else "not_configured"
            ),
            "thread_pool_size": actual_thread_source,
            "configured_rayon_threads": thread_source,
            "enabled_optional_features": (
                "BASS_RUST_OPTIONAL_FEATURES" if feature_text else "not_configured"
            ),
            "production_native_dispatch_permitted": payload_source,
            "native_dispatch_provenance_state": payload_source,
            "development_override_environment": "RF-00_development_contract",
            "development_override_active": (
                DEVELOPMENT_OVERRIDE_ENV
                if development_override_raw is not None else "not_configured"
            ),
        },
        "reference_native_build": reference_native_build,
    }
