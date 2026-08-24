from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable
import hashlib
import json

import sympy as sp

from symir.core import Bundle, Equation, Expr, PredicateClass, SymIRError


WSC3_VERSION = "1.0.0"


class DAEError(SymIRError):
    pass


def _sym(name: str) -> sp.Symbol:
    return sp.Symbol(name)


def _dsym(name: str) -> sp.Symbol:
    return sp.Symbol(f"D1__{name}")


def expr_to_sympy(expr: Expr) -> sp.Expr:
    if expr.op == "Const":
        return sp.sympify(expr.value)
    if expr.op == "Ref":
        if not isinstance(expr.value, str):
            raise DAEError("Ref value must be a string")
        return _sym(expr.value)
    if expr.op == "Derivative":
        if len(expr.args) != 1:
            raise DAEError("Derivative currently supports one argument")
        arg = expr.args[0]
        if not isinstance(arg, Expr) or arg.op != "Ref" or not isinstance(arg.value, str):
            raise DAEError("Derivative expects Ref(variable)")
        return _dsym(arg.value)
    if expr.op == "Add":
        return sp.Add(*(expr_to_sympy(a) for a in expr.args))
    if expr.op == "Mul":
        return sp.Mul(*(expr_to_sympy(a) for a in expr.args))
    if expr.op == "Sub":
        return expr_to_sympy(expr.args[0]) - expr_to_sympy(expr.args[1])
    if expr.op == "Div":
        return expr_to_sympy(expr.args[0]) / expr_to_sympy(expr.args[1])
    if expr.op == "Pow":
        return expr_to_sympy(expr.args[0]) ** expr_to_sympy(expr.args[1])
    if expr.op == "Neg":
        return -expr_to_sympy(expr.args[0])
    raise DAEError(f"unsupported Expr op {expr.op}")


def equation_residual(eq: Equation) -> sp.Expr:
    return sp.expand(expr_to_sympy(eq.lhs) - expr_to_sympy(eq.rhs))


def _active_equations(bundle: Bundle, active_exact_predicates: Iterable[str]) -> list[Equation]:
    active = set(active_exact_predicates)
    by_id = {p.id: p for p in bundle.predicates}
    for pid in sorted(active):
        if pid not in by_id:
            raise DAEError(f"unknown active predicate {pid}")
        p = by_id[pid]
        if p.classification not in {PredicateClass.EXACT_IDENTITY, PredicateClass.EXACT_INVARIANT}:
            raise DAEError(f"predicate {pid} is not exact and cannot specialize DAE structure")
    return [e for e in sorted(bundle.equations, key=lambda x: x.id)
            if set(e.exact_predicates).issubset(active)]


def _unknowns(bundle: Bundle) -> list[str]:
    return sorted(n.id for n in bundle.nodes
                  if n.metadata.get("structural_role", "unknown") == "unknown")


@dataclass(frozen=True)
class MassMatrixForm:
    variables: tuple[str, ...]
    derivative_variables: tuple[str, ...]
    differential_variables: tuple[str, ...]
    algebraic_variables: tuple[str, ...]
    algebraic_rows: tuple[int, ...]
    residuals: tuple[str, ...]
    mass_matrix: tuple[tuple[str, ...], ...]
    rhs: tuple[str, ...]
    input_hash: str
    pass_version: str = WSC3_VERSION

    def canonical_dict(self) -> dict[str, Any]:
        return {
            "variables": list(self.variables),
            "derivative_variables": list(self.derivative_variables),
            "differential_variables": list(self.differential_variables),
            "algebraic_variables": list(self.algebraic_variables),
            "algebraic_rows": list(self.algebraic_rows),
            "residuals": list(self.residuals),
            "mass_matrix": [list(r) for r in self.mass_matrix],
            "rhs": list(self.rhs),
            "input_hash": self.input_hash,
            "pass_version": self.pass_version,
        }

    def content_hash(self) -> str:
        raw = json.dumps(self.canonical_dict(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode()).hexdigest()


def mass_matrix_form(bundle: Bundle, active_exact_predicates: Iterable[str] = ()) -> MassMatrixForm:
    bundle.validate()
    equations = _active_equations(bundle, active_exact_predicates)
    variables = _unknowns(bundle)
    dsyms = [_dsym(v) for v in variables]
    residuals = [equation_residual(e) for e in equations]
    rvec = sp.Matrix(residuals)

    M = sp.simplify(rvec.jacobian(dsyms))
    derivative_set = set(dsyms)
    if any(set(entry.free_symbols) & derivative_set for entry in M):
        raise DAEError("residual is nonlinear in first derivatives; mass-matrix extraction is invalid")

    zero_sub = {d: 0 for d in dsyms}
    base = sp.Matrix([sp.expand(r.subs(zero_sub)) for r in residuals])
    rhs = sp.Matrix([-x for x in base])

    algebraic_rows = tuple(i for i in range(M.rows)
                           if all(sp.simplify(M[i, j]) == 0 for j in range(M.cols)))
    differential_cols = {j for j in range(M.cols)
                         if any(sp.simplify(M[i, j]) != 0 for i in range(M.rows))}
    differential_vars = tuple(variables[j] for j in sorted(differential_cols))
    algebraic_vars = tuple(v for j, v in enumerate(variables) if j not in differential_cols)

    return MassMatrixForm(
        variables=tuple(variables),
        derivative_variables=tuple(str(d) for d in dsyms),
        differential_variables=differential_vars,
        algebraic_variables=algebraic_vars,
        algebraic_rows=algebraic_rows,
        residuals=tuple(sp.sstr(sp.expand(r)) for r in residuals),
        mass_matrix=tuple(tuple(sp.sstr(sp.simplify(M[i, j])) for j in range(M.cols))
                          for i in range(M.rows)),
        rhs=tuple(sp.sstr(sp.expand(x)) for x in rhs),
        input_hash=bundle.content_hash(),
    )


def explicit_dynamics(bundle: Bundle, active_exact_predicates: Iterable[str] = ()) -> dict[str, sp.Expr]:
    equations = _active_equations(bundle, active_exact_predicates)
    out: dict[str, sp.Expr] = {}
    for e in equations:
        if e.lhs.op == "Derivative" and len(e.lhs.args) == 1:
            a = e.lhs.args[0]
            if isinstance(a, Expr) and a.op == "Ref" and isinstance(a.value, str):
                rhs = expr_to_sympy(e.rhs)
                if any(str(s).startswith("D1__") for s in rhs.free_symbols):
                    continue
                out[a.value] = sp.expand(rhs)
    return out


def lie_derivative(expr: sp.Expr, dynamics: dict[str, sp.Expr]) -> sp.Expr:
    return sp.expand(sum(sp.diff(expr, _sym(name))*rhs
                         for name, rhs in sorted(dynamics.items())))


@dataclass(frozen=True)
class ConstraintClosure:
    equation_id: str
    depth: int
    algebraic_unknowns: tuple[str, ...]
    levels: tuple[str, ...]
    introduced_algebraic_at_depth: int | None
    input_hash: str


def pantelides_style_constraint_closure(
    bundle: Bundle,
    constraint_equation_id: str,
    active_exact_predicates: Iterable[str] = (),
    max_depth: int = 6,
) -> ConstraintClosure:
    """
    Narrow WSC-3 first-order constrained-system closure.

    It repeatedly differentiates an algebraic constraint along the explicit
    differential flow until an algebraic unknown enters the differentiated
    constraint.  This reproduces the classical pendulum's two differentiations
    needed to expose lambda and obtain an index-1 representation.

    It is intentionally NOT claimed to be a complete general Pantelides
    implementation.
    """
    equations = _active_equations(bundle, active_exact_predicates)
    eq_map = {e.id: e for e in equations}
    if constraint_equation_id not in eq_map:
        raise DAEError(f"constraint {constraint_equation_id} is not active")
    eq = eq_map[constraint_equation_id]

    dynamics = explicit_dynamics(bundle, active_exact_predicates)
    variables = _unknowns(bundle)
    algebraic = tuple(sorted(set(variables) - set(dynamics)))
    alg_symbols = {_sym(a) for a in algebraic}

    current = equation_residual(eq)
    levels = [sp.sstr(sp.factor(current))]
    if set(current.free_symbols) & alg_symbols:
        return ConstraintClosure(eq.id, 0, algebraic, tuple(levels), 0, bundle.content_hash())

    for depth in range(1, max_depth + 1):
        current = lie_derivative(current, dynamics)
        levels.append(sp.sstr(sp.factor(current)))
        if set(current.free_symbols) & alg_symbols:
            return ConstraintClosure(eq.id, depth, algebraic, tuple(levels), depth, bundle.content_hash())

    return ConstraintClosure(eq.id, max_depth, algebraic, tuple(levels), None, bundle.content_hash())


@dataclass(frozen=True)
class InitializationResult:
    equations: tuple[str, ...]
    solve_for: tuple[str, ...]
    solutions: tuple[dict[str, str], ...]


def solve_initialization(
    equations: Iterable[sp.Expr],
    fixed_values: dict[str, Any],
    solve_for: Iterable[str],
) -> InitializationResult:
    # SymIR symbol identity is canonical by *name*, not by optional SymPy
    # assumptions.  This makes serialized expressions and independently
    # constructed verifier expressions interoperable.
    solve_names = tuple(solve_for)
    exprs = [sp.sympify(e) for e in equations]
    free_by_name: dict[str, list[sp.Symbol]] = {}
    for e in exprs:
        for s in e.free_symbols:
            free_by_name.setdefault(str(s), []).append(s)

    subs = {}
    for name, value in fixed_values.items():
        for s in free_by_name.get(name, []):
            subs[s] = sp.sympify(value)

    reduced = [sp.factor(sp.expand(e.subs(subs))) for e in exprs]
    reduced = [e for e in reduced if sp.simplify(e) != 0]

    unknown_syms = []
    for name in solve_names:
        candidates = []
        for e in reduced:
            candidates.extend(s for s in e.free_symbols if str(s) == name)
        unique = list(dict.fromkeys(candidates))
        if len(unique) > 1:
            raise DAEError(f"ambiguous SymPy symbols share IR name {name}")
        unknown_syms.append(unique[0] if unique else _sym(name))

    raw = sp.solve(reduced, unknown_syms, dict=True) if reduced else [{}]
    sols = tuple(
        {str(k): sp.sstr(sp.simplify(v)) for k, v in sorted(sol.items(), key=lambda kv: str(kv[0]))}
        for sol in raw
    )
    return InitializationResult(
        equations=tuple(sp.sstr(e) for e in reduced),
        solve_for=solve_names,
        solutions=sols,
    )
