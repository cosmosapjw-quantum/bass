# G-POL-LIOUVILLE-II-B1 hostile audit

## Verdict

**PASS as a recovered local tensor-to-Stokes sign authority.**

The earlier transcript claim that a PR #12 existed was not durable.  Fresh GitHub inspection found no such PR or branch, so B1 was classified `PARTIALLY_RECOVERED` and reconstructed from the PR #11 tensor authority.  The present source, tests, independent oracle, mutation evidence and receipt are the new durable authority.

## Physical contract

Metric signature remains `(-,+,+,+)`.  The photon propagation direction is `e`; B1 does not identify it with the observer sky direction `n=-e`.

For a right-handed screen `s1 x s2 = e`,

`H = 1/2 [[I+Q,U-iV],[U+iV,I-Q]]`.

Consequences fixed by finite tensor contraction:

- canonical xy screen: `packed[8] = -V/2`;
- passive dyad rotation: `(Q+iU)'=exp(-2 i psi)(Q+iU)`;
- active tensor rotation: `(Q+iU)'=exp(+2 i psi)(Q+iU)`;
- handedness reversal `s2 -> -s2`: `(I,Q,U,V)->(I,Q,-U,-V)`.

All variables in this gate are dimensionally identical to the bolometric coherency tensor except the dimensionless angle and basis vectors.

## Code audit

The Rust module validates finite unit/tangent/orthogonal dyads, stores handedness explicitly, converts in both directions, separates active and passive APIs, and rejects nonfinite states, angles and axes.  A deterministic local canonical dyad is provided only as a chart helper, not a global atlas.

## Independent evidence

A separate Python oracle uses complex Hermitian 3x3 tensors and dyad contractions, without importing Rust formulas.  Across two nontrivial states and seven finite angles:

- passive phase max error: `4.44e-16`;
- active phase max error: `4.44e-16`;
- active/passive inverse max error: `8.88e-16`;
- invariant max defect: `1.78e-15`;
- handedness error: `4.44e-16`;
- generated V on the V=0 lane: `0`;
- canonical p8 sign error: `0`.

Rust regression: 9/9.  Python regression: 6/6.

## Adversarial mutations

The regression rejects each of:

1. passive phase sign reversal;
2. active phase sign reversal;
3. V extraction sign reversal.

## Risks and claim boundary

P0: none in the tested local adapter.

P1: none for B2 prerequisite use.

P2:

- the deterministic dyad helper is discontinuous across chart-selection boundaries;
- the external `n=-e`, IAU/COSMO and HEALPix bridge remains absent by design.

Allowed claim: local BASS tensor/Stokes sign and finite active/passive spin-2 phase are sealed.

Not allowed: global map convention, E/B or harmonic readiness, observer-output compatibility, or full polarized Liouville closure.
