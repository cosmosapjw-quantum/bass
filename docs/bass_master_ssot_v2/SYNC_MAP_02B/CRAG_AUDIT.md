# SYNC-MAP-02B plot-driven CRAG audit

## Plot production

The requested Python plotting call failed with a runtime `ClientError`. The plot step was not waived. Two deterministic SVG figures and their CSV inputs were committed instead:

- `REC_RELATION_CLASSES.svg` / `REC_RELATION_CLASSES.csv`;
- `BASS14_REC_OVERLAP_MATRIX.svg` / `BASS14_REC_OVERLAP_MATRIX.csv`.

The SVGs encode only the exact classified counts and make no continuous-data or uncertainty claim.

## Plot reading

### REC relation classes

The largest class is `PINNED_IMPORT_PENDING_OWNER_EQUATIONIR`, with 4 of 9 relations. REC-owned specialization and extension account for 3 of 9; independent nonauthoritative oracles account for 2 of 9.

The visual conclusion is therefore not “REC repeatedly rederived the whole BASS geometry.” It is:

```text
REC has four common formula occurrences whose BASS ownership is conceptually clear,
but exact import locks cannot yet be written because the owner EquationIR records are absent.
```

### Active REC lineage versus BASS-14 geometry export

Thirteen of fourteen BASS geometry formulas have no active REC rederivation detected. One formula, `BASS.GEO.STRUCTURE_CONSTANTS.001`, appears as a dependency only. Duplicate authority count is zero.

This is a strong result for the active PR #47 lineage, but the zero-height duplicate bar must not be read as an all-history theorem.

## CRAG

### C — Correctness

- Counts in both SVGs equal the machine registry and the Wolfram tests.
- Relation-class total is `4+1+2+2=9`.
- BASS matrix total is `13+1+0=14`.
- No plot category is promoted beyond its registry meaning.

### R — Retrieval and source alignment

- The shared normal-frame energy and direction formulas agree algebraically with the BASS photon theorem.
- Doppler and aberration belong to the common frame theorem.
- Hydrogen-frame frequency rate, moving Doppler face, and event surfaces remain REC-owned.
- Covariant/PSTF and anisotropic light-propagation literature supports this separation but does not establish code identity.

### A — Augmented adversarial checks

- Wrong energy-drift sign gives residual `6`.
- Wrong hydrogen-adapter coefficient gives residual `1`.
- A foreign DAG endpoint is rejected.
- `R_H=0` and `v_x=0` are separated by two exact counterexamples.
- Oracle authority promotion, provider admission, and duplicate-owner mutations fail the registry or receipt contracts.

### G — Generation and next prediction

The plots predict that the highest-value next federation work is not a broad REC rewrite. It is:

1. classify the corresponding REI relations;
2. take the union of REC and REI shared-owner gaps;
3. export each common formula once from BASS as EquationIR;
4. replace project-local algebraic compatibility with exact import hashes.

## Claim classification

### Surviving

```text
ACTIVE_REC_PR47_RELATIONS_CLASSIFIED
NO_ACTIVE_REC_DUPLICATE_AUTHORITY_AGAINST_BASS14_DETECTED
REC_OWNED_ADAPTER_AND_FACE_FORMULAS_SEPARATED
RESTORED_HARDENED_WOLFRAM_STACK_200_OF_200_PASS
```

### Narrowed

```text
FOUR_SHARED_RELATIONS_ARE_ALGEBRAICALLY_COMPATIBLE
BUT_NOT_YET_CROSS_REPOSITORY_SEMANTIC_HASH_EQUIVALENT
```

### Rejected

```text
ALL_HISTORICAL_REC_BRANCHES_DEDUPLICATED
REC_PHYSICAL_FACE_ADMITTED
REC_PROVIDER_READY
OFFICIAL_DAG_UPDATED
CROSS_REPOSITORY_COMPATIBILITY_ESTABLISHED
SCIENCE_OR_RF04_PROMOTED
```

## Verdict

```text
PASS_WITH_FOUR_BASS_OWNER_EXPORT_GAPS
```
