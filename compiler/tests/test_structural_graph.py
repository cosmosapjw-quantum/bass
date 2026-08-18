import sys
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from symir.core import AuthorityLevel, Bundle, Equation, Expr, Node, Predicate, PredicateClass, Stage, SymIRError
from structural.graph import compile_structure

H="3ecf0dbc8b47a8af83da81e9ed37823b6922e139e420c5bfa2e071b6bbabe361"

def ref(x): return Expr("Ref", value=x)
def der(x): return Expr("Derivative", (ref(x),))
def add(*xs): return Expr("Add", tuple(ref(x) for x in xs))
def node(x, stage=Stage.BACKGROUND, role="unknown"):
    return Node(x,"Field",AuthorityLevel.CONTINUUM,stage,"R","1","normal","scalar",metadata={"structural_role":role})

def test_alias_elimination_is_exact_and_deterministic():
    b=Bundle(H,[node("a"),node("b"),node("c")],[
        Equation("alias",ref("b"),ref("a"),Stage.BACKGROUND),
        Equation("ec",der("c"),add("b","c"),Stage.BACKGROUND),
        Equation("ea",der("a"),ref("a"),Stage.BACKGROUND)])
    r=compile_structure(b)
    assert r.aliases=={"b":"a"}
    assert "alias" not in r.incidence
    assert set(r.equation_to_variable.values())=={"a","c"}

def test_numerical_hint_cannot_activate_specialization():
    p=Predicate("near",PredicateClass.NUMERICAL_HINT,Expr("Const",value=True))
    b=Bundle(H,[node("x")],[Equation("e",der("x"),ref("x"),Stage.BACKGROUND)], [p])
    with pytest.raises(SymIRError,match="not exact"):
        compile_structure(b,["near"])

def test_inactive_exact_branch_equation_is_not_structuralized():
    p=Predicate("branch",PredicateClass.EXACT_INVARIANT,Expr("Const",value=True),"proof-1")
    b=Bundle(H,[node("x")],[Equation("conditional",der("x"),ref("x"),Stage.BACKGROUND,("branch",))],[p])
    r0=compile_structure(b)
    r1=compile_structure(b,["branch"])
    assert r0.active_equations==()
    assert r1.active_equations==("conditional",)
    assert r1.proof_receipts==("proof-1",)

def test_matching_finds_balanced_system():
    b=Bundle(H,[node("x"),node("y")],[
        Equation("ex",der("x"),ref("y"),Stage.BACKGROUND),
        Equation("ey",der("y"),ref("x"),Stage.BACKGROUND)])
    r=compile_structure(b)
    assert not r.unmatched_equations
    assert not r.unmatched_variables
    assert set(r.equation_to_variable)=={"ex","ey"}

def test_scc_groups_cycle_into_one_blt_block():
    b=Bundle(H,[node("x"),node("y")],[
        Equation("ex",der("x"),ref("y"),Stage.BACKGROUND),
        Equation("ey",der("y"),ref("x"),Stage.BACKGROUND)])
    r=compile_structure(b)
    assert len(r.blocks)==1
    assert r.blocks[0].variables==("x","y")

def test_blt_orders_dependencies_before_dependents():
    b=Bundle(H,[node("x"),node("y"),node("z")],[
        Equation("ex",der("x"),ref("x"),Stage.BACKGROUND),
        Equation("ey",der("y"),add("x","y"),Stage.BACKGROUND),
        Equation("ez",der("z"),add("y","z"),Stage.BACKGROUND)])
    r=compile_structure(b)
    assert [b.variables for b in r.blocks]==[("x",),("y",),("z",)]
    assert r.blocks[1].dependencies==(0,)
    assert r.blocks[2].dependencies==(1,)

def test_stage_extraction_is_preserved():
    b=Bundle(H,[node("x",Stage.BACKGROUND),node("q",Stage.COLLISION)],[
        Equation("ex",der("x"),ref("x"),Stage.BACKGROUND),
        Equation("eq",ref("q"),ref("x"),Stage.COLLISION)])
    r=compile_structure(b)
    assert r.stage_equations=={"background":("ex",),"collision":("eq",)}

def test_under_determined_diagnostic():
    b=Bundle(H,[node("x"),node("y")],[Equation("ex",der("x"),ref("x"),Stage.BACKGROUND)])
    r=compile_structure(b)
    assert r.unmatched_variables==("y",)

def test_result_hash_is_deterministic():
    eqs=[Equation("ex",der("x"),ref("x"),Stage.BACKGROUND),Equation("ey",der("y"),add("x","y"),Stage.BACKGROUND)]
    b1=Bundle(H,[node("x"),node("y")],eqs)
    b2=Bundle(H,[node("y"),node("x")],list(reversed(eqs)))
    assert compile_structure(b1).content_hash()==compile_structure(b2).content_hash()
