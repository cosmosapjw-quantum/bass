# General-frame native Codazzi diagnostic

This is a native port of the numerical contraction in
`bianchi.conventions.codazzi_residual`, not a change to the evolution equations
or a replacement for that differentiable JAX oracle.

- Production kernel: `_rustcore/src/kinetic/constraints.rs`, fixed-size f64
  row-major inputs, epsilon_012 = +1.
- Formula: C_a = 3 A_b Sigma_ab + epsilon_abc N_bd Sigma_cd - q_a.
- `QState.codazzi_residual()` now uses the native diagnostic by default.
- Explicit native entry points remain `bianchi.q.diagnostics.codazzi_residual_native`
  and `QState.codazzi_residual_native()` (backward-compatible alias).
- PyO3 symbol: `q_codazzi_residual`, registered through the normal extension.
- The original QState diagnostic body is retained as
  `QState.codazzi_residual_python_oracle()`. The differentiable global
  `bianchi.conventions.codazzi_residual` remains unchanged. No backend identity
  fingerprints are updated; this does not remove every JAX path in BASS.
- Invalid shapes/nonfinite inputs raise ValueError; contraction overflow is
  rejected by Rust. The kernel does not symmetrize tensors, impose trace-free
  projections, or reinterpret chart-specific scalar Codazzi constraints.
- Native requests fail closed via the existing backend policy. There is no
  Python/JAX fallback and no fake extension. A newly built development extension
  remains subject to that policy's existing verification/override rules.

## Verification boundary (2026-10-06)

Verified by executing the exact production source using rustc: six Rust tests
and 128 independent seeded NumPy contraction fixtures (64 symmetric trace-free
shears and 64 unrestricted tensors to catch accidental transposes). Eight input
validation cases executed against the real Python wrapper without an extension.
The initial zero-returning kernel failed five behavior tests; the initial wrapper
failed shape rejection. These were corrected before the successful executions.

The initial standalone phase was blocked by absent Cargo dependencies, pytest,
and the native extension. A subsequent offline build supplied a real modified
extension. The default-route change was then verified against that extension:

- CORE environment (without JAX/SciPy): 10 tests passed, with the one explicitly
  named live-JAX oracle test deselected, not counted as a pass.
- Oracle environment: all 11 tests passed, including the real QState default
  route against the separately named JAX oracle and the real PyO3 binding.
- A fresh-process default-route test uses nonzero momentum flux, an independent
  diagonal-N contraction, and checks that JAX/JAXlib/SciPy were not imported.
  Before routing changed, this same test failed because the default diagnostic
  attempted to import the absent JAX dependency.

These runs explicitly used `BASS_ALLOW_UNVERIFIED_NATIVE_DEV=1` with the real
modified wheel. The resulting unverified-development warnings are expected:
this is research-mode verification, not a fingerprint-approved release. No Rust
binary changes were needed for the final Python default-route switch. The full
project suite was not rerun for that routing-only step.

## Reproduce

With rustc on PATH:

    rustc --edition=2021 --test _rustcore/src/kinetic/constraints.rs -o /tmp/codazzi-tests
    /tmp/codazzi-tests
    python -m pytest tests/test_native_codazzi_kernel.py

The differential test compiles `tests/rust/codazzi_driver.rs`, which includes the
production module by path, rather than maintaining a test implementation. If
pytest is unavailable, its actual test function can be run without substituting
pytest or the native extension:

    python - <<'PY'
    import runpy, tempfile
    from pathlib import Path
    check = runpy.run_path('tests/test_native_codazzi_kernel.py')
    with tempfile.TemporaryDirectory() as directory:
        check['test_production_rust_codazzi_against_independent_numpy'](Path(directory))
    print('128 production Rust / NumPy fixtures passed')
    PY

With a legitimately built real extension, run (use the documented explicit
development override for an unverified research wheel):

    cargo test --manifest-path _rustcore/Cargo.toml --offline
    # CORE: this named test alone requires the optional live JAX oracle.
    python -m pytest tests/test_q_codazzi_native.py -k 'not matches_jax_oracle'
    # Oracle environment with JAX installed:
    python -m pytest tests/test_q_codazzi_native.py
    python -m pytest

The binding tests intentionally fail rather than skip when the extension is
missing. They include the analytic vector/optional-zero-flux case and a real
QState nonzero-flux comparison against the unchanged JAX oracle.
