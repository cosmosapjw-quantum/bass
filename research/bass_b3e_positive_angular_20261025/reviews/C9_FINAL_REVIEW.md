# C9 final independent scientific and figure review

**Verdict: PASS_SCOPED. Material open findings: 0.**

Unit: BASS_B3E_POSITIVE_ANGULAR_CONTROL_20261025. Workflow1.0.0.
This final verdict closes the actual numerical and figure review after the
single authorized presentation repair. R6, preexecution C9, the original
figure findings and the failed presentation artifacts remain preserved.
Different-model scientific review is NOT_RUN.

## Review independence and scope

The reviewer independently derived the source-aware bound and reviewed the
root-authored contract before inspecting lower-tier code. The reviewer did not
implement or edit the algorithm/renderer and did not run a scientific solver,
quadrature, symbolic evaluator, test suite, plot command or IVP. Read-only
source/JSON/CSV/hash inspection and arithmetic reconciliation of already saved
tensor entries were performed. This does not add another scientific campaign
or count as a rerun of the implementation.

Final input identities, including all5 actually viewed PNGs, are recorded in
`C9_FINAL_INPUT_IDENTITIES.json`. The code, raw data, independent mathematical
derivation, Wolfram evidence, custom test results and actual execution receipts
jointly support the admitted scope: source-aware sufficient positive angular
quadrature for supplied mapped cohorts, tested on19main endpoints,
2orientation comparisons and1positive mixture. The exact bound is an
ideal-node statement; actual binary64 checks have their explicitly separate
floating/reference allowance.

## Actual numerical results reconciled

The raw sweep has22rows:14inherited-reference endpoints,5new manufactured
endpoints,2canonical orientation checks and1positive four-cohort mixture.
All162row gates are true. ALL_ROWS.csv has22rows and SELECTOR_COST.csv
has617candidate rows; labels, metrics and counts reconcile with raw JSON.
Direct Frobenius arithmetic on saved tensor differences matches the recorded
norms. No dropped row, hidden cap failure or altered tolerance was observed.

| Check | Actual maximum/result | Contract |
|---|---:|---:|
| Full tensor Frobenius relative error | 2.907450008788106e-12 | <=2e-8 |
| Full tensor component relative error | 2.2749899941573606e-12 | <=2e-8 |
| Selected source-aware bound/F_lower | 9.210494258280034e-9 | <=1e-8 |
| New64/96 reference difference | 4.527945333448024e-15 | <=2e-12 |
| N64 ideal reference bound | 4.736202670726976e-15 | <=2e-12 |
| N96 ideal reference bound | 3.063265208217133e-22 | <=2e-12 |
| Minimum signed Loewner residual | -1.0393020115642785e-14 | >=-2e-12 |
| Co-rotated tensor residual | 1.4343390365909523e-15 | <=512eps |
| Bound/frame invariance residual | 1.6738707359255868e-16 | <=512eps |
| Mixture Frobenius error | 2.015084035559054e-15 | <=2e-8 |
| Mixture actual packet residual | 4.810206962113011e-15 | <=512eps |
| Mixture number residual | 7.771561172376096e-16 | <=512eps |

The negative signed Loewner residual occurs in the zero ideal-bound isotropic
limit and is within the separately declared floating/reference allowance.
It was not clipped into a positive value or relabelled an exact interval
enclosure. The minimum-K checks preserve all preceding failing sufficient
bounds. The selected general fixtures are not tuned afterward to their small
measured errors.

The19main endpoint ray sums are13440source-aware versus15842for the stated
conservative baseline, with8strict savings and11ties. This is a point-count
comparison under the same sufficient-error target and rule family; it does
not prove a wall-time speedup or globally optimal quadrature.

The mixture contains9722actual packets. Its number density is
1.1002499999999993m^-3 and its ideal absolute tensor bound is
7.909332736827402e-27J/m³, with F_lower=1.2387526673290285e-18J/m³.
Its Loewner enclosure usesΣc_a beta_a M_a. Signed tensor entries and
positive physical coefficients were retained.

All28original Q14/Q26 error records are preserved byte-equivalent as parsed
values, including22failures at2e-8. The14stored fine-reference tensors were
rescaled by the analytically correct exp(−.4) factor; no old angular/time
campaign was rerun.

## Focused test and scientific controls

The actual custom test script reports7check groups,165sphere monomials through
degree8 and16invalid-input cases. It is one script, not165pytest methods.
The source angular zeros are exactzero in the direct±x check. The isotropic
G5 K0/18-ray oracle residual is1.5860328923216522e-16. The G1 maxK0 cap
returns BoundNotMet with its failing history. Nonfinite, complex, malformed,
asymmetric/non-STF/negative-source inputs and out-of-domain R, negative
density, negative mixture coefficients and undefined zero-total mixture
relative error are rejected as contracted.

The test stderr contains one RuntimeWarning from constructing the intended
nonfinite I*np.inf input. That rejection test passes and the child exits0.
The warning is retained in its original stderr; it is not a numerical gate
failure or an unexplained rerun.

The mathematical pressure enclosure, Frobenius contraction and secant energy
bound were reviewed in R6. The actual code implements them without a
commuting-matrix assumption. Wolfram reports16exact zero residual groups as
independent finite cross-checks. The continuous proof and the finite symbolic
checks remain distinct evidence.

## Figure findings and actual closure

The reviewer actually viewed the original2080×1920PNG and identified:

- **C9-V1:** upper legend obscured the G5 exactzero ideal-bound marker.
- **C9-V2:**330.2mm-native canvas made9pt/8pt text too small when scaled to
  the requested180mm/90mm reading contexts.

Root authorized one presentation-only repair. The original source, original
PNG and original finding are preserved in results/figure_label_repair/.
The reviewer then read the exact renderer diff and actually viewed all5new
PNGs. The following observations close both findings:

- Legends now sit outside data axes; all3zero-bound markers in the overview,
  including G5, are fully visible.
- The overview is native180×260mm at300dpi,2125×3070pixels.
- Four separate90mm layouts cover inherited errors, general/orientation/
  mixture errors, horizontal point counts and invariant residuals. They are
  not reductions of the dense overview.
- Actual renderer metadata gives a minimum visible font size7pt. Compact
  A/I labels carry exact eta fractions, with a visible key; G/r/M labels are
  also defined. Axes, norm/energy denominator,2e-8 target,512eps allowance
  and exactzero display-floor meaning remain consistent with the data.
- No observed clipping, overlapping labels, covered datum or changed
  scientific meaning remains in the actual images. Native sizes and the
  separate90mm presentation satisfy the scoped readability obligation.

Final overview SHA256:
`cf7c6bbfebf42f83d53990c9f5fcf6251db2313efa5da32b73f24d92a7451331`.

The four90mm hashes are bound in the final input receipt and
AFTER_VERIFICATION.json. The latter's PENDING independent-review marker is
its preserved pre-review snapshot; this final C9 records the actual completed
independent image review.

Five numerical outputs remain byte-identical across the figure repair:
POSITIVE_ANGULAR_SWEEP.json,TEST_RESULTS.json,NUMERICAL_SUMMARY.json,
ALL_ROWS.csv and SELECTOR_COST.csv. The reviewer compared the before/after
receipts and recomputed their current byte hashes. All5new figure hashes and
sizes also match their actual files. No test or sweep rerun was performed.

## Actual commands, resources and recovery boundary

Four metered children actually completed with exit0: focused test, sweep,
initial summary and the authorized presentation-only summary rerun. The first
three used the preexecution-reviewed code. The fourth changes only the
renderer; scientific source, source copies, fixture/reference data, contract
and gate code remain unchanged. The actual fourth child took
1.7538231660000747wall/1.753029CPU seconds. The four-child total is
5.316162086004624wall/5.312123CPU seconds. Root's separately measured
Wolfram evaluation is accounted in the outer resource ledger.

All15preexecution input identities matched after the reported workspace
recovery and before the authorized renderer change. Every first-three-run
code/input hash matched current bytes at that review. This establishes the
unchanged scientific inputs used by the new runs. It does not recover or
certify the original lost48private intake files, original archive bytes or
provider ACKs. Those loss/recovery facts belong to the separate root receipt.
Remote whole-archive restore remains NOT_RUN.

Historical remaining budget remainsnull, budget_reset=false. Prior B3d and
other historical subtotals are separate. No new IVP, old campaign replay,
native source transaction or production change was performed here.

## Report and current-source consistency

REPORT_KO.md and the targeted current refresh were read for material claim
consistency. The latest observed central SHA a28ba343bb85addf1a7e9e58e75816ed3b75cd3b
changes CR delivery/ACK metadata; its unchanged AGENTS/BASS handoff identities
and stable PR188/REC135 pins do not invalidate this frozen scientific input.
Other-owner scoped results are labelled owner-reported. No material
inconsistency in the report's equations, counts, errors, physical scope or
current-source interpretation was found. The report's provisional figure
wording may now be updated to this final verdict and actual fourth-command
resources without a repeated scientific review.

The admitted result closes this bounded angular-control unit. Actual B3c
cohort history binding, native finite receiver trace/absorption, calibrated
REC/geometry coupling and B4/B5 remain separate open obligations. Whole BASS
physical completion isnull. No strong-no-go or broad novelty claim is
admitted. No further optional test, plot revision or broad review is needed
for the present scoped result.
