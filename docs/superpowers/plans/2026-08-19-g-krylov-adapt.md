# G-KRYLOV-ADAPT Implementation Plan

**Status (2026-08-20):** historical implementation plan, superseded for
closure by the hostile-repair audit and executable regressions.  In
particular, the final API is explicitly residual-estimate-only and makes no
KIOPS parity or arbitrary-nonnormal forward-error claim.

**Goal:** Add a matrix-free adaptive truncated Krylov exponential/phi-action backend without changing BASS physics operators.

**Architecture:** Preserve PR #6 full-dimensional Arnoldi/Pade13 as a same-physics reference lane. Add a separate literature-informed module using projected exponentials, IOP(2), residual-estimate control, and adaptive Krylov dimension/time substeps. Keep all production migration blocked.

**Tech Stack:** Rust 1.94.1, nalgebra, pinned Cargo.lock/offline vendor, Python/SciPy only as independent oracle.

**Global constraints:** no physics changes; no hidden tolerance drift; m<n must be genuinely exercised; every acceptance claim requires comparison to full-Arnoldi/dense gold; fail closed on exhausted substep/rejection budget.

1. RED/GREEN adaptive exp action on diagonal n=48 with m<=12.
2. Add distinct standalone phi1 and direct scaled `t phi1` actions; route Kato-AEM2 through the latter.
3. Add non-normal/stiff negative and adversarial cases; verify error control does not underestimate silently.
4. Bind to scalar and polarized Type-II collision/Kato operators; recover second-order Kato behavior.
5. Benchmark matvecs/wall time only under same operator/output/tolerance.
6. Replay the untouched 122-test archive base separately from generated/integration regressions, locked/offline, and check changed files with rustfmt.
7. Record receipt/claim boundary and stack a single-commit PR on PR #8.
