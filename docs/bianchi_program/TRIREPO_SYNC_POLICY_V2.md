# Tri-Repository Synchronization Control Plane v2

- Program: `BIANCHI-WOLFRAM-TRIREPO-20260830`
- Bootstrap: `TRI-SYNC-V2-BOOTSTRAP-01`
- Coordinator owner: `bass`
- State: `BOOTSTRAP / PROPOSAL_ONLY / NO_SCIENCE_PROMOTION`
- Parent policy PRs: BASS #68, REC #44, REI #21
- Jira epic: `BASS-16`
- Repository owners: `BASS-17`, `BASS-19`, `BASS-18`

## Purpose

This control plane prevents `bass`, `rec_bianchi`, and `rei_bianchi` from
silently becoming competing authorities for the same derivation. It adds a
machine-readable ownership registry, exact import locks, duplicate-path
classification, periodic reconciliation, and a shadow DAG. It does not move
scientific source between repositories and does not merge or promote any
current Draft/HOLD branch.

## Systems of record

The three storage planes are intentionally asymmetric.

1. **GitHub owns bytes and scientific evidence.** Source, exact commit/tree,
   semantic registries, tests, receipts, PR review, and provider artifacts are
   identified here.
2. **Dropbox owns append-only recovery packets.** It mirrors source manifests,
   sync outputs, and restore instructions. Dropbox content never mutates a Git
   branch automatically.
3. **Atlassian owns the approved execution DAG and decisions.** Jira and
   Confluence store owners, blockers, next nodes, supersession, and links to
   GitHub/Dropbox identities. They are not a formula-byte authority.

No two planes are treated as symmetric writable replicas. A recovery from
Dropbox requires a separately reviewed `RECOVERY_INTAKE` branch and Draft PR.

## Ownership table

| Domain | Sole owner | Consumers |
| --- | --- | --- |
| metric, orientation, Riemann, tetrad, screen, units, photon-direction conventions | `bass` | REC, REI |
| Bianchi algebra, connection, curvature, background Einstein equations | `bass` | REC, REI |
| matter-source envelope `{Omega,q_a,Pi_ab,Q_energy,Q_momentum}` | `bass` | REC, REI |
| primordial recombination history | `rec_bianchi` | BASS, REI |
| atomic-rate bundle shared with late thermochemistry | `rec_bianchi` | REI |
| astrophysical reionization, thermochemistry, late opacity | `rei_bianchi` | BASS |
| REC/REI overlap rule and coupled fixed-point ledger | `bass` | REC, REI provide inputs only |
| final transport and likelihood-ready mean/operator output | `bass` | HTT consumes |

This bootstrap records namespace ownership only. Every active formula,
adapter, provider field, and independent oracle must be mapped in the next
semantic-inventory node before source-level deduplication can pass.

## Cross-repository classification

Every local formula-like object must be one of:

```text
AUTHORITATIVE_DERIVATION
AUTHORIZED_REPLAY
INDEPENDENT_ORACLE
ADAPTER_SPECIALIZATION
OWNED_EXTENSION
DUPLICATE_AUTHORITY
```

An independent recomputation is allowed only when it declares:

```json
{
  "authority_effect": "NONE",
  "replay_of": "<exact global formula_id>",
  "independence_class": "COMPONENT_ORACLE"
}
```

The same semantic hash without such a declaration is
`DUPLICATE_DERIVATION_PATH`. More than one owner of one `formula_id` is
`DUPLICATE_AUTHORITY`.

## Machine files

Each repository publishes:

```text
docs/bianchi_program/TRIREPO_AUTHORITY_EXPORT.json
docs/bianchi_program/TRIREPO_IMPORT_LOCK.json
docs/bianchi_program/TRIREPO_SYNC_POINTER.json
```

BASS runs `scripts/trirepo_sync_audit.py` and emits:

```text
TRIREPO_AUTHORITY_REGISTRY.json
TRIREPO_SYNC_STATE.json
TRIREPO_DUPLICATE_REPORT.json
TRIREPO_DAG_PROPOSAL.json
TRIREPO_SYNC_RECEIPT.json
```

The `sync_run_id` is the SHA-256 of canonical JSON containing all three
repository commit/tree bindings, export/import document digests, convention
hashes, approved edge set, and observation digest.

## Fail-closed status vocabulary

```text
IN_SYNC
BOOTSTRAP_PARTIAL
DRIFT_DETECTED
STALE_UPSTREAM
STALE_UPSTREAM_IDENTITY
MISSING_IMPORT_FORMULA
DUPLICATE_AUTHORITY
DUPLICATE_DERIVATION_PATH
CONVENTION_DRIFT
BLOCKED_INPUT_IDENTITY
BACKUP_INCOMPLETE
CONTROL_PLANE_DRIFT
```

`BLOCKED`, `FAIL`, and `NOT_RUN` retain their meanings and are never converted
into one another for presentation.

## DAG policy

The machine shadow DAG is regenerated on every audit. Bootstrap output may:

- propose nodes and edges;
- mark consumer nodes stale or blocked;
- add comments and status receipts;
- open Draft synchronization PRs.

It may not automatically:

- alter official Jira `Blocks` links;
- change scientific ownership;
- promote a claim level;
- merge or close a PR;
- force-push;
- restore Dropbox content into GitHub;
- relabel a scientific failure.

Official DAG mutation requires an explicit approval receipt.

## Cadence

- PR/push: contract and impact audit.
- Daily at 03:10 KST: metadata reconciliation.
- Weekly Sunday at 04:00 KST: full semantic inventory and restore spot-check,
  once the complete-inventory baseline exists.
- Before merge or claim promotion: mandatory full reconciliation.

The bootstrap scheduled job remains informational while coverage is
`BOOTSTRAP_NAMESPACE_ONLY`. Drift-failing enforcement starts only after
`SYNC-GATE-01` is approved and the active source inventory is complete.

## Current expected outcome

The first run is expected to report `DRIFT_DETECTED`, not because a formula is
known to be wrong, but because the active BASS, REC, and REI source lineages are
not yet enumerated formula by formula. That result creates the next executable
nodes without changing the official Jira dependencies:

```text
REC -> REI
REC -> BASS
REI -> BASS
```

## Claim boundary

```text
TRIREPO_SYNC_COORDINATOR_CONTRACT_ONLY
NO_COMPLETE_SOURCE_LEVEL_DEDUPLICATION
NO_AUTOMATIC_OFFICIAL_DAG_MUTATION
NO_PROVIDER_ADMISSION
NO_CROSS_REPOSITORY_COMPATIBILITY
NO_NUMERICAL_PARITY
NO_SCIENCE_VALIDITY
NO_RF04_OR_REC_OR_REI_PROMOTION
```
