# BASS CE1-K: canonical source-safety + panel-local pressure discrepancy

**Date** 2026-10-29. **Scope** positive, massless, collisionless, reflection-even diagonal expanding Bianchi I, Lambda=0. **Parent** BASS PR246 HEAD `4474f8acb13614ffda7a30524a815976e306efc9`; separate mathematical donor PR247 HEAD `bd94bf270dcbf3bf140ac6cf7a7caf7e72532ac0`. Neither parent nor donor mutated. This is an isolated **Draft / nonproduction** candidate.

## Completed scientific result

- Canonical PR246 files are byte-preserved: `einstein_interval.py` blob `3a3f384e793a59f0779cb09a21dd74c1ae7d0c3a`, `einstein_tabulated_time.py` blob `b2047a7a7fd64e8a1148d242ee32840f648184b5`, `einstein_tabulated_local.py` blob `c6f1a59db197766aae401d9868fcea3951f26c24`. The new module imports these and does not replace their paths or physics.
- For fixed positive continuum and exact-binary discrete measures, the pressure source difference obeys `D(ell+s*1)=exp(-4s)*D(ell)`. Combined with rigorously certified panel minima m_j for both exact and stored Hermite histories, `eta_j=min(eta_uniform, exp(-4m_j)*E_Q(B-m_j*1))`. See `THEORY_KO.md` for proof and conditions.
- Any geometry upper B_i below m_j raises an exception, rather than silently clipping an impossible box. A source/path byte fingerprint is compared before and after the certificate; this is a runtime integrity guard, not an atomic concurrency proof.
- Original exact-binary table, shear, RHS, 4-panel RK4/Hermite, MPFR192 operations and fixed `max|Delta h|<1e-5` contract unchanged. Source data, geometry Emax, pressure comparison coefficient and exact Hermite knot jumps are distinct carriers.

## Actual current-turn tests and numerics

- TDD RED (missing module): collection error, exit 2. GREEN new tests 7 passed. Rebuilt canonical parent (PR246 original archived code) 14 passed before patch. **Full scoped regressions 102 PASS in 18.47s**, exit 0, Python 3.13.5, `PYTHONPATH=.`.
- Fresh full source/time/refinement calculations 1,2,4,8: 6,24,96,384 rays respectively; full CE1-K output and initial/time source components. `run_sweep.py`, `SCIENCE_SWEEP.log`, `SWEEP_IN_PROGRESS.json`.
- **Refinement8**: canonical CE1-I `1.2273903547843227e-5` (NOT_MET), donor PR247 `9.638652224938659e-6`, **CE1-K `9.411551484445186e-6`** (MET). This is smaller angular resolution for the same certified target, **not** 4x measured wall-time speedup.
- **Refinement16**: current exact stored source rays/masses, RK4 state, Hermite coefficient and times SHA match *exactly* PR246's independent OS-partitioned MPFR192 reference. Geometry B and certified lower logscale `m=[0,.008399762101744314,.016523420850249375,.024380051867032383]` also match. Fresh MPFR192 recomputation of all four panel source caps: `[3.569278983301304e-5, 2.9241709495299544e-5, 2.358366230872103e-5, 1.861256875971887e-5]`. New source `h<=2.1459172502504843e-6`; SHA-verified **inherited** parent initial `1.865856997285437e-16` and time+jump `8.158297286595899e-7`; outward-assembled **CE1-K h upper `2.9617469790966602e-6`**, target MET. Parent CE1-I `3.6749116877624083e-6` and donor CE1-J `3.0184081966517434e-6`.
- Source-only ref16 computation finished successfully and was captured in `REF16_SOURCE_ONLY.log`, but its final JSON writer initially raised a Python `AttributeError` from shadowing `time`. A **separate, tested log reassembly** used the captured current MPFR outputs and interval-arithmetic addition, producing `REF16_SOURCE_ONLY.json`; original script variable was repaired, **full source-only script not rerun after repair**. This is an implementation/result-writer defect, not a physics discrepancy.
- Wolfram exact single-ray tests: common-scale ratio `1` and Jacobian derivative sum plus `4P` `0`. This is independent symbolic algebra, not independent-author review.
- The `REFINEMENT_CE1K.png` and `PANEL_SOURCE_CAPS_CE1K.png` figures were generated from stored inputs and directly opened/read. Target crossing occurs at refinement8; curves for PR247 and CE1-K nearly overlap, whereas source-cap contraction is visibly distinguishable.

## Adversarial risk ledger

| Priority | Object | Evidence | Consequence | Minimal remaining action |
|---|---|---|---|---|
| P1 | Formal MPFR/Python result trust | ctypes directed source and comparison, 102 scoped tests and SHA checks, no machine code verification | Not a formal proof of arbitrary interpreter execution | independent code/program-level audit, preserve exact binary source |
| P1 | Distinct-author R6/C9 | No independent-author acceptance in either parent/donor or this run | Scoped-only admission | verified separate human/agent authorship and independent provenance |
| P1 | RF-00 / RF-BENCH-00 | Parent PR246/247 policy checks failed despite scoped CI success | merge policy hold | diagnose and repair root checks separately, no blanket waiver |
| P2 | Ref16 time residual | source fresh; time+jump from SHA-verified PR246 OS partitioned evidence | not a new full time residual run | selective fresh partitioned residual for new authoritative final head if necessary |
| P2 | Mutable source during call | before/after SHA checks only | concurrency ABA not formally excluded | immutable snapshot or lock if production mutability allowed |
| P3 | Visualization | two figures read at full size | no publication-ready size verification | print-scale micro review before article use |

### Methodology references

- Neumaier (1994), *Computing* 52, 315–336, DOI `10.1007/BF02276880`: differential inequalities and logarithmic norms in validated ODEs.
- Heinzle & Uggla (2006), *Classical and Quantum Gravity* 23, 3463–3489, DOI `10.1088/0264-9381/23/10/016`: spatially homogeneous Bianchi I Einstein–Vlasov dynamics.

Neither source asserts this exact CE1-K angular cell discrepancy formula; the formula is directly derived from the frozen pressure operator.

## Decision and DAG

CE1-K `SCOPED_NUMERICALLY_CHECKED_AND_IMPLEMENTED`; R/C **18/20 scoped** stage outputs, independent-author R6/C9 `NOT_RUN`. Original upper DAG **9/15**, CE-1 `PARTIAL`, production_ready=false, merge_ready=false, auto_next=false. No full Einstein–Boltzmann, polarization, tilt, spatial Boltzmann hierarchy, observational likelihood or independent formal code proof. Next narrow unit: external distinct-author R6/C9 on the combined canonical path and RF root-policy diagnosis; do not merge parent/donor or auto-promote.