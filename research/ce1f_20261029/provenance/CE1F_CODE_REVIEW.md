# CE1-F independent implementation review

Reviewer: `/root/angular_certificate_review`; 2026-10-29 Asia/Seoul. Result: **PASS_SCOPED** for the actual isolated source/certificate implementation and focused contracts reviewed below. No unresolved P0/P1/P2 finding was identified. This review covers a specified positive continuum angular table, its positive grouped quadrature, and exact-ODE source-error propagation. It does not constitute formal verification of Python/MPFR, a native implementation, measured-sky input certification, or a time-integrator error proof.

## Reviewed identities

- Parent commit: `a05906527d7dd5e5f6a653a0e4f7d977679d4a0c` (CE1-E).
- `bianchi/nonperturbative/einstein_tabulated_source.py`, SHA256 `1bfce9103c02c06f7f3477a16b2f9ccc1d3e34a0de71acd5fa6b9c5ef7115345`.
- `tests/nonperturbative/test_einstein_tabulated_source.py`, SHA256 `86ea7fdca00460dd8c2dc462d5004d3f5d7dacd8ba77cd8e7a9fddc3cdebff69`.
- `research/ce1f_20261029/{CONTRACT.md,THEORY.md,ALGORITHM.md,science.py,evidence/RESULTS.json}` read in full.
- Parent `einstein_interval.py`, `einstein_vlasov.py` and CE1-E implementation/report were read for the actual inherited mathematical and numerical contracts.

The reviewer wrote only files under `survey_review/`; no scientific implementation or test correction was made by the reviewer. The primary agent independently implemented the module and corrected the focused test reference.

## Equation-to-code checks

1. **Cell definition and refinement.** Original binary64 energy inputs are converted to exact Fractions. Refinement uses rational subdivision in both solid-angle coordinates and exact energy division by f². This preserves the original piecewise-constant density. Zero-energy cells are skipped; positive total energy is required. A representative denotes all eight implicit coordinate reflections, so moments computed from its squared direction are the correct diagonal grouped-source moments.

2. **Trigonometry and cell means.** `_trig_pi` binds MPFR `sinpi/cospi` with RNDD/RNDU. Exact special values at 0,1/2,1 are explicit. Endpoint evaluation with the interior sine maximum1 included is valid on the rational input interval in [0,1]. It does not make an invalid global monotonicity assumption. `2*pi*(tb-ta)=4 Delta phi` is the correct denominator in the average cosine-square expression. `_cell_geometry` uses the cancellation-free mean of mu² and the correct endpoint products for x/y/z ranges. Intersections with analytically established [0,1] are proof-enclosure tightening; they do not alter source data.

3. **Centered cell bias.** The implemented widths, Popoviciu variance caps, `Q=3*d²*V/4`, factors1/2 and3/8, and worst-case exponential powers match the independent Hessian derivation in `CE1F_MATH_REVIEW.md`. Taking all b_i and the volume factor at most1 is valid on the declared nonnegative log-scale box. The code uses upper endpoints outwardly and returns componentwise sums.

4. **Stored-ray correction.** `_stored_data` uses the exact rational square of each recorded binary64 ray component, not the rounded NumPy product. The segment norm floor includes `min(1,sum X)`, so it remains valid for nonunit stored representatives. The `epsilon_i/r0+M_i*epsilon_1/(2*r0³)` term correctly includes both parts of the gradient bound. Its construction accounts for the uncertainty width of the analytic cell mean.

5. **Stored mass correction.** Each exact refinement energy is compared against the actual stored binary64 mass. `|Delta w|sqrt(sum X)` uniformly bounds the kernel discrepancy because the component pressure kernel is at most r and `r≤sqrt(sum X)` in the expanding box. It is safe to add the same correction to each pressure component.

6. **Initial energy and Emax.** The continuum exact sum, exact-real stored energy `sum stored_w*sqrt(sum X)`, floating source-energy result, and their discrepancies are separated. `energy_max_upper=max(continuum.upper,stored_real.upper)` bounds both exact solutions. This closes the potential underestimate that would arise from using only the rounded numerical `energy0`.

7. **Initial expansion and geometry.** The continuum root uses exact binary sx,sy and exact sz=-(sx+sy); the stored initial state is compared directly with it, so root and trace-rounding discrepancies enter d0. Both continuum and stored expansions are checked nonnegative. The common log-scale hull follows from `h_i'≤Emax`. The inherited positive MPFR Dini propagator is applied to the proved source forcing, not to a measured fine-grid gap.

8. **API/range behavior.** The module requires explicit `python_oracle`, finite real inputs of the contracted shape, strict ordered partitions spanning [0,1], nonnegative energies and positive finite total, bounded integer refinement, positive resolved stored rays/masses, nonnegative geometry with max ell≤2, and finite end time in (0,.2]. Inputs are copied and arrays made read-only. Binary64 source evaluation and ODE time-integration errors are explicitly excluded; this exclusion is consistent throughout the code and output dictionaries.

## Independent executions

### Focused contracts

Actual command, exit0:

```text
PYTHONPATH=/workspace/scratch/c7d714747210/runtime_deps:. python3 -m pytest -q tests/nonperturbative/test_einstein_tabulated_source.py
18 passed in 2.58s
```

The base interpreter initially lacked pytest; that current-turn PACKAGE_MISSING was resolved by pointing to the already installed task-local dependencies. No runtime-unavailable status was inferred or inherited.

The final tests cover directed trig, strict exact-real L0 certificate, isotropic pressure and energy, geometric-midpoint mutation, same-density refinement, independent original-cell quadrature, amplified nonunit-ray and mass corrections, energy continuity, trace, initial Hamiltonian residual, coupled IVP, nonuniform/zero cells, copied input, invalid inputs and explicit execution domain.

The primary's first test version compared ordinary floating quadrature with a tolerance below its summation error. Its preserved result was17pass/1fail. The corrected version independently integrates the initial angular factors with90-digit mpmath while retaining the8e-16 acceptance threshold; it does not relax the requested threshold or alter the physical source. The reviewer read the corrected test and independently executed its18 cases successfully.

### Separate implementation-independent probes

- `CE1F_CODE_PROBE.json`:36 source/box cases,108 tensor48×48 original-cell quadratures, refinements1/3/8, geometry caps0,.08,.6, zero-energy cells, highly nonuniform energies and narrow/nonuniform cells. Nonzero-geometry maximum measured gap/bound0.1260502645740118; no violation above the2e-13 numerical-reference floor.
- `CE1F_TRIG_INDEPENDENT.json`:14 strict comparisons to an independently coded Decimal120 Taylor series, including rational endpoints and t=1/2±2^-100. Every reference is enclosed by the returned outward interval.
- `CE1F_L0_EXACT_REAL.json`:12 strict L0 comparisons using independent Decimal110 continuum means from the original table and independent Decimal110 evaluation of the exact stored ray/mass formula. Every component is below its certificate; maximum gap/bound0.36395234019863876.

At L0, an ordinary float source/quadrature difference can exceed the exact-real stored-source certificate because it includes unbudgeted floating evaluation error. This was observed in the preliminary probe, correctly classified as a numerical-reference floor, and resolved with the strict Decimal110 calculation. No certificate or tolerance was enlarged to hide it.

## Campaign and claims review

`science.py` integrates the original physical cell densities using a separate tensor GL source, with order32/48 and time-tolerance comparisons. It compares that numerical reference to the same table refined1/2/4/8/16, not to changing physical models. Its nine IVPs are three reference/tolerance histories, five table-refinement histories and one sign mutation. Its255 pressure probes equal51 probes at each refinement. Independent axisymmetric80-digit source integrals and high Legendre-energy moments add crosschecks; they are not used as proofs of the uniform bound.

The declared geometry target remains1e-5. Refinement8 returns a certified h upper1.1487502870767398e-5, so that candidate does not meet it. Refinement16 uses1536 grouped representative cells of the same input table and returns2.8664006502756824e-6, meeting the target. The measured h difference6.74239771791818e-8 and Hamiltonian residual around2.54e-14 are numerical falsification results, separate from the exact-ODE certificate. This is an admissible bounded refinement, not a change in tolerance or physical input.

The reported approximately second-order refinement slope1.99956785 is supported by the five recorded levels and by the analytic O(cell-width²) bound. It should remain labeled an observed slope for the recorded table rather than a general sharpness theorem. Omission of the centered Taylor term is detected at all five levels; the wrong source sign gives a constraint discrepancy around0.11948. The original midpoint mutation is likewise rejected.

All reviewed results consistently keep `time_error_certified=false`, `production_ready=false`, `merge_ready=false` and upper DAG9/15. The table is explicitly synthetic declared data, not a measured sky. No new universal no-go or physical-isotropization result is submitted.

## Closure

R6 mathematical review and this C9 implementation review are **PASS_SCOPED** for the recorded source/test bytes. No core correction was required by the reviewer. If these source or test identities change, review only the changed mathematical/code dependencies. Provider publication receipts, final archive identity, installed-wheel evidence and remote CI remain the primary agent's separate storage/packaging obligations.

