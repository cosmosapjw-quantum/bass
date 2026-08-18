import json
import sympy as sp
from pathlib import Path

Sp,Sm,X,N,v,gam=sp.symbols("Sigma_p Sigma_m Sigma_13 N1 v2 gamma")
rt3=sp.sqrt(3)
Sigma2=Sp**2+Sm**2+X**2
Omega=1-Sigma2-N**2/sp.Integer(12)
Gp=1+(gam-1)*v**2
Gm=1-(gam-1)*v**2
sig2=Sp+rt3*Sm
q=2*Sigma2+sp.Rational(1,2)*((3*gam-2)+(2-gam)*v**2)*Omega/Gp
T=((3*gam-4)*(1-v**2)+(2-gam)*sig2*v**2)/Gm
F=sp.Matrix([
 -(2-q)*Sp+N**2/3+gam*Omega*v**2/(2*Gp)-3*X**2,
 -(2-q)*Sm+rt3*gam*Omega*v**2/(2*Gp)+rt3*X**2,
 X*(-(2-q)+3*Sp-rt3*Sm),
 (q-4*Sp)*N,
 v*(T-sig2)
])
vars=[Sp,Sm,X,N,v]
J=sp.simplify(F.jacobian(vars))
spars=[[0 if sp.simplify(J[i,j])==0 else 1 for j in range(5)] for i in range(5)]
jvp=J*sp.Matrix(sp.symbols("dSp dSm dX dN dv"))
out={
 "state":[str(x) for x in vars],
 "rhs":[sp.sstr(sp.factor(x)) for x in F],
 "jacobian":[[sp.sstr(sp.factor(J[i,j])) for j in range(5)] for i in range(5)],
 "exact_sparsity":spars,
 "jvp":[sp.sstr(sp.factor(x)) for x in jvp],
}
print(json.dumps(out,indent=2))
