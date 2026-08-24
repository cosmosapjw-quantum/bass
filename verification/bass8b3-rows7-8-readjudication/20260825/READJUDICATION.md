# BASS-8B.3 rows 7–8 re-adjudication

## Verdict

```text
row 7 — collision equilibrium / projector
PARTIAL_WITH_EXPLICIT_GAP

row 8 — paired left invariant
PARTIAL_WITH_EXPLICIT_GAP
```

The mathematical acceptance criteria are supported at receipt level by the sealed
2A→2B.0→2B.1→2B.2→2B.3 chain. In particular, the final receipts report a typed
electron-state jet, a direction-dependent full-generator rate, a paired left dual,
a generic moving-bundle differential, right/left null identities, a normalized
rank-one projector, differentiated null identities, and the Kato commutator.

The rows are **not** promoted to `AUTHORITY_COMPLETE` because the exact final 2B.3
binary package cannot be re-materialized under its declared checksum in the active
runtime. The declared final sidecar is:

```text
23d7ff71dff3d10f15efbebefe52839effa28bfb93fba5b725ab2faa2c12b0cc
```

The file currently present under the same filename is a different, earlier archive:

```text
size      514231 bytes
SHA-256   5532588b554029d31d9fff1cd9ea994862a354436a1febc6a2c19c63de3dbace
manifest  51 entries
fresh test surface 28/28
```

Its ZIP CRC and its own bounded replay pass, but it is not the checksum-addressed
633703-byte final package described by the GitHub seal and final verification log.
A passing older candidate cannot substitute for missing final bytes.

## Physics/mathematics assessment

No positive formula conflict was found. The selected carrier is a paired finite
physical collocation carrier, not a finite-ell exact boost matrix. The evidence
chain supports, on that declared discrete carrier and away from exact vacuum,

```text
C r = 0
 a^T C = 0
 a^T r = 1
 P^2 = P
 C P = P C = 0
 differentiated right/left null identities
 P Pdot + Pdot P - Pdot = 0
 K = [Pdot,P]
 [K,P] = Pdot
```

Generic three-vector covariance, the Type-II aligned restriction, the
non-identifiability of a collision-selected projector at exact vacuum, and the
cancellation of a nonzero global scalar opacity from normalized P/Pdot/K are also
supported by the final receipts.

## Scope

This is a bounded discrete finite-carrier result. It is not a continuum
finite-electron-tilt theorem, not Rust lowering, not a runtime solver, and not a
VI0 classifier.

## Matrix effect

```text
before: 6 COMPLETE / 2 PARTIAL / 2 MISSING / 0 CONFLICT
after:  6 COMPLETE / 4 PARTIAL / 0 MISSING / 0 CONFLICT
```

Rows 7–8 move from `MISSING` to `PARTIAL_WITH_EXPLICIT_GAP`; they do not move to
`COMPLETE`. Rows 9–10 remain partial.
