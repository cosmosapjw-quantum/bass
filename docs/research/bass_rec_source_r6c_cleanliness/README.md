# R6C — clean source-worktree differential replay

## Final result

The exact local R6C replay completed successfully:

```text
classification=PASS_BASS_REC_SOURCE_R6C_CLEAN_BACKEND_NONREGRESSION
red parent      0a4875e5c18419a672c164eb5c849f3f4ab01571
green source    92d67dc79cf645947beb93ac01a9505ee277dabd
red backend     rc=0
green backend   rc=0
focused suite   21/21 PASS
golden hashes   PASS
clean worktrees true
build location  NON_GIT_STAGING_DIRECTORIES
```

The complete local receipt is stored in Dropbox at:

```text
/bianchi/_runtime_receipts/BASS_REC_SOURCE_R6C_20260904T012030Z
```

A selected UTF-8 mirror and the original receipt SHA-256 ledger are committed under:

```text
docs/research/bass_rec_source_r6c_cleanliness/
  local_receipts/BASS_REC_SOURCE_R6C_20260904T012030Z/
```

## What R6C closed

The preceding R6B run had already shown identical backend behavior on the coherent RED parent and R6 GREEN source, but both detached source worktrees contained the same generated path:

```text
?? build/
```

R6C separated source identity from package-build workspace:

1. exact detached Git worktrees were used for identity checks and tests;
2. exact `git archive` exports were used for non-Git PEP-517 staging.

The replay preserved the same Python 3.12 lock, source-built native wheel, development-payload policy, deterministic thread settings, backend cone, focused tests, source hashes, and binding hashes. Both source worktrees remained completely clean under:

```text
git status --porcelain=v1 --untracked-files=all
```

Packaging artifacts were observed only in the staging exports:

```text
stage-red/build
stage-red/bianchi_solver.egg-info
stage-green/build
stage-green/bianchi_solver.egg-info
```

## Behavioral scope

Both backend cones reported:

```text
53 passed, 1 skipped, 29 warnings
```

The warnings were the expected `UnverifiedNativeDevelopmentWarning` records because this lane intentionally used a source-built wheel with:

```text
BASS_ALLOW_UNVERIFIED_NATIVE_DEV=1
```

Therefore R6C establishes behavior-level parent/GREEN nonregression and clean source-worktree execution. It does not establish trusted production-native provenance.

## Cross-repository authority gate

The current REC authority gate is Draft PR `rec_bianchi#55` at:

```text
head
9c143a846dd43caea6b79c1fb83c5170c41c23b1

required local classification
PASS_R5D_TRUSTED_RF00_PAYLOAD_PROVENANCE_AND_BACKEND_GATE
```

Its v2 handoff targets the current R6 GREEN source, keeps the development override unset, verifies the admitted RF04 wheel and installed shared-object bytes, runs all 21 focused tests and the backend cone, and requires a clean source worktree. Its static handoff workflow passed at run `33827180260`; the actual local trusted-payload execution remains outstanding.

## R7 opening policy

R7 may open only after the conjunction:

```text
PASS_BASS_REC_SOURCE_R6C_CLEAN_BACKEND_NONREGRESSION
AND
PASS_R5D_TRUSTED_RF00_PAYLOAD_PROVENANCE_AND_BACKEND_GATE
  -> BASS_REC_SOURCE_R7_FULL_GRID_AND_SPECTRAL_PSTF_ADAPTER_TDD_RED
```

R7 remains test-only when opened. Neither R6C nor R5D by itself authorizes physical REC source wiring, grid/PSTF numerical parity, a physical directional face, provider export, `PASS_REC_PHYSICAL_SPLIT`, or `PASS_RF04`.
