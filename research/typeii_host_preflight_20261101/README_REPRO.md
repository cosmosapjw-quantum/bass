# BASS Type-II exact physical four-dimensional chart and isolated RustCore mock host

Nonproduction scope. Original git owner/main SHA 9c6506e4e2087129a8b674ff10438e5db1a55c9d; stacked exact parent PR318 52e77e59e0d37b75b892efa38d05784ddb731757.

1. Local model (does not claim exact downloaded fixture bytes): from this extracted archive root:
   `cd source && python verify_original_fixture.py --output ../data && python -m unittest -q test_typeii_physics.py && python -O -m unittest -q test_typeii_physics.py && python referee_saved.py --data ../data && python -O referee_saved.py --data ../data`.
2. In the original GitHub checkout with this source at `research/typeii_host_preflight_20261101/`:
   `python research/typeii_host_preflight_20261101/source/verify_original_fixture.py --repo-root . --output research/typeii_host_preflight_20261101/ci_generated --require-original` checks original Git blob identity and canonical fixture content before producing source-locked physics data.
3. Compile-only actual generated reference test on installed Rust host:
   `rustc --edition=2021 --test research/typeii_host_preflight_20261101/source/typeii_state_contract.rs -o /tmp/typeii-contract-tests && /tmp/typeii-contract-tests`.
   This **does not** compile `_rustcore` or link a production RustCore state.
4. Real production host vendor/cargo preflight **not executed** in model environment:
   `cd _rustcore && cargo metadata --locked --offline --format-version 1 && cargo test --locked --offline`. Only run with owner-authorized exact cached git revisions/vendor bundle, not by unapproved online dependency downloads.
5. Remote CI `.github/workflows/typeii-host-preflight.yml` restores the actual original source fixture and its nine Git blobs, executes Rust generated original RHS/JVP, tests and referee, and saves a new 401-row scientific artifact. Inspect the run and SHA before admission. Source byte identity and generated-data numerical identity are different claims.

S0/S1/S2 ZIPs form a recoverable succession. `reports/S2_MANIFEST.json` holds member file SHA256; `reports/NEXT_THREAD_HANDOFF.txt` is the compact next-thread handoff. Stage II 11/11 remains historical, BASS 9/15 scoped, Join J1 0/2 HOLD, Type-II preflight PARTIAL, production/merge unapproved.