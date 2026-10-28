# BF3-A: periodic polarized transport on prescribed Bianchi I

Status: COMPLETE_SCOPED_PERIODIC_SPATIAL_TRANSPORT_SLICE. Parent BF2 PR214/10bba48833a3a3ea20b7596b61c90a67003126e5. Additive research code only, not production Q/Rust. Upper BF3 remains PARTIAL and count remains8/15.

One periodic spatial coordinate x in [0,2pi), diagonal prescribed Bianchi-I scale factors, full bolometric IQUV, geodesic/nonrotating normal tetrad, untilted cold Thomson. u=t/T_star; cbar=c*T_star/L_star is explicit. Spatially varying radiation and opacity do not imply a spatially inhomogeneous metric or EFE feedback.

PhysicalHistory integrates the Fourier-Galerkin PDE with pinned P8 tensor transport. CharacteristicHistory uses direction-dependent exact finite-Fourier shifts and2x2 screen pullback with RK4, without calling the physical-carrier/direct RHS. Geometry and local collision definition are shared; no independent-model claim. Analytic finite-mode opacity multiplication uses non-wrapping convolution, not aliasing nodewise multiplication.

Mean streaming is zero, but streaming changes opacity/radiation correlations and the mean collision source. The actual mean differs from a mean-opacity homogeneous solve by.008403637851993828 at u=.4. Removing streaming changes the mean source by.0002528544283064704. Initial background I40=.1 is retained. No log/shape averaging, clipping, weight normalization or density renormalization.

13 unique pytest items passed. A single scientific campaign used9geometry/9displacement/10physical-PDE IVPs,4characteristic RK4 histories,1homogeneous control and1reaction-only control; tests separate, old campaigns0.64-step source/carrier endpoint discrepancies4.3263e-12/2.3672e-11. Spatial Nx17->25 source gap1.3692e-8, angular ntheta8->16 gap2.2672e-9; same-grid parity is not continuum accuracy. Exact free-shift/dilution max error1.5792e-11. Local energy residual after subtracting raw collision defect9.7483e-13. Mean work integral residual1.4587e-13.

One input-boundary defect was detected by a failing regression: nontransverse initial carriers had not been rejected. Added a strict initial-only screen check; valid-fixture dynamics/tolerances unchanged; no science replay. No native subagent or independent-model review; symbolic CAS checks are separate.

Run from this directory (NumPy, SciPy, SymPy, pytest):

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m pytest tests/test_spatial_transport.py -q

The immutable complete ZIP includes verify_bf3a.py, verify_saved.py, full Korean derivation/handoff, exact detailed DAG/contract, raw rows, CAS, logs, plots and hashes. Run full science commands from that ZIP, not from a selected Git publication that omits the verifier. Full reruns are unnecessary merely to preserve evidence.

Next BF3-B: independent spatially nonlocal source-memory solution retaining characteristic spatial shifts and path-dependent optical depth. No automatic next node or merge. No EFE/material feedback, generic tilted spatial solver, full-frequency validity, observer-sky claim, or global positivity/tail certificate.
