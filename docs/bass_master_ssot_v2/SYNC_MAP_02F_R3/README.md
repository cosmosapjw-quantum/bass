# SYNC-MAP-02F-R3 — BASS consumer-binding contracts

## Status

```text
repository scope          BASS_ONLY
expected RED              PASS_EXPECTED_RED
RED source head           21f5b08b704a90af19e617a372c994239e9046a2
RED source tree           ff6d5dcc1fd7ad90c0b7bf54a1239e01caae7cce
GREEN source              PUBLISHED / LOCAL EXACT REPLAY REQUIRED
consumer runtime parity   WITHHELD
```

The observed RED contained exactly 12 failing unittest methods, zero errors, raw exit code 1, and the common expected cause: the production binding contract and GREEN validation surfaces were intentionally absent. The wrapper classified this as `PASS_EXPECTED_RED`, exited 0, and verified its SHA-256 manifest.

This stage now implements the minimum GREEN contract required by that test. It remains a BASS-owned request and acceptance-gate layer. It does not edit or execute `rec_bianchi`, `rei_bianchi`, or `htt_base`, and it does not infer runtime parity from formula or source-symbol occurrence.

## Contract inventory

```text
consumer repositories                   3
formula binding requests               10
source-role pins                       11
named source symbols                   12
explicit absent implementation slots    1
owner formulas                           6
state surfaces                           6
certificate families                     4
blocked promotions                      13
```

Consumers are partitioned as:

```text
rec_bianchi   4 requests
rei_bianchi   2 requests
htt_base      4 requests
```

## Critical firewalls

- `GRID_F_Q_E` and `PSTF_F_AELL_Q` are the frequency-resolved representation pair; numerical parity requires an `ANGULAR_REPRESENTATION_CERTIFICATE` instance.
- `J_I_AELL` and `G_ANGULAR_ENERGY` are noninvertible projections in general; generic source binding requires a `SPECTRAL_PROJECTION_CLOSURE_CERTIFICATE` instance.
- kinetic-to-fluid reduction requires a `MOMENT_EXCHANGE_CERTIFICATE` instance.
- scalar intensity cannot be promoted to `POLARIZED_COHERENCY` without a `POLARIZED_SCREEN_CERTIFICATE` instance.
- the REI generic direction-flow role remains an explicit absent implementation slot.
- the REI H-only energy-drift role remains restricted to FLRW or an exactly isotropic angular subspace.
- HTT full-field blackbody pullback and the prepulled-value primitive remain distinct roles.
- every authorization field for source mutation, runtime parity, provider/science promotion, and merge/ready transition remains `false`.

## Parallel BASS REC-source evidence

The executed R6C cleanliness result is recorded as read-only parallel evidence:

```text
PASS_BASS_REC_SOURCE_R6C_CLEAN_BACKEND_NONREGRESSION
publication head  3f605360eae96a7fbe5dd9c31ec510c5d56e255b
green source      92d67dc79cf645947beb93ac01a9505ee277dabd
clean worktrees   true
```

It does not satisfy this binding contract and does not establish trusted production-native authority. The separate required gate remains:

```text
PASS_R5D_TRUSTED_RF00_PAYLOAD_PROVENANCE_AND_BACKEND_GATE
```

## Local GREEN replay

```bash
bash scripts/run_sync_map02f_r3_consumer_bindings_local.sh
```

Expected gate:

```text
Python verifier                    PASS
Python mutation tests             12/12
Wolfram MUnit                     18/18
failed / not evaluated             0 / 0
strict JSON round trip             PASS
atomic receipt publication         PASS
SHA256SUMS                         PASS
exit code                             0
```

Generated files:

```text
artifacts/sync_map02f_r3_consumer_bindings/
  SYNC_MAP_02F_R3_CONSUMER_BINDING_WOLFRAM_RECEIPT.json
  SYNC_MAP_02F_R3_CONSUMER_BINDING_LOCAL_VALIDATION_SUMMARY.json
  SHA256SUMS
```

A local GREEN result authorizes only the creation of three separately owned runtime-validation requests:

```text
REC_BINDING_RUNTIME_VALIDATION
REI_BINDING_RUNTIME_VALIDATION
HTT_BINDING_RUNTIME_VALIDATION
```

No cross-repository parity federation may be considered until each requested consumer-owned runtime stage has an independent exact-source receipt.
