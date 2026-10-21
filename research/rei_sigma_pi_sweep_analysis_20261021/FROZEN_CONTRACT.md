# ACCEL03 — frozen theory / implementation contract

Frozen before new implementation outputs on 2026-10-21 (Asia/Seoul).
Unit: ACCEL03_PORTABLE_SWEEP_ANALYSIS_AND_MASSIVE_STRESS_RESPONSE.
Controller owns this contract and scientific admission; prescribed implementation belongs to a lower-tier coding executor. One fresh independent review closes the unit. Existing verified ACCEL02 evidence is reused.

## Goal and baseline
Close the actual output-path gap for arbitrary explicitly planned split-stress cases: original split_sweep.aggregate hardcodes729 and split_plot hardcodes64steps/fixed slices. Supply portable plan-driven aggregation, cancellation-aware diagnostics and actual-sample figures using stored NCP five-case/two-step results and archived729 endpoints. Derive and implement a small diagnostic of the existing massive finite-sum response; no solver change.

Base branches at intake:
- BASS research/rei-sigma-pi-native-moments-20261021 commit215bb3e66d81a7013d2132831d210aee36234ab4, tree7b49f694aa9d3114c4102f04d5c3d8906dc3be05.
- REI same branch commit926bae816ef8339137e2813cc40f1d514b763e1f, treeb6e5e3e91287f407008793d16dd4d486a27bf45c.
- Executable source remains BASS7fe0e25a28c0e48110c522378e203ffb934cc504 / REI231df3ab717dbc112f63b77953f64def08e9bcb5. ACCEL02 source bindings verified unchanged in new target archive.
- Target archive SHA256 ad92f4207a6845a0326a095cb904792b6d34bf0654f7148fe3c530b47f5e2817,6003218bytes; actual one-GET verification and stored comparisons in intake.
- New branch research/rei-sigma-pi-sweep-analysis-20261021; new directory research/rei_sigma_pi_sweep_analysis_20261021.

## Authority and allowed writes
Write new analysis code, focused tests, saved analysis results/figures and documentation only under this new directory. Do not change original pilot, ACCEL01, ACCEL02 production code or their frozen input/reference outputs. Existing checkout is a source snapshot, not a Git working tree; publication uses leased Git Data updates on a new branch. Preserve unrelated root-level NCP return files in parent trees.
Read applicable REI AGENTS (same blob429a5a13 as retained policy). Current user explicitly authorizes light sandbox checks and push/backups. No benchmark, new trajectory, full suite, dependency install, NCP rerun or native compilation is needed.

## Physical conventions and claim
Non-tilted LRS Bianchi I; signature(-,+,+,+). Original warm C15 a=.1999.. .2, independent matter/radiation P2 seeds, original half-contraction norm. Retain physical c,hbar,k_B through the owner normalization; computational moment variables are already nondimensionalized by its fixed scales. Total stress adds signed components before norm. No clipping small signed residuals.
This unit claims portable saved-result accounting/plots and exact fixed-weight massive response identities, checked on a bounded finite set. NCP target5case evidence is admitted against unchanged ACCEL02 tolerances. FullEoR/non-LRS/Q^a/convergence remains separate.

## Production API and data authority
Provide aggregate.py with:
- --plan PATH (required authority for full expected candidate set)
- --manifest PATH when pending group outputs are supplied
- --scope PATH (repeatable) and/or --result PATH (repeatable)
- --out PATH; optional explicit --baseline if needed.
Use existing result_paths_from_scope receipt selection where useful. Explicit result imports report that route honestly.
Output summary.json, cases.csv (endpoints), history.csv (only available actual initial+evolved samples), diagnostics and provenance sufficient to reproduce figures.
No runtime source/NumPy comparison against analyst host and no PreparedContext creation inside the aggregate path. Reuse pure work_plan case/science functions and pinned completion registry where safe; validate stored plan/science/toolchain mutually.
Candidate sets partition into reused_completed, successful_pending and missing_pending; pending-only manifest count is not the denominator. Missing returns PARTIAL with explicit missing IDs; do not treat absent samples as zero. Unexpected IDs, conflicting duplicates, wrong input/source/science binding, wrong step count, malformed/nonfinite scientific rows, failed original physics gate produce a clear input-integrity/physics diagnosis.
Requested completed-case aliases are legitimate: map science_id to the pinned baseline csv_case_id, then retain requested case_id. Keep per-row source/backend/toolchain/nsteps/run cohort and history_available. Do not claim all mixed rows ran natively.
Duplicate same case-body may be deduplicated when only group metadata/case_cache.reused differ; conflicting scientific payloads are reported, not silently selected.
Validate original eight gate names/limits, stored initial mapping, owner-result nsteps/history count, initial/final a, final equality with last history and required source/config. Do not re-run solver. Existing error reductions and positivity criteria are unchanged.
Default archived729 projection is64steps with zero available intermediate history; NCP5case2step projection gives15rows including initial once, not20rows counting final twice.

## Cancellation and response diagnostics
For p=signedPi_m, r=signedPi_r, A=abs(p)+abs(r):
- q=abs(p+r)/A for A>0 (residual fraction), cancellation=1-q, condition=A/abs(p+r).
- A=0 yields null ratio/condition and ZERO_COMPONENT_SCALE; exact total0 with A>0 has q0 and divergent condition represented as null plus EXACT_CANCELLATION.
- Preserve owner historical cancellation_fraction independently.
- All finite-domain row operations should be NumPy vectorized where useful, with initialized output arrays and masked division; no np.vectorize.
- Total sum/norm/work reconstruction uses a component-scaled arithmetic check, not relative error divided by near-zero total. Default arithmetic limit 128*eps64 times an explicitly relevant nonzero component scale; if all scales zero require exact zero. For existing serialized redundant fields whose construction order differs, preserve original values and report residuals; do not silently replace them.
- Matched-control response uses exact initial requested signedSigma, nsteps, science context and same source/backend/toolchain cohort, zero requested matter/radiation stresses, same start/end interval. Missing control => null/status. Raw final-minus-initial change stays distinct.

## Massive response diagnostic (derived)
Let x=ln(a/a0), r0=exp(-x), u=mu^2,
R2=exp(2b)(1-u)+exp(-4b)u, P2phys=(3t-1)/2,
t=exp(-4b)u/R2, E=sqrt(mbar^2+r0^2 qbar^2 R2),
v2=r0^2 qbar^2 R2/E^2.
J2=r0^3 sum W E v2 P2phys; J4=r0^3 sum W E v2^2 P2phys.
At fixed weights:
J2_x=-5J2+J4.
J2_b=-G, G=r0^3 sum W E v2 [2(2-v2)P2phys^2+9t(1-t)] >=0 for W>=0.
Thus dJ2/dt=H(-5J2+J4)-sG for xdot=H,bdot=s.
This is the collisionless massive constitutive response only; radiation collision/emission/UV terms stay in the owner.
At b0 and separable1+alpha_m P2, angular integral=2alpha_m/5 and the radial J4/J2 factor is a weighted v2 average in[0,1] for nonzero anisotropy. Massless limit J4=J2 gives fixed-b a^-4; nonrelativistic leading term gives a^-5.
Provide moment_response.py computing these diagnostic sums from existing quadrature arrays/weights, no ODE, and verify_moment_response.py for bounded checks below. It need not change or load the native backend.
Wolfram residuals for both derivatives returned exactly0; positivity query returned empty negative domain; actual code/output retained.

## Figures and scientific output
Provide plot_sweep.py consuming analysis outputs only. Generate:
1. NCP5case actual-sample signed component/shear summary with actual2step labels and one cancellation time-history panel using three saved times.
2. Archived729 endpoint parameter-slice figure with selectable exact signedSigma (default0), actual coordinate scatter and source/nsteps labeling.
Record source point tables and provenance for every plotted series; preserve signed quantities separately from norms. No interpolation, smoothing, fitting, nearest-control borrowing, absent-cell fill or fabricated history. History lines join actual time samples and show markers.
May use installed NumPy/Matplotlib; primary API docs checked. Reuse existing plot_reuse and split_plot field mappings/style only where their fixed-case assumptions are removed.
Root and fresh reviewer must inspect rendered PNGs. Fix concrete layout/semantic findings only; one review closes accepted scope.

## Bounded verification, fixed before implementation
0 solver calls;0 builds;0 benchmark runs. At most2 CPU workers, numericalthreads1.
- Actual NCP5 saved result groups against plan+manifest:5expected,5success,0missing,15historyrows,nsteps2, correct cohort; ensure portable relocated path intake.
- Actual archived729 completion-only plan:729expected/reused,0pending,0historyrows; endpoint fields reproduce pinned CSV exactly as floating numbers and aliases work.
- Existing one-case first/second successful scope result validates identical scientific duplicate handling.
- Focused mutation tests only for missing case(PARTIAL), unexpected/conflicting case, wrongnsteps, badsciencebinding, failedgate, absentcontrol, exactcancellation, zeroscale and legitimate alias/duplicate; no full old suite.
- Moment response: alpha in[-0.9,0,1.8], x in[0,ln(.2/.1999),.1], b in[-.1,0,.1],27points. Existing96x32 quadrature. Five-point finite differences h=2^-15 in x/b; normalize derivative residual by sum(abs(kernel)) or energy J0 to avoid cancellation. Bound2e-9 for both analytic identities. G nonnegative within128eps64*J0. Massless/massive asymptotic checks are illustrative computational limits, clearly distinct from C15 parameters, and may use a few analytic one-node values without new source preparation.
- Figure point-table values reproduce aggregate values; all counts/labels/cohorts checked; actual PNG visual review.
Preserve raw commands/stdout/exitstatus and actual input/source IDs. Report requested execution model separately from unexposed actual runtime model. New diagnosis may authorize one targeted repair and its regression check; do not widen criteria.

## Completion and checkpoints
A: source/backup delta, NCP admission evidence, derivation+CAS, this frozen contract, initial DAG; publish and provider ACK.
B: code+bounded raw results+figures; publish and provider ACK.
C: one fresh independent review, scoped decision, report, executable Codex and next-thread handoffs, final restore package; publish, one full remote GET/size/SHA/CRC/member check, receipt closeout.
Reuse prior checkpoint helpers. Stage receipts describe observed status, not inferred success. Final archive may precede its own ACK; keep later actual receipts in their containing Git commit without recursive hashes.
