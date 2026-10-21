# S9 figure captions

All three figures target 180 mm width. State variables h, b, y and x are dimensionless.

## Figure 1: Recorded histories and absolute sample residuals

Left: actual recorded h, b, y samples for both solver arms and three tolerances, overlaid on the fixed S8 numerical reference. Right: absolute differences at exactly matching output times; no reference interpolation. The residual scale is symlog with a linear interval up to 1e-17, so zeros remain zero. The dash-dot line is the fixed 1e-9 fine-reference comparison gate. Crosses mark the last retained sample of an incomplete history. Curves join samples for display and do not certify dense interpolation or continuum angular accuracy.

## Figure 2: Recorded error divided by the unchanged gate

The denominator is printed below each column label. Ratios above one are failures and have a red outline. Labels retain measured ratios while only colors saturate below 1e-6 or above 1e3. A prefix is explicitly marked p; n/a denotes an unavailable assessment. A small prefix ratio does not pass a complete-history gate. PASS/GATE FAIL are the recorded complete-history observer verdicts; PREFIX and NO RAW remain incomplete. Additional exact-stock, moment and workspace contracts are included in the case verdict, not represented by a continuous numeric ratio here.

## Figure 3: Solver work and elapsed time in this execution environment

Left: native counters summed over recorded segments of each closed history; crosses mark incomplete histories. Work from a failing segment that returned no counters is not invented. Right: elapsed process time from PROCESS.json, including process and I/O overhead; hatched bars mark incomplete histories. Tolerances, requested output clipping and history completion differ, so these are host-local diagnostics with no portable speedup claim.

## Case states

| Case | State | Output samples | Last x | Failure |
|---|---|---:|---:|---|

| closed_mf_into_ls_r0 | PASS | 153 | 1.2 | — |

| closed_mf_into_ls_r1 | PASS | 153 | 1.2 | — |

| closed_mf_into_ls_r2 | PASS | 153 | 1.2 | — |

| flrw_mf_into_ls_fine | PASS | 153 | 1.2 | — |

| closed_small_clock4_r0 | PASS | 153 | 1.2 | — |

| closed_small_clock4_r1 | PASS | 153 | 1.2 | — |

| closed_small_clock4_r2 | PASS | 153 | 1.2 | — |

| flrw_small_clock4_fine | PASS | 153 | 1.2 | — |
