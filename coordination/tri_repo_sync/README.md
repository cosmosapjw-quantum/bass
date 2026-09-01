# BASS / REC / REI formula synchronization control plane

This directory prevents `bass`, `rec_bianchi`, and `rei_bianchi` from independently owning the same derivation.

## Authority model

- GitHub exact objects own formula text, source, tests, and semantic identity.
- Atlassian owns workflow state, dependency links, ownership decisions, and human approval records.
- Dropbox owns versioned recovery snapshots and restore receipts.

The surfaces are synchronized but are not interchangeable. Drift is reported; no newest-wins merge is allowed.

## Files

- `FORMULA_FAMILY_REGISTRY.json`: unique formula-family owners and prerequisites.
- `LANE_MANIFEST.json`: BASS lane state and exact upstream pins.
- `fixtures/REC_LANE_MANIFEST.json`: exact REC state used for the initial SYNC-01 compilation.
- `fixtures/REI_LANE_MANIFEST.json`: exact REI state used for the initial SYNC-01 compilation.
- `compile-dag.mjs`: deterministic fail-closed DAG compiler.
- `CURRENT_COMPILED_DAG.json`: generated current snapshot after all three live manifests are published.
- `SYNC_POLICY.json`: cadence, mutation limits, and promotion firewall.
- `tests/`: compiler and current-snapshot contracts.
- `schemas/`: public JSON schemas.

## Commands

```bash
node --test coordination/tri_repo_sync/tests/*.test.mjs

node coordination/tri_repo_sync/compile-dag.mjs \
  --registry coordination/tri_repo_sync/FORMULA_FAMILY_REGISTRY.json \
  --manifest coordination/tri_repo_sync/LANE_MANIFEST.json \
  --manifest coordination/tri_repo_sync/fixtures/REC_LANE_MANIFEST.json \
  --manifest coordination/tri_repo_sync/fixtures/REI_LANE_MANIFEST.json \
  --output /tmp/COMPILED_DAG.json
```

## State meanings

- `pass`: target maturity and all promotion evidence are present.
- `validated_non_durable`: the result may be mathematically or numerically checked, but required persistence or independent receipts are absent.
- `ready_to_start`: prerequisites pass and the owner has not started the node.
- `in_progress`: valid work exists below the target maturity.
- `blocked`: a prerequisite, explicit blocker, provider gate, or durability gate is unsatisfied.
- `stop_invalid`: duplicate authority, owner mismatch, cycle, or invalid owner state.

## Hard firewall

The compiler never automatically performs any of the following:

```text
scientific PASS
provider export
PR ready transition
merge
Jira Done transition
```

A scheduled workflow may detect drift and publish a receipt. It may not erase or upgrade the underlying scientific claim boundary.