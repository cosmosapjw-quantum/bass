from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Iterable
import hashlib
import json

from symir.core import Bundle, Equation, Expr, PredicateClass, SymIRError


STRUCTURAL_PASS_VERSION = "1.0.0"


def refs(expr: Expr) -> set[str]:
    out: set[str] = set()
    if expr.op == "Ref" and isinstance(expr.value, str):
        out.add(expr.value)
    for arg in expr.args:
        if isinstance(arg, Expr):
            out.update(refs(arg))
    if isinstance(expr.value, Expr):
        out.update(refs(expr.value))
    return out


def equation_refs(eq: Equation) -> set[str]:
    return refs(eq.lhs) | refs(eq.rhs)


def primary_target(eq: Equation) -> str | None:
    if eq.lhs.op == "Ref" and isinstance(eq.lhs.value, str):
        return eq.lhs.value
    if eq.lhs.op == "Derivative" and eq.lhs.args:
        arg = eq.lhs.args[0]
        if isinstance(arg, Expr) and arg.op == "Ref" and isinstance(arg.value, str):
            return arg.value
    return None


class _UnionFind:
    def __init__(self, items: Iterable[str]):
        self.parent = {x: x for x in items}

    def find(self, x: str) -> str:
        p = self.parent[x]
        if p != x:
            self.parent[x] = self.find(p)
        return self.parent[x]

    def union(self, a: str, b: str) -> str:
        ra, rb = self.find(a), self.find(b)
        root, other = sorted((ra, rb))
        self.parent[other] = root
        return root


@dataclass(frozen=True)
class StructuralBlock:
    id: int
    variables: tuple[str, ...]
    equations: tuple[str, ...]
    dependencies: tuple[int, ...]


@dataclass(frozen=True)
class StructuralResult:
    input_hash: str
    active_exact_predicates: tuple[str, ...]
    aliases: dict[str, str]
    active_equations: tuple[str, ...]
    stage_equations: dict[str, tuple[str, ...]]
    incidence: dict[str, tuple[str, ...]]
    equation_to_variable: dict[str, str]
    unmatched_equations: tuple[str, ...]
    unmatched_variables: tuple[str, ...]
    dependency_edges: tuple[tuple[str, str], ...]
    blocks: tuple[StructuralBlock, ...]
    proof_receipts: tuple[str, ...]
    pass_name: str = "WSC-2-StructuralGraph"
    pass_version: str = STRUCTURAL_PASS_VERSION

    def canonical_dict(self) -> dict:
        return {
            "pass_name": self.pass_name,
            "pass_version": self.pass_version,
            "input_hash": self.input_hash,
            "active_exact_predicates": list(self.active_exact_predicates),
            "aliases": dict(sorted(self.aliases.items())),
            "active_equations": list(self.active_equations),
            "stage_equations": {k: list(v) for k, v in sorted(self.stage_equations.items())},
            "incidence": {k: list(v) for k, v in sorted(self.incidence.items())},
            "equation_to_variable": dict(sorted(self.equation_to_variable.items())),
            "unmatched_equations": list(self.unmatched_equations),
            "unmatched_variables": list(self.unmatched_variables),
            "dependency_edges": [list(x) for x in self.dependency_edges],
            "blocks": [asdict(x) for x in self.blocks],
            "proof_receipts": list(self.proof_receipts),
        }

    def canonical_json(self) -> str:
        return json.dumps(self.canonical_dict(), sort_keys=True, separators=(",", ":"))

    def content_hash(self) -> str:
        return hashlib.sha256(self.canonical_json().encode()).hexdigest()


def _validate_active_predicates(bundle: Bundle, active: set[str]) -> tuple[str, ...]:
    by_id = {p.id: p for p in bundle.predicates}
    receipts: list[str] = []
    for pid in sorted(active):
        if pid not in by_id:
            raise SymIRError(f"unknown active predicate {pid}")
        p = by_id[pid]
        if p.classification not in {PredicateClass.EXACT_IDENTITY, PredicateClass.EXACT_INVARIANT}:
            raise SymIRError(f"predicate {pid} is not exact and cannot specialize structure")
        if p.proof_receipt:
            receipts.append(p.proof_receipt)
    return tuple(sorted(set(receipts)))


def _active_equations(bundle: Bundle, active: set[str]) -> list[Equation]:
    return [
        e for e in sorted(bundle.equations, key=lambda x: x.id)
        if set(e.exact_predicates).issubset(active)
    ]


def _unknowns(bundle: Bundle) -> list[str]:
    return sorted(
        n.id for n in bundle.nodes
        if n.metadata.get("structural_role", "unknown") == "unknown"
    )


def _alias_map(equations: list[Equation], unknowns: list[str]) -> tuple[dict[str, str], set[str]]:
    uf = _UnionFind(unknowns)
    unknown_set = set(unknowns)
    alias_eqs: set[str] = set()
    for e in equations:
        if e.lhs.op == "Ref" and e.rhs.op == "Ref":
            a, b = e.lhs.value, e.rhs.value
            if isinstance(a, str) and isinstance(b, str) and a in unknown_set and b in unknown_set:
                uf.union(a, b)
                alias_eqs.add(e.id)
    aliases = {u: uf.find(u) for u in unknowns if uf.find(u) != u}
    return aliases, alias_eqs


def _canon(name: str, aliases: dict[str, str]) -> str:
    while name in aliases:
        name = aliases[name]
    return name


def _maximum_matching(incidence: dict[str, tuple[str, ...]], targets: dict[str, str | None]) -> dict[str, str]:
    var_to_eq: dict[str, str] = {}

    def candidates(eq: str) -> list[str]:
        vals = list(incidence[eq])
        t = targets.get(eq)
        if t in vals:
            vals.remove(t)
            return [t] + sorted(vals)
        return sorted(vals)

    def augment(eq: str, seen: set[str]) -> bool:
        for var in candidates(eq):
            if var in seen:
                continue
            seen.add(var)
            owner = var_to_eq.get(var)
            if owner is None or augment(owner, seen):
                var_to_eq[var] = eq
                return True
        return False

    for eq in sorted(incidence):
        augment(eq, set())
    return {eq: var for var, eq in sorted(var_to_eq.items())}


def _tarjan(vertices: list[str], edges: dict[str, set[str]]) -> list[tuple[str, ...]]:
    index = 0
    stack: list[str] = []
    onstack: set[str] = set()
    indices: dict[str, int] = {}
    low: dict[str, int] = {}
    comps: list[tuple[str, ...]] = []

    def visit(v: str) -> None:
        nonlocal index
        indices[v] = low[v] = index
        index += 1
        stack.append(v); onstack.add(v)
        for w in sorted(edges.get(v, set())):
            if w not in indices:
                visit(w); low[v] = min(low[v], low[w])
            elif w in onstack:
                low[v] = min(low[v], indices[w])
        if low[v] == indices[v]:
            comp: list[str] = []
            while True:
                w = stack.pop(); onstack.remove(w); comp.append(w)
                if w == v: break
            comps.append(tuple(sorted(comp)))

    for v in sorted(vertices):
        if v not in indices:
            visit(v)
    return comps


def _blt_blocks(vertices: list[str], edges: tuple[tuple[str, str], ...], eq_to_var: dict[str, str]) -> tuple[StructuralBlock, ...]:
    adjacency: dict[str, set[str]] = {v: set() for v in vertices}
    for dep, target in edges:
        if dep in adjacency and target in adjacency:
            adjacency[dep].add(target)
    comps = _tarjan(vertices, adjacency)
    comp_of = {v: i for i, comp in enumerate(comps) for v in comp}
    dag: dict[int, set[int]] = {i: set() for i in range(len(comps))}
    indeg = {i: 0 for i in dag}
    for dep, target in edges:
        a, b = comp_of[dep], comp_of[target]
        if a != b and b not in dag[a]:
            dag[a].add(b); indeg[b] += 1
    ready = sorted((i for i,d in indeg.items() if d == 0), key=lambda i: comps[i])
    order: list[int] = []
    while ready:
        i = ready.pop(0); order.append(i)
        for j in sorted(dag[i], key=lambda k: comps[k]):
            indeg[j] -= 1
            if indeg[j] == 0:
                ready.append(j); ready.sort(key=lambda k: comps[k])
    new_id = {old: new for new, old in enumerate(order)}
    var_to_eq = {v:e for e,v in eq_to_var.items()}
    blocks=[]
    for old in order:
        vars_=comps[old]
        eqs=tuple(sorted(var_to_eq[v] for v in vars_ if v in var_to_eq))
        deps=tuple(sorted(new_id[d] for d in range(len(comps)) if old in dag[d]))
        blocks.append(StructuralBlock(new_id[old], vars_, eqs, deps))
    return tuple(blocks)


def compile_structure(bundle: Bundle, active_exact_predicates: Iterable[str] = ()) -> StructuralResult:
    bundle.validate()
    active = set(active_exact_predicates)
    receipts = _validate_active_predicates(bundle, active)
    equations = _active_equations(bundle, active)
    unknowns = _unknowns(bundle)
    aliases, alias_eqs = _alias_map(equations, unknowns)
    canonical_unknowns = sorted({_canon(v, aliases) for v in unknowns})

    incidence: dict[str, tuple[str, ...]] = {}
    targets: dict[str, str | None] = {}
    stage_equations: dict[str, list[str]] = {}
    structural_eqs: list[Equation] = []
    for e in equations:
        stage_equations.setdefault(e.stage.value, []).append(e.id)
        if e.id in alias_eqs:
            continue
        rr = sorted({_canon(r, aliases) for r in equation_refs(e) if r in set(unknowns)})
        incidence[e.id] = tuple(rr)
        t = primary_target(e)
        targets[e.id] = _canon(t, aliases) if t in set(unknowns) else None
        structural_eqs.append(e)

    eq_to_var = _maximum_matching(incidence, targets)
    unmatched_eqs = tuple(sorted(set(incidence) - set(eq_to_var)))
    matched_vars = set(eq_to_var.values())
    unmatched_vars = tuple(sorted(set(canonical_unknowns) - matched_vars))

    dep_edges: set[tuple[str, str]] = set()
    for e in structural_eqs:
        target = eq_to_var.get(e.id)
        if target is None:
            continue
        for dep in incidence[e.id]:
            if dep != target:
                dep_edges.add((dep, target))
    dep_edges_t = tuple(sorted(dep_edges))
    blocks = _blt_blocks(canonical_unknowns, dep_edges_t, eq_to_var)

    return StructuralResult(
        input_hash=bundle.content_hash(),
        active_exact_predicates=tuple(sorted(active)),
        aliases=dict(sorted(aliases.items())),
        active_equations=tuple(e.id for e in equations),
        stage_equations={k: tuple(sorted(v)) for k,v in sorted(stage_equations.items())},
        incidence=dict(sorted(incidence.items())),
        equation_to_variable=dict(sorted(eq_to_var.items())),
        unmatched_equations=unmatched_eqs,
        unmatched_variables=unmatched_vars,
        dependency_edges=dep_edges_t,
        blocks=blocks,
        proof_receipts=receipts,
    )
