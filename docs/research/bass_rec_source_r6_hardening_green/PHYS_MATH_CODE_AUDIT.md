# PHYS–MATH–CODE audit — R6 authority hardening GREEN candidate

## Equation-to-code map

| Contract | Code surface | Current implementation |
|---|---|---|
| positive paired rates | `_finite_nonnegative`, `constant_pair` | finite/nonnegative validation; signed zero normalized |
| photon/boson source | `SourceSpecies`, `SourceStatistics`, `pointwise_action` | immutable metadata plus affine evaluation |
| signed net coefficient | `chi_affine_s_inv` | `kappa_s_inv-eta_s_inv`; no positivity projection |
| physical-to-Q time | `rates_per_tau` | divide both primary rates by one positive finite `H_s_inv` |
| canonical source identity | `_payload_sha256`, `constant_pair` | schema-v2 JSON with exact binary64 hex rates and metadata |
| integrated projection identity | `IntegratedMomentMapBinding.create` | target/moment-map/radial-weight/source hashes |
| representation firewall | `require_source_representation_compatibility` | pointwise and integrated states are disjoint; binding required |
| finite-result firewall | `_finite_result`, `SourceArithmeticError` | nonfinite output is rejected before return |
| angular product rank | `required_work_rank`, `validate_work_rank` | unchanged R5 contract |

## PMC-01 — validated construction

`SourceAuthorityBundle` and `IntegratedMomentMapBinding` are frozen, slotted,
`init=False` dataclasses.  Their public `__init__` methods always raise
`TypeError`; the validated factories allocate with `object.__new__` and set all
fields internally.  Caller-supplied payload or binding hashes are therefore not
accepted by the public API.

The low-level Python operation `object.__new__(SourceAuthorityBundle)` can still
produce an uninitialized object, as it can for most Python classes.  This is not
a supported public constructor and no solver path may accept arbitrary objects
without an `isinstance` and factory-origin/provenance check.

Status: **SOURCE-LEVEL FIXED; runtime test pending**.

## PMC-02 — backward-compatibility surface

The eleven migrated R5 survivor tests use only:

- `constant_pair` with `POINTWISE_SPECTRAL`;
- primary fields, `chi_affine_s_inv`, hash shape;
- `rates_per_tau`, `pointwise_action`;
- state/frequency enums;
- work-rank and pointwise compatibility checks.

Those APIs remain present.  The intentional compatibility break is restricted
to the previously superseded unbound integrated-witness admission and to the
v1 payload identity, both explicitly migrated in the R6 RED contract.

Status: **STATICALLY CONSISTENT; exact survivor replay pending**.

## PMC-03 — stable arithmetic path

The implementation uses

```text
eta-(kappa-eta)f
```

rather than evaluating two potentially overflowing terms and subtracting them.
This preserves the exact source law and reduces one avoidable cancellation
failure.  It still rejects an actually nonfinite final binary64 result.

The code catches both an explicit `OverflowError` and the normal IEEE result
`inf`/`nan`.  It does not use arbitrary precision, rescaling, or silent clipping.

Status: **APPROPRIATE FOR A FAIL-CLOSED PROTOCOL TYPE**.

## PMC-04 — integrated-binding limits

`require_source_representation_compatibility` verifies:

- binding type;
- integrated target class;
- exact target-state identity.

It does not yet receive a concrete `SourceAuthorityBundle` and therefore cannot
compare `binding.source_sha256` to the payload being consumed.  That comparison
belongs in the later BASS receiving adapter, not in this representation-only
predicate.

Status: **NARROWLY CORRECT; solver integration remains blocked**.

## PMC-05 — dependency and import boundary

The updated module imports only the Python standard library.  It does not import
JAX, NumPy, SciPy, the Rust extension, REC, Q, backend policy, or formula/compiler
packages.  No top-level `bianchi.__init__` change is made.

Status: **LOW REGRESSION CONE**.

## PMC-06 — source and workflow separation

The implementation commit changes:

```text
bianchi/source_authority.py
.github/workflows/bass-rec-source-r6-hardening-red.yml
```

The workflow is renamed semantically to GREEN and runs the two focused suites.
No test is weakened on the GREEN branch.

Status: **TDD ORDER PRESERVED**.

## Required local verification

1. exact commit/tree/blob identity;
2. `py_compile`;
3. R5 survivor suite `11/11`;
4. R6 hardening suite `10/10`;
5. two-process equality of schema-v2 source hashes;
6. two-process equality of integrated binding hashes;
7. constructor, signed-zero, overflow and target-mismatch probes;
8. deterministic source-branch audit data and SVG;
9. clean detached worktree.

Only after these pass should the same parent/candidate backend differential used
for R5C be repeated.  A focused GREEN alone does not establish production-native
provenance or solver nonregression.

## Ranked findings

### P0

None in the static implementation.

### P1

1. The source has not yet been executed on the exact implementation commit.
2. Backend behavior-level differential must be repeated after focused GREEN.
3. Trusted production-wheel provenance remains a separate open lane.

### P2

1. No fixed v2 golden hash is committed yet; first local execution should freeze
   it in a closeout receipt rather than modifying the source.
2. There is no target adapter that compares the binding source hash with the
   incoming source bundle.
3. Frame/channel string registries and convention hashes remain future adapter
   responsibilities.

### P3

The inherited workflow filename still contains `red` although its displayed
name and behavior are GREEN.  Renaming the path is cosmetic and should not be
mixed into this physics-contract change.

## Verdict

```text
PHYS_MATH_CODE_R6_GREEN_SOURCE_PASS
EXECUTABLE_GREEN_AND_REPOSITORY_NONREGRESSION_PENDING
NO_SOLVER_OR_PROVIDER_PROMOTION
```
