# RF04 LOCAL-01 v2 public-boundary implementation prompt — R2

Work only on a new isolated implementation branch whose exact parent is the authority branch containing RF04-V2-PUBLIC-MAPPING-R2-20260831. Use R2_IMPLEMENTATION_PLAN.md from this delivery and do not use an earlier pre-R2 local implementation plan. Do not edit, rebase, merge, close, retarget, or force-update PR #70 or PR #71. Preserve PASS_RF04_SCALAR_RAW_SLICE_PROOF, LOCAL-02 NOT_RUN, and NO_PASS_RF04 unless fresh LOCAL-01 evidence proves otherwise.

Before any source edit, verify every package manifest entry; the PR #70 parent commit/tree; the final donor Git blob 693e9fff0d44f2b8e40966ceb8da3c348d830bd4 and SHA-256 f1f624d47b35208d339e6ea298f023d70012e54c80357973a65dc63c9491de6e; and the inherited v1/v2 authority blobs. Stop with STOP_INVALID on any mismatch.

Implement exactly the three existing v2 public symbols. The identity symbol has this exact public argument order:

~~~
rf04_typeii_polarized_execution_identity_v2(directions, weights, remap_plan)
~~~

It validates the caller inputs, derives the grid and plan digests through the codecs in V2_PUBLIC_MAPPING.json, and returns the canonical JSON identity. The trajectory and batch result identity must be byte-identical to the direct identity result for the same invocation context. Do not introduce mutable global state. The static runtime payload ID is bass-rf04-polarized-v2-native-local01/v1; record the exact wheel SHA-256 only in the evidence receipt.

Use ScreenInputPolicy::Reject { tolerance: 1e-10 }, never Project, and apply the exact geometry receipt codecs, receipt hash, and chain formulas from the mapping. The two diagnostic arrays measure the complete raw accepted-step candidate immediately before final projection and the stored accepted state immediately after it. Implement the exact batch status/error-code table; common failures are whole-call typed exceptions, while individual member failures are rows with status 1, an all-NaN final state, completed accepted-step count, and the exact allowed code.

Use test-first work. Preserve focused RED logs before each public-boundary slice, then GREEN logs. Build the locked Rust 1.94.1 wheel outside every Git worktree, install it cleanly, and read back all three v1 and all three v2 symbols. Run the affected Rust/PyO3/Python tests and the PHYS-MATH and PHYS-MATH-CODE audits. If any required semantic is still missing or any P0/P1 remains, stop fail-closed and do not start LOCAL-02.
