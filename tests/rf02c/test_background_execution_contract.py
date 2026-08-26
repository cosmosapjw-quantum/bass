"""RF-02C step-1 native-provenance contract tests."""
from __future__ import annotations

import base64
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from types import ModuleType
import sysconfig
import zipfile

import numpy as np
import pytest

from bianchi import backend_policy as policy
from bianchi.q import group as q_group


RF02B_WHEEL_SHA256 = "f1b5940ed453c744b3a285898f079b9a8b0e43f66d99937fd7fa632f49d8c3f6"
RF02B_SHARED_OBJECT_SHA256 = "8b130c76f9c4a91d3eac9c3a37dd8b4c91ba45476d578c3260d87647693fabdd"
RF02B_SBOM_SHA256 = "af5a2b91780776ff550c17ae39aa37405889dab9350d6f8045a91a2fab15bb3c"
RF02C_WHEEL_SHA256 = "fc1b263e94a0d9e8e5458cc9d8fc0cadfd2f4549110ac2a775c0d652bdaf1629"
RF02C_SHARED_OBJECT_SHA256 = "ed4babb5f1d8d3ebef104f8d4bb209271aa9d577b7a8d72606208eacdfdb5478"
RF02C_SBOM_SHA256 = "7fb53a1096e8f1afa104121621a36d7b2e449b0535640abd9145f874a5e8ef4b"


def _extension_suffix() -> str:
    return sysconfig.get_config_var("EXT_SUFFIX") or ".so"


def _record_digest(value: bytes) -> str:
    return base64.urlsafe_b64encode(hashlib.sha256(value).digest()).decode().rstrip("=")


def _write_verified_install(tmp_path: Path):
    """Create a complete local installed-payload boundary, not a mocked verifier."""
    root = tmp_path / "distribution"
    files = {
        "bianchi_rustcore/__init__.py": b"# native package\n",
        f"bianchi_rustcore/native{_extension_suffix()}": b"native payload bytes",
        "bianchi_rustcore-0.1.0.dist-info/METADATA": b"metadata\n",
        "bianchi_rustcore-0.1.0.dist-info/WHEEL": b"wheel\n",
        "bianchi_rustcore-0.1.0.dist-info/sboms/bianchi_rustcore.cyclonedx.json": b"{}\n",
    }
    for relative, content in files.items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    record = "\n".join(
        f"{relative},sha256={_record_digest(content)},{len(content)}"
        for relative, content in files.items()
    ) + "\n"
    (root / "bianchi_rustcore-0.1.0.dist-info/RECORD").write_text(record)
    manifest = tuple(
        policy._NativeInstalledFile(relative, len(content), hashlib.sha256(content).hexdigest())
        for relative, content in files.items()
    )
    receipt = policy._NativePayloadReceipt(
        identity="test-rf02b",
        wheel_sha256="a" * 64,
        installed_files=manifest,
    )
    return root, receipt, files


def _install_distribution_seams(monkeypatch, root: Path, receipt):
    from bianchi.q.geometry_identity import geometry_route_identity

    class Distribution:
        def locate_file(self, name):
            return root / name

        def read_text(self, name):
            if name != "direct_url.json":
                return None
            return json.dumps({"archive_info": {"hashes": {"sha256": receipt.wheel_sha256}}})

    native = ModuleType(policy.NATIVE_MODULE_NAME)
    native.__file__ = str(root / receipt.installed_files[1].relative_path)
    native.rayon_thread_pool_size = lambda: 1
    native.chart_rhs = lambda *_args: None
    native.rf02c_execution_identity = lambda: json.dumps(geometry_route_identity())
    real_import = policy.importlib.import_module

    def injected(name, package=None):
        if name == policy.NATIVE_MODULE_NAME:
            return native
        return real_import(name, package)

    monkeypatch.setattr(policy, "_TRUSTED_NATIVE_PAYLOADS", (receipt,))
    monkeypatch.setattr(policy.metadata, "distribution", lambda _name: Distribution())
    monkeypatch.setattr(
        policy,
        "_distribution_version",
        lambda: (policy.EXPECTED_EXTENSION_VERSION, "test_distribution_metadata"),
    )
    monkeypatch.setattr(policy.importlib, "import_module", injected)
    policy._reset_native_loader_for_tests()
    return native


@pytest.fixture(autouse=True)
def _reset_loader(monkeypatch):
    monkeypatch.delenv(policy.DEVELOPMENT_OVERRIDE_ENV, raising=False)
    policy._reset_native_loader_for_tests()
    yield
    policy._reset_native_loader_for_tests()


def test_provenance_rf02b_receipt_uses_the_immutable_delta_identities():
    receipt = policy.RF02B_R4_DELTA_NATIVE_PAYLOAD
    assert receipt.wheel_sha256 == RF02B_WHEEL_SHA256
    fingerprints = {item.relative_path: item for item in receipt.installed_files}
    shared_object = fingerprints[
        "bianchi_rustcore/bianchi_rustcore.cpython-312-x86_64-linux-gnu.so"
    ]
    sbom = fingerprints[
        "bianchi_rustcore-0.1.0.dist-info/sboms/bianchi_rustcore.cyclonedx.json"
    ]
    assert (shared_object.size, shared_object.sha256) == (3336944, RF02B_SHARED_OBJECT_SHA256)
    assert (sbom.size, sbom.sha256) == (205826, RF02B_SBOM_SHA256)


def test_provenance_rf02c_receipt_uses_the_built_payload_identities():
    receipt = policy.RF02C_V2_NATIVE_PAYLOAD
    assert receipt.identity == "bass-rf02c-native-background-execution-v2"
    assert receipt.wheel_sha256 == RF02C_WHEEL_SHA256
    fingerprints = {item.relative_path: item for item in receipt.installed_files}
    shared_object = fingerprints[
        "bianchi_rustcore/bianchi_rustcore.cpython-312-x86_64-linux-gnu.so"
    ]
    sbom = fingerprints[
        "bianchi_rustcore-0.1.0.dist-info/sboms/bianchi_rustcore.cyclonedx.json"
    ]
    assert (shared_object.size, shared_object.sha256) == (
        3_771_016,
        RF02C_SHARED_OBJECT_SHA256,
    )
    assert (sbom.size, sbom.sha256) == (205_916, RF02C_SBOM_SHA256)


def test_provenance_verified_payload_dispatches_without_development_override(monkeypatch, tmp_path):
    root, receipt, _files = _write_verified_install(tmp_path)
    native = _install_distribution_seams(monkeypatch, root, receipt)

    selected = policy.select_backend("background.chart_rhs", policy="rust_required")

    assert selected.native_module is native
    assert selected.installed_payload_verified is True
    assert selected.development_override is False
    assert selected.diagnostic is None


@pytest.mark.parametrize("tamper", ("wheel", "shared_object", "sbom", "record", "install_manifest"))
def test_provenance_tamper_fails_closed_before_default_dispatch(monkeypatch, tmp_path, tamper):
    root, receipt, files = _write_verified_install(tmp_path)
    _install_distribution_seams(monkeypatch, root, receipt)
    dist_info = root / "bianchi_rustcore-0.1.0.dist-info"
    if tamper == "wheel":
        class WrongWheelDistribution:
            def locate_file(self, name):
                return root / name

            def read_text(self, name):
                if name != "direct_url.json":
                    return None
                return json.dumps({"archive_info": {"hashes": {"sha256": "b" * 64}}})

        monkeypatch.setattr(policy.metadata, "distribution", lambda _name: WrongWheelDistribution())
    elif tamper == "shared_object":
        (root / f"bianchi_rustcore/native{_extension_suffix()}").write_bytes(b"tampered")
    elif tamper == "sbom":
        (dist_info / "sboms/bianchi_rustcore.cyclonedx.json").write_bytes(b"tampered")
    elif tamper == "record":
        (dist_info / "RECORD").write_text("bianchi_rustcore/__init__.py,,0\n")
    else:
        altered = tuple(
            policy._NativeInstalledFile(item.relative_path, item.size, "0" * 64)
            if item.relative_path == "bianchi_rustcore/__init__.py"
            else item
            for item in receipt.installed_files
        )
        monkeypatch.setattr(
            policy,
            "_TRUSTED_NATIVE_PAYLOADS",
            (policy._NativePayloadReceipt(receipt.identity, receipt.wheel_sha256, altered),),
        )
    policy._reset_native_loader_for_tests()

    with pytest.raises(policy.UnverifiedNativePayloadError):
        policy.select_backend("background.chart_rhs", policy="rust_required")


def test_provenance_delta_verifier_rejects_a_wheel_with_corrupt_record(tmp_path):
    delta = tmp_path / "delta"
    wheel_dir = delta / "rf02b-wheel"
    wheel_dir.mkdir(parents=True)
    wheel = wheel_dir / "bianchi_rustcore-0.1.0-test.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr("bianchi_rustcore/native.so", b"payload")
        archive.writestr("bianchi_rustcore-0.1.0.dist-info/RECORD", "corrupt,row\n")
    wheel_sha = hashlib.sha256(wheel.read_bytes()).hexdigest()
    restore = {
        "wheel": {"filename": wheel.name, "sha256": wheel_sha},
        "shared_object": {"path": "bianchi_rustcore/native.so", "sha256": hashlib.sha256(b"payload").hexdigest()},
    }
    restore_path = delta / "RF02B_R4_DELTA_RESTORE.json"
    restore_path.write_text(json.dumps(restore))
    manifest = {
        "payloads": {
            "RF02B_R4_DELTA_RESTORE.json": hashlib.sha256(restore_path.read_bytes()).hexdigest(),
            f"rf02b-wheel/{wheel.name}": wheel_sha,
        }
    }
    (delta / "DELTA_MANIFEST.json").write_text(json.dumps(manifest))
    script = Path(__file__).resolve().parents[2] / "tools/native/verify_content_addressed_delta.py"

    result = subprocess.run(
        [sys.executable, str(script), "--delta-root", str(delta)],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "RECORD" in result.stderr


def test_capability_report_identifies_the_matched_rf02b_payload(monkeypatch, tmp_path):
    root, receipt, _files = _write_verified_install(tmp_path)
    receipt = replace(
        receipt,
        identity=policy.RF02B_R4_DELTA_NATIVE_PAYLOAD.identity,
        wheel_sha256=policy.RF02B_R4_DELTA_NATIVE_PAYLOAD.wheel_sha256,
    )
    _install_distribution_seams(monkeypatch, root, receipt)

    report = policy.capability_report()

    assert report["matched_native_payload_identity"] == receipt.identity
    assert report["matched_native_payload_wheel_sha256"] == receipt.wheel_sha256
    assert report["installed_native_payload_fingerprint_verified"] is True
    assert report["reference_native_build"] is None
    assert report["cargo_lock_binding_verified"] is False


class _GeometryNative:
    def __init__(self, identity):
        self.identity = identity
        self.calls = []

    def rf02c_execution_identity(self):
        return self.identity

    def qg_classify(self, n6, a3):
        self.calls.append((tuple(n6), tuple(a3)))
        return "I", "A", None, False, (0, 0, 0), 0


def test_public_geometry_route_validates_domain_and_native_identity(monkeypatch):
    from bianchi.q import geometry_identity

    native = _GeometryNative(json.dumps(geometry_identity.geometry_route_identity()))
    monkeypatch.setattr(q_group, "require_native", lambda _route: native)

    result = q_group.classify([1.0, 0.0, 0.0], [0.0, 0.0, 0.0])

    assert result["name"] == "I"
    assert native.calls == [((1.0, 0.0, 0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0))]
    with pytest.raises(ValueError, match="finite"):
        q_group.classify([float("nan"), 0.0, 0.0], [0.0, 0.0, 0.0])
    with pytest.raises(ValueError, match="Jacobi"):
        q_group.classify([1.0, 0.0, 0.0], [1.0, 0.0, 0.0])
    assert len(native.calls) == 1


def test_public_geometry_route_rejects_a_native_identity_mismatch(monkeypatch):
    from bianchi.q import geometry_identity

    mismatched = geometry_identity.geometry_route_identity()
    mismatched["routing_fingerprint"] = "0" * 64
    native = _GeometryNative(mismatched)
    monkeypatch.setattr(q_group, "require_native", lambda _route: native)

    with pytest.raises(q_group.GeometryRouteIdentityError, match="routing_fingerprint"):
        q_group.classify([1.0, 0.0, 0.0], [0.0, 0.0, 0.0])


def test_public_geometry_route_capability_requires_identity_symbol():
    expected = {
        "q.group.classify": "qg_classify",
        "q.group.jacobi_residual": "qg_jacobi",
        "q.group.structure_constants": "qg_structure_constants",
        "q.group.ricci3": "qg_ricci3",
        "q.group.curvature": "qg_curvature",
        "q.group.kappa": "qg_kappa",
        "q.group.roundtrip": None,
    }

    for route_id, operation_symbol in expected.items():
        required = policy.ROUTE_CAPABILITIES[route_id].required_symbols
        assert required[-1] == "rf02c_execution_identity"
        if operation_symbol is None:
            assert required == ("rf02c_execution_identity",)
        else:
            assert required == (operation_symbol, "rf02c_execution_identity")


def test_public_background_routes_require_the_common_execution_identity():
    expected = {
        "background.integrate": "integrate_background",
        "background.integrate_batch": "integrate_batch",
        "background.integrate_history": "integrate_background_history",
        "background.restart_history": "restart_background_history",
        "background.integrate_batch_history": "integrate_background_batch_history",
        "background.chart_rhs": "chart_rhs",
        "background.chart_jvp": "chart_jvp",
        "background.chart_constraints": "chart_constraints",
        "background.chart_project": "chart_project",
        "background.chart_project_checked": "chart_project_checked",
    }

    for route_id, operation_symbol in expected.items():
        assert policy.ROUTE_CAPABILITIES[route_id].required_symbols == (
            operation_symbol,
            "rf02c_execution_identity",
        )


def test_public_background_route_rejects_identity_before_numerical_execution(
    monkeypatch, tmp_path
):
    root, receipt, _files = _write_verified_install(tmp_path)
    native = _install_distribution_seams(monkeypatch, root, receipt)
    native.rf02c_execution_identity = lambda: json.dumps(
        {"identity_schema": "tampered"}
    )
    policy._reset_native_loader_for_tests()

    with pytest.raises(policy.NativeCapabilityIdentityError, match="identity mismatch"):
        policy.select_backend("background.chart_rhs", policy="rust_required")


def test_public_geometry_route_exposes_frozen_fingerprints():
    from bianchi.q import geometry_identity

    identity = geometry_identity.geometry_route_identity()

    assert identity["convention_hash"] == (
        "ac824b10e966f7cdb680d4a1a62ccfb414a9479e84f3d72231eeb4c88f649b33"
    )
    assert identity["state_schema_hash"] == (
        "9fa370fa32a5e0d7af7e8d97263db947a579d80c793e2818212b339a4b15e0f1"
    )
    assert identity["execution_contract_v2_hash"] == (
        "804826b9d5ce2f3333de0558447e351a8050dc8147d268e8a6055b6c5669e51c"
    )
    assert identity["event_registry_hash"] == (
        "8b3d342328b4549c797fca1c106181657f832a07fafed29eb498450465b43918"
    )
    assert identity["routing"] == {
        "class_b_exceptional_kappa": -9.0,
        "class_b_exceptional_routing_tolerance": 1e-9,
    }
    assert identity["scalar_chart_schema_hash"] == (
        "6e5fb51e028dc573a3759ac383dac948073e3a7f86f25564f26dfcbc10a10e7a"
    )
    assert identity["supported_chart_labels"] == [
        "class_a",
        "class_b",
        "exceptional",
        "type_ix_d",
        "type_ix_d_future",
    ]
    assert identity["native_payload_identity"] == (
        "bass-rf02c-native-background-execution-v2"
    )
    assert len(identity["native_capability_receipt"]) == 64


@pytest.mark.parametrize(
    "bad_n,bad_a,match",
    (
        ([[1.0, 0.0], [0.0, 1.0]], [0.0, 0.0, 0.0], "shape"),
        (
            [[1.0, 1.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
            [0.0, 0.0, 0.0],
            "symmetric",
        ),
        ([1.0, 0.0, 0.0], [0.0, float("inf"), 0.0], "finite"),
    ),
)
def test_public_geometry_route_rejects_hostile_shapes_before_native(
    monkeypatch, bad_n, bad_a, match
):
    native = _GeometryNative("unused")
    monkeypatch.setattr(q_group, "require_native", lambda _route: native)

    with pytest.raises(ValueError, match=match):
        q_group.classify(bad_n, bad_a)

    assert native.calls == []


def test_rf02c_randomized_jvp_receipt_is_canonical_and_direct_native(tmp_path):
    root = Path(__file__).resolve().parents[2]
    tool = root / "tools/audit/rf02c_randomized_jvp.py"
    first = tmp_path / "jvp-first.json"
    second = tmp_path / "jvp-second.json"

    for output in (first, second):
        completed = subprocess.run(
            [sys.executable, str(tool), "--root", str(root), "--output", str(output)],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        assert completed.returncode == 0, completed.stderr

    assert first.read_bytes() == second.read_bytes()
    receipt = json.loads(first.read_text())
    assert receipt["schema"] == "bass-rf02c-randomized-jvp-receipt/v1"
    assert receipt["status"] == "PASS"
    assert receipt["case_count"] == 250
    assert receipt["detector"]["frozen_corpus_source"].endswith(
        "rf02c_randomized_jvp.py"
    )
    assert receipt["execution"]["native_api"] == (
        "direct installed bianchi_rustcore.chart_rhs/chart_jvp"
    )
    assert receipt["execution"]["jax_used"] is False
    native_identity = receipt["execution"]["native_identity"]
    assert native_identity["wheel_filename"].endswith(".whl")
    assert len(native_identity["wheel_sha256"]) == 64
    assert native_identity["native_payload_identity"] == (
        "bass-rf02c-native-background-execution-v2"
    )
    assert len(native_identity["native_capability_receipt"]) == 64
    assert len(native_identity["execution_identity_sha256"]) == 64
    assert native_identity["execution_identity"] == (
        __import__("bianchi.q.geometry_identity", fromlist=["geometry_route_identity"])
        .geometry_route_identity()
    )
    canonical_receipt = first.read_text()
    assert "file://" not in canonical_receipt
    assert "/tmp/" not in canonical_receipt
    assert len(receipt["canonical_log_sha256"]) == 64
    assert len(receipt["canonical_result_sha256"]) == 64


def test_rf02c_composite_receipt_binds_parent_and_is_byte_identical(tmp_path):
    root = Path(__file__).resolve().parents[2]
    tool = root / "tools/audit/rf02c_compose_receipt.py"
    jvp = tmp_path / "jvp.json"
    detector = subprocess.run(
        [
            sys.executable,
            str(root / "tools/audit/rf02c_randomized_jvp.py"),
            "--root",
            str(root),
            "--output",
            str(jvp),
        ],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    assert detector.returncode == 0, detector.stderr
    first = tmp_path / "receipt-first.json"
    second = tmp_path / "receipt-second.json"

    for output in (first, second):
        completed = subprocess.run(
            [
                sys.executable,
                str(tool),
                "--root",
                str(root),
                "--jvp-receipt",
                str(jvp),
                "--output",
                str(output),
            ],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        assert completed.returncode == 0, completed.stderr

    assert first.read_bytes() == second.read_bytes()
    receipt = json.loads(first.read_text())
    assert receipt["schema"] == "bass-rf02c-composite-receipt/v1"
    assert receipt["inherited_randomized_jvp"]["status"] == (
        "NOT_REUSED_INCOMPLETE_REPLAY_MATERIAL"
    )
    assert receipt["inherited"]["git_parent"]["commit"] == (
        "0563c080e54fcd90d6160bec35e4f20d240d8d2e"
    )
    assert receipt["inherited"]["audit_manifest"]["git_blob"] == (
        "f4e1fd4de82a8ada0dcc4623af240eaa413bcba2"
    )
    assert receipt["execution_contract_v2"] == {
        "path": "docs/rust_first_runtime/RF02C_EXECUTION_CONTRACT_V2.json",
        "git_blob": "257d63d4ce1e3386caece4a85a3f72a2681d9032",
        "content_sha256": (
            "804826b9d5ce2f3333de0558447e351a8050dc8147d268e8a6055b6c5669e51c"
        ),
    }
    assert receipt["jvp_receipt"]["content_sha256"] == hashlib.sha256(
        jvp.read_bytes()
    ).hexdigest()
    assert len(receipt["canonical_result_sha256"]) == 64
    assert "jvp_native_identity_changes" in receipt["invalidation_predicates"]


def test_rf02c_composite_receipt_rejects_jvp_mutation(tmp_path):
    root = Path(__file__).resolve().parents[2]
    detector_tool = root / "tools/audit/rf02c_randomized_jvp.py"
    composer = root / "tools/audit/rf02c_compose_receipt.py"
    pristine = tmp_path / "jvp-pristine.json"
    completed = subprocess.run(
        [
            sys.executable,
            str(detector_tool),
            "--root",
            str(root),
            "--output",
            str(pristine),
        ],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    base = json.loads(pristine.read_text())
    mutations = (
        ("seed", lambda value: value["detector"].__setitem__("seed", 0)),
        (
            "log",
            lambda value: value["canonical_log"][0].__setitem__(
                "maximum_normalized_error", 0.5
            ),
        ),
        (
            "result_digest",
            lambda value: value.__setitem__("canonical_result_sha256", "0" * 64),
        ),
        (
            "source_digest",
            lambda value: value["detector"].__setitem__("source_sha256", "0" * 64),
        ),
    )
    for name, mutate in mutations:
        candidate = json.loads(json.dumps(base))
        mutate(candidate)
        candidate_path = tmp_path / f"jvp-{name}.json"
        candidate_path.write_text(json.dumps(candidate, sort_keys=True))
        result = subprocess.run(
            [
                sys.executable,
                str(composer),
                "--root",
                str(root),
                "--jvp-receipt",
                str(candidate_path),
                "--output",
                str(tmp_path / f"composite-{name}.json"),
            ],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        assert result.returncode != 0, name


def test_projection_postcondition_core_is_checked_and_raw_candidate_is_unchanged():
    root = Path(__file__).resolve().parents[2]
    charts_path = root / "_rustcore/src/ode/charts.rs"
    current = charts_path.read_text()
    base = subprocess.run(
        ["git", "show", "HEAD:_rustcore/src/ode/charts.rs"],
        cwd=root,
        text=True,
        capture_output=True,
        check=True,
    ).stdout

    raw_start = "pub fn project_constraints("
    current_raw_end = (
        "/// RF-02B scalar state schema frozen into the RF-02C checked-projection receipt."
    )
    base_raw_end = "/// 야코비안-벡터 곱"
    assert current[current.index(raw_start) : current.index(current_raw_end)] == base[
        base.index(raw_start) : base.index(base_raw_end)
    ]
    assert "pub fn project_constraints_checked(" in current
    assert "CHECKED_PROJECTION_MAX_ITERATIONS: usize = 8" in current
    assert "CHECKED_PROJECTION_DAMPING: f64 = 1e-12" in current
    for failure_code in (
        "PROJECTION_INVALID_INPUT",
        "PROJECTION_SINGULAR",
        "PROJECTION_NONFINITE",
        "PROJECTION_NON_MONOTONE",
        "PROJECTION_NOT_CONVERGED",
        "PROJECTION_PHYSICAL_DOMAIN",
    ):
        assert failure_code in current
    assert "fn chart_project_checked" not in (root / "_rustcore/src/lib.rs").read_text()


def test_rf02b_payload_is_development_only_with_explicit_diagnostic(
    monkeypatch, tmp_path
):
    root, receipt, _files = _write_verified_install(tmp_path)
    receipt = replace(
        receipt,
        identity=policy.RF02B_R4_DELTA_NATIVE_PAYLOAD.identity,
    )
    native = _install_distribution_seams(monkeypatch, root, receipt)
    del native.rf02c_execution_identity
    policy._reset_native_loader_for_tests()

    with pytest.raises(policy.IncompatibleNativeExtensionError, match="identity"):
        policy.select_backend("background.chart_rhs", policy="rust_required")

    with pytest.warns(
        policy.UnverifiedNativeDevelopmentWarning,
        match="RF02B_DEVELOPMENT_ONLY_NATIVE_PAYLOAD",
    ):
        selected = policy.select_backend(
            "background.chart_rhs",
            policy="rust_required",
            development_override=True,
        )
    assert selected.native_module is native
    assert selected.installed_payload_verified is True
    assert selected.development_override is True
    assert selected.diagnostic is not None
    assert "RF02B_DEVELOPMENT_ONLY_NATIVE_PAYLOAD" in selected.diagnostic


def test_rf02c_domain_adapter_bodies_are_out_of_lib_rs():
    root = Path(__file__).resolve().parents[2]
    lib_rs = (root / "_rustcore/src/lib.rs").read_text()
    background = (root / "_rustcore/src/python/background.rs").read_text()
    geometry = (root / "_rustcore/src/python/geometry.rs").read_text()
    registration = (root / "_rustcore/src/python/register.rs").read_text()

    for function_name in (
        "make_chart",
        "chart_rhs",
        "chart_project_checked",
        "integrate_background",
        "integrate_batch",
        "qg_classify",
        "qg_curvature",
    ):
        assert f"fn {function_name}" not in lib_rs
    assert "register_background(m)?" in lib_rs
    assert "register_geometry(&m)?" in lib_rs
    assert "fn chart_project_checked" in background
    assert "fn integrate_background" in background
    assert "fn qg_classify" in geometry
    assert "wrap_pyfunction!(chart_project_checked" in registration
    assert "wrap_pyfunction!(qg_classify" in registration


def _rf02c_native_entrypoint(name: str):
    import bianchi_rustcore

    return getattr(bianchi_rustcore, name)


def _integrate_history(chart, y0, t_eval, gamma, kappa=0.0, **kwargs):
    return _rf02c_native_entrypoint("integrate_background_history")(
        chart,
        np.asarray(y0, dtype=np.float64),
        np.asarray(t_eval, dtype=np.float64),
        gamma,
        kappa,
        **kwargs,
    )


def test_rf02c_trajectory_routes_are_registered_as_one_call_native_owners():
    root = Path(__file__).resolve().parents[2]
    background = (root / "_rustcore/src/python/background.rs").read_text()
    registration = (root / "_rustcore/src/python/register.rs").read_text()
    for symbol in (
        "integrate_background_history",
        "restart_background_history",
        "integrate_background_batch_history",
    ):
        assert f"fn {symbol}" in background
        assert f"wrap_pyfunction!({symbol}" in "".join(registration.split())
    assert "Python::with_gil" not in background


def test_rf02c_zero_length_and_initial_domain_rules_are_typed():
    completed = _integrate_history("class_a", [0.3, 0.0, 0.0, 0.0, 0.0], [0.0], 1.0)
    assert completed["status"] == "COMPLETED"
    assert len(completed["samples"]) == 1
    assert completed["samples"][0]["sample_kind"] == "initial"
    assert completed["events"] == []

    invalid = _integrate_history("class_a", [2.0, 0.0, 0.0, 0.0, 0.0], [0.0], 1.0)
    assert invalid["status"] == "FAILED"
    assert invalid["failure"]["code"] == "INITIAL_DOMAIN_VIOLATION"


def test_rf02c_history_stores_raw_and_certificate_margins_separately():
    first = _integrate_history(
        "class_a", [0.3, 0.0, 0.0, 0.0, 0.0], [0.0, 0.1], 1.0, rtol=1e-8, atol=1e-10
    )
    second = _integrate_history(
        "class_a", [0.3, 0.0, 0.0, 0.0, 0.0], [0.0, 0.1], 1.0, rtol=1e-10, atol=1e-12
    )
    for result, rtol, atol in (
        (first, 1e-8, 1e-10),
        (second, 1e-10, 1e-12),
    ):
        sample = result["samples"][-1]
        raw = sample["domain_margins_raw"]["Omega"]
        certificate = sample["domain_margins_certificate"]["Omega"]
        scale = atol + rtol * max(1.0, np.max(np.abs(sample["state"])))
        assert raw == sample["Omega"]
        assert certificate == raw + scale
        assert certificate != raw


def test_rf02c_type_ix_recollapse_event_transition_and_restart_are_atomic():
    h0 = 0.8
    n0 = np.sqrt(2.0 * (1.0 - h0 * h0))
    result = _integrate_history(
        "type_ix_d_future",
        [h0, 0.0, 0.0, 0.0, n0, n0, n0],
        [0.0, 4.0],
        1.0,
    )
    root_samples = [sample for sample in result["samples"] if sample["sample_kind"] == "event_root"]
    assert len(root_samples) == 1
    root = root_samples[0]
    event = result["events"][0]
    transition = result["transitions"][0]
    assert event["event_id"] == "type_ix_recollapse"
    assert event["sample_index"] == transition["sample_index"] == root["sample_index"]
    assert transition["transition_id"] == "type_ix_expanding_to_contracting"
    assert transition["state_bytes_preserved"] is True
    assert result["segments"][0]["status"] == "TRANSITION_REQUIRED"
    assert result["segments"][1]["phase"] == "contracting"
    assert sum(sample["tau_bits"] == root["tau_bits"] for sample in result["samples"]) == 1
    expected_root = np.log((1.0 + h0) / (1.0 - h0)) + 2.0 * np.arctan(h0)
    root_tolerance = 8.0 * (1e-12 + 1e-10 * max(1.0, abs(expected_root)))
    assert abs(root["tau"] - expected_root) <= root_tolerance
    assert abs(root["state"][0]) <= event["epsilon_g"]


def test_rf02c_restart_reuses_byte_identical_root_and_stored_latch():
    h0 = 0.8
    n0 = np.sqrt(2.0 * (1.0 - h0 * h0))
    first = _integrate_history(
        "type_ix_d_future",
        [h0, 0.0, 0.0, 0.0, n0, n0, n0],
        [0.0, 3.8],
        1.0,
    )
    restarted = _rf02c_native_entrypoint("restart_background_history")(first, 4.0)
    event = first["events"][0]
    transition = first["transitions"][0]
    assert event["epsilon_g"] == restarted["events"][0]["epsilon_g"]
    assert event["tau_bits"] == transition["tau_bits"]
    assert transition["state_bytes_preserved"] is True
    assert restarted["samples"][transition["sample_index"]]["state_sha256"] == first[
        "samples"
    ][transition["sample_index"]]["state_sha256"]


@pytest.mark.parametrize(
    "chart,y0,gamma,kappa",
    (
        ("class_a", [0.3, 0.0, 0.0, 0.0, 0.0], 1.0, 0.0),
        ("class_b", [-0.4, 0.24, 0.0, 0.36, np.sqrt(2.16)], 1.3, 4.0),
        (
            "exceptional",
            [-0.5, 1.0 / (2.0 * np.sqrt(3.0)), 0.0, 0.0, 0.0, 1.0 / np.sqrt(12.0)],
            4.0 / 3.0,
            0.0,
        ),
        ("exceptional", [-0.4, 0.1, 0.05, -0.05669872981077808, 0.6, 0.15], 1.2, 0.0),
        ("type_ix_d", [0.0, 0.0, 0.0, 0.0, np.sqrt(2.0), np.sqrt(2.0), np.sqrt(2.0)], 2.0 / 3.0, 0.0),
    ),
)
def test_rf02c_frozen_nontransition_trajectory_oracles(chart, y0, gamma, kappa):
    result = _integrate_history(chart, y0, [0.0, 0.1], gamma, kappa)
    assert result["status"] == "COMPLETED"
    assert result["failure"] is None
    assert len(result["samples"]) == 2
    observed = np.asarray(result["samples"][-1]["state"], dtype=np.float64)
    initial = np.asarray(y0, dtype=np.float64)
    if chart == "class_a":
        u0 = initial[0] ** 2
        u = u0 * np.exp(-0.3) / (1.0 - u0 + u0 * np.exp(-0.3))
        expected = np.asarray([np.sqrt(u), 0.0, 0.0, 0.0, 0.0])
    elif chart == "exceptional" and gamma == pytest.approx(1.2):
        from bianchi import integrate as python_integrate
        from bianchi.charts import exceptional as python_exceptional
        import jax.numpy as jnp

        times = jnp.asarray([0.0, 0.1])
        config = python_integrate.SolverConfig(
            rtol=1e-11, atol=1e-13, max_steps=200_000
        )
        oracle = python_integrate.solve_jit(
            python_exceptional.rhs,
            python_exceptional.StateE.from_array(jnp.asarray(initial)),
            0.0,
            0.1,
            {"gamma": gamma},
            ts=times,
            cfg=config,
        )
        assert python_integrate.status(oracle)["accepted"] is True
        expected = np.asarray(oracle.ys.as_array(), dtype=np.float64)[:, -1]
    else:
        expected = initial

    scale = 1e-12 + 1e-10 * np.maximum(
        1.0, np.maximum(np.abs(observed), np.abs(expected))
    )
    assert float(np.max(np.abs(observed - expected) / scale)) <= 1.0
    for sample in result["samples"]:
        assert sample["normalized_constraint_residual"] <= 1.0
        assert all(
            value >= 0.0 for value in sample["domain_margins_certificate"].values()
        )


def test_rf02c_batch_preserves_order_failure_isolation_and_thread_identity():
    batch = _rf02c_native_entrypoint("integrate_background_batch_history")
    states = np.asarray(
        [
            [0.3, 0.0, 0.0, 0.0, 0.0],
            [2.0, 0.0, 0.0, 0.0, 0.0],
            [0.2, 0.0, 0.0, 0.0, 0.0],
        ],
        dtype=np.float64,
    )
    one = batch("class_a", states, np.asarray([0.0, 0.1]), 1.0, 0.0, threads=1)
    many = batch("class_a", states, np.asarray([0.0, 0.1]), 1.0, 0.0, threads=4)
    assert [member["status"] for member in one] == ["COMPLETED", "FAILED", "COMPLETED"]
    assert one == many
    assert one[0]["samples"][-1]["state_sha256"] == many[0]["samples"][-1]["state_sha256"]
    assert one[2]["samples"][-1]["state_sha256"] == many[2]["samples"][-1]["state_sha256"]


def test_rf02c_verified_public_routes_execute_trajectory_and_batch_without_override():
    single_native = policy.require_native("background.integrate_history")
    single = single_native.integrate_background_history(
        "class_a",
        np.asarray([0.3, 0.0, 0.0, 0.0, 0.0]),
        np.asarray([0.0, 0.1]),
        1.0,
        0.0,
    )
    assert single["status"] == "COMPLETED"

    batch_native = policy.require_native("background.integrate_batch_history")
    assert batch_native is single_native
    batch = batch_native.integrate_background_batch_history(
        "class_a",
        np.asarray(
            [
                [0.3, 0.0, 0.0, 0.0, 0.0],
                [0.2, 0.0, 0.0, 0.0, 0.0],
            ]
        ),
        np.asarray([0.0, 0.1]),
        1.0,
        0.0,
        threads=2,
    )
    assert [member["status"] for member in batch] == ["COMPLETED", "COMPLETED"]
    report = policy.capability_report()
    assert report["matched_native_payload_identity"] == (
        "bass-rf02c-native-background-execution-v2"
    )
    assert report["production_native_dispatch_permitted"] is True
