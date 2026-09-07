# Local Codex handoff — BG02 state-to-constraint map

TASK=BG02_STATE_TO_CONSTRAINT_MAP_VALIDATION_V1
ROLE=LOCAL_HOST_EXECUTOR_AND_BOUNDED_REPAIR
SEPARATE_WORK_THREAD=NOT_USED
GITHUB_ACTIONS=DO_NOT_USE

## 1. Objective and existing evidence

Run the concrete research code already authored by the main thread, fix observed defects within this slice, validate it, and return readable Git evidence. Do not replan BASS or reimplement its geometry. This is the first validation of a full-ONF-state to constraint-component map, not another execution of the completed AUX comparison.

Prior candidate evidence is accepted as PASS_AUXILIARY_ONLY in its actual scope: original loader blocked with 17 unevaluated IDs, then the one required owner import enabled 17 Success / 0 Failure / 0 unevaluated / exit 0. Historical 16/1/exit1 is preserved and reused. The main thread inspected the original failure, repaired final JSON, owner/consumer source and loader diff. Those runs need not be repeated.

Read `docs/research/bg02_state_constraints/REVIEW_AND_DERIVATION_KO.md` at this delivery commit. Four executable inputs are already supplied under `research/diagnostics/bg02_state_constraints_20260907/`:

- `StateConstraints.wl` — exact state map through existing BASS APIs.
- `state_constraints_tests.wl` — 19 SC-prefixed tests and five actual-evaluation diagnostic inputs.
- `run_state_constraints.wls` — required source loading, observed-ID/results and final JSON.
- `plot_state_constraints.py` — reads actual stdout, extracts JSON and plots only actual returned mapper values.

All four are PREPARED_UNEXECUTED. Test-first authoring and static review are not observed RED/GREEN. Main-thread Container and Python calls failed before output. Do not call the code validated before running it. The code is not installed in BASS init.wl and no production adoption is requested.

## 2. Exact existing dependency snapshot — already available on GitHub

Use the SIX FILES from publication `2e1b6e2f12cc766c8ffe1160d6371a88730064a8` at:

`artifacts/handback/bg02_repaired_aux_comparison/20260907T052727Z/source/`

They are the returned read-only source subset of candidate `e404f914c0817b4c2ab3a0ff4632a8457e026fde`, tree `e2fc64860631e781082cceb3bef5b24fb8a06084`. This directory is the runtime BASS_REPO. The delivery branch also contains a HISTORICAL repository root: DO NOT use that root as BASS_REPO. The exact candidate snapshot, not the delivery commit's old root kernel, is the source to consume.

| Path relative to source/ | Git blob |
|---|---|
| wolfram/BASS/Kernel/Authority/BG02Convention.wl | d636a9e1643f65f43b18ca43477fab62dc20dd29 |
| wolfram/BASS/Kernel/Geometry/StructureConstants.wl | d224da1091da815d3979bdc3262ca65b4ab83ee4 |
| wolfram/BASS/Kernel/Geometry/LeviCivitaConnection.wl | c8e4be28b00956b1fe2009a7d5bc8222a45585e0 |
| wolfram/BASS/Kernel/Geometry/ONFConnectionCurvature.wl | 653aa9c4ee075db2fe4286de7936255b4f81179d |
| wolfram/BASS/Kernel/Background/EinsteinProjection.wl | ae8ee9bd834f83f0b7306943e3da637e86abe9f1 |
| docs/bass_master_ssot_v2/BG_02_IMPLEMENTATION/BG_02_CONVENTION_V2.json | 3083776f097e8a072866c3e695d72c7e07686c58 |

Reuse this snapshot or the already available exact candidate files. Do not require a new full checkout or ask the user to upload an archive. Verify actual file/blob identity and record source-subset execution. Publication identity, original candidate identity and newly authored code identity are distinct.

## 3. Physical/input contract

Use signature (-,+,+,+), positive K, epsilon123=+1, Hgeom=H_time/c and kappaG=8*pi*G/c^4. aB is a commutator vector, not normal acceleration. nB is the FULL symmetric structure tensor, not its trace-free part. rho/q are already normal-frame stress-energy components. Caller-supplied units and consistent symbolic assumptions are a contract, not a new automatic unit checker.

The exact input keys are Hgeom,aB,nB,sigma,rho,q,Lambda,kappaG. Do not accept injected sigma2/R3/divK values. Preserve all off-diagonal shear entries. Prove input symmetry/STF and nB.aB=0 under supplied assumptions, or return the stated Failure without projection. Approximate Real data are outside this exact-reference slice. Hgeom=0 is admitted without dividing by Hgeom. Nonzero Einstein residuals are legitimate off-shell outputs, not a reason to alter the input.

The map must call the existing geometry/owner/projection functions. Its only new mathematical reduction is the homogeneous free-index connection contraction of K. No second Koszul generator, hardcoded family Ricci table, source stub, copied owner coefficients, state projection, new Jacobi RHS or integrator is permitted.

## 4. Execution and informed repair

First read applicable local repository instructions and reuse an existing matching SC result if present. Do not reuse AUX PASS as SC results. New work must retain first-attempt logs and exact revision IDs.

Use an isolated worktree or directory. Resolve the existing actual local wolframscript and WolframKernel paths. The previous working kernel path was `/usr/local/Wolfram/WolframEngine/15.0/SystemFiles/Kernel/Binaries/Linux-x86-64/WolframKernel`; verify existence rather than guessing. Do not use MCP/cloud routing, GitHub Actions, package installation, license changes or permanent environment changes.

Execute `run_state_constraints.wls` with BASS_REPO set to the actual candidate snapshot. Use explicit `wolframscript -local <actual kernel> -file <actual runner>`, external timeout 150s, TERM then kill after 10s; the script has an inner 120s bound. Capture complete stdout/stderr and actual process exit regardless of success. Do not allow shell errexit to discard nonzero-exit evidence. Preserve the source-before record and host-side before/after hashes of all six dependency files and the four new code files. Check for incomplete final JSON or partial test events honestly.

If an implementation/loader/test-harness/serialization/plot defect is observed in THESE NEW FILES, diagnose it and repair it autonomously, then run relevant small regressions and the original SC target again. One repair cycle is not one edit. Do not ask for permission after each productive correction and do not blindly repeat unchanged failures. Keep process limits and any actual resource caps; sum attempts/time across this logical task. Missing syntax execution in the main thread does not justify a fake prior RED or a pre-written PASS.

The six already compared owner/geometry files and the old AUX/native suites remain read-only. Do not change physical expected identities to fit an output. If evidence instead requires an owner semantic amendment, expansion into actual time evolution or a protected source change, preserve the finding and return the smallest source-level proposal; do not silently enter that new scope.

After a genuine SC run, call the supplied Python plotting script with `--stdout <actual stdout.log> --out <fresh plot directory>`. It extracts the actual SC_FINAL payload. A non-PASS or incomplete result is preserved, not plotted as successful evidence. If matplotlib/runtime is unavailable, retain the successful symbolic result separately and report plot generation blocked; do not rerun Wolfram just to repair plot publication. Inspect both actually generated figures and record overlap/legibility and semantic scope. The line segments are guides across five algebraic inputs, not time trajectories or values evaluated between them.

## 5. Acceptance

Return actual outcomes for these exact 19 IDs (from the test file), including any missing/unevaluated status; do not infer completeness from a success rate. Expected successful completion has all 19 Success, no actual messages/runtime failures, genuine exit 0, and unmodified dependencies. It must show:

- input tensor norm/divergence constructed inside the map, not injected by tests;
- exceptional full-shear state with Hres=M=0, and deletion at the SAME Hgeom giving Hres=u^2/ell^2 while M stays zero;
- full-transverse, nonzero-flux momentum values and proper-frame covariance with nonzero momentum;
- Hgeom=0 regularity; exact-domain/missing/override/shape/STF/Jacobi failures returned without correction;
- general owner gradient-slot arithmetic kept separate from homogeneous geometric claims;
- plot input values actually produced by mapper calls, not substituted expected curves.

Failure of a physical assertion is not the same as an unevaluated report or parser failure. Preserve whichever actually occurs. No new broad audit or reviewer-of-reviewer loop is required once this work unit's evidence is adequate. Same-author checking is not independent review.

Even a successful SC run means only PASS_RESEARCH_COMPONENT_ONLY for this exact map. It does not mean numerical RHS, all-family solver, arbitrary-ell transport, native xTensor four-projection proof, generic gradient geometry, serialized production ingestion, finite-time stability, provider, likelihood or RF04 admission. No capture6/native17/old AUX invocation is included.

## 6. Git-first return, no manual archive transfer

Commit/non-force push related repaired code and readable results to an isolated task evidence branch, leaving main, PR131's historical head, original evidence and candidate dependencies unchanged. Use `[skip ci]` for commits, no workflow files, no Actions dispatch or CI computation, no merge/force push. A new PR is unnecessary for this return; an append-only link comment on PR131 is sufficient.

Publish CHATGPT_HANDOFF_KO.md, RETURN_STATUS.json, actual raw logs/final JSON, input/source/code identity, any repair patch and small regression logs, evaluated diagnostic rows, generated PNG/SVG and visual-inspection note if available. Keep essential files readable outside ZIP. No tokens, license files or unrelated raw data. Read the remote ref and principal file bodies back at the actual publication commit. A publication failure is not a scientific test failure and must not trigger a rerun of accepted scientific work.

Final output should contain actual status, repo/branch, tested source/code identity, publication commit/tree, HANDOFF_URL, RESULT_URL and remote-readback result. The user will pass only these links/output to the main conversation. Do not delegate this work to a work thread or ask the user to download/re-upload handoff archives.
