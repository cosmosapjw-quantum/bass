# REI current source intake for the Sigma–Pi pilot
Observed through 2026-10-21 05:22 UTC (14:22 KST). Read-only GitHub intake and local source materialization; no native science, ODE, benchmark, commit or push was run by this subtask.

## Coverage
- GitHub branch collection: 253 entries, pages 100+100+53; terminal short page reached.
- GitHub all-state pull requests, sorted updated descending: 211 entries, pages 100+100+11; terminal short page reached.
- Relevant recursive trees were untruncated: PR198 10,368 entries; PR212 5,063; PR141 8,600. Latest PR210 tree also read.
- This is complete enumeration of the visible branch and PR collections, followed by selected source/result inspection. It is not every file in all 253 branches, every historical commit, or account-wide conversation coverage.
- Exact branch and compact PR metadata: REI_CURRENT_INVENTORY.json.
- Shell git ls-remote failed in this turn with browser-proxy connection failure. Authenticated GitHub connector succeeded; this did not block source reads.

## Current identities
| Lane | PR | Observed head |
|---|---:|---|
| Main | — | ae3402713c4b6530ab2b27f008f5f5d5c6a999ed |
| LRS V14 | 198 | 3360a345f8e0f2f9d2b6bdd42d21e584446ec9b8 |
| Age-exposure | 199 | 964b2e3c098f6e475999a4eddc7a6aa0f8f053cc |
| Cross-repo orchestration | 212 | a23c65ab261a0ad54e410944acdf471d21274a57 |
| BRPERF01 | 210 | e4c8133288614638792888367ca10b2ded3138ff |
| RUN19 | 211 | c9deb933761a8d2593d1176aee028cd423bdbc05 |
| BR06 | 208 | 54948439be7039c9b2b1f9580bee69bebeb80129 |
| C15 actual coupled Sigma–stress | 141 | 80825585f9fe31d2ee0d5af545ada3fa1f52be72 |

Default main is not a substitute for these published research sources. Different lanes are not mutually merged merely because they share a repository.

## Shortest runnable physical pilot source
Use original C15 at PR141. Exact minimal source/readout closure is materialized under c15_source/ with original repository paths. SOURCE_FETCH_MANIFEST.json contains 25 files, total 1,315,759 bytes, all source Git blob hashes matched. The closure includes two existing scientific result files and its readme/gate; thus the runnable code alone is smaller.

Current-turn import and initial-state construction passed with Python/NumPy/SciPy. There was no new ODE run. Runtime Rust compilation is unnecessary: original source-owned MD14 spectral cells and Grackle Case-A rates are already in CSV files and checked by original code.

Entry point:
- research/rei_c15_sigma_pi_feedback_20261015/coupled.py
- Parameters(Sigma_initial, orientation, gamma_quadrupole, nu_quadrupole, massive_fraction, massive_quadrupole, massive_mass_over_T=30, L=8, ...)
- EinsteinBoltzmann(parameters).run(nsteps=64)
- Source quadrature defaults 8X8; original massive finite quadrature 96x32.
- All signed quadrupole amplitudes alpha are in [-1,2] and represent positive seeds 1+alpha P2. Gamma and neutrino initial J0=1, J2=alpha/5.
- Existing initial state is fixed warm gas at a=0.1999, Tgas=12000 K, xHII=.4, xHeII=.5. End a=.2. Source/rate domain and this initial condition must not be silently extrapolated to cold z=20.

C15 evolves b,s and photon/neutrino multipoles with gas/UV state, finite-mass collisionless matter, and Einstein shear sourcing. It has full microscopic donor/emitter-reservoir and photon-energy closure limitations explicitly preserved in original source. It is a conditional near-z4 exploratory coupling calculation, not cold-to-late EoR validation.

## Norm and stress meanings
Original C15 uses sigma^i_j=diag(-s,-s,2s) and Sigma_half=sqrt(3)|s|/H, with orientation stored separately. Frobenius Sigma_F=sqrt(2) Sigma_half.
Original internal stress name Pi means signed DeltaP=P_parallel-P_perp, in Pa=J/m^3:
pi^i_j=diag(-DeltaP/3,-DeltaP/3,2DeltaP/3).
The physical magnitude is |pi|_half=|DeltaP|/sqrt(3); Frobenius |pi|_F=sqrt(2/3)|DeltaP|.

C15 KAPPA=8*pi*G/(3*c^2) is the shear coefficient when its source is DeltaP. It is one third of K_time=8*pi*G/c^2. Use Pi_half=K_time*|DeltaP|/(sqrt(3)*H^2); Pi_F=sqrt(2)*Pi_half. With geometric Einstein kappa=8*pi*G/c^4 and H in inverse seconds, the numerator needs kappa*c^2.

For equal primordial radiation seed alpha and no massive stress, signed DeltaP0=(rho_gamma0+rho_nu0)*alpha/5. Inverting a requested Pi_half therefore includes factor 5:
alpha=epsilon_pi * 5*sqrt(3)*H0^2*Pi_half/[K_time*(rho_gamma0+rho_nu0)].
Check alpha within [-1,2] and preserve separate shear/stress signs. H0 depends on chosen Sigma through the Hamiltonian; compute it from the original initial-state construction.

The nonphysical control GRAVITY_PI_DISABLED_CONTROL has Pi_total_source=0 by a source switch despite nonzero component tensor stresses. For plotted physical Pi, sum the component Pi_gamma+Pi_nu+Pi_massive+Pi_UV; distinguish this from the RHS-selected source. Do not plot its switched-off value as vanishing physical anisotropic stress.

## Existing exact raw reusable now
C15_STUDY_RESULTS.json contains series: eight actual cases, 64 rows each (512 rows), including H, s_inv_s, Sigma, orientation, individual Pi, Tgas, ion fractions, photon number, and per-step ledgers.
SIGMA_PI_HHE_COUPLED_HISTORY.csv is a compact export but lacks H. Use JSON to normalize Pi without reconstructing H approximately.

Files:
c15_source/research/rei_c15_sigma_pi_feedback_20261015/C15_STUDY_RESULTS.json
c15_source/research/rei_c15_sigma_pi_feedback_20261015/SIGMA_PI_HHE_COUPLED_HISTORY.csv

The source exact CSV blob is 0ae179e1eaaa69a208e9a78fd80317c34621d79e and JSON blob 5f1ac55a2aabb73897fc8d0c2674032237d75ad0.
The earlier scratch c15csv.csv convenience copy has an extra terminal newline; use the original-tree copy above for exact provenance.

## Newer lanes and direct relevance
### PR198 current NCP backlog
The report under v14/vigilode_radau_20261019/parallel_campaign_20261020/ncp_backlog_20261021/ records source d234243a79e4e8e611aaf4ac61949c5ef9111468. 144/246 jobs complete; 100 V12 native cap-not-run and two dependent jobs blocked. Native started jobs 131/131 succeeded: V12 44/144, V13 84/84, SSPRK three commands. Historical supervisor debit 200.398972 s versus 180 s cap is preserved. V13 and SSPRK data are finite-scope evidence; signed Bianchi and full EoR remain HOLD.
Latest SSH contract uses user-provided ssh -i /home/cosmosapjw/.ssh/ncp_key root@49.50.142.2 -p 22, but this metadata update observed neither key availability nor connection. Do not infer current host state from that artifact.

### PR199
Latest current README/HANDOFF say native BE time8/time16/time32 all executed and returned. All 12 scalar adjacent endpoint differences decreased, but the existing 0.005 target fails for both adjacent pairs. Positive DOP853 age32 is a different operator, not a time-refinement level. Completed cases should be reused; this lane is not a completed cold signed-Bianchi Sigma–Pi sweep.

### PR210
BRPERF01 has actual bounded completed optimization: 15 positive rate coefficients on 1..10^6 K compact tables; prepared native rates shared across H/He/D; immutable prepared frozen-opacity and birth-ray contexts; persistent independent worker fixtures and ordered reduction. It retains source labels, original thresholds, summation order and physical owners. This code is valid in its original frozen-gas BR06 contract. Importing its tables directly into C15 would change its source/rate owner and require targeted numerical validation; it is unnecessary for today's short pilot. Reuse its architectural patterns—cache invariant data, independent case workers, ordered output—and retain original C15 coefficients.

## Source links
https://github.com/cosmosapjw-quantum/rei_bianchi/pull/141
https://github.com/cosmosapjw-quantum/rei_bianchi/blob/80825585f9fe31d2ee0d5af545ada3fa1f52be72/research/rei_c15_sigma_pi_feedback_20261015/README_KO.md
https://github.com/cosmosapjw-quantum/rei_bianchi/pull/198
https://github.com/cosmosapjw-quantum/rei_bianchi/pull/199
https://github.com/cosmosapjw-quantum/rei_bianchi/pull/210
https://github.com/cosmosapjw-quantum/rei_bianchi/pull/211
https://github.com/cosmosapjw-quantum/rei_bianchi/pull/212
