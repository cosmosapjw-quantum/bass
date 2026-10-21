# Final independent review — compact33 completed pilot

**Decision: PASS_SCOPED_COMPLETED_PILOT_AND_RECOVERY. No blocking findings.**

This review closes the earlier code review’s pending actual-data and figure checks. It is independent of the contract, production implementation and plot authors. The reviewer edited only this review directory, imported no producer analysis/solver module for the raw audit, and performed no new integration or performance benchmark.

## Admitted result

The authoritative data are `results/pilot_v2` (127 cases × 193 epochs = 24,511 samples) and `results/full62_oracles` (two cases × 193 epochs). The independent audit recomputed the 39 scientific input hashes, source base and all case identities; validated RESULT/COMPLETE/trajectory hashes; and confirmed all 13 retained owner gates for every case. The source base is:

`ee7e9ae76c852079ce86cdd5165624ab2b7fc7a9c672016501ed5da5fb4341d3`

Every saved x/z sample covers the declared z=20→2 interval. All 21 Y columns, full62 lifted states and compact33 states have the required shape. Full and half conventions agree exactly by the stated sqrt(2) conversion. n/T raw abundances are exactly zero. There are no negative raw Y values. Independently recovered maxima are baryon residual 2.1094e-15, isotope scaled conservation residual 2.5132e-15, electron-density relative reconstruction residual 6.5281e-16 and signed tensor-sum residual 2.1684e-19. The minimum sampled angular weight is 0.16873 and minimum saved optical-depth increment is 3.7544e-7.

| Comparison case | Maximum signed error | Maximum charge-fraction error | Maximum tau error |
|---|---:|---:|---:|
| s04_m04_r04 | 1.207537e-9 | 2.090017e-8 | 4.304210e-11 |
| cancel_positive_matter | 1.045091e-10 | 2.928707e-8 | 1.319342e-11 |
| Frozen acceptance limit | 3e-7 | 3e-5 | 3e-7 |

Both pairs pass. Reviewer and producer charge-fraction arithmetic differ only in whether division precedes subtraction; their maxima differ below 7e-18. This is finite implementation agreement, without a continuum-convergence assertion.

## Recovery and reuse

The NumPy JSON repair converts only scalar metadata with `np.generic.item()` and recursively visits dictionaries/lists/tuples. It leaves numerical arrays unchanged. The original atomic JSON writer is captured before assigning the full62 output adapter, avoiding recursion. The compact physics source hash is unchanged from finite admission, and the gate expression AST is identical to the donor. The earlier verification of all 57 unchanged donor files is reused.

The old failed JSON attempt still has 127 raw NPZ files under `results/pilot`; it is not the authoritative completed campaign. The successful data use their new, explicitly recorded source base and reside in `pilot_v2`.

The dispatcher and analyzer now both default to `pilot_v2`. The reviewer verified the dispatcher’s current hash against `FINAL_RESUME_VERIFICATION.json` and all 127 identity-bound `complete_reused` records. That actual focused resume used zero new workers and zero new integrations. The Codex and next-thread handoffs use the corrected defaults. Relative file inputs and lane paths derived from `__file__` support relocation of completed data; no new-machine numerical run was performed by this review.

## Figure and source check

All four final PNGs were personally viewed. Labels, legends and adopted-model captions are readable. The main time figure uses full Frobenius norms; cancellation and sweep figures retain signed coordinates. The ion figure explicitly shows all declared states, labels zero inventories and undefined fractions, and identifies equal electronic-rate assumptions. The case envelope is a scenario min–max range. The sweep consists of discrete samples with no interpolated contour.

The independent audit checks every aggregate array against each original compact trajectory, including full/half observables, Y, charge fractions and diagnostics. All 250 sweep values match their raw endpoints and same-shear controls exactly. Cancellation curves, subtraction and q ratios match the raw arrays exactly. All 16 listed data/figure output hashes match, including final PNG and PDF files. The author’s 571 exact line-artist checks and rendered-PDF inspection receipt are reused; the reviewer personally inspected PNGs and verified the PDF hashes.

For positive initial matter stress, the initial cancellation ratio is 2.1684e-16 from floating-point construction, rather than bitwise zero. The final signed shear is -5.083174e-5 and q=0.7377993. The opposite seed yields +5.082930e-5 and q=0.7378080. The raw zero-seed control maximum is 3.189257e-20 and remains present in source/output.

## Limits of admission

This is a finite, prescribed-temperature/external-UV, test-fluid preliminary model. It carries the declared H-through-Li inventory with photo/RR/DR and electron-density Thomson feedback. It does not complete thermal/radiative Q^a closure, active thermonuclear fusion, CI/CX, molecular or secondary-electron physics, isotope-specific electronic rates, non-LRS evolution, or resolution convergence. The 33-state subspace depends on even LRS parity, equal isotope rates/fractions and the zero n/T inventory. Baryonic anisotropic stress is zero; the anisotropic matter component is separately collisionless and massive.

The donor Einstein gate is an algebraic check using the same Friedmann definition. Angular positivity concerns the saved epochs and sampled angles. Neither is a proof of global error bounds or continuum convergence. The 62→33 reduction does not establish a measured speedup. NCP 64 CPU / 128 GiB remains the target; the actual pilot used an 8-CPU-quota/8-GiB sandbox with four workers.

Root may close, publish and back up Stage C with this scoped acceptance. No further integration, detailed benchmark or optional broad review is needed for this contract. Delivery ACKs and backup verification remain root’s publication responsibilities.

## Evidence

- `FINAL_REVIEW.json`: decision, source identity, scope, file hashes and closure of earlier findings.
- `FINAL_RAW_CHECK.json`: independent numerical/hash audit output.
- `check_final_raw.py`: reproducible read-only audit; no solver import or call.
- Earlier `CONTRACT_REVIEW` and `CODE_REVIEW` files remain historical stage records.
