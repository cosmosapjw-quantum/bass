"""Bianchi background-cosmology solver.

The package root is deliberately dependency-light. Optional Python oracle
frontends configure and import JAX/SciPy/SymPy only when those frontends are
requested explicitly.
"""
from __future__ import annotations

import importlib


__version__ = "0.1.0"

__all__ = ["conventions", "algebra", "__version__"]

_LAZY_PUBLIC_MODULES = frozenset({"conventions", "algebra"})


def __getattr__(name: str):
    """Preserve the historical public modules without importing them eagerly."""

    if name not in _LAZY_PUBLIC_MODULES:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module = importlib.import_module(f"{__name__}.{name}")
    globals()[name] = module
    return module


def __dir__() -> list[str]:
    return sorted(set(globals()) | _LAZY_PUBLIC_MODULES)
