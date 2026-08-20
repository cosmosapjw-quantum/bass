# G-PRE-LIOUVILLE-SAFETY-II hostile audit

## Verdict and claim boundary

The stacked checkpoint is a **physical-screen-subspace polarized
collision/Kato safety layer with explicit fixed-grid AP correction option**.

The AP lane is a discrete numerical correction.  It is not a modification of
the continuum Thomson collision law.  Paired rest-to-normal quadrature remains
the reference lane.  This checkpoint is not a full polarized Liouville solver,
does not establish a generic positivity theorem, and does not authorize
production migration.

## Physical carrier

The raw embedding retains nine real numbers per angular node: six real
symmetric and three imaginary antisymmetric components of a Hermitian
coherency tensor.  Checked APIs canonicalize every accepted near-unit direction
and act on the four-real-dimensional screen carrier

`J = P(e) J P(e)`.

The external input policies are:

- `ScreenInputPolicy::Reject { tolerance }`;
- `ScreenInputPolicy::Project`.

Finite packed input whose projection arithmetic becomes nonfinite is rejected
with `ScreenProjectionArithmeticNonFinite`.  Finite projection/state pairs
whose leakage subtraction overflows are rejected separately with
`ScreenLeakageArithmeticNonFinite`.  Nonfinite velocity, velocity derivative,
direction, weight, tolerance, state, and operator output paths fail closed.

The longitudinal hostile state `J=e a^T+b e^T` remains a raw-kernel null
negative control.  The checked carrier rejects it or projects it away.  On the
104-dimensional physical carrier of the moving paired-grid test, the discrete
collision kernel has one null mode: the moving equilibrium monopole.

## Fixed-grid AP lane

The opt-in scalar operator is

`C_AP = (I-P) C_raw (I-P)`.

The polarized physical implementation applies the corresponding factors in
the explicit right-to-left order

`Q_screen Q_eq C_raw Q_eq Q_screen`.

Independent full-basis probes match these formulas and retain deliberately
wrong one-sided or swapped-order variants as negative controls.  On the fixed
six-node normal-frame grid, raw and corrected moving-equilibrium residuals are
recorded separately:

- raw scalar residual: `1.8027168019362667e-2`;
- corrected scalar residual: `0` in the tested arithmetic;
- `nu=230`, raw stiffness amplification:
  - `alpha=1`: `4.146248644453413e0`;
  - `alpha=1e3`: `4.146248644453413e3`;
  - `alpha=1e5`: `4.1462486444534134e5`.

The paired rest-to-normal reference has raw equilibrium residual
`6.796226888376623e-16` and raw/corrected action difference
`1.6711069443220838e-16`.

## Cone and screen safety

The supplied 12-test regression covers interior, linearly polarized boundary,
and both handednesses of the circular-V cone boundary.  For the circular
boundary, packed component `p8` is `+/-0.5`, the input minimum coherency
eigenvalue is zero, a depth-20 collision action remains finite with output
minimum eigenvalue approximately `0.5`, zero measured screen leakage, one
accepted action, zero rejected actions, and maximum basis 3.

The paired-grid interior and linear-boundary depth-20 lanes record:

- interior input/output minimum eigenvalue:
  `0.15 / 0.4249575562443828`;
- boundary input/output minimum eigenvalue:
  `0 / 0.4076106258561014`;
- boundary screen leakage: `1.3234889800848443e-23`;
- one accepted action, zero rejected actions, maximum basis 12.

The checked Kato exponential records screen leakage
`2.220446049250313e-16`, one accepted action, zero rejected actions, and
maximum basis 12.

These are tested diagnostics, not a positivity theorem.

## Independent audits

- relativistic polarized kinetic-theory audit: 12 supplied plus 7 independent
  probes, 19/19; P0/P1/P2 = 0/0/0;
- quadrature/AP audit: 12 supplied plus 7 independent probes, 19/19;
  P0/P1 = 0/0.

The AP audit independently checks full-basis scalar and polarized operator
order, wrong-order negative controls, paired-grid equivalence across every
physical basis column, finite alpha receipts, and overflow fail-closed paths.

## Open risks

- P0: none.
- P1: none.
- P2: the scalar collision-only AP entry point conservatively requires finite
  derivative factors that it does not use, rejecting an absurd extreme-weight
  lane; the committed receipt tests reuse some implementation-derived oracle
  pieces and naïve test norms, offset by independent full-basis and stable-norm
  hostile probes.

## Next DAG node

The next node is `G-POL-LIOUVILLE-II`.  It remains a future polarized
geometric/free-streaming transport implementation and is not provided by this
safety checkpoint.
