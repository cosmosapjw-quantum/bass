# Time-dependent resonant redistribution and phase-space transport: scoped result

Draft PR341. Immutable parent PR339/0577ef0a40cf10130a5933eb52c7230d4de1f11b. Local phases P1-P4 complete for the stated approximation. Upper DAG9/15 scoped/source-mapped; zero new full-production nodes. Main/parent/production code unchanged.

## Derived and actually implemented geometric measure
The original TypeII direction flow has sphere divergence3 Sigma_nn. Propagating its angular Jacobian gives J'=3 Sigma_nn J, while (ln nu_n)'=-(1+Sigma_nn). Hence a^3 nu_n^3 J is conserved along a collisionless ray. For two photon polarizations the count on a normal hypersurface is dN=(2/c^3) a^3 f nu_n^2 dnu_n dOmega_n dV_comoving. With nu_a=D nu_n and dOmega_a=D^-2 dOmega_n, it becomes (2/c^3)a^3 f nu_a^2 dnu_a dOmega_a/D dV_comoving. With initial normal angular labels the cell capacity is proportional to a^3 J D^-3 times the atom-frequency cell's integral of nu_a^2. This is implemented as the transported photon count, not a fixed-volume occupation surrogate.

A new positive polar/azimuthal quadrature is used and advected with the source direction equations. The original26 source rays are not treated as sky quadrature. Finite-difference divergence and perturbed-ray area determinants independently verify the Jacobian (gaps5.51e-10 and1.03e-11). Over the original finite TypeII interval the correctly counted comoving photons equal0.9999999999999982; dropping J gives3.5061314987410097 in the same control. Normal-slice collision time uses D/H_n, not1/(Gamma H_n).

## Stated scattering approximation and conservation
We use leading thermal/recoil Fokker-Planck frequency redistribution plus a separately applied elastic electric-dipole angular generator. This **factorized model is not the full correlated angle-frequency R_II kernel**. The chosen D_nu=(kB Tm/(m_H c^2))nu^2 R_sc has units Hz^2/s. The occupation collision operator is nu^-2 d_nu[nu^2 D_nu(d_nu f+h/(kB Tm)f(1+f))]. Its exponential-fitted pair flux conserves photons and annihilates a common-temperature Bose-Einstein distribution. Actual nonlinear BE relaxation verifies number, reservoir heat and free-energy behavior. The main tagged packet runs use the dilute linear limit; the maximum prescribed background occupation in the widest z1100 band is 3.6910752384893403e-17. Tags represent a linear response, not physical occupancy inferred from a unit probability.

Rayleigh angular scattering is elastic in the atom tetrad, but normal-frame photon energy changes through momentum exchange with the bulk flow. The separate normal-energy/momentum and proper heat readouts were tested. A standalone angular test has normal energy change0.04751498 per initial atom-frame energy while its atom-frame energy change is4.03e-16. It must not be called thermal heating. Frequency redistribution heat is minus the atom-frame photon energy change; normal-frame frequency exchange and geometric work are recorded separately. Terminal ionization records the photon energy removed, not a fully solved atomic calorimeter.

## Actual time-dependent source data
Fifteen source packet cases ran. The principal start is mean-z1100, ending1089.0448669578338 over delta tau_H=0.01. Initial condition: an isotropic atom-frame occupation with a prescribed Gaussian frequency shape, centered+3 and width3 initial Doppler units, normalized to one tagged photon on the normal hypersurface. Source n1s, Tm and finite n<=3 tagged ionization fates are prescribed parent histories. No photon feedback into atomic populations, thermal evolution, electron density or metric is solved.

| case | red band exit | blue band exit | tagged ionized |
|---|---:|---:|---:|
| fine_evolving | 0.29943711414400281 | 0.2949971103613197 | 0.40556577549478567 |
| fine_frozen | 0.29942961684649594 | 0.2949901114939113 | 0.40558027166001898 |
| band40 | 0.085592523583775407 | 0.06734254003213111 | 0.84706493638415925 |
| band80 | 0.023053079558426198 | 0.0040881519528947665 | 0.97285876848879649 |
| no_frequency | 0.061796781448506199 | 0 | 0.93820321855155764 |
| no_redistribution | 0.061570135962576759 | 0 | 0.93842986403742379 |
| no_destruction | 0.50747837172210764 | 0.49252162827795581 | 0 |
| earlier_source | 0.030503741425910329 | 0.038078062501161657 | 0.93141819607289311 |
| later_source | 0.50824531849667698 | 0.48852388867053809 | 0.0032307928328172159 |

The20/40/80-Doppler cases have **different absorbing boundaries**, so they are different finite-domain problems, not a globally converged escape estimate. A photon crossing the blue edge can physically return after redshifting and a red-edge photon can return by diffusion; this model deliberately terminates both. The large total-exit change -0.56729299299400149 between20 and80 widths refutes interpreting these boundary probabilities as global escape. The earlier/later cases start at mean-z1400 and800 respectively and share the declared interval and packet recipe, not a single cosmological emission history.

The factorized frequency process and angular process share a physical scattering rate; their individual leading moments are represented, but their joint correlations are not. This is an explicit physical approximation, not a second independently physical population of scatterings. FP validity requires sufficient spectral smoothness on a Doppler scale. Core redistribution accuracy, the chosen moment closure and boundary matching remain distinct from discretization error.

## Numerical convergence and independent evolution
A frozen actual-source discretization with8 angular nodes and40 frequency cells was integrated by an independent **unsplit sparse BDF** system with explicit loss states. Split-solver probability gaps for96/192/384 steps are1.84436e-6/2.21108e-7/1.04991e-7. This compares two different temporal algorithms for the same finite-dimensional model, not to an exact R_II solution.

In the evolving32-angle20-width source run, 320cells/384steps to640cells/768steps changes a terminal probability by at most 1.3483878473219413e-05. The paired evolving-minus-frozen tagged-ionization effect is -1.4496165233301994e-05; the change of that paired effect under joint refinement is 1.7853436079517948e-07. The separate32-to72 angular-node comparison holds frequency/time grids fixed and differs by approximately3e-14 in this specific nearly isotropic packet. No general all-source angular accuracy certificate is claimed.

Across all15 cases, count-ledger maximum defect=4.2676973066591017e-13; normal energy+boundary loss+destruction+geometric/interaction work residual=1.4908186447490368e-15 in initial line energy units; collision four-force frame defect=1.8136154681447353e-19. Small ledger residuals demonstrate conservation of the implemented model, not accuracy of its physical approximations.

## Executed verification and repairs
14 unit contracts x normal/-O=28 actual test executions;15 malformed inputs rejected. Three optimized science replays reproduce7 JSON/CSV/NPY outputs byte-exact. Original BASS9/9 blobs and selected parent source identities are unchanged. External CAS residuals for sphere divergence, BE pair flux and comoving measure are zero; these are algebra checks, not independent-author review.

Two actual input-admission bugs were detected with RED regression tests: fractional frequency-cell numbers silently truncated to integers, and tiny negative photon counts admitted as a tolerance. Both now reject before computation. No physical rate, accepted solution, input identity or numerical tolerance was changed. The source data reproduced after repair.

Same-author hostile controls: omitting stimulated scattering gives BE pair-flux relative error0.10585559970964724; omitting D from the angular generator fails equilibrium with generator residual0.00049695612161618219; omitting J causes the3.50613 collisionless-count error above. Native subagent and distinct-author/blind referee NOT_RUN.

## Preservation and claim boundary
Every P-stage is separately committed/pushed, remotely read back and host-archived with ZIP/SHA256 checks. No external write is attempted because the previous unit already diagnosed repeated ENOSPC. Do not report a new external backup as verified. No user data was deleted or storage configuration changed. Hosted CI is not established unless separately read back.

Admit exact source-local phase-space and tetrad identities, a conservative discrete thermal kernel, source-conditioned time-dependent packet evolution and explicit boundary/model sensitivity. Do not admit a complete joint redistribution kernel, global escape, self-consistent atomic/thermal/metric feedback, polarization, native HYREC population rerun, new cosmological xe/tau or observed CMB. Upper9/15 unchanged; StageII11/11 historical/current canonical unestablished; JoinJ1 0/2 HOLD. Production_ready=false, merge_ready=false, auto_next=false.

Next constructive unit: CORRELATED_ANGLE_FREQUENCY_REDISTRIBUTION_AND_OUTER_BOUNDARY_MATCHING. Compare the factorized frequency/angle treatment with a source-bound joint redistribution kernel and attach conservative outer-band propagation/re-entry before interpreting an escape probability. Independently retain StageII evidence recovery and authorized storage repair.

Primary literature: Rybicki(2006), arXiv:astro-ph/0603047, and Hirata & Forbes(2009), arXiv:0903.4925. Their redistribution and equilibrium analyses inform the approximation and its limits; the TypeII measure and present numerical outputs were derived/executed here.
