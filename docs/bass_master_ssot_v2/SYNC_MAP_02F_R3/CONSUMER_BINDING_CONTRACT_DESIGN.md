# SYNC-MAP-02F-R3 consumer-binding contract design

## Status and authority

This document specifies a **BASS-only** child of the bounded semantic closeout in PR #119. It is a design contract, not a runtime-parity certificate.

```text
exact parent commit
4a78ea05310126f720719e369a782466fdd1111e

validated closeout source head
25dc6a75fc781d329dbe9a2b6d68eeb5f8a6607e

parent local gate
Python 10/10 + Wolfram 17/17 + strict JSON + SHA256SUMS + exit 0
```

No REC, REI, or HTT source may be modified or executed by this stage. Consumer source identities are read-only pins. Literature has `authority_effect=NONE` over formula hashes, source status, acceptance, or promotion.

## Purpose

The previous stages establish:

1. six BASS-owned formula identities;
2. six distinct state surfaces;
3. ten formula–consumer semantic relations and eleven source roles;
4. four projection/closure certificate families;
5. a bounded semantic closeout with all runtime and science promotions withheld.

R3 converts those facts into typed requests that a consumer repository may later accept, reject, or validate. It does **not** infer implementation parity from formula occurrence or source-symbol occurrence.

The distinction is normative:

```text
BindingRequest
  = exact formula identity
  + consumer and source-role pin
  + convention/domain/unit adapters
  + state-surface scope
  + required evidence and acceptance gates
  + an explicitly non-promotional status

RuntimeParityCertificate
  = separately authorized execution in the owning consumer repository
  + exact source identity
  + required fixtures and residuals
  + certificate instances, not merely certificate schemas
```

## Exact count contract

```text
consumer repositories                  3
formula binding requests              10
source-role pins                      11
named source symbols                  12
explicit absent implementation slots   1
owner formulas                          6
state surfaces                          6
certificate families                    4
blocked promotions                     13
cross-repository source mutations       0
runtime parity admissions               0
provider promotions                     0
science promotions                      0
```

## Formula authority

The implementation contract must pin the following six IDs and semantic hashes exactly.

| Formula ID | Semantic hash | Dimension |
|---|---|---|
| `BASS.FRAME.ABERRATED_DIRECTION.001` | `b20aa445f5e2890674480a6e8e71fd919aa9efd13a1a8c4780e98b67b9974eec` | `1` |
| `BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001` | `99ededbaa9c04ab51f2ffda4c19a55236b243021271445d3dad916e2e660c143` | `K` |
| `BASS.FRAME.DOPPLER_FACTOR.001` | `fb56218a0256edde59a1d89eb4e3ce69ce82800d852908ee84ce8aec83f2fb47` | `1` |
| `BASS.FRAME.SOLID_ANGLE_JACOBIAN.001` | `0436b513724b09fe826aa486c5dd3def19d0dc5e6daf9fabdd8d899fd1618dc4` | `1` |
| `BASS.PHOTON.DIRECTION_FLOW.001` | `1eb20b3b46b596139d781d529a1511df983c2b6c00fbe85208ef03e7888f08ce` | `L^-1` |
| `BASS.PHOTON.ENERGY_DRIFT.001` | `840fe1d68d87b78bb5b5d831fb3d8025b26c29fda1f9da49b0f387e1a8d7bcfd` | `L^-1` |

The registry semantic hash remains:

```text
5951f566d911c81848743055c1573f6d11b0b00937d36747b71e6bc12dd96416
```

## State-surface authority

The contract must preserve all six state types and may not collapse them into a generic “radiation state”.

```text
GRID_F_Q_E
PSTF_F_AELL_Q
J_I_AELL
G_ANGULAR_ENERGY
FLUID_COMPONENT_SUMMARY
POLARIZED_COHERENCY
```

Binding policy:

```text
GRID_F_Q_E <-> PSTF_F_AELL_Q
  representation relation only on a declared complete or band-limited subspace
  ANGULAR_REPRESENTATION_CERTIFICATE required for numerical parity

PSTF_F_AELL_Q -> J_I_AELL
GRID_F_Q_E    -> G_ANGULAR_ENERGY
  noninvertible spectral projections
  SPECTRAL_PROJECTION_CLOSURE_CERTIFICATE required

kinetic state -> FLUID_COMPONENT_SUMMARY
  MOMENT_EXCHANGE_CERTIFICATE required

scalar state -> POLARIZED_COHERENCY
  implicit promotion forbidden
  POLARIZED_SCREEN_CERTIFICATE required before any polarized runtime claim
```

No certificate schema is itself a certificate instance.

## Binding-request inventory

The exact request order is part of the contract.

### REC

| Pair ID | Formula | Read-only role pin | Binding status |
|---|---|---|---|
| `02F-R2A-REC-ABERRATION` | aberrated direction | `ROLE-REC-ABERRATION` | runtime validation required |
| `02F-R2A-REC-DOPPLER` | Doppler factor | `ROLE-REC-DOPPLER` | runtime validation required |
| `02F-R2A-REC-DIRECTION-FLOW` | direction flow | `ROLE-REC-DIRECTION-FLOW` | runtime validation required |
| `02F-R2A-REC-ENERGY-DRIFT` | energy drift | `ROLE-REC-ENERGY-DRIFT` | runtime validation required |

REC may request bindings on the frequency-resolved primary pair `GRID_F_Q_E` and `PSTF_F_AELL_Q`. Any numerical transform between them remains certificate-gated. `J_I_AELL` and `G_ANGULAR_ENERGY` remain unavailable for a generic frequency-dependent source without a spectral-projection/closure certificate. Polarized REC remains outside this stage.

The convention and unit contract retains:

```text
metric signature              (-,+,+,+)
spatial orientation           epsilon_123=+1
photon propagation direction  e
outward sky direction         n_sky=-e
ray-length parameter          s=c*t
proper-time adapters          R_t=c*R_s, V_t=c*V_s
normal-frame sector           A_normal^a=0 for the pinned geodesic-normal formulas
boost domain                  beta_squared<1
```

### REI

| Pair ID | Formula | Read-only role pin | Binding status |
|---|---|---|---|
| `02F-R2A-REI-DIRECTION-FLOW` | direction flow | `ROLE-REI-DIRECTION-FLOW-ABSENT` | blocked: absent generic implementation |
| `02F-R2A-REI-ENERGY-DRIFT` | energy drift | `ROLE-REI-ENERGY-DRIFT-CONTROL` | restricted control subspace only |

The REI direction-flow role must remain an absent implementation slot. It may not acquire source symbols, `implements_full_formula=true`, or generic parity through this BASS-only stage.

The REI energy-drift role is limited to:

```text
FLRW_OR_EXACTLY_ISOTROPIC_ANGULAR_SUBSPACE
```

The relation

```text
R_REI=-H
R_BASS=-H-sigma_ab e^a e^b
```

therefore does not support generic Bianchi transport parity. Any generic promotion requires a separately implemented angular transport state and consumer-owned execution.

### HTT

| Pair ID | Formula | Read-only role pin(s) | Binding status |
|---|---|---|---|
| `02F-R2A-HTT-ABERRATION` | aberrated direction | `ROLE-HTT-ABERRATION-BIDIRECTIONAL` | runtime validation required |
| `02F-R2A-HTT-DOPPLER` | Doppler factor | `ROLE-HTT-DOPPLER-BIDIRECTIONAL` | runtime validation required |
| `02F-R2A-HTT-SOLID-ANGLE` | solid-angle Jacobian | `ROLE-HTT-SOLID-ANGLE-ORACLE` | oracle validation required |
| `02F-R2A-HTT-BLACKBODY-T` | blackbody temperature pullback | `ROLE-HTT-BLACKBODY-FULL`, `ROLE-HTT-BLACKBODY-PREPULLED` | full and partial APIs must remain distinct |

HTT consumes observable sky fields rather than a BASS kinetic state surface in these four bindings. A full thermodynamic-temperature pullback evaluates the source field at the inverse-aberrated direction and applies Doppler weight one. A prepulled-value primitive performs only the weighted multiplication after the caller has supplied values at the transformed directions. The partial primitive may not be promoted to the full formula.

Spin weight, Doppler weight, field spectrum, sky domain, and mask/estimator treatment are independent metadata and must not be collapsed into a single “boosted map” flag.

## Exact source-role pins

### REC

```text
source commit  c4bf37d7271caf651bca41b6eaab8caff436452b
source path    src/full_bianchi_hyrec/background/characteristics.py
source blob    f71ec2607daac808b871279ad0893d4653169343
symbols        aberrate_direction
               doppler_factor
               normal_frame_characteristic.D0_direction_normal_s_inv
               normal_frame_characteristic.R_normal_s_inv
```

### REI

```text
source commit  f4eb2c893ce6449f8899ab6f02c83421fc7c7019
source path    src/rei_bianchi/b2b_physical_model.py
source blob    b3cc5e45988687b76d5be04c6335009b4c9bd17f
symbols        [] for generic direction flow
               SpectrumLane.redshift_coeff for the restricted H-only control
```

### HTT

```text
source commit  29427a1f7f2c5d46e43ffe03053c4ac13e969228
source path    htt/obsstat/lorentz_sky_pullback.py
source blob    c518cdd0dcdd3ca628c71f6dd9e6a75e174ba805
symbols        aberrate_sky_direction
               deaberrate_sky_direction
               doppler_factor_unboosted
               doppler_factor_boosted
               solid_angle_jacobian
               pullback_thermodynamic_temperature_field
               thermodynamic_temperature_pullback
```

The eleven role rows contain twelve named symbols because two HTT bidirectional roles each contain two symbols and the REI absent role contains none.

## Required acceptance-gate templates

Every binding request must identify one or more gate templates. The implementation must define at least these templates.

### `FORMULA_IDENTITY_GATE`

Required evidence:

```text
formula_id
formula_semantic_hash
formula_registry_semantic_hash
consumer_repository
consumer_source_commit/path/blob
consumer_source_symbols
```

### `CONVENTION_DOMAIN_UNIT_GATE`

Required evidence:

```text
source and target frame roles
direction convention
metric and orientation convention
parameter and unit conversion
domain and subspace restrictions
input policy
numerical policy
```

### `ANGULAR_REPRESENTATION_GATE`

Required certificate family:

```text
ANGULAR_REPRESENTATION_CERTIFICATE
```

This gate is required before grid/PSTF numerical parity. It must record basis, normalization, measure, quadrature/transform, target and work cutoffs, both round-trip residuals, conditioning/stability, and input/output state hashes.

### `SPECTRAL_PROJECTION_GATE`

Required certificate family:

```text
SPECTRAL_PROJECTION_CLOSURE_CERTIFICATE
```

This gate is required before a generic `J` or `G` source claim. Full-source quadrature or a proved multiplication-closure/invariant-subspace result is mandatory. A scalar effective opacity is not admitted by occurrence alone.

### `MOMENT_EXCHANGE_GATE`

Required certificate family:

```text
MOMENT_EXCHANGE_CERTIFICATE
```

This gate must include equal-and-opposite radiation/matter four-force and number, energy, and momentum ledgers.

### `POLARIZED_SCREEN_GATE`

Required certificate family:

```text
POLARIZED_SCREEN_CERTIFICATE
```

This gate must include the screen projector, transported screen basis, U(1) connection, spin-phase convention, polarized collision operator, and coherency Hermiticity/positivity policy.

### `RESTRICTED_SUBSPACE_GATE`

Required evidence:

```text
exact subspace predicate
proof or exact residual on that subspace
negative witness outside the subspace
explicit prohibition of generic promotion
```

## Authorization firewall

Every field below must be exactly false.

```text
consumer_source_mutation_authorized
runtime_parity_admitted
provider_promotion_authorized
science_promotion_authorized
merge_or_ready_transition_authorized
formula_occurrence_implies_runtime_parity
source_role_pin_implies_runtime_parity
certificate_schema_implies_runtime_certificate
```

The thirteen promotions already blocked by the parent closeout remain blocked:

```text
CROSS_REPOSITORY_CONSUMER_RUNTIME_PARITY
GRID_PSTF_NUMERICAL_PARITY
J_SPECTRAL_CLOSURE_ADMISSION
G_SPECTRAL_CLOSURE_ADMISSION
FLUID_EXCHANGE_RUNTIME_PASS
SCREEN_BASIS_TRANSPORT_IMPLEMENTED
POLARIZED_COLLISION_RUNTIME
POLARIZED_ARBITRARY_ELL_COMPILER
BASS_BACKGROUND_PROVIDER
GLOBAL_MATTER_TILT
LIKELIHOOD_READY
SCIENCE_PROMOTION
PASS_RF04
```

## Stage DAG

```text
BOUNDED_SEMANTIC_CLOSEOUT
  -> CONSUMER_BINDING_CONTRACTS
      -> REC_RUNTIME_VALIDATION
      -> REI_RUNTIME_VALIDATION
      -> HTT_RUNTIME_VALIDATION

REC_RUNTIME_VALIDATION ---\
REI_RUNTIME_VALIDATION ----> CROSS_REPOSITORY_PARITY_FEDERATION
HTT_RUNTIME_VALIDATION ---/
```

The three runtime-validation nodes are future repository-owned stages. Their names in this DAG are routing declarations, not assertions that they exist or pass.

## Failure taxonomy

```text
IDENTITY_MISMATCH
COUNT_CONTRACT_MISMATCH
PAIR_COVERAGE_MISMATCH
SOURCE_ROLE_PIN_MISMATCH
CONVENTION_OR_UNIT_ADAPTER_MISSING
STATE_SURFACE_COLLAPSE
CERTIFICATE_FAMILY_MISSING
RESTRICTED_SUBSPACE_ESCALATION
ABSENT_IMPLEMENTATION_PROMOTED
PARTIAL_API_PROMOTED_TO_FULL
AUTHORIZATION_FIREWALL_WEAKENED
DAG_MALFORMED_OR_CYCLIC
LITERATURE_AUTHORITY_ESCALATED
EXECUTION_ENVIRONMENT_BLOCKED
```

Software-contract failure and execution-environment failure must remain separate.

## Test-first stop condition

The current PR intentionally publishes the mutation-sensitive test before the implementation surfaces. Before production contract code is added, the RED test must be observed to fail because the following expected files are absent:

```text
docs/bass_master_ssot_v2/SYNC_MAP_02F_R3/CONSUMER_BINDING_CONTRACTS.json
scripts/verify_sync_map02f_r3_consumer_bindings.py
scripts/run_sync_map02f_r3_consumer_bindings_local.sh
wolfram/BASS/Kernel/IR/ConsumerBindingContractsR3.wl
wolfram/BASS/Tests/ConsumerBindingContractsR3.wlt
wolfram/scripts/run_consumer_binding_contracts_r3.wls
```

A GitHub job with `runner_id=0` and `steps=[]` is not an observed RED test. It is an execution-environment blocker.

After an expected RED is observed, the minimum GREEN implementation may add only the surfaces above plus documentation and source-packet workflow steps. It may not mutate a consumer repository or include a runtime parity result.

## Post-GREEN routing

A locally GREEN R3 contract routes to three separately authorized nodes:

```text
REC_BINDING_RUNTIME_VALIDATION
REI_BINDING_RUNTIME_VALIDATION
HTT_BINDING_RUNTIME_VALIDATION
```

Each node must execute in the owning repository against the exact pinned source identity. Only after all requested per-repository gates have independent receipts may a cross-repository parity federation be considered.
