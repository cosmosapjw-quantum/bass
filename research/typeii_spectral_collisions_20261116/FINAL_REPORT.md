# Type II electron-frame spectral photoionization and Compton moments

Immutable parent PR334: 7ad4e4b1cf841e0a974715bcece739ec06b38014. Current Draft PR336. This unit has four local deliverables S1..S4, not four upper production nodes.

## Derived and implemented result
The mean-electron-frame occupation of the prescribed normal Planck bath is n(x,mu)=1/[exp(Gamma*x*(1+beta*mu))-1]. Proper ground-state photoionization rates and photoelectron excess-energy moments were implemented with author-supplied Verner HI/HeI/HeII cross sections. An independent normal-frame integral includes the full energy/solid-angle transformation. The original source Fortran remains unmodified and is compiled for parity tests.

For nonrelativistic isotropic thermal electrons and unpolarized input radiation, the leading Compton energy moment retains the induced angular bilinear B=n0^2-(6/5)n1^2+(1/2)n2^2-(3/10)n3^2. With U3=integral x^3 n0 dx and J4=integral x^4(n0+B)dx, T_C/T_n=J4/(4U3) and proper electron heat is 4 sigma_T c k_B u_e (T_C-T_m)/(m_e c^2). Photon number is conserved by the associated frequency-flux moment. The formula reduces to Planck/BE equilibrium at zero tilt. It is an instantaneous unpolarized energy closure, not the full angular/polarized collision evolution.

The separate low-beta derivation gives T_C/T_n=1+(2pi^2/9-7/6)beta^2+O(beta^4). At beta=.05 the full numerical ratio is 1.0025698013034738, whereas the energy-matched scalar temperature differs. Omitting induced scattering gives T_C/T_n=0.95805737403223501 even at zero tilt, failing thermal equilibrium.

## Actual source data and passive temperature response
The current experiment uses 358 original-TypeII source time states on mean z1700..300, 1074 ground-state single-target rate records, and five fixed-parent-xe thermal trajectories. There is no new native HYREC population history and no new optical-depth result.

At mean z1100, the exact boosted HI proper photoionization rate is3.518365641965801e-15 s^-1, 2.059847906279727 times the unboosted normal blackbody and1.99245467389383 times the energy-matched scalar approximation. At mean z300 the HI ratio is17.866634494285965 but the absolute rate is only1.6524912672105466e-75 s^-1. Helium rates can have even larger ratios with still smaller absolute values; the full data retain logarithms to avoid mistaking underflow or large ratios for a physical population effect. These are ground-state continuum diagnostic rates, not net recombination.

With identical parent xe(t), H(t), proper-clock factor, fixed-composition thermal convention and initial T_m(z1700), the passive endpoint mean-z300 temperatures are:
- prescribed scalar bath: 778.51179156376213 K;
- energy-matched scalar bath: 778.75220103768129 K;
- spectral induced-Compton energy moment: 779.17597606057529 K.
Spectral minus scalar is 0.66418449681316361 K; spectral minus energy-matched is 0.42377502289400582 K. The largest stored-grid spectral-minus-scalar difference is 11.815483309938827 K near the finite intervention boundary. The endpoint is more directly interpretable than a boundary-adjacent sampled maximum. None of these differences include xe feedback, chemical heat-capacity terms or momentum/radiation backreaction.

## Actual verification and bounded hostile review
12 analytic contracts passed normally and under Python -O (24 test executions). The original Fortran fit agrees in24 HI/HeI/HeII energy cases within maximum relative 1.0792268789749926e-06; this numerical parity does not establish a new accuracy bound on the astrophysical fit itself. Independent adaptive photo integrals, direct pair-angle and literal azimuth kernel integrations verify the spectral quadratures. Three differentiated frequency-flux cases give photon-number residuals below5e-16 and energy-moment residual below2e-14 in normalized units. The actual source probes have maximum frame-rate relative gap 1.1368683772162249e-13, and independent Radau/BDF passive-temperature gap below 1.3571161616710015e-06 K.

Wrong-model controls: omit aberration measure and the example HI rate shifts by 0.065173650214503637 relative; omit induced scattering and the zero-tilt equilibrium temperature ratio shifts by -0.04194262596776499; collapse the angular induced term into n0^2 and the beta=.05 Compton temperature ratio shifts by 9.9774015791975756e-05. Seven malformed inputs are rejected. Source/baseline physical calculations replay under -O byte-identically. Original BASS9/9 blobs remain unchanged. Review is same-author hostile, not genuinely blind or independently authored; native subagent NOT_RUN.

## Scope disposition and next construction
Admit source-locked microscopic continuum rates, derived leading Compton energy moment with induced angular structure, numerical source-field rates, and a controlled passive thermal response. Hold state-resolved forward/reverse bound-free detailed balance, stimulated recombination and native multilevel atom coupling, variable-composition chemical energy, polarized/anisotropic radiation evolution, force/momentum feedback, Einstein-baryon-radiation coupling and observed CMB visibility. The local normal Planck field is prescribed, not derived as a global Bianchi radiation solution.

Next unit: LEVEL_RESOLVED_BOUND_FREE_DETAILED_BALANCE_BRIDGE. Obtain level-resolved cross sections and reverse radiative-capture kernels with exact normalization and thermal equilibrium tests, then couple them to the native population equations without disguising a ground-state diagnostic as an effective multilevel rate. Retain the separate proper clock and radiation energy/angle structure.

Local S1..S4 scoped complete; upper BASS DAG9/15 scoped/source-mapped; new full upper nodes0. StageII11/11 historical/current canonical evidence unestablished; JoinJ1 0/2 FULL PASS HOLD. Production_ready=false, merge_ready=false, auto_next=false. Each phase has a pushed checkpoint, remote readback and host/external-disk hash-verified archive.
