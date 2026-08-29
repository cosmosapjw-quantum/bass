"""RF-04 public dispatch only; all numerical work remains in native Rust.

The backend inventory, adapter and numerical owner must be registered before
these functions can run.  Test-only dense oracles are never imported here.
"""
from __future__ import annotations

from types import ModuleType
from typing import Any

from bianchi.backend_policy import BackendPolicy, select_backend

__all__ = [
    'typeii_execution_identity_v1',
    'typeii_trajectory_v1',
    'typeii_batch_v1',
]


def _native(route_id: str) -> ModuleType:
    selection = select_backend(route_id, policy=BackendPolicy.RUST_REQUIRED)
    if selection.native_module is None:
        raise RuntimeError('native_required selection returned no native module')
    return selection.native_module


def typeii_execution_identity_v1() -> str:
    """Return the exact native execution identity; never synthesize it in Python."""
    return _native('kinetic.typeii.execution_identity_v1').rf04_typeii_execution_identity_v1()


def typeii_trajectory_v1(*arguments: Any) -> Any:
    """Forward the frozen positional request unchanged in one native call."""
    return _native('kinetic.typeii.trajectory_v1').rf04_typeii_trajectory_v1(*arguments)


def typeii_batch_v1(*arguments: Any) -> Any:
    """Forward the complete batch; no per-member Python loop or fallback."""
    return _native('kinetic.typeii.batch_v1').rf04_typeii_batch_v1(*arguments)
