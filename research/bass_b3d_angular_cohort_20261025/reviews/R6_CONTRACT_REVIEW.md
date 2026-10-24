# Independent R6 review — B3d fixed angular cohort

## Decision and independence

**PASS_SCOPED for the stated preparation and bounded implementation. No material physical or mathematical blocker was found.** Numerical execution still requires root's S0 preservation ACK and the contract's pre-execution exact symbolic evidence. Record the small convention clarifications below before execution; they change neither the model nor any numerical threshold. No second broad review is needed for those clarifications.

This reviewer did not author the frozen contract or implementation and ran no numerical process or IVP. The reviewer supplied independent literature/analytic notes and checked the root contract against the actual unchanged parent source conventions. This is independent-agent review, not evidence of different-model scientific review. Remote publication approval and backup ACK are outside this scientific decision.

## Inputs and actual read scope

Read `FROZEN_CONTRACT.md` in full, the central authority/current-source receipts, the copied prior B3c handoff/admission, the actual parent `cubature14` and emitted packet construction, actual `kinetic.moments/tensor`, actual `FixedScale`, and the actual LINE01 energy card. `R6_INPUT_IDENTITIES.json` records the reviewed file bytes and the unchanged source/copy identities. Primary literature and official SciPy1.17 source reads are detailed in `theory/LITERATURE_INTAKE.md` and its tool-receipt file.

The prior B3c time-splitting result is preserved as owner-reported. This new unit isolates a finite cohort's angular error without repeating the12 old IVPs. The actual3NPZ+6owner-module identity checks remain reused; no original NPZ or old archive is consumed here.

## Scientific contract checks

### 1. Source measure, units and frame — PASS

The normalized measure `q(n)dOmega/(4pi)` is positive and integrates to1 for symmetric trace-free S. Taking `n_b=1 m^-3` explicitly defines a diagnostic cohort; no atomic transition or new donor is silently executed. The actual energy owner E_b and fixed `Pstar=E_b/c` are consistent with massless `k_birth=n` and `w_birth=alphaL*E_b*n_b*A*q`.

The moment scale `rho_star=alphaL*E_b*n_b*D*exp(-a)` is positive and independent of the numerical approximation. Both physical SI and BASS tensor normalizations are dimensionally consistent. No rest-mass denominator suppresses a radiation error. Pi is current STF stress rather than an injection rate. The non-tilted hydrogen/normal tetrad choice is explicit.

### 2. Clock, dilution and support — PASS

Birth labels stay fixed. Homogeneous diagonal transport gives momentum `R*n` and the common number-density factor `det(R)`; energy redshift is then supplied once by the moment. No extra Lorentz Doppler weight or event-rate clock factor is applied. The stated direction Jacobian is correct when changing variables and is not inserted twice.

The path parameter chi is explicitly algebraic, so no unspecified proper-time duration is needed for this cohort map. With a=.4 and B=(.3,−.1,−.2), every directional expansion coefficient is at least.2 for eta∈[0,1]. Along the specified chi path each photon energy decreases. This closes the selected unresolved-line red-side support assumption without claiming a resolved line-wing absorption result or an actual REC incident trace.

### 3. Angular exactness and leading errors — PASS

The actual14point rule's sign/permutation symmetry and constant/second/fourth moments establish degree5 exactness. Its three degree6 error classes agree with the frozen fractions. Direct expansion of `sqrt(sum exp(-2eta*b_i)n_i²)` gives the stated ANISO energy coefficient and both diagonal/offdiagonal pressure coefficients. For the frozen primary diagonal S=B/2, the nonzero exact coefficients are given under R6-C2 below.

The constructive26rule uses the canonical positive axis/edge/corner weights in official SciPy1.17. Its degree6 moments add the missing monomial classes, establishing degree7 exactness by symmetry. Numerical comparison with this constructed cohort is distinct from consuming the saved REC35×26 inventory. The contract correctly does not presume that either rule passes2e-8 everywhere.

### 4. Continuum reference and analytic bound — PASS

For K=40, the largest polynomial degree is84: q contributes2, the pressure numerator another2, and z^40 contributes80. A128point uniform azimuth rule integrates all relevant nonzero Fourier frequencies exactly. After azimuth integration, each surviving Cartesian monomial becomes a polynomial in mu of degree at most84, within64point Gauss-Legendre exactness127. This remains true for the co-rotated physical pair.

The exact binomial coefficient ratios are below1 in absolute value beyond the first omitted term, so the geometric-tail bound holds for `|z|<=delta<1`. The selected eigenvalue ratio gives `delta<=tanh(.5)`. Positivity and exact normalization of q justify averaging the uniform remainder without an additional q_max factor; the same is true for ideal positive reference weights. The factor2 accounts for quadrature remainder plus continuum remainder. The pressure prefactor is bounded by `rmax²/sqrt(a0)` componentwise. These are ideal-node truncation bounds; the contract correctly separates floating node/summation error from interval certification.

The independent axial S=0 closed formulas are correct, including `Pxx=Pyy=(F−Pzz)/2`. The isotropic limit must use its explicit branch to avoid a removable0/0. The octant cross-check is legitimate for the diagonal fixtures with the parity convention in R6-C1.

### 5. Acceptance metrics and claim scope — PASS

F-normalized tensor errors remain meaningful for near-zero offdiagonal or anisotropic stresses. The numerical gates distinguish reference accuracy, physical packet mapping, exact leading coefficients, resolved small-eta orders and the reported2e-8 benchmark. The order parameter is redshift deformation eta, not an ODE step. A finite-table result does not establish a uniform physical domain certificate or repair the coupled geometry of the prior trajectory.

Simultaneously rotating the physical tensors and rays is a tensor-coordinate covariance test. Keeping the numerical ray set fixed while rotating the physical pair measures quadrature orientation dependence. The contract correctly distinguishes these operations and does not label the second a covariance failure.

Actual tensor/number mapping should be checked independently of the stored STF reconstruction. `kinetic.moments` enforces Pi_zz=−Pi_xx−Pi_yy, so that representation's zero trace alone is not an independent numerical conservation witness; `kinetic.tensor` or directly summed P provides the intended check.

### 6. Execution boundary and prior work — PASS

One focused test, one finite sweep and one summary/plot process are proportional to this scope. The combined120wall/60CPU guard includes the already measured superseded B3c1 Wolfram debit. Historical remaining resources stay null and are not reset. Source/card/core copies must remain unchanged. No old IVP, temporal replay, archive or NPZ download is needed. Scientific admission remains separate from Git identity, upload ACK, repository CI and full remote restore.

## Narrow pre-execution clarifications

### R6-C1 — octant parity, reporting clarity

The first-octant integral may be multiplied by8 only for reflection-even integrands such as F and diagonal P. The full-sphere flux and offdiagonal P vanish by sign-reflection cancellation for diagonal S,C. Compute those by explicit sign folding or state their analytic zero; do not multiply a positive first-octant cross moment by8 and compare it with a full-sphere zero. This is a convention clarification, not a different reference or extra numerical run.

The bounded interface must also enforce the stated continuous positivity `q_min=1+lambda_min(S)>0`, not merely positivity at14/26sampled rays. Admitted C is diagonal-positive or a symmetric positive-definite co-rotation of it. If a free-matrix C interface is exposed, symmetry belongs to that domain check; no expansion to arbitrary nonsymmetric transport is admitted by this review.

### R6-C2 — explicit primary coefficients and order reporting

For `B=diag(3/10,−1/10,−1/5)`, with Delta=Q14−continuum:

| Fixture | Energy coefficient | Diagonal pressure coefficient |
|---|---|---|
| ANISO S=B/2 | `DeltaF/eta² -> −9/35000` | `DeltaP/eta -> diag(13,−11,−2)/10500` |
| ISO S=0 | `DeltaF/eta³ -> −9/17500` | `DeltaP/eta² -> diag(13,−11,−2)/3500` |

The ISO general expressions are `−tr(B³)/35` for cubic energy and `(3*b_i²−tr(B²))/35` for quadratic pressure. All offdiagonal coefficients of these diagonal fixtures are zero.

Freeze the coefficient gate as `maxabs(DeltaP/eta^p−C_exact)/maxabs(C_exact)<=.05` for pressure and the corresponding scalar expression for energy. The coefficient-comparison Delta is the raw normalized F/P difference, before dividing by reference F. Define the finest resolved triplet as the first three consecutive small eta with both adjacent pair errors above4096eps; apply the stated window to its two adjacent pair orders. No fitted coefficient, hidden denominator change or tolerance adjustment is authorized.

These clarifications can be recorded in one root addendum and acknowledged by the implementer. Their closure does not require another broad R6 cycle. C9 should inspect their direct implementation together with the actual results and figure.

## Final claim ceiling

The contract is sufficient to quantify finite angular error for the selected photon cohort and to compare a constructive positive26rule against the actual14rule. It does not close native finite absorption, calibrated REC history, a full angular continuum certificate for the old B3c trajectory, B4restart, B5general domains, or overall physical completion. Different-model scientific review remains NOT_RUN.

## Targeted clarification closure — final R6 decision

Read root's `CONTRACT_ADDENDUM.md` in full before numerical execution. It explicitly closes octant parity, the exact14rule primary coefficients, signed coefficient normalization and both adjacent orders of the finest resolved triplet. Targeted readback of the prepared interface also confirms continuous eigenvalue-based q positivity, symmetric positive transport, sign-reflected octant evaluation, and the specified coefficient/order expressions. This readback is not a numerical test or full C9 code review.

**Final R6: PASS_SCOPED / APPROVED_FOR_FROZEN_BOUNDED_EXECUTION_AFTER_ROOT_S0_ACK. R6-C1 and R6-C2 are CLOSED; material open scientific findings0.** No model, tolerance, fixture, reference quadrature or resource limit changed. The implementer may execute the already frozen bounded commands after root confirms S0 preservation. C9 and final scientific admission remain separate later steps.
