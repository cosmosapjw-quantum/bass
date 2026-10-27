# DV2-C: coframe-compatible expanding Bianchi-II transport

Status: COMPLETE_SCOPED_COFRAME_COMPATIBLE_EXPANDING_BIANCHI_II_PROVIDER.
Parent: d7844b16a19e838af620372c34c4cedcfadb68b5 / PR201. This additive research unit does not edit production code, the owner/main branch, old evidence, or tolerances.

## Construction

Select positive diagonal scale factors first. In physical coordinates:

    ds^2=-c^2 dt^2+ax^2 dx^2+ay^2 dy^2+az^2(dz-n0*x*dy)^2.
    Hi=dot(ai)/ai, H=mean(Hi), sigma=diag(Hi-H).
    N=c*n_structure, Nzz=c*n0*az/(ax*ay).
    dot(Nzz)=(-H+2sigma_zz)*Nzz.

The code uses u=t/T_star and coordinates/(c*T_star), so rates are multiplied by T_star. The primary interval is0..0.4; log(ai)=hi*u+di*u^2/2, h=(.12,.45,.28), d=(.16,-.12,.08), k0=.9. Normal untilted cold-Thomson opacity is1.1+.2cos(2u). No Einstein consistency is inferred from coframe consistency.

For s=n.sigma.n, vS=-sigma.n+s*n and OmegaN=N.n-tr(N)n/2:

    dot(n)=vS+(N.n) cross n
    dot(log r)=-(H+s)
    dot(E)=(vS*n^T-n*vS^T+[OmegaN]_cross)*E
    dot(log Jac)=3s
    Jac*r^3*volume/volume_initial=1.

E is a transported3x2 screen, not an E-mode coefficient. This class-A measure identity does not assume a linear Bianchi-I momentum map. It must not be copied into classB without derivation. Unchanged SourceMemory and VolterraHistory receive mu=r,w=w0*Jac,v=w*r^4. Full initial gain-null radiation is retained.

## New checks

Independent canonical Hamiltonian coordinate rays and an independent tangent-map area calculation verify direction/redshift/Jac. Frozen, conformal-ultrastatic and N=0 Bianchi-I limits are checked. Direct Cartesian radiation invokes pinned P8; harmonic evolution combines pinned analytic shear and curvature matrices; Volterra solves unknown source without direct callbacks. All three share prescribed fields/conventions, not source histories.

9 unique pytest items. The one new scientific campaign ran8 geometry-provider IVPs,1 coordinate IVP,1 tangent-map IVP,6 direct IVPs,3 harmonic IVPs,4 Volterra solves. Tests are separate; no ancestor campaign reruns. External CAS returned five exact zero residuals. Native subagent and independent-model review NOT_RUN.

Max coordinate direction/redshift errors1.16e-13/6.01e-14; tangent-area1.04e-12; P8 screen-rate6.12e-14; volume-area-redshift identity8.88e-16. At16/32/64 time panels on12x24 angular nodes, Volterra source differences1.6991e-9/1.0619e-10/6.6338e-12. At L4/6/8, harmonic source errors2.4405e-6/3.7803e-9/6.7768e-12 but carrier errors2.6064e-3/3.2728e-4/3.8599e-5. Source convergence is not full-field convergence. Raw angular gaps, energy-work balance and off-grid source-interpolant errors are separate.

Initial signed B20=.1 is source-null yet returns Mzz(.4)=.019646797457580512; independent Volterra=.01964679745790246. This additional signed-tail run is not a new positive paired-state finite-time experiment. Dropping Jac or intrinsic screen transport is detected. Removing opacity factors still leaves an equal-lag kernel difference.00334426 in this clock/representation; no universal no-convolution theorem is claimed.

## Reproduce and preserve

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m pytest tests/test_expanding.py -q

The complete immutable archive also includes verify_dv2c.py, raw evidence, REPORT_KO.md, OPERATOR_CONTRACT.json, detailed DAG, CAS, logs, figure and handoff. Run the validator only for authorized reproduction, not to re-publish saved evidence. verify_saved.py verifies saved hashes/DAG/results without scientific reruns. The Git selection and full archive are distinguished in DELIVERY.json.

Source references and exact vendor hashes are in SOURCE_MAP.json. Executed core/tests and publication readbacks are compared by Git blob identity. The final external receipt owns final commit/PR/archive/backup identities; they are not retroactively inserted into an already uploaded archive.

## Boundaries and next

Upper research count6/15 remains unchanged; DV2-C is a scoped subgate, DV2 overall PARTIAL. production_ready=false, overall_physical_completion=null. No EFEfeedback, generic rotating/offdiagonal coframes, classB, tilted normal-clock wiring, spectral recoil, global tail bound, productionRust or observer-sky claim. Positivity only checked on the recorded mixed fixtures.

Next DV2-D: class-B Bianchi-V instantaneous generator and angular/energy-flux measure. Derive A_struct contributions instead of copying the class-A Jac*r^3*volume identity. No merge requested.
