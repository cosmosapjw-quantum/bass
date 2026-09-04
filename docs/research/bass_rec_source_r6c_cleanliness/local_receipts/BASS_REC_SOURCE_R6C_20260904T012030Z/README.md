# R6C exact local cleanliness replay — receipt mirror

## Execution identity

```text
local receipt
/home/cosmosapjw/Dropbox/bianchi/_runtime_receipts/
BASS_REC_SOURCE_R6C_20260904T012030Z

RED parent
0a4875e5c18419a672c164eb5c849f3f4ab01571

R6 GREEN source
92d67dc79cf645947beb93ac01a9505ee277dabd

publication head at execution
3f605360eae96a7fbe5dd9c31ec510c5d56e255b
```

## Observed result

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

The backend cone completed on both sides with:

```text
53 passed, 1 skipped, 29 warnings
```

The warnings are the expected development-payload warnings because R6C is a
behavior-level comparison under `BASS_ALLOW_UNVERIFIED_NATIVE_DEV=1`. They do
not establish trusted production-native provenance.

The source worktrees were empty under `git status --porcelain=v1
--untracked-files=all`. The packaging artifacts were generated only in the
exact non-Git archive stages:

```text
stage-red/build
stage-red/bianchi_solver.egg-info
stage-green/build
stage-green/bianchi_solver.egg-info
```

## Deterministic identities

```text
source payload
7f0db7e1cf7423ff6751a21ab4002ef8f13d89f788a8a746b26992abecf791e8

integrated moment-map binding
54762aa915b3fa0da847676a3d4491b8f7f2f358e48dd275fffee84ba6496093
```

## Claim boundary

This closes the BASS R6 behavior-level nonregression and cleanliness gate. It
does not establish trusted production-native provenance, physical REC source
integration, grid/PSTF adapters or numerical parity, a physical directional
face, provider export, `PASS_REC_PHYSICAL_SPLIT`, or `PASS_RF04`.

The next critical authority gate remains the REC-owned R5D trusted RF-00
payload replay. R7 may open only after both R6C and R5D pass.
