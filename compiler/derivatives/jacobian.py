from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Sequence
import hashlib
import json

import numpy as np
import sympy as sp

from symir.core import Bundle
from dae.index import (
    _active_equations,
    _dsym,
    _sym,
    _unknowns,
    equation_residual,
)


WSC4_VERSION = "1.0.0"


@dataclass(frozen=True)
class JacobianBundle:
    variables: tuple[str, ...]
    derivative_variables: tuple[str, ...]
    residuals: tuple[str, ...]
    J_x: tuple[tuple[str, ...], ...]
    J_dx: tuple[tuple[str, ...], ...]
    structural_sparsity_x: tuple[tuple[int, ...], ...]
    structural_sparsity_dx: tuple[tuple[int, ...], ...]
    exact_sparsity_x: tuple[tuple[int, ...], ...]
    exact_sparsity_dx: tuple[tuple[int, ...], ...]
    input_hash: str
    pass_version: str = WSC4_VERSION

    def canonical_dict(self) -> dict[str, Any]:
        return {
            "variables": list(self.variables),
            "derivative_variables": list(self.derivative_variables),
            "residuals": list(self.residuals),
            "J_x": [list(r) for r in self.J_x],
            "J_dx": [list(r) for r in self.J_dx],
            "structural_sparsity_x": [list(r) for r in self.structural_sparsity_x],
            "structural_sparsity_dx": [list(r) for r in self.structural_sparsity_dx],
            "exact_sparsity_x": [list(r) for r in self.exact_sparsity_x],
            "exact_sparsity_dx": [list(r) for r in self.exact_sparsity_dx],
            "input_hash": self.input_hash,
            "pass_version": self.pass_version,
        }

    def content_hash(self) -> str:
        raw = json.dumps(self.canonical_dict(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode()).hexdigest()


def _residuals(bundle: Bundle, active_exact_predicates: Iterable[str]) -> list[sp.Expr]:
    return [
        sp.expand(equation_residual(e))
        for e in _active_equations(bundle, active_exact_predicates)
    ]


def _structural_sparsity(
    residuals: Sequence[sp.Expr],
    variables: Sequence[sp.Symbol],
) -> tuple[tuple[int, ...], ...]:
    """
    Incidence/structural sparsity: a variable is structurally present if it
    occurs in the unsimplified residual expression.  This intentionally does
    not remove algebraic cancellations.
    """
    rows = []
    for r in residuals:
        free = r.free_symbols
        rows.append(tuple(1 if v in free else 0 for v in variables))
    return tuple(rows)


def _exact_sparsity(J: sp.Matrix) -> tuple[tuple[int, ...], ...]:
    return tuple(
        tuple(0 if sp.simplify(J[i, j]) == 0 else 1 for j in range(J.cols))
        for i in range(J.rows)
    )


def calculate_residual_jacobians(
    bundle: Bundle,
    active_exact_predicates: Iterable[str] = (),
) -> JacobianBundle:
    bundle.validate()
    names = _unknowns(bundle)
    x = [_sym(n) for n in names]
    dx = [_dsym(n) for n in names]
    rs = _residuals(bundle, active_exact_predicates)
    R = sp.Matrix(rs)

    Jx = sp.simplify(R.jacobian(x))
    Jdx = sp.simplify(R.jacobian(dx))

    return JacobianBundle(
        variables=tuple(names),
        derivative_variables=tuple(str(d) for d in dx),
        residuals=tuple(sp.sstr(r) for r in rs),
        J_x=tuple(
            tuple(sp.sstr(sp.simplify(Jx[i, j])) for j in range(Jx.cols))
            for i in range(Jx.rows)
        ),
        J_dx=tuple(
            tuple(sp.sstr(sp.simplify(Jdx[i, j])) for j in range(Jdx.cols))
            for i in range(Jdx.rows)
        ),
        structural_sparsity_x=_structural_sparsity(rs, x),
        structural_sparsity_dx=_structural_sparsity(rs, dx),
        exact_sparsity_x=_exact_sparsity(Jx),
        exact_sparsity_dx=_exact_sparsity(Jdx),
        input_hash=bundle.content_hash(),
    )


def exact_jvp(
    bundle: Bundle,
    vx: Sequence[sp.Expr | int | float],
    vdx: Sequence[sp.Expr | int | float] | None = None,
    active_exact_predicates: Iterable[str] = (),
) -> tuple[sp.Expr, ...]:
    """
    Exact symbolic JVP for the DAE residual:
        J_x vx + J_dx vdx.
    It computes directional derivatives directly, without materializing a
    numerical Jacobian.
    """
    names = _unknowns(bundle)
    if len(vx) != len(names):
        raise ValueError("vx length mismatch")
    if vdx is None:
        vdx = [0] * len(names)
    if len(vdx) != len(names):
        raise ValueError("vdx length mismatch")

    x = [_sym(n) for n in names]
    dx = [_dsym(n) for n in names]
    rs = _residuals(bundle, active_exact_predicates)

    out = []
    for r in rs:
        val = sp.Integer(0)
        for s, v in zip(x, vx):
            val += sp.diff(r, s) * sp.sympify(v)
        for s, v in zip(dx, vdx):
            val += sp.diff(r, s) * sp.sympify(v)
        out.append(sp.expand(val))
    return tuple(out)


def numerical_sparsity(
    jacobian: Sequence[Sequence[sp.Expr | str]],
    substitutions: dict[str, Any],
    tol: float = 0.0,
) -> tuple[tuple[int, ...], ...]:
    """
    Pointwise numerical sparsity is a diagnostic only; it can be smaller than
    structural/exact symbolic sparsity on special solution manifolds.
    """
    subs = {_sym(k): sp.sympify(v) for k, v in substitutions.items()}
    rows = []
    for row in jacobian:
        rr = []
        for entry in row:
            ex = sp.sympify(entry).subs(subs)
            z = complex(sp.N(ex))
            rr.append(1 if abs(z) > tol else 0)
        rows.append(tuple(rr))
    return tuple(rows)


def finite_difference_jvp(
    residual_fn,
    x: np.ndarray,
    dx: np.ndarray,
    vx: np.ndarray,
    vdx: np.ndarray,
    eps: float = 1e-7,
) -> np.ndarray:
    """Hostile numerical oracle only; never an authority derivative."""
    x = np.asarray(x, dtype=float)
    dx = np.asarray(dx, dtype=float)
    vx = np.asarray(vx, dtype=float)
    vdx = np.asarray(vdx, dtype=float)
    return (
        np.asarray(residual_fn(x + eps * vx, dx + eps * vdx), dtype=float)
        - np.asarray(residual_fn(x - eps * vx, dx - eps * vdx), dtype=float)
    ) / (2 * eps)
