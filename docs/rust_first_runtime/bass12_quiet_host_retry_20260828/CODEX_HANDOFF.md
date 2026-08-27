# Codex handoff — BASS-12R1 quiet-host retry

Repository: `~/bass`

Fetch this exact plan branch:

```text
agent/plans/bass12-quiet-host-retry-20260828-r1
```

The package root is:

```text
docs/rust_first_runtime/bass12_quiet_host_retry_20260828/
```

Materialize and verify it in a new temporary directory:

```bash
set -euo pipefail
cd ~/bass
git fetch origin agent/plans/bass12-quiet-host-retry-20260828-r1
PLAN_WT="$(mktemp -d /tmp/bass12-retry-plan.XXXXXX)"
rmdir "$PLAN_WT"
git worktree add --detach "$PLAN_WT" \
  origin/agent/plans/bass12-quiet-host-retry-20260828-r1
cd "$PLAN_WT/docs/rust_first_runtime/bass12_quiet_host_retry_20260828"
./UNPACK_AND_VERIFY.sh /tmp/bass12-retry-materialized
```

Require both markers:

```text
PASS_BASS12_QUIET_HOST_RETRY_HANDOFF
PASS_BASS12_QUIET_HOST_RETRY_GITHUB_PACKAGE
```

Then read and execute exactly:

```text
/tmp/bass12-retry-materialized/
BASS12_QUIET_HOST_RETRY_HANDOFF_20260828/CODEX_HANDOFF.md
```

Execute only work unit `BASS-12R1`.

This is a local-only measurement retry. Do not commit, push, create or update a
PR, merge, tag, mutate RF-02C, update Jira/Confluence, start BASS-13, or tune
Candidate B. Do not kill or renice unrelated processes. If the two-snapshot
quiet-host gate fails, timing is `NOT_RUN` and Candidate B is not rejected.

Stop immediately after exactly one of:

```text
ACCEPTED_LEGACY_CANDIDATE_FOR_RF02C_ADOPTION_REVIEW
REJECTED_LEGACY_CANDIDATE
BLOCKED_HOST_OR_ENVIRONMENT
```
