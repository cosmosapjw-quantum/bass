import sys, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from symir.core import AuthorityLevel, Bundle, Equation, Expr, Node, Predicate, PredicateClass, Stage
from structural.graph import compile_structure
H="3ecf0dbc8b47a8af83da81e9ed37823b6922e139e420c5bfa2e071b6bbabe361"
def R(x): return Expr("Ref",value=x)
def D(x): return Expr("Derivative",(R(x),))
def N(x,stage): return Node(x,"DerivedField",AuthorityLevel.CONTINUUM,stage,"R","1","normal","scalar",metadata={"structural_role":"unknown"})
p=Predicate("typeII_aligned",PredicateClass.EXACT_INVARIANT,Expr("Const",value=True),"G-DYN-MANIFOLD-II")
nodes=[N("v2",Stage.BACKGROUND),N("P",Stage.COLLISION),N("Pdot",Stage.COLLISION),N("K",Stage.COLLISION)]
eqs=[
 Equation("v2dot",D("v2"),R("v2"),Stage.BACKGROUND,("typeII_aligned",)),
 Equation("Pdef",R("P"),Expr("ProjectorFromTilt",(R("v2"),)),Stage.COLLISION,("typeII_aligned",)),
 Equation("Pdotdef",R("Pdot"),Expr("Mul",(R("P"),R("v2"))),Stage.COLLISION,("typeII_aligned",)),
 Equation("Kdef",R("K"),Expr("Commutator",(R("Pdot"),R("P"))),Stage.COLLISION,("typeII_aligned",)),
]
r=compile_structure(Bundle(H,nodes,eqs,[p]),["typeII_aligned"])
print(json.dumps({**r.canonical_dict(),"content_hash":r.content_hash()},indent=2))
