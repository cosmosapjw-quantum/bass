# BASS native delta artifact r2 — PARTIAL/BLOCKED

This branch stores only deterministic archive parts and their ordered manifest. It is bound to delta source `bff2852af3536d0d9e8badc3e5e2ad024f299278`, tree `603791eee595dac4ec8c9f177d53842695b3932f`, with canonical base `0d1203da778c5e92fce4c9bbf24c8044c5b46018` retained as authority.

- archive: `BASS_NATIVE_REPRO_BASS-NATIVE-DELTA-20260824T092016Z.tar.xz`
- archive SHA-256: `ef0f35b76ab4ef4877ed577afe391ed677a7a6767bcbc64db62dd853d757afca`
- archive size: `175949544` bytes
- content-manifest SHA-256: `61e4216d23ec33949e621b78ea2da1a755cd2d154741532b298a63ac48d4f91a`
- parts: `21`; every part is at most `8388608` bytes
- native wheel SHA-256: `b58fe7400c51cf0016b877a681758ebb9896d07cfb3f80be7ca82df64b734d10`

Authenticated retrieval for this private repository:

```bash
git clone --depth 1 --branch artifact/native-repro-bundle-20260824-r2 \
  https://github.com/cosmosapjw-quantum/bass bass-native-r2
cd bass-native-r2/repro/native/BASS-NATIVE-DELTA-20260824T092016Z
sha256sum -c BUNDLE_MANIFEST.sha256
mkdir reconstructed
python3 reassemble_bundle.py \
  --manifest BUNDLE_MANIFEST.json \
  --parts-dir parts \
  --output reconstructed/BASS_NATIVE_REPRO_BASS-NATIVE-DELTA-20260824T092016Z.tar.xz
sha256sum reconstructed/BASS_NATIVE_REPRO_BASS-NATIVE-DELTA-20260824T092016Z.tar.xz
tar -xJf reconstructed/BASS_NATIVE_REPRO_BASS-NATIVE-DELTA-20260824T092016Z.tar.xz \
  -C reconstructed
```

The reassembler trusts only the ordered `parts` array and verifies each size/hash and the final archive hash. The closeout r2 receipt records the artifact commit and remote readback because a commit cannot contain its own identity. This is not a PASS closeout: R5B-001/R5B-002 remain RED, project Wolfram/xAct replay remains OPEN, and formula source bytes are absent. Do not merge main, merge/ready a PR, change tolerances/references, or promote scientific claims without explicit approval.
