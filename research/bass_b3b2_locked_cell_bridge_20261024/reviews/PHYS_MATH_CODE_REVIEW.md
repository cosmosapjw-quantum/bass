# BASS B3b2 independent physics, mathematics and code review

## Final disposition

**PASS_SCOPED after one targeted repair. P0=0, P1=0, P2 open=0.**

The initial independent review found one concrete P2 inverse-representation defect and placed the general reversible-adapter claim on HOLD. One bounded reviewer probe reproduced it. The controller authorized a narrow repair; the reviewer then read the actual repaired function, added regression, affected raw results and source hashes. The HOLD is now closed. The original actual 35 by 26 forward/covariance results remain valid throughout; the failed inverse edge case and correction are preserved below.

Approved scope: an opt-in, labeled conversion of the actual locked REC photon inventory to BASS massless snapshot packets, physical N/T agreement, fixed-grid inverse, true vacuum and state observer covariance within the frozen floating checks. This review admits no LINE01 incident-boundary reconstruction, atomic-source replacement, event-rate coupling, finite absorption update, IVP, production source or merge.

Reviewer: /root/b3b2_crossrepo_census, separate from the implementing agent. This is an independent same-model scientific/code review. **Different-model scientific review: NOT_RUN.** A requested lower-tier implementation does not itself constitute a different-model scientific review.

## Exact reviewed targets

| Target | SHA256 |
|---|---|
| FROZEN_CONTRACT.md, repaired R6 target | df63c3328c2ab4ab8c7f5ac5e5c122b354c892a3845dd09f69645500027cc653 |
| theory/SNAPSHOT_BRIDGE_THEORY.md, repaired R6 target | 396e6e802955a4eb6256e2b43dd7e4fc58a5929d9fc103a394b0107a92069ad3 |
| Final code/locked_bridge.py | d88571cc11fcfe441f117977a7eece63e3c58ac06543e45542e2f54af12b819e |
| Final tests/test_locked_bridge.py | 4bdbcdb72cf4247f7962b657f2750115295fd589de2d780eba554d3a4f36f830 |
| code/reference_runner.py | 2e057497d21720c6f0905158d4bb164bb4f4591a518554d13eb1dd754ac227a0 |
| Final artifacts/VALIDATION.json | ba5e927157967caf2840309fb1ddf6d9f0da4f7d1fa6bf8ed1b45f573d745aee |
| C9 affected-check script at focused readback | aa9f7abf4e61b36ebbb7c5cb0f1d3d6930386edc78974fb525fe025c0a1686d1 |

Final source/test hashes match the hashes in the actual affected-command receipts. Unchanged vendor Git blobs were independently recomputed from the local bytes: kinetic.py 1fef508f01479508e5489cf8a167d2aff8184a81 and core.py 3e95a652715b346a47f097fde2131540237390a4. No vendor implementation was rewritten.

The actual three NPZ identities are preserved in inputs/IDENTITY.json and checked by the loader before allow_pickle=False reads. Source ownership was checked against the actual REC source copies: bose_photon_number, build_source_derived_bootstrap_parent, and PR43 _network_energy_coordinates_eV. These use G*f*normalized angular weights, a hydrogen-frame scalar/isotropic bootstrap state, and tracked momentum_scale*c respectively.

## Independent mathematical and implementation checks

### Number current, stress and dimensional conversion — PASS

With n_ij=G_i A_j f_ij and ell=(1,n_direction), the actual direct sums use N=c sum(n ell) and T=sum(c p_i n ell ell). N^0/c is number density; T^00 is energy density; c T^0i is physical energy flux. G is in m^-3, p in kg m s^-1, A and f are dimensionless. The saved cp, rather than a recomputed centroid or target energy, is the physical energy authority.

For kappa=8 pi G_Newton/c^4, alphaL=kappa L^2 has units m^3/J. Therefore k=(p/Pstar)n_direction and w=alphaL c Pstar n are dimensionless. Substitution into unchanged kinetic.tensor, sum((w/e) p4 p4), gives alphaL T with e=p/Pstar. Number recovery sum(w ell)/(alphaL Pstar) supplies the required c. The existing moment function gives state pressure/stress; no U, J, PiRate or Source object is constructed by the new adapter.

The implementation retains the actual 35 by 26 grid rather than substituting a lower-order emission cubature. Normalization raw_A/sum(raw_A) occurs only in the source-specific intake; the general LockedGrid validator rejects unnormalized A. No extra 4 pi, polarization factor, invented bandwidth or Doppler-width adjustment is introduced.

### Physical oracle and mutations — PASS

physical_sums is a direct SI double loop over G, A, f and saved cp. It does not call to_packets, packet_observables or vendor moment/tensor formulas and does not use BASS scale parameters. A separate Fraction-based rational fixture supplies exact expected N/T and an explicitly specified beta=3/5 matrix with gamma=5/4. Thus the expected moment is not obtained by sending the same implementation output back to itself.

The nonaxial covariance experiment uses the existing boost_matrix in its tensor expectation as well as in the packet boost. This shared component is bounded by independent algebraic inspection of the matrix gamma^2/(gamma+1) spatial term and by the separately specified exact axial oracle. It is not presented as an independent implementation of every Lorentz matrix element.

The tests detect wrong G normalization, the actual competing parent target-energy replacement, and omitted state weight reweighting. The target-energy mutation leaves the measured photon number unchanged while changing energy density by -6.274855397481909e-09 relative and T by 1.0957342862106858e-09 in the frozen global-L1 scale. These effects are above the frozen threshold. The omission mutation reaches T covariance residual 0.07371223129259362. Their rejection directly probes physical ownership and transformation risks.

### Frame, labels and inverse — PASS after P2 repair

The packet state binds the exact grid digest, cell labels, angular labels, units and a 4 by 4 frame matrix. A fixed-grid inverse rejects changed grid/labels, nonzero mass, off-grid k and a nonidentity observer frame. Explicit inverse boosts are checked against the original grid. This is not a general packet rebinning or an inverse of aggregated moments.

Active plus-sign beta agrees with the existing kinetic owner. Under D=E'/E, density weight w'=D w and ell'=Lambda ell/D give N'=Lambda N and T'=Lambda T Lambda^T. This snapshot simultaneity-slice density rule is not applied to the invariant spacetime event measure dR. The B3a event/state distinction and G1B reduction are preserved.

The source is bootstrap INITIAL-DATA, with coupled_macro_endpoint=false, not a completed coupled trajectory. The actual builder is restricted to a validated Bianchi-II source branch and repeats scalar Planck-plus-distortion occupation isotropically in the hydrogen tetrad. Synthetic anisotropic tests are labeled accordingly. A state snapshot has no rate clock; the adapter correctly assigns none.

### Vacuum, domain and arithmetic — PASS_SCOPED

True vacuum is represented by the same nonempty canonical momentum grid with exactly zero weights. This is compatible with the unchanged kinetic validator, avoids log weights, and yields exactly zero current/stress in the tested boosts. There is no epsilon photon seed, donor reservoir or positivity clipping.

Finite-real validation rejects complex, negative and nonfinite inputs. Arithmetic guards reject positive products erased to zero, nonfinite scaling, unsupported mass-shell energy, positive w*e or w/e failure, and recovered positive contributions erased by division. The inverse repair retains those checks. Floating tolerance statements are for the actual locked data and declared diagnostics, not an interval certificate or a guarantee that every mathematically positive binary64 scaling is supported.

## Actual numerical evidence read

Exact argv/cwd, code/input hashes, environment, process exit and measured child CPU/wall are in artifacts/EXECUTION_LEDGER.json and its raw COMMAND files. The reviewer read the commands and outputs rather than treating test names as evidence.

| Evidence | Actual result and scope |
|---|---|
| Pre-repair unit suite | 10 methods passed. The inverse edge case below was not yet among them; this is not a claim that it passed initially. |
| Actual state | 910 packets, number density 106530.54352303005 m^-3, energy density 1.740735402878829e-13 J m^-3 |
| Direct moment comparison | N residual 4.018991460485999e-19; T residual 2.279091117273708e-16 |
| Covariance data | 36 rows: actual isotropic and synthetic anisotropic stocks, axial/nonaxial charts, nine speeds 0 through0.8 |
| Max covariance residuals | N 1.1775832543398129e-15; T 3.717949182316828e-16, below512 epsilon=1.1368683772161603e-13 |
| Repaired actual inverse | Max positive-f roundtrip residual0.0 in the stored binary64 computation; this is a measured zero, not a universal exact-arithmetic claim |
| Repaired inverse-boost diagnostic | Max positive-f relative residual1.1102230246251565e-15, below128 epsilon=2.842170943040401e-14 |

Residuals divide max component error by the global L1 absolute-contribution scale. They do not divide by a vanishing tensor component. The exact-zero residual path tests actual zero rather than installing a log floor.

Command01 failed with UnicodeDecodeError while attempting to decode the stored parent_payload bytes as UTF-8. Its exit1 and raw stderr remain in the ledger; subsequent numerical calls succeeded. The source input is used through its actual arrays and not through that failed ad hoc text interpretation. This failure must not be described as first-run PASS.

The pre-P2 reference run at command06 used bridge SHA b3dd10bda92adff488e332778fccc8e81ef047ec620b1dae62fb355491ca5be3. The repaired bridge is d88571cc11fcfe441f117977a7eece63e3c58ac06543e45542e2f54af12b819e. Only affected inverse operations were rechecked afterward; the full old suite was not replayed by this reviewer.

## P2-C9-01: dummy unit-occupation overflow — found, reproduced, repaired

### Initial finding and HOLD

Before the repair, fixed_grid_inverse called to_packets(grid, ones, units) merely to obtain expected geometry. It then formed weight_factor*G*A as one denominator. A supplied state could be representable even though the irrelevant unit-occupation state and combined denominator overflowed.

The independent one-cell probe used G=1e301, p=1, A=1, direction=(1,0,0), f=1e-301 and Units(1,1,1). The real forward state had finite w≈299792458 and finite N/T, but fixed_grid_inverse raised 'packet weight: nonfinite arithmetic or positive underflow' while constructing the dummy state. Reversing the actual forward products, (w/weight_factor)/(G*A), recovered1e-301 with measured relative error0. This is an implementation-domain defect, not a negative weight, bad physical source or a failure of the inverse equation.

Full original argv, cwd, stdout/stderr, source hash and timing are preserved in INDEPENDENT_PROBE_01.json. One-thread guard CPU5s/wall10s; actual child wall0.09185697700013407s, CPU0.091173s, process exit0. Exit0 means the planned defect reproduction succeeded, not that the defective inverse was accepted. Reviewer IVP0, old campaign replay0, full suite replay0.

### Controller-authorized targeted repair

The current inverse now builds expected labels and expected k directly, without a fake occupation or weight. It computes n=w/weight_factor and then f=n/(G*A), reversing the accepted forward products. Finite and positive-underflow guards apply at both divisions. Equations, data, tolerances, source ownership and vendor code are unchanged.

### Actual focused regression readback

| Command | Check | Exit | Wall / CPU seconds |
|---|---|---:|---:|
| 07 | unittest -k inverse: existing boost/inverse, incompatible identity/frame, new large-G/small-f regression; 3 passed | 0 | 0.17157508298987523 / 0.17097999999999997 |
| 08 | unittest -k actual: actual910-packet forward/inverse and saved energy-owner check;1 passed | 0 | 0.19751311800791882 / 0.195883 |
| 09 | C9_AFFECTED_CHECKS.py: actual fixed inverse and36 inverse-boost errors only | 0 | 0.15585186700627673 / 0.15497799999999998 |

The current test file contains11 methods. Evidence is the original10-method pass plus the named affected regressions after repair; no claim is made that a full current11-method suite was rerun.

The affected script preserves PRE_C9_REPAIR/VALIDATION.json and BOOST_COVARIANCE.csv, updates only inverse-dependent fields and records C9_AFFECTED_CHECKS.json. The reviewer compared the CSVs:36 rows, only inverse_positive_f_relative changed, in12 rows. All plotted N/T and mutation columns remain identical. Thus the already inspected figure need not be recomputed.

**P2-C9-01 status: CLOSED.** No further optional numerical probe or broad test replay is warranted for this claim.

## Figure and publication boundary

FIGURE_REVIEW.md separately records direct PNG inspection and the data/plot binding. Its disposition is PASS_SCOPED. The numerical result, code-review decision, backup upload ACK and eventual publication ACK are separate records; this reviewer performed no remote mutation or publication.

The parent may proceed to its own fresh expected-SHA publication gate for the reviewed research-only tree. Historical remaining wall/CPU budgets remain null and budget_reset=false. New IVP0, old campaign replay0, merge0 and production activation0 remain required.

## Reviewer process record

One bounded scientific probe was run to resolve the concrete P2 risk. No second reviewer probe or suite rerun was run. Read-only byte/CSV checks and actual source/log inspection supplied the remaining evidence. A metadata-only assertion that the ledger still ended at command07 became stale when the implementer appended affected commands08/09; it failed, and the reviewer reread the append-only ledger. This caused no scientific execution or deleted evidence.

## Focused runtime-loss recovery readback — PASS_SCOPED

After actual shared-scratch loss, the controller authorized exactly one reference_runner invocation to regenerate missing CSV/figure artifacts. This is a new explicitly logged recovery run, not an original pre-loss log or an old campaign replay. The reviewer did not execute scientific code during this readback.

Original approved code d88571cc11fcfe441f117977a7eece63e3c58ac06543e45542e2f54af12b819e, tests4bdbcdb72cf4247f7962b657f2750115295fd589de2d780eba554d3a4f36f830, reference runner2e057497d21720c6f0905158d4bb164bb4f4591a518554d13eb1dd754ac227a0 and both vendor files match their retained pre-loss SHA256 exactly. The separate recovery harness differs from the original wrapper only in the ledger and stdout/stderr filename prefixes; one-thread execution and CPU20s/wall30s guards are unchanged.

Actual recovery command: python code/reference_runner.py, cwd /workspace/scratch/fe69646d3c76/bass_source/research/bass_b3b2_locked_cell_bridge_20261024. Started2026-10-24T08:33:56Z; exit0; child wall3.331809647999762s and CPU3.323592s; stderr empty. This is additional observed cost; historical remaining budgets are stillnull and budget_reset=false. The fresh ledger has one entry and does not erase the earlier runs/probe.

Known pre-loss physical N/T, stock density, direct residuals,36-case covariance maxima, corrected inverse maxima and all energy-mutation aggregates agree exactly with the new JSON values. All three CSV files and the final PNG match their pre-loss SHA256 exactly. The PNG is379033bytes with SHA08479a47282e21337be1eb29e4765774c3ce3edad7c22bb8189c7182cdd6510e, so the earlier actual visual inspection is reusable by byte identity; a new visual inspection is not claimed.

Regenerated PDF SHA85404f7a827b9d32f4a4ab4eab5787822da1738e037d173557ea9fcb8359362d differs from the old172fa33daceb9abe4f62e333d502a8bd58d87adbf63e7d2a7209a43d57444118 and contains new creation metadata. Exact old PDF bytes are not recovered, and an exhaustive attribution of every byte difference is not claimed. Likewise, new VALIDATION.json is a new result file; its numeric content agrees but its old post-C9 annotation/history is retained separately in this review rather than falsely claiming exact old JSON bytes.

RECOVERY_READBACK_REVIEW.json binds current hashes, actual raw receipt, equality checks and these limitations. Final scientific/code/figure disposition remainsPASS_SCOPED, open blockers0, different-model scientific reviewNOT_RUN. No new unit-test suite, IVP or old campaign replay was requested by this reviewer. Publication and backup ACKs remain separate controller gates.


