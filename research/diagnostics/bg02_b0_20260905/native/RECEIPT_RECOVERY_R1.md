# BG-02 receipt recovery R1: evidence intake and software RED

## Scope and state

This child starts from BASS PR #130 commit
`477371143f15ef2625a7de21a5d178b09ffc1c32`, tree
`fe4c9f9b6deae0bf072dd553cd046c0a4a7801e3`.
The first commit adds tests, bounded software-only CI, and this record.
It does not change the native calibration, production geometry, W2 registry,
component oracle, or peer repositories. No observed RED is claimed until CI
returns an actual test result. Synthetic subprocess tests are not native runs.

The user's recovery checkpoint at 2026-09-05 13:17 KST remains the latest
requested calibration contract. Its twelve obligations are NOT identical to
the twelve historical IDs in PR #130. Do not substitute count equality for
semantic equivalence. Revised-contract native admission remains PENDING.

## Newly located historical native evidence

REI PR #67, commit `76f7f70d1510b268a6a06c3ae9722ef68fe0ce47`, tree
`3391af719e1939fd1d9ae55aa0ebe6f430415b80`, preserves the actual first run of
the unchanged BASS source. Read original bytes at:

- `research/rei_m2_local_native_20260905/native/PROCESS_RECEIPT.json`
- `research/rei_m2_local_native_20260905/native/native.json`
- `research/rei_m2_local_native_20260905/native/stdout.log`

Original process/native statuses are `PASS_NATIVE_CALIBRATION_ONLY` and
`PASS_NATIVE_TYPED_VIEW_CALIBRATION_ONLY`. The receipts report exit 0,
no timeout, all twelve declared checks true, source/input unchanged, and a
clean worktree. The residual arrays contain the twelve historical groups
reported as 416 exact-zero scalar entries. This session read the committed
receipt content; it did not re-execute native calculations or recompute their
SHA-256 locally, because container/Python admission returned ClientError.

Native receipt locator:
- Git blob: `f4cbd8493daa72709e96b3d7c962f4413f6e80ed`
- SHA-256 reported by the original process receipt:
  `5b28385a1e2d80b4e9281675f45c3f4e92c611864c4afdf4852b840f88c5ec33`
Process receipt Git blob: `7b0b7cf95c1771453139b7a7db93ae7894a8f55d`.
Raw stdout Git blob: `75f8effbdc2a3bad0ceb514600b9342bdc3cb76b`.

Raw stdout line 19 contains `Verbose::shdw` before `nativeBody` evaluation.
The original `messages=[]` records only the later Block[$MessageList={}]
interval. Preserve the historical PASS receipts and genuine component result;
do not call the whole invocation message-free and do not invent a physics
failure from a message-accounting failure. No retry is required merely to
reconstruct the already durable result.

## Bounded implementation target

After an observed software RED, modify only run_native.py to:

1. Derive succeeded/failed/not-evaluated counts from strict Boolean results,
   even when the declared ID set is incomplete or results are malformed.
2. Distinguish an unavailable required-ID set (not-evaluated count unknown)
   from a known twelve-check contract with no evaluated results (0/0/12).
3. Preserve failed, missing, invalid and unexpected IDs separately.
4. Reject duplicate JSON keys rather than silently choosing the last value.
5. Inspect both rendered stdout and stderr across initialization/evaluation;
   any observed Wolfram message blocks the wrapper's success. Do not hide or
   allowlist the historical Verbose warning.
6. Keep atomic exclusive publication and compare the JSON round trip against
   actual observed data, never a fixed expected twelve-pass summary.

Log scanning is a rendered-message guard, NOT proof that suppressed messages
or unrecorded partial kernel checks do not exist. Native .wls early-exit
accounting and whole-evaluation instrumentation remain a separate open slice.
OS termination or inaccessible output storage cannot be represented as an
admitted successful run. Existing output directories are never overwritten.

## Contract differences that must not be silently closed

The historical suite has package, normal/K, full raw-to-BASS Riemann, two
physical Ricci contractions, Gauss, Codazzi, mixed Ricci, matter momentum,
Hamiltonian, and two nonzero-sign witnesses. It does not separately record
all of the recovery checkpoint's metric-inverse, raw first-fourth contraction,
physical spatial Ricci/scalar and T_nn/T_ni obligations. Some are supported
indirectly; indirect implication is not a new named native execution.
The Hamiltonian check is an off-shell identity residual, not E_nn=0 on a
chosen Einstein-matter solution.

## Physics boundary and stale-plan warning

Keep X_abcd=-B_abcd for the locked all-lower views; do not negate physical
Ricci. Keep positive K and q=-h T n. With C_a=div K_a-D_a tr K,
M_a=-C_a-kappa_G q_a, kappa_G=8*pi*G/c^4.
The 2026-09-04 native-bridge plan predates the typed-view correction: its
exceptional Task 6 carrier must not be mistaken for the complete signed
momentum residual. Preserve C3 and use M3=-C3-kappa_G*q3; full exceptional
native verification remains absent.

## Verification and remaining work

The new workflow runs stdlib software tests only on this isolated branch,
with a three-minute job bound. It does not run native xAct, alter other
workflows, use a self-hosted runner, or promote physics. Record actual RED
and GREEN results separately. No complete-project percentage is meaningful
from these tests.

Next after software closure: update the native per-check journal and explicit
recovered-contract mapping, then run that separately versioned native slice
only in an admitted kernel. Public registry/consumer amendment, abstract
four-projection bridge, exceptional witness, constraint propagation, background
evolution, provider admission, science and RF04 remain withheld.

## Primary documentation consulted

- https://reference.wolfram.com/language/ref/$MessageList.html
- https://reference.wolfram.com/language/ref/message/General/shdw.html
- https://xact.es/xCoba/

SciSpace discovery did not supply an equation-level convention authority in
this session. No project coefficient was changed from literature snippets.
Connected Wolfram context/evaluator each failed HTTP 404 before kernel output.
