import sys
from pathlib import Path

import numpy as np
import sympy as sp

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from symir.core import AuthorityLevel, Bundle, Equation, Expr, Node, Stage
from derivatives.jacobian import (
    calculate_residual_jacobians,
    exact_jvp,
    finite_difference_jvp,
    numerical_sparsity,
)
from derivatives.kato_lowrank import scalar_boosted_projector, directional_parameter_jvp

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

def dae_bundle():
    return Bundle(H,[N("x"),N("y")],[
        Equation("alg",Add(R("x"),R("y")),C(1),Stage.BACKGROUND),
        Equation("dx",D("x"),Add(Neg(R("x")),Pow(R("y"),C(2))),Stage.BACKGROUND),
    ])

def test_residual_jacobians_split_x_and_dx():
    j=calculate_residual_jacobians(dae_bundle())
    assert j.J_x == (("1","1"),("1","-2*y"))
    assert j.J_dx == (("0","0"),("1","0"))
    assert j.exact_sparsity_dx == ((0,0),(1,0))

def test_exact_jvp_matches_materialized_symbolic_jacobian():
    vx=(sp.Integer(2),sp.Integer(3)); vdx=(sp.Integer(5),sp.Integer(7))
    direct=exact_jvp(dae_bundle(),vx,vdx); y=sp.Symbol("y")
    assert tuple(sp.expand(x) for x in direct) == (sp.Integer(5), 7-6*y)

def test_structural_sparsity_can_exceed_exact_after_cancellation():
    b=Bundle(H,[N("x")],[Equation("cancel",Add(R("x"),Neg(R("x"))),C(0),Stage.BACKGROUND)])
    j=calculate_residual_jacobians(b)
    assert j.exact_sparsity_x == ((0,),)
    assert j.structural_sparsity_x == ((0,),)

def test_numerical_sparsity_is_only_pointwise():
    j=calculate_residual_jacobians(dae_bundle()); num=numerical_sparsity(j.J_x,{"x":0,"y":0})
    assert j.exact_sparsity_x[1][1] == 1
    assert num[1][1] == 0

def test_finite_difference_jvp_agrees_with_exact_numeric():
    def f(x,dx): return np.array([x[0]+x[1]-1, dx[0]+x[0]-x[1]**2])
    x=np.array([.3,.4]);dx=np.array([.2,.0]);vx=np.array([.7,-.2]);vdx=np.array([.5,.1])
    fd=finite_difference_jvp(f,x,dx,vx,vdx,eps=1e-7)
    exact=np.array([vx[0]+vx[1], vdx[0]+vx[0]-2*x[1]*vx[1]])
    assert np.max(np.abs(fd-exact)) < 1e-8

def test_lowrank_projector_idempotency_and_kato_identity():
    e=np.array([[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]],float)
    w=np.full(6,4*np.pi/6); op=scalar_boosted_projector(e,w,.05,axis=1)
    rng=np.random.default_rng(4); y=rng.normal(size=6)
    assert np.max(np.abs(op.P(op.P(y))-op.P(y))) < 1e-14
    vdot=.03
    lhs=op.K(op.P(y),vdot)-op.P(op.K(y,vdot)); rhs=op.Pdot(y,vdot)
    assert np.max(np.abs(lhs-rhs)) < 1e-13

def test_lowrank_projector_directional_parameter_jvp():
    e=np.array([[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]],float)
    w=np.full(6,4*np.pi/6); v=.03; op=scalar_boosted_projector(e,w,v,axis=1)
    rng=np.random.default_rng(5); y=rng.normal(size=6); dy=rng.normal(size=6); dv=.2
    exact=directional_parameter_jvp(op,y,dy,dv); eps=1e-7
    plus=scalar_boosted_projector(e,w,v+eps*dv,axis=1).P(y+eps*dy)
    minus=scalar_boosted_projector(e,w,v-eps*dv,axis=1).P(y-eps*dy)
    fd=(plus-minus)/(2*eps)
    assert np.max(np.abs(fd-exact)) < 2e-8

def test_jacobian_receipt_hash_is_deterministic():
    assert calculate_residual_jacobians(dae_bundle()).content_hash() == calculate_residual_jacobians(dae_bundle()).content_hash()
