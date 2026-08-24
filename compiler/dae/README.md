# WSC-3 DAE / Index / Initialization

Implemented:
- residual form `F(t,x,x')=0`;
- derivative-linear mass matrix `M x' = f`;
- differential/algebraic classification;
- first-order constrained-system Pantelides-style differentiation closure;
- consistent-initialization solve helper;
- Wolfram Pantelides/StructuralMatrix oracle receipt;
- BASS Type-II Codazzi initialization example.

The first WSC-3 differentiation closure is intentionally not claimed to be a
complete general Pantelides or StructuralMatrix implementation. General graph
augmentation, dummy derivatives and cancellation-aware structural-matrix
analysis remain open compiler work.
