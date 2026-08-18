# BASS Neutral Continuum SymIR v1

This IR sits **above** every angular/energy discretization.

## Hard invariants

1. Continuum nodes cannot contain `ell_max`, Lebedev nodes, energy grids,
   interpolation, Strang, Krylov, or other numerical-discretization metadata.
2. A pointwise angular collision rate is not a scalar. `q_v(e)` remains a
   `PointwiseRate` / `DiagonalAngularOperator`.
3. Only `exact_identity` and `exact_invariant` predicates may rewrite authority
   equations.
4. `numerical_hint` and `physical_approximation` predicates may influence a
   numerical polyalgorithm but may not rewrite the physics authority.
5. `ObservedSkyEndpoint` is output-only.
6. spectral→bolometric and transport→observed-sky maps are represented with
   once-only tokens.
7. Every transformation pass carries content hashes and proof/provenance
   receipts.

## Explicit non-goals of v1

- no equation-variable matching;
- no tearing/BLT;
- no Pantelides implementation;
- no generated Rust code;
- no discretization IR.

Those are subsequent compiler passes built on this contract.
