# CE1-U deterministic reproduction

Dependencies: Python 3.11+, numpy 2.3.5, scipy 1.17.0, pytest 9.0.2, matplotlib; Linux libmpfr.so.6 for the genuine 192-bit outward knot-source check. No GPU or Rust compiler required for this *new* CE1-U source certificate because the original BASS Rust outputs and frozen CE1-T GL generator are reused without changing their binaries.

Package layout from project root: `research/ce1t_20261030/cellwise_gl_rust.py` and `research/ce1t_20261030/local_GL40_history_authority.csv` are pinned, preserved source dependencies. Run:

```bash
python research/ce1u_20261030/source/ce1u_cert_source.py --order 6 --K 12 --output research/ce1u_20261030/data/GL6_source_exact_bound.json
python research/ce1u_20261030/source/ce1u_cert_source.py --order 8 --K 12 --output research/ce1u_20261030/data/GL8_source_exact_bound.json
python research/ce1u_20261030/source/ce1u_physical_histories.py --out research/ce1u_20261030/data
python research/ce1u_20261030/source/ce1u_mpfr192_knots.py --output research/ce1u_20261030/data/MPFR192_source_knots.json
python research/ce1u_20261030/source/ce1u_analyze.py --root research/ce1u_20261030
python -m pytest -q research/ce1u_20261030/tests/test_ce1u_science.py
python -m compileall -q research/ce1u_20261030/source
```

The exact-rational certificate computes moment expressions with rational enclosures for pi and sqrt2 and exact dyadic stored binary64 ray/mass data. Runtime-seconds fields are non-deterministic. CSV output formatting/line ending changes do not alter semantic numeric identity; test source ray/mass SHA for exact original numerical input identity.

Proof claim: source bound for all 0<=ell_i<=0.08 and derived difference of *exact* Einstein-Vlasov ODE solutions. Python DOP853 and four-panel RK4 are separate numerical diagnostics; MPFR192 knot tests enclose exact source evaluations at stored binary64 numerical states, not uncertainty in those states.
