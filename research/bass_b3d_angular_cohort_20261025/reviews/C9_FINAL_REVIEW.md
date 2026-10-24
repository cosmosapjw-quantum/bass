# Independent C9 review of actual B3d results

## Scientific recommendation and review boundary

**Final scientific and figure recommendation: PASS_SCOPED. Material open
findings0. The targeted visual finding C9-V1 is CLOSED.**
The actual bounded angular-cohort experiment supports its frozen claim: it
quantifies continuum angular error of the unchanged14-ray rule and a positive26
candidate, verifies the exact leading coefficients, and separates angular error
from prior time-splitting results. It does not assert that either finite rule
passes2e-8 for all selected anisotropic transports.

The reviewer did not implement or modify the code, run a test/sweep/oracle, or
replay any prior campaign. It independently derived the angular results before
execution, read the prepared implementation, then read actual raw outputs and
viewed the actual generated PNG. Different-model scientific review remains
**NOT_RUN**. Root controls final admission and external delivery; this review
does not attest to Git/Drive/Dropbox ACKs or full remote restoration.

The numerical findings below are final. One minor visual tick-label correction
was requested after actual PNG inspection; its actual successful closure is
recorded below. No further scientific execution or figure work is requested.

## Actual execution and one mechanical failure

The execution ledger records these actual child processes:

| Attempt | Child command | Exit | Interpretation |
|---|---|---:|---|
| 01 | `tests/test_angular_cohort.py` | 0 | Focused new scientific checks passed |
| 02 | `code/run_sweep.py` | 0 | Single bounded cohort/reference sweep completed |
| 03 | `code/summarize.py` | 1 | NumPy Boolean was not accepted by JSON serialization |
| 04 | `code/summarize.py` | 0 | Summary and actual PNG completed after mechanical repair |
| 05 | `code/summarize.py` | 0 | The single requested tick-label correction was rendered |

The exact argv, absolute cwd, UTC times, environment, code hashes, stdout,
stderr and wall/CPU are in `results/EXECUTION_LEDGER.json`. Through attempt04
Python wall/CPU totals are5.781100525004149s/5.775743s, including the failed
attempt. Tests and the sweep were each run once. New IVPs=0 and source
transactions=0. Historical resources and symbolic costs remain separate.
After the one visual correction, the final five-child Python totals are
8.168898051000724s wall and8.162283s CPU. These include every failed/successful
summary process; they are not a new reset of historical remaining resources.

The preserved traceback locates the failure in JSON encoding of summary gates.
The preserved one-line repair is

    gates={k:bool(v) for k,v in gates.items()}

after gate assembly. Reading the pre-repair source and diff confirms it converts
Boolean scalar representations without changing their truth values, equations,
tolerances, quadrature grids or raw sweep results. The first failure, original
source, diff and repair record remain. No test or sweep replay was required.

The focused test is one custom script, not a claimed pytest/unittest method
count. It evaluates all56 monomials through degree5 forQ14 and all120 through
degree7 forQ26, records four rule/source validation rows, and checks six invalid
input cases. The execution also verifies seven unchanged source/dependency
copies. These counts must not be relabelled as176 independent test methods.

## Reference, invariant and exact-symbolic evidence

The saved Wolfram output contains18 residual groups, all zero, plus positive
weights. It checks56/120 monomials and agrees with all eight exact main
energy/pressure coefficient entries derived independently. The reviewer read
this actual output; it was not rerun for C9.

| Actual maximum or minimum | Value | Relevant interpretation |
|---|---:|---|
| Reference32/64 difference | 1.9539925233402755e-14 | Below2e-12 |
| Independent octant/full difference | 7.299574441658989e-15 | Below2e-12 |
| Axial asinh/reference difference | 1.1223186627952777e-14 | Below2e-12 |
| K40 ideal-node bound, absolute | 8.674355235422484e-15 | Analytic truncation only |
| K40 bound normalized by F | 8.44930024167247e-15 | Below2e-12 |
| Actual packet mapping residual | 6.661338147750939e-16 | Below512eps |
| Direct spatial-trace residual | 6.661338147750941e-16 | Below512eps |
| Co-rotated-ray covariance residual | 2.162836871602664e-16 | Below512eps |
| Continuum reference rotation difference | 3.4064680727741957e-15 | Below2e-12 |
| Minimum continuum birth q | 0.9 | Strictly positive |
| Minimum directional log expansion | 0.2 | Strictly redward prescribed path |

Actual packets retain positive weights and number density n_b D. The checked
final number density is approximately0.301194211912202m^-3, with normalized
rounding residuals of ordereps. The highest physical energy/birth-energy ratio
is0.8187307530779819, consistent with the analytic e^-1/5 support bound. No
finite donor or event-rate normalization is inferred from these state weights.

The floating reference differences can exceed the ideal-node truncation bound:
the latter excludes floating node construction, transcendental evaluation and
summation. Both quantities are explicitly preserved; this is not an interval
certificate. The coarse16-point axial pressure error is approximately1.02e-11
and is retained as a diagnostic; the admitted64-point reference is the one
tested against2e-12. No coarse result was erased or promoted to the final gate.

## Leading coefficients and resolved orders

At eta=1/128, the actual signed coefficient discrepancies are:

| Source | Energy coefficient relative discrepancy | Pressure coefficient max-norm discrepancy |
|---|---:|---:|
| ANISO | 0.017057234599229032 | 0.024805773081556536 |
| ISO | 0.0010574219955337139 | 0.0011991089089021258 |

All are below the frozen5%. These use signed raw normalized F/P differences,
not a fitted coefficient and not the additional continuum-F-normalized error.

The selected finest resolvedQ14 triplet is1/128,1/64,1/32 for every admitted
observable. Both adjacent orders pass:

| Source / observable | First adjacent order | Second adjacent order | Frozen band |
|---|---:|---:|---|
| ANISO energy | 2.0241298939979053 | 2.0471831118583608 | [1.8,2.2] |
| ANISO pressure | 1.0346431468570938 | 1.0669951878736548 | [0.8,1.2] |
| ISO energy | 3.0014970243445065 | 3.002919289634917 | [2.8,3.2] |
| ISO pressure | 2.001247380993907 | 2.0023890474835953 | [1.8,2.2] |

These are orders in the prescribed anisotropic deformation eta, not time-step
convergence orders. The actual26 results are consistent with their higher exact
orders on resolved rows. In particular ANISO energy/pressure begin near3/2,
and resolved ISO energy/pressure near4/3.

The ISO-Q26 energy error at eta=1/128 is6.51255342974353e-13, below4096eps.
The corresponding first adjacent energy order is correctly null with
ROUNDING_UNRESOLVED. A raw leading ratio is retained in data but cannot support
a resolved coefficient claim. Later resolved ISO-Q26 energy orders are
3.996586129579531 and3.993000016300517. No slope was manufactured from the
unresolved row.

## Angular benchmark failures are the measured result

The main benchmark contains28 rule/source/eta rows. Exactly6 pass and22 fail
the2e-8 normalized full-tensor comparison:

- Four eta=0 rows pass by birth-moment exactness, up to floating reference error.
- Q14 fails all12 selected nonzero-eta rows.
- Q26 fails all six ANISO nonzero-eta rows.
- Q26 passes only the ISO eta1/128 and1/64 nonzero rows, and fails the four
  remaining ISO nonzero rows.

At eta=1, the aligned results are:

| Source / rule | Energy error/F | Tensor error/F | STF error/F |
|---|---:|---:|---:|
| ANISO Q14 | 0.0008101696001214329 | 0.004834587578027367 | 0.005104644111401196 |
| ANISO Q26 | 0.00020196017524835673 | 0.0014195314442230931 | 0.00148685150263923 |
| ISO Q14 | 0.0005193387079012793 | 0.0034894766648670542 | 0.0036625895675007785 |
| ISO Q26 | 0.000137904471378997 | 0.001045518426306019 | 0.0010914865834323513 |

The candidate improves these selected errors and their small-eta orders, while
retaining a material finite angular error at eta=1. Neither a positive measure
nor exact birth stress guarantees continuum accuracy after anisotropic drift.

The four rotated-physical-pair/fixed-ray eta=1 tensor errors are respectively
0.004659055526426848,0.0006267293943566231,0.003262338971481504 and
0.0004659558150323502 for ANISOQ14,ANISOQ26,ISOQ14,ISOQ26. All also exceed2e-8;
they are separate rotation diagnostics, not extra rows in the28-row benchmark.
Co-rotated rays preserve covariance. The explicitly nonzero fixed-orientation
differences distinguish angular-rule orientation sensitivity from a tensor
covariance failure. The max-component norm is the frozen component norm, not
a claimed rotation-invariant norm.

The16 frozen computational gates all pass because they admit trustworthy error
quantification, reference control and model consistency. They do not assert a
28/28 angular benchmark pass. This distinction is essential to PASS_SCOPED.

## Actual figure review and targeted visual finding

The actual `results/angular_cohort_errors.png` was opened. Its four panels show
the saved energy errors, pressure errors, signedQ14 leading ratios and the
fixed-grid orientation comparison. The2e-8 comparison line is visible, errors
above it remain visible, ISO/ANISO refer to birth source shapes, Q26 is labelled
a candidate rather than an actual REC inventory, and the footnote identifies
log-masked eta=0/true-zero entries. Scientific CSV/JSON values remain intact.

**C9-V1, minor readability:** in the lower-left ratio panel the logarithmic minor
tick labels near3e-2 and4e-2 run together. Root requested and this reviewer
confirmed a single tick-only correction: major ticks at1/128,1/64,1/32,1/16
with fraction labels, and no minor tick labels on that panel. No numerical
calculation, reference, source, tolerance or additional experiment is implicated.
The pre-correction PNG/source and the targeted diff should remain recoverable.

Status at this entry: numerical PASS_SCOPED; visual closure pending corrected
PNG readback. No optional figure redesign or test/sweep replay is requested.

### C9-V1 closure — actual corrected image and unchanged data

The reviewer opened the actual corrected PNG after attempt05. The four intended
fraction ticks are clear and separated; the crowded minor labels are absent.
All four panels, legends, comparison line and scope/zero-mask footnote remain
legible. **Actual visual review: PASS_SCOPED.**

The saved `results/figure_label_repair/tick_repair.diff` changes exactly two
plotting statements: the lower-left x ticks/labels and its minor formatter.
The pre-correction source and PNG remain. `AFTER_VERIFICATION.json` and direct
review hash readback show all five numerical JSON/CSV files byte-identical:
SUMMARY, COHORT_SWEEP, TEST_RESULTS, angular_errors and leading_ratios. The test
and sweep were not rerun. The final figure SHA256 is
`07ac5d367da17eb4bdba283f895ac3a6386504c75c8d8af0248a4f7dcf3e16be`;
final summarizer SHA256 is
`b7b3340beab1e97f60b116437b2018503fa95704917ed4a58c7005811e3661d8`.

Final reviewed inputs, actual output hashes and image dimensions are recorded
in `C9_FINAL_INPUT_IDENTITIES.json`. The reviewer performed no numerical
scientific execution; read-only receipt/file inspection and actual image
viewing are distinct from the metered scientific children.

## Claim ceiling

This admits only the frozen one-cohort angular experiment. It does not close
native finite absorption, supply a receiver-cell incident trace, calibrate a REC
trajectory, retroactively prove angular-continuum accuracy of old B3c IVPs,
replace the actual REC910 bootstrap, or complete B4/B5. Overall BASS physical
completion remains null. Merge and production remain outside the scope.
