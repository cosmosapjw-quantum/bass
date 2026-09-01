# Tri-Repository Formula Authority Synchronization Design

**Date:** 2026-09-02  
**Program:** `BASS-REC-REI-FORMULA-SYNC-V1`  
**Applies to:** `cosmosapjw-quantum/bass`, `cosmosapjw-quantum/rec_bianchi`, `cosmosapjw-quantum/rei_bianchi`  
**Upstream control surfaces:** BASS Formula SSOT v2, the tri-repository Atlassian control plane, Jira BASS-17/BASS-18/BASS-19, and each repository's exact active research head.

## Goal

Prevent the three lanes from independently re-deriving or silently redefining the same formulas. A single machine-readable authority registry assigns every formula family to exactly one owner. Repository-local lane manifests then declare authority, consumer, adapter, oracle, or audit roles and pin every imported authority by exact Git commit.

The control plane also compiles current lane states into a deterministic DAG. It may automatically classify nodes as `pass`, `validated_non_durable`, `ready_to_start`, `in_progress`, `blocked`, or `stop_invalid`, but it may not automatically promote a scientific claim, export a provider, mark a pull request ready, merge code, or transition a Jira issue to Done.

## Authority partition

The three storage systems are synchronized but are not co-equal authorities.

| Domain | Authority | Allowed synchronized content |
|---|---|---|
| formulas, source, tests, exact byte identity | GitHub exact objects | registry, lane manifests, compiled DAG, receipts, code |
| workflow status, ownership, dependencies, human decisions | Atlassian | human-readable mirror, issue links, proposed transitions, claim ceiling |
| recovery and stage backup | Dropbox | versioned snapshot, restore map, backup receipt |

Conflict resolution is domain-specific:

1. GitHub wins for formula text, code, tests, commit/tree identity, and semantic manifests.
2. Atlassian wins only for Jira workflow state, assignee, and owner decisions.
3. Dropbox wins only for backup existence, file IDs, revisions, and restore locations.
4. A difference across domains is recorded as drift; no surface silently overwrites another surface.

## Formula ownership

Every formula family has one `authority_owner`. Non-owners may only use these roles:

- `consumer`: exact-pinned imported authority;
- `adapter`: representation or interface map that does not redefine the source formula;
- `oracle`: independent comparison implementation, explicitly non-authoritative;
- `audit`: residual, limit, or adversarial check.

Two authority declarations for one family are `STOP_INVALID:DUPLICATE_AUTHORITY`. An authority declaration by a lane other than the registry owner is `STOP_INVALID:OWNER_MISMATCH`. An imported authority whose pinned commit differs from the owner's declared authority commit is `STALE_IMPORT` and blocks dependent promotion.

The initial ownership partition is:

- BASS: conventions and units; Bianchi algebra and Cartan geometry; GR homogeneous background equations; temporal Jacobi/structure evolution; exact homogeneous photon Liouville and polarized hierarchy; rest and finite-tilt Thomson theorem layers; arbitrary-finite-L compiler; universal optical-depth/charge identities; coupled background assembly; observer/local-boost theorem and output adapter.
- REC: primordial H/He multilevel kinetics; line/continuum transfer; two-photon/Raman channels; directional source-face reconstruction; interpolation and provider error envelopes; recombination provider export.
- REI: late-time H/He thermochemistry; OTS event graph and ledgers; reionization opacity/current/source closures; canonical interval evolution; reionization provider export.
- BASS owns the REC/REI splice and global conservation assembly, but may only consume exact-pinned REC and REI provider exports. It may not replace provider formulas.

## Lane manifest

Each repository carries `coordination/tri_repo_sync/LANE_MANIFEST.json`. It contains:

- lane name and repository;
- exact source branch, commit, and tree;
- Atlassian issue and Dropbox root;
- owned and imported formula families;
- role, status, maturity, scope, authority commit, import pin, and evidence flags;
- blockers and claim ceiling;
- current and next DAG nodes.

Allowed maturity levels, in increasing order, are:

`idea`, `derived`, `symbolic_verified`, `durable_formula`, `implemented`, `runtime_verified`, `provider_exported`, `integrated`, `science_validated`.

A maturity label never substitutes for evidence. Promotion requirements are formula-family specific and may include `github_exact_identity`, `dropbox_backup`, `atlassian_sync`, `tests_pass`, `formal_receipt`, or `runtime_receipt`.

## Deterministic DAG compilation

The compiler reads one registry plus exactly one manifest per lane. It performs:

1. schema and uniqueness checks;
2. authority-owner and duplicate-authority checks;
3. cycle detection over formula prerequisites;
4. maturity and promotion-evidence evaluation;
5. exact import-pin drift checks;
6. downstream blocking and weakest-upstream claim-ceiling propagation;
7. generation of ready, blocked, non-durable, stale, and invalid sets;
8. generation of a proposed Atlassian mutation plan and Dropbox backup plan.

Automatic classification rules:

- conflicting authority or a dependency cycle -> `stop_invalid`;
- missing authority, explicit blocker, invalid owner state, stale required import, or unsatisfied prerequisite -> `blocked`;
- prerequisites satisfied and owner state `not_started` -> `ready_to_start`;
- derivation or implementation active below target maturity -> `in_progress`;
- target maturity reached but required persistence/evidence missing -> `validated_non_durable`;
- target maturity and all promotion requirements satisfied -> `pass`.

Scientific promotion always remains manual. The compiled DAG emits `manual_promotion_required: true` for every family.

## Synchronization cadence

- event driven: every change to a lane manifest, authority registry, or compiled DAG;
- scheduled audit: daily at 03:15 Asia/Seoul (`18:15 UTC`);
- full reconciliation: before every stage promotion, provider export, PR ready transition, merge, or downstream integration;
- manual dispatch: after a runtime recovery or authority correction.

The scheduled GitHub workflow is initially audit-only. It validates manifests, fetches the two public producer manifests, compiles the DAG, and fails on drift. Cross-repository GitHub mutation, Dropbox publication, and Atlassian publication require explicit repository secrets and remain fail-closed when unconfigured.

## Current bootstrap snapshot

The first synchronization snapshot is pinned to:

- BASS: `c35177409909b7eef0f5c99c0c61a456b5e55117`, tree `c2fa8cd3f34b46b9522479501a502d1ecd5ded6a`, Draft PR #79 lineage;
- REC: `c4bf37d7271caf651bca41b6eaab8caff436452b`, tree `445b3fbc68aaba3e17c590831bff184b2e98e86f`, Draft PR #47;
- REI: `f4eb2c893ce6449f8899ab6f02c83421fc7c7019`, tree `16d060d45ddfa401e4a5c22f9ca53cf65399ff51`, Draft PR #32.

Current scientific boundaries are preserved:

- BASS ALG-01 is durable and BG-02 is not yet a durable Git authority;
- REC remains blocked by absent source-defined 26-direction physical-face reconstruction and has no provider export;
- REI remains stopped at the standalone runtime bridge (`UNDECLARED_IMPORT: ntpath`) and has no passed first canonical interval or provider export;
- BASS integration remains blocked by REC and REI provider gates.

## Failure policy

The synchronizer is fail-closed. It never resolves formula conflicts by choosing the newest timestamp, longest document, or most advanced claim. A conflict produces an explicit receipt and blocks dependent nodes. Runtime interruptions preserve the last durable snapshot and do not inherit transcript-only results.

## Security and secrets

No access token is committed. The optional scheduled publishers read credentials only from secret environment variables. Logs must redact authorization headers and tokens. Missing secrets produce `SYNC_DESTINATION_UNCONFIGURED`, not PASS.

## Rollback

- GitHub: close the three synchronization Draft PRs and delete only their synchronization branches.
- Dropbox: delete only the versioned synchronization snapshot folder after separate confirmation.
- Atlassian: retain the audit history; mark the receipt page superseded rather than deleting scientific provenance.

## Acceptance criteria for SYNC-01

1. Test-first RED is observed before compiler implementation.
2. Compiler tests cover canonical hashing, duplicate authority, owner mismatch, stale imports, dependency blocking, non-durable blocking, cycle detection, ready-to-start classification, and manual-promotion protection.
3. All three lane manifests are committed on child branches of the exact active heads.
4. The BASS registry compiles those manifests without duplicate authority.
5. The compiled state preserves every current scientific blocker and claim ceiling.
6. GitHub readback confirms commits, trees, PR heads, and committed blobs.
7. Dropbox contains a versioned snapshot and restore map.
8. Confluence and Jira mirror the snapshot without changing scientific task status or dependency links.

## Non-goals

SYNC-01 does not derive BG-02, repair the REI runtime bridge, reconstruct the REC physical face, implement arbitrary-L kernels, change provider formulas, or integrate `htt_base`. It only prevents duplicated authority and keeps the work DAG synchronized.