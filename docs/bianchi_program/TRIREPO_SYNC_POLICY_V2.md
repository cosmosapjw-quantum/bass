# TRI-SYNC-V2 — tri-repository authority and DAG synchronization policy

- Program: `BIANCHI-WOLFRAM-TRIREPO-20260830`
- Change: `TRI-SYNC-V2 BOOTSTRAP-01`
- Schema: `2.0.0`
- Sync run: `72fa2eabd32ab5d6ce2cbdb7633375d71ebce93c543ab562162d6853bd54e69f`
- State: `PROPOSAL_ONLY / NO_SCIENCE_PROMOTION`

This policy turns the existing static tri-repository declaration into a machine-auditable control plane. It does not move scientific ownership, merge any research branch, or promote any formula or provider claim.

## Single-writer authorities

- GitHub is the byte, source, review and scientific-evidence authority.
- Dropbox is append-only reconstruction and disaster-recovery storage.
- Atlassian is the approved execution DAG, ownership, blocker and decision authority.

These systems exchange receipts and identifiers; they are not symmetric writable replicas. Dropbox never writes directly into a scientific branch. Atlassian never becomes formula-byte authority. Recovery from Dropbox must enter GitHub through a separate `RECOVERY_INTAKE` Draft PR.

## Repository ownership

- `bass`: shared conventions, Bianchi algebra and geometry, background evolution, Einstein–Boltzmann orchestration, REC/REI splice, fixed-point ledger and final observables.
- `rec_bianchi`: primordial recombination microphysics and immutable `RecombinationHistory` provider artifacts.
- `rei_bianchi`: astrophysical reionization, thermochemistry, opacity and `MatterSource` provider artifacts.

The consumer of a formula may perform an independent oracle or adapter specialization, but it must declare `replay_of`, `authority_mode`, the producer commit and semantic hash. A second undeclared authority for the same semantic formula is a hard structural failure.

## Formula modes

Allowed modes are:

- `AUTHORITATIVE_DERIVATION`
- `PINNED_IMPORT`
- `AUTHORIZED_REPLAY`
- `INDEPENDENT_ORACLE`
- `ADAPTER_SPECIALIZATION`
- `OWNED_EXTENSION`

`DUPLICATE_AUTHORITY` is a failure classification, not an allowed mode.

## Machine products

Each repository publishes:

- `TRIREPO_AUTHORITY_EXPORT.json`
- `TRIREPO_IMPORT_LOCK.json`
- `TRIREPO_SYNC_POINTER.json` where applicable

BASS additionally publishes:

- `TRIREPO_AUTHORITY_REGISTRY.json`
- `TRIREPO_SYNC_STATE.json`
- `TRIREPO_DAG_PROPOSAL.json`
- generated duplicate, DAG and sync receipts

The common `sync_run_id` is the SHA-256 of the three policy-head identities and schema/version seed. Every GitHub, Dropbox and Atlassian receipt for one run must carry the same value.

## Automatic audit

The read-only coordinator performs:

1. schema and required-key validation;
2. unique formula-owner validation;
3. semantic-hash duplicate detection;
4. import commit/hash/convention comparison;
5. dependency and provider readiness classification;
6. shadow-DAG generation;
7. control-plane drift detection.

Structural errors fail the workflow. Scientific blockers such as an unpublished REC provider remain explicit `BLOCKED_DEPENDENCY` states but do not corrupt a structurally valid control-plane run.

## Cadence

- every PR/push touching tri-repo manifests: structural audit;
- daily at 03:10 KST: metadata reconciliation;
- weekly Sunday at 04:00 KST: full semantic and restore audit;
- before merge or claim promotion: mandatory full three-plane reconciliation.

Scheduled GitHub execution becomes active only after the workflow reaches the repository default branch. Until then, the workflow is Draft-PR evidence only.

## Automatic DAG policy

The coordinator may automatically generate a shadow DAG and comments. It may not automatically:

- change scientific ownership;
- delete or reverse official Jira `Blocks` links;
- promote a claim level;
- merge or close a PR;
- force-push a branch;
- overwrite historical Dropbox packets;
- change `FAIL` to `BLOCKED` or the reverse.

Official Jira edge mutation requires an explicit approval receipt. This bootstrap creates proposal-only state and preserves the existing `REC -> REI`, `REC -> BASS`, and `REI -> BASS` edges.

## Status vocabulary

Structural and dependency states are kept distinct:

- `IN_SYNC`
- `STALE_UPSTREAM`
- `MISSING_IMPORT_LOCK`
- `DUPLICATE_AUTHORITY`
- `DUPLICATE_DERIVATION_PATH`
- `BLOCKED_DEPENDENCY`
- `BLOCKED_INPUT_IDENTITY`
- `BACKUP_INCOMPLETE`
- `CONTROL_PLANE_DRIFT`
- `READY_FOR_ADAPTER_REVIEW`

## Claim boundary

This bootstrap authorizes the synchronization schemas, read-only auditor, shadow-DAG proposal, Draft PRs, Dropbox packet and Atlassian control-plane records only. It does not authorize REC export, REI splice, BASS consumption, numerical parity, cross-repository compatibility, scientific validity or RF04 promotion.
