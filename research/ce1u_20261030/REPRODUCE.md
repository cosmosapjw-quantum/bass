# CE1-U reconstruction and acceptance

Use the exact current BASS branch (child of CE1-T #263) at the documented commit. The GL source and 4-panel comparison are MPFR192, **not** the inherited midpoint CE1-F pressure certificate.

```bash
python -m pip install numpy==2.3.5 scipy==1.17.0 mpmath==1.3.0 pytest==9.0.2
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 python research/ce1u_20261030/certified_gl_source.py 4 6 8
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 python research/ce1u_20261030/certify_gl_coupled.py 4 6 8
PYTHONPATH=. python -m pytest -q research/ce1u_20261030/tests/test_gl_source.py
rustup toolchain install 1.94.1 --profile minimal
rustc +1.94.1 --edition=2021 -C opt-level=2 -A dead_code research/ce1r_20261030/sky_time_derivative.rs -o /tmp/bass_ce1u_rust
/tmp/bass_ce1u_rust --selftest
PYTHONPATH=. python research/ce1u_20261030/rust_parity.py --binary /tmp/bass_ce1u_rust
```

The Rust comparator uses BASS's **actual** `_rustcore/src/kinetic/comoving.rs` via the original CE1-R CLI. Rust binary64 E/P/E' is a cross-check, not an MPFR certificate. All Ray/mass initial data must be exact binary and GL4/6/8. The original physical six-cell table and h target 1e-5 are immutable. `rho=6`, `B=.07`, elliptic Chebyshev bound plus exact rational GL root/weight bracketing and MPFR192 ray rounding are the two distinct source error carriers. New RK4/Hermite panel residual and binary knot jumps are recomputed for the actual GL source; see code comments and report for proof domain.
