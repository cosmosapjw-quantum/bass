# BASS–REC source protocol R5C — development behavior versus production provenance

## Exact parent

```text
R5 candidate PR  #112
commit            fc4d21b92a1abd1e9b35178f7d666831fc5c827d
base              d81ad12f795b6ac6d57293502e75426ed1dbbb1a
changed source    bianchi/source_authority.py only
```

## Why R5B stopped

The provisioned local run succeeded through:

```text
requirements.lock installation
Maturin installation
Rust 1.94.1 native-wheel build
project/native installation
JAX and bianchi_rustcore imports
py_compile
focused source protocol 11/11
two-process canonical payload hash
```

The locally built wheel was:

```text
bianchi_rustcore-0.1.0-cp312-cp312-manylinux_2_34_x86_64.whl
SHA-256 bf5a59534ffc9d6f9c3410aa19319f18a4a8a7a9761bcd61c5da8c8627ddf609
```

Backend integration did not reach numerical comparison.  The existing RF-00
policy rejected the wheel with:

```text
UnverifiedNativePayloadError
installed_wheel_or_manifest_does_not_match_trusted_payload
```

This is correct fail-closed behavior.  Importability and a successful local
build do not establish source-to-binary production provenance.

## Purpose of this branch

The script

```text
scripts/research/run_bass_rec_source_r5c_dev_behavior.sh
```

creates a separate **development behavior** lane.  It:

1. proves that default dispatch still rejects the untrusted wheel;
2. runs policy and packaging tests without an override;
3. runs the native integration cone on both the R4 base and R5 candidate under
   the exact `BASS_ALLOW_UNVERIFIED_NATIVE_DEV=1` override;
4. requires the typed development warning;
5. compares JUnit counts for the paired base/candidate runs;
6. reruns the focused eleven-test source protocol and two-process payload hash;
7. leaves the caller checkout and the trusted-payload registry unchanged.

A successful classification is deliberately narrow:

```text
PASS_R5C_DEV_BEHAVIOR_ONLY_NO_PRODUCTION_PROVENANCE
```

It does not make the local wheel trusted and does not admit production native
dispatch.

## Run

The preceding R5B receipt is used by default:

```bash
bash scripts/research/run_bass_rec_source_r5c_dev_behavior.sh
```

The command may be launched from `rec_bianchi` or any other directory because
the script identifies BASS from `remote.origin.url` and uses detached temporary
worktrees.

Override the receipt path when needed:

```bash
R5B_RECEIPT_DIR=/absolute/path/to/BASS_REC_SOURCE_R5B_<stamp> \
bash scripts/research/run_bass_rec_source_r5c_dev_behavior.sh
```

Receipts are written to:

```text
~/Dropbox/bianchi/_runtime_receipts/BASS_REC_SOURCE_R5C_<UTC>/
```

The script records its own classification and exits with shell status zero so a
failed test does not terminate a failure-sensitive interactive shell.

## Parallel trusted lane

Production provenance remains a separate node:

```text
BASS_REC_SOURCE_R5D_TRUSTED_NATIVE_PROVENANCE
```

A recoverable RF-01 immutable bundle exists at:

```text
branch   artifact/native-repro-bundle-20260825-r4
commit   b069e46eeb649b7b33e5ca30c3508d144fcd0e2c
bundle   repro/native/BASS-RF01-NATIVE-20260825T035620Z
archive  1c587e04e93095d39ec821b2a7cb6824132d9c2ded635ee8c6101410490fabd3
wheel    c912ac94adef60b724af3ba892d7865d0148c77fa578be6c28ef021cce3b7482
```

It is stored in 22 ordered Git parts with a machine-readable bundle manifest.
Recovery must verify every part, the concatenated archive, the internal content
manifest, the wheel archive, installed-file hashes, RECORD, loaded extension
path, and route identity before calling any default production route.

The RF-01 wheel may be too old for routes that now require RF-02C/RF-03/RF-04
symbols.  Such a failure is a compatibility result and must not be repaired by
weakening provenance.  The preferred R5D target is the newest recoverable wheel
already named in the current trusted registry.

## Claim boundary

```text
R5 source protocol runtime                  PASS
R5 canonical payload identity              PASS
R5 local build/import                       PASS
RF-00 default fail-closed provenance        PASS
R5C development behavior                    NOT RUN YET
R5D production-native provenance            BLOCKED
source integration                          NOT STARTED
grid/PSTF source parity                     NOT STARTED
physical face/provider/statistics           WITHHELD
PASS_RF04                                   WITHHELD
```
