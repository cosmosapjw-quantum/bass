"""Software boundary proof only: no native numerical validation is claimed."""
from pathlib import Path
import importlib.util
import sys
from types import ModuleType, SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / 'bianchi/kinetic/__init__.py'


def load_wrapper(monkeypatch, selector):
    assert PATH.is_file(), 'RF04 thin public wrapper has not been implemented'
    parent = ModuleType('bianchi')
    backend = ModuleType('bianchi.backend_policy')
    backend.BackendPolicy = SimpleNamespace(RUST_REQUIRED='rust_required')
    backend.select_backend = selector
    monkeypatch.setitem(sys.modules, 'bianchi', parent)
    monkeypatch.setitem(sys.modules, 'bianchi.backend_policy', backend)
    spec = importlib.util.spec_from_file_location('rf04_wrapper_under_test', PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize('short', ['execution_identity', 'trajectory', 'batch'])
def test_dispatch_uses_one_exact_native_call_without_copy(monkeypatch, short):
    route = 'kinetic.typeii.' + short + '_v1'
    symbol = 'rf04_typeii_' + short + '_v1'
    calls, selections = [], []
    marker = object()

    class Native:
        def __getattr__(self, requested):
            assert requested == symbol
            def call(*args):
                calls.append(args)
                return marker
            return call

    def selector(requested, *, policy):
        selections.append((requested, policy))
        return SimpleNamespace(native_module=Native())

    wrapper = load_wrapper(monkeypatch, selector)
    args = () if short == 'execution_identity' else tuple(object() for _ in range(13))
    result = getattr(wrapper, 'typeii_' + short + '_v1')(*args)
    assert result is marker
    assert selections == [(route, 'rust_required')]
    assert len(calls) == 1 and len(calls[0]) == len(args)
    assert all(a is b for a, b in zip(calls[0], args, strict=True))


def test_dispatch_does_not_fallback_when_backend_rejects(monkeypatch):
    class Rejection(RuntimeError):
        pass
    def selector(*args, **kwargs):
        raise Rejection('native identity mismatch')
    wrapper = load_wrapper(monkeypatch, selector)
    with pytest.raises(Rejection, match='native identity mismatch'):
        wrapper.typeii_execution_identity_v1()


def test_dispatch_rejects_impossible_none_native_selection(monkeypatch):
    wrapper = load_wrapper(monkeypatch, lambda *a, **k: SimpleNamespace(native_module=None))
    with pytest.raises(RuntimeError, match='native_required'):
        wrapper.typeii_execution_identity_v1()
