# Receipt — BASS-8B.2B.3 projector / paired-left / Kato audit

## Decision

`PASS_BOUNDED_DISCRETE_PROJECTOR_LEFT_KATO_AUTHORITY`

This closes the selected finite-carrier audit node only. It does not itself
promote authority rows 7 or 8; those remain for BASS-8B.3 re-adjudication.

## Frozen authority lineage

- BASS-8B.2A typed electron state jet: PASS
- BASS-8B.2B.0 paired physical carrier: PASS
- BASS-8B.2B.1 rate / paired left dual: PASS
- BASS-8B.2B.2 moving bundle differential: PASS
- BASS-8B.2B.3 complete projector / left / Kato audit: PASS bounded

## Packaged evidence

- package manifest: 57/57 PASS
- focused tests: 15/15 PASS
- predecessor 2B.0: 6/6 PASS
- predecessor 2B.1: 17/17 PASS
- predecessor 2B.2: 15/15 PASS
- combined tests: 53/53 PASS
- exact SymPy algebra: PASS
- exact Wolfram algebra: PASS
- actual xAct/xTensor 1.3.0 screen geometry: PASS
- randomized generic-vector cases: 500 PASS
- finite-difference cases: 80 PASS
- SO(3) cases: 120 PASS
- hostile mutations: 5 classes, 500/500 detected per class
- physical spectral nullity: {1}
- minimum tested nonzero shape gap: 0.14050598095073813
- plot evidence: 4/4 present in the full package

The exact package has size 633703 bytes and SHA-256
`23d7ff71dff3d10f15efbebefe52839effa28bfb93fba5b725ab2faa2c12b0cc`.
The GitHub commit preserves its checksum and the load-bearing audit receipts and
Wolfram/xAct replay sources. It does not claim that the binary package or PNG
plots are embedded.

## Wolfram / xAct qualification

The project xAct archive and the official temporary-download archive have the
same SHA-256:

`7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be`

The fresh stateless Wolfram run loaded xTensor 1.3.0 and xPerm 1.2.4 and
returned exact zero for screen-projector idempotence, tangent, trace, and
differentiated-transversality residuals. Because the connected kernel cannot
see the chat container's `/mnt/data`, that replay used the checksum-identical
official archive in a temporary directory. The preserved host runner prepends
the project `/mnt/data/xact_stage` path and is not mislabeled as having been
executed by the stateless plugin.

## Architecture and nonclaims

- frontend/reference/validation: pure Python + NumPy/SciPy/SymPy/pytest
- performance backend target: Rust 1.94.1 locked/offline-capable
- excluded active target: JAX/JAXlib/Equinox/Diffrax
- Rust lowering: not performed
- runtime/time stepper: not wired
- classifier: not started
- PR / merge / tag: none

## Next node

`BASS-8B.3_ROWS7_8_READJUDICATION`
