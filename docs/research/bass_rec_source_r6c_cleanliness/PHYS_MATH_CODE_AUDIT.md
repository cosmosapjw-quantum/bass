# PHYS–MATH–CODE audit — R6C cleanliness replay

## Root cause

The R6B runner used the detached Git worktree as both:

1. the source under test; and
2. the PEP-517 package-build source directory.

`pip install ... .` consequently created the untracked path `build/` on both the RED parent and GREEN source. The backend cones and focused suite all passed, and the failure sets were empty. The dirty path was therefore symmetric harness output, but the strict cleanliness gate correctly withheld formal PASS.

## Minimality of R6C

R6C preserves the exact commits, dependency lock, native wheel, environment variables, tests, hash fixtures, and comparison logic. The only architecture change is:

```text
before: package build source = detached Git worktree
after:  package build source = exact non-Git git-archive export
```

Tests still run from the exact detached worktree. This avoids both weak alternatives:

- adding `build/` to `.gitignore`, which would hide rather than eliminate the artifact from the gate;
- blindly deleting an unexplained dirty path before inspection.

## Required receipts

R6C records:

- exact GREEN tree/source/test blobs;
- equality of `_rustcore`, `requirements.lock`, and `pyproject.toml` across parent and candidate;
- archive/extraction return codes;
- staged source blob identity;
- package installation and import logs;
- parent/GREEN backend logs and failure sets;
- focused suite result;
- two-process source and binding hashes;
- complete source-worktree status with all untracked files;
- inventory of packaging artifacts generated only in staging.

## Ranked findings

### P0

None.

### P1

Formal R6 behavior-level closeout remains withheld until the R6C replay returns clean worktrees and the same passing test/hash results.

### P2

- The source-built native wheel remains a development payload admitted through the explicit override; trusted production-wheel provenance is a separate node.
- The root package wheels built from RED and GREEN are not claimed byte-identical because their Python source differs by design.
- GitHub-hosted jobs have repeatedly failed before runner allocation, so local exact-head receipts remain the active execution lane.

### P3

Staging directories may contain `build/` or `*.egg-info`; these are inventoried as build outputs and are outside Git source identity.

## Verdict

```text
R6B_BEHAVIORAL_NONREGRESSION_SUPPORTED
R6B_FORMAL_PASS_WITHHELD
R6C_REPLAY_READY
PRODUCTION_CODE_UNCHANGED
```
