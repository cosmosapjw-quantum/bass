# DV1-B: finite-time polarized three-lane pilot, L8 carrier acceptance held

Status: **SCOPED_ACCEPTANCE_NOT_MET**. This is a valid negative acceptance result, not a solver crash. The only unmet science criterion is `fine_L_carrier_max`: observed `2.645458623741215e-4` exceeds the frozen `2e-4`. Nine unique unit tests passed. DV-1 remains PARTIAL; progress remains5/15, production_ready=false. Do not relax the tolerance or shorten the interval to relabel this result.

Parent PR196 / `4ab97cb946a81f28c16f2e2410168e678f56a1cb`. Only additive isolated research files are changed; no production/owner/main changes or merge. Source identities are in SOURCE_MAP.json. All five vendor modules are byte-preserved parent code.

## Scope and implementation

Prescribed noncommuting finite-shear Bianchi I, normal untilted cold elastic Thomson, full-polarized bolometric carrier, `u=t/T_star` in `[0,.45]`. Physical rate is `nu=n_e* sigma_T c`; all rates are multiplied by T_star in code. Photon propagation direction and DL2 `Q+iU=sum(E+iB) spin2Z` convention are retained. Real P8 S+A is decoded as Hermitian S+iA.

The new harmonic ODE uses the analytic Wigner generator, precomputed on five STF shear bases, with full-polarized collision blocks. It does not call direct or Volterra reference sources. Its Galerkin cutoff is an explicit approximation, not an amplitude expansion. The shared initial state is supported through ell4; L4/5/6/7/8 all retain it. Unsupported initial modes are rejected, not silently dropped. Direct/Volterra share prescribed geometry and raw angular quadrature; their agreement does not independently validate shared inputs.

For exact retained c_L and truncated h_L, e_L'=A_LL e_L+A_LQ c_Q. Low moments may converge while the full angular carrier does not. This error identity is not a known bound on the unresolved tail.

## Principal measured results

At the fine20x40 grid, source endpoint errors for L4,6,8: `4.9609732e-6,2.4640788e-8,1.0712142e-10`. Full carrier sampled maxima: `8.6338564e-3,1.5584396e-3,2.6454586e-4`. Final low kinetic moment error `2.11727e-10`, ell<=4 coefficient error `3.692997e-8`. Full distribution fails the frozen target even though these low ports pass.

Direct vs independently solved Volterra, same12x24 grid at128 panels: source endpoint `1.66178e-12`, carrier `3.07809e-13`. Reconstructed off-grid source `1.49676e-11` differs from polynomial-source error `7.23194e-9`. Direct angular gap12->20 is `1.73242e-12`; harmonic tolerance sensitivity `8.24341e-14`. Neither explains the carrier discrepancy.

Saved-state decomposition gives weighted total carrier error `4.03252e-4`, retained projection norm `3.31276e-5`, outside-L8 residual norm `4.01889e-4`. This supports a cutoff diagnosis; it is not a certified continuum tail bound. I40=.15 has initial source0 but endpoint Mzz direct/Volterra/harmonic8 = `-.0006240367400941753/-.0006240367400960171/-.0006240368401986058`. Preserve its initial memory. E/B-deletion mutation is an instantaneous RHS test, not a retained finite-time counterfactual run.

## Evidence and reproduction

Full immutable archive contains detailed Korean theory/contract/DAG,90 common-ray comparison rows,54 physical rows,6 tail points, source identities, logs, figure and NPZ carrier snapshots. The Git publication contains the exact tested solver/tests/vendor, source map, concise results/DAG and delivery pointers. The full validator, saved-data checker and NPZ snapshots are in the ZIP; full-campaign reproduction commands below are run from the extracted ZIP, not a truncated Git publication.

Safe saved-data inspection (no IVPs):

    python verify_saved.py

New scoped unit tests (9 unique items):

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m pytest tests/test_harmonic_history.py -q

Fresh campaign reproduction, only under an explicit new run budget:

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python verify_dv1b.py

The science validator should exit2 when the full-carrier gate fails; do not reinterpret this as an implementation failure. It defaults to a fresh temporary cache. Opt-in local resume requires `BASS_DV1B_RESUME=1` and `BASS_DV1B_CACHE=<printed-cache-path>` with exact source identity. Never load third-party pickle caches. Delivered scientific arrays are NPZ and metadata JSON, not pickles.

The first runtime timed out and a later output serializer rejected numpy.bool_. Current-unit lost computations are conservatively debited; optional repeats were removed. Retained history counts H10/direct5/geometry4/Volterra6, plus earlier timeout upper H6/direct5/geometry4/Volterra6 and lost-output H2. Worst-case totals stay within original ceilings18/10/10/12. Reanalyses and snapshot extraction make no new IVPs. No archived campaign was rerun and no budget reset occurred. Native subagent and independent-model review NOT_RUN.

## Next unit

DV1-B::L10-cutoff-extension: extend the isolated Wigner/spin-transform support to10 with enlarged-band tests, then run only the new harmonic history at exactly the same input/time/gates. Reuse saved direct/Volterra snapshots at their six declared times. Do not promote DV-1 before the full-carrier criterion is met. Rust, generic tilt, curved Bianchi, spectra/recoil, Einstein feedback, observational sky and spatial background/fluctuation projection remain outside this result.
