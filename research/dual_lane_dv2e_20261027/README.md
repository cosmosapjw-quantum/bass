# DV2-E: frozen Bianchi-V polarized finite-time benchmark

COMPLETE_SCOPED_FROZEN_BIANCHI_V_FINITE_TIME. Additive research only; no production code or merge.

Physical scope: H=sigma=N=0, constant normal-time A=c*a_structure, massless bolometric radiation, untilted cold Thomson, signature(-,+,+,+), photon propagation direction. All rates multiply T_star for u=t/T_star. The angular Mobius map has energy ratio1, not a boost Doppler factor. Raw angular weights change by Jac=(cosh(|A|t)-mu0 sinh(|A|t))^-2.

The exact normalized tangent map transports screens. Independent coordinate Hamiltonian/P8 geometry checks and an exact free dipole density/flux solution validate the supplier. Existing SourceMemory and VolterraHistory are unchanged. Harmonic evolution uses the attached original DV2D analytic operator, source byte identity recorded below; no direct/Volterra source callback or grid fitting.

Exact local free dipole result for I_i=Ib+eps*mu_i, x=a*t:

    rho=4pi*Ib+4pi*eps*(coth(x)-x*csch(x)^2)
    qz=4pi*eps*csch(x)^2*(x*coth(x)-1)
    rho_dot=2*a*qz

Energy per photon remains one. Nonzero local density change is balanced by spatial flux divergence; do not renormalize it away.

## Source authority

Remote parent02a88bf2f6ca93f38e0e173d663657f6ef7ecad0 already contains a parallel DV2D variant named class_b_streaming.py. The attached original8a0dbb46 ZIP instead contains classb_streaming.py, blob7645b202ac57dd6b9f241895841c0e00427e0659. This exact original is vendored here; the remote variant is not claimed byte-identical or silently overwritten. Original33-file archive separately preserved before new computation; see DV2D_PRESERVATION.json.

## Verification

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m pytest tests/test_frozen_v.py -q
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python verify_dv2e.py
    python verify_saved.py

11unique pytest items pass. The full validator is in the complete immutable ZIP; selected Git publication may omit raw evidence/full prose. verify_saved verifies the full archive payload without science reruns; it requires the complete ZIP including SHA256SUMS and raw results. EXECUTION_LEDGER.json owns historical run counts; a new validator invocation records only itself. Main A=(0,0,.7),nu=1.3,u0..0.5; L4/6/8. Source endpoint differences3.2510e-4/2.8299e-7/1.0805e-10, carrier1.0509e-2/1.7055e-3/1.6286e-4. Source accuracy does not certify full-field accuracy. Volterra16/32/64 panels source6.2537e-11/3.9027e-12/2.3981e-13. Full initial source-null B22=.1 returns Mxy(.5)=.016929083328088252; harmonic/direct and Volterra/direct agree to4.71e-15/9.15e-15. Raw angular, time, off-grid and positivity diagnostics remain distinct.

Output failure is retained: first completed scientific run failed JSON serialization on numpy.bool_. Only serialization was changed; one full current-campaign rerun was necessary. Total science debit16direct,12harmonic,10Volterra,4P8geometry,2coordinate,14analytic providers; test calls separate, old-campaign reruns0. Native subagent/fresh-model review NOT_RUN; CAS is symbolic only.

Full evidence archive contains raw rows, predeclared gates, all code, detailed Korean report/contract/DAG, CAS, failure/repair logs, figures, handoff and hashes. Current source-limited bench is not production/Rust/Einstein/tilted/frequency/general-tail or positivity certification. Upper progress6/15 remains; DV2-E is a subgate, upperDV2 PARTIAL. Next DV2-F is coframe-compatible expanding Bianchi V, not automatically executed.
