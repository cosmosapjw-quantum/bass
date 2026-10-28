# BF3-C: periodic static-lapse collisionless photon transport

Status: COMPLETE_SCOPED_STATIC_PERIODIC_LAPSE_CHARACTERISTICS. Additive research only, exact parent PR218 commit24db3ea928c476e6cbaa94553307cde773a65832. No production/owner changes, merge, or historical radiation-campaign replay. Upper BF3 PARTIAL and scoped/source-mapped count8/15, not global physics completeness.

Metric (-+++): ds²=-N(x)² c²dt²+L_star²d{x}², N=exp(epsilon cos x)>0. u=t/T_star, cbar=c T_star/L_star. Finite epsilon, no amplitude expansion. Normal proper time is Ndt and the static observer acceleration is c² grad(log N)/L_star. This is a genuinely curved prescribed spacetime, not an Einstein solution.

## Construction and exact checks

TetradHistory evolves x'=cbar N n, n'=-cbar(grad N-n(n.grad N)), log r'=-cbar n.grad N and physical screens. J=r^4 E X_initial E^T preserves the full IQUV carrier. Independent canonical Hamiltonian H_u=cbar N|p| supplies 6D tangents; an independent Christoffel geodesic/4-vector parallel transport supplies a normal-screen gauge comparison. No old P8 geodesic-normal RHS is misused for acceleration.

Killing energy N E_local and transverse covariant momenta are conserved. A radial exact travel-time quadrature and a nonradial turning point N=E_K/p_perp are separate oracles. Screen normalization/projection and density/weight renormalization are not applied.

The coupled x-direction measure obeys J_xOmega*r^3=1. The x/mu tangent determinant includes cross blocks; angular Jacobian alone and products of diagonal blocks are generally wrong. Canonical full6D det1/symplecticity and the independent reduced measure are checked. This global Lagrangian identity is not a local final-position angular quadrature rule.

Static occupation f(N E_local) is invariant; bolometric isotropic I_eq proportional to N^-4 is stationary. Coordinate-time local energy balance is dt(N rho)+(c/L_star)div(N²q)=0, q=energy flux/c. Hence the periodic conserved global energy is integral N rho dV, not integral rho dV.

## Executed evidence

13 unique pytest items passed. Tests-first missing-module RED and first GREEN retained. One numerical campaign:9 tetrad,7 canonical Hamilton,4 coordinate-parallel and5 reduced-measure IVPs. Tests separate, old campaigns0, full science replay0. Native subagent and independent model review NOT_RUN. External Wolfram checked seven zero identities plus explicit reduced divergence and curvature.

Four epsilon fixtures0,.35,.55,-.8,24 rays,9 output times. Main maximal position/screen/Killing-relative errors3.00e-12/4.84e-12/1.17e-12. Coupled phase-measure residual1.99e-12, canonical symplectic defect1.87e-12. Global Killing energy and normalized number relative drifts5.55e-15/2.89e-15 using independently integrated tangent determinants. Misusing angular-only measure gives endpoint energy defect.3739508; omitting the measure gives1.2177896. These are finite-quadrature identity tests, not continuum Eulerian convergence claims.

Turning point epsilon.55,x0=pi/2,nx0=-.6,pperp=.8 occurs at u1.1403908621,x1.15303475646, matching the analytic threshold to3.75e-14. Initial screen freezing produces leakage.61029. Adaptive-tolerance refinement, reversibility, periodic lift, input errors and carrier PSD for physical fixtures are also checked. No universal positivity/tail/long-time guarantee.

## Reproduce

    OPENBLAS_NUM_THREADS=1 python -m pytest tests/test_lapse.py -q
    python verify_saved.py

Full scientific campaign (a new counted execution):

    OPENBLAS_NUM_THREADS=1 python verify_bf3c.py

Git publication contains the two executed core files, the complete13-test file, the unchanged carrier-encoding vendor, README and concise metadata. The immutable ZIP additionally contains full validator, saved-data validator, all raw results, detailed report/contracts/DAG/handoff, CAS input/output, test/science logs, plots and hashes. Do not claim the selected Git subtree is the complete archive. Use the ZIP for archive-only commands.

Next BF3-D: field reconstruction and bounded static-lapse spatial-angular transport with eventwise normal collision clock N(x)nu_star, exact stationary I~N^-4 and Killing-energy balance. Do not auto-execute, add generic tilt or promote to Einstein feedback. Current provider alone is not the full BF3 inhomogeneous-metric PDE solver.
