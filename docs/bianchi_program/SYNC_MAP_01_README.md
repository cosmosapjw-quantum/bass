# SYNC-MAP-01 — Tri-repository formula path and ownership inventory

**Result:** `PASS_WITH_FINDINGS`

This stage expands the FED-00 namespace bootstrap into a bounded path-level inventory for `bass`, `rec_bianchi`, and `rei_bianchi`. It classifies formula families as authority, adapter, provider, independent oracle, formula-only snapshot, or pending implementation.

It does not copy scientific source between repositories and does not select a winner when semantic authorities conflict.

## Load-bearing finding

The BASS geometry chain is split:

```text
PR #83: ALG-01R2 -> canonical Levi-Civita connection
PR #82: ALG-01R1 -> W2/Gauss-Codazzi + spatial curvature + xCoba oracle
```

Both are verified in their own lineages, but they are not a single exact descendant chain. Durable BG-02 work must not mix their trees. The next bounded node is:

```text
SYNC-MAP-01C_GEOMETRY_LINEAGE_COMPOSITION
```

## Shared interface candidate

REC and REI require the common identities

```text
n_e = n_HII + n_HeII + 2 n_HeIII
kappa_T = sigma_T n_e
```

Wolfram gives exact zero residual between the reordered expressions, but this is only provisional algebraic equivalence. `SYNC-MAP-02` must create cross-language canonical payloads. BASS should own the typed interface schema while REC and REI retain ownership of their provider values.

## Control-plane disposition

- BASS PR #86 remains the active governance parent because it descends from the standing authorization and owns the reconciled cross-plane publication.
- BASS PR #87 and its peer lane manifests are retained as a technical donor parallel.
- No PR is closed, merged, or declared a semantic winner.

## Scope boundary

The exact all-rank photon SSOT and eleven-branch atlas remain formula-only authorities. They do not establish finite-electron-tilt collision, recombination/reionization, hierarchy truncation, line-of-sight integration, solver construction, numerical evolution, or inference.

## Claim boundary

```text
PATH_AND_OWNERSHIP_INVENTORY_ONLY
NO_AUTOMATIC_SEMANTIC_CONFLICT_WINNER
NO_PROVIDER_ADMISSION
NO_BG02_DURABLE_PROMOTION
NO_NUMERICAL_OR_SCIENCE_PROMOTION
```
