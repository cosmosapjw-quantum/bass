# VI0 scalar eigenframe exact theory, replay instructions

Only this source-owned *theory* unit is committed. A full VI0 production solver and Rust migration are NOT included.

## Original source

BASS main at `9c6506e4e2087129a8b674ff10438e5db1a55c9d`; Git blob SHAs in `VI0_SOURCE_AUTHORITY.json`. Historical G-DYN design PR15 HEAD `af467a974cfd9bd8ccd59870e5a03c8099f23db1`, but PR15 does not contain all newer main source modules. Source-locked formula origins: `bianchi/conventions.py`, `bianchi/matter/fluid.py`, `bianchi/charts/general.py`, `bianchi/charts/class_a.py`, `generated/rust/typeii/typeii_kato.rs`. Full 7D literature: Hervik 2004, DOI 10.1088/0264-9381/21/9/007.

## Run

From the folder containing these files:

```sh
python -m pip install 'sympy==1.14.0' 'numpy==2.3.5' 'pytest==9.0.2'
python vi0_exact.py > VI0_SCOPED_RESULT.json
python -m pytest -q test_vi0_exact.py
python -m compileall -q vi0_exact.py test_vi0_exact.py
```

Expected: exact construction, seven original constraints/rank and operator tests + two extra exact/numeric regression tests, **9/9 PASS**. `VI0_SCOPED_RESULT.json` is a constructed scoped theory receipt, not a production CI claim. Source checks in GitHub CI should verify all seven Git blob hashes before granting provenance.

## CI/inputs

No runtime Python JAX import is needed. The main repo's read-only source files remain unchanged. The generated 6-axis scalar projector is an exact rational witness (not a proposed replacement for the original full-angle or polarized collision solver). The observer quadrature must contain paired ±e_i directions for the exact rank witness; other angular grids need their own independent Gram rank test. 
