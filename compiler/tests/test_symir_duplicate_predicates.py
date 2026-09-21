"""Predicate IDs must identify one rule before any structural lookup."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from symir.core import Bundle, Equation, Expr, Predicate, PredicateClass, Stage, SymIRError
from structural.graph import compile_structure


def make_bundle(predicates):
    return Bundle("fixture", [], [Equation(
        "equation", Expr("Ref", value="x"), Expr("Const", value=0),
        Stage.BACKGROUND, ("condition",))], predicates)


@pytest.mark.parametrize("operation", ["validate", "canonical_json", "compile_structure"])
@pytest.mark.parametrize("reverse", [False, True])
def test_duplicate_predicate_cannot_change_authority_by_list_order(operation, reverse):
    predicates = [
        Predicate("condition", PredicateClass.NUMERICAL_HINT, Expr("Const", value=False)),
        Predicate("condition", PredicateClass.EXACT_INVARIANT, Expr("Const", value=True), "proof"),
    ]
    value = make_bundle(list(reversed(predicates)) if reverse else predicates)
    with pytest.raises(SymIRError, match="duplicate predicate id"):
        if operation == "compile_structure":
            compile_structure(value, ["condition"])
        else:
            getattr(value, operation)()


def test_unused_duplicate_predicates_are_also_ambiguous():
    p = Predicate("unused", PredicateClass.EXACT_IDENTITY, Expr("Const", value=True))
    with pytest.raises(SymIRError, match="duplicate predicate id"):
        Bundle("fixture", [], [], [p, p]).content_hash()


def test_unique_predicates_keep_order_independent_hash_and_proof_receipt():
    exact = Predicate("condition", PredicateClass.EXACT_INVARIANT, Expr("Const", value=True), "proof")
    hint = Predicate("hint", PredicateClass.NUMERICAL_HINT, Expr("Const", value=False))
    a, b = make_bundle([exact, hint]), make_bundle([hint, exact])
    assert a.content_hash() == b.content_hash()
    assert compile_structure(a, ["condition"]).proof_receipts == ("proof",)
    assert compile_structure(a).active_equations == ()
