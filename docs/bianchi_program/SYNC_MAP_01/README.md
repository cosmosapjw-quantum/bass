# SYNC-MAP-01 — Active-lineage formula-like path inventory

**Program:** `BIANCHI-WOLFRAM-TRIREPO-20260830`  
**Parent sync run:** `b759e046500c593ece5bdc43199b721ac720006da62c8b8bfc549175f8a5798e`  
**Execution owner:** `BASS-24`  
**Control parent:** BASS Draft PR #86 at `ea6a17d759ca55d6cfbbb7b64924be296fe6ea84`  
**Stage boundary:** path-level inventory only; semantic equivalence is deferred to `SYNC-MAP-02`.

## Purpose

This stage inventories formula sources, schemas, adapters, providers, generated
sources, receipts and independent oracles on the exact active scientific
lineages of `bass`, `rec_bianchi` and `rei_bianchi`. It prevents a later
semantic scan from silently comparing a stale or superseded branch.

## Exact lineages

```text
bass
PR #83
c787e6c51608568fcb60d52f010235f8cb2c1076
3619744e9ba2b0633737b244cb18310ec89047c8

rec_bianchi
PR #47
c4bf37d7271caf651bca41b6eaab8caff436452b
445b3fbc68aaba3e17c590831bff184b2e98e86f

rei_bianchi
PR #32
f4eb2c893ce6449f8899ab6f02c83421fc7c7019
16d060d45ddfa401e4a5c22f9ca53cf65399ff51
```

## Classification vocabulary

```text
AUTHORITATIVE_DERIVATION
AUTHORITATIVE_SCHEMA
AUTHORITATIVE_PROVIDER
ADAPTER_SPECIALIZATION
INDEPENDENT_ORACLE
OWNED_EXTENSION
RUNTIME_BRIDGE
PROVENANCE_ONLY
SUPPORT_ONLY
MIXED_OWNERSHIP_REQUIRES_SPLIT
```

A mixed path must retain every candidate owner, set `split_required=true`, and
claim no authority. An independent oracle must have `authority_effect=NONE`
and at least one provisional `replay_of_candidates` target.

## Key preliminary findings

1. BASS already contains the common convention, Bianchi structure-constant,
   Jacobi, Cartan, O(3) covariance and Levi-Civita connection authorities.
2. REC's `background/characteristics.py`, directional-face admission and its
   Wolfram frame/face verifier combine BASS-owned frame/characteristic physics
   with REC-owned hydrogen-frame boundary and event semantics. They require a
   semantic split or explicit imported formula adapters.
3. REI's `bass_integration_substrate.py` combines the BASS matter-source
   envelope/custody with REI-produced source values and must be split at the
   interface contract.
4. REC's Wolfram/Sage/Lean/Rocq files and REI's Wolfram verifier are preserved
   as independent oracles only. They do not become additional formula owners.
5. The REI runtime-bridge and host-context packages are implementation and
   capability paths, not formula authority. Their current `UNDECLARED_IMPORT:
   ntpath` stop is retained.

## Files

```text
TRIREPO_PATH_INVENTORY_SOURCE.json   reviewed source inventory
TRIREPO_PATH_INVENTORY.json          deterministic validated output
CANONICAL_IDENTITY_PAYLOAD.json      compact identity payload
SYNC_MAP_01_TDD_RED_RECEIPT.json     genuine missing-coordinator RED
SYNC_MAP_01_SCISPACE_METHOD_LOCK.md  methodology-only literature lock
SYNC_MAP_01_WOLFRAM_RECEIPT.json     independent cross-language hash check
SYNC_MAP_01_PUBLICATION_RECEIPT.json GitHub/Dropbox/Atlassian closeout
```

## Run locally

```bash
python scripts/trirepo_formula_inventory.py \
  --input docs/bianchi_program/SYNC_MAP_01/TRIREPO_PATH_INVENTORY_SOURCE.json \
  --output docs/bianchi_program/SYNC_MAP_01/TRIREPO_PATH_INVENTORY.json \
  --canonical-payload docs/bianchi_program/SYNC_MAP_01/CANONICAL_IDENTITY_PAYLOAD.json
python -m unittest -v tests/test_trirepo_formula_inventory.py
```

## Withheld claims

```text
NO_EQUATIONIR_SEMANTIC_EQUIVALENCE
NO_HISTORICAL_ALL_BRANCH_SCAN
NO_DUPLICATE_DERIVATION_PATH_CLOSURE
NO_AUTOMATIC_OFFICIAL_DAG_MUTATION
NO_PROVIDER_ADMISSION
NO_CROSS_REPOSITORY_COMPATIBILITY
NO_NUMERICAL_PARITY
NO_SCIENCE_PROMOTION
```
