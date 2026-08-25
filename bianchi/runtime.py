"""Thin Python orchestration for the RF-01 native runtime substrate.

No numerical implementation lives here.  Production construction always uses
the typed RF-00 policy, including installed-payload verification (or its
explicit development override diagnostic).
"""

from __future__ import annotations

from types import MappingProxyType
from typing import Any

from .backend_policy import BackendPolicy, capability_report, select_backend


class Workspace:
    """Python lifetime wrapper around one plan-bound native workspace."""

    def __init__(self, plan: "RuntimePlan", native: Any):
        self._plan = plan
        self._native = native

    @property
    def plan_fingerprint(self) -> str:
        return str(self._native.plan_fingerprint)

    @property
    def size(self) -> int:
        return int(self._native.size)

    @property
    def is_busy(self) -> bool:
        return bool(self._native.is_busy)

    @property
    def is_poisoned(self) -> bool:
        return bool(self._native.is_poisoned)

    def snapshot(self) -> dict[str, Any]:
        return dict(self._native.snapshot())

    def reset(self) -> None:
        self._native.reset()

    def recover(self) -> None:
        self._native.recover()


class RuntimePlan:
    """Immutable Python frontend for one verified native RuntimePlan."""

    def __init__(
        self,
        thread_count: int,
        *,
        fixture_size: int = 64,
        require_finite: bool = True,
        cpu_variant: str = "scalar",
    ):
        selection = select_backend(
            "runtime.plan",
            policy=BackendPolicy.RUST_REQUIRED,
        )
        assert selection.native_module is not None
        self._selection = selection
        report = capability_report(
            BackendPolicy.RUST_REQUIRED,
            probe_legacy_global_pool=False,
        )
        self._build_capability = MappingProxyType(
            {
                name: (
                    tuple(report[name])
                    if name == "optional_features"
                    else report[name]
                )
                for name in (
                    "extension_version",
                    "python_abi",
                    "rustc_version",
                    "cargo_lock_sha256",
                    "wheel_sha256",
                    "build_profile",
                    "cpu_arch",
                    "simd_variant",
                    "optional_features",
                    "formula_manifest_sha256",
                )
            }
        )
        self._native = selection.native_module.RuntimePlan(
            thread_count=thread_count,
            fixture_size=fixture_size,
            require_finite=require_finite,
            cpu_variant=cpu_variant,
        )

    @property
    def thread_count(self) -> int:
        return int(self._native.thread_count)

    @property
    def private_pool_size(self) -> int:
        return int(self._native.private_pool_size)

    @property
    def fixture_size(self) -> int:
        return int(self._native.fixture_size)

    @property
    def fingerprint(self) -> str:
        return str(self._native.fingerprint)

    def capability_receipt(self) -> dict[str, Any]:
        receipt = dict(self._native.capability_receipt())
        receipt.update(self._build_capability)
        receipt.update(
            {
                "backend_policy": self._selection.policy.value,
                "installed_payload_verified": (
                    self._selection.installed_payload_verified
                ),
                "development_override": self._selection.development_override,
                "policy_diagnostic": self._selection.diagnostic,
            }
        )
        return receipt

    def counters(self) -> dict[str, int]:
        return dict(self._native.counters())

    def reset_counters(self) -> None:
        self._native.reset_counters()

    def workspace(self) -> Workspace:
        return Workspace(self, self._native.workspace())

    def run_fixture(
        self,
        values: Any,
        workspace: Workspace,
        *,
        steps: int = 1,
    ):
        if not isinstance(workspace, Workspace):
            raise TypeError("workspace must be a bianchi.runtime.Workspace")
        return self._native.run_fixture(
            values,
            workspace._native,
            steps=steps,
        )


__all__ = ["RuntimePlan", "Workspace"]
