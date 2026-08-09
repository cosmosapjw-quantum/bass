# BASS Route A — first-slice public API v1

**Contract ID:** `bass.api.v1/a0-first-slice`

**Machine mirror:** `contracts/a0/first_slice_api_v1.json`

This file freezes the public contract for the first executable Route A slice. It specifies
an API; it does not claim that the API is implemented. The only public import surface is
`bass.api.v1`. `bass.__init__` must not re-export provisional internals.

## Public symbols

| Symbol | Exact contract |
|---|---|
| `API_CONTRACT_ID` | String constant equal to `bass.api.v1/a0-first-slice` |
| `get_conventions() -> ConventionSpec` | Return the immutable, non-switchable BASS v1 convention record. |
| `list_families() -> tuple[FamilySpec, ...]` | Return exactly eleven canonical families in order `I, II, III, IV, V, VI_0, VI_h, VII_0, VII_h, VIII, IX`; `VI_h` contains exceptional-branch metadata for `VI_-1/9`. Registry presence is not runtime support. |
| `select_family(family_id: FamilyID, *, h: Fraction \| float \| numpy.float64 \| None = None) -> FamilySelection` | Apply the dispatch rules below. No positional `h`, string coercion, or proximity dispatch. |
| `capabilities() -> CapabilitySnapshot` | Return immutable rows for `registry`, `geometry`, `background`, `transport`, `output`, and `statistics`, each in `READY`, `LOCKED_PENDING_EVIDENCE`, or `OUT_OF_SCOPE`. |
| `CODATA_2022` | Immutable `PhysicalConstants` record with exact SI `c`, 2022 CODATA `G`, its standard uncertainty, units, year, and source URI. |
| `A0_BACKGROUND_BUDGET_V1` | Immutable `ResidualBudget` with `atol=0` per channel and `rtol=1024*2^-53`. |
| `FLRWPoint(...)` | Frozen constructor with the exact fields and units below. |
| `evaluate_flrw_residuals(point: FLRWPoint, *, constants: PhysicalConstants = CODATA_2022) -> FLRWResidualSet` | Evaluate the three frozen term lists and return raw values and scales; bind both `point_sha256` and `constants_sha256`; do not decide PASS/FAIL. |
| `check_flrw_residuals(residuals: FLRWResidualSet, *, budget: ResidualBudget = A0_BACKGROUND_BUDGET_V1) -> ResidualCheckSet` | Return `PASS` or `FAIL` per channel and bind `residuals_sha256` plus `budget_sha256`. Only the exact default constants and budget may support an A0 characterization claim; custom values are diagnostic. |
| `canonical_bytes(record: CanonicalRecord) -> bytes` | Serialize only the exported immutable-record union using the exact frame below. Arbitrary-object serialization is forbidden. |
| `content_sha256(record: CanonicalRecord) -> str` | Lowercase hexadecimal SHA-256 of `canonical_bytes(record)`. |

The exported record and enum types are `ConventionSpec`, `FamilyID`, `FamilySpec`,
`FamilySelection`, `CapabilityState`, `CapabilityRow`, `CapabilitySnapshot`,
`PhysicalConstants`, `FLRWPoint`, `ResidualChannelID`, `ResidualChannel`,
`FLRWResidualSet`, `ResidualBudget`, `CheckStatus`, `ResidualCheck`, and
`ResidualCheckSet`.

The exported exception hierarchy is rooted at `BASSError` and contains
`ConventionError`, `ShapeTypeError`, `DomainError`, `ConstraintViolation`,
`IntegrationFailure`, `ConvergenceFailure`, `UnsupportedSector`, and `BackendMismatch`.
Only errors assigned below may be emitted by the first-slice functions; the remaining
classes are reserved stable names and are not evidence that their sectors exist.

## Exact record fields

All records are frozen and use immutable tuples rather than mutable collections.

| Record | Ordered fields |
|---|---|
| `ConventionSpec` | `contract_id: str`; `metric_id: str`; `riemann_id: str`; `orientation_id: str`; `physical_time_id: str`; `kinematic_expansion_id: str`; `adm_relation_id: str`; `structure_id: str`; `units_id: str` |
| `FamilySpec` | `family_id: FamilyID`; `class_id: str`; `h_kind: str`; `h_domain: str \| None`; `aliases: tuple[str,...]`; `exceptional_branches: tuple[str,...]`; `capabilities: CapabilitySnapshot` |
| `FamilySelection` | `requested_id: FamilyID`; `canonical_id: FamilyID`; `branch_id: str`; `h_exact: Fraction \| None`; `h_binary64: float \| None`; `registry_only: bool`; `frame_parity: str \| None` |
| `CapabilityRow` | `layer: str`; `state: CapabilityState`; `evidence_sha256: str \| None` |
| `CapabilitySnapshot` | `rows: tuple[CapabilityRow,...]` in the fixed layer order above |
| `PhysicalConstants` | `c_m_s: float`; `G_m3_kg_s2: float`; `G_standard_uncertainty_m3_kg_s2: float`; `codata_year: int`; `source_uri: str` |
| `FLRWPoint` | `t_s: float`; `H_s_inv: float`; `dH_dt_s_inv2: float`; `rho_energy_J_m3: float`; `d_rho_energy_dt_J_m3_s: float`; `pressure_J_m3: float`; `R3_m_inv2: float`; `Lambda_m_inv2: float` |
| `ResidualChannel` | `channel_id: ResidualChannelID`; `raw_value: float`; `unit_id: str`; `reference_scale: float`; `relative_value: float \| None`; `ordered_terms: tuple[float,...]` |
| `FLRWResidualSet` | `contract_id: str`; `point_sha256: str`; `constants_sha256: str`; `channels: tuple[ResidualChannel,...]` in `HAMILTONIAN, CONTINUITY, RAYCHAUDHURI` order |
| `ResidualBudget` | `contract_id: str`; `hamiltonian_atol_s_inv2: float`; `continuity_atol_J_m3_s: float`; `raychaudhuri_atol_s_inv2: float`; `rtol: float` |
| `ResidualCheck` | `channel_id: ResidualChannelID`; `status: CheckStatus`; `limit: float`; `budget_sha256: str` |
| `ResidualCheckSet` | `status: CheckStatus`; `residuals_sha256: str`; `budget_sha256: str`; `checks: tuple[ResidualCheck,...]`; `failed_channels: tuple[ResidualChannelID,...]` |

`CheckStatus` has exactly `PASS` and `FAIL`. A finite residual miss is a returned `FAIL`,
not an exception. `relative_value` is `None` exactly when `reference_scale==0`.

`CODATA_2022.c_m_s` is exactly `299792458.0` and has zero uncertainty by SI definition.
`CODATA_2022.G_m3_kg_s2` is `6.67430e-11` and its standard uncertainty is `1.5e-15`,
with source URI `https://physics.nist.gov/cuu/pdf/JPCRD2022CODATA.pdf`.

## Scalar and family dispatch

A real scalar accepts only exact built-in `float` or exact NumPy `float64`; `bool`, integer,
string, complex, float32, nonfinite values, and scalar subclasses are rejected. Zero is
allowed and normalized to positive zero for serialization. Nonzero subnormal input is
rejected. The implementation copies accepted values into canonical little-endian binary64.

Exact family tags use `fractions.Fraction` with a positive denominator. Rules are:

1. non-parameterized families reject `h`;
2. `III` needs no `h` and is the canonical `VI_h(-1)` alias;
3. `VI_0` and `VII_0` are named exact boundary branches and reject `h`;
4. `VI_h` requires `h<0`; exact `Fraction(-1,1)` resolves to `III`, exact
   `Fraction(-1,9)` resolves to branch `VI_-1/9`, and exact zero is rejected in favor of
   `VI_0`;
5. `VII_h` requires `h>0`; exact zero is rejected in favor of `VII_0`;
6. a binary64 `h` parameterizes only the explicitly requested generic family. It never
   selects an alias, boundary, or exceptional branch by equality or proximity. Binary64
   `-1.0` and `0.0` are rejected as reserved exact values; nearby values remain generic.

The generic domains include irrational real parameters through their declared binary64
approximations. The selected value and representation kind are preserved; no claim of exact
irrational representation is made.

## Residual term lists and checks

The exact ordered terms, units, scale algorithm, negative controls, and analytic fixtures
are frozen in `contracts/a0/characterization_v1.json`. `evaluate_flrw_residuals` uses
`math.fsum` for both signed residuals and absolute reference scales. An empty term list,
nonfinite or overflowed term, nonzero subnormal term, underflow to zero, or failed scale
construction raises rather than producing a check result.

For scale zero, `check_flrw_residuals` uses `abs(raw)<=atol`; under the A0 budget this means
exact zero. Otherwise it uses `abs(raw)<=atol+rtol*reference_scale`. The aggregate is PASS
only when all three channel checks pass.

An A0 PASS claim additionally requires
`residuals.constants_sha256==content_sha256(CODATA_2022)`,
`check.residuals_sha256==content_sha256(residuals)`, and
`check.budget_sha256==content_sha256(A0_BACKGROUND_BUDGET_V1)`. A changed point,
constant, residual term/value, or budget therefore invalidates every downstream check.

## Exception versus status mapping

Every exception has `code: str` and bounded allowlisted metadata. Metadata keys are limited
to `field`, `expected`, `received_type`, `shape`, `unit_id`, `family_id`, `branch_id`, and
`contract_id`; each textual value is at most 256 Unicode scalar values. Hostile object
values, arbitrary `repr`, credentials, and raw exception text are never retained.

| Condition | Outcome |
|---|---|
| Wrong convention or unresolved frame/parity adapter | `ConventionError`: `E_CONVENTION_ID`, `E_FRAME_UNRESOLVED`, or `E_PARITY_UNRESOLVED` |
| Wrong scalar/container type, dtype, shape, subclass, nonfinite, subnormal, or immutable-storage failure | `ShapeTypeError`: `E_TYPE`, `E_DTYPE`, `E_SHAPE`, `E_SUBCLASS`, `E_NONFINITE`, `E_SUBNORMAL_UNSUPPORTED`, or `E_IMMUTABLE` |
| Unsupported record/framing/metadata or hash mismatch | `ShapeTypeError`: `E_SERIALIZATION_CONTRACT` or `E_CONTENT_HASH` |
| Family, `h`, time, or constants outside the declared domain | `DomainError`: `E_FAMILY_ID`, `E_H_REQUIRED`, `E_H_FORBIDDEN`, `E_H_DOMAIN`, `E_H_SPECIAL_FLOAT`, `E_TIME_DOMAIN`, or `E_CONSTANT_DOMAIN` |
| Requested locked/out-of-scope capability | `UnsupportedSector`: `E_SECTOR_LOCKED` or `E_SECTOR_OUT_OF_SCOPE` |
| Finite residual exceeds its budget | Returned `ResidualCheck(status=FAIL)`; no exception |

`FLRWPoint.t_s` and both physical constants must be strictly positive; all other point
fields may have either sign but must satisfy the scalar contract. Positivity of total
energy or a particular equation of state is a case-specific physical constraint, not a
silent constructor assumption.

## Canonical bytes and hash frame

The exact byte frame is

`b"BASS-CANONICAL-v1\0" || uint64_be(metadata_length) || metadata_json || uint64_be(payload_length) || payload`.

`metadata_json` is UTF-8, NFC-normalized, sorted-key, compact JSON with separators `,` and
`:`, and `allow_nan=false`. It contains no floating values. It contains the API contract ID,
record type, schema version `1`, ordered payload-field descriptors, unit IDs, shapes,
dtypes, and all non-floating enum/string/integer/bool/null fields. Exact rationals are
stored as signed decimal numerator and positive decimal denominator strings.

All floating fields occur only in `payload`, concatenated in the record-field order as
little-endian IEEE-754 binary64. Tuple elements retain tuple order. Negative zero is written
as positive zero. Payload descriptors use dtype `<f8`, byte offsets, and exact scalar/tuple
shapes. The two lengths are unsigned 64-bit big-endian integers. Trailing bytes, unknown
metadata keys, duplicate fields, and version coercion are errors.

`content_sha256` hashes the complete frame, not the payload alone. Canonical serialization
is defined only for the exported record union; this prevents arbitrary objects from
entering the evidence channel.
