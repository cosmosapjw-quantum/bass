"""Focused RF-00 proofs for the minimal frontend and optional oracle seam."""
from __future__ import annotations

import ast
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest

import bianchi
from bianchi import optional_dependencies as optional


ROOT = Path(__file__).resolve().parents[1]
OPTIONAL_ROOTS = {
    "jax",
    "jaxlib",
    "diffrax",
    "equinox",
    "optimistix",
    "lineax",
    "scipy",
    "sympy",
    "mpmath",
}


def _run_fresh(code: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )


def _backend_route_modules() -> tuple[str, ...]:
    modules = set()
    for path in sorted((ROOT / "bianchi").rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        if not any(
            isinstance(node, ast.Call)
            and (
                isinstance(node.func, ast.Name)
                and node.func.id in {"select_backend", "require_native"}
                or isinstance(node.func, ast.Attribute)
                and node.func.attr in {"select_backend", "require_native"}
            )
            for node in ast.walk(tree)
        ):
            continue
        relative = path.relative_to(ROOT).with_suffix("")
        parts = list(relative.parts)
        if parts[-1] == "__init__":
            parts.pop()
        modules.add(".".join(parts))
    return tuple(sorted(modules))


def test_minimal_top_level_import_does_not_touch_optional_stacks():
    roots = repr(sorted(OPTIONAL_ROOTS))
    completed = _run_fresh(
        f"""
import sys

OPTIONAL = set({roots})

class RejectOptionalImports:
    def find_spec(self, fullname, path=None, target=None):
        if fullname.partition('.')[0] in OPTIONAL:
            raise AssertionError(f'optional import attempted: {{fullname}}')
        return None

sys.meta_path.insert(0, RejectOptionalImports())
import bianchi
import bianchi.backend_policy
import bianchi.backend
assert 'conventions' not in bianchi.__dict__
assert 'algebra' not in bianchi.__dict__
assert not OPTIONAL.intersection(sys.modules), sorted(OPTIONAL.intersection(sys.modules))
print(bianchi.__version__)
"""
    )
    assert completed.stdout.strip() == bianchi.__version__


def test_backend_route_modules_do_not_import_optional_oracle_stacks():
    modules = repr(_backend_route_modules())
    roots = repr(sorted(OPTIONAL_ROOTS))
    completed = _run_fresh(
        f"""
import importlib
import sys

OPTIONAL = set({roots})

class RejectOptionalImports:
    def find_spec(self, fullname, path=None, target=None):
        if fullname.partition('.')[0] in OPTIONAL:
            raise AssertionError(f'optional import attempted: {{fullname}}')
        return None

sys.meta_path.insert(0, RejectOptionalImports())
for module_name in {modules}:
    importlib.import_module(module_name)
assert not OPTIONAL.intersection(sys.modules), sorted(OPTIONAL.intersection(sys.modules))
print('BACKEND_ROUTE_IMPORTS_PASS')
"""
    )
    assert completed.stdout.strip() == "BACKEND_ROUTE_IMPORTS_PASS"


def test_dependency_light_pstf_basis_is_oracle_byte_identical():
    from bianchi.matter._pstf_low_rank import u_basis
    from bianchi.matter import pstf_coeff

    for rank in (1, 2):
        assert (u_basis(rank) == pstf_coeff.U_basis(rank)).all()
        assert not u_basis(rank).flags.writeable


def test_public_lazy_exports_preserve_conventions_and_algebra():
    from bianchi import algebra, conventions

    assert bianchi.algebra is algebra
    assert bianchi.conventions is conventions
    assert bianchi.__all__ == ["conventions", "algebra", "__version__"]
    assert {"conventions", "algebra"}.issubset(dir(bianchi))


@pytest.mark.parametrize(
    ("module_name", "dependency"),
    (
        ("jax", "jax"),
        ("scipy.integrate", "scipy"),
        ("sympy", "sympy"),
        ("mpmath", "mpmath"),
    ),
)
def test_missing_optional_dependency_is_typed_and_actionable(
    monkeypatch, module_name, dependency
):
    missing = ModuleNotFoundError(
        f"No module named {dependency!r}", name=dependency
    )

    def fail_import(_module_name):
        raise missing

    optional.require_optional.cache_clear()
    monkeypatch.setattr(optional.importlib, "import_module", fail_import)
    with pytest.raises(optional.OptionalDependencyError) as caught:
        optional.require_optional(
            module_name, feature="focused-test", dependency=dependency
        )

    error = caught.value
    assert error.dependency == dependency
    assert error.feature == "focused-test"
    assert error.module_name == module_name
    assert error.extra == "python-oracle"
    assert "bianchi-solver[python-oracle]==0.1.0" in str(error)
    assert error.__cause__ is missing


@pytest.mark.parametrize(
    ("public_module", "dependency"),
    (
        ("bianchi.conventions", "jax"),
        ("bianchi.observables.distances", "scipy"),
        ("bianchi.symbolic.frame", "sympy"),
    ),
)
def test_public_optional_path_reports_typed_missing_dependency(
    public_module, dependency
):
    completed = _run_fresh(
        f"""
import importlib
import sys
from bianchi.optional_dependencies import OptionalDependencyError

class MissingDependency:
    def find_spec(self, fullname, path=None, target=None):
        if fullname.partition('.')[0] == {dependency!r}:
            raise ModuleNotFoundError(
                'blocked optional dependency', name={dependency!r}
            )
        return None

sys.meta_path.insert(0, MissingDependency())
try:
    importlib.import_module({public_module!r})
except OptionalDependencyError as error:
    assert error.dependency == {dependency!r}
    assert error.extra == 'python-oracle'
    print(error.dependency)
else:
    raise AssertionError('optional public path unexpectedly imported')
"""
    )
    assert completed.stdout.strip() == dependency


@pytest.mark.parametrize(
    "failure",
    (
        ModuleNotFoundError("No module named 'internal_bug'", name="internal_bug"),
        ImportError("unexpected optional-module source defect"),
        OSError("unexpected optional-module data defect"),
    ),
)
def test_unrelated_optional_module_failures_are_not_relabelled(monkeypatch, failure):
    def fail_import(_module_name):
        raise failure

    optional.require_optional.cache_clear()
    monkeypatch.setattr(optional.importlib, "import_module", fail_import)
    with pytest.raises(type(failure)) as caught:
        optional.require_optional("jax", feature="focused-test", dependency="jax")
    assert caught.value is failure
    assert not isinstance(caught.value, optional.OptionalDependencyError)


def test_explicit_python_oracle_enables_x64_before_array_creation():
    completed = _run_fresh(
        """
from bianchi.optional_dependencies import require_jax_x64
jax, jnp = require_jax_x64(feature='focused-x64-test')
assert bool(jax.config.jax_enable_x64)
assert str(jnp.zeros(1).dtype) == 'float64'
print('x64')
"""
    )
    assert completed.stdout.strip() == "x64"


def test_x64_configuration_runtime_failure_is_typed(monkeypatch):
    failure = RuntimeError("configuration already frozen")
    fake_jax = SimpleNamespace(
        config=SimpleNamespace(update=lambda *_args, **_kwargs: (_ for _ in ()).throw(failure))
    )

    def fake_require(module_name, **_kwargs):
        assert module_name == "jax"
        return fake_jax

    optional.require_jax_x64.cache_clear()
    monkeypatch.setattr(optional, "require_optional", fake_require)
    with pytest.raises(optional.OptionalDependencyConfigurationError) as caught:
        optional.require_jax_x64(feature="focused-test")
    assert caught.value.__cause__ is failure


def test_x64_configuration_unexpected_bug_is_not_relabelled(monkeypatch):
    failure = AssertionError("unexpected configuration bug")
    fake_jax = SimpleNamespace(
        config=SimpleNamespace(update=lambda *_args, **_kwargs: (_ for _ in ()).throw(failure))
    )

    def fake_require(module_name, **_kwargs):
        assert module_name == "jax"
        return fake_jax

    optional.require_jax_x64.cache_clear()
    monkeypatch.setattr(optional, "require_optional", fake_require)
    with pytest.raises(AssertionError) as caught:
        optional.require_jax_x64(feature="focused-test")
    assert caught.value is failure
