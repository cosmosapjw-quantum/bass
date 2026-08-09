# External symbolic/numerical oracle job

Use `bianchi_phase_r` only for a bounded verification obligation after the owner authorizes
external-repo execution. No remote writes, commits, pushes, PRs, or source edits.

## Request contract

- request/assignment ID
- BASS obligation and gate IDs
- repository URL and exact 40-hex commit
- clean worktree and submodule state
- mathematical statement, conventions, domains, branches, assumptions, canonical target
- input files and SHA-256 hashes
- exact commands, seeds, precision/tolerances, wall-time/memory/output limits
- prohibited shortcuts and independence mode
- expected stdout/stderr/result paths and receipt schema

## Return contract

Return commit/status, environment lock, exact commands, exit/timeout/signal data, complete
logs, result artifacts and hashes, assumptions actually used, residuals/error norms, and
one status: `DURABLE_VERIFIED`, `FAILED`, or `DURABLE_UNVERIFIED`.

The Work-side coordinator must independently inspect the result before it can support a
BASS gate. Formula/code lineage shared with BASS must be disclosed and may reduce the
independence classification.
