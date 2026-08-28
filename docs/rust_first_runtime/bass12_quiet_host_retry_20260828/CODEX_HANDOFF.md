# Codex handoff — BASS-12R2 remotely materialized execution package

The prior `BLOCKED_BY_MISSING_EXECUTION_PACKAGE` was a transport failure: the
R2 policy files were present on GitHub, but the 17,464-byte executable ZIP was
only attached to the originating ChatGPT session. It was not reachable from the
local Codex host.

The exact ZIP is now stored on this plan branch as eight content-addressed
base64 parts. Do **not** ask the user to copy the ChatGPT attachment into
`~/bass`, and do not execute the retired R1 package.

## Materialize from the remote plan branch

```bash
set -euo pipefail
cd ~/bass
git fetch origin agent/plans/bass12-quiet-host-retry-20260828-r1
PLAN_WT="$(mktemp -d /tmp/bass12-r2-plan.XXXXXX)"
rmdir "$PLAN_WT"
git worktree add --detach "$PLAN_WT" \
  origin/agent/plans/bass12-quiet-host-retry-20260828-r1
TRANSPORT="$PLAN_WT/docs/rust_first_runtime/bass12_quiet_host_retry_20260828/execution_package"
"$TRANSPORT/RECONSTRUCT_AND_VERIFY.sh" /tmp/bass12-r2-materialized
```

Require all three outcomes:

```text
PASS_BASS12_TARGET_DERIVED_RETRY_R2
8 tests / OK
PASS_BASS12_REMOTE_EXECUTION_PACKAGE_TRANSPORT
```

Then execute exactly:

```text
/tmp/bass12-r2-materialized/
BASS12_TARGET_DERIVED_HARNESS_RETRY_R2_20260828/CODEX_HANDOFF.md
```

Resume from the package gate. Do not recreate the old BASS-12R1 contract. Do
not create another plan, audit, review, or transport package. The next objective
transition is `NOT_RUN -> quiet-host preflight -> paired timing if authorized`.

Candidate B, PR #23, PR #36, Jira, RF-02C, and `main` remain read-only. Do not
copy the ZIP into the canonical checkout; keep materialized bytes under `/tmp`.
