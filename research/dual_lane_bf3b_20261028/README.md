# BF3-B: independent retarded spatial source-memory

Status: COMPLETE_SCOPED_RETARDED_SPATIAL_SOURCE_MEMORY. Parent BF3-A PR216 at `201231f0918727ae4de6b27bf85c91bdc34ef8fd`. This additive research directory does not modify production or previous campaign results. Upper BF3 remains PARTIAL; scoped/source-mapped count8/15 is not global physics completeness.

## Scope and construction

One periodic dimensionless coordinate x in [0,2pi), prescribed homogeneous diagonal Bianchi I, nonrotating geodesic normal tetrad, full bolometric IQUV, untilted cold Thomson opacity nu=n_e* sigma_T c. Time u=t/T_star, explicit cbar=c*T_star/L_star. No shear/radiation/opacity amplitude expansion; prescribed geometry and bath still give a linear radiation problem. No EFE/material feedback, spectral validity or production admission.

The unknown source is M(t,x)=int J dOmega. A fixed Fourier cutoff retains exact truncated opacity convolution V_kk'=nu_(k-k') without circular aliasing. The known streaming/loss matrix A_q=-i k v_q - V defines a fundamental matrix Phi_q and U_q(t,s)=Phi_q(t)Phi_q(s)^-1. Its construction never uses radiation initial data or a radiation RHS. The source kernel retains U_q V, both screens, angular weights and redshift factors. M=b+int K M is independently marched by quadratic product integration and GL4 kernel quadrature, solving an18*Nx complex source system per panel. Main dimension306. Full initial angular/spatial carrier and accumulated screen history remain; no9-state Markov closure or speed/memory advantage is claimed.

A crucial discretization distinction is preserved: P_K exp(-path optical depth)P_K is NOT the same finite-cutoff propagator as exp(-t P_K nu P_K). For nu=nu0(1+eps cos x),f=cos2x,K2, their difference begins at nu0^2 eps^2 t^2 cos2x/8. Exact continuum path attenuation is checked separately and converges to the Galerkin result as spatial resolution increases; it is not silently substituted at fixed cutoff.

## Verified evidence

13 unique pytest items passed. One main science campaign plus a bounded kernel-only audit; no historical replay. Main geometry/displacement/loss/direct/characteristic/Volterra calls13/13/14/3/1/14, supplemental1/1/1/0/0/0, actual14/14/15/3/1/14. Tests count separately. Native subagent and independent model review NOT_RUN; external Wolfram exact checks are separate.

On the same Nx17/angular8x16 grid, at u=.4,8/16/32/64 panels give source errors8.88596e-8/5.55332e-9/3.46964e-10/2.15721e-11 and carrier1.49387e-8/9.35648e-10/6.04732e-11/5.87519e-12. First orders4.00011,4.00049. Third characteristic path matches the direct carrier to2.36717e-11. Fine off-grid reconstructed source9.49179e-11 is distinct from interpolant4.00090e-8. GL4->6 and uncompressed full history differ by2.66e-15 and3.55e-15. Loss-only conditioning is sampled, not globally certified; main max1.96445.

Spatial gaps Nx9/13/17 versus25 are1.84440e-4/1.98440e-6/1.35866e-8. Angular gaps6/8/12 versus16 polar nodes are1.24277e-6/2.26720e-9/1.42109e-14. Same-grid parity is not continuum accuracy. No retained or unresolved spatial/angular tail is declared zero.

A uniform-opacity kernel has a real-space off-diagonal block0.0152329 for t=.2,s=.05 and roundoff6.40e-16 at t=s. This checks actual spatial nonlocality, not only Fourier-mode coupling. Finite Fourier support is global; no compact numerical domain-of-dependence theorem is claimed.

Initial I40=.1cos x has source1.84e-16 but produces Mzz(x0,.4)=-.000178278452875903 direct and-.000178278452882568 memory. This is a signed response, not an extra integrated positive pair. Main positive-carrier samples were checked separately. Mean streaming is zero, yet suppressing spatial dynamics changes mean source by.00025285427. Actual mean energy-history balance, including geometric work and raw collision quadrature defect, has residual1.10e-12.

The first I40 test used GL4, whose polar nodes are P4 zeros. It tested an almost-zero initial state. Only this test moved to GL6 and acquired a nonzero-input guard; no algorithm or tolerance changed. RED and failed/repair logs are retained. Initial runtime/service failures occurred before command execution; current Python/container execution succeeded.

## Reproduce and evidence locations

From this directory:

    OPENBLAS_NUM_THREADS=1 python -m pytest tests/test_spatial_memory.py -q

The complete immutable ZIP additionally contains the full science validators, detailed Korean report/handoff, all raw rows, exact CAS source/output, failure logs, figures, ledger and SHA256SUMS. From that ZIP, without redoing science:

    python verify_saved.py

A new science campaign requires explicit execution accounting:

    OPENBLAS_NUM_THREADS=1 python verify_bf3b.py
    OPENBLAS_NUM_THREADS=1 python verify_nonlocal_kernel.py

Git publishes executable core/tests/all seven pinned vendors plus concise metadata. It is not byte-identical to the complete archive payload. Do not run archive-only commands against the selected Git subset. DELIVERY.json identifies the sealed archive and actual backup assurances.

## Next and boundaries

BF3-C is the next scoped unit: a static positive periodic lapse on a prescribed genuinely spatially inhomogeneous metric. Derive/check coordinate-time versus proper-time transport, normal acceleration, Killing energy N*E_local, screen and phase-space/angular measure before adding collisions. A candidate N(x)=exp(epsilon cos x) uses finite epsilon, not a metric-amplitude expansion. Do not auto-run BF3-C, assume EFE constraints, or modify the original Bianchi transport records. General tilt, inhomogeneous EFE evolution, thermal/recoil/frequency validity, production Rust, uniform stiff positivity/tail bounds and efficiency remain open.
