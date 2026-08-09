# BASS clean-rebuild decision brief

Use this brief only after the original-runtime export attempt either fails or is impossible.
It is a decision boundary, not an approved design or implementation plan.

## Evidence that may govern a rebuild

- `docs/specs/LOWELL_BIANCHI_FINAL_CODE_AUDIT_CONTRACT_20260810.txt` is the byte-identical
  durable copy of the user-supplied primary low-ell requirements and hostile-audit
  contract. Its SHA-256 is
  `de4c4d3d467e91d3f8420b5b2748ee7294db3ca8e809df4045b2f8c2d71881f1`.
- `docs/recovery/TRANSCRIPT_TASK3_10_STATE_20260809.md` supplies future RED-test invariants
  for geometry, fluids, history, opacity, and kinetic EMT sources.
- `recovered_sources/legacy_partial/` is reference-only and must not be overlaid into a new
  production package.
- `harness/BASS_v1_background_highl_harness/` is a separate harness-only provenance lane;
  its immutable historical receipts do not validate a new solver.
- No observational NPZ/B execution is part of reconstruction.

## Design choices that must be explicit

1. Canonical namespace: historical `src/bass/...` bootstrap shape versus the interrupted
   run's `bianchi/full/...` shape, or a documented compatibility boundary between them.
2. First deliverable: minimal homogeneous background kernel versus immediate restoration
   of the five transcript-named `bianchi/full` modules.
3. Family scope per milestone: Block-1 families first or all eleven Bianchi types from the
   first release contract.
4. Relationship between low-ell and background/high-ell harnesses.
5. Numerical types, units, conventions, public immutability, provenance hashing, and error
   normalization contracts.

## Candidate routes

- **Route A — evidence-first clean rebuild (recommended):** write a new approved design,
  implement a minimal canonical background/API slice, then rebuild transcript modules in
  dependency order under observed RED, fresh GREEN, cumulative regression, and independent
  review. Lowest provenance risk; longest route.
- **Route B — transcript-shaped compatibility reconstruction:** recreate `bianchi/full`
  interfaces directly from the surviving invariants. Faster, but Task 3–5 signatures must
  be newly designed and explicitly labeled rather than called recovered.
- **Route C — legacy overlay transplant:** rejected as a canonical route because the
  overlay is incomplete and its original baseline and execution receipts are absent.

Approval of Route A or B starts a fresh brainstorming/design gate in the current thread.
Until then, no production solver file should be created.
