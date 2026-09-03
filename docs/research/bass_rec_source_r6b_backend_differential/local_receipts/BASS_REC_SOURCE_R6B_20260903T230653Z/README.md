# R6B parent–candidate backend differential — local receipt mirror

## Source execution

```text
local receipt
/home/cosmosapjw/Dropbox/bianchi/_runtime_receipts/
BASS_REC_SOURCE_R6B_20260903T230653Z

red parent
0a4875e5c18419a672c164eb5c849f3f4ab01571

green source
92d67dc79cf645947beb93ac01a9505ee277dabd

publication head at execution
b97b84a0351f3b43e6f34699e9aa19b1aed8afaa
```

## Observed result

The runner emitted:

```text
classification=UNRESOLVED_R6B_DIFFERENTIAL
base_backend_rc=0
green_backend_rc=0
failure_sets_identical=true
green_focused_rc=0
deterministic_golden_hashes=true
clean_worktrees=false
```

Both backend cones completed successfully:

```text
base   53 passed, 1 skipped, 29 warnings
GREEN  53 passed, 1 skipped, 29 warnings
```

The warnings on both sides are the expected
`UnverifiedNativeDevelopmentWarning` produced by the explicitly enabled
source-built native-development payload. No failed-test set exists on either
side.

The only failed top-level gate was repository cleanliness. Both detached
worktrees contained exactly the same untracked packaging artifact:

```text
?? build/
```

Accordingly, this receipt supports:

```text
PASS_BACKEND_TEST_BEHAVIOR_ON_PARENT_AND_GREEN
NO_CANDIDATE_SPECIFIC_FAILED_TEST
IDENTICAL_POST_INSTALL_BUILD_ARTIFACT
```

It does **not** rewrite the runner's machine classification. The formal stage
remains `UNRESOLVED_R6B_DIFFERENTIAL` until a minimally repaired runner either
builds outside the source worktrees or removes the known generated `build/`
directory before the final cleanliness check and reproduces the same test and
hash results.

## Deterministic identities

```text
native wheel
bf5a59534ffc9d6f9c3410aa19319f18a4a8a7a9761bcd61c5da8c8627ddf609

source payload
7f0db7e1cf7423ff6751a21ab4002ef8f13d89f788a8a746b26992abecf791e8

integrated binding
54762aa915b3fa0da847676a3d4491b8f7f2f358e48dd275fffee84ba6496093
```

## Mirror scope

This directory is a selected UTF-8 GitHub mirror of the local Dropbox receipt.
`SHA256SUMS.original.txt` preserves the hashes of the full local receipt,
including environment-install logs not duplicated here. No physical REC
source, solver wiring, grid/PSTF adapter, trusted native-payload promotion,
physical face, provider export, or `PASS_RF04` claim follows from this receipt.
