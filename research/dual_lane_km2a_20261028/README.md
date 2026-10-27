# KM-2A: finite-beta polarized Thomson generator in normal time

Status: COMPLETE_SCOPED_INSTANTANEOUS_TILTED_NORMAL_TIME. Upper KM-2 remains PARTIAL, research count6/15 includes source mapping and scoped units only. No production code, owner branch, merge, finite-time solver or previous campaign rerun.

## Definition

Signature(-,+,+,+), photon propagation n, beta=v_e/c fixed and subluminal, nu0=n_e_star*sigma_T*c in normal proper-time units. Proper density is not preboosted. D=gamma(1-beta.n). P8 real S+A represents physical Hermitian S+iA.

J_e=D^4 S J_n S^T; dOmega_e=D^-2 dOmega_n; M_e=int D^2 S J_n S^T dOmega_n.

L_n J=nu0 D [D^-4 S^T ((3/8pi) P_e M_e P_e) S - J]. Exactly one ray factor D, distinct from D^4 and D^-2. Raw quadrature weights are neither normalized nor projected. Vacuum rate is exact zero.

Covariant radiation force F^a=cQ^a=nu0(delta^a_b+U^a U_b)T^{bc}U_c, U=u_e/c. Elastic invariant U_aF^a=0 means rho_dot=beta.q_dot. For fixed-beta homogeneous normal-slice collision-only evolution gamma(rho-beta.q), not U_aT^{ab}U_b, is invariant. Moving prescribed matter can exchange normal-frame energy; no matter feedback has been wired.

## Evidence

13 unique pytest items passed. Science:15 boost rows,15 mixed-force rows,5 independent pairwise-Jones checks,8 normal-grid equilibrium and8 isotropic-force rows,18 scalar spectral ray calls. New IVPs0, old-campaign reruns0. Fixed gates algebra2e-11/force5e-10/spectral2e-10. Max pairwise/force/elastic/spectral normalized residuals1.364e-15/6.775e-15/9.374e-16/4.215e-15.

The O(N^2) reference uses independent 4-vector boosts/gauge restoration and Jones overlaps, not the new source factorization. Existing collision_moving.py already contains one D; its spectral integral agrees with the new initially-unpolarized bolometric trace. It is not a polarized finite-time oracle.

Boosted equilibrium alone cannot detect D omission or duplication. Non-equilibrium force does: a beta=.6x mixed fixture gives missing/duplicate invariant defects-.19156676/+.16480853. Uniform normal grids at beta=.85 require angular refinement: equilibrium error8/16/32/64 =.0052915/3.3696e-6/1.95e-13/3.61e-15; analytic force error=.03914/5.0045e-5/5.84e-12/6.86e-15. Do not equate same-grid agreement with continuum accuracy.

Electron initial I30=.1 is gain-null but normal-time D weighting yields nonzero M_e_dot diagonal(.0182571869451,.0182571869451,-.0171832347719). Exact Wolfram integrals agree. Gain rank9 is not a finite-state closure: multiplication D and gain do not commute. Preserve the complete initial carrier in future memory equations.

## Provenance and repair

P8, polarized_dictionary and collision_moving byte identities are pinned in SOURCE_MAP.json. The archive collision_oracle whole file is historical; the three executed grid/phase helper ASTs match live reads. Legacy _boost_screen_map AST also matches current source, but whole production polstate was not run. At beta0 old helper extends as I3 while the new one uses P; comparisons must be restricted to physical screens. The initial whole3x3 diagnostic mismatch is retained in the full archive. Only15 boost diagnostics were recomputed, with unchanged physics/tolerances; no full science rerun.

PolQState scalar-x rest-semigroup sandwich is read, not executed as production, and cannot be called a generic normal-time update without the ray-rate owner. This scoped adapter does not silently replace it. Cold Thomson energy-domain verification remains open.

## Reproduce

From this directory:

    python -m pytest tests/test_tilted.py -q

All13 tests are executable with the selected Git code/vendor. Full campaign and saved-evidence validators are in the complete immutable ZIP:

    python verify_km2a.py
    python verify_saved.py

Do not rerun science merely for delivery. Git publishes the tested core, reference, spectral check, tests, necessary vendor and concise results/contracts/DAG. The full ZIP additionally holds the report, all raw rows, symbolic inputs/results, failure logs, source snapshots, plots and manifest. DELIVERY.json identifies it. The original user DV2F4e4349ad archive was independently preserved before science; parallel remote dbfab149 is not overwritten or silently substituted.

Next KM-2B: fixed-beta frozen normal-time finite-time solver retaining initial source-null radiation. No production/Rust, matter/Einstein feedback, generic evolving beta, spectral recoil, spatial averaging or independent-model review is admitted here.
