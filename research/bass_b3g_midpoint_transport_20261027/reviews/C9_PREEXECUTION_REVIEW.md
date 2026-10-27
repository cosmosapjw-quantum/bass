# C9 preexecution review — midpoint transport consumer

Reviewer: independent B3g source/theory agent `/root/b3g_midpoint_intake`.
The reviewer did not implement these files and did not import them, execute
tests, evaluate new moments, call core.rhs, run an IVP, or replay an old campaign.
Source copies, hashes and text were inspected read-only.

## Initial decision

`TARGETED_REPAIR_BEFORE_FROZEN_EXECUTION` for the two findings below. The
scientific construction is ready for the prescribed saved-data execution once
these changes are made and their changed paths are checked. No optional
review expansion or additional campaign is requested. Existing 512-epsilon,
2e-12 and 2e-8 thresholds, the 20 CPU/60 wall allocation, source model and
physical admission ceiling stay fixed.

## Inspected identities

Base: `d7dcd731de1a0c59e5e65db5038c333f5abae0bd`.

| File | SHA256 at initial review |
|---|---|
| FROZEN_CONTRACT.md | 70c3bbf83875fb4d1ea59788480e32c051e33cd3636ac8ca5d0bc4699ac793d8 |
| code/reconstruct.py | c91e60d13b17245b06891ef8f25d1f78f849745316d0692c2c733ec1305e275f |
| code/consume.py | 198df29adf31e8e2b7a7a80f7e38392ed09c140853da75bbe6f33086b84501d9 |
| code/metered.py | defe11080533d9785ddabcbddf9744040f8829b5607d6cc0949912588833c2e7 |
| code/plot.py | 22a28aba3a6212128ec8786319ff3808bcc3fe1ddb078112e1b48aa7f468482b |
| tests/test_controls.py | 04f7f0c2b95c04d5f1661be49cfe57c4fec9bd52d241d06aa8014b5258388056 |

Also read IMPLEMENTATION.md and provenance/SELECTED_INPUTS.json; the unchanged
B3f endpoint/ball/mixture and positive-angular functions; the B3g transport,
geometry and binding imports; original B3c core, kinetic, source producer,
source validator and original driver serialization.

## C9-1: derivative normalization must survive STF cancellation

**Target:** `geometry_check` in code/reconstruct.py.

**Observed code:** each residual is divided by
`max(max(abs(expected_derivative)), finfo.tiny)`. The core serializes five STF
entries and reconstructs zz in `State.unpack`, whereas the explicit comparison
forms all three diagonal derivatives independently.

**Mechanism and effect:** if `-3*h*sigma + pi` nearly cancels, its small
expected output does not measure the arithmetic scale of either term. A
roundoff-size difference in the reconstructed zz entry can then produce an
order-one normalized residual. The same output-normalization policy is
ill-conditioned for an exactly or nearly vanishing odd derivative. This is a
potential false FAIL of the new comparison, not a new defect in the unchanged
core or a physical shear signal. No failed scientific execution is claimed.

**Minimal repair:** keep the frozen 512-epsilon threshold, but normalize by
documented positive equation-term scales. In the shear equation a suitable
scale is the maximum of `3*abs(h)*max(abs(sigma))`, the source shear scale,
and the positive radiation-energy scale; this retains the scale of isotropic
stress before trace cancellation. Energy derivatives should retain sector
scales, and odd equations should use their equation terms plus the appropriate
positive sector energy scale. Record the chosen scales and raw signed
residuals so the comparison is auditable. Do not change, project or clip the
physical tensor to make this comparison pass.

Strengthen the existing control with a nonzero ANISO midpoint/STF case and a
cancelling STF representation case. These can be algebraic controls in the
single planned test command; no extra RHS invocation or campaign is required.

## C9-2: interrupted child execution needs a durable start receipt

**Target:** code/metered.py.

**Observed code:** the execution ledger is written only after subprocess.run
returns. If the controller or workspace session is interrupted after child
start but before that write, no durable attempt marks the stage as started.

**Mechanism and effect:** a later invocation could see no prior attempt and
run the same scientific stage again, losing the additive budget and preserving
neither an unknown debit nor the interrupted attempt. This directly affects
the user's requested interruption/resume workflow.

**Minimal repair:** write one `STARTED` attempt record before spawning the
child, including the exact command/cwd, time, frozen new-code identity and
selected-input-manifest identity. Finalize that same attempt with return code,
measured cost and completion state after the child returns. An incomplete
attempt must retain null/unknown costs and require root adjudication before
automatic replay. A failed launch likewise keeps a recorded attempt. This is
one operational ledger, not a new audit layer. Preserve old budget values,
stage order, completed stages and all failures.

## Scientific paths inspected and accepted in their frozen scope

- The independent exact RK4 identity and four-stage box induction agree with
  the contract. Source duration is authoritative; endpoint subtraction is only
  a diagnostic. The fixed H=1.01, B=.2 box includes the frozen positive
  directional-expansion check h0-delta*Mh>.2.
- Top-level midpoint_S is used. Its source STF normalization is covered by
  the explicitly empirical arithmetic reserve, not described as restoration
  of original sigma/alpha/beta bytes.
- Beta3 is reconstructed in the original STF chart and receives the sum of
  beta1/beta2 radii. Analytic and empirical terms remain separate.
- The diagonal R and determinant use the correct signs and dilution. Positive
  birth counts are already time-integrated and are not multiplied by duration.
- Finite14 weights, degree-four birth moment and the even quadratic source
  are unchanged. The joint moment kernel has Lipschitz constant sqrt(2), so
  the finite14 perturbation expression has the stated joint energy/spatial
  tensor meaning. Odd residuals are retained separately.
- B3e selection and moments and B3f ball/mixture are reused. The historical
  `PHYSICAL_BALL` result is nested under `NUMERICAL_RECONSTRUCTION` semantics;
  a separate physical call leaves INPUT_ERROR_UNSPECIFIED and null radii.
- The continuum tensor is postprocessing on fixed geometry, distinct from
  the original finite14 self-consistent trajectory. No new IVP or finite
  absorption is claimed.
- Source kicks have already been applied. The geometry adapter receives
  separate matter and radiation T plus zero cQ, and returns zero U/J.
- Consumer rows and summary are saved before a final consistency failure is
  raised; the two figures read saved output only. The runner prescribes only
  one test, one consumer and one plot stage, subject to the start-receipt fix.

## Required transition

Root authorizes one bounded repair for these changed paths. The lower-tier
agent makes the repair without scientific execution. The independent reviewer
checks only the changed functions/controls and appends its result below.
`PASS_SCOPED_C9` then leads directly to the three already frozen metered
commands. Final raw and figure review decides scientific admission.

## Targeted repair rereview — PASS_SCOPED_C9 / GO_FOR_FROZEN_EXECUTION

Root authorized one repair batch for C9-1 and C9-2. The same independent
reviewer inspected only the changed normalization/geometry functions, runner,
two new controls, updated contract adjudication and execution-freeze record.
No scientific execution was performed by the reviewer.

- **C9-1 CLOSED.** geometry_check now records signed raw residuals, explicit
  positive equation-term scales and normalized residuals. The sigma scale
  includes the positive radiation energy before trace cancellation; the odd
  scale likewise has a positive radiation term. normalize_residual treats a
  zero equation scale as an exact-zero check. The threshold remains 512 eps.
  The reported signed sigma-derivative change uses the actual adapter pi,
  preserving the stable pairwise trace decomposition already admitted in B3g.
  The added ANISO-STF control is nonzero; the cancellation helper control
  verifies the new normalization and zero-scale refusal. All actual core RHS
  calls remain the two planned final consumer calls. Aggregate drho algebraic
  comparison uses the frozen maximum sector derivative scale; the independent
  photon-tensor consistency check retains its positive photon-energy scale.
- **C9-2 CLOSED.** the runner verifies the five frozen code/test files and
  selected inputs, records STARTED with command/cwd/time/identities and null
  cost before child launch, and refuses an incomplete/unknown-debit attempt.
  Completion updates that attempt with measured child and wrapper CPU cost.
  Prior failures, unknown historical remaining budgets, stage order and
  no-automatic-retry behavior remain. A launch exception leaves the recorded
  attempt incomplete instead of silently permitting replay.

Rereview identities:

| File | SHA256 |
|---|---|
| FROZEN_CONTRACT.md after root adjudication | d25b3b35d87bb9d7af336e8d4b0d842a56e98cf13611d6179ba46d08917bc524 |
| code/reconstruct.py | 39ab3ffac2fd12125d087de4d7f14369798f4e19f08bf7512e328a6121e84359 |
| code/metered.py | 56cbe9fac3833ec1defc3b517b5ca1df5e7f4b99593de1480208d1774ca967eb |
| tests/test_controls.py | c383ea98d30e93d5e5821d0e4a17fc6241bdf8e0bb233a36eb93f77cb2c0f488 |
| provenance/EXECUTION_FREEZE.json | fa3d3159c861befd60de2b2610eeffbe76d19baad04b0dd68ecd659f140856b2 |

code/consume.py and code/plot.py retain their initial review hashes. All five
code/test hashes match EXECUTION_FREEZE.json; its input-manifest hash matches
the actual SELECTED_INPUTS.json. Ten focused test items are now prepared.

**Blocking findings remaining: 0.** Root may proceed directly with the frozen
tests -> consume -> plot sequence under the unchanged cumulative limits.
This is static execution readiness; numerical outcomes and scientific
admission remain pending the actual run and independent raw/figure review.

