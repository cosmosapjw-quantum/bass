# SYNC-MAP-01R1 SciSpace provenance methodology lock

## Search question

Which research-software provenance models distinguish prospective workflow
specifications from retrospective execution traces and support exact source
lineage, reusable research objects, and cross-repository reproducibility?

## Methodological result

The SciSpace search surfaced a consistent provenance architecture across work
on prospective/retrospective workflow provenance, TavernaProv/ProvONE-style
workflow descriptions, CWLProv research objects, hybrid provenance capture,
and reusable research-object packaging.

The common methodological lessons adopted here are:

1. A prospective workflow or DAG is not a retrospective record of a completed
   derivation or execution.
2. A summary provenance graph must retain locators into the detailed source and
   execution evidence; it cannot replace those objects.
3. Reuse, specialization, adapter execution, and independent reimplementation
   need distinct provenance relations.
4. A reusable research object should bind source, inputs, outputs, environment,
   and execution receipts without collapsing them into one status label.
5. Cross-system interoperability requires stable identifiers and explicit
   mappings rather than prose similarity.

Representative search results included work by Lim et al. on prospective and
retrospective scientific-workflow provenance, Soiland-Reyes et al. on
TavernaProv, Prabhune et al. on P-PIF/ProvONE interoperability, Khan et al. on
CWLProv research objects, Zhang et al. on hybrid provenance, and Yuan et al. on
reusable research objects.

## Project application

`SYNC-MAP-01R1` therefore uses four deliberately separate layers:

- **Formula-family proposal:** prospective ownership and prerequisites.
- **Git source lineage:** exact commits, trees, paths, and Git blob identities.
- **Dropbox reconstruction:** append-only recovery bytes and restored replay.
- **Atlassian projection:** work ownership and DAG state, not formula truth.

The following relations are not silently identified:

```text
GIT_DURABLE
GIT_FORMULA_ONLY
GIT_SIBLING_HELD
EXTERNAL_SNAPSHOT_ONLY
RED_ONLY
NOT_STARTED_OR_BLOCKED
```

Likewise, a consumer replay cannot promote itself to authority; a sibling
formula cannot become canonical merely because its tests pass; and an external
formula snapshot cannot be counted as repository implementation.

## Authority firewall

The literature above supports provenance architecture only. It does not decide
BASS metric, orientation, tetrad index order, Bianchi branch conditions,
Thomson coefficients, finite-tilt physics, or any scientific claim. Those are
owned by exact project formula sources and their independent audits.

## Claim boundary

```text
PROVENANCE_METHOD_ONLY
NO_FORMULA_EQUIVALENCE
NO_SEMANTIC_WINNER
NO_PROVIDER_ADMISSION
NO_SCIENCE_PROMOTION
```
