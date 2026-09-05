# B0R1 native xAct typed-view calibration — source delivery

Status at publication: **PREPARED_UNEXECUTED**. This is neither a new native PASS nor an observed RED/GREEN cycle. Container and Python tool admission failed before execution; connected Wolfram context/evaluator returned MCP SSE HTTP 404 before a kernel result. No new numerical or symbolic runtime result is claimed.

## Actual advance

The previous PR #129 Wolfram replay was plain coordinate algebra. This new diagnostic calls pinned native xAct/xCoba `DefMetric`, `MetricInBasis`, `MetricCompute`, `ComponentArray`, and `ToValues`. Its native Riemann and Ricci components are compared with a separately assembled Christoffel calculation. It does not import the BASS component oracle or assign the expected Einstein momentum to the native output.

The 12 exact named obligations were written into CONTRACT.json before the runner. They are prepared test specifications, NOT 12 executed tests. This is diagnostic source, not production code or a canonical authority amendment.

## Physical scope

The metric is the generic exponential homogeneous Bianchi V calibration family, tau=c*t:

    ds^2 = -d tau^2 + exp(2 H1 tau) dx^2
         + exp(2 H2 tau-2 a0 x) dy^2 + exp(2 H3 tau-2 a0 x) dz^2.

H1,H2,H3,a0 have dimension L^-1. The normal is future-directed, K=+h h nabla n, and q=-h T n. The independent metric-derived spatial K and divergence are compared against native mixed Ricci. Native E components are formed from native Ricci and the declared matter tensor, not from the target momentum formula.

The native all-lower X view is tested against independent derivative-first B components via X=-B. Physical Ricci is contracted in both views and must agree without negation. The full spatial Gauss and Codazzi component arrays are tested before substituting a sentinel, so they do not reduce to the rank-one-K zero-wedge control.

At a0=H1=1/ell,H2=H3=0,tau=x=0, the old momentum formula must differ by +4/ell^2. A wrongly negated physical Ricci must also be detected. Arbitrary symbolic flux components test the unchanged matter sign. This is one metric-family calibration, not a theorem for all Bianchi branches, the exceptional VI_-1/9 sector, arbitrary lapse/shift, or the abstract four-projection bridge.

## Runtime contract

- Existing `Authority/Environment.wl` is loaded before any full BASS init (the latter is never loaded).
- xAct archive identity is the already published `run_stage.wls` pin, not a newly predicted hash: 7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be.
- The pin qualifies the claim that this particular runtime was used; it does not determine whether a formula is true. No optional CAS or new generated-source hash gates this run.
- Use a fresh kernel. xCoba must resolve within the verified extracted archive; package membership and real definitions are checked.
- No CAS fallback is silently called. The Python launcher is standard-library orchestration only.
- Output must be a new directory outside the checkout. No automatic deletion, retry, rebase, commit or push occurs.
- The launcher writes a checkpoint before kernel launch and a process receipt after return, timeout or handled error. It preserves logs and native failure receipts. OS termination of the launcher itself can leave only the checkpoint; it is not a PASS.
- Admission requires the exact named ID set, every computed check true, no recorded native computation messages, a valid native receipt, exit 0, no timeout, unchanged inputs and a clean checkout. Missing kernel/receipt is not misreported as a failed Einstein theorem.
- Archive extraction uses the existing activation helper and may leave its temporary installation for failure inspection; no broad cleanup is performed.

## Local execution

Use a clean detached worktree containing this child branch. The input archive can be the already extracted Fix3 package's vendor file; no additional download is required.

    python3 research/diagnostics/bg02_b0_20260905/native/run_native.py \
      --xact-source /tmp/bass-bg02-cas-fix3/BASS_BG02_CAS_BATCH_FIX3_20260904/vendor/xAct_1.3.0.tgz \
      --output /absolute/new/path/outside/the/checkout

The new PROCESS_RECEIPT.json, native.json when available, stdout.log and stderr.log are the next evidence. Do not reuse old native PASS receipts or the 13-method Python source-adversarial log.

Possible narrow success: PASS_NATIVE_CALIBRATION_ONLY. Even that would not amend the production formula registry, close the full native bridge, or admit a provider.

## References inspected for this delivery

BASS at ac01009dec8678d9f1b8af10fb915b871e2358fd:
- Authority/Environment.wl, blob fea03d26573433a2934796ec5e513544ed78e0be.
- Geometry/XCobaCurvatureWitnesses.wl, blob e556bd4fbde147e7bcf5ad276ad92b571da04c14.
- wolfram/scripts/run_stage.wls, blob e4d55f77327d69236c03c1a401086a80f6d00d73.

Official xCoba documentation: https://xact.es/xCoba/ . SciSpace located Gourgoulhon, arXiv:gr-qc/0703035; its abstract supports its subject coverage, not a newly checked equation-level claim in this session.

Next: execute this native calibration once, inspect its actual residuals, then perform the versioned public momentum/view amendment if supported. R10A and REC donor work remain independent. No overall completion percentage is assigned from this source-only delivery.
