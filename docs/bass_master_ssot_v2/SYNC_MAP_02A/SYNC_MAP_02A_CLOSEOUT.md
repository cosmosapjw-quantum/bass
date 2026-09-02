# SYNC-MAP-02A closeout

The canonical BASS geometry lineage now exports fourteen formulas with stable `BASS.GEO.*` IDs, valid `EquationIR`, formula-local semantic SHA-256 values, and fifteen closed `depends_on` edges.

## Exact result

```text
formula_count = 14
dependency_edge_count = 15
registry_semantic_hash = d08082e38227c7731c103b26ba8cb029bbf212759f03e64ff1c8ac8ae7f1ab51
convention_hash = e12258405c1c2ec296839524f5169e03441715b3acaaff1cef9de28bfa490a70
type_registry_semantic_hash = e0e5fbba464a839fcb5b11d41c7772c666224ec69f806910aab3bfab5a2f1762
owner = bass
```

The semantic projection excludes identifier, theorem-label and provenance metadata, while retaining assumptions, domain, dimensions, mathematical terms, structural-zero rules, branch predicates and known limits. A matching hash is a candidate same-semantics signal under compatible conventions; it is not by itself a cross-repository proof.

## Identity and verification

```text
parent PR #91
80d271cc528e1a0ffa813ecd3e3fb7610f3fa755
3fd8818938eaa0988988c6927cff799455a7a31d

implementation/source-packet commit
e6946d7eb99bc11e07912aacf06ff6d8242d9c37

semantic-index commit/tree
e057ff21ae3d5a6b97f4efa77293e93f5675f11b
62cba0cdf4b69a5cbcfa509d0a86c2322dae0eb1
```

TDD and replay:

```text
RED run 33586084200: expected missing-module/schema/loader failure
GREEN run 33586400828: SUCCESS
index-head run 33586600166: SUCCESS
fresh Wolfram/xAct replay: 175 succeeded, 0 failed, 0 not evaluated
export_valid = true
artifact 9830216763
artifact SHA-256 c6a88e4899f8d3b82ff6708d8641cd72be2730f4a97452e5d7d383c84878a375
```

## Next nodes

```text
SYNC-MAP-02B_REC_RELATION_CLASSIFICATION
SYNC-MAP-02C_REI_RELATION_CLASSIFICATION
```

The parallel BASS physics lane may open `BG-02_GR_BACKGROUND_EINSTEIN_PROJECTION_DESIGN` from the composed geometry parent.

## Claim boundary

```text
BASS_14_FORMULA_EQUATIONIR_REGISTRY_VERIFIED
BASS_14_FORMULA_SEMANTIC_HASH_EXPORT_VERIFIED
BASS_15_DEPENDENCY_EDGES_VERIFIED
SYNC_MAP_02A_EXACT_SOURCE_PACKET_REPLAY_175_OF_175

NO_REC_OR_REI_RELATION_CLASSIFICATION
NO_CROSS_REPOSITORY_SEMANTIC_EQUIVALENCE
NO_BACKGROUND_EINSTEIN_MATTER_EVOLUTION
NO_PROVIDER_ADMISSION
NO_NUMERICAL_PARITY
NO_SCIENCE_VALIDITY
NO_PASS_RF04
```
