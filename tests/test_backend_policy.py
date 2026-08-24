"""Focused RF-00 backend identity and fail-closed policy proofs.

Failure cases inject the loader result through the documented lazy-import seam.
They never uninstall the native wheel, mutate ``sys.modules``, or reload either
policy module, so one case cannot change the interpreter state seen by another.
"""
from __future__ import annotations

import json
import sysconfig
from types import ModuleType

import numpy as np
import pytest

from bianchi import backend
from bianchi import backend_policy as policy


CAPABILITY_FIELDS = (
    "backend_policy",
    "extension_version",
    "python_abi",
    "rustc_version",
    "cargo_lock_sha256",
    "wheel_sha256",
    "build_profile",
    "cpu_arch",
    "simd_variant",
    "rayon_threads",
    "optional_features",
    "formula_manifest_sha256",
)


@pytest.fixture(autouse=True)
def _isolated_native_loader_cache(monkeypatch):
    """Keep injected loader outcomes local without reloading Python modules."""

    monkeypatch.delenv(policy.DEVELOPMENT_OVERRIDE_ENV, raising=False)
    policy._reset_native_loader_for_tests()
    yield
    policy._reset_native_loader_for_tests()


def _native_module(**symbols):
    module = ModuleType(policy.NATIVE_MODULE_NAME)
    extension_suffix = sysconfig.get_config_var("EXT_SUFFIX") or ".so"
    module.__file__ = f"/proof-fixture/bianchi_rustcore{extension_suffix}"
    module.rayon_thread_pool_size = lambda: 1
    for name, value in symbols.items():
        setattr(module, name, value)
    return module


class _PayloadEvidence:
    """Callable verified-payload seam that remains compatible with cache reset."""

    def __init__(self, verified: bool, reason: str):
        self.verified = verified
        self.reason = reason
        self.origins = []

    def __call__(self, native_origin):
        self.origins.append(native_origin)
        return self.verified, self.reason

    def cache_clear(self):
        return None


def _inject_payload_evidence(monkeypatch, *, verified=True, reason=None):
    evidence = _PayloadEvidence(
        verified,
        reason or (
            "test_verified_installed_payload"
            if verified
            else "test_unverified_native_payload"
        ),
    )
    monkeypatch.setattr(policy, "_installed_native_payload_matches", evidence)
    return evidence


def _inject_native_import(monkeypatch, outcome):
    """Replace only the extension import and delegate every unrelated import."""

    real_import = policy.importlib.import_module
    calls = []

    def injected(name, package=None):
        if name != policy.NATIVE_MODULE_NAME:
            return real_import(name, package)
        calls.append(name)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome

    monkeypatch.setattr(policy.importlib, "import_module", injected)
    return calls


def _missing_extension_error():
    return ModuleNotFoundError(
        "No module named 'bianchi_rustcore'", name=policy.NATIVE_MODULE_NAME
    )


def test_policy_matrix_native_transitional_oracle_unknown_and_conflict(monkeypatch):
    native = _native_module(chart_rhs=lambda *_args: np.arange(5.0))
    calls = _inject_native_import(monkeypatch, native)
    payload_evidence = _inject_payload_evidence(monkeypatch)

    selected = policy.select_backend("background.chart_rhs")
    assert selected.policy is policy.BackendPolicy.RUST_REQUIRED
    assert selected.native_module is native
    assert selected.load_state is policy.NativeLoadState.AVAILABLE
    assert selected.installed_payload_verified is True
    assert selected.development_override is False
    assert selected.diagnostic is None
    assert selected.uses_rust
    assert calls == [policy.NATIVE_MODULE_NAME]
    assert payload_evidence.origins == [native.__file__]

    with pytest.warns(RuntimeWarning, match="legacy_python_transitional"):
        transitional = policy.select_backend(
            "type_v.evolve_coupled", l_max=3, i_max=1
        )
    assert transitional.policy is policy.BackendPolicy.LEGACY_PYTHON_TRANSITIONAL
    assert transitional.native_module is None
    assert transitional.transitional_reason

    oracle = policy.select_backend(
        "background.chart_rhs", policy=policy.BackendPolicy.PYTHON_ORACLE
    )
    assert oracle.policy is policy.BackendPolicy.PYTHON_ORACLE
    assert oracle.native_module is None
    assert not oracle.uses_rust
    assert calls == [policy.NATIVE_MODULE_NAME]

    with pytest.raises(policy.BackendPolicyError, match="unregistered backend route"):
        policy.select_backend("not.a.registered.route")
    with pytest.raises(policy.BackendPolicyError, match="unknown backend policy"):
        policy.select_backend("background.chart_rhs", policy="surprise_backend")
    with pytest.raises(policy.BackendPolicyError, match="conflicts"):
        policy.select_backend(
            "background.chart_rhs", policy="rust_required", force_python=True
        )
    with pytest.raises(policy.BackendPolicyError, match="reserved"):
        policy.select_backend(
            "background.chart_rhs", policy="legacy_python_transitional"
        )


def test_auto_diagnostic_is_explicit_warned_and_non_production(monkeypatch):
    calls = _inject_native_import(monkeypatch, _missing_extension_error())

    with pytest.warns(RuntimeWarning, match="auto_diagnostic.*python_oracle"):
        selected = policy.select_backend(
            "background.chart_rhs", policy="auto_diagnostic"
        )
    assert selected.policy is policy.BackendPolicy.PYTHON_ORACLE
    assert selected.load_state is policy.NativeLoadState.MISSING_EXTENSION
    assert not selected.uses_rust
    assert calls == [policy.NATIVE_MODULE_NAME]


def test_static_transitional_route_never_probes_native(monkeypatch):
    calls = _inject_native_import(
        monkeypatch,
        AssertionError("static transitional selection probed the native extension"),
    )

    with pytest.warns(RuntimeWarning, match="legacy_python_transitional"):
        selected = policy.select_backend(
            "hierarchy.J_moment", l=6, i=0, f0_supported=True
        )
    assert selected.policy is policy.BackendPolicy.LEGACY_PYTHON_TRANSITIONAL
    assert selected.native_module is None
    assert calls == []


def test_missing_extension_is_typed_actionable_and_never_calls_oracle(monkeypatch):
    calls = _inject_native_import(monkeypatch, _missing_extension_error())

    with pytest.raises(policy.MissingNativeExtensionError) as caught:
        backend.chart_rhs("class_a", np.zeros(5), 4.0 / 3.0, policy="rust_required")
    assert caught.value.route_id == "background.chart_rhs"
    assert isinstance(caught.value.__cause__, ModuleNotFoundError)
    message = str(caught.value)
    assert "not installed" in message
    assert "python_oracle" in message
    assert "Install" in message

    # The one-entry cache proves the deterministic failure without re-import churn.
    with pytest.raises(policy.MissingNativeExtensionError):
        policy.select_backend("background.chart_rhs", policy="rust_required")
    assert calls == [policy.NATIVE_MODULE_NAME]


@pytest.mark.parametrize(
    "load_error",
    [
        ImportError("extension module was compiled for an incompatible interpreter"),
        OSError("bianchi_rustcore.so: undefined symbol: PyExc_ImportError"),
    ],
    ids=("import-error", "abi-loader-error"),
)
def test_incompatible_extension_is_typed_and_reports_active_abi(
    monkeypatch, load_error
):
    _inject_native_import(monkeypatch, load_error)

    with pytest.raises(policy.IncompatibleNativeExtensionError) as caught:
        backend.chart_rhs("class_a", np.zeros(5), 4.0 / 3.0, policy="rust_required")
    assert caught.value.route_id == "background.chart_rhs"
    assert caught.value.__cause__ is load_error
    assert (sysconfig.get_config_var("SOABI") or "unknown") in str(caught.value)
    assert "Reinstall" in str(caught.value)
    assert "fallback is not automatic" in str(caught.value)


def test_nested_missing_dependency_is_incompatible_not_missing_extension(monkeypatch):
    nested = ModuleNotFoundError("No module named 'numpy'", name="numpy")
    _inject_native_import(monkeypatch, nested)

    with pytest.raises(policy.IncompatibleNativeExtensionError) as caught:
        policy.select_backend("background.chart_rhs", policy="rust_required")
    assert caught.value.__cause__ is nested


def test_arbitrary_native_initialization_error_is_not_suppressed(monkeypatch):
    unexpected = RuntimeError("native initializer defect")
    _inject_native_import(monkeypatch, unexpected)

    with pytest.raises(RuntimeError, match="native initializer defect") as caught:
        policy.select_backend("background.chart_rhs", policy="rust_required")
    assert caught.value is unexpected


def test_observed_extension_suffix_mismatch_is_typed(monkeypatch):
    native = _native_module(chart_rhs=lambda *_args: np.arange(5.0))
    native.__file__ = "/proof-fixture/bianchi_rustcore.cpython-311-x86_64-linux-gnu.so"
    _inject_native_import(monkeypatch, native)

    with pytest.raises(policy.IncompatibleNativeExtensionError) as caught:
        policy.select_backend("background.chart_rhs", policy="rust_required")
    assert "EXT_SUFFIX" in str(caught.value.__cause__)
    assert "SOABI" in str(caught.value)


def test_observed_distribution_version_mismatch_is_typed(monkeypatch):
    native = _native_module(chart_rhs=lambda *_args: np.arange(5.0))
    _inject_native_import(monkeypatch, native)
    monkeypatch.setattr(
        policy,
        "_distribution_version",
        lambda: ("0.0.9", "installed_distribution_metadata"),
    )

    with pytest.raises(policy.IncompatibleNativeExtensionError) as caught:
        policy.select_backend("background.chart_rhs", policy="rust_required")
    assert "0.0.9" in str(caught.value.__cause__)
    assert "0.1.0" in str(caught.value.__cause__)


def test_missing_required_native_symbol_is_incompatible(monkeypatch):
    _inject_native_import(monkeypatch, _native_module(unrelated=lambda: None))

    with pytest.raises(policy.IncompatibleNativeExtensionError) as caught:
        policy.select_backend("background.chart_rhs", policy="rust_required")
    assert isinstance(caught.value.__cause__, AttributeError)
    assert "chart_rhs" in str(caught.value)


def test_python_oracle_is_explicit_and_does_not_probe_native(monkeypatch):
    calls = _inject_native_import(
        monkeypatch,
        AssertionError("explicit Python oracle probed the native extension"),
    )

    import jax.numpy as jnp

    from bianchi.charts import class_a

    state = np.array([0.21, -0.13, 0.31, 0.19, 0.0])
    gamma = 4.0 / 3.0
    expected = np.asarray(
        class_a.rhs(
            0.0,
            class_a.StateA.from_array(jnp.asarray(state)),
            {"gamma": gamma},
        ).as_array()
    )
    observed = backend.chart_rhs(
        "class_a", state, gamma, policy=policy.BackendPolicy.PYTHON_ORACLE
    )
    np.testing.assert_array_equal(observed, expected)
    assert calls == []


def test_rust_required_wrapper_uses_native_and_never_imports_oracle(monkeypatch):
    state = np.array([0.21, -0.13, 0.31, 0.19, 0.0])
    expected = np.array([1.25, -2.5, 3.75, -4.0, 5.5])
    native_calls = []

    def native_rhs(chart, values, gamma, kappa=0.0):
        native_calls.append((chart, np.asarray(values).copy(), gamma, kappa))
        return expected.copy()

    native = _native_module(chart_rhs=native_rhs)
    payload_evidence = _inject_payload_evidence(monkeypatch)
    real_import = policy.importlib.import_module

    def guarded_import(name, package=None):
        if name == policy.NATIVE_MODULE_NAME:
            return native
        if name in backend._CHART_MODULES.values():
            raise AssertionError("rust_required reached the Python oracle")
        return real_import(name, package)

    monkeypatch.setattr(policy.importlib, "import_module", guarded_import)
    observed = backend.chart_rhs(
        "class_a", state, 4.0 / 3.0, policy=policy.BackendPolicy.RUST_REQUIRED
    )

    np.testing.assert_array_equal(observed, expected)
    assert len(native_calls) == 1
    assert payload_evidence.origins == [native.__file__]


def test_installed_native_wrapper_result_is_unchanged_from_direct_call(monkeypatch):
    load = policy.load_native()
    if not load.available:
        pytest.skip("installed native extension is exercised by the native-wheel job")
    assert load.module is not None and hasattr(load.module, "chart_rhs")
    payload_evidence = _inject_payload_evidence(monkeypatch)

    real_import = policy.importlib.import_module

    def forbid_oracle_import(name, package=None):
        if name in backend._CHART_MODULES.values():
            raise AssertionError("installed rust_required route reached Python oracle")
        return real_import(name, package)

    monkeypatch.setattr(policy.importlib, "import_module", forbid_oracle_import)
    state = np.array([0.21, -0.13, 0.31, 0.19, 0.0])
    gamma = 4.0 / 3.0
    direct = np.asarray(load.module.chart_rhs("class_a", state, gamma, 0.0))
    wrapped = backend.chart_rhs(
        "class_a", state, gamma, policy=policy.BackendPolicy.RUST_REQUIRED
    )
    np.testing.assert_array_equal(wrapped, direct)
    assert payload_evidence.origins == [policy._native_extension_origin(load.module)]


def test_public_route_inventory_uses_every_committed_contract_category():
    inventory = policy.public_route_inventory()
    allowed_states = {state.value for state in policy.PublicRouteState}

    assert set(inventory) == set(policy.ROUTE_CAPABILITIES)
    assert {
        state
        for record in inventory.values()
        for state in (
            record["supported_state"],
            record["explicit_oracle_state"],
            record["outside_native_domain_state"],
        )
    } == allowed_states

    for route_id, capability in policy.ROUTE_CAPABILITIES.items():
        record = inventory[route_id]
        assert set(record) == {
            "supported_state",
            "explicit_oracle_state",
            "outside_native_domain_state",
            "required_symbols",
            "transitional_reason",
        }
        assert record["supported_state"] == "native_required"
        assert record["explicit_oracle_state"] == (
            "python_oracle" if capability.python_oracle_supported else "unsupported"
        )
        assert record["outside_native_domain_state"] == (
            "legacy_python_transitional"
            if capability.transitional_reason is not None
            else "unsupported"
        )
        assert record["required_symbols"] == list(capability.required_symbols)
        assert record["transitional_reason"] == capability.transitional_reason


def test_capability_report_has_exact_fields_provenance_and_canonical_json(
    monkeypatch,
):
    missing = _missing_extension_error()
    _inject_native_import(monkeypatch, missing)
    report = policy.capability_report(policy.BackendPolicy.PYTHON_ORACLE)

    assert set(CAPABILITY_FIELDS) <= set(report)
    assert report["backend_policy"] == "python_oracle"
    assert report["python_abi"] == (sysconfig.get_config_var("SOABI") or "unknown")
    assert report["cargo_lock_sha256"] is None
    assert report["expected_cargo_lock_sha256"] == policy.EXPECTED_CARGO_LOCK_SHA256
    assert isinstance(report["optional_features"], list)
    assert report["optional_features"] == sorted(set(report["optional_features"]))

    provenance = report["provenance"]
    assert set(CAPABILITY_FIELDS) <= set(provenance)
    assert all(isinstance(provenance[name], str) and provenance[name] for name in CAPABILITY_FIELDS)

    canonical = json.dumps(
        report, sort_keys=True, separators=(",", ":"), allow_nan=False
    )
    assert json.loads(canonical) == report
    assert canonical == json.dumps(
        json.loads(canonical), sort_keys=True, separators=(",", ":"), allow_nan=False
    )
