# BASS PR automatic commit/push policy

Effective 2026-08-18.

For every subsequent BASS PR-level task, the agent should perform the following without requiring a separate commit/push instruction:

1. create or reuse the PR-specific branch;
2. execute the scoped scientific/code verification gates;
3. commit completed reviewable changes and evidence;
4. push the branch normally (never force-push unless explicitly approved);
5. create the PR when it becomes reviewable, or update the existing PR automatically;
6. fetch/verify the remote branch or PR head SHA before reporting completion;
7. preserve failure evidence when a gate fails instead of silently dropping it.

## Merge boundary

Automatic commit/push **does not imply automatic merge**.

- `main` or another integration branch is merged only after explicit user approval unless the user later changes this policy.
- Failed or partially verified scientific claims must remain clearly scoped in the PR description/receipts.
- Production migration remains separately gated from research/reference PRs.

## Commit granularity

Prefer one coherent commit per independently reviewable task when the available Git interface permits it. Multiple ordinary commits inside one PR are acceptable when connector/API constraints make atomic multi-file commits impractical.
