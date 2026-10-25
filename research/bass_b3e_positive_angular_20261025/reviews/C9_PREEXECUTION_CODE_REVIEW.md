# C9 read-only preexecution code review

**Verdict: PASS_SCOPED_FOR_BOUNDED_EXECUTION. Material open findings: 0.**

This is an independent review of the actual implementation before its first
scientific child. The reviewer supplied the independent mathematical derivation
and R6 contract review but did not implement the code. No scientific numerical
process, Wolfram evaluation or IVP was run by the reviewer. Read-only file
hash checks, JSON inspection and static AST parsing were performed. The actual
input hashes are in `C9_PREEXECUTION_INPUT_IDENTITIES.json`.

The positive next action is root confirmation of the actual S0 backup ACK,
then the three frozen metered commands. Final scientific admission remains
pending those actual results and actual PNG inspection. No scientific gate,
fixture, tolerance or claim scope is changed by this review.

## Source identity and execution boundary

- All14 files listed in IMPLEMENTATION_READINESS match their recorded hashes.
- All9 SOURCE_COPIES entries match their actual destination bytes, including
  the immutable B3d raw reference and the independent theory/receipt copies.
- The actual kinetic tensor/moments implementation and FixedScale conversion
  were read. Parent/vendor code is unchanged. The reused raw reference has
  the expected14 fixtures and F/P/pi/flux/T fields; shape rescaling does not
  touch density dilution or the original Q14/Q26 relative errors.
- All5 new scientific/test Python files parse as valid AST without import or
  execution. This is syntax evidence only, not runtime/test evidence.
- The raw and parsed Wolfram evidence is present; parsed evidence reports
  the actual16 exact zero residual groups. The independent continuous proof
  remains the basis for the quantified bound, rather than those finite cases.

## Equation-to-code review

### `positive_angular.py`

The implementation validates finite real matrices and physical density, checks
symmetry/trace and continuous source positivity from the minimum eigenvalue,
and rejects nonpositive determinant, singular R and the frozen outgoing/
conditioning violations. It does not project S or clip q. The prescribed
boundary fixtures use nᵀ(I+S)n, which is a sum of nonnegative diagonal terms
for G4/G5 and has exactzero on their±x source directions.

`geometry` implements H=I/3+2S/15, M=RHRᵀ, s,delta and the secant lower
energy consistently. `bound` uses the signed binomial recurrence followed by
absolute value, the tplus/tminus ratio, factor2, the Frobenius source-aware
bound and the explicitly conservative baseline. `select` records every K
candidate and returns the first sufficient K, preserving cap exhaustion as
BoundNotMet with its history. The direct fixed-K bound may exceed the selector's
K64 cap for reference diagnostics, as the contract requires for K93.

`sphere_rule` has normalized weights w_mu/(4N),2N azimuths and2N² nodes.
`moments` retains signed flux and tensor entries, computes raw spatial trace
independently of the STF representation, and uses physical momentum once.
`packets` uses k=Rn, w=alphaL E_b n_b detR A q and zero mass. The copied
kinetic tensor then agrees with the declared physical normalization when
divided by alphaL E_b n_b detR. No event clock, source transaction or alternate
energy normalization is inserted.

### `run_sweep.py`

The inherited14 cases consume the hash-bound raw B3d N64 data and rescale all
shape tensor fields by exp(−.4). Their original Q14/Q26 errors remain copied
values. There is no call to the old sweep, temporal integrator,14/26 generator,
or a reconstructed old campaign.

For5 new cases both selectors are evaluated before the new direct moments.
The reference routine builds its own polar rings and integrates them directly;
it does not call the selector or selected-rule builder. The64/96 comparison
and fixedK61/K93 bounds are recorded separately. Sharing NumPy's Gauss-node
generator between direct references is correctly treated as floating numerical
evidence, not a rigorous interval certificate.

The covariance code uses separate birth Oy and final Ox rotations, transforms
the original numerical reference into the final frame and separately evaluates
co-rotated and canonical rays. Bound/M residuals use the declared energy scale;
K equality is exact. The mixture concatenates actual packets once and sums
signed tensors with positive E_b n_b detR factors. Its Loewner matrix is
Σc_a beta_a M_a, closing R6 clarification1 without a fictitious average map.

The gate calculations correspond to A–F: sufficient/minimal K, both target
norms, actual error versus ideal bound plus the separate allowance, signed
Loewner eigenvalue residuals, reference refinement, raw invariants, packet
mapping, isotropic oracle, covariance and positive mixture. Every row and failed
gate is serialized before a nonzero sweep exit. The max(0,−λ_min) expression
only reports a PSD residual; it does not modify P. All physical data are kept.

### `tests/test_positive_angular.py`

This is one focused custom script, as declared. It enumerates all Cartesian
monomials through total degree8 atNmu5 against the double-factorial sphere
formula, checks the exact H/M identities for noncommuting inputs, tests the
G5 isotropic analytic result withK0/18rays, and checks exact angular zeros.
The cap test requires maxK0 to refuse G1 and preserve its failing bound.
The invalid-input table covers the specified finite/real/shape, symmetry,
trace, continuous positivity, determinant/singularity, conditioning/outgoing,
density and zero/negative-mixture cases. A zero-coefficient mixture member
contributes no error or denominator. These tests use explicit formulas and
contracts, and do not merely check that one implementation calls itself.

### `summarize.py`

All rows and every selector candidate are exported to CSV. Plot inputs come
from the new saved raw output. The19 main endpoints,2 orientation checks and
1 mixture have separate labels; selector count comparison is restricted to
the19main endpoints. The original coarse-rule failures remain accessible in
raw data and all-rows CSV. The log display floor is labelled, with explicit
zero markers and unchanged exact numerical data. The actual rendered PNG
will still need final visual inspection; static source review cannot certify
legibility or overlapping labels.

## Metering and stopping rule

`metered_run.py` supplies the exact interpreter, lane cwd, start/endUTC,
stdout/stderr paths, package/runtime versions, source/input hashes and
child wall/CPU. It sets one BLAS/OpenMP thread and a writable MPLCONFIGDIR.
Each child is bounded by remaining implementation allocation and the frozen
30wall/20CPU maximum; total implementation allocation is60wall/40CPU.
Existing receipts are added rather than reset. Historical remaining budget
staysnull and previous subtotals remain separate. The root controller accounts
for its separately measured Wolfram time in the overall120wall/60CPU guard.

The existing three commands are the authorized finite next step. A nonzero
test/sweep/summary or scientific gate returns actual evidence to root for its
specific interpretation and any bounded repair. This preexecution PASS is not
a claim that those commands have run, that their gates passed, or that the
full BASS physical goal is complete.
