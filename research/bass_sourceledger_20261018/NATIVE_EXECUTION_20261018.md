# Actual pinned native SourceLedger execution

`RUN_NATIVE.sh` executed locally against REI commit `0e25846433170d0f420c4cda44a0bedbf02cd177`. The runner staged 146 committed files, checked source hashes, built the external release probe with Cargo 1.99.0 and Cargo jobs 2, and executed it.

The compiler artifact SHA-256 is `e64732a17cc97718852804df03e388d6ad0a4c8fc65c47c1d203ee2e4e59c6cb`. It emitted 58 native rows and a completion marker. `NATIVE.jsonl` SHA-256 is `d6edcebd1d95a8cfca64b6f24cd530a82eadae657c5637a94e3e43669cc4374f`.

All matched discrete oracle fields passed their stated cross-language relative target `5e-11`; ledger residual target is `1e-11`, normalized by emitted photons/H or eV/H with floor `1e-30`. Five invalid inputs exited 3 and created no output JSONL. Raw logs and rows are preserved in `evidence_native_20261018/`.

This is native source-only transport evidence. H/He, opacity, feedback, Qa, polarization, checkpoint/restart and EoR remain HOLD.
