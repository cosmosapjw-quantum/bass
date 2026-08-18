import sys
from pathlib import Path
import pytest
import sympy as sp

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from symir.core import AuthorityLevel, Bundle, Equation, Expr, Node, Stage
from dae.index import DAEError, mass_matrix_form, pantelides_style_constraint_closure, solve_initialization

H="3ecf0dbc8b47a8af83da81e9ed37823b6922e139e420c5bfa2e071b6bbabe361"
def R(x): return Expr("Ref",value=x)
def C(x): return Expr("Const",value=x)
def D(x): return Expr("Derivative",(R(x),))
def Add(*xs): return Expr("Add",tuple(xs))
def Mul(*xs): return Expr("Mul",tuple(xs))
def Sub(a,b): return Expr("Sub",(a,b))
def Pow(a,b): return Expr("Pow",(a,b))
def Neg(a): return Expr("Neg",(a,))
def N(x): return Node(x,"Field",AuthorityLevel.CONTINUUM,Stage.BACKGROUND,"R","1","normal","scalar",metadata={"structural_role":"unknown"})

def test_index1_mass_matrix_extraction():
    b=Bundle(H,[N("x"),N("y")],[
        Equation("dx",D("x"),Add(Neg(R("x")),R("y")),Stage.BACKGROUND),
        Equation("alg",Add(R("x"),R("y")),C(1),Stage.BACKGROUND)])
    m=mass_matrix_form(b)
    assert m.mass_matrix == (("0","0"),("1","0"))
    assert m.rhs == ("-x - y + 1","-x + y")
    assert m.differential_variables == ("x",)
    assert m.algebraic_variables == ("y",)
    assert m.algebraic_rows == (0,)

def test_nonlinear_derivative_rejected_for_mass_matrix():
    b=Bundle(H,[N("x")],[Equation("bad",Pow(D("x"),C(2)),R("x"),Stage.BACKGROUND)])
    with pytest.raises(DAEError,match="nonlinear in first derivatives"):
        mass_matrix_form(b)

def pendulum_bundle():
    return Bundle(H,[N(x) for x in ("x","vx","y","vy","lam")],[
        Equation("dx",D("x"),R("vx"),Stage.BACKGROUND),
        Equation("dvx",D("vx"),Mul(R("lam"),R("x")),Stage.BACKGROUND),
        Equation("dy",D("y"),R("vy"),Stage.BACKGROUND),
        Equation("dvy",D("vy"),Sub(Mul(R("lam"),R("y")),C(1)),Stage.BACKGROUND),
        Equation("constraint",Add(Pow(R("x"),C(2)),Pow(R("y"),C(2))),C(1),Stage.BACKGROUND)])

def test_pendulum_constraint_closure_exposes_lambda_after_two_differentiations():
    cl=pantelides_style_constraint_closure(pendulum_bundle(),"constraint")
    assert cl.algebraic_unknowns == ("lam",)
    assert cl.introduced_algebraic_at_depth == 2
    assert cl.depth == 2
    assert "lam" not in cl.levels[0]
    assert "lam" not in cl.levels[1]
    assert "lam" in cl.levels[2]

def test_pendulum_hidden_constraints_and_initial_multiplier():
    cl=pantelides_style_constraint_closure(pendulum_bundle(),"constraint")
    init=solve_initialization([sp.sympify(x) for x in cl.levels],
                              {"x":1,"y":0,"vx":0,"vy":0},["lam"])
    assert init.solutions == ({"lam":"0"},)

def test_typeII_codazzi_initialization_forces_v1_zero():
    gamma,Omega,v1,v2,v3=sp.symbols("gamma Omega v1 v2 v3", real=True)
    Gp=1+(gamma-1)*(v1**2+v2**2+v3**2)
    c1=3*gamma*Omega*v1/Gp
    init=solve_initialization([c1],
        {"gamma":sp.Rational(13,10),"Omega":sp.Rational(4,5),
         "v2":sp.Rational(1,20),"v3":0},["v1"])
    assert init.solutions == ({"v1":"0"},)

def test_mass_matrix_hash_is_deterministic():
    b=pendulum_bundle()
    assert mass_matrix_form(b).content_hash()==mass_matrix_form(b).content_hash()
