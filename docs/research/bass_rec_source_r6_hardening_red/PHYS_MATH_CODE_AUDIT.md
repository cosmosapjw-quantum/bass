# PHYS–MATH–CODE audit — R6 hardening RED

## Exact code surface

Parent implementation:

```text
bianchi/source_authority.py
commit fc4d21b92a1abd1e9b35178f7d666831fc5c827d
blob   f9eceaa02e82c746045df255af2ce674dab1bb75
```

R5C established behavior-level backend nonregression: the exact R4 parent and R5 candidate both returned zero under the same local source-build environment and wheel.

## PMC-01 — constructor bypass

The class is a frozen, slotted dataclass but retains the generated public constructor. `frozen=True` prevents mutation after construction; it does not validate construction. A caller can currently supply negative/nonfinite rates, malformed strings, a non-enum frequency kind, and a forged `payload_sha256` directly.

Severity: **P1**. The object is named an authority bundle and must be valid by construction before solver wiring.

Minimal GREEN shape:

- suppress the generated public initializer or make it validation-complete;
- compute `payload_sha256` internally only;
- keep the documented factory compatible with the R5 call surface.

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

Minimal GREEN shape: add an immutable `IntegratedMomentMapBinding` with an internally computed hash, and require an exact target-state match for integrated admission.

## PMC-06 — nonfinite arithmetic can escape

The validators protect inputs, but the division and affine action do not validate outputs. Finite binary64 inputs can overflow.

Severity: **P2** before solver integration; **P1** once connected to state evolution.

Minimal GREEN shape: add `SourceArithmeticError` and reject nonfinite results from both public arithmetic methods.

## PMC-07 — compatibility and regression risk

The first GREEN must preserve:

- the existing R5 factory call without new required arguments;
- all eleven R5 focused tests;
- dependency-light package import;
- backend route tables and native policy bytes;
- behavior-level backend nonregression.

Adding eager imports to `bianchi.__init__`, NumPy dependencies, solver callbacks, or REC data is out of scope.

## Test classification

The R6 test is a **protocol/authority RED**, not a physics-validation or solver-regression test. It includes two survivor controls so a future GREEN cannot satisfy new hardening requirements by breaking the R5 source law or Q-time domain.

Expected parent outcome:

- direct-constructor test fails;
- signed-zero test fails;
- species/statistics/schema test fails;
- integrated-kind firewall test fails;
- missing-binding test fails;
- binding-type test fails;
- two arithmetic tests fail;
- source-off and Q-domain controls pass.

No exact failure count is promoted until the test executes on the committed R6 head.

## Verdict

```text
PHYS_MATH_CODE_R6_RED_CONTRACT_PASS
R5C_NONREGRESSION_PRESERVED_AS_PREREQUISITE
R6_PRODUCTION_HARDENING_NOT_IMPLEMENTED
NO_SOLVER_OR_SOURCE_INTEGRATION
```
