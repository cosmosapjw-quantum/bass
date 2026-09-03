# PHYS–MATH–CODE audit — R6 hardening RED

## Exact code surface

Parent implementation:

```text
bianchi/source_authority.py
commit fc4d21b92a1abd1e9b35178f7d666831fc5c827d
blob   f9eceaa02e82c746045df255af2ce674dab1bb75
```

R5C established behavior-level backend nonregression: the exact R4 parent and R5 candidate both returned zero under the same local source-build environment and wheel.

## PMC-00 — contradictory survivor/admission tests

The initial R6 RED commit ran the unchanged R5 suite and the new R6 suite together. Exact source review found that they required opposite results for one identical call:

```text
frequency_kind = SOURCE_INTEGRATED_WITNESS
state_kind     = RADIAL_INTEGRATED_ANGULAR_GRID
binding        = absent
```

- historical R5 test: return normally;
- R6 hardening test: raise `SourceRepresentationError`.

No deterministic implementation can satisfy both. Severity: **P0 test-contract contradiction**.

Repair in this RED branch:

- preserve the historical v1 test and behavior at PR #112 exact head;
- migrate the R6 child survivor file by replacing only the superseded admission assertion with a stable enum-distinctness assertion;
- make the R6 test the sole authority for integrated-witness admission;
- add the migrated survivor path to the workflow trigger and first-GREEN allowlist.

No production path changes. Status: **CLOSED AT CONTRACT LEVEL; LOCAL REPLAY REQUIRED**.

## PMC-01 — constructor bypass

The class is a frozen, slotted dataclass but retains the generated public constructor. `frozen=True` prevents mutation after construction; it does not validate construction. A caller can currently supply negative/nonfinite rates, malformed strings, a non-enum frequency kind, and a forged `payload_sha256` directly.

Severity: **P1**. The object is named an authority bundle and must be valid by construction before solver wiring.

Minimal GREEN shape:

- suppress the generated public initializer or make it validation-complete;
- compute `payload_sha256` internally only;
- keep the documented factory compatible with the stable R5 call surface.

## PMC-02 — signed-zero identity split

`_finite_nonnegative` accepts `-0.0`; `float.hex()` preserves its sign. Two semantically identical sources can therefore acquire different payload hashes.

Severity: **P2 now / P1 after provenance fan-out**.

Minimal GREEN shape: canonicalize every accepted zero to positive zero before storage and hashing.

## PMC-03 — source statistics absent

`pointwise_action` hard-codes the bosonic `1+f` factor, but neither the class name nor its payload records photon/boson semantics. BASS contains other kinetic species and moment lanes, so a generic receiving object is unsafe without explicit binding.

Severity: **P1**.

Minimal GREEN shape: immutable photon/boson enums or equivalent literal fields included in the v2 payload hash. Do not implement fermion dynamics in R6.

## PMC-04 — constant pair can claim integrated-witness frequency kind

`constant_pair` currently accepts either enum value. The scalar pair carries no target moment-map identity and therefore cannot be a source-integrated witness.

Severity: **P1**.

Minimal GREEN shape: the factory admits `POINTWISE_SPECTRAL` only and raises a typed representation error otherwise.

## PMC-05 — integrated witness admission lacks a binding object

`require_source_representation_compatibility` admits `SOURCE_INTEGRATED_WITNESS` for both integrated state kinds solely from two enums. It has no target-state, moment-map, radial-weight, or source identity.

Severity: **P1**.

Minimal GREEN shape: add an immutable `IntegratedMomentMapBinding` with an internally computed hash, require a binding for every integrated admission, and require an exact target-state match.

## PMC-06 — nonfinite arithmetic can escape

The validators protect inputs, but the division and affine action do not validate outputs. Finite binary64 inputs can overflow.

Severity: **P2** before solver integration; **P1** once connected to state evolution.

Minimal GREEN shape: add `SourceArithmeticError` and reject nonfinite results from both public arithmetic methods.

## PMC-07 — compatibility and regression risk

The first GREEN must preserve:

- the existing R5 factory call without new required arguments;
- all eleven **stable** R5 survivor tests after removal of the explicitly superseded unbound-witness assertion;
- dependency-light package import;
- backend route tables and native policy bytes;
- behavior-level backend nonregression.

It must not preserve the obsolete claim that an unbound integrated witness is admissible. Adding eager imports to `bianchi.__init__`, NumPy dependencies, solver callbacks, or REC data is out of scope.

## Test classification

The R6 test is a **protocol/authority RED**, not a physics-validation or solver-regression test. It includes two survivor controls so a future GREEN cannot satisfy new hardening requirements by breaking the R5 source law or Q-time domain.

After the coherence amendment, exact static inspection predicts:

- stable R5 suite: 11 pass;
- R6 constructor test: fail;
- R6 signed-zero test: fail;
- R6 species/statistics/schema test: fail;
- R6 integrated-kind firewall test: fail;
- R6 missing-binding test: fail;
- R6 binding-type test: fail;
- two R6 arithmetic tests: fail;
- source-off and Q-domain controls: pass.

No exact execution count is promoted until Python runs on the amended committed head.

## Verdict

```text
P0_TEST_CONTRACT_CONTRADICTION_CLOSED
PHYS_MATH_CODE_R6_RED_CONTRACT_COHERENT
R5C_NONREGRESSION_PRESERVED_AS_PREREQUISITE
R6_EXECUTED_RED_NOT_YET
R6_PRODUCTION_HARDENING_NOT_IMPLEMENTED
NO_SOLVER_OR_SOURCE_INTEGRATION
```
