# BASS RF-00 native reproduction bundle

This bundle is bound to BASS native code commit
`4073f5a66910142545167b2987bfe350239fd7c9`, tree
`f0d98afc9139281a04a0dece2221a055a85c2fb0`, Cargo.lock SHA-256
`d500208e9353ade1cb74693918598846628219e6e7bd2e2bce9ec85e29eb6310`,
CPython 3.12 (`cpython-312-x86_64-linux-gnu`), Linux x86_64, and glibc 2.39.

It reuses the byte-identical r2 Cargo vendor/config/lock and 22-wheel Python
dependency closure without fetching. RF-00 adds the two pinned PEP 517 build
wheels and a new strict-portable native wheel. It contains no target directory,
venv, Cargo registry cache, credentials, Rust toolchain archive, or Wolfram/xAct.

The delivery branch may have a later evidence-only commit. That head is resolved
from authenticated Git and is not a native-source identity. The native payload is
always bound to the code commit and tree above.

After extraction, verify into a destination that does not exist:

```bash
BASS_CARGO_BIN="$HOME/.rustup/toolchains/1.94.1-x86_64-unknown-linux-gnu/bin/cargo" \
BASS_RUSTC_BIN="$HOME/.rustup/toolchains/1.94.1-x86_64-unknown-linux-gnu/bin/rustc" \
scripts/restore_and_verify.sh \
  --repo-url https://github.com/cosmosapjw-quantum/bass \
  --source-commit 4073f5a66910142545167b2987bfe350239fd7c9 \
  --expected-tree f0d98afc9139281a04a0dece2221a055a85c2fb0 \
  --bundle "$PWD" \
  --dest /new/empty-parent/bass-rf00-restore \
  --python /usr/bin/python3.12
```

Authentication for the private repository must already be configured. The
script fails closed before materialization on identity or dependency mismatch,
then executes locked/offline Cargo tests, an offline root install, typed native
capability/import checks, and the focused RF-00 test closure.

Machine evidence begins at `metadata/EVIDENCE.json`; hashes for every regular
file are in the NUL-terminated `metadata/CONTENT_MANIFEST.sha256`.
