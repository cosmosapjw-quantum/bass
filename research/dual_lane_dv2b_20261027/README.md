# DV2-B: frozen Bianchi-II polarized finite-time benchmark

Status: COMPLETE_SCOPED_FROZEN_BIANCHI_II_FINITE_TIME. Parent PR199, commit
2c0ea7dfbf4fdcb6b2e6542f0d8d4bcf4214028b. Upper DV2 remains PARTIAL; 6/15
scoped/source-mapped upper nodes, not global physical completion. No production
edits, merge, historical campaign rerun, or whole-current-Rust validation.

## Construction

Physical signature(-,+,+,+), propagation direction n, normal proper time t.
Code uses u=t/T_star, curvature k=c*n_structure*T_star, nu=n_e*sigma_T*c*T_star.
H=sigma=0, N=k a a^T constant. Frozen ultrastatic geometry is prescribed, not an
Einstein solution for the evolved radiation. Cold Thomson is a declared regime,
not a spectral validity certificate.

Exact direction/screen provider:

    n(t)=R_a(k*(a.n0)*t)n0
    E(t)=R_a(k*(a.n0)*t) R_n0(-k*t/2) E0
    dOmega_t=dOmega0; energy ratio=1

No Bianchi-I p=Aq matrix is used. The inherited KM3 source-memory/Volterra code
receives the explicit curved geometry protocol mu=1,v=w. Intrinsic screen
rotation and the full initial gain-null carrier are retained.
Canonical z-axis free solution:

    f_s(t,theta,phi)=exp(-i*s*k*t/2)f_si(theta,phi-k*cos(theta)*t).

Three independent kinetic paths are used: pinned P8 Cartesian RHS, analytic
curvature harmonic Galerkin IVP with explicit L cutoff, and independently solved
Volterra source. They share prescribed geometry/IC conventions, not source
histories. The exact direction/screen formula is checked against P8 geometry ODEs.

Canonical m=0,l=2 has an exact three-channel closure for (I20,E20,B20):

    B=[[-.9nu,-sqrt(6)nu/10,0],[-sqrt(6)nu/10,-.4nu,k],[0,-k,-nu]].

For constant nu, exp(tB) is the all-time oracle. Sym(B) eigenvalues are
{-nu,-nu,-.3nu}; curvature is antisymmetric. This is not a general finite-L
closure. The constant geometry/rate source kernel is lag-only in the continuum;
the identical-lag numerical discrepancy is9.99e-16. No FFT/speedup is claimed.

## Evidence

10 unique pytest items. New campaign:9 harmonic IVPs,8 direct IVPs,3 geometric
reference IVPs,6 Volterra solves,9 exact-geometry provider objects; test calls are
separate. No scientific reruns. Parent vendor bytes pinned by SOURCE_MAP.json.
Main interval0..0.8,k=.9,nu=1.4; mixed positive I/E/B/V initial state through l4.

At endpoint L4/6/8 source errors:1.3463e-4/1.6872e-8/3.2863e-13; full carrier
errors:8.2192e-3/7.3620e-4/1.9557e-5. Source precision does not certify the sky.
Volterra16/32/64-panel source errors:1.5331e-10/9.5763e-12/6.0574e-13.
Direct angular8->12 /12->20 source gaps5.6520e-11/4.4409e-14. ODE tolerance
sensitivity and off-grid source interpolation are separately recorded.

Initial B20=.1 is source-null but Mzz(.8)=.04241506349520012 exactly in the m0
oracle. H/direct/Volterra differ by3.96e-15/2.53e-15/8.01e-13. Positive paired
state minimum screen eigenvalue .9809891947. Deleting initial gain-null state
loses source norm .05194763149; omitting intrinsic screen twist loses free-carrier
amplitude .01253818251. Wolfram independently checks the block/Jacobian algebra,
not an independent-model review. native_subagent and fresh_model_review NOT_RUN.

## Reproduce / packaging

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m pytest tests -q

The full immutable archive additionally contains verify_dv2b.py, all raw results,
Korean theory report and handoff, full detailed DAG, CAS/logs/figures/hashes. From
the full archive run python verify_dv2b.py for the new campaign or verify_saved.py
for hash/result inspection only. Git publishes the tested core/tests/vendor plus
concise report/contract/results/DAG and delivery receipt. Do not describe selected
Git files as the full archive. No old campaigns need rerunning for publication.

## Next / limits

DV2-C: time-dependent coframe-compatible Bianchi-II provider. Specify positive
scale factors first: Nzz=Nzz0*(az/az0)/[(ax/ax0)(ay/ay0)] so
Nzz_dot=(-H+2sigma_zz)Nzz. Do not choose arbitrary H,sigma,N independently.
This compatibility is not Einstein backreaction. Class B, generic tilt,
spectral redistribution/recoil, production Rust, spatial averaging and observer
sky remain open. Preserve raw weights, initial carrier and output-specific error
budgets. production_ready=false; overall_physical_completion=null.
