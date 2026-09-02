# Four-Repository DAG Reconciliation — Concurrent Snapshot R1

**Program:** `BIANCHI_FOUR_REPO_DAG_RECONCILIATION_20260902_R1`  
**Observed:** 2026-09-02 14:49 KST  
**Repositories:** `bass`, `rec_bianchi`, `rei_bianchi`, `htt_base`  
**Status:** `SHADOW_DAG_ADJUSTED / OFFICIAL_LINKS_UNCHANGED / SCIENCE_NOT_PROMOTED`

## 1. Evidence boundary

This reconciliation was prepared from:

- repeated direct GitHub readback of the four repositories during one response;
- current Jira and Confluence readback;
- the current project thread;
- personal-context retrieval of relevant prior conversations and memories.

The conversation/memory query is not a raw export of every transcript. GitHub exact objects remain formula/code/evidence authority. Dropbox is recovery authority. Atlassian is the workflow and DAG projection.

The same instruction was issued in four concurrent sessions. Therefore this record is append-only and snapshot-bound. It does not assume that a branch observed earlier in the response remained latest: the repositories were polled again immediately before publication. This process detected BASS PR #95 after an earlier local REC-classification audit; PR #95 supersedes that pre-publication assessment.

## 2. Current exact heads

| Lane | Current source | Scope |
| --- | --- | --- |
| BASS geometry | PR #91, `80d271cc...` | connection + W2 + spatial curvature, 158/158 replay |
| BASS semantic export | PR #93, `6587c081...` | 14 geometry EquationIR formulas, 175/175 replay |
| BASS BG-02 design | PR #94, `ef6d51aa...` | Einstein projection design only; no production implementation |
| BASS–REC relation map | PR #95, `f1eab555...` | active REC relation classification, restored 200/200 |
| REC science | PR #47, `c4bf37d7...` | REC-NEXT-03 contracts; physical 26-direction face absent |
| REI science | PR #32, `f4eb2c89...` | runtime bridge stopped on undeclared `ntpath` import |
| HTT full-sky boost | PR #442, `29427a1f...` | scoped scalar local-observer boost only |
| HTT processed boost | PR #444, `978fbe61...` | Task-7B no-candidate; Task-7C design ready |

## 3. DAG corrections

### 3.1 Add `htt_base` as a fourth coordination lane

The historical BASS-16 program remains the BASS/REC/REI physics core. `htt_base` is added to the coordination projection as the observer/output/statistics consumer and local-observer-transform implementation lane. It does not become an owner of Bianchi background geometry, REC atomic physics, or REI thermochemistry.

### 3.2 Split producer and consumer

The old single node `INT.HTT_BACKGROUND_EXPORT` is too coarse. It is replaced in the shadow DAG by:

```text
BASS.HTT_EXPORT_BUNDLE
  -> HTT.BASS_BUNDLE_CONSUMER
  -> HTT.STATISTICS_GATE
```

A matching field name or file format is not cross-repository compatibility. The producer and consumer each require their own exact receipts.

### 3.3 Narrow the existing Jira blockers

The existing Jira chain

```text
BASS-19 (REC) -> BASS-18 (REI) -> BASS-17 (BASS)
```

is retained structurally, but its meaning is narrowed to provider integration and promotion. It must not block:

- generic BASS algebra, geometry and curvature;
- BASS EquationIR export;
- BG-02 design or production implementation;
- REC source-authority work that does not fabricate a provider;
- REI runtime-bridge repair;
- `htt_base` Task-7C local-observer identifiability work.

### 3.4 Adopt the concurrent REC relation closeout

BASS PR #95 is the current authority for `SYNC-MAP-02B`. It reports no active REC duplicate authority against the 14 exported BASS geometry formulas, while identifying four common formulas that still lack BASS stable export IDs:

```text
BASS.FRAME.ABERRATED_DIRECTION.001
BASS.FRAME.DOPPLER_FACTOR.001
BASS.PHOTON.DIRECTION_FLOW.001
BASS.PHOTON.ENERGY_DRIFT.001
```

The next federation node is therefore REI relation classification, not another REC derivation.

### 3.5 Union-driven shared export

After `SYNC-MAP-02C_REI_RELATION_CLASSIFICATION`, BASS creates one shared frame/photon EquationIR extension from the union of REC and REI consumer gaps. REC, REI and HTT then consume it through exact pins, typed adapters, or authority-effect-`NONE` independent oracles. No consumer may select itself as semantic owner.

### 3.6 Parallel execution frontier

The following work is independent and may proceed concurrently without sharing a mutable branch:

```text
FED.MAP02C_REI
BASS.BG02_IMPLEMENT
REC.FACE_SOURCE_AUTHORITY
REI.RUNTIME_BRIDGE_REPAIR
HTT.WU011_TASK7C
HTT.PR315_DETERMINISM
```

Their promotion gates remain separate.

### 3.7 Scope the HTT reproducibility blocker

Jira BASS-25 blocks only `HTT.WU011_RELEASE_GATE` and later Task-8/release reproducibility. It does not invalidate WU-010, the Task-7B negative characterization, Task-7C design, or any BASS/REC/REI physics node. The expected hash must not be updated until the nondeterministic preimage difference is explained.

### 3.8 Resolve the duplicate WU-011 projection without a cycle

BASS-21 is the current WU-011 execution projection. BASS-22 is retained as an older specification surface. Its structured `Blocks` relation toward the already-Done BASS-20 is stale/reversed. This reconciliation records the defect but does not add a compensating opposite `Blocks` edge, which would create a misleading cycle. Removal or correction of the old link is a separate bounded Jira mutation.

## 4. Four-lane DAG

```text
FEDERATION
AUTH -> FED00 -> MAP01 -> GEOMETRY_COMPOSE -> MAP02A
                                              |-> MAP02B_REC [PASS, PR #95]
                                              `-> MAP02C_REI [NEXT]
MAP02B_REC + MAP02C_REI
  -> SHARED_FRAME_PHOTON_EXPORT
  -> {SYNC_REC, SYNC_REI, SYNC_HTT}
  -> MAP02D
  -> SYNC_GATE01 [manual approval only]

BASS PHYSICS
GEOMETRY [PASS]
  -> BG02_DESIGN [PASS design-only]
  -> BG02_IMPLEMENT [READY]
  -> BG02_CONSTRAINT_PROP
  -> STRUCTURE_EVOLUTION
REC_PROVIDER + REI_PROVIDER + STRUCTURE_EVOLUTION
  -> COUPLED_HISTORY
PHOTON_CORE_FORMULA + SHARED_FRAME_PHOTON_EXPORT
  -> {ARBITRARY_L_COMPILER, FINITE_TILT_COLLISION}
COUPLED_HISTORY + ARBITRARY_L_COMPILER + FINITE_TILT_COLLISION
  -> BASS.HTT_EXPORT_BUNDLE

REC
NEXT03_CONTRACTS
  |-> FACE_SOURCE_AUTHORITY [READY]
  `-> COMMON_IMPORT_REPAIR [after shared export]
FACE_SOURCE_AUTHORITY + COMMON_IMPORT_REPAIR
  -> PHYSICAL_FACE_IMPLEMENT
  -> PROVIDER_EXPORT

REI
THERMOCHEMISTRY [partial]
RUNTIME_BRIDGE_REPAIR [READY]
COMMON_IMPORT_REPAIR [after shared export]
  -> FIRST_CANONICAL_INTERVAL
  -> PROVIDER_EXPORT
REC provider is a promotion pin for REI provider; it does not block the runtime repair.

HTT
WU010_LOCAL_BOOST [scoped PASS]
  -> WU011_TASK7B [PASS negative/no candidate]
  -> WU011_TASK7C [READY]
  -> WU011_RELEASE_GATE
PR315_DETERMINISM -> WU011_RELEASE_GATE only
BASS.HTT_EXPORT_BUNDLE
  -> HTT.BASS_BUNDLE_CONSUMER
WU011_RELEASE_GATE + HTT.BASS_BUNDLE_CONSUMER
  -> HTT.STATISTICS_GATE
```

## 5. Claim boundaries retained

```text
NO_PASS_RF04
NO_PASS_REC_PHYSICAL_SPLIT
NO_PASS_FIRST_CANONICAL_INTERVAL
NO_EMPIRICAL_BETA_OR_BOOST_SUBTRACTION
NO_CROSS_REPOSITORY_SEMANTIC_EQUIVALENCE_UNTIL_MAP02D
NO_PERIODIC_DRIFT_FAILING_ACTIVATION_UNTIL_MANUAL_SYNC_GATE01_APPROVAL
```

The photon formula SSOT remains formula-only: finite electron tilt, recombination/reionization, hierarchy truncation, numerical evolution and inference are not silently promoted by this DAG update.

## 6. Current next actions

1. **Federation:** execute `SYNC-MAP-02C_REI_RELATION_CLASSIFICATION` on the exact REI PR #32 lineage.
2. **BASS:** implement BG-02 from PR #91 + PR #94 design, including the connection-order guard and native xAct source-packet replay.
3. **REC:** work only on accepted causal/source-identical 26-direction data and its authority record; do not create another common boost/characteristic derivation.
4. **REI:** repair the undeclared `ntpath` runtime bridge contract without retry drift or provider promotion.
5. **HTT:** execute Task-7C; separately diagnose BASS-25 before Task-8/release.

## 7. Non-actions

- no PR merge or ready transition;
- no force push or history rewrite;
- no source deletion or owner reassignment;
- no Jira workflow transition;
- no official Jira dependency-link mutation;
- no provider admission;
- no scientific claim promotion;
- no scheduled drift-failing activation.
