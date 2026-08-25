"""Typed, explicit loaders for optional Python frontend/oracle dependencies."""
from __future__ import annotations

from functools import lru_cache
import importlib
from types import ModuleType


ORACLE_EXTRA = "python-oracle"
_INSTALL_HINT = "python -m pip install 'bianchi-solver[python-oracle]==0.1.0'"


class OptionalDependencyError(ImportError):
    """An explicit optional frontend cannot load one of its dependencies."""

    def __init__(
        self,
        dependency: str,
        feature: str,
        module_name: str,
        *,
        extra: str = ORACLE_EXTRA,
        detail: str | None = None,
    ) -> None:
        self.dependency = dependency
        self.feature = feature
        self.module_name = module_name
        self.extra = extra
        suffix = f" ({detail})" if detail else ""
        super().__init__(
            f"optional dependency {dependency!r} is required by {feature!r}{suffix}. "
            f"Install the explicit {extra!r} frontend with: {_INSTALL_HINT}"
        )


class OptionalDependencyConfigurationError(OptionalDependencyError):
    """An optional dependency is installed but cannot meet its runtime contract."""


def _requested_dependency_failure(
    exc: ImportError, module_name: str, dependency: str
) -> bool:
    """Return whether an import error identifies the requested dependency."""

    missing_name = getattr(exc, "name", None)
    if not isinstance(missing_name, str):
        return False
    return any(
        missing_name == candidate
        or missing_name.startswith(f"{candidate}.")
        or candidate.startswith(f"{missing_name}.")
        for candidate in (dependency, module_name)
    )


@lru_cache(maxsize=None)
def require_optional(
    module_name: str,
    *,
    feature: str,
    dependency: str | None = None,
    extra: str = ORACLE_EXTRA,
) -> ModuleType:
    """Import one dependency only after an optional frontend is selected."""

    dependency_name = dependency or module_name.partition(".")[0]
    try:
        return importlib.import_module(module_name)
    except ImportError as exc:
        if not _requested_dependency_failure(exc, module_name, dependency_name):
            raise
        raise OptionalDependencyError(
            dependency_name,
            feature,
            module_name,
            extra=extra,
            detail=f"{type(exc).__name__}: {exc}",
        ) from exc


@lru_cache(maxsize=None)
def require_jax_x64(*, feature: str) -> tuple[ModuleType, ModuleType]:
    """Load JAX for an explicit oracle and enable x64 before JAX NumPy.

    No arrays are allocated here, so dependency/configuration validation does not
    initialize a device merely to inspect a dtype.
    """

    jax = require_optional("jax", feature=feature, dependency="jax")
    try:
        jax.config.update("jax_enable_x64", True)
    except (RuntimeError, ValueError) as exc:
        raise OptionalDependencyConfigurationError(
            "jax",
            feature,
            "jax",
            detail=(
                "failed to enable required x64 mode before oracle array creation; "
                f"{type(exc).__name__}: {exc}"
            ),
        ) from exc
    jnp = require_optional("jax.numpy", feature=feature, dependency="jax")
    return jax, jnp
