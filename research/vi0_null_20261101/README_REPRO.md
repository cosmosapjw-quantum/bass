# VI0 physical null Liouville source-owned replay

From a clean checkout of `cosmosapjw-quantum/bass` at the exact head of Draft PR #312:

```bash
python -m pip install numpy==2.3.5 scipy==1.17.0 sympy==1.14.0 pytest==9.0.2 matplotlib==3.10.8
python research/vi0_null_20261101/source/vi0_null_liouville.py
python -m pytest -q research/vi0_null_20261101/source/test_vi0_null_liouville.py
python research/vi0_null_20261101/source/verify_saved_physics.py
python -O research/vi0_null_20261101/source/verify_saved_physics.py
python research/vi0_null_20261101/source/make_science_plots.py
```

Note: script default output is `research/vi0_null_20261101/data/`, not the repo root. The parent `vi0_dynamics.py` is loaded from unchanged `research/vi0_manifold_20261101/` and checked by exact Git blob SHA; original seven BASS formula files must be checked in CI. Optimized mode uses the explicitly raised, RHS-free audit, not optimized pytest assertions. All 78,720 source-owned tracer-ray rows and 1,476 moment rows are generated anew, not copied from the thin PR sample. Original VI0 background gamma-law fluid is source-authentic; photon I0=1 is a separately specified non-gravitating test source, not observed CMB.

Source-inclusive S2 ZIP has locked parent Python, all data+figures and tests. It should reproduce physical science offline with exact source and dependencies from the archive root. It does not authorize production and preserves parent PR311 immutable.
