# BASS CE1-P | Scoped physical-history research report (2026-10-29)

## Result and evidence status

This deliverable computes **actual model-generated physical time histories** under the original fixed Einstein-Vlasov continuum source. It is not a comparison with observed CMB data or a full polarization Einstein-Boltzmann model. Simulation generated using a finite interval u=0..0.08. Current top-level BASS DAG **9/15** (21 edges), CE-1 PARTIAL, production_ready=false, merge_ready=false, auto_next=false. Scoped theory/coding steps with produced output 18/20; distinct-author R6/C9 NOT_RUN.

Parent PR253 exact HEAD `e4a0feba0e8709d5e996ed8ef4c9c9bf1da4c4d0`. New PR256 `3a7a38f9615f100fddda0379bd3d6ec359ccc586` is a *separate* direct MPFR API branch, not used here. The PR255 CE1-N docs-only branch is NOT a source of code execution.

## Directly derived mathematics, normalization and assumptions

Massless collisionless, positive, reflection-even initial angular mass dW, diagonal expanding Bianchi-I, Lambda 0; signature(-,+,+,+), ell_i=ln a_i, h_i=Tstar H_i, u=t/Tstar, E=8πG Tstar² rho_energy/c² and P_i with same normalization, a_i(0)=1. The original six angular-cell energies and exact binary64 geometrical edges/shear are unchanged (identity SHA256 `022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`). The full initial energy E0=.9 and initial Hbar from Hamiltonian constraint.

For conserved covariant momenta p_i=n0_i, define r=sqrt(Σ exp(-2ell_i) p_i²), V=exp(Σell_i), E=V^-1 ∫r dW, P_i=V^-1∫exp(-2ell_i)p_i²/r dW. Then ΣP_i=E, E'=-θE-Σh_iP_i. Background satisfies ell_i'=h_i, h_i'=-θh_i+P_i, C=Σ_{i<j}h_i h_j-E and C'=-2θC; σ_i'= -θσ_i+(P_i-E/3). The pair of identities and constraint law were checked symbolically with Wolfram: (0,0,0); Wolfram check confirms algebra, not independent author validation.

GL24 and GL40 approximate same piecewise-constant six-cell continuum (not a new distribution). Frozen stored-ray channels f=1,4,8,16 use pinned BASS code and same physical cell mass. The 41 times 0..0.08 are at 0.002 steps. DOP853 integration `rtol=3e-12`, `atol=3e-14`; separate original RK4 family at 32/64/128 steps is an independent time discretization consistency check. GL40 has 9600 positive rays; nfev=47. No perturbative or fluid closure is substituted.

## Numeric results (GL40 continuum numerical reference)

At u=0.08:

| Quantity | Value |
|---|---:|
| h1 | 0.6877105036637803 |
| theta | 1.53236900410762 |
| Hbar | 0.5107896680358733 |
| E | 0.7584190590089557 |
| sigma²=Σsigma_i²/2 | 0.02429919590763715 |
| pi_1, pi_2, pi_3 | 0.00849896527168642, -0.0320779519805771, 0.0235789867088907 |
| principal photon energy ratios | 0.943925856622744, 0.96774377759763, 0.963210462479376 |
| max |C| over 41 samples | 2.55795e-13 |
| max |E-ΣP| | 3.33067e-15 |
| max analytic energy continuity defect | 2.55351e-15 |

Refinement comparison over all 41 times, max over i and u of |h_stored - h_GL40|:

| f | Number of rays | Empirical difference to GL40 |
|---:|---:|---:|
| 1 | 6 | 1.720068789845541e-05 |
| 4 | 96 | 1.077522395309671e-06 |
| 8 | 384 | 2.696307590532854e-07 |
| 16 | 1536 | 6.74239769571372e-08 |

GL24-GL40 max h difference: 7.77156e-16. This is **not a rigorous continuum quadrature error bound**. Ref8 RK4 relative to DOP853 final max h errors: n32 4.74953e-13; n64 2.88658e-14; n128 1.44329e-15. No numerically proven asymptotic theorem is claimed.

The strict original CE1-N target max|Delta h|<1e-5 has a **different exact certificate** for the original 4-panel RK4/Hermite path (PR255 ref8 9.28056365759593e-6), and is not interchangeable with differences from the new DOP853 numerical trajectory. Principal redshift ratios refer only to photon energy, not thermodynamic CMB temperature. Neither T,Q,U, a_lm nor a physical likelihood is generated.

## Verification, failure classification and figure audit

- Python executed in this current session, C++ compiler capability separately probed. `pytest tests/test_physical_histories.py -q`: 7/7 PASS. Python module compile checks recorded separately.
- Frozen Git blob test/source hashes and original binary64 SHA checked before source creation. 41-point Hamiltonian, radiation trace, positivity, photon-energy ratios, anisotropic-stress trace, energy continuity and independent analytic initial pressure all checked.
- The initial finite-difference derivative test failed due O(Δu²) truncation at Δu=.002, not physical drift. Changed to 5-point O(Δu⁴) derivative and reran the same physical acceptance test. Matplotlib mathtext label syntax fixed without modifying data.
- Four actual saved-data plots read visually: anisotropic-pressure, H_i, principal redshift, angular-refinement gap. No statistical fit or observational map output.
- Native distinct-author subagents: NOT_EXPOSED; serial execution fallback. R6/C9 distinct-author independent audit NOT_RUN. Strict code CI of the new Git head NOT_RUN unless independently observed; results from local Python cannot be substituted for GitHub CI.

## Recent cross-repo context and non-automatic imports

BASS PR256 (`3a7a38f9615f100fddda0379bd3d6ec359ccc586`) repairs MPFR nonfinite direct-program certificates in a sibling branch. REI PR269 photo rates vs Puchwein19 (no IVP); BASS_HE PR111 conditional D-pair angular response; bass_cr PR124 3201-atom prefix certificates; WU088_HH PR163 remains 34/49 HOLD; rec_bianchi PR159 HD parsed-source callgraph guard; vigilode PR116 N03 conditional certificates; htt_base PR564 report-first DAG. These are *independent, unmerged* scopes; none are imported into this frozen collisionless matter source without an explicit translation/authority gate.

## Scientific interpretation and claim gate

The anisotropic pressure remains trace-free relative to E/3, and the diagonal expansion history is sourced by the full angular distribution. Numerical histories of h_i, sigma_i, pi_i, energy and redshift have been generated and can be interrogated directly. This is scientific progress (new raw model data), not a top-level acceptance of the full production Einstein-Boltzmann pipeline. Top DAG stays **9/15**, CE1 PARTIAL.

The single best next bounded physical step is to derive and compute the **normal-frame unpolarized photon sky intensity/energy moment angular map along null geodesics** from the same six-cell dW, with a carefully identified emission/observer epoch and source measure; then compare its exact harmonic projection against the kinetic stress moments. This requires specifying which operational observable is available from the six-cell source and does not permit calling it a Planck CMB temperature map without spectral assumptions. Retain the production gate and do not merge sibling PRs.

## Literature and source identifiers

Heinzle & Uggla (2006), DOI 10.1088/0264-9381/23/10/016; Lee, Nungesser & Tod (2020), DOI 10.1007/s10714-020-02699-7, arXiv:1911.04937. These support the kinetic-equation setting; the specific finite-input numerical rows and local code are new in this run, not literature results.