# C9 independent implementation and outcome review

Reviewer: `/root/native_qss_theory` (Astra theory/review role; did not write this implementation).
Review mode: read-only source inspection; no scientific code execution, numerical replay, or code edits.
Current phase: CLOSED after one root-authorized targeted correction and read-only inspection of the single fresh controls/result/plot execution. Independent decision: **PASS_SCOPED_NUMERICAL_RECONSTRUCTION_AND_PHOTON_RETURN**. Complete physical atomic transaction admission remains open; root owns final admission/publication.

## Pre-node observation

At `2026-10-27 10:57:41 UTC`, the new BASS branch
`research/bass-b3h-history-inverse-20261027` still pointed to base
`29dcf5ab94ae8b84bf8e3f31dddb31ce719929b1`. Central canonical HEAD was
`55202663275cd0607c968129b33de805d06f5d8b`; central AGENTS blob remained
`429a5a13ee75b1222bc50627f8d5973d01dd21c4`, whose actual policy text had been read.
Root and this reviewer were active. Source intake and delegated implementation
had returned completed work. The implementation reported zero scientific runs.
Original central DAG is 27/88, with no admission by this review.

Read in full: `FROZEN_CONTRACT.md`, `IMPLEMENTATION.md`,
`inputs/EXECUTION_FREEZE_READY_DRAFT.json`, `code/inverse.py`,
`code/reference.py`, `code/net.py`, `code/result.py`, `tests/controls.py`,
`code/metered.py`, `code/plot.py`, and the copied transport operator.
Relevant saved trace fields, validation-only snapshot entries, original source
formulas, and the prior incoming result were inspected.

## One targeted numerical correction

**C9-1 — virtual 2s conditioning estimate omits trace-difference amplification.**

`code/inverse.py` currently computes the virtual estimate as

`32*ulp(1)*cancellation*max(1,r/(tau*Fprime))`

and uses that value to set `virtual_well_conditioned_under_assumed_model`.
However the assumed model is 32 ulps of each actual trace `i,v,o`, not a
32-ulp relative perturbation of `r`. The code already computes the propagated
ratio uncertainty

`er=(eB+abs(r)*eD)/(abs(D)-eD)`.

When `D=o-i` is small relative to the trace values, `er/abs(r)` can substantially
exceed `32*ulp(1)`. The equilibrium source `feq=i+D/A(tau)` also depends directly
on the input trace uncertainties and on `A(tau)`. The current virtual estimate
does not propagate either dependence. Thus its Boolean can classify a virtual
reconstruction as well conditioned under a model it did not actually apply.
The independent observed virtual-vs-beta comparison is still useful; the
issue is the stated conditioning qualification, not a demonstrated wrong
population value. No numerical run was performed to infer such a value.

Suggested bounded repair: use the already computed `tau_interval`, trace
intervals, and coefficient intervals to propagate `A`, `feq`,
`Gamma*feq-Cp*yp`, and division by `Cs`, reporting the resulting virtual `ys`
interval and relative uncertainty under the same declared assumed model.
Alternatively replace the current formula with an explicitly heuristic
diagnostic and do not let it qualify the model-based acceptance test; the
first option directly fulfils the frozen conditioning requirement. Preserve
the distinction between an assumed arithmetic model and a rigorous
end-to-end or physical certificate. The existing single controls/result
invocations can verify this correction; no additional campaign is requested.

Initial disposition: root authorization of one targeted repair was requested,
with the virtual-state conditioning statement pending correction and observed
results. This did not invalidate the constructive endpoint inverse or prohibit
authorized bounded execution. The correction and final disposition are recorded
below; this historical finding is retained rather than erased.

## Two narrow completeness/wording observations

1. Root's selected target explicitly included reconstructed Ly-alpha optical
   depth at the two native knots. The current result returns virtual-bin `tau`
   but does not yet serialize `R_Lya=LYA_FACT*H/(nH_cm3*x1s)` and
   `tau_Lya=A_effective/R_Lya`. These are now derived from available source
   inputs, with no additional provider or native run. Add these diagnostic
   fields if they remain in the intended result; label the stored outgoing
   closure as the original optically thick update. Computing this finite
   diagnostic does not turn that stored update into a finite-tau solver.
2. `code/result.py` and one contract sentence say `x1s=1-xe`. The exact source
   statement is `x1s=1-xHII`. The known right snapshot has `xe=xHII`, so this
   is not a demonstrated numerical error on the selected state. Preserve the
   exact source definition in the result description; do not generalize that
   endpoint equality to all possible source states.

These are finite corrections in this same review pass, not new external
prerequisites or requests for broad retesting.

## Static findings supporting the implementation

- The primary inverse reads only `fin/favg/fout` and source coefficients. The
  right population, Gamma and optical depth remain validation-only. The
  control explicitly removes the holdout fields before inversion.
- The selected bins are non-diffusing. Gamma uses the actual alpha-scaling
  exponent 8 and the correct degeneracy factors. The native global-index
  redshift expression and original Hubble summation order are represented.
- The 70-digit reference is a separate implementation using coth, exact
  binary64 input ratios, independently expressed coefficients, and direct
  piecewise quadrature. It does not call the primary inverse or primitive.
- The original exponential branch is checked after inversion. No clipping,
  cross-bin averaging, or silent small-tau formula substitution is present.
- The x1s interval is explicitly labeled as an assumed 32-ulp numerical
  propagation model, not a rigorous source or physical accuracy certificate.
- The new net calculation constructs the signed departure difference first,
  splits at the retained incoming knot, and integrates with a stable
  piecewise-linear exponential primitive. Saved incoming primary values and
  high-precision strings are reused. The source-native knot arithmetic for
  endpoint recovery and the old exact-real affine tube representation are
  kept as different conventions.
- Transport applies the existing B3g operator to the new outgoing/net
  measure. In the scalar geometry the number and energy identities have the
  correct factors `exp(-3h)` and `exp(-4h)`.
- `cQ` has units J/(m^3 s); dividing it by c yields Q in J/m^4. The reported
  time average is explicitly weighted by the common-volume factor before
  division by proper elapsed time. It is not mislabeled as an endpoint
  local source. The spatial isotropic source is zero while the tensor has
  pressure U/3.
- The direct Ly-alpha atomic internal-energy increment has sign `-E21*D`.
  The complementary internal energy required for both excited-state storage
  changes is `E21*(D+DeltaN2s+DeltaN2p)`. It is explicitly marked as required
  bookkeeping with physical refill owner null, not observed channel energy.
- `D`, the endpoint upper storage defect `DeltaN2p`, and the required finite
  complement `D+DeltaN2p` are separate fields. The actual source non-Ly-alpha
  operands are not claimed to have been newly exported or integrated.
- No B3i invocation or completed physical atomic transaction is claimed.
  Physical radii remain null, and old campaign replay is explicitly false.
- The guard records fresh current-unit costs and preserves unknown historic
  budgets. Its controls/result/plot sequence is finite and has no automatic
  retry. Review did not run it or alter its freeze.

## Observed results and final disposition

### Latest observation and scope of this final read

At `2026-10-27 11:43:12 UTC`, the new BASS branch was
`fd3524e914d6bec70f30e2a5643134e956cbba0a`, central canonical HEAD was
`1a38f94fa50c763bb9df6ccc8ba569f287fe97d5`, and central AGENTS remained
`429a5a13ee75b1222bc50627f8d5973d01dd21c4`. Root, the implementation agent,
and this reviewer were active; source intake had completed. The newer central
HEAD is the baseline for subsequent additive publication. This review does not
replace it with either earlier central observation.

The reviewer read the amended `inverse.py` and `result.py`, the new diagnostic
normalization input, all 12 stored reconstructed-state diagnostics, all 82
acceptance entries, all 20 control entries, the complete new execution ledger,
and the plot receipt. The reviewer also opened and visually inspected the
actual `figures/NATIVE_HISTORY_INVERSION_NET.png`. No test, inverse, quadrature,
transport, or plot generation was re-executed by the reviewer.

### Correction closure

**C9-1 is resolved.** The implementation now propagates the actual trace
intervals and tau interval through `A`, `feq`, the separate numerator products,
their subtraction, and division by `Cs`. It reports intermediate intervals and
uses the resulting relative width for virtual-state qualification. Correlations
are deliberately discarded to obtain a conservative independent-interval
model. The 32-ulp premise and the computed coefficient premise remain stated
assumptions; this is not an end-to-end directed-rounded source-error proof or
a physical certificate. The observed virtual relative interval widths are at
most `2.1254655212141443e-13`, while all observed virtual-vs-beta discrepancies
meet the frozen `2e-10` criterion. This addresses the original omitted
trace-difference amplification without broadening the research scope.

Both narrow observations are also resolved. The result now includes `R_Lya`
and `tau_Lya` at the two primary knots. Its normalization input identifies the
preserved REC LINE01 literal `(6.2649e8+2*6.2648e8)/3` and explicitly states
that the original HyRec update itself has no separate A scalar and remains
optically thick. The output is a diagnostic, not an altered line closure or an
inverse input. The population description now correctly uses `1-xHII` and
limits the observed `xe=xHII` equality to the known snapshot.

### Recorded numerical outcomes

The following values are read from `results/INVERSION_NET_RESULT.json`, not
recomputed by this reviewer.

| Quantity | Native index 5126 | Native index 5127 |
|---|---:|---:|
| Primary virtual-bin tau | 1.1076102907893572 | 1.1076274318532282 |
| x1s | 0.8549423676545932 | 0.8550700033096545 |
| x2s | 6.568412727733193e-15 | 6.563187316112037e-15 |
| x2p | 1.9746733281751027e-14 | 1.97310609216277e-14 |
| Maximum cross-bin relative difference from primary | 6.441026214723226e-14 | 3.8562484596277084e-14 |
| R_Lya [s^-1] | 1.0832539936116934 | 1.0832181815556692 |
| Diagnostic tau_Lya | 578334662.9949324 | 578353783.1996193 |

The primary right x1s relative holdout residual is
`7.920240944016569e-15`; the largest of the six right x1s residuals is
`4.648272554029396e-14`. The largest primary/reference tau discrepancy is
`1.5190168930369314e-15`. Reported right Gamma, TR, nH, and H port
discrepancies are zero in binary64 comparison. The beta/gamma check and all
qualified virtual estimates pass separately, with no cross-bin averaging.

The primary assumed x1s intervals are
`[0.8549423676537193, 0.8549423676554655]` and
`[0.8550700033087796, 0.8550700033105251]`. These are numerical-model
diagnostics. Their width is distinct from both the primary/reference residual
and the still-null physical accuracy radii.

The new finite photon result is:

- `DeltaN0 = 23.46391833488862 m^-3` per reference volume.
- `DeltaU0 = 3.8342003535474504e-17 J/m^3` at the left pullback slice.
- Independent 70-digit net relative differences are
  `1.9834943391822266e-14` and `2.025285279780588e-14` on the net quantities'
  own scales, below the frozen `2e-11` limit.
- `Nout0 = 9140.55668717356 m^-3` and
  `Uout0 = 1.493643353446071e-14 J/m^3`, using saved incoming totals.
- `Nout1 = 9138.228883843674 m^-3` and
  `Uout1 = 1.4931361982830613e-14 J/m^3` after the reused B3g map.
- The stored number and energy scalar transport residuals are zero; the
  signed event-to-end energy identity residual is
  `1.9065577974856846e-33 J/m^3`.
- The common-volume time-averaged `cQ_rad^0` is
  `2.2444227347368295e-26 J/(m^3 s)`; spatial source components are zero.
  This remains separately named from the finite photon stress tensors.

The endpoint storage changes are
`DeltaN2s = -1.3076617928069534e-9 m^-3` and
`DeltaN2p = -3.922015722821008e-9 m^-3` per reference volume. The upper
required finite complement is `23.463918330966607 m^-3`, while the
balance-inferred QSS complement is `23.46391833488862 m^-3`; their difference
is the explicitly reported upper storage defect. The combined excited
internal-energy change is `-8.545367403111164e-27 J/m^3`. These values do not
identify a physical refill energy owner.

### Execution and figure observation

The execution ledger records exactly one controls child, one result child,
and one saved-result plot child, each with exit status 0 and the same freeze
SHA256 `ef4414567eff42fad97ec61298b7e359fced0323c6b82dd1a35250b07530a587`.
All **20 controls** and **82 numerical acceptance checks** pass. Cumulative
recorded child CPU time is `5.377854000000001 s`, wall time
`5.46034009399591 s`, and the observed peak child RSS is 66,076 KiB.
Historical remaining budgets remain null. These are observed new-unit costs,
not retrospectively inferred old costs.

The rendered figure is legible and agrees with the stored quantities: the
two endpoint virtual-bin optical depths nearly overlap, the cross-bin panel
uses a `1e-14` scale, the positive net trace decreases slightly across the
represented cell, and the storage bars are negative on a `1e-9 m^-3` scale.
Its title and storage panel explicitly retain null physical radii and the open
physical refill owner. No figure correction or regeneration is requested.

### Final independent decision

**PASS for the frozen numerical endpoint reconstruction, source-effective
population/opacity diagnostics, finite represented net/outgoing photon return,
and QSS storage-defect bookkeeping.** Root may use this scoped decision for
the corresponding source publication and DAG evidence update.

**No admission of a complete physical atomic transaction or new B3i RHS
consumption.** The actual non-Ly-alpha channel energy owner and between-knot
physical population/storage evolution remain separate scientific work. The
result correctly records physical refill owner null, complete physical atomic
transaction false, B3i calls 0, old campaign replay false, native solver calls
0, and all physical radii null. The original central count remains 27/88 at
this review; this numerical subunit does not manufacture an original-node
completion. The ANISO continuum–finite14 difference and its numerical budgets
remain outside this unit and unchanged.

This closes the same review pass after the single authorized targeted repair.
No further numerical execution, repair, or review layer is requested.
