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
## 2026-11-01 REI IGM mission-tether amendment (preserves the rules above)

Before automatically creating the next research PR, classify its **science owner, DAG and direct physical consumer** using [REI IGM mission realignment](REI_IGM_MISSION_REALIGNMENT_20261101.md) and the [typed mission DAG](REI_IGM_MISSION_DAG_20261101.json). "Next loop" alone is **not** authorization to keep chasing the latest auxiliary CE1 PR. Default to the earliest genuinely incomplete REI IGM critical-path physics; explicit user-directed side exploration remains allowed and source-conditional.

Every PR reports `DAG_OWNER`, `CANONICAL_DELTA`, `PHYSICAL_DELIVERABLE`, `SOURCE_OR_CLOCK_EQUIVALENCE`, `CONSUMER` and `CLAIM_CEILING` succinctly in its existing description. **The number of scoped R/C stages, green CI, plots, new rows, uploaded ZIPs or repeated same-author reviews never upgrades a canonical science node.** Reuse one durable checkpoint where adequate; per-stage evidence status can point to it without per-stage binary duplication.

If two consecutive auxiliary PRs produce no canonical delta, the next unqualified task defaults to central REI or an owner-matched BASS→REI bridge, after one concise mission check. This is not a ban on explicit exploratory science or a new physical acceptance gate. Source, merge, force-push, production and original scientific gate protections above remain unchanged. Audit historical failures without relabeling them.
