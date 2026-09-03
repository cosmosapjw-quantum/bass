# SYNC-MAP-02E-R1 — BASS-only semantic-hardening local replay

This node belongs to **BASS only**. It does not edit or execute REC, REI, or HTT source. Repository names retained in `declared_consumer_targets` are dependency targets, not implementation-parity claims and not permission to mutate those repositories.

## Exact parent

```text
BASS PR #99
commit e1467825c8f4c5e3f47df5da5b8a6202e8f96f30
registry semantic hash
16f699043a7420c6e62abdad02434a216075ce55f69583b5051965ea53db5612
```

The parent export remains immutable at:

```text
docs/bass_master_ssot_v2/SYNC_MAP_02E/
BASS_SHARED_FRAME_PHOTON_EXPORT.json
```

The R1 generator writes a superseding full registry to an artifact directory. It does not overwrite the parent file.

## What is hardened

1. The aberration coefficient is serialized as

   ```text
   gamma^2/(gamma+1)
   ```

   so `beta=0` is directly evaluable and no `0/0` is generated.

2. Blackbody thermodynamic temperature is a weighted section map:

   ```text
   Pullback[A_beta, temperature_tilde]
     = doppler_factor_source * temperature_source
   ```

   It has two direct dependencies with different roles:

   ```text
   ABERRATED_DIRECTION  BASE_MAP_REQUIRED
   DOPPLER_FACTOR       FIBER_WEIGHT_REQUIRED
   ```

3. Photon characteristics use physical ray length

   ```text
   s = c*t
   ```

   while `ell` is reserved for angular multipole rank.

4. Energy and direction flow are explicitly specialized to the geodesic homogeneous normal:

   ```text
   A_normal^a = 0
   ```

   The Bianchi structure vector `aB^a` is not normal four-acceleration.

5. Polarization screen-basis transport remains outside this six-formula export:

   ```text
   EXCLUDED_NEXT_BASS_NODE
   ```

6. The legacy name `consumer_bindings` is removed. The replacement
   `declared_consumer_targets` does not assert source availability, numerical policy, or runtime parity.

## Prerequisites

```text
Python >= 3.10
Wolfram Language / wolframscript >= 15.0
Git
GNU coreutils sha256sum
```

No network access and no third-party Python package are required after the repository is cloned.

## One-command local replay

From the repository root:

```bash
bash scripts/run_sync_map02e_r1_local_validation.sh
```

An alternative output directory can be supplied:

```bash
bash scripts/run_sync_map02e_r1_local_validation.sh /absolute/output/path
```

The shell entry point resolves `python3` once with `command -v`, uses that exact executable for all Python steps, and passes its absolute path into the Wolfram replay. This avoids relying on a nonexistent `System`FindExecutable` function inside Wolfram Language 15.0.1.

The runner performs, in order:

1. deterministic full-registry generation;
2. fail-closed Python verification;
3. six standard-library unit tests;
4. exact-count Wolfram `TestReport` with 11 top-level MUnit tests;
5. source and generated-artifact SHA-256 manifest construction.

## Direct commands

Generate and verify without Wolfram:

```bash
PYTHON_BIN="$(command -v python3)"

"${PYTHON_BIN}" scripts/build_sync_map02e_r1_hardening.py \
  --input docs/bass_master_ssot_v2/SYNC_MAP_02E/BASS_SHARED_FRAME_PHOTON_EXPORT.json \
  --output /tmp/BASS_SHARED_FRAME_PHOTON_EXPORT_R1.json \
  --receipt /tmp/SYNC_MAP_02E_R1_LOCAL_BUILD_RECEIPT.json

"${PYTHON_BIN}" scripts/verify_sync_map02e_r1_hardening.py \
  --input /tmp/BASS_SHARED_FRAME_PHOTON_EXPORT_R1.json \
  --receipt /tmp/SYNC_MAP_02E_R1_LOCAL_BUILD_RECEIPT.json

"${PYTHON_BIN}" -m unittest -v tests/test_sync_map02e_r1_semantic_hardening.py
```

Run the Wolfram replay directly. The second user argument is the resolved Python executable and is mandatory:

```bash
PYTHON_BIN="$(command -v python3)"

wolframscript -file \
  wolfram/scripts/run_sync_map02e_r1_local_replay.wls \
  /tmp/bass-sync-map02e-r1 \
  "${PYTHON_BIN}"
```

The Wolfram runner fails closed with `FAIL_PYTHON3_ARGUMENT_MISSING` when that argument is absent or does not name an existing path, and with `FAIL_PYTHON3_UNUSABLE` when `python --version` cannot be executed successfully.

## Expected outputs

```text
BASS_SHARED_FRAME_PHOTON_EXPORT_R1.json
SYNC_MAP_02E_R1_LOCAL_BUILD_RECEIPT.json
SYNC_MAP_02E_R1_LOCAL_WOLFRAM_REPLAY_RECEIPT.json
SYNC_MAP_02E_R1_LOCAL_VALIDATION_SUMMARY.json
SHA256SUMS
```

Acceptance requires:

```text
Python generator exit code       0
Python verifier exit code        0
standard-library unit tests      6/6
Python executable probe          0
MUnit top-level tests            11/11
MUnit failed                     0
MUnit not evaluated              0
Wolfram export validator         true
Wolfram patch-contract validator true
```

Zero discovered MUnit tests is a hard failure.

## Failure preservation

Do not edit expected hashes or weaken predicates to obtain a PASS. Preserve the generated directory and command output when any of these occur:

```text
unexpected parent registry hash
semantic-hash mismatch
missing aberration base-map edge
singular zero-boost coefficient
ray parameter written as ell
normal-acceleration specialization missing
screen transport promoted into the six-formula export
consumer_bindings reintroduced
missing or unusable explicit Python executable
MUnit zero discovery
```

## Claim boundary

A successful local replay authorizes only a BASS-owned formula-registry hardening receipt. It does not authorize:

```text
cross-repository software parity
REC, REI, or HTT source mutation
BASS numerical background provider
matter-frame global tilt
finite-electron-tilt collision
polarization screen transport
likelihood readiness
provider admission
science or RF04 promotion
```
