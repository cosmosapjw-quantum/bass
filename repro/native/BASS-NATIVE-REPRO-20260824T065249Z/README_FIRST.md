# BASS native reproducibility artifact parts

Classification: **PARTIAL/BLOCKED**. Source commit `0d1203da778c5e92fce4c9bbf24c8044c5b46018`, tree `675213f191477b1f47c725892e9f4c804c623ab0`.

Archive: `BASS_NATIVE_REPRO_BASS-NATIVE-REPRO-20260824T065249Z.tar.xz`
Size: `176301104` bytes
SHA-256: `033b408558b1c908b1604b80ed3f942f9720120c2f15dae0b231ecb4547f8db1`
Parts: `22`; each is at most `8388608` bytes.

Do not concatenate a filename glob. The ordered `parts` array in `BUNDLE_MANIFEST.json` is authoritative:

```bash
sha256sum -c BUNDLE_MANIFEST.sha256
python3 reassemble_bundle.py \
  --manifest BUNDLE_MANIFEST.json \
  --parts-dir parts \
  --output BASS_NATIVE_REPRO_BASS-NATIVE-REPRO-20260824T065249Z.tar.xz
sha256sum BASS_NATIVE_REPRO_BASS-NATIVE-REPRO-20260824T065249Z.tar.xz
```

The repository is private. Obtain this branch with authenticated Git, not assumed raw/browser access.
