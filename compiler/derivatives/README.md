# WSC-4 Jacobian / Sparsity / JVP

Authority products:
- exact residual Jacobians `J_x` and `J_dx`;
- exact symbolic sparsity after simplification;
- structural incidence sparsity before cancellation;
- exact symbolic JVP without numerical matrix materialization.

Diagnostics:
- pointwise numerical sparsity;
- finite-difference JVP.

The diagnostics are not allowed to rewrite symbolic sparsity or authority
derivatives.

A low-rank Type-II finite-tilt projector program is included as a first
discretization-layer consumer of JVP/operator-program metadata.  It is
explicitly below Continuum SymIR.
