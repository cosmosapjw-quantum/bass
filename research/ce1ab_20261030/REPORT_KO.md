# CE1-AB | DOP853 continuous GL IVP to original six-cell physical Gram

**Bounded new physics (2026-10-30, conditional on predecessor proofs and MPFR implementation)**

- Exact parent PR275 HEAD \`bc06cb2fc3952477b437891d8b04650f8f164b40\`. Parallel sibling PR273 remains independent. Source SHA256 \`022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035\`.
- The original SciPy 1.17.0 DOP853 solver with original self-consistent six-cell Einstein–Vlasov RHS has been replayed; GL6 and GL8 each reproduce 41×6 original binary64 geometry entries exactly. The 3 adaptive segments' regenerated hex F coefficients **are not claimed to be original archived dense coefficients**.
- Rigorous *conditional* directed MPFR192 a posteriori residual enclosure: GL6 \`η_GL ≤1.712475127509631e-6\`; GL8 \`η_GL ≤1.7124854278440174e-6\`. Both satisfy unchanged original strict \`h<1e-5\`. 32 slabs per adaptive segment, full initial/jump/domain guards.
- Original exact six-cell continuum geometry to saved 41 states: GL6 \`≤1.7124756750269696e-6\`, GL8 \`≤1.7124854392150078e-6\`. Includes inherited PR264 exact source vs GL exact ODE and dyadic last-time extension.
- Directed MPFR192 82 new angular Jacobian records: \`||ΔS||₂≤7.696298836326487e-6\` (GL6), \`≤7.696345757810941e-6\` (GL8).
- With inherited PR270 uniform original continuum source-only bound and PR275 source-at-fixed-state Gram: **λ₂(41-sample Gram) > 2.4422537651068245e-5 (GL6); >2.9964894483083110e-5 (GL8)** on the actual continuous self-consistent Einstein–Vlasov spacetime. This also implies continuous-time kernel rank≥2 by continuity; it does **not** numerically bound the corresponding time-integral operator's λ₂.
- New local 12/12 pytest and isolated S2 ZIP extraction 12/12 PASS. Exact 99/99 original source manifest PASS. Exact independent distinct-author R6/C9 NOT_RUN.

Source and test code are in this branch. Reproduce physical evidence in \`CE1AB_S1_IMPLEMENTATION_AND_SCIENCE_20261030.zip\`; S0 derivation in \`CE1AB_DERIVATION_KO.md\`. GitHub CI separately reports any new remote verification.

**No third Gram mode, spectral temperature, polarization, ensemble covariance, CMB likelihood, production readiness, merge or auto-next.**
\`UPPER_DAG=9/15\`, edges21, \`CE1=PARTIAL\`, scoped R/C 18/20, R6/C9 distinct-author NOT_RUN; STOP_AFTER_ONE_BOUNDED_UNIT.
