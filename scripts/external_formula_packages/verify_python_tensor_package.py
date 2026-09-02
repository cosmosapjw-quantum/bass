#!/usr/bin/env python3
"""Run bounded, fail-closed tensor-package witnesses.

This script deliberately distinguishes an independent package implementation
from an independent algebra engine.  EinsteinPy and OGRePy use SymPy; Pytearcat
reports whether its selected backend is SymPy or Giac.
"""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import sys
import traceback
from pathlib import Path
from typing import Any

import sympy as sp


EXPECTED_DIAGONAL = (sp.Integer(11) / sp.Symbol("t") ** 2, -14, -9 * sp.Symbol("t") ** 2, -4 * sp.Symbol("t") ** 4)


def _write(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _normalise(expr: Any) -> sp.Expr:
    return sp.simplify(sp.nsimplify(expr))


def _verify_matrix(matrix: Any, t: sp.Symbol) -> dict[str, Any]:
    expected = (
        sp.Integer(11) / t**2,
        sp.Integer(-14),
        -sp.Integer(9) * t**2,
        -sp.Integer(4) * t**4,
    )
    diagonal_residuals = [_normalise(matrix[i, i] - expected[i]) for i in range(4)]
    off_diagonal_residuals = [
        _normalise(matrix[i, j])
        for i in range(4)
        for j in range(4)
        if i != j
    ]
    return {
        "metric": "diag(-1,t^2,t^4,t^6)",
        "expected_covariant_einstein_diagonal": [str(x) for x in expected],
        "diagonal_residuals": [str(x) for x in diagonal_residuals],
        "off_diagonal_residuals": [str(x) for x in off_diagonal_residuals],
        "pass": all(x == 0 for x in diagonal_residuals + off_diagonal_residuals),
    }


def _einsteinpy() -> dict[str, Any]:
    from einsteinpy.symbolic import EinsteinTensor, MetricTensor

    t, x, y, z = sp.symbols("t x y z", positive=True, real=True)
    components = sp.Array(sp.diag(-1, t**2, t**4, t**6).tolist())
    metric = MetricTensor(components, (t, x, y, z))
    einstein = EinsteinTensor.from_metric(metric).tensor()
    matrix = sp.Matrix(4, 4, lambda i, j: einstein[i, j])
    result = _verify_matrix(matrix, t)
    result.update(
        {
            "package": "einsteinpy",
            "package_version": importlib.metadata.version("einsteinpy"),
            "package_axis": "INDEPENDENT_GR_PACKAGE_SHARED_SYMPY_ENGINE",
            "algebra_engine": f"sympy-{sp.__version__}",
        }
    )
    return result


def _ogrepy() -> dict[str, Any]:
    os.environ.setdefault("OGREPY_DISABLE_WELCOME", "True")
    import OGRePy as T

    t, x, y, z = sp.symbols("t x y z", positive=True, real=True)
    coords = T.Coordinates(t, x, y, z)
    metric = T.Metric(
        coords=coords,
        components=T.diag(-1, t**2, t**4, t**6),
        symbol="g",
    )
    components = metric.einstein().components(
        indices=(-1, -1), coords=coords, warn=False
    )
    matrix = sp.Matrix(4, 4, lambda i, j: components[i, j])
    result = _verify_matrix(matrix, t)
    result.update(
        {
            "package": "OGRePy",
            "package_version": importlib.metadata.version("OGRePy"),
            "package_axis": "INDEPENDENT_GR_PACKAGE_SHARED_SYMPY_ENGINE",
            "algebra_engine": f"sympy-{sp.__version__}",
        }
    )
    return result


def _pytearcat() -> dict[str, Any]:
    import pytearcat as pt
    from pytearcat.tensor.core import core as ptcore

    t, x, y, z = pt.coords("t,x,y,z")
    pt.fun("aa", "t")
    pt.fun("bb", "t")
    pt.fun("cc", "t")
    # Concrete scale factors keep the witness deterministic and inexpensive.
    metric = pt.metric("ds2 = -dt**2 + t**2*dx**2 + t**4*dy**2 + t**6*dz**2")
    del metric
    einstein = pt.einstein()
    components = einstein.tensor[0]
    matrix = sp.Matrix(4, 4, lambda i, j: sp.sympify(components[i][j]))
    result = _verify_matrix(matrix, sp.Symbol("t", positive=True, real=True))
    backend = getattr(ptcore, "core_calc", "UNKNOWN")
    result.update(
        {
            "package": "pytearcat",
            "package_version": importlib.metadata.version("pytearcat"),
            "package_axis": (
                "INDEPENDENT_GR_PACKAGE_GIAC_ENGINE"
                if backend == "gp"
                else "INDEPENDENT_GR_PACKAGE_SHARED_SYMPY_ENGINE"
            ),
            "algebra_engine": "giac" if backend == "gp" else f"sympy-{sp.__version__}",
            "pytearcat_core_calc": backend,
        }
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", choices=("einsteinpy", "ogrepy", "pytearcat"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    dispatch = {
        "einsteinpy": _einsteinpy,
        "ogrepy": _ogrepy,
        "pytearcat": _pytearcat,
    }
    receipt: dict[str, Any] = {
        "schema_version": "1.0.0",
        "stage_id": "XCAS_01_EXTERNAL_FORMULA_PACKAGE_VERIFICATION",
        "backend": args.backend,
        "authority_effect": "NONE",
        "python": sys.version,
    }
    try:
        result = dispatch[args.backend]()
        receipt.update(result)
        receipt["status"] = "PASS" if result["pass"] else "FAIL_FORMULA"
    except Exception as exc:  # fail closed, but preserve the package failure
        receipt.update(
            {
                "status": "BLOCKED_RUNTIME",
                "pass": False,
                "exception_type": type(exc).__name__,
                "exception": str(exc),
                "traceback": traceback.format_exc(),
            }
        )
    _write(args.output, receipt)
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
