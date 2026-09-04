# PHYS–MATH–CODE Audit — R10A Projection Authority Hardening

## Equation-to-code map

| Mathematical object | Current code | R10A failure mode |
|---|---|---|
| locked mode order | `canonical_real_harmonic_modes` | survives |
| unit field `Pi_L 1` | `unit_field_coefficients` | actual supplied vector omitted from comparison contract |
| normalized real basis | `_associated_legendre`, `_complex_harmonic_normalization`, `_real_harmonic` | realized basis matrix not identity-bound; same implementation used on both sides |
| GL × uniform-phi rule | `_gauss_legendre_rule`, `SphereQuadrature.create` | semantic and floating realization identities conflated |
| public quadrature admission | `_validated_quadrature` | only type/rank/length checks; stale hashes and same-length mutations survive |
| synthesis | `synthesize_real_spherical_harmonics` | trusts stored object fields without recomputed identity |
| projection | `project_real_spherical_harmonics` | trusts stored object fields without recomputed identity |
| comparison identity | `_build_contract` | omits actual unit field, time basis, divisor |
| report identity | report payload in `compare_constant_pair_grid_and_pstf` | stronger than contract, but public constructor permits forgery |
| pass criterion | componentwise `atol+rtol*scale` | report and plot omit direct utilization ratio |
| physical positivity | `min(samples) >= 0` | only node-sampled positivity, not continuous sphere |

## Root-cause classification

These are not failures of the affine source theorem. They arise at the authority boundary between a numerical transform and its provenance object.

The common root is:

```text
DECLARED_CONVENTION_IDENTITY != COMPLETE_REALIZED_OPERATOR_IDENTITY
```

Secondary roots are:

```text
VALIDATED_AT_FACTORY_ONLY != VALIDATED_AT_PUBLIC_USE_BOUNDARY
FROZEN_DATACLASS != VALID_BY_CONSTRUCTION
EXECUTED_RANK_SWEEP != UNBOUNDED_PUBLIC_ADMISSION
```

## Expected-RED test design

The R10A suite has 16 tests:

```text
13 future-behaviour tests expected to fail
  stale hash rejection
  same-length weight tamper rejection
  basis mutation invalidation
  explicit sample layout
  semantic/realization identity split
  basis-matrix identity
  actual unit-field contract binding
  time/divisor contract binding
  factory-only contract
  factory-only report
  tolerance utilization
  no continuous-positivity overclaim
  rank ceiling

3 controls expected to pass
  current L=2 parity
  analytic Y00/Y10/Y11c/Y11s values
  exact affine projection linearity
```

The runner accepts only the exact thirteen-test failure set, no errors or skips, three controls, and all 49 inherited tests passing.

## Minimal future GREEN design

The first GREEN should remain one production file if feasible: `bianchi/source_parity.py`.

### Change 1 — versioned identities

Add immutable fields:

```text
sample_layout
basis_algorithm_id
quadrature_algorithm_id
projection_spec_sha256
basis_matrix_sha256
projection_realization_sha256
```

Retain `projection_contract_sha256` only as a compatibility alias to the full realization identity or deprecate it explicitly. Silent semantic repurposing is forbidden.

### Change 2 — one canonical payload builder

Create internal pure functions that return the exact semantic and realization payloads. `SphereQuadrature.create` and `_validated_quadrature` must use the same builders. No duplicated hashing logic.

### Change 3 — use-time validation

At every public transform boundary:

```text
validate scalar fields and array lengths
validate geometry/range/order/positive weights
recompute H_spec, H_B, H_real
compare against stored identities
reject before numerical evaluation
```

The validation must not mutate or repair the object.

### Change 4 — comparison contract V2

The contract must include:

```text
actual_unit_field_sha256
unit_field_is_canonical
time_basis
rate_divisor_hex
projection_spec_sha256
projection_realization_sha256
atol_hex
rtol_hex
```

Diagnostic noncanonical unit fields may be retained with `require_pass=false`, but their contract identity must differ from the canonical comparison.

### Change 5 — factory-only receipts

Make both `SourceParityContract` and `SourceParityReport` `init=False` and construct internally after complete validation. Add public `validate()` or `recompute_identity()` methods only if needed by downstream consumers.

### Change 6 — honest numerical envelope

Until a separate high-L lane passes, add an explicit current certificate ceiling:

```text
MAX_CERTIFIED_L_WORK = 8
```

Reject higher ranks by default. A future API may support an explicitly named uncertified diagnostic mode, but it must not share the certified path or hashes.

### Change 7 — diagnostics

Store:

```text
max_tolerance_utilization
continuous_positivity_certified
positivity_certificate_kind
```

The initial continuous-positivity value is false unless the analytic coefficient bound is checked and passed.

## Regression risks

- changing hash schemas invalidates R10 golden identities by design;
- compatibility aliases can accidentally hide V1/V2 differences;
- recomputing a full basis matrix at every call is costly if not cached safely;
- caching by mutable object identity can reintroduce tamper acceptance;
- a hard rank ceiling may break callers that used uncertified high ranks;
- factory-only dataclasses may affect serialization consumers.

Mitigations:

```text
new schema versions
explicit migration tests
cache only immutable canonical payload bytes or rebuild at comparison creation
no cache keyed solely by object id
separate certified and diagnostic APIs
```

## Independent-oracle requirement

The current analytic low-mode control is necessary but not sufficient. R10A GREEN should add a runner-only second oracle using at least one of:

```text
SciPy `sph_harm_y` / legacy `sph_harm`
SymPy `Ynm` evaluated at selected exact or high-precision points
qualified SHT library
```

The oracle must compare point values and coefficient transforms without importing the production `_real_harmonic` function.

## Final code verdict

```text
CURRENT_R10_CODE: bounded numerically consistent, authority-incomplete
R10A_TEST_SOURCE: test-only and DAG-admissible
NEXT REQUIRED EVIDENCE: exact local 16-test / 13-failure / 3-control RED
PRODUCTION PATCH BEFORE RED: forbidden
```
