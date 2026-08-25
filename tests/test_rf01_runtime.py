"""Focused RF-01 contract for the modular native runtime substrate.

The fixture is deliberately synthetic.  These tests do not migrate or exercise
an RF-02+ production physics kernel and they contain no performance acceptance
threshold.
"""

from __future__ import annotations

import gc
import hashlib
import threading
import time

import numpy as np
import pytest


rust = pytest.importorskip("bianchi_rustcore")


def _plan(threads: int = 1, size: int = 64):
    return rust.RuntimePlan(
        thread_count=threads,
        fixture_size=size,
        cpu_variant="scalar",
        require_finite=True,
    )


def _digest(values: np.ndarray) -> str:
    return hashlib.sha256(values.tobytes(order="C")).hexdigest()


def test_runtime_plan_validates_configuration_and_owns_private_pool(monkeypatch):
    with pytest.raises(rust.RuntimeConfigError, match="thread_count"):
        rust.RuntimePlan(thread_count=0)
    with pytest.raises(rust.RuntimeConfigError, match="thread_count"):
        rust.RuntimePlan(thread_count=-1)
    with pytest.raises(rust.RuntimeConfigError, match="fixture_size"):
        rust.RuntimePlan(thread_count=1, fixture_size=0)
    with pytest.raises(rust.RuntimeConfigError, match="fixture_size"):
        rust.RuntimePlan(thread_count=1, fixture_size=2**63)
    with pytest.raises(rust.UnsupportedCapabilityError, match="scalar"):
        rust.RuntimePlan(thread_count=1, cpu_variant="avx2")

    monkeypatch.setenv("RAYON_NUM_THREADS", "19")
    one = _plan(1)
    two = _plan(2)
    assert one.thread_count == one.private_pool_size == 1
    assert two.thread_count == two.private_pool_size == 2
    assert one.fingerprint != two.fingerprint


def test_plan_fingerprint_and_capability_receipt_are_canonical():
    a = _plan(2, 96)
    b = _plan(2, 96)
    assert a.fingerprint == b.fingerprint
    receipt = a.capability_receipt()
    assert receipt == b.capability_receipt()
    assert receipt["schema"] == "bass-runtime-plan-capability-v1"
    assert receipt["fingerprint"] == a.fingerprint
    assert receipt["thread_count"] == 2
    assert receipt["private_rayon_pool"] is True
    assert receipt["uses_global_rayon_pool"] is False
    assert receipt["cpu_variant"] == "scalar"
    assert receipt["require_finite"] is True
    assert a.counters()["ffi_compute_entries"] == 0


def test_workspace_plan_binding_reset_and_no_growth_after_warmup():
    plan = _plan(2, 128)
    workspace = plan.workspace()
    x = np.linspace(-0.25, 0.75, 128, dtype=np.float64)

    plan.run_fixture(x, workspace, steps=1)
    warm = workspace.snapshot()
    assert warm["size"] == 128
    assert warm["all_zero"] is False
    assert warm["busy"] is False
    assert warm["poisoned"] is False
    capacities = warm["capacities"]

    plan.reset_counters()
    plan.run_fixture(x, workspace, steps=100)
    counters = plan.counters()
    assert counters == {
        "ffi_compute_entries": 1,
        "input_copies": 2,
        "output_copies": 1,
        "workspace_growth_events": 0,
        "designated_rust_allocations": 0,
    }
    assert workspace.snapshot()["capacities"] == capacities

    workspace.reset()
    reset = workspace.snapshot()
    assert reset["all_zero"] is True
    assert reset["capacities"] == capacities

    other = _plan(1, 128)
    with pytest.raises(rust.PlanMismatchError, match="different RuntimePlan"):
        other.run_fixture(x, workspace, steps=1)


def test_fixed_configuration_is_exactly_repeatable_with_identical_counter_trace():
    plan = _plan(2, 257)
    workspace = plan.workspace()
    x = np.linspace(-1.0, 1.0, 257, dtype=np.float64)
    digests: list[str] = []
    traces: list[dict[str, int]] = []
    for _ in range(20):
        workspace.reset()
        plan.reset_counters()
        digests.append(_digest(plan.run_fixture(x, workspace, steps=17)))
        traces.append(plan.counters())
    assert len(set(digests)) == 1
    assert traces[1:] == traces[:-1]


def test_one_thread_and_configured_n_pass_primitive_state_tolerance():
    x = np.linspace(-0.4, 0.9, 513, dtype=np.float64)
    one = _plan(1, x.size)
    many = _plan(3, x.size)
    out_one = one.run_fixture(x, one.workspace(), steps=23)
    out_many = many.run_fixture(x, many.workspace(), steps=23)
    np.testing.assert_allclose(out_many, out_one, rtol=1e-15, atol=1e-15)


def test_buffer_validation_copy_accounting_and_returned_lifetime():
    plan = _plan(1, 16)
    workspace = plan.workspace()
    good = np.arange(16, dtype=np.float64)

    plan.reset_counters()
    returned = plan.run_fixture(good, workspace, steps=2)
    assert returned.dtype == np.dtype("=f8")
    assert returned.flags.c_contiguous
    assert plan.counters()["input_copies"] == 2
    assert plan.counters()["output_copies"] == 1

    saved = returned.copy()
    del plan, workspace
    gc.collect()
    np.testing.assert_array_equal(returned, saved)


@pytest.mark.parametrize(
    ("bad", "message"),
    [
        (np.arange(16, dtype=np.float32), "float64"),
        (np.arange(32, dtype=np.float64).reshape(2, 16), "rank-1"),
        (np.arange(32, dtype=np.float64)[::2], "contiguous"),
        (np.arange(16, dtype=np.dtype(">f8")), "native-endian"),
        (np.arange(15, dtype=np.float64), "length"),
        (np.array([0.0] * 15 + [np.inf], dtype=np.float64), "finite"),
    ],
)
def test_invalid_buffers_fail_before_native_compute(bad, message):
    plan = _plan(1, 16)
    workspace = plan.workspace()
    plan.reset_counters()
    with pytest.raises(rust.InvalidBufferError, match=message):
        plan.run_fixture(bad, workspace, steps=1)
    assert plan.counters()["ffi_compute_entries"] == 0
    assert workspace.snapshot()["busy"] is False


def test_workspace_concurrent_and_recursive_reuse_fail_without_deadlock():
    plan = _plan(2, 4096)
    workspace = plan.workspace()
    x = np.linspace(-0.5, 0.5, 4096, dtype=np.float64)
    failures: list[BaseException] = []

    def first_user() -> None:
        try:
            plan.run_fixture(x, workspace, steps=4000)
        except BaseException as exc:  # pragma: no cover - diagnostic collection
            failures.append(exc)

    thread = threading.Thread(target=first_user)
    thread.start()
    deadline = time.monotonic() + 10.0
    while not workspace.is_busy and time.monotonic() < deadline:
        time.sleep(0.001)
    assert workspace.is_busy
    with pytest.raises(rust.WorkspaceBusyError, match="busy"):
        plan.run_fixture(x, workspace, steps=1)
    thread.join(timeout=30.0)
    assert not thread.is_alive()
    assert failures == []

    with pytest.raises(rust.WorkspaceBusyError, match="reentrant"):
        plan._test_recursive_reentry(workspace)
    assert workspace.is_busy is False


def test_gil_is_detached_once_for_a_coarse_rust_operation():
    plan = _plan(2, 4096)
    workspace = plan.workspace()
    x = np.linspace(-1.0, 1.0, 4096, dtype=np.float64)
    start = threading.Event()
    stop = threading.Event()
    progressed = 0

    def python_peer() -> None:
        nonlocal progressed
        start.wait()
        while not stop.is_set():
            progressed += 1

    peer = threading.Thread(target=python_peer)
    peer.start()
    start.set()
    before = progressed
    plan.run_fixture(x, workspace, steps=2500)
    after = progressed
    stop.set()
    peer.join(timeout=5.0)
    assert after > before


def test_rust_panic_is_contained_and_poison_requires_explicit_recovery():
    plan = _plan(1, 8)
    workspace = plan.workspace()
    with pytest.raises(rust.RuntimePanicError, match="contained Rust panic"):
        plan._test_panic(workspace)
    assert workspace.is_poisoned is True
    with pytest.raises(rust.WorkspaceStateError, match="poisoned"):
        plan.run_fixture(np.arange(8, dtype=np.float64), workspace, steps=1)
    workspace.recover()
    assert workspace.is_poisoned is False
    assert plan.run_fixture(
        np.arange(8, dtype=np.float64), workspace, steps=1
    ).shape == (8,)


def test_high_level_frontend_uses_the_typed_native_policy(monkeypatch):
    monkeypatch.setenv("BASS_ALLOW_UNVERIFIED_NATIVE_DEV", "1")
    from bianchi import backend_policy

    backend_policy.load_native.cache_clear()
    backend_policy._installed_native_payload_matches.cache_clear()
    from bianchi.runtime import RuntimePlan

    plan = RuntimePlan(thread_count=1, fixture_size=4)
    workspace = plan.workspace()
    result = plan.run_fixture(np.arange(4, dtype=np.float64), workspace, steps=1)
    assert isinstance(result, np.ndarray)
    receipt = plan.capability_receipt()
    assert receipt["backend_policy"] == "rust_required"
    assert {
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
    } <= set(receipt)
    if receipt["installed_payload_verified"]:
        assert receipt["cargo_lock_sha256"] is not None
        assert receipt["wheel_sha256"] is not None


def test_high_level_plan_construction_never_probes_legacy_global_pool(monkeypatch):
    from bianchi import backend_policy

    load = backend_policy.load_native()
    assert load.available and load.module is not None

    def forbidden_global_probe():
        raise AssertionError("RuntimePlan construction probed the global Rayon pool")

    monkeypatch.setattr(load.module, "rayon_thread_pool_size", forbidden_global_probe)
    from bianchi.runtime import RuntimePlan

    plan = RuntimePlan(thread_count=2, fixture_size=8)
    assert plan.private_pool_size == 2
    assert plan.capability_receipt()["uses_global_rayon_pool"] is False
