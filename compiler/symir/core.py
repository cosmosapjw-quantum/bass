from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Iterable
import hashlib
import json


SCHEMA_VERSION = "1.0.0"


class SymIRError(ValueError):
    pass


class AuthorityLevel(str, Enum):
    CONTINUUM = "continuum"
    DISCRETIZATION = "discretization"
    RUNTIME = "runtime"


class PredicateClass(str, Enum):
    EXACT_IDENTITY = "exact_identity"
    EXACT_INVARIANT = "exact_invariant"
    NUMERICAL_HINT = "numerical_hint"
    PHYSICAL_APPROXIMATION = "physical_approximation"


class Stage(str, Enum):
    BACKGROUND = "background"
    CHARACTERISTIC = "characteristic"
    TRANSPORT = "transport"
    COLLISION = "collision"
    OUTPUT = "output"


FORBIDDEN_CONTINUUM_METADATA = {
    "ell_max",
    "lmax",
    "lebedev_order",
    "lebedev_nodes",
    "energy_grid",
    "log_energy_grid",
    "interpolation",
    "strang",
    "krylov",
    "quadrature_nodes",
    "quadrature_weights",
}

POINTWISE_KINDS = {
    "PointwiseRate",
    "DiagonalAngularOperator",
}

ONCE_ONLY_KINDS = {
    "SpectralToBolometricMap",
    "ObservedSkyEndpoint",
}


@dataclass(frozen=True)
class Expr:
    op: str
    args: tuple[Any, ...] = ()
    value: Any = None

    def to_dict(self) -> dict[str, Any]:
        def conv(x: Any) -> Any:
            if isinstance(x, Expr):
                return x.to_dict()
            if isinstance(x, tuple):
                return [conv(v) for v in x]
            return x
        return {
            "op": self.op,
            "args": [conv(v) for v in self.args],
            "value": conv(self.value),
        }


@dataclass(frozen=True)
class Node:
    id: str
    kind: str
    authority_level: AuthorityLevel
    stage: Stage
    domain: str
    units: str
    frame: str
    representation: str
    dependencies: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)
    consumes_tokens: tuple[str, ...] = ()
    produces_tokens: tuple[str, ...] = ()

    def validate(self) -> None:
        if self.authority_level == AuthorityLevel.CONTINUUM:
            bad = FORBIDDEN_CONTINUUM_METADATA.intersection(self.metadata)
            if bad:
                raise SymIRError(
                    "continuum node contains discretization metadata: "
                    + ",".join(sorted(bad))
                )
        if self.kind == "ObservedSkyEndpoint" and self.stage != Stage.OUTPUT:
            raise SymIRError("ObservedSkyEndpoint is output-only")
        if self.kind in POINTWISE_KINDS and self.metadata.get("scalarized", False):
            raise SymIRError("pointwise angular operator cannot be scalarized")
        if self.kind in ONCE_ONLY_KINDS and not (
            self.consumes_tokens or self.produces_tokens
        ):
            raise SymIRError(
                f"{self.kind} must participate in a once-only token contract"
            )


@dataclass(frozen=True)
class Predicate:
    id: str
    classification: PredicateClass
    expr: Expr
    proof_receipt: str | None = None

    @property
    def may_rewrite_authority(self) -> bool:
        return self.classification in {
            PredicateClass.EXACT_IDENTITY,
            PredicateClass.EXACT_INVARIANT,
        }


@dataclass(frozen=True)
class Equation:
    id: str
    lhs: Expr
    rhs: Expr
    stage: Stage
    exact_predicates: tuple[str, ...] = ()


@dataclass(frozen=True)
class PassReceipt:
    pass_name: str
    pass_version: str
    input_hash: str
    output_hash: str
    exact_predicates: tuple[str, ...] = ()
    proof_receipts: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()


@dataclass
class Bundle:
    formula_authority_hash: str
    nodes: list[Node]
    equations: list[Equation]
    predicates: list[Predicate] = field(default_factory=list)
    pass_receipts: list[PassReceipt] = field(default_factory=list)
    schema_version: str = SCHEMA_VERSION

    def validate(self) -> None:
        if self.schema_version != SCHEMA_VERSION:
            raise SymIRError(f"unsupported schema version {self.schema_version}")

        node_ids = [n.id for n in self.nodes]
        if len(node_ids) != len(set(node_ids)):
            raise SymIRError("duplicate node id")
        for n in self.nodes:
            n.validate()

        equation_ids = [eq.id for eq in self.equations]
        if len(equation_ids) != len(set(equation_ids)):
            raise SymIRError("duplicate equation id")

        pred = {p.id: p for p in self.predicates}
        for eq in self.equations:
            for p_id in eq.exact_predicates:
                if p_id not in pred:
                    raise SymIRError(f"missing predicate {p_id}")
                if not pred[p_id].may_rewrite_authority:
                    raise SymIRError(
                        f"predicate {p_id} may not rewrite authority equations"
                    )

        consumers: dict[str, list[str]] = {}
        for n in self.nodes:
            for tok in n.consumes_tokens:
                consumers.setdefault(tok, []).append(n.id)
        dup = {k: v for k, v in consumers.items() if len(v) > 1}
        if dup:
            raise SymIRError(f"once-only token consumed more than once: {dup}")

    def canonical_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "schema_version": self.schema_version,
            "formula_authority_hash": self.formula_authority_hash,
            "nodes": [
                {
                    **asdict(n),
                    "authority_level": n.authority_level.value,
                    "stage": n.stage.value,
                }
                for n in sorted(self.nodes, key=lambda x: x.id)
            ],
            "equations": [
                {
                    "id": e.id,
                    "lhs": e.lhs.to_dict(),
                    "rhs": e.rhs.to_dict(),
                    "stage": e.stage.value,
                    "exact_predicates": list(e.exact_predicates),
                }
                for e in sorted(self.equations, key=lambda x: x.id)
            ],
            "predicates": [
                {
                    "id": p.id,
                    "classification": p.classification.value,
                    "expr": p.expr.to_dict(),
                    "proof_receipt": p.proof_receipt,
                }
                for p in sorted(self.predicates, key=lambda x: x.id)
            ],
            "pass_receipts": [
                asdict(p)
                for p in sorted(
                    self.pass_receipts,
                    key=lambda x: (x.pass_name, x.pass_version, x.output_hash),
                )
            ],
        }

    def canonical_json(self) -> str:
        return json.dumps(
            self.canonical_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )

    def content_hash(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()


def exact_specialization_allowed(predicate: Predicate) -> bool:
    return predicate.may_rewrite_authority


def require_no_scalarization(node: Node) -> None:
    if node.kind in POINTWISE_KINDS:
        raise SymIRError(
            f"{node.id}: pointwise operator cannot be coerced to a scalar"
        )
