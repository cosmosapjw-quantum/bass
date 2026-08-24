# Next: WSC-4 Jacobian / sparsity / JVP parity

After WSC-3 review, the next compiler pass should generate and cross-check:

1. analytic Jacobian of residual and mass-matrix forms;
2. structural sparsity patterns;
3. matrix-free JVP programs;
4. optional VJP metadata for later sensitivity work;
5. Wolfram `D`/`SparseArray` and SymPy independent crosschecks;
6. Rust-lowering-ready block/JVP metadata.

Production migration remains blocked.
