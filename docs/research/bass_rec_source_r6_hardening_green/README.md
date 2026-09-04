# BASS–REC Source Protocol R6 — Authority Hardening GREEN Candidate

**Date:** 2026-09-04  
**Stage:** `BASS_REC_SOURCE_R6_AUTHORITY_HARDENING_GREEN`  
**Current disposition:** `SOURCE_CREATED / LOCAL_EXACT_REPLAY_REQUIRED`  
**Authority effect:** protocol-only; no solver or physical-source admission

## Executed RED prerequisite

The user executed the coherent R6 RED branch in a detached exact-head worktree and supplied:

```text
classification=PASS_EXPECTED_R6_AUTHORITY_HARDENING_RED
commit=0a4875e5c18419a672c164eb5c849f3f4ab01571
tree=89c131a2cd2d386555f49745c06e6f74ca34ca8a
source_blob=f9eceaa02e82c746045df255af2ce674dab1bb75
r5_test_blob=db336d64633d8a9552bc3613c588a00f33404a4d
r6_test_blob=49be9546c4655bc5ca330bc31ae2daf07578b74f
compile_rc=0
r5_survivor_rc=0
r6_expected_red_rc=0
clean_worktree=true
```

The accompanying upload is named
`BASS_REC_SOURCE_R6_RED_20260903T221626Z.zip`.  The exact terminal summary is
preserved below as a transcript-derived receipt; this branch does not claim that
the ZIP bytes were independently ingested or rehashed by the GitHub connector.

## Exact GREEN source candidate

```text
parent RED head  0a4875e5c18419a672c164eb5c849f3f4ab01571
source commit    92d67dc79cf645947beb93ac01a9505ee277dabd
source tree      65cb63e6d08e80e9a8f38f83e3a536cb0a00a693
source path      bianchi/source_authority.py
source blob      869677390004f68aef9f547e6556f5f1c15bd012
```

The implementation remains standard-library-only and changes no background,
transport, collision, hierarchy, backend, output, provider, or statistics path.

## Implemented R6 semantics

1. `SourceAuthorityBundle` is valid-by-factory: its public constructor always
   raises `TypeError`, and callers cannot inject `payload_sha256`.
2. Nonnegative scalar rates and occupations canonicalize IEEE-754 `-0.0` to
   `+0.0` before storage and hashing.
3. The constant-pair source is explicitly bound to
   `SourceSpecies.PHOTON` and `SourceStatistics.BOSON`.
4. The payload schema is versioned as
   `bass.source_authority.constant_pair.v2` and includes species/statistics in
   its canonical SHA-256 payload.
5. `constant_pair` accepts only `POINTWISE_SPECTRAL`; it cannot masquerade as
   an integrated source witness.
6. `IntegratedMomentMapBinding` binds an integrated witness to one exact target
   state, moment-map hash, radial-weight-family hash, and source hash.
7. Integrated compatibility fails closed without that typed binding and rejects
   target-state reuse.
8. `pointwise_action` and `rates_per_tau` raise `SourceArithmeticError` if
   finite inputs produce nonfinite binary64 outputs.
9. The source action is evaluated in the algebraically equivalent affine form

   ```text
   eta - (kappa-eta) f
   ```

   which avoids an unnecessary `inf-inf` intermediate near `eta=kappa` while
   preserving the photon/boson law exactly in real arithmetic.

## Scope firewall

This node does **not** add:

- a REC provider or physical atomic source table;
- solver-loop wiring;
- grid or PSTF source adapters;
- an integrated closure for `G(e)` or `J^(i)_{A_l}`;
- virtual-spike tail handling;
- two-photon or Raman kernels;
- polarized REC sources;
- a trusted native wheel;
- physical directional faces, observables, likelihoods, or statistics.

## Verification truth

The exact RED has been observed.  The GREEN source has been published but has
not yet been run in the user's local exact-head environment.  Connected Wolfram
was attempted twice for this stage and returned upstream HTTP 502 before any
kernel result.  No fresh Wolfram PASS is claimed.

The next gate is:

```text
bash scripts/research/run_bass_rec_source_r6_green_local.sh
```

A successful run must preserve all eleven R5 survivors, pass all ten R6 tests,
show deterministic two-process v2 bundle and binding hashes, pass the targeted
constructor/zero/overflow/binding probes, generate the source-branch audit SVG,
and leave the detached source worktree clean.

## Claim boundary

```text
PASS_EXECUTED_R6_RED
R6_GREEN_SOURCE_CREATED
R6_GREEN_RUNTIME_NOT_YET
NO_SOLVER_SOURCE_WIRING
NO_GRID_PSTF_SOURCE_PARITY
NO_GENERIC_INTEGRATED_CLOSURE
TRUSTED_PRODUCTION_WHEEL_NOT_ESTABLISHED
NO_PHYSICAL_FACE_OR_PROVIDER
NO_PASS_RF04
```
