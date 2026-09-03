# BASS–REC Source Protocol R6 — Authority Hardening TDD RED

**Date:** 2026-09-04  
**Stage:** `BASS_REC_SOURCE_R6_AUTHORITY_HARDENING_RED`  
**Disposition:** `EXPECTED_RED / PRODUCTION_UNCHANGED`  
**Authority effect:** `NONE`

## Exact parent and newly closed prerequisite

```text
repository  cosmosapjw-quantum/bass
parent PR   #112
parent      fc4d21b92a1abd1e9b35178f7d666831fc5c827d
parent tree c0caf9b8017d4c3850a1a99629246164fd4b27ff
```

The user-supplied R5C differential receipt established:

```text
classification=PASS_NO_BACKEND_REGRESSION
base=d81ad12f795b6ac6d57293502e75426ed1dbbb1a
candidate=fc4d21b92a1abd1e9b35178f7d666831fc5c827d
base_rc=0
candidate_rc=0
failure_sets_identical=true
source_build_override=1
wheel_sha256=bf5a59534ffc9d6f9c3410aa19319f18a4a8a7a9761bcd61c5da8c8627ddf609
```

This closes behavior-level backend nonregression for the one-file R5 candidate. It does not convert the locally built wheel into a trusted production payload.

## Purpose of this RED

R5 proved a narrow receiving protocol, but its public construction and metadata remain too weak for solver wiring. R6 freezes the next bounded semantics before changing production code.

The new focused test requires:

1. **validated construction** — the public dataclass constructor cannot bypass factory validation or inject a forged payload hash;
2. **signed-zero canonicalization** — `+0.0` and `-0.0` represent one physical rate and one payload identity;
3. **photon/boson binding** — the current stimulated source is explicitly photon/Bose, not a generic kinetic source;
4. **schema transition** — the strengthened payload is versioned as `bass.source_authority.constant_pair.v2`;
5. **source-kind firewall** — a constant pointwise pair cannot masquerade as an integrated source witness;
6. **moment-map binding** — every integrated witness is tied to its target state, moment map, radial-weight family, and source identity;
7. **finite arithmetic** — binary64 overflow in source action or time-basis conversion raises a typed error;
8. **survivor controls** — source-off, negative-`chi_affine`, and expanding-Q-time domain behavior remain unchanged.

## Why moment-map binding is load-bearing

Two frequency distributions can have the same energy-integrated angular state while producing different source integrals under a different radial weight. A generic `SOURCE_INTEGRATED_WITNESS` tag therefore cannot authorize both `G(e)` and `J^(i)_{A_l}`. The witness must name the exact projection it certifies.

## Why statistics binding is load-bearing

The implemented law is

```text
C_B[f] = eta (1+f) - kappa f,
```

which is bosonic. A fermionic source has `1-f`; the two agree at vacuum and differ by `2 eta f` away from vacuum. A generic class name without particle/statistics metadata is therefore unsafe on a repository that also contains neutrino and other kinetic lanes.

## Expected RED

The exact R5 parent is expected to fail the new test because it currently:

- exposes the generated dataclass constructor;
- preserves signed zero in `float.hex()` payloads;
- has no species/statistics fields or v2 schema;
- allows `constant_pair(... SOURCE_INTEGRATED_WITNESS)`;
- admits integrated states without a moment-map binding;
- has no `IntegratedMomentMapBinding` or `SourceArithmeticError`;
- returns nonfinite arithmetic results rather than failing closed.

The source-off and expanding-domain control tests should continue to pass.

## Scope firewall

No production source, backend, solver, Rust, PSTF, Q, face, provider, observable, or statistics module is changed in this stage. No physical REC data are imported.

## Next node

```text
BASS_REC_SOURCE_R6_AUTHORITY_HARDENING_GREEN
```

The GREEN may modify only `bianchi/source_authority.py` plus the R6 test/doc packet. Grid/PSTF adapters, Mode-A/J closures, physical source data, jumps, two-photon/Raman kernels, solver wiring, output, and statistics remain later nodes.

## Claim boundary

```text
PASS_R5C_BEHAVIOR_LEVEL_BACKEND_NONREGRESSION
R6_HARDENING_CONTRACT_COMMITTED
R6_GREEN_NOT_YET
TRUSTED_PRODUCTION_WHEEL_NOT_ESTABLISHED
NO_SOLVER_SOURCE_WIRING
NO_GRID_PSTF_SOURCE_PARITY
NO_PHYSICAL_FACE_OR_PROVIDER
NO_PASS_RF04
```
