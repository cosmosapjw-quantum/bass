# WSC-3 DAE / Index / Initialization Implementation Plan

**Goal:** Add public residual/mass-matrix DAE lowering, constrained-system
index-reduction metadata, and consistent-initialization generation.

- [x] residual form
- [x] mass-matrix extraction
- [x] differential/algebraic classification
- [x] pendulum two-derivative closure
- [x] consistent initialization helper
- [x] Type-II Codazzi initialization example
- [x] Wolfram Pantelides/StructuralMatrix oracle
- [x] stacked regression
- [x] commit/push and stacked PR

**Non-claim:** this first constrained-system closure is not a complete general
Pantelides or StructuralMatrix implementation.
