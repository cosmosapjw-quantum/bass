# Independent physics and figure review — BASS B3a REC adapter

Reviewer: `/root/b3a_theory_review`, 2026-10-24. Scope: read-only audit of the new detached REC LINE01 event adapter and one current diagnostic figure. This review did not execute the scientific source, tests, quadratures, IVPs, historical campaign, or figure generator. It reused the earlier independent 23 exact rational checks and read the implementation's actual logs/receipts.

## Initial decision

- Event-measure mathematics and dimensional BASS mapping: **PASS_SCOPED**.
- The displayed A/B figure and stored residuals: **PASS_SCOPED**.
- Selected REC factory's frame/clock validation: **FIX_REQUIRED**, finding PHY-01 below.
- Exact zero-transfer attachment acceptance: **PENDING_TARGETED_CHECK**, finding PHY-02 below.

The preceding decisions apply to the initial inspected source bytes. A targeted closure addendum must identify changed files and actual new evidence before the two open findings are closed.

## Read scope and identities

Inspected: `CONTRACT.md`, `code/event_measure.py`, `code/rec_adapter.py`, `code/bass_binding.py`, `code/reference_runner.py`, `tests/test_adapter.py`, `results/CURRENT_REFERENCE.json`, `results/VALIDATION_RECEIPT.json`, stored CSV rows, actual `results/AB_EXACT_BOOST.png`, `reviews/SOURCE_OWNER_REVIEW.md`, and relevant unchanged REC/BASS source functions.

Initial source/output SHA256 values:

| File | SHA256 |
|---|---|
| `code/event_measure.py` | `8d2f4e4644c18b100663d611f78ceb1781520ee0f31b2e06b8195ad806ee6bb6` |
| `code/rec_adapter.py` | `d50ef5db1dddcc953dbab1199ea6b23d92dbe0838dbfacdaa2b59a5e6bcfbf34` |
| `code/bass_binding.py` | `6d38301ed628b990920349faa2234288c3dc1b6b3492ffa201f74f9bc81e1881` |
| `code/reference_runner.py` | `43b2bf23f5b1b7c3e5ffaf2cea7ab2969ef4cc3deecd941d65b8b6f0ead1da47` |
| `tests/test_adapter.py` | `551eccc284165e5db6c38ebaad1e1a3612757dd614cb07693c022c20f4d5ddda` |
| `results/CURRENT_REFERENCE.json` | `8d78ef4c310c913a87ce52542cb96b5cf2fed08abd1af7a84eeb8f2518362f22` |
| `results/AB_EXACT_BOOST.csv` | `dc3aaa9302d1ab5a806600ac9b9672a70445210cf946c77a36a47ea85b7f3f0c` |
| `results/AB_EXACT_BOOST.png` | `c4d9ac4d510c1fbcf052dc4aaf96e60872787035b4878ea178866a936829ba1a` |
| `results/VALIDATION_RECEIPT.json` | `29797c78850a67547cab74b6254fb2610fc7475bab877a9326588fe447aa7490` |

## Accepted physics and source correspondence

1. `r=c p=(E,E n)` with unchanged volumetric event rates gives `cQ=sum(rate*r)` and `K=sum(rate*r*r/(-u.r))`. This agrees with the independent derivation using `dR` per `dV4/c` and `u.u=-1`. Boosting changes momenta and the observer denominator; it does not multiply event weights by a density Doppler factor.
2. Generic-observer `K(u)` is returned covariantly. A three-dimensional `PiRate` is returned only for `u=(1,0,0,0)`; the code avoids misidentifying a generic coordinate spatial subblock with the observer's physical PSTF tensor. The stored non-axis covariance test explicitly distinguishes fixed-observer tensor transformation from changing the observer.
3. A/B expectations match the prior exact independent derivation, including the oblique rational counterexample. The exact-axis shortcut is scalar and explicitly x-directed. The angular counterexample does not alter G1B's fixed-angular collisionless radial homogeneity argument.
4. The REC factory reads the selected detached LINE01 state, reconstructs all eight signs of the square-root principal directions, rotates by the actual eigenvectors, and divides the inherited octant weight by eight. Each channel retains its nonnegative angular event law. The gross rate scale and absence of forced normalization are visible in code.
5. Down and up represent the model's effective escaping-reservoir channels after elimination of resonance radiation. The unchanged upstream `exchange_source` uses the corresponding net population defect. Signed absorption is preserved by subtraction; no positivity clipping is used.
6. The actual native scalar extract is passed through the existing detached full-Planck/stimulated source with an explicitly constructed rotated shear fixture. The output is correctly labelled as neither native LINE02 parity nor a history execution. The source's internal atomic excitation ledger is the identified energy counterpart. Thermal, ionization and free-electron yields remain zero at this recoil-free narrow-line scope.
7. `factor=kappa L^3/c` multiplying `cQ` produces the correct BASS `U` and `J`; multiplying physical pressure rate produces `PiRate_hat`. The pure attachment copies explicitly provided current `pressure` and `pi`. It does not add a pressure rate to `Source.pi`, call the Einstein RHS, advance a population, or inject kinetic packets.
8. The two sector arrays use a value and its exact unary negation. Their source balance is distinct from finite-population/finite-photon-stock admissibility, which the synthetic callback does not certify.

## Numerical evidence read, without scientific rerun

The initial implementation receipt records 12 unittest items passing, exit 0, and one reference/plot execution with exit 0. Combined measured wall time is 2.786142267010291 s and CPU 2.781338 s. These counts belong to the new adapter, separate from the earlier 23 exact review assertions and all historical Wolfram/Thomson tests.

The stored donor comparison uses the **same finite quadrature** on both paths. Its normalization is gross emitted-plus-absorbed power, which remains meaningful close to cancellation:

- Native-scalar energy discrepancy / gross: `1.9453006649083304e-16`.
- Native-scalar PiRate discrepancy / gross: `4.070403924557633e-16`.
- Constructed emission discrepancy / gross: `1.2070126599814901e-15`.
- Constructed absorption discrepancy / gross: `2.6822503555144215e-16`.
- Constructed LTE net / gross: `2.19456847269362e-16`, with raw net energy `2.7755575615628914e-17 J m^-3 s^-1`.

The LTE result is floating cancellation near equilibrium, not an exact-zero result. Tiny nonsymmetric entries in the stored net K/PiRate arise from separately accumulated gross components and are well below the declared gross-normalized gate. They are not a licence to feed this rate into the state-stress validator.

The saved 96-row A/B CSV has maximum signed numeric-minus-exact absolute residual `4.440892098500626e-16`, consistent with `CURRENT_REFERENCE.json`. This read-only comparison inspected saved numbers; it did not rerun moment evaluations. Same-grid agreement establishes implementation correspondence, not continuum angular convergence, source-model accuracy, native history agreement, or a new nonlinear coupled result.

## Actual visual inspection

The reviewer loaded `AB_EXACT_BOOST.png` with `view_image` and inspected its rendered content.

- The upper panel distinguishes A, B and their difference by labelled colors. Sparse numerical markers coincide with the analytic curves at the plotted resolution.
- The oblique fixture is a separate purple diamond at `|beta|=0.6` with the actual vector `(0.2,0.4,0.4)` written in the legend. The x-axis explicitly distinguishes axis beta from the magnitude used only for that point. Its negative value is visible below the zero line.
- The physical A/B difference remains nonzero while numerical residuals stay near machine roundoff. The panels therefore distinguish physical angular dependence from implementation discrepancy.
- The lower panel has a signed **linear** residual axis with scientific-notation scaling. It includes zero and the full stored residual range; no zero-to-log substitution or residual clipping is used.
- The y normalization corresponds to rest power `P=unit energy * event rate`. The title and caption identify finite event measures and a current detached adapter diagnostic. Labels, legend, caption and tick text are legible and not visibly clipped.

No figure repair is required for the inspected image. This is one new diagnostic, not a rerender or reinterpretation of previous G1B figures.

## Findings requiring targeted closure

### PHY-01 — REC factory permits incorrect initial clock/frame labels

**Target:** initial `rec_adapter.event_bundle` checks only `identity.owner` before assigning the supplied identity to the owner-rest directions and proper-time rates.

**Evidence:** `Identity` requires nonempty strings but admits any `frame`/`clock`; `event_bundle` does not compare those fields with the selected REC source convention. A caller can therefore label unchanged owner-rest rates as `clock='conformal_time'` or `frame='already_boosted'`. `attach_source` only compares the completed bundle with the supplied expected identity, so matching wrong labels are not refused.

**Impact:** source values and their semantic frame/clock can disagree without a conversion. This defeats the requested provider admission boundary.

**Minimal repair:** selected REC event construction must require the canonical source frame (`rest`, or a single documented owner-frame enum) and `proper_time_dt_dV_invariant`; use the explicit `.boosted(...)` operation for a changed frame. Add negative checks for incorrect initial frame and clock. Generic externally specified event measures can retain the broader identity API. Do not rerun unchanged figures or old campaigns.

### PHY-02 — exact zero-transfer attachment has no current execution check

**Target:** central B3a zero-exchange acceptance and the initial twelve tests.

**Evidence:** rest A/B tests exercise nonzero emission; LTE tests compare the rounded net to zero under a gross-normalized tolerance. No initial test exercises exact all-zero channels and successful attachment without a positive-domain callback.

**Impact:** an exact zero-transfer claim would exceed the saved test evidence. It is distinguishable from the correctly reported LTE cancellation result.

**Minimal repair:** construct a valid detached donor state with `n_u=0`, `f_plus=0`, positive lower density/expansion and valid S. Verify exactly zero gross rates, Q, K, PiRate, U and J, unchanged supplied state stresses, and attachment without a callback. This is a small new boundary check, not a historical replay. Alternatively retain the original zero-transfer acceptance as pending and restrict the claimed completion accordingly.

## History and admission boundaries

The prior preparatory Wolfram first-pass 7/16 failure, repaired 16/16 plus separate 4/4, and prior Thomson 20/21 outcome remain separate historical evidence. None is silently replaced by the new test count. The 23 exact assertions are reused from this reviewer's earlier independent run; they are not reexecuted here.

No native source execution, IVP, campaign replay, finite-stock transaction, continuous angular convergence study, production activation or merge was performed by this review. B1's old pytest command/cwd gap and unknown historical remaining budget remain untouched. Literature/novelty admission is not expanded by this code and figure review.

## Post-repair closure addendum — final disposition

**Final physics-and-figure decision: PASS_SCOPED. PHY-01 and PHY-02 are CLOSED.**

The reviewer read the changed `rec_adapter.py`, `bass_binding.py`, new
`tests/test_repairs.py`, `REPAIR_ADDENDUM.md`, appended validation receipt and
actual raw logs `03_repair_targeted.log`, `04_repair_targeted.log` and
`05_tests.log`. No scientific computation or figure rerender was performed by
the reviewer for closure.

Post-repair SHA256 identities:

| File | SHA256 |
|---|---|
| `code/rec_adapter.py` | `c04618b6156d355a2b043d5570a1937edbc807ea3f1d600c8512a8eda5e50546` |
| `code/bass_binding.py` | `5644d526e8c8eb10e8209a109cded2764aed7df0b042482f81f2a632f32e8626` |
| `tests/test_repairs.py` | `f63ca40cd793f9b18bf977277de8dca4edf4e01f4cce357fcd38ca01750ef1e7` |
| `results/VALIDATION_RECEIPT.json` | `21b107e6c22060db4e14c5f00d174b64d4a101f2763f84bcdcf9243b438dfb3d` |
| `REPAIR_ADDENDUM.md` | `1bbcad95c69c13cde949d08c543b3f03274f53b8b5a3914f3b400368bbef6388` |

**PHY-01 closure.** The selected REC factory now requires its canonical
`rest` source frame and `proper_time_dt_dV_invariant` clock before constructing
owner-rest event measures. The BASS rate mapping also independently requires
that clock. A subsequent explicit physical boost preserves the invariant clock
and can use a new target-frame label. The new regressions reject `ln_a`,
`conformal_time` and `already_boosted` at inappropriate entry points, while
admitting a properly boosted measure. The targeted run before repair actually
showed five failed F1 subtests; the same checks pass after the guard repair.
The source's physical frame/clock semantics therefore agree with the returned
values at this API boundary.

**PHY-02 closure.** The new test calls the actual unchanged detached donor with
`n_l=1e9 m^-3`, `n_u=0`, `f_plus=0`, `H=1e-13 s^-1`, `S=0`. It then calls the
event adapter and verifies exactly zero gross rates, cQ, K and PiRate. The BASS
attachment has exactly zero U, J and PiRate_hat, succeeds without a callback,
and preserves the supplied current pressure and pi. This case already passed
the pre-repair targeted invocation; the new evidence closes a missing test,
not a newly fixed mathematical defect. The earlier LTE floating cancellation
remains recorded as a separate result.

The concurrently reported duplicate-accounting defect F2 was also inspected:
the key is now `(owner, epoch, transfer_id)`, so a frame representation change
does not make the same physical source charge new. Full expected-identity
comparison remains in place. The actual targeted regression records the
initial failed cross-frame refusal and its passing result after correction.

The raw sequence is retained: initial 12/12 PASS with the coverage omissions;
targeted pre-repair 3 test methods with 6 failed assertions/subtests across F1
and F2 and exact-zero PASS; post-repair targeted 3/3 PASS; final affected suite
15/15 PASS. Exit codes are respectively 0, 1, 0 and 0. Counts are not added as
if repeated items were new distinct tests. Including the failing run, the
implementation harness records 5.127101682999637 s wall and
5.1194999999999995 s CPU, separately from other reviewer activity and all
historical budget fields.

Read-only SHA256 comparison against the initial table confirmed byte identity
for `event_measure.py`, `reference_runner.py`, `test_adapter.py`,
`CURRENT_REFERENCE.json`, `AB_EXACT_BOOST.csv` and `AB_EXACT_BOOST.png`.
The unchanged moment/boost mathematics, source-reference numerical outputs,
CSV and actual visually inspected figure therefore retain their prior scoped
acceptance. No repeat of those calculations or visual generation is required.

All findings raised by this finite physics-and-figure review are closed for
the detached instantaneous adapter. Native history, finite stock advancement,
continuum angular accuracy, B1/B2 historical acceptance obligations and
production remain under their already stated separate gates. There is no
remaining code or figure change requested by this reviewer for the present
scope.
