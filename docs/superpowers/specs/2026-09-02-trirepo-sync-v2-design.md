# TRI-SYNC-V2 Bootstrap-01 Design

**Program:** `BIANCHI-WOLFRAM-TRIREPO-20260830`  
**Bootstrap:** `TRI-SYNC-V2-BOOTSTRAP-01`  
**Approved:** 2026-09-02 KST  
**Scope:** policy and metadata only; no science-source ownership transfer, merge, or claim promotion.

## Problem

`bass`, `rec_bianchi`, and `rei_bianchi` share conventions and geometry, but
active branches can independently introduce formula-like objects without a
global formula identifier or a declared import/replay relationship. The
existing tri-repository policy assigns broad owners but does not mechanically
detect duplicated authority, stale imports, or control-plane drift.

## Decision

Use an asymmetric three-plane architecture:

- GitHub is authoritative for source bytes, formula registries, tests, and
  exact commit/tree identities.
- Dropbox is an append-only recovery mirror for one sync run.
- Atlassian is authoritative for approved execution ownership and decisions.

BASS owns a standard-library Python coordinator. Each repository publishes an
authority export, an import lock, and a sync pointer. The coordinator builds a
common authority registry, duplicate report, sync state, shadow-DAG proposal,
and receipt. It is read-only with respect to external services.

## Identity

Every formula namespace has a globally unique `formula_id`, sole owner,
semantic payload/hash, common convention hash, source paths, consumers, and
allowed consumer modes. A run ID is SHA-256 over canonical JSON containing:

- all three repository commit/tree bindings;
- digests of all six export/import documents;
- convention hashes;
- the approved dependency edge set;
- the bootstrap observation digest.

Git object IDs, semantic SHA-256 values, Dropbox metadata IDs, and Atlassian
content IDs remain separate identity domains.

## Duplicate classification

A consumer-side recomputation is valid only when it has
`authority_effect=NONE`, an exact `replay_of` formula ID, and an
`independence_class`. Otherwise a matching semantic hash is a
`DUPLICATE_DERIVATION_PATH`. Multiple producers or owners for one formula ID
are `DUPLICATE_AUTHORITY`.

The first bootstrap registers ownership namespaces, not every active formula.
It must therefore report the active-lineage inventory gap rather than claim a
complete deduplication pass.

## DAG behavior

The machine may regenerate a shadow DAG and propose status changes. It may not
mutate official Jira links, scientific owners, claim levels, PR states, or
Dropbox-to-Git recovery without a separate approval receipt. The existing
approved dependencies remain:

```text
rec_bianchi -> rei_bianchi
rec_bianchi -> bass
rei_bianchi -> bass
```

## Cadence

The GitHub workflow runs contract tests on relevant pushes/PRs and has a daily
03:10 KST schedule. During bootstrap, scheduled drift is informational because
formula coverage is incomplete. A later approved `SYNC-GATE-01` may enable
fail-on-drift enforcement after the complete semantic inventory is green.

## Error handling

Malformed schema/program/repository/digest/input cardinality is `BLOCKED` with
exit code 64. Valid input with detected scientific-control drift emits the full
receipt set; optional `--fail-on-drift` returns exit code 2. Missing external
credentials are `NOT_RUN`, never a cross-store PASS.

## Testing

TDD requires an initial GitHub Actions failure while the production module is
absent, followed by a green run after the minimal coordinator is added. Tests
cover deterministic hashing, binding-sensitive run IDs, duplicate owners,
authorized oracles, duplicate paths, missing/stale imports, immutable official
edges, and five-output emission.

## Publication

Three policy-child Draft PRs carry the repository-specific manifests. One
append-only Dropbox folder stores all six inputs, five generated outputs, and a
restore map. One Confluence child page and one Jira task record the same run ID;
comments on BASS-16/17/18/19 link all identities. No official dependency link
changes in this bootstrap.

## Claim boundary

```text
TRIREPO_BOOTSTRAP_AUDIT_EXECUTED
NO_COMPLETE_SOURCE_LEVEL_SEMANTIC_DEDUPLICATION
NO_AUTOMATIC_OFFICIAL_DAG_MUTATION
NO_PROVIDER_ADMISSION
NO_CROSS_REPOSITORY_COMPATIBILITY
NO_SCIENCE_VALIDITY
```
