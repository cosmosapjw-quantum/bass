# BASS B3b2 independent figure review

**Disposition: PASS_SCOPED. Scientific presentation blockers0; cosmetic blockers0.**

Reviewer /root/b3b2_crossrepo_census directly opened the actual final PNG with the image viewer, read the producing reference_runner.py, and checked its actual CSV/JSON inputs. This is an actual rendered scientific figure, not a generated illustration or a reconstructed claim.

## Reviewed artifact identity

| Artifact | SHA256 |
|---|---|
| LOCKED_CELL_BRIDGE.png | 08479a47282e21337be1eb29e4765774c3ce3edad7c22bb8189c7182cdd6510e |
| LOCKED_CELL_BRIDGE.pdf | 172fa33daceb9abe4f62e333d502a8bd58d87adbf63e7d2a7209a43d57444118 |
| CELL_STOCK.csv | 47161a5765649d08a16cdfd35b17e3378a5a8f08a27906f21eca8b2475e85331 |
| Final BOOST_COVARIANCE.csv | d59e66fdb65a1494f152c29b976bed2d59a43d8d2d3889efd9299f09518fa45d |
| ENERGY_OWNER_MUTATION.csv | 3acc123fc0bf6e4d60424bf2f7f581ea2e3db3ae9a0bc1afd87db2061da8ebd0 |
| reference_runner.py | 2e057497d21720c6f0905158d4bb164bb4f4591a518554d13eb1dd754ac227a0 |

Direct visual inspection applies to the PNG. The PDF is the same matplotlib figure export with its recorded bytes; a separate PDF rasterization was not performed or claimed. The PNG provides legible titles, tick labels, axis units, legends and four nonoverlapping panels.

## Panel-by-panel assessment

| Panel | Actual content inspected | Judgment |
|---|---|---|
| (a) Locked inventory |35 labeled cells, actual photon stock in m^-3 and saved cp_i in eV on a separately labeled right axis. Source identified as scalar isotropic bootstrap INITIAL-DATA. | PASS. The energy curve follows cell order, so its jumps are between distinct labeled groups, not evidence of interpolated spectral dynamics. |
| (b) Correct state boost | N/T residual divided by machine epsilon for axial and nonaxial boosts of separately labeled synthetic anisotropy on the actual grid. Frozen512-epsilon criterion stated. | PASS. The plotted low residual scale is readable; it does not imply an interval certificate. Actual isotropic cases remain in the36-row machine-readable data. |
| (c) Rejected omission | N/T residuals with w'=D w deliberately omitted, explicitly marked REJECTED. Axial/nonaxial styles distinguish transformations. | PASS. This displays a rejected state-transformation mutation, not an alternative physical result. |
| (d) Rejected energy owner | Actual competing parent target energy substitutes for saved cp_i. Photon-number relative change0, energy-density relative change -6.274855397481909e-09. Y axis scales by10^9, bar annotations show raw signed changes. | PASS. Both the scale convention and mutation status are visible; the zero number result is not hidden by a positive plotting floor. |

Source-data provenance is appropriately narrower than a full trajectory. The panel(a) input is the saved scalar/unpolarized isotropic hydrogen-frame bootstrap INITIAL-DATA; the plot does not relabel it as reconstructed native angular data. The displayed anisotropic case is synthetic and clearly labeled.

## Data-to-figure consistency and zeros

CELL_STOCK.csv has35 rows. BOOST_COVARIANCE.csv has36 rows:2 scenarios by2 charts by9 speeds. ENERGY_OWNER_MUTATION.csv has1 explicit rejected mutation. The plotting code selects the synthetic scenario for panels(b)/(c); no data selection is concealed by a claim that those panels show the actual isotropic input.

The plots use linear y axes. Numeric zeros remain at zero. In panel(d), the number bar is exactly the stored0.0; the energy bar retains its negative sign. Panel(b)'s phrase 'Zero is plotted at zero; no fabricated floor' describes plotting treatment, not a claim that every covariance residual is analytically or numerically zero. No missing value or underflow is encoded as a false nonzero log floor.

The numerical criterion uses a global L1 absolute-contribution scale, which is defined in VALIDATION.json and the code review. Near-zero symmetry components therefore do not produce misleading componentwise relative ratios.

## Binding to the targeted inverse repair

The P2 inverse fix changed no plotted formula or field. Its affected check saved the previous data and updated only inverse_positive_f_relative in12 of36 CSV rows. The reviewer compared all other CSV fields and found them unchanged. The actual inverse roundtrip and max inverse residual were refreshed in VALIDATION.json, while N/T, cell stock, mutation values and the PNG/PDF bytes stayed fixed.

This figure therefore remains bound to the admitted current result without another rendering campaign. It is evidence for a snapshot representation bridge and its rejected mutations. It is not evidence for finite LINE01 absorption, source clocks, native/COM source replacement, coupled background evolution or production readiness.

## Review separation

This figure review is independent of the implementing agent and same-model with the controller; different-model scientific review remains NOT_RUN. Visual inspection and byte/CSV consistency checks required no scientific rerun, IVP, old campaign replay or remote write. Publication and backup ACKs remain separate parent-owned steps.

## Focused runtime-loss recovery readback — PASS_SCOPED

After actual shared-scratch loss, the controller authorized exactly one reference_runner invocation to regenerate missing CSV/figure artifacts. This is a new explicitly logged recovery run, not an original pre-loss log or an old campaign replay. The reviewer did not execute scientific code during this readback.

Original approved code d88571cc11fcfe441f117977a7eece63e3c58ac06543e45542e2f54af12b819e, tests4bdbcdb72cf4247f7962b657f2750115295fd589de2d780eba554d3a4f36f830, reference runner2e057497d21720c6f0905158d4bb164bb4f4591a518554d13eb1dd754ac227a0 and both vendor files match their retained pre-loss SHA256 exactly. The separate recovery harness differs from the original wrapper only in the ledger and stdout/stderr filename prefixes; one-thread execution and CPU20s/wall30s guards are unchanged.

Actual recovery command: python code/reference_runner.py, cwd /workspace/scratch/fe69646d3c76/bass_source/research/bass_b3b2_locked_cell_bridge_20261024. Started2026-10-24T08:33:56Z; exit0; child wall3.331809647999762s and CPU3.323592s; stderr empty. This is additional observed cost; historical remaining budgets are stillnull and budget_reset=false. The fresh ledger has one entry and does not erase the earlier runs/probe.

Known pre-loss physical N/T, stock density, direct residuals,36-case covariance maxima, corrected inverse maxima and all energy-mutation aggregates agree exactly with the new JSON values. All three CSV files and the final PNG match their pre-loss SHA256 exactly. The PNG is379033bytes with SHA08479a47282e21337be1eb29e4765774c3ce3edad7c22bb8189c7182cdd6510e, so the earlier actual visual inspection is reusable by byte identity; a new visual inspection is not claimed.

Regenerated PDF SHA85404f7a827b9d32f4a4ab4eab5787822da1738e037d173557ea9fcb8359362d differs from the old172fa33daceb9abe4f62e333d502a8bd58d87adbf63e7d2a7209a43d57444118 and contains new creation metadata. Exact old PDF bytes are not recovered, and an exhaustive attribution of every byte difference is not claimed. Likewise, new VALIDATION.json is a new result file; its numeric content agrees but its old post-C9 annotation/history is retained separately in this review rather than falsely claiming exact old JSON bytes.

RECOVERY_READBACK_REVIEW.json binds current hashes, actual raw receipt, equality checks and these limitations. Final scientific/code/figure disposition remainsPASS_SCOPED, open blockers0, different-model scientific reviewNOT_RUN. No new unit-test suite, IVP or old campaign replay was requested by this reviewer. Publication and backup ACKs remain separate controller gates.


