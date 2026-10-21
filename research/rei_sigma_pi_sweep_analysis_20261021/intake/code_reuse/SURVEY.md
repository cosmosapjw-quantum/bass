# ACCEL03 source seam and next-unit recommendation

Read-only survey, 2026-10-21. The parent reported a newly returned NCP five-case,
two-step run after this survey began. Its archive is being inspected by the
backup agent; no claim here independently admits that new run. ACCEL02 source
and all completed729 scientific evidence are reused.

## Recommended unit

Implement a standalone plan-driven aggregate and figure adapter for the existing
split-stress solver results. This closes a demonstrated output path gap: new
custom native cases execute, but the original aggregator accepts only the
original signed_grid()729 and the original figure footer always says64steps.
The output adapter can be implemented and verified with saved results and zero
new solver calls, native builds or performance benchmarks.

## Exact current contracts and reusable seams

1. `work_plan.py:65-108`: the case schema has exactly12 fields:
   case_id; three nonnegative magnitudes; three signs in{-1,0,1}; three signed
   coordinates; signed_Pi_total_requested; nominal_cancellation. Signed shear
   must have magnitude below sqrt(3). Coordinates and labels are unique.
2. `work_plan.py:110-152`: `load_completed_registry()` binds the original source,
   contract, endpointCSV, summary and review; it returns coordinate-keyed records
   with science_id, full science payload, seed and external completion locator.
3. `work_plan.py:161-209`: a pending_work_plan.v1 is the candidate authority.
   It contains candidate/completed/pending counts, science_context(_id),
   evidence_sources, completed records and pending records. A completed record
   has requested case_id plus baseline science_id and evidence.csv_case_id;
   requested aliases are legitimate. Pending has full case/seed/science/science_id.
   Completed reuse occurs only for64steps. A default completed-only plan has no
   global nsteps field:64 is recoverable from the pinned completion record.
4. `batch_worker.py:142-191`: shared_case_science.v1 manifest describes ONLY
   pending work; split_pilot.case_count is pending_count. completion_reuse binds
   the plan hash. Do not use manifest count as the full expected denominator.
5. `batch_worker.py:270-317`: a native result is the same
   rei.sigma_pi_split.group_result.v1 shape as the original group result, adding
   case_cache. Required group metadata: science_binding, owner_ref, nsteps,
   cases, status=SUCCEEDED. Each case contains case, seed, calibration, initial,
   numeric_checks, gates, owner_result. owner_result has config, source_identity,
   history(nsteps), final, nsteps, errors, schema. Histories include nsteps evolved
   rows; include initial as step0 to yield nsteps+1 exported rows per case.
6. `batch_worker.py:222-268`: case_store/source_id/science_id holds case.json and
   receipt.json. receipt binds science/source/toolchain/bytes/SHA256 and original
   label; wrapper result relabels the case to the plan's requested alias. A fresh
   group can legitimately have reused=true while the first saysfalse, so group
   JSON byte equality is not the duplicate scientific-result criterion.
7. `sweep.py:318-347`: scalar_row flattens nested mappings; result_paths_from_scope
   selects PASS/returncode0 receipts and verifies sibling result.json hash.
   It resolves the result relative to the receipt location and is portable under
   archive relocation. Explicit file imports should retain which validation
   route was used rather than invent executor success receipts.
8. `split_sweep.py:280-343`: current aggregate hardcodes signed_grid()729 for
   expected records. Its endpoint/history projection can be reused, but the
   expected-set construction must come from the supplied plan for custom work.
9. `split_plot.py`: fixed requested_slices=(0,.004,-.004), fixed64step footer,
   fixed extremal cancellation families and hard dependency on history.csv.
   Preserve this original script for original figures. New adapter must use
   actual supplied cases/nsteps/available histories and an explicit selection.
10. `plot_reuse.py`: reusable example of endpoint-only plotting. It labels
    markers as real samples, records each plotted point and hashes the pinnedCSV;
    it is itself fixed to nine cancellation points and is not a generic API.

## Portable result validation

Do not directly call validate_plan/validate_pending for postprocessing a foreign
target's recorded run. Those functions check the current Python/NumPy/SciPy
toolchain, regenerate initial context and seed_for. A postprocessor should bind
the recorded plan/science payload to its recorded toolchain and source, then
validate saved results against those records. The host doing analysis may have
a different compiler/library/runtime. This is scientific result ingestion, not
a request to rerun the solver or load its shared library.

Minimum semantic validation: expected case+seed+parameters/source; nsteps and
history length; initial/final scale factor and final==last history; exact eight
gate names with true values; finite fields; reductions used by the existing
error gates and initial checks. Use unchanged numerical limits. Single-pass
conversion and per-case reductions can replace global repeated scans.

Completed endpoints are mapped by known science_id to the pinned baseline CSV
row and then relabelled to requested case_id. Retain baseline source reference,
backend/run cohort, nsteps64 and history availability. Do not synthesize initial
or intermediate history from endpoint columns. For a mixed native+archived
64step dataset, retain per-row origin and do not silently call every row native.

Duplicate semantics: an exact repeat of the same scientific case body may be
deduplicated despite different case_cache.reused metadata. Conflicting bodies
must be reported with case/science identity and source paths. Missing expected
cases produce PARTIAL with explicit missingIDs; missing is never numeric zero.

## Three useful mathematical diagnostics

1. Signed LRS norm/work correspondence: for sigma=diag(-s,-s,2s) and
   pi_A=diag(-D_A/3,-D_A/3,2D_A/3), half-norms are sqrt(3)|s| and |D_A|/sqrt(3).
   With the owner normalization, signedPi_total=factor*(Dm+Dr), total norm is
   its absolute value; workA=2sDA and work/(H^3/kappa_t)=2signedSigma*signedPiA.
   Preserve physical constants and existing pressure/energy conventions.
2. Cancellation conditioning: for p=Pi_m, r=Pi_r, A=|p|+|r|>0,
   q=|p+r|/A is in[0,1], cancellation fraction=1-q, and sum condition number
   A/|p+r|=1/q. Component errors bounded by eps|p| and eps|r| imply absolute
   total error<=epsA. Relative total error is unsuitable near q=0. At A=0,
   mark the new ratio undefined with explicit ZERO_COMPONENT_SCALE status;
   preserve the owner's historical cancellation_fraction=0 without relabelling
   it as a measured conditioning value. At exact nontrivial cancellation use
   null plus a named divergent/zero-total status instead of nonfinite JSON.
3. Matched-control response: DeltaSigma(case)=Sigma_f(case)-Sigma_f(control)
   with exactly identical initial signedSigma, nsteps, science context and
   appropriate run/backend cohort, and zero initial requested matter/radiation
   stresses. No such control means response unavailable. Raw initial-to-final
   changes remain separate. This distinction prevents borrowing the64step
   baseline control for a2step native result.

## Proposed bounded acceptance contract

- Candidate accounting is a set partition of known reused, successful new and
  missing expected IDs. Unexpected IDs/coordinate clashes are rejected.
- Order-independent endpoint and history values reproduce saved scalar fields;
  case aliasing preserves science identity. No solver imports that run work.
- All-nine-field/three-component norm and work checks use scale-aware arithmetic
  residuals; choose the exact bound before implementation, preserving original
  physics gate thresholds. Do not use a relative total-stress tolerance.
- A2step five-case NCP dataset is labelled2step and contributes15history rows;
  completed729 endpoints remain64step and history unavailable if not supplied.
- Missing cells and missing controls remain visibly unavailable. For the sparse
  five-case set use scatter at actual coordinates; do not fill a rectangle or
  connect absent parameter points. Time-history lines connect only actual stored
  chronological samples and identify their low temporal resolution.
- Figure source point tables reproduce plotted IDs/coordinates/values. Visual
  read checks signed-vs-norm labels, color scale, panel comparability, legibility
  and clipping. No fit/interpolation/smoothing.
- Small mutation fixtures cover dropped expected case, duplicate/conflicting
  case, wrongnsteps, wrongbinding, failedgate, absentcontrol, zero-scale and
  exact-cancellation diagnostics. Fixtures are explicitly implementation tests.

## Available saved inputs

- Original split729 aggregate/cases.csv, summary.json and reviewed completion
  record are local and pinned. Original47,385-row history is external; do not
  download it just to validate the endpoint-only path.
- ACCEL02 evidence/TRAJECTORY_RAW.json has five records, each containing case,
  original and native full case results (two evolved steps). It can check scalar
  projection independently; it is not an executor result and must retain that
  different source provenance if imported.
- ACCEL02 evidence/worker/plan.json, prepared/manifest.json, scope_first and
  scope_second each contain one successful group with the same case. These
  exercise actual receipts and scientifically identical duplicate handling.
- Parent reports a new real NCP5case×2step archive, whose raw intake is pending
  in this survey. Prefer it as the production-shaped input once admitted.

## Attachment policy reuse

The five relevant text attachments01/04/05/07/08 have exact unchanged sizes and
SHA256 versus prior ATTACHMENT_INTAKE.json. Reuse their prior full-text intake;
this pass read the output/code contract portions and both figure checklists.
No installation/bootstrap/archive extraction was run. Preserve the earlier
policy adaptations: current workflow1.0 and current scope govern; inherited
fixed audit counts, blanket benchmark/plot requirements and lowellRust/family
tasks do not reset closed ACCEL02 work. For actual new figures, semantic and
legibility review from07/08 is directly useful and should be performed once on
the generated output, with repairs driven by actual findings.

No production code was modified. No scientific execution, benchmark, build,
new plot or external mutation was performed by this survey.
