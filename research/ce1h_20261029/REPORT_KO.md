# BASS CE1-H 연구 보고서 (2026-10-29)

## 결론

**Derived**: positive collisionless diagonal Bianchi-I radiation has an exact pressure Jacobian infinity row sum 4P_i, and all P_i decrease coordinatewise on the expanding ell>=0 octant. Hence the source Lipschitz coefficient in CE1-G's nonlinear a posteriori comparison can be replaced by 4 max_i P_i(0), evaluated by outward MPFR192 from exact original angular-cell energies and means. The geometry/source box still uses the original Emax.

**Numerically checked**: on the unchanged physical table, source and Hermite RK4 panels, Emax=0.9 and Pmax=0.32500000000000007. The comparison coefficient drops 3.6 -> 1.3000000000000003 (63.89%). At refinement16, the **fresh isolated-panel** total h-error upper becomes 3.675931156248731e-6 versus CE1-G's 3.7019164499698285e-6 (0.70194% tighter). The original 1e-5 target remains met. Refinements1/2/4/8 still do NOT meet the target.

**Implementation verified**: 9 new + 72 inherited targeted tests PASS. MPFR source/whole-panel residuals were recomputed for refinement16 in four isolated OS processes (21.95 seconds including source and verification), with identical SHA-256 for source ray/mass and RK4/Hermite path across all four workers. The reconstructed CE1-G baseline source/time/total bounds exactly match the immutable predecessor evidence. This is process-level isolation, **not native subagent execution**.

**Not admitted**: distinct-author R6/C9 review, formally verified MPFR ctypes/Python implementation, generic spatial Einstein–Boltzmann, collision/polarization/native/production, full-repository policy CI, measured-sky acquisition uncertainty, merge readiness. Upper DAG remains 9/15; CE-1 PARTIAL.

## Provenance and concurrent work

- Parent BASS CE1-G PR #240, head `0fd95e4baadf8982cdb1f9f81725b7b8e8fd0aa1`, original ZIP SHA-256 `8657f6e7ad51b516896c0a9988644b12790b6cdc48372e14945f8232c4942448`.
- CE1-F PR #239 remains parent of #240. Independent alternative PR #238 was corrected in PR #241, head `2c6b6c23466cc3a08aabf0e33357e088b667ce0d`, for an exact-real stored Emax undercap 1.209228145833137e-16. No merge into CE1-H, and no claim of actual geometry bound violation.
- Latest related PRs inspected: BASS_HE #105, bass_cr #120, rec_bianchi #155, rei_bianchi #261, WU088_HH #156, htt_base #564. Their collision, chemistry, UVB and observational contracts were not imported into this collisionless CE1-H source.
- The CE1-G archive's 84 payload SHA-256 and ZIP CRC were checked before reuse. `REPLAY_RESULTS.json` explicitly marks inherited ref16 panel evidence, while `FRESH_PARTITIONED_REF16.json` records the independently recomputed current-turn four-panel MPFR values.

## Theoretical result

See `THEORY_KO.md` for definitions, exact Jacobian derivation, monotonicity, pressure moment formula and the 2x2 positive comparison propagator. The key result is

    ||P(ell)-P(ell_tilde)||_infty <= 4 max_i P_i(0) ||ell-ell_tilde||_infty,

for nonnegative ell and ell_tilde, with positive finite angular-energy measure. No approximation or numerical discretization enters this inequality.

The continuum initial pressures are obtained by exact original-cell angular means, not by nearest float64 stored rays. Independent mpmath100 cell integration and 48 Jacobian probes verify the formulas. Wolfram Language simplifies the single-ray Jacobian row-sum identity to zero.

## Coded path and results

`bianchi/nonperturbative/einstein_tabulated_sharp.py` is an opt-in Python oracle layer. It calls CE1-G's certified source/time path, replaces only the comparison coefficient, computes the exact-binary initial Hamiltonian root directly without repeating the expensive source quadrature, and retains source/initial/time+jump error decomposition. No original source files, native defaults, physical inputs or tolerances are changed.

The 9 new tests cover initial pressure sum, isotropic limit, refinement-invariant physical moments, strict sharpness, exact Hermite jump preservation, invalid backend/type rejection, unchanged target and physics, direct Hamiltonian root equivalence, and near-axis anisotropic positive-cell guard. TDD RED: import failure for missing new module; GREEN: 9 PASS. Full focused suite: 81 PASS.

### Exact-real outward h-error upper bounds

| refinement | CE1-G upper | CE1-H upper (repropagated) | target 1e-5 |
|--:|--:|--:|:--|
|1|7.071729426664234e-4|7.054251335641942e-4|NOT_MET|
|2|1.839992320006233e-4|1.835319479813658e-4|NOT_MET|
|4|4.686090215195172e-5|4.672928019569285e-5|NOT_MET|
|8|1.232291865386809e-5|1.227583245284435e-5|NOT_MET|
|16|3.701916449969829e-6|3.675931156250885e-6|MET|

The ref16 value above is the **conservative SHA-verified archived-panel repropagation**, using CE1-G's final initial-only envelope as a safe initial bound. The separate **fresh ref16** process-isolated run gives the slightly tighter 3.675931156248731e-6, with source h=2.8593843542799015e-6, time+jump h=8.16546801782192e-7 and initial h=1.8663743530269244e-16. It exactly reconstructs the archived CE1-G baseline. The difference between the two sharp ref16 paths is ~2.15e-18 and comes from the conservative initial-error reuse.

The independent CE1-G original-cell GL40/DOP853 h difference 6.543159869476511e-8 remains **falsification-only**. No new independent continuum numerical IVP claim is made.

## Runtime classification

Current Python 3.13.5 and C++ compiler probes: PYTHON_PASS and CPP_PASS. NumPy 2.3.5, SciPy 1.17.0, mpmath 1.3.0, pytest 9.0.2, SymPy 1.14.0 present; gmpy2 PACKAGE_MISSING but not required because libmpfr.so.6 ctypes backend is available. A monolithic ref16 CE1-G/CE1-H recomputation exceeded current-turn time limits (EXECUTION_FAILED for that attempt); independent per-panel processes completed and byte-identity checks passed. This is a runtime execution observation, not a mathematical counterexample or a claimed general speedup.

## Remaining claim gates

R6 distinct-author mathematical proof review: NOT_RUN. C9 distinct-author code review: NOT_RUN. Full repo RF-00/RF-BENCH-00 policy CI: NOT_ADMITTED; existing failures are separate. No merge or production promotion. This unit's scoped science and Python oracle tests are complete subject to those review gates. Original top-level DAG nodes/edges are unchanged, 9/15.

## Next bounded research

A candidate CE1-I is a time-dependent, path-local pressure Jacobian envelope using rigorous positive lower bounds on ell_i(u) for both the exact and reconstructed histories, with the same positive measure and frozen target. Another independent obligation is MPFR program-level verification; neither is automatically started. Distinct-author review should be completed before any production admission.
