# RF-03 R4 validator repair and local handoff

Status: tested bootstrap repair; RF-03 implementation remains NOT_RUN here.
Package ID: `BASS-RF03-REMOTE-REBIND-20260828-R4`.

This repairs `BLOCKED_BY_VALIDATOR_DEFECT`, not a scientific or remote-state
failure. R2 at `55335d3817a82da7e0f9bf24ef7632a2533645d3` and all six original
raw SHA-256 values remain unchanged. RF-02C stays at
`dfa17457d402bd441d3fdf786c2d79c529512ee5`.

R4 reads Git blobs as bytes and writes them with `write_bytes`. It runs the
original R2 offline manifest/semantic checker unchanged. R2's obsolete live
R1-tip comparison is explicitly replaced by an exact historical R1 commit/tree
check; every original source-blob check is retained. Do not invoke the old R2
`validate_package.py --live` separately after this replacement succeeds.

```bash
python3 validate_rebind.py
python3 tests/test_validate_rebind.py
python3 validate_rebind.py --live --repo /path/to/bass \
  --materialize /path/to/a/new/authority-directory
```

The tests use real Git processes and synthetic repositories/source data. They
are not RF-03 runtime or scientific tests. The authenticated production-clone
live check and RF03-AUTH-01 onward remain local work. See CODEX_HANDOFF.md.
No `PASS_RF03_AUTHORITY`, `PASS_RF03`, performance, or scientific claim is made.
