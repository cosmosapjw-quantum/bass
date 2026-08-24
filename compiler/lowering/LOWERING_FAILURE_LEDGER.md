# Lowering failure ledger

Two target-language defects were found only when the generated code was
compiled by Rust 1.94.1.

1. **Rust numeric literal typing** — raw SymPy Rust output left integer
   coefficients in `integer * f64` expressions.  The lowering pass now
   canonicalizes numerical coefficients to floating-point before printing.
2. **Multiplicative grouping loss** — SymPy 1.14 printed
   `r2*(gamma - 1.0)` as `r2*gamma - 1.0` in this code path.  The lowering
   pass now applies `expand_mul` before Rust printing, with an explicit
   regression test.

These are code-generation defects, not formula changes.  They are evidence
that generated Rust must always be compiler-tested/differential-tested rather
than trusted from printer output alone.
