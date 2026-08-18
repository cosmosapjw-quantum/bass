## Scope

WSC-3 adds a public BASS-owned DAE layer on top of Neutral Continuum SymIR and WSC-2 structural metadata.

### Implemented
- residual `F(t,x,x')=0` representation;
- derivative-linear mass-matrix extraction;
- differential/algebraic classification;
- constrained first-order Pantelides-style differentiation closure;
- consistent-initialization helper;
- Type-II Codazzi initialization example;
- Wolfram Pantelides/StructuralMatrix oracle.

### Verification
`python -m pytest -q compiler/tests`

Result: **25 passed**.

### Claim boundary
This PR does **not** claim a complete general Pantelides or StructuralMatrix implementation. General graph augmentation, dummy derivatives and cancellation-aware structural-matrix parity remain open.

Next: WSC-4 Jacobian/sparsity/JVP parity.
