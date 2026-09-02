# BG-02 updated DAG and work completeness

Percentages below measure declared deliverables, not test counts or perceived
code volume.

## 1. Completed prerequisites

| Node | State | Completion | Evidence |
|---|---|---:|---|
| `SYNC_MAP_01C_GEOMETRY_LINEAGE_COMPOSITION` | PASS, Draft | 100% | PR #91, exact parent lineage, native Wolfram/xAct `158/158` |
| `SYNC_MAP_02A_BASS_EQUATIONIR_AND_SEMANTIC_HASH_EXPORT` | PASS, Draft, parallel lane | 100% | PR #93, 14 formulas, 15 edges, native replay `175/175` |
| `BG-02_GR_BACKGROUND_EINSTEIN_PROJECTION_DESIGN` | PASS, this branch | 100% | four projections, rate identities, shear adapter, limits, P0 guard, SciSpace lock, dual audit, CRAG |

## 2. Open and blocked nodes

| Node | State | Completion | Blocking condition |
|---|---|---:|---|
| `BG-02_GR_BACKGROUND_EINSTEIN_PROJECTION_IMPLEMENTATION` | OPEN | 0% | production module and native xAct projection not written |
| `BG-02C_CONSTRAINT_PROPAGATION_AND_RESIDUAL_MONITOR_DESIGN` | BLOCKED | 0% | requires implemented off-shell projection APIs |
| `BG-03_TEMPORAL_JACOBI_AND_STRUCTURE_EVOLUTION` | BLOCKED | 0% | requires BG-02 implementation and residual contract |
| `NUM_ARBITRARY_L_OPERATOR_COMPILER` | BLOCKED | about 5% | formula authority exists; executable compiler ABI does not |
| `SYNC_MAP_02B_REC_RELATION_CLASSIFICATION` | OPEN, parallel | 0% | BASS export is ready; REC occurrences unclassified |
| `SYNC_MAP_02C_REI_RELATION_CLASSIFICATION` | OPEN, parallel | 0% | BASS export is ready; REI occurrences unclassified |

## 3. Program-level completion estimates

| Layer | Completion | Interpretation |
|---|---:|---|
| canonical common-geometry formula line | 100% | conventions, algebra, connection, W2 and W3 are composed and replayed |
| BASS formula-export lane | 100% | BASS side only; no REC/REI equivalence claim |
| BG-02 mathematical design | 100% | implementation-ready, not production-ready |
| BG-02 production implementation | 0% | six required APIs absent |
| BG-02 native xAct four-projection replay | 0% | current design oracle is pure Wolfram only |
| BG-02 constraint propagation | 0% | deliberately separate next node |
| federation `SYNC_MAP_02` total | about 33% | BASS lane closed; REC and REI lanes open |
| full background-evolution program | about 35% | geometry strong; Einstein/matter runtime and propagation absent |
| arbitrary-`L` executable compiler | about 5% | generic-rank formula authority is not executable arbitrary-`L` support |
| full `bass+rec_bianchi+rei_bianchi+htt_base` end-to-end program | about 18% | providers, coupled evolution, outputs and fitting gates remain open |

These estimates are intentionally conservative.  A formula-only all-rank
hierarchy is not counted as an arbitrary-`L` numerical solver, and a registry
entry is not counted as family-ready background evolution.

## 4. Updated DAG

```text
PR #91  W2 + W3 canonical composition
   |
   +--> BG-02 DESIGN                     PASS HERE
   |       |
   |       +--> BG-02 IMPLEMENTATION     NEXT PHYSICS NODE
   |               |
   |               +--> BG-02C CONSTRAINT PROPAGATION / RESIDUAL MONITOR
   |                       |
   |                       +--> BG-03 TEMPORAL JACOBI / STRUCTURE EVOLUTION
   |
   +--> PR #93 BASS EquationIR export    PASS PARALLEL
           |
           +--> SYNC-MAP-02B REC relation classification
           +--> SYNC-MAP-02C REI relation classification
                    |
                    +--> cross-repository semantic gate
```

## 5. Recommended next step

```text
BG-02_GR_BACKGROUND_EINSTEIN_PROJECTION_IMPLEMENTATION
```

Branch from exact PR #91 head
`80d271cc528e1a0ffa813ecd3e3fb7610f3fa755`.

Implement one residual tensor and the six required projection APIs, then run a
fresh native xTensor/xCoba source-packet replay.  The correct kill criterion is
any nonzero projection residual, any failure of V/II index-order witnesses, any
loss of the exceptional momentum carrier, or any failed/not-evaluated native
test.

## 6. Parallel next step

```text
SYNC_MAP_02B_REC_RELATION_CLASSIFICATION
```

This may proceed independently from PR #93 because it classifies ownership and
semantic relations rather than changing BG-02 physics.

## 7. Forbidden jumps

Do not start any of the following before BG-02 implementation and native replay:

```text
background numerical integration
constraint damping or adjusted-ADM tuning
all-family runtime claims
REC/REI provider admission
arbitrary-L optimization
observable generation
likelihood or fitting
publication-grade solver claim
```
