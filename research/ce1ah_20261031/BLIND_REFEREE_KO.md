# CE1AH same-context adversarial scientific review, bounded one pass

**Scope:** CE1AH original Einstein–Vlasov constrained initial-shear tangent dynamics. This is a same-author review, NOT distinct-author R6/C9.

| Object / attack | Observed check | Verdict and limit |
|---|---|---|
| Initial-shear perturbation violates Hamiltonian | Exact initial derivative `δH=σ·δσ/(6H)` and full nonlinear ±ε H computed from constraint; all C(0) ~ 1e-16 | PASS scoped. A factor-of-two alternative `/(3H)` is wrong and explicitly excluded |
| Wrong pressure linearization / factor of 2 | `∂_ell_k P_i= -P_i-2δik P_i+Rik`, independent finite differences GL6/8; column sums match `-E-Pk` | PASS scoped; continuous source calculus exact, numerical check sampled |
| Fixed-geometry derivative confused with backreaction | Full 18D tangent includes `-θ δh_i-h_i δθ` and `J δell` plus constrained variation of H(0). Independently finite-differenced full nonlinear 6D IVPs | PASS scoped, physical feedback retained |
| Wrong Condon-Shortley l4 | Explicit real Y40,Y42,Y44 vs independent SciPy sph_harm_y for anisotropic ell; C4 parent CE1AE saved GL6/8/16 401 epochs | PASS scoped; no imaginary/signed phase inferred from reflection-even source |
| Harmonic gradient lacks intensity normalization | Exact covariance expression and common dilation `Σ∂ell alpha=0`, 3-axis FD tests | PASS scoped |
| Tangent vacuum/dust or fluid closure smuggled | Original massless collisionless source, exact rank-four R in J, no perfect fluid or thermal/compton closure | PASS scoped; only diagonal Bianchi I |
| Conservation and units | Background |Hamiltonian| < 1e-12, tangent |δC| < 1e-12, δ log F+∫δq ≪ 1e-10; BASS dimensionless u=t/Tstar explicit | PASS scoped; not observational |
| False GL continuum certification | GL6/8/16 endpoints match numerically, no rigorous spectral/source enclosure for tangent | NOT CERTIFIED, production HOLD |
| Source drift | Original array SHA and Git blob identity, negative tamper test | PASS scoped; original CE1AF histories read-only |
| Missing true independent reviewer | Host native subagents absent; Wolfram symbolic tool previously returned unrelated expression; primary proof is direct algebra and Python/SciPy FD | R6 and C9 distinct-author NOT_RUN |

**Smallest future validation, not requested within this unit:** distinct-author review of `J`, constrained derivative `δH`, harmonic angular kernel; rigorous angular-continuum tangent quadrature enclosure if production grade is needed. Stop here; no invented DAG closure.
