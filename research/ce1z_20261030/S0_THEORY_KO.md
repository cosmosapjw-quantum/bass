# CE1-Z S0 | 원본 BASS Rust K4 두 시점 Gram 스펙트럼

2026-10-30 · bounded unit; parent PR271 exact HEAD `9cf562496cb753fe831e684ccf0b4dd54f5c5d94` · ancestor PR268 `c4d303ebd8294df8a4b564b140b88fc8e57b0e67`. Preserve unmerged drafts, main and six-cell immutable source `022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`. BASS Rust source Git blob `a29b12b5e7b0d529bddaf9eac53cfdb984ddaa84`. No new continuum model.

## Exact model theorem (derived)
For the frozen reflection-even massless collisionless Bianchi I scalar angular-energy sky, normalization and Condon–Shortley conventions are those of PR271:

\[\alpha_{4m}(u)=4\pi a_{4m}(u)/E(u),\quad X(u)=\frac13(\alpha_{40},\sqrt{2}\alpha_{42},\sqrt{2}\alpha_{44})\in\mathbb R^3.\]

At any sampled proper times \(u_j\in[0,0.08]\), the deterministic unequal-time kernel is exactly
\[K_{jk}=K_4^\delta(u_j,u_k)=X(u_j)\cdot X(u_k),\qquad K=XX^\top\succeq0,\quad\mathrm{rank}(K)\le 3.\]
Proof: the original eight-reflection symmetry removes odd m and imaginary parts, and reality pairs m and -m, leaving m=0,+2,+4. For all real c, c^T K c = |X^T c|^2 >=0. S=X^TX (3x3) and K (41x41) have identical nonzero eigenvalues. This is a deterministic Gram relation, **not** stochastic covariance, independent ensemble realization, observed Planck C_ell or likelihood matrix.

The source-locked 6x41 BASS-Rust native sky outputs and 6x1681 PR271 pair records are reused *as data*. No new Rust propagation, MPFR math source proof, or DOP853 interval proof is claimed. The strict original \(h<10^{-5}\) criterion remains unchanged and already MET at GL6 N4.

## Science question (bounded)
Measure eigenmode fractions, effective participation ratio \(R=(\mathrm{tr}K)^2/\mathrm{tr}(K^2)\), and the unequal-time shape cosine \(r_4(0,.08)\) for GL6/8 and 4/8/16 panels. Independent reconstruction from immutable original BASS Rust sky CSV must match the frozen K4 pair CSV without re-running the IVPs. Test symmetry, PSD, rank<=3, positive exact source/energy, source Git blob, all six combinations, and tamper failures. Quantify whether the existing PR270 conditional entrywise upper radius \(\epsilon_K\) can in principle resolve the second nonzero eigenvalue via \(|\delta\lambda_i|\le41\epsilon_K\) (Weyl): this **does not** by itself certify a binary64 Rust sky center.

## Status and permissions
Upper science DAG **9/15** (21 edges), CE-1 PARTIAL, new completed upper nodes=0, production_ready=false, merge_ready=false, auto_next=false. Native subagent NOT_RUN (no dispatch facility); distinct-author R6/C9 NOT_RUN. Preserve original fixed positive six-cell and all source SHA identities. Stop after this one subgate; no automatic merge.
