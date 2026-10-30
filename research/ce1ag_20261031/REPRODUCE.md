# BASS CE1-AG reproducibility, exactly one original continuum shear-work sign unit

Base: `cosmosapjw-quantum/bass` PR284 HEAD
`a3e1139e043e3f42f682a0dd84857db819972e73`.
Immutable frozen physical input SHA256:
`022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`.

Run (NumPy and pytest required):

```bash
python research/ce1ag_20261031/source/certify_continuum_sign.py
python -m pytest -q research/ce1ag_20261031/source/test_ce1ag.py
python -m compileall -q research/ce1ag_20261031/source
```

Expected new artifacts: `data/CE1AG_CONTINUUM_SIGN_CERTIFICATE.json`,
`data/CE1AG_RIGOROUS_LOWER_CURVE_401.csv`. CSV entries are **analytically certified
lower curves**, not 401 newly numerically evolved physical states. Full original
`CE1AF_PHYSICAL_TIMELINE.csv.gz` remains unchanged, and the GEOMETRY original strict
`h=1e-5` is not modified. Test `test_actual_parent_source_when_repository_present`
uses the actual checked-out parent `input/cellwise_gl_rust.py`; a standalone zip
without the parent records that test as `SKIP`, not PASS.

No new upper-DAG admission. Independent distinct-author R6/C9 NOT_RUN.
Never confuse source hash identity, analytically derived inequality,
local implementation tests and a verified GitHub CI.
