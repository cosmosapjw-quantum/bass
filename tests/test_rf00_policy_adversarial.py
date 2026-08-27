"""Adversarial closure for RF-00 native identity and Mode-B routing."""
from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
import sysconfig
from types import ModuleType, SimpleNamespace

import numpy as np
import pytest

from bianchi import backend_policy as policy
from bianchi.q.geometry_identity import geometry_route_identity
from bianchi.q import polstate


@pytest.fixture(autouse=True)
def _isolated_native_loader_cache(monkeypatch):
    monkeypatch.delenv(policy.DEVELOPMENT_OVERRIDE_ENV, raising=False)
    policy._reset_native_loader_for_tests()
    yield
    policy._reset_native_loader_for_tests()


def _extension_suffix() -> str:
    return sysconfig.get_config_var("EXT_SUFFIX") or ".so"


def _inject_native_import(monkeypatch, module: ModuleType) -> None:
    real_import = policy.importlib.import_module

    def injected(name, package=None):
        if name == policy.NATIVE_MODULE_NAME:
            return module
        return real_import(name, package)

    monkeypatch.setattr(policy.importlib, "import_module", injected)
    monkeypatch.setattr(
        policy,
        "_distribution_version",
        lambda: (policy.EXPECTED_EXTENSION_VERSION, "test_distribution_metadata"),
    )


class _PayloadEvidence:
    """Callable payload-verification seam that supports the cache-reset fixture."""

    def __init__(self, verified: bool, reason: str):
        self.verified = verified
        self.reason = reason
        self.origins = []

    def __call__(self, native_origin):
        self.origins.append(native_origin)
        return self.verified, self.reason

    def cache_clear(self):
        return None


def _inject_payload_evidence(monkeypatch, *, verified: bool, reason: str):
    evidence = _PayloadEvidence(verified, reason)
    monkeypatch.setattr(policy, "_installed_native_payload_matches", evidence)
    return evidence


def _native_module(**symbols):
    module = ModuleType(policy.NATIVE_MODULE_NAME)
    module.__file__ = f"/proof/bianchi_rustcore{_extension_suffix()}"
    module.rayon_thread_pool_size = lambda: 1
    module.rf02c_execution_identity = lambda: json.dumps(geometry_route_identity())
    for name, value in symbols.items():
        setattr(module, name, value)
    return module


def _modeb_inputs():
    e = np.array(((1.0, 0.0, 0.0), (0.0, 1.0, 0.0)))
    w = np.array((0.4, 0.6))
    J = np.arange(36.0).reshape(2, 2, 3, 3) / 37.0
    return e, w, J


def test_python_shadow_module_is_incompatible_not_available(monkeypatch):
    shadow = ModuleType(policy.NATIVE_MODULE_NAME)
    shadow.__file__ = "/shadow/bianchi_rustcore.py"
    shadow.qp_collide_modeb = lambda *_args: None
    _inject_native_import(monkeypatch, shadow)

    load = policy.load_native()
    assert load.state is policy.NativeLoadState.INCOMPATIBLE_EXTENSION
    assert load.module is None
    assert "native extension origin" in (load.detail or "")
    with pytest.raises(policy.IncompatibleNativeExtensionError):
        policy.select_backend("q.polstate.collide_modeb", policy="rust_required")


def test_pre_rf00_native_wheel_without_runtime_capability_is_incompatible(
    monkeypatch,
):
    module = ModuleType(policy.NATIVE_MODULE_NAME)
    module.__file__ = f"/proof/bianchi_rustcore{_extension_suffix()}"
    module.qp_collide_modeb = lambda *_args: None
    _inject_native_import(monkeypatch, module)

    load = policy.load_native()
    assert load.state is policy.NativeLoadState.INCOMPATIBLE_EXTENSION
    assert "rayon_thread_pool_size" in (load.detail or "")


def test_maturin_nested_extension_origin_is_accepted(monkeypatch):
    wrapper = ModuleType(policy.NATIVE_MODULE_NAME)
    wrapper.__file__ = "/proof/bianchi_rustcore/__init__.py"
    wrapper.qp_collide_modeb = lambda *_args: None
    wrapper.rayon_thread_pool_size = lambda: 1
    nested = ModuleType(f"{policy.NATIVE_MODULE_NAME}.{policy.NATIVE_MODULE_NAME}")
    nested.__file__ = f"/proof/bianchi_rustcore/bianchi_rustcore{_extension_suffix()}"
    wrapper.bianchi_rustcore = nested
    _inject_native_import(monkeypatch, wrapper)

    load = policy.load_native()
    assert load.state is policy.NativeLoadState.AVAILABLE
    assert load.module is wrapper
    assert policy._native_extension_origin(wrapper) == nested.__file__


def test_nested_extension_with_wrong_abi_is_incompatible(monkeypatch):
    wrapper = ModuleType(policy.NATIVE_MODULE_NAME)
    wrapper.__file__ = "/proof/bianchi_rustcore/__init__.py"
    wrapper.qp_collide_modeb = lambda *_args: None
    nested = ModuleType(f"{policy.NATIVE_MODULE_NAME}.{policy.NATIVE_MODULE_NAME}")
    nested.__file__ = "/proof/bianchi_rustcore/bianchi_rustcore.cpython-311-wrong.so"
    wrapper.bianchi_rustcore = nested
    _inject_native_import(monkeypatch, wrapper)

    load = policy.load_native()
    assert load.state is policy.NativeLoadState.INCOMPATIBLE_EXTENSION
    assert "EXT_SUFFIX" in (load.detail or "")


def test_r2_capability_binds_loaded_so_to_distribution_owned_file(
    monkeypatch, tmp_path: Path
):
    suffix = _extension_suffix()
    relative = f"bianchi_rustcore/native{suffix}"
    owned = tmp_path / "distribution" / relative
    shadow = tmp_path / "shadow" / f"native{suffix}"
    owned.parent.mkdir(parents=True)
    shadow.parent.mkdir(parents=True)
    payload = b"synthetic-r2-extension-fingerprint"
    owned.write_bytes(payload)
    shadow.write_bytes(payload)
    digest = hashlib.sha256(payload).hexdigest()
    metadata_relative = "bianchi_rustcore-0.1.0.dist-info/METADATA"
    metadata_path = tmp_path / "distribution" / metadata_relative
    metadata_path.parent.mkdir(parents=True)
    metadata_payload = b"Name: bianchi-rustcore\nVersion: 0.1.0\n"
    metadata_path.write_bytes(metadata_payload)
    metadata_digest = hashlib.sha256(metadata_payload).hexdigest()
    wheel_digest = hashlib.sha256(b"synthetic-r2-wheel").hexdigest()

    def record_digest(value: str) -> str:
        return base64.urlsafe_b64encode(bytes.fromhex(value)).decode().rstrip("=")

    record_relative = "bianchi_rustcore-0.1.0.dist-info/RECORD"
    record_path = tmp_path / "distribution" / record_relative
    record_path.write_text(
        "\n".join(
            (
                f"{relative},sha256={record_digest(digest)},{len(payload)}",
                f"{metadata_relative},sha256={record_digest(metadata_digest)},{len(metadata_payload)}",
            )
        )
        + "\n",
        encoding="utf-8",
    )

    receipt = policy._NativePayloadReceipt(
        identity="rf01_r4_loaded_distribution_file_fingerprint",
        wheel_sha256=wheel_digest,
        installed_files=(
            policy._NativeInstalledFile(relative, len(payload), digest),
            policy._NativeInstalledFile(
                metadata_relative,
                len(metadata_payload),
                metadata_digest,
            ),
        ),
    )

    class Distribution:
        def locate_file(self, name):
            return tmp_path / "distribution" / name

        def read_text(self, name):
            if name == "direct_url.json":
                return json.dumps(
                    {"archive_info": {"hashes": {"sha256": wheel_digest}}}
                )
            return None

    monkeypatch.setattr(policy.metadata, "distribution", lambda _name: Distribution())
    monkeypatch.setattr(
        policy,
        "_distribution_version",
        lambda: (policy.EXPECTED_EXTENSION_VERSION, "installed_distribution_metadata"),
    )
    monkeypatch.setattr(
        policy,
        "_TRUSTED_NATIVE_PAYLOADS",
        (receipt,),
    )

    active = {"origin": shadow}
    monkeypatch.setenv("RAYON_NUM_THREADS", "7")

    real_import = policy.importlib.import_module

    def injected(name, package=None):
        if name != policy.NATIVE_MODULE_NAME:
            return real_import(name, package)
        module = ModuleType(policy.NATIVE_MODULE_NAME)
        module.__file__ = str(active["origin"])
        module.rayon_thread_pool_size = lambda: 3
        return module

    monkeypatch.setattr(policy.importlib, "import_module", injected)
    report = policy.capability_report()
    assert report["native_shared_object_origin"] == str(shadow)
    assert not report["installed_native_build_verified"]
    assert not report["cargo_lock_binding_verified"]
    assert report["rayon_threads"] == report["thread_pool_size"] == 3
    assert report["configured_rayon_threads"] == 7
    assert report["provenance"]["rayon_threads"] == (
        "native_extension.rayon_thread_pool_size"
    )
    assert report["provenance"]["configured_rayon_threads"] == "RAYON_NUM_THREADS"

    active["origin"] = owned
    policy._reset_native_loader_for_tests()
    report = policy.capability_report()
    assert report["native_shared_object_origin"] == str(owned)
    assert report["installed_native_build_verified"]
    assert report["cargo_lock_binding_verified"]
    assert (
        report["provenance"]["cargo_lock_sha256"]
        == "rf01_r4_loaded_distribution_file_fingerprint"
    )


def test_unverified_native_payload_fails_closed_by_default(monkeypatch):
    native = _native_module(chart_rhs=lambda *_args: np.arange(5.0))
    _inject_native_import(monkeypatch, native)
    evidence = _inject_payload_evidence(
        monkeypatch,
        verified=False,
        reason="test_unverified_source_build",
    )

    with pytest.raises(policy.UnverifiedNativePayloadError) as caught:
        policy.select_backend("background.chart_rhs", policy="rust_required")

    assert caught.value.route_id == "background.chart_rhs"
    assert "test_unverified_source_build" in str(caught.value)
    assert policy.DEVELOPMENT_OVERRIDE_ENV in str(caught.value)
    assert evidence.origins == [native.__file__]


def test_exact_development_override_warns_and_returns_typed_diagnostic(monkeypatch):
    native = _native_module(chart_rhs=lambda *_args: np.arange(5.0))
    _inject_native_import(monkeypatch, native)
    evidence = _inject_payload_evidence(
        monkeypatch,
        verified=False,
        reason="test_unverified_source_build",
    )
    assert policy.DEVELOPMENT_OVERRIDE_ENV == "BASS_ALLOW_UNVERIFIED_NATIVE_DEV"
    monkeypatch.setenv(policy.DEVELOPMENT_OVERRIDE_ENV, "1")

    with pytest.warns(policy.UnverifiedNativeDevelopmentWarning) as recorded:
        selected = policy.select_backend(
            "background.chart_rhs", policy=policy.BackendPolicy.RUST_REQUIRED
        )

    assert selected.policy is policy.BackendPolicy.RUST_REQUIRED
    assert selected.native_module is native
    assert selected.load_state is policy.NativeLoadState.AVAILABLE
    assert selected.installed_payload_verified is False
    assert selected.development_override is True
    assert selected.diagnostic is not None
    assert selected.diagnostic.startswith("UNVERIFIED_DEVELOPMENT_NATIVE_PAYLOAD:")
    assert "route=background.chart_rhs" in selected.diagnostic
    assert "reason=test_unverified_source_build" in selected.diagnostic
    assert str(recorded[0].message) == selected.diagnostic
    assert evidence.origins == [native.__file__]


@pytest.mark.parametrize("override", ("0", "true", "yes", " 1", "1 "))
def test_invalid_development_override_value_is_typed(monkeypatch, override):
    native = _native_module(chart_rhs=lambda *_args: np.arange(5.0))
    _inject_native_import(monkeypatch, native)
    _inject_payload_evidence(
        monkeypatch,
        verified=False,
        reason="test_unverified_source_build",
    )
    monkeypatch.setenv(policy.DEVELOPMENT_OVERRIDE_ENV, override)

    with pytest.raises(policy.BackendPolicyError) as caught:
        policy.select_backend("background.chart_rhs", policy="rust_required")

    assert caught.value.route_id == "background.chart_rhs"
    assert f"{policy.DEVELOPMENT_OVERRIDE_ENV} must be exactly '1'" in str(caught.value)
    assert repr(override) in str(caught.value)


def test_verified_installed_payload_dispatches_without_override(monkeypatch):
    native = _native_module(chart_rhs=lambda *_args: np.arange(5.0))
    _inject_native_import(monkeypatch, native)
    evidence = _inject_payload_evidence(
        monkeypatch,
        verified=True,
        reason="test_verified_installed_payload",
    )

    selected = policy.select_backend(
        "background.chart_rhs", policy=policy.BackendPolicy.RUST_REQUIRED
    )

    assert selected.native_module is native
    assert selected.installed_payload_verified is True
    assert selected.development_override is False
    assert selected.diagnostic is None
    assert evidence.origins == [native.__file__]


@pytest.mark.parametrize(
    ("requested", "normalized"),
    (
        ("python", policy.BackendPolicy.PYTHON_ORACLE),
        ("python_oracle", "python_oracle"),
        (policy.BackendPolicy.PYTHON_ORACLE, policy.BackendPolicy.PYTHON_ORACLE),
    ),
)
def test_modeb_python_alias_and_typed_policy_use_selector_and_preserve_output(
    monkeypatch, requested, normalized
):
    e, w, J = _modeb_inputs()
    calls = []

    def selected(route_id, *, policy):
        calls.append((route_id, policy))
        return SimpleNamespace(
            policy=policy_module.BackendPolicy.PYTHON_ORACLE,
            native_module=None,
        )

    policy_module = policy
    monkeypatch.setattr(polstate, "select_backend", selected)
    monkeypatch.setattr(
        polstate.PL, "collide", lambda _e, _w, block, x: np.asarray(block) + x
    )

    observed = polstate.collide_modeb(e, w, J, 2, 0.25, backend=requested)
    np.testing.assert_array_equal(observed, J + 0.25)
    assert calls == [("q.polstate.collide_modeb", normalized)]


@pytest.mark.parametrize(
    ("requested", "normalized"),
    (
        ("rust", policy.BackendPolicy.RUST_REQUIRED),
        ("rust_required", "rust_required"),
        (policy.BackendPolicy.RUST_REQUIRED, policy.BackendPolicy.RUST_REQUIRED),
    ),
)
def test_modeb_rust_alias_and_typed_policy_use_selector_and_preserve_output(
    monkeypatch, requested, normalized
):
    e, w, J = _modeb_inputs()
    calls = []

    class Native:
        @staticmethod
        def qp_collide_modeb(_e, _w, packed, _n_p, _x):
            return np.asarray(packed)

    def selected(route_id, *, policy):
        calls.append((route_id, policy))
        return SimpleNamespace(
            policy=policy_module.BackendPolicy.RUST_REQUIRED,
            native_module=Native,
        )

    policy_module = policy
    monkeypatch.setattr(polstate, "select_backend", selected)
    observed = polstate.collide_modeb(e, w, J, 2, 0.25, backend=requested)
    expected = polstate.PL.unpack9(
        polstate.PL.pack9(J.reshape(-1, 3, 3))
    ).reshape(J.shape)
    np.testing.assert_array_equal(observed, expected)
    assert calls == [("q.polstate.collide_modeb", normalized)]


@pytest.mark.parametrize("requested", (None, "unknown_backend"))
def test_modeb_rejects_unknown_backend(monkeypatch, requested):
    e, w, J = _modeb_inputs()
    monkeypatch.setattr(
        policy.importlib,
        "import_module",
        lambda: pytest.fail("invalid backend reached the native loader"),
    )
    with pytest.raises(policy.BackendPolicyError):
        polstate.collide_modeb(e, w, J, 2, 0.25, backend=requested)


@pytest.mark.parametrize(
    ("load", "error_type"),
    (
        (
            policy.NativeLoadResult(
                policy.NativeLoadState.MISSING_EXTENSION,
                None,
                ModuleNotFoundError(
                    "No module named 'bianchi_rustcore'",
                    name=policy.NATIVE_MODULE_NAME,
                ),
                "missing",
            ),
            policy.MissingNativeExtensionError,
        ),
        (
            policy.NativeLoadResult(
                policy.NativeLoadState.INCOMPATIBLE_EXTENSION,
                None,
                ImportError("ABI mismatch"),
                "ABI mismatch",
            ),
            policy.IncompatibleNativeExtensionError,
        ),
    ),
)
def test_modeb_rust_required_propagates_typed_native_failure(
    monkeypatch, load, error_type
):
    e, w, J = _modeb_inputs()
    real_import = policy.importlib.import_module

    def injected(name, package=None):
        if name != policy.NATIVE_MODULE_NAME:
            return real_import(name, package)
        assert load.cause is not None
        raise load.cause

    monkeypatch.setattr(policy.importlib, "import_module", injected)
    with pytest.raises(error_type) as caught:
        polstate.collide_modeb(e, w, J, 2, 0.25, backend="rust")
    assert caught.value.route_id == "q.polstate.collide_modeb"
