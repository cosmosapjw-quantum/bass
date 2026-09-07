"""Regression for equation IDs overwritten by structural-analysis mappings."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from symir.core import AuthorityLevel, Bundle, Equation, Expr, Node, Stage, SymIRError
from structural.graph import compile_structure

FORMULA_HASH = "3ecf0dbc8b47a8af83da81e9ed37823b6922e139e420c5bfa2e071b6bbabe361"


def bundle(equation_ids=("ex", "ey"), second_stage=Stage.BACKGROUND):
    nodes = [Node(x, "Field", AuthorityLevel.CONTINUUM, Stage.BACKGROUND,
                  "R", "1", "normal", "scalar") for x in ("x", "y")]
    equations = [Equation(identifier, Expr("Derivative", (Expr("Ref", value=x),)),
                          Expr("Ref", value=x), stage)
                 for identifier, x, stage in zip(equation_ids, ("x", "y"),
                                                 (Stage.BACKGROUND, second_stage))]
    return Bundle(FORMULA_HASH, nodes, equations)


@pytest.mark.parametrize("operation", ["validate", "canonical_json", "compile_structure"])
@pytest.mark.parametrize("second_stage", [Stage.BACKGROUND, Stage.COLLISION])
def test_duplicate_equations_are_rejected_before_overwrite(operation, second_stage):
    value = bundle(("duplicate", "duplicate"), second_stage)
    with pytest.raises(SymIRError, match="duplicate equation id"):
        if operation == "compile_structure":
            compile_structure(value)
        else:
            getattr(value, operation)()


def test_distinct_equations_preserve_both_variables_and_order_independent_hash():
    value = bundle()
    result = compile_structure(value)
    assert result.equation_to_variable == {"ex": "x", "ey": "y"}
    assert result.unmatched_equations == ()
    assert result.unmatched_variables == ()
    reordered = Bundle(FORMULA_HASH, list(reversed(value.nodes)),
                       list(reversed(value.equations)))
    assert reordered.content_hash() == value.content_hash()
    assert compile_structure(reordered).canonical_json() == result.canonical_json()


def test_empty_equations_and_separate_identifier_namespaces_remain_valid():
    Bundle(FORMULA_HASH, [], []).validate()
    value = bundle(("x", "y"))
    value.validate()
    assert compile_structure(value).equation_to_variable == {"x": "x", "y": "y"}
