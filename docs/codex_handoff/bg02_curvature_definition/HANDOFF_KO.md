# Local Codex handoff — BG02 curvature definition to hypersurface blocks

TASK=BG02_CURVATURE_DEFINITION_TO_BLOCKS_V1
ROLE=LOCAL_HOST_EXECUTOR_AND_BOUNDED_REPAIR
SEPARATE_WORK_THREAD=NOT_USED
GITHUB_ACTIONS=DO_NOT_USE

## 1. Goal

Execute the supplied native xTensor derivation from the ambient curvature/commutator definition to the Gauss, Codazzi and normal-Ricci hypersurface blocks. Preserve the first observed result, repair only defects in the three new files within the fixed geometric contract, revalidate, and publish readable Git evidence.

Do not re-run or reopen the already accepted predecessor:

- AP tested code: `4149649462758165e64673ebb86498b708ef9a0e`
- AP evidence: `d34606f2754da02b58b38946dc414fe50f257ed6`
- AP00--AP12: 13/13 Success, exit 0
- AP ceiling: `PASS_CONDITIONAL_ABSTRACT_CONTRACTION_ONLY`

The AP result explicitly left `curvature_definition_to_blocks_verified=false`. This task targets that one remaining premise only.

Read at the delivery commit:

- `docs/research/bg02_curvature_definition/DERIVATION_AND_SCOPE_KO.md`
- `research/diagnostics/bg02_curvature_definition_20260907/CurvatureDefinitionBridge.wl`
- `research/diagnostics/bg02_curvature_definition_20260907/curvature_block_tests.wl`
- `research/diagnostics/bg02_curvature_definition_20260907/run_curvature_blocks.wls`

All three code files are PREPARED_UNEXECUTED. No new CB PASS exists before your run.

## 2. Fixed mathematical contract

Use exactly:

```
g_ab signature (-,+,+,+)
n^a n_a = -1
h_ab = g_ab+n_a n_b
K_ab = + h_a^c h_b^d nabla_c n_d
A_a = n^b nabla_b n_a
```

The normal is hypersurface orthogonal. `A_a` is normal acceleration, not Bianchi `a^B_a`.

For xTensor's induced metric machinery, the project convention is represented by:

```
$ExtrinsicKSign = +1
$AccelerationSign = -1
```

Do not change those signs to make residuals vanish without first demonstrating an actual project-convention mismatch.

The required equations are frozen by the derivation note:

```
P_h[R_abcd] = R3_abcd + K_ac K_bd - K_ad K_bc
P_h[n^a R_abcd] = D_d K_bc - D_c K_bd
P_h[n^a n^d R_bdca]
  = -(L_n K)_bc + K_b^a K_ac + D_c A_b + A_b A_c
P_h[(L_n K)_bc - n^a nabla_a K_bc] = +2 K_b^a K_ac
```

The operator-level commutator derivations are load-bearing. Do not replace them with a rule that directly substitutes the target Gauss/Codazzi/Ricci equation.

## 3. Native execution

Use the existing local Wolfram/xTensor installation. Do not install or upgrade packages, change licensing, use MCP/cloud Wolfram, xCoba, GitHub Actions or CI.

Resolve the actual paths instead of assuming them. The previous accepted AP run used:

```
/usr/bin/wolframscript
/usr/local/Wolfram/WolframEngine/15.0/SystemFiles/Kernel/Binaries/Linux-x86-64/WolframKernel
/home/cosmosapjw/.WolframEngine/Applications/xAct/xTensor/Kernel/init.m
```

Run in an isolated directory/worktree with a fresh kernel. Suggested outer envelope:

```
timeout --signal=TERM --kill-after=10s 300s \
  <actual wolframscript> -local <actual WolframKernel> \
  -file <actual run_curvature_blocks.wls>
```

The runner has an inner 240-second bound. Capture raw stdout, stderr and actual process exit even when nonzero. Do not allow shell errexit to discard the first failure.

The runner must observe exactly nine CB IDs:

- CB00_POSITIVE_K_ACCELERATION_SIGN_LOCK
- CB01_GAUSS_OPERATOR_COMMUTATOR
- CB02_GAUSS_TENSOR
- CB03_CODAZZI_OPERATOR_COMMUTATOR
- CB04_CODAZZI_TENSOR
- CB05_NORMAL_RICCI_OPERATOR_COMMUTATOR
- CB06_LIE_VS_PROJECTED_NORMAL_K
- CB07_NORMAL_RICCI_TENSOR
- CB08_XTENSOR_INDUCED_DECOMPOSITION_RECONSTRUCTION

Record actual per-ID outputs/messages, runtime failures, whole-invocation messages, source hashes, xTensor init hash/version and process exit. A TestReport that never starts means IDs are unevaluated/unknown, not physical failures.

## 4. In-scope automatic repair

Likely implementation-sensitive surfaces include:

- current xTensor `InducedFrom` / generated-head naming
- `Projectorcbh` inert-head behavior
- `ProjectDerivative` evaluation order
- `SortCovDs` canonical slot conventions
- `GradNormalToExtrinsicK` and sign variables
- `LieD` / `LieDToCovD` behavior
- held evaluation, dummy/free-index freshness and `ReplaceIndex`
- uncaught `Throw` or incomplete final JSON

If these produce an actual failure, diagnose and repair the THREE NEW FILES only. Add small API regressions for the observed defect and rerun the original nine CB assertions. Multiple informed edit-test-diagnose iterations inside this same task are allowed. Preserve every attempted code revision and first failure.

Do not modify the frozen geometric equations, AP expected values, old AP/SC/AUX/native files, BASS production source, candidate owner, or xTensor package. Do not introduce a coordinate metric or xCoba as an easier replacement for the abstract proof.

If the actual native convention reveals that a written Riemann slot ordering is wrong, preserve the native xTensor convention and repair only the adapter/index ordering after explicitly deriving the mapping. Do not flip both native curvature and target equations together.

## 5. Acceptance and claim ceiling

A successful run requires:

- 9/9 exact IDs observed
- every CB assertion Success
- actual exit 0
- no unhandled whole-invocation messages
- no runtime failures
- unchanged three code inputs during the accepted attempt
- actual native xTensor evaluation

The status ceiling is:

`PASS_NATIVE_CURVATURE_BLOCK_DERIVATION_ONLY`

If this passes, set `curvature_definition_to_blocks_verified=true` in the returned result. Do not mutate the earlier AP evidence file to do so.

The logical scientific consequence may be stated narrowly: this new PASS plus the already accepted AP PASS closes the research-level mathematical chain

```
ambient curvature definition
 -> Gauss/Codazzi/normal-Ricci blocks
 -> Ricci/Einstein contraction
 -> four 1+3 projections
 -> existing BASS component consumer parity.
```

It still does NOT imply production native API integration, background time evolution, constraint propagation, family-wide solver support, matter closure, provider/RF04 or release/merge readiness.

No new plot is required: these are exact abstract tensor identities, and an expected-number plot would add no evidence. Do not fabricate a figure to satisfy a generic plotting checklist.

## 6. Git-first return

Use a new CB-specific evidence branch or an existing exact matching task branch. Commit with `[skip ci]`, non-force push only. No Actions/workflow changes, no merge, no force push, no mutation of main/PR131 historical refs or previous evidence branches.

Publish readable files outside any archive:

- `CHATGPT_HANDOFF_KO.md`
- `RETURN_STATUS.json`
- raw stdout/stderr/final JSON for every attempt
- original and repaired CB code revisions
- patch(es) and focused API regression logs
- attempt/time accounting
- package/runtime provenance
- remote readback record

Remote-read the final branch/ref/tree and the principal file bodies. Publication failure is separate from the mathematical run and must not cause a rerun of an accepted calculation.

Return only the actual status, repo/branch, tested code identity, publication commit/tree, HANDOFF_URL, RESULT_URL, remote-readback status and the next minimal scientific action. The user will pass those links/output back to the main conversation. No work thread or manual archive transfer is part of the normal path.
