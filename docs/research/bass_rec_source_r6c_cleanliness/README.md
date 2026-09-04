# R6C — clean source-worktree differential replay

## Purpose

Close the sole unresolved **behavior-level** R6B gate without weakening the repository-cleanliness requirement.

The exact R6B receipt established identical backend behavior on the coherent RED parent and R6 GREEN source:

```text
red parent      0a4875e5c18419a672c164eb5c849f3f4ab01571
green source    92d67dc79cf645947beb93ac01a9505ee277dabd
base backend    rc=0
green backend   rc=0
focused suite   rc=0
golden hashes   PASS
```

The formal runner nevertheless returned `UNRESOLVED_R6B_DIFFERENTIAL` because both detached source worktrees contained the same untracked path:

```text
?? build/
```

Dropbox readback identifies the origin precisely. In both environments, `pip install ... .` processed the Git worktree as a PEP-517 source tree, built a `bianchi_solver` wheel, and left `build/` behind. No candidate-specific dirty path or failed test existed.

## Minimal repair

R6C does not ignore `build/`, add it to `.gitignore`, or delete an unexplained dirty path. Instead it separates the two roles that R6B conflated:

1. exact detached Git worktrees are used for identity checks and tests;
2. exact `git archive` exports are used as non-Git packaging/build staging areas.

The root Python wheel is built and installed from the staging export. Therefore packaging artifacts may exist in staging, but both source worktrees must remain completely clean under:

```text
git status --porcelain=v1 --untracked-files=all
```

## Preserved differential contract

R6C retains all R6B controls:

- same Python 3.12 dependency lock;
- same source-built native wheel, SHA-256 `bf5a59534ffc9d6f9c3410aa19319f18a4a8a7a9761bcd61c5da8c8627ddf609`;
- same `BASS_ALLOW_UNVERIFIED_NATIVE_DEV=1` source-build policy;
- same deterministic thread settings;
- same backend policy/integration/packaging cone;
- same 21 focused R5+R6 tests;
- same two-process source and binding hashes;
- exact source/tree/test blob checks;
- no trusted-native, physical-source, adapter, face, provider, or RF04 promotion.

## Expected PASS

```text
classification=PASS_BASS_REC_SOURCE_R6C_CLEAN_BACKEND_NONREGRESSION
red_backend_rc=0
green_backend_rc=0
failure_sets_identical=true
green_focused_rc=0
deterministic_golden_hashes=true
clean_worktrees=true
build_location=NON_GIT_STAGING_DIRECTORIES
```

## Cross-repository authority gate

R6C closes only the BASS **development-payload behavior lane**. The REC coordination authority remains Draft PR `rec_bianchi#55`, whose exact critical-path gate is:

```text
PASS_R5D_TRUSTED_RF00_PAYLOAD_PROVENANCE_AND_BACKEND_GATE
```

No matching executed R5D receipt is currently present in the synchronized Dropbox runtime-receipt tree. Therefore an R6C PASS must not be promoted into trusted-native or physical-source authority.

## Next-node policy

After an R6C PASS:

```text
BASS behavior-level R6 closeout     COMPLETE
trusted-native authority gate       STILL BLOCKED ON REC R5D
```

The source-adapter RED node may open only after **both** gates are satisfied:

```text
PASS_BASS_REC_SOURCE_R6C_CLEAN_BACKEND_NONREGRESSION
AND
PASS_R5D_TRUSTED_RF00_PAYLOAD_PROVENANCE_AND_BACKEND_GATE
  -> BASS_REC_SOURCE_R7_FULL_GRID_AND_SPECTRAL_PSTF_ADAPTER_TDD_RED
```

R7 remains test-only when opened. It must not wire physical REC data into a production solver.
