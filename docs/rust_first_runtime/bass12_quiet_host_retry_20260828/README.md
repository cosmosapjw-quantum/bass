# BASS-12 retry package

## Active generation

Use `r2_target_derived/`. It repairs the observed false blocker in R1 by deriving
the benchmark-harness identity from the immutable target Git object rather than
a stale hand-written checksum.

## Historical generation

The original ZIP, split archive, sidecar, and R1 handoff are preserved for
provenance. They must not be executed for the next retry.

## Scientific blocking policy

- Candidate source/test and frozen benchmark input/output remain hard-bound.
- A target harness disagreement is blocking only when baseline/candidate bytes
  differ from the target object.
- A retired plan checksum mismatch is nonblocking provenance metadata.
- Historical native binary hashes are record-only when both paired populations
  use one attributable environment and frozen scientific digests pass.
- Actual host contention can still block a fair performance measurement because
  Git worktrees do not isolate CPU, memory bandwidth, I/O, or the scheduler.
