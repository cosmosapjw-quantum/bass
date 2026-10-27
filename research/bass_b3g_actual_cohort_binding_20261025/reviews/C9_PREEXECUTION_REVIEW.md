# C9 preexecution static/source review

Reviewer: /root/b3g_rec_recovery; independent of the implementation worker.
Disposition: TARGETED_REPAIR_REQUIRED_BEFORE_GO.
Actual scientific/test/consumer/plot execution during this review:0.
This review is based on source and restored input inspection. The examples
below are analytic/static counterexamples, not claimed executed tests.

## Reviewed source identity and scope

Checkout observed HEAD:d6af237b66e78ca6ed4572068f6bc1a805bbb2d9.
Read this lane's FROZEN_CONTRACT.md, theory/TRANSPORT_AND_GEOMETRY.md,
inputs/MANIFEST.json, provenance/FROZEN_COMMANDS.json and:
code/{binding,transport,geometry,readiness,consume_saved,plot_saved,metered_run}.py,
tests/test_binding.py.
Read unchanged inputs/b3f/vendor/core.py and code/cohort_input_error.py,
selected source receipts/PATHs and native metadata/source constants.

The frozen command manifest at review identifies:
- binding.py8dfa4868401f8d242c24a53ac5c686a1083817ef9c1ca9f2718de3a31dc8ff9e
- transport.pydfdfe5fba1e87f6ff8ac05be4fb420e17ef944acaee99e6b96a415ccfcdbc1d3
- geometry.pya061d289eabfae8281847b9c21df52ccdb359af55b4a421d0e33e4bf9a14078a
- readiness.pyf658f26aa93d34c527c4c1ab18f4e76920666463db0e927fff025bfa2bec77c2
- consume_saved.pyde6dc7c1e23834193eb3f7ca6f359537672961ba9512f015c5925748c1975b54
- plot_saved.py68ec9febc00641ca80b775e0fd8271bd0d3a8718ccd778927a8877fee4eed6fa
- metered_run.py535a69748905c0fcbf54a0416783b768070c73553fec13541fffbce1b03a24a9
- tests/test_binding.py368b87349dcff6ad8c7624eceb7697f548ff4a03e852ddd3d287ab5d328f9f3f

## Blocking findings and minimal repairs

### C9-P1 — source duration uses the wrong stored clock difference

Target: binding.bind_birth, dtau=interval_end_tau-interval_start_tau.

Evidence: last actual receipt has interval_start_tau=.09960937500000089,
interval_end_tau=.1, but authoritative source_subflow_duration_tau=.000390625.
The original producer uses constant dt=.1/256 in source_arguments; accumulated
run.tau is separately recorded in interval_start_tau. Thus endpoint subtraction
differs from the actual subflow duration by approximately2.3e-12 relatively,
above512eps, even though the stored physical source duration is valid.

Impact: a false representation failure on the unchanged admitted source.
The first-receipt-only test does not cover the accumulated-clock case.

Repair: use the explicit source_subflow_duration_tau in L*dtau/c; retain the
interval-endpoint difference as a separately labelled clock diagnostic. Keep
the fixed representation tolerance. Add the last actual saved birth to the
focused source-duration test. Do not alter/recompute the original trajectory.

### C9-P2 — positive map/error bounds may silently underflow to zero

Target: transport.diagonal_bound, determinant_bound and duhamel.

Evidence: diagonal a=(800,0,0),e=(700,0,0) first computes exp(-800)=0 in
binary64; multiplication by expm1(700) then returns0. The exact first component
is exp(-100)-exp(-800)>0 and is representable. Similarly determinant a=300,
e=100 computes0 although its bound exp(-600)-exp(-900)>0 is representable.
Duhamel growth exp(mT) with mT=-1000 and positive e0,zero forcing can return0
while the mathematical term is positive. Products can also underflow before a
later factor restores representable size.

Impact: CONDITIONAL bound output with false zero, or a zero diagonal nominal
map that is mathematically invertible.

Repair: either evaluate the relevant positive expressions in a justified
log-domain representation, or explicitly restrict the numerical domain with a
typed underflow/range refusal. For this finite task a refusal is sufficient:
do not return zero as a positive conditional bound or invertible nominal map.
Cover map, determinant and Duhamel positive terms with targeted tests. Preserve
the mathematical theorem and label any numerical range restriction; no new
physical tolerance or old campaign is needed. No interval-roundoff certificate
is requested by this finding.

### C9-P3 — metadata completeness is promoted to physical absorption

Target: readiness.finite_donor_readiness return physical_finite_absorption.

Evidence: all nonempty metadata fields plus evidence_class
ACTUAL_BOUND_FINITE_DONOR return physical_finite_absorption=true while the same
record returns transaction_executed=false. No transaction, donor count/face
payload or owner result is consumed by this function.

Impact: downstream interpretation may close B3h from string completeness.
The current actual source-only row remains false, but the exported API has a
claim-promotion branch outside this unit's evidence.

Repair: keep structural/model-candidate readiness distinct and make physical
finite absorption false for this transaction-free unit. Any future completion
must consume an actual separately admitted transaction receipt. Add a focused
test that even complete ACTUAL-labelled metadata alone cannot mark physical
absorption complete. This is a claim-semantics fix, not a new security gate.

### C9-P4 — near-isotropic STF extraction can falsely reject valid stress

Target: geometry.si_to_core, pi=spatial-p*I followed by unchanged Source.arrays.

Evidence: valid diagonal spatial stress(1,1,1+ulp(1)) has p=1+ulp(1)/3 in exact
arithmetic. The represented p rounds to1, so direct subtraction yields
pi=(0,0,ulp(1)); the inherited core tests its trace on pi's own magnitude and
rejects it. The actual ISO saved data include pi around1e-16 of radiation
density, so the cancellation regime is relevant to this selected input class.

Impact: a valid near-isotropic stress may be misclassified as physically
non-STF or fail the ordinary saved-endpoint consumer. The exact-isotropic test
does not cover this regime.

Repair: evaluate the same mathematical diagonal STF components via pairwise
differences, e.g.pi_ii=((Tii-Tjj)+(Tii-Tkk))/3, retaining offdiagonal components.
This is an algebraically equivalent evaluation, not a projection or clipping
of supplied physical stress. Alternatively preserve an explicitly supplied
p/pi split with verified reconstruction. Add a near-isotropic symmetric
synthetic control. Keep original core and acceptance tolerances unchanged.

## Checks supporting the plan

-512births and514endpoints are actually available, including all gross source
 receipts and separate lower-rest/excitation/radiation sectors.
-Integrated down counts are used once and fixed E matches unchanged B3f.
-Source-energy uncertainty remains separate from inherited fixed-E B3f; missing
 eS/en/eE remain null and the B3f call requires INPUT_ERROR_UNSPECIFIED.
-R(t_b,t_b)=I is used only at birth; absent midpoint beta remains an explicit
 final-transport input obligation.
-C9-S1 wording is now corrected: nominal logarithmic alpha reconstruction has
 separate unknown numerical reconstruction error; no original-byte claim.
-SI stress and energy-equivalent four-force units match alphaL and L/c; rate
 terms are not inserted into state pi. The deliberately distinct c=5,L=7 unit
 test is useful and independent of default physical constants.
-Native E21 matches copied hydrogen.h; native Wien and standalone Planck remain
 separately named; native instantaneous ledger is reused and not re-executed.
-The source/RHS consumer performs four algebraic RHS checks, no IVP. The core
 equations compared are the correct Bianchi-I zero-curvature/rotation limits.
-The rational moment, decimal exponential, unit-conversion and reference-law
 controls provide useful independent expected values. The new findings need
 the focused controls specified above, not a broader historical test replay.
-The metered driver preserves STARTED/failed attempts, rejects automatic replay
 and enforces command order/cumulative allocation; historical unknown budgets
 are not reset. The actual cost ledger remains pending execution.

## Stop rule and next action

Authorize one bounded mechanical repair addressing C9-P1..P4, refresh the code
freeze and inspect only the corresponding diff. If those findings close,
perform the single frozen test/consumer/plot sequence and review its actual raw
outputs and figures. No optional recursive audit or broader suite is needed.
Scientific admission remains pending until those actual results are reviewed.

## Bounded repair readback — GO_FOR_FROZEN_EXECUTION

The root-authorized mechanical repair was read back without importing/running
the changed numerical code or executing tests. The original findings above are
retained. Review scope was only C9-P1..P4, the associated tests and frozen hashes.

- C9-P1 CLOSED_STATIC: bind_birth now reads the positive authoritative
  source_subflow_duration_tau; endpoint subtraction is retained separately as
  interval_endpoint_subtraction_minus_source_duration_tau. The last actual
  ISO receipt is included in the focused test; the512eps criterion is unchanged.
- C9-P2 CLOSED_STATIC: positive nominal diagonal-map/determinant zero results
  raise explicit underflow ValueError. Positive component bounds/products and
  Duhamel growth, integral and forcing products reject silent underflow. This
  is a declared numerical-range refusal, not a zero certificate. Eight focused
  underflow cases cover the indicated paths. Existing finite moderate-input,
  zero-interval and positive/zero/negative-growth controls remain present.
- C9-P3 CLOSED_STATIC: input_candidate_ready is separate from
  physical_finite_absorption, which is always false in this transaction-free
  unit. A complete ACTUAL-labelled metadata control checks the distinction.
- C9-P4 CLOSED_STATIC: diagonal pi uses algebraically equivalent pairwise
  differences, while offdiagonal entries and the inherited core are unchanged.
  The explicit one-ULP near-isotropic control checks both signed components.
  No clipping/projection or acceptance-threshold change was introduced.

Actual sha256sum readback agrees with the updated frozen command manifest:

| File | SHA256 |
|---|---|
| code/binding.py | 043437f5de3f71483f082b9924da7801e2c89b9a7bf231289e0c898c569dd29e |
| code/transport.py | 69f67c7631a5bed304f5186597c091d128e025043e37963f9a945e749610326b |
| code/geometry.py | 1a6f4891e3455452cc868bdd41d51d4d1b78af95d6ee50564ab263cb9b2f0b76 |
| code/readiness.py | 13048bd8729a4842e1a9027a9e30edc84f9006c72873aa57ac9dcf7236b4e684 |
| tests/test_binding.py | 1f84f4a37867276fc711d90abab37d88e17318d176994dbf5f292d95c62adada |
| code/consume_saved.py | de6dc7c1e23834193eb3f7ca6f359537672961ba9512f015c5925748c1975b54 |
| code/plot_saved.py | 68ec9febc00641ca80b775e0fd8271bd0d3a8718ccd778927a8877fee4eed6fa |
| code/metered_run.py | 535a69748905c0fcbf54a0416783b768070c73553fec13541fffbce1b03a24a9 |

Disposition: GO_FOR_FROZEN_EXECUTION under the unchanged root allocation and
one-test/one-consumer/one-plot command sequence. Scientific/test execution by
this reviewer remains0. This closes the preexecution findings; final numerical
and physical admission awaits actual raw results and the designated final
independent reviewer. No further optional static audit is required.

