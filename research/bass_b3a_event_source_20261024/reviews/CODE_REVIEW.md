# Independent PHYS-MATH-CODE review — BASS B3a

Reviewer: /root/source_owner_intake. Date: 2026-10-24.
Reviewed local lane: research/bass_b3a_event_source_20261024/.
Implementation was supplied by a separately delegated implementation agent; this
reviewer did not edit implementation, tests or reference outputs.

## Initial decision

**CHANGES_REQUIRED: two concrete interface-contract findings.**
The event-moment mathematics, eight-sign REC packet construction, source-owner
selection, BASS c factors and state-stress/rate separation are consistent with
the frozen scoped model. The current public adapter nevertheless admits a wrong
REC origin frame/clock, and a coordinate-frame change bypasses its duplicate
physical-transfer guard. Repair these two interface findings before source push.

This decision is limited to the source-only adapter. No cosmological evolution,
stock transaction, closed photon reservoir, native LINE02/history parity or
continuum angular-convergence admission is requested or inferred.

## Read and checked evidence

Read CONTRACT.md, SOURCE_INDEX.json; all five current code modules; the complete
test_adapter.py; actual 01_tests.log and VALIDATION_RECEIPT.json;
CURRENT_REFERENCE.json; the separate independent THEORY_REVIEW.md; relevant
REC donor code/theory and actual BASS Source.arrays implementation.

All six vendored payloads in SOURCE_INDEX.json were independently SHA256 and Git
blob checked during this review. Six matched. The source COPY's prior newline
repair remains recorded; no donor physics was changed.

The primary executor receipt records 12 unittest methods with exit0, 0.729535135 s
wall / 0.728739 s CPU. The independent reference/plot subprocess records exit0,
2.056607132 s wall / 2.052599 s CPU. These are inspected original current-unit
executions, not reruns by this reviewer. They do not include the new negative
cases below.

The current numerical report has native-scalar detached reference energy/PiRate
gross-scaled discrepancies 1.9453006649083304e-16 / 4.070403924557633e-16.
Its original angular S is explicitly constructed. Same-quadrature donor parity
is correctly scoped and is not continuum convergence.

## F1 — REC origin frame/clock can be falsely labelled

**Severity:** material correctness of the typed source contract. **Status:** OPEN.

**Target:** rec_adapter.event_bundle(state, identity); event_measure.Identity;
bass_binding.attach_source.

**Observed source:** event_bundle checks the identity type and owner string only.
It generates unboosted matter-rest directional packets with physical rates in
proper seconds, regardless of the supplied identity.frame and identity.clock.
Identity merely requires nonempty strings. attach_source checks equality with
caller-supplied expected_identity, so two matching wrong labels pass together.

**Actual targeted reproduction:** at one new manufactured positive emission state,
both of these passed event_bundle and attach_source:
- identity.clock="ln_a";
- identity.frame="already_boosted".

Both produced nonzero BASS transfer U=[7.009139642176173e-17,
-7.009139642176173e-17] with the incorrect metadata. No H conversion or boost
had occurred. This is an input-admission error, not an error in the event
integral itself.

**Impact:** a caller can treat proper-second rest-frame rates as ln(a) or
already-transformed source values while the API claims clock/frame identity
protection. Matching two arbitrary strings does not enforce the donor's
physical contract.

**Minimal repair:** specify canonical REC origin frame and invariant proper
time-volume clock constants and enforce them when constructing event_bundle.
A generic post-construction boost may set its explicit destination-frame ID;
the source creator must not accept that target ID as its original frame.
Retain expected_identity comparison for stale/other-target attachment checks.
Add negative cases for both wrong origin labels and preserve the current raw
failure observations.

## F2 — representation frame is included in the physical transfer token

**Severity:** material duplicate-source guard defect. **Status:** OPEN.

**Target:** bass_binding.attach_source key construction.

**Observed source:** the applied-transfer key includes owner, epoch, frame,
clock and transfer_id. The Lorentz representation of the same physical event
therefore has a different key after changing frame.

**Actual targeted reproduction:** attach one source with
owner=REC_LINE01, epoch=reviewer_epoch, transfer_id=physical_event_1. Boost that
same GrossEventBundle to other_observer and call attach_source with the first
applied_transfer_keys. The second call passed and the returned ledger had two
keys for the one physical token.

**Impact:** the claim that an exchange is charged once is representation
dependent. This matters even though this unit does not itself advance stock:
it is the ledger token intended for downstream use.

**Minimal repair:** separate physical transfer identity from representation
identity. For this scoped API, a physical token such as (owner,epoch,transfer_id)
must be invariant under frame/clock relabelling; retain frame/clock agreement
as its own compatibility check. If a caller intentionally creates another
independent ledger, it can start a new empty applied-key set. Add a negative
cross-frame duplicate test using the existing applied-key set.

## Targeted execution and provenance

Only the two diagnosed risks were probed. The three observations correspond to
F1 wrong clock, F1 wrong frame and F2 cross-frame duplication. No full suite was
replayed. The script uses a small 2x2 principal angular rule with eight signs,
a manufactured emission state and synthetic callback True; this does not admit
real finite-stock positivity.

- Script: reviews/probe_code_review.py.
- Raw source hashes, argv/cwd, stdout/stderr, exit and resource measurements:
  reviews/CODE_REVIEW_PROBE_INITIAL.json.
- Command: current Python executable, reviews/probe_code_review.py.
- Working directory: /workspace/scratch/fe69646d3c76/bass_source/research/bass_b3a_event_source_20261024.
- Process exit: 0, meaning diagnostic observations were collected successfully.
  **All three expected rejection contracts failed** on the initial code.
- Measured wall: 0.7490066320024198 s; CPU: 0.7477369999999999 s.
- New IVP=0, old campaign replay=0, full-suite replay=0.
- Historical remaining budget=null and budget_reset=false are unchanged.
  The new review cost is additive to this unit's measured record.

## Checks that support the scoped mathematical implementation

1. PhotonEventMeasure retains nonnegative gross rates on boosts and transforms
   only r=c p. The current code does not call kinetic density-weight boosting.
2. moments computes cQ=sum(rate*r) and K=sum(rate*r*r/(-u.r)).
   It returns a three-dimensional PiRate only in the explicit rest observer
   chart. A generic observer receives K(u), avoiding an incorrect raw spatial
   projection. The fixed-u covariance test is correctly distinct from changing
   the observer denominator.
3. REC construction uses all eight signs of sqrt(n2), eigenvector rotation,
   weight/8 and the unchanged beta_vector. No angular renormalization is used.
   The two gross channels remain nonnegative and are subtracted after moments.
4. Native scalar extraction restores the documented excited population and
   Planck blue boundary, while retaining the full-Planck/stimulated detached
   scope and constructed S. It does not claim native LINE02 parity.
5. With cQ^i=c*force_density, multiplying the four cQ components by
   kappa L^3/c yields U=kappa L^3 E_dot/c and
   J=kappa L^3 force_density. PiRate_hat uses the same rate factor.
   Equal/opposite sectors are the inspected atomic excitation/photon partner;
   no matter pressure-rate is invented.
6. attach_source copies explicit current pressure/pi unchanged into the actual
   BASS Source class. PiRate_hat remains a separate return. BASS
   Source.arrays(2,balanced=True) independently validates tensor state and
   balanced transfer components.
7. A nonzero binding without a callable successful positive-domain check is
   refused; no populations/rates are clipped. The existing successful callback
   test is explicitly synthetic and does not establish a physical donor stock.

## Figure inspection

The actual current PNG results/AB_EXACT_BOOST.png was visually inspected. Axis
A/B curves and their separate difference are labelled, the oblique point is
distinguished at |beta|=.6, the negative oblique xx difference is visible, and
the residual panel is linear with zero retained. The scalar closed form is
correctly restricted to an axis boost. No figure rerender was performed.

## Re-review plan

The implementation owner should make the minimal F1/F2 repairs and add their
affected negative tests, preserving initial raw results. This reviewer will
read the changed lines and rerun only probe_code_review.py against the repaired
code. The reference mathematical output and plot do not depend on the repaired
admission/key logic and need not be regenerated. Final status and repaired
source hashes will be appended below when the re-review is actually complete.


## Final re-review — findings closed

**Final decision: PASS_SCOPED for the current source-only adapter.**
F1 and F2 are CLOSED on the exact post-repair source identities below. No
remaining material finding was identified within the frozen B3a scope. This
review is complete; further audit or historical scientific replay is not
required for publication of this scoped result.

The reviewer read the actual minimal repairs, REPAIR_ADDENDUM.md and the new
three-method test_repairs.py. The unchanged initial probe was rerun once on
the repaired source, with original initial evidence left intact. All three
observed cases now raised the appropriate ValueError:

| Case | Initial observation | Post-repair observation |
|---|---|---|
| F1 wrong clock ln_a | Accepted wrong metadata | Refused canonical-origin clock mismatch |
| F1 origin frame already_boosted | Accepted wrong metadata | Refused canonical-origin frame mismatch |
| F2 same physical token in another frame | Accepted a duplicate charge | Refused duplicate transfer |

The source factory now enforces ORIGIN_FRAME=rest and
INVARIANT_CLOCK=proper_time_dt_dV_invariant. The BASS conversion also validates
the canonical invariant clock. Explicit actual boosts retain their destination
frame and unchanged invariant event-clock convention. Physical transfer keys
are now (owner,epoch,transfer_id), while full expected-identity equality remains
a separate attachment compatibility requirement.

### Exact repaired source and new execution

- code/rec_adapter.py SHA256: c04618b6156d355a2b043d5570a1937edbc807ea3f1d600c8512a8eda5e50546.
- code/bass_binding.py SHA256: 5644d526e8c8eb10e8209a109cded2764aed7df0b042482f81f2a632f32e8626.
- code/event_measure.py SHA256: 8d2f4e4644c18b100663d611f78ceb1781520ee0f31b2e06b8195ad806ee6bb6;
  unchanged from the initial review.
- reviews/probe_code_review.py SHA256: b69ced43b1a658f6861bbcc6e08ac22bee3feab0bb9e9bc1d67e88551f6e424c;
  unchanged from the initial execution.
- Final receipt: reviews/CODE_REVIEW_PROBE_FINAL.json, with exact argv/cwd,
  source hashes, stdout/stderr and process resource record.
- Final targeted probe exit0; all three rejection expectations satisfied.
- New measured re-review wall=0.486750309006311 s, CPU=0.48627299999999996 s.
- Initial + final independent reviewer probes total wall=1.2357569410087308 s,
  CPU=1.2340099999999998 s. These are additive current-unit costs, not an
  inferred remaining old campaign budget.

The review additionally read the actual lower-tier RED/GREEN/final logs:
results/03_repair_targeted.log preserves 3 test methods with 6 failed
subcases/assertions on the old guards; results/04_repair_targeted.log records
3/3 PASS after repair; results/05_tests.log records final 15/15 PASS. The
initial 12/12 test log remains historical and did not cover the two missing
guards. The exact-zero source fixture invokes the actual donor and establishes
zero gross channels, moments, U/J and unchanged supplied pi without requiring a
callback for a zero transfer. It does not certify a finite nonzero stock.

This reviewer did not repeat the complete suite, reference generation or plot.
The corrected code affects input admission and the physical-charge key, not the
mathematical kernel or numerical reference outputs. The original independently
inspected figure and moment evidence are therefore reused. New IVP=0;
old campaign replay=0; reviewer full-suite replay=0. Remaining historical
wall/CPU budgets remain null, budget_reset=false.

Publication/backup ACK is a separate controller action. This scientific/code
review does not assert that a push, backup, merge or activation has occurred.
Native/history coupling, real finite-stock advancement, continuum angular
convergence, B1's historical pytest argv/cwd gap, B2's preserved acceptance
limits and production admission remain at their existing gates.
