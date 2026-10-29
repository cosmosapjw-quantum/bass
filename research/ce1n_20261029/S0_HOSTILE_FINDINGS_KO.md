# CE1-N S0: hostile MPFR direct certification premise check (2026-10-29)

PR #252 parent HEAD `8e26188d03197b0a4f878c5ce98e015468a4e24b`, pinned MPFR module Git blob `abbab0990fdefaf535ccbf5191ae3e060cb19214`. Original six-cell CE1-M physics and 384-ray result are protected, upper DAG **9/15**, CE-1 PARTIAL.

**RED #1 (P1, polynomial source only):** `_mismatch_coefficients(source,K)` retains an unkeyed `_ce1c_exact_mismatch_cache[K]` across positive stored mass/ray rebinding. For `PolynomialRadiation(ntheta=8)` at `ell=(0,0,0)`, first certificate x upper `1.193178730416563e-15`. Rebind stored `source.mass=source.mass.copy()*2`; the old certificate is reused, despite exact continuum x pressure `0.294` and valid exact-rational+MPFR pressure mismatch lower `0.29399999999999954`. A positive ray factor 1.001 similarly yields gap lower ~0.000294 but printed bound ~`2.586594364224074e-12`. This refutes a direct **mutable polynomial source certificate premise**, not the unchanged original positive tabulated CE1-M fixture.

**RED #2 (P1, lower direct time API):** `residual_taylor_mpfr(...,subcells=-1)` skips all subcell tests and returns `ell_defect=h_defect=0`; valid subcells=1 returns ~2.031e-5 and 1.046e-4. Higher-level tabulated certifier already validates 1..32; this failure is the unguarded directly callable residual routine.

**Executed:** three focused new adversarial tests `3 FAILED / 0 PASS, exit1, 0.80s`; frozen source from PR252, current-turn `PYTHON_PASS` 3.13.5, `CPP_PASS` g++14.2, libmpfr.so.6 accessible. Native delegated subagent `NOT_RUN`.

**Minimal repair:** calculate exact mismatch from current source, rather than cache keyed by K alone; validate `subcells` is non-bool integer 1..256 before MPFR derivative work. Retain all physical equations, target `1e-5`, source normalization, RK4/Hermite, 192-bit precision and positive signed-mass exclusion. Test against rational oracle, mpmath 100 dps and affected original MPFR science regression. No production or formal-program proof claim.

S0 create-only ZIP `BASS_CE1N_S0_20261029.zip`: **5380 bytes**, SHA-256 `b24a52e1bc44c360ff35902ab98cc8003ae7af37af826bfa903c363335dee538`, 3 files, CRC PASS. S1 to implement minimum fixes.