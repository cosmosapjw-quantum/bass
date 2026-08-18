import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from symir.core import (
    AuthorityLevel, Bundle, Equation, Expr, Node,
    Predicate, PredicateClass, Stage, SymIRError,
    exact_specialization_allowed, require_no_scalarization,
)

FORMULA_HASH = "3ecf0dbc8b47a8af83da81e9ed37823b6922e139e420c5bfa2e071b6bbabe361"


def minimal_bundle():
    q = Node(
        id="q_v", kind="PointwiseRate",
        authority_level=AuthorityLevel.CONTINUUM,
        stage=Stage.COLLISION, domain="S2", units="L^-1",
        frame="normal", representation="scalar angular field",
        metadata={"depends_on_direction": True},
    )
    pred = Predicate(
        id="typeII_aligned",
        classification=PredicateClass.EXACT_INVARIANT,
        expr=Expr("Eq", (Expr("Ref", value="N2"), Expr("Const", value=0))),
        proof_receipt="G-DYN-MANIFOLD-II",
    )
    eq = Equation(
        id="v2_evolution",
        lhs=Expr("Derivative", (Expr("Ref", value="v2"),)),
        rhs=Expr("Ref", value="F_v2"), stage=Stage.BACKGROUND,
        exact_predicates=("typeII_aligned",),
    )
    return Bundle(FORMULA_HASH, [q], [eq], [pred])


def test_hash_is_deterministic():
    assert minimal_bundle().content_hash() == minimal_bundle().content_hash()


def test_continuum_rejects_discretization_metadata():
    n = Node("bad", "Field", AuthorityLevel.CONTINUUM, Stage.TRANSPORT,
             "S2", "1", "normal", "scalar", metadata={"ell_max": 8})
    with pytest.raises(SymIRError, match="discretization metadata"):
        n.validate()


def test_near_manifold_cannot_rewrite_authority():
    p = Predicate("nearCS", PredicateClass.NUMERICAL_HINT,
                  Expr("Less", (Expr("Ref", value="d_CS"), Expr("Const", value=1e-4))))
    b = Bundle(FORMULA_HASH, [], [Equation("bad", Expr("Ref", value="x"),
        Expr("Const", value=0), Stage.BACKGROUND, ("nearCS",))], [p])
    with pytest.raises(SymIRError, match="may not rewrite authority"):
        b.validate()


def test_exact_invariant_may_specialize():
    assert exact_specialization_allowed(minimal_bundle().predicates[0])


def test_pointwise_rate_cannot_scalarize():
    with pytest.raises(SymIRError, match="cannot be coerced"):
        require_no_scalarization(minimal_bundle().nodes[0])


def test_observed_sky_is_output_only():
    n = Node("sky", "ObservedSkyEndpoint", AuthorityLevel.CONTINUUM,
             Stage.TRANSPORT, "S2", "1", "transport", "map",
             consumes_tokens=("transport_to_sky_once",))
    with pytest.raises(SymIRError, match="output-only"):
        n.validate()


def test_once_only_token_cannot_be_consumed_twice():
    a = Node("sky1", "ObservedSkyEndpoint", AuthorityLevel.CONTINUUM,
             Stage.OUTPUT, "sky", "1", "transport_to_sky", "map",
             consumes_tokens=("sky_once",))
    b = Node("sky2", "ObservedSkyEndpoint", AuthorityLevel.CONTINUUM,
             Stage.OUTPUT, "sky", "1", "transport_to_sky", "map",
             consumes_tokens=("sky_once",))
    with pytest.raises(SymIRError, match="consumed more than once"):
        Bundle(FORMULA_HASH, [a, b], []).validate()
