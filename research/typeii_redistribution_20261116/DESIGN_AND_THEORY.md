# Time-dependent resonant redistribution and Type-II phase-space transport

Immutable parent PR339 `0577ef0a40cf10130a5933eb52c7230d4de1f11b`. All changes are research-only. Original main/source locks and parent branch remain unchanged. External disk copies have an unresolved ENOSPC failure from PR339; no repeated writes or user cleanup are authorized by this science continuation. GitHub and verified host ZIPs are the preservation routes.

## Selected bounded work
P1: derive and checkpoint correct normal/atomic phase-space measure, redistribution closure, IC/BC and failing contracts.
P2: implement independently tested angular measure, number-conservative redistribution and finite-band transient solver.
P3: execute actual evolving TypeII inputs, compare frozen/source changes, frequency/angular/time refinement and band boundaries.
P4: one same-author adversarial pass, fresh reproducibility, final source-scoped report and handoff. Native subagent and distinct-author referee NOT_RUN. Local 0/4 initially, upper9/15 scoped/source-mapped; no new full-production node.

## Geometry and measures: derived
Signature(-,+,+,+); retain c,h=2pi hbar,k_B. Tau is the normal Hubble time d tau=H_n dt_n. Original BASS normal-frame direction flow is -Sigma n+(n.Sigma.n)n plus frame rotation and N1 n_x(e_x cross n). With trace Sigma=0 the surface divergence is 3Sigma_nn; rotation and the TypeII curvature term have zero surface divergence. Thus J_Omega'=3Sigma_nn J_Omega. Since (ln nu_n)'=-(1+Sigma_nn) and V'=3V, V nu_n^3 J_Omega is invariant along each collisionless ray. This is the phase-space geometric conservation law, not the assertion that a set of26 rays is an angular quadrature.

Use actual Gauss-Legendre mu x periodic-phi quadrature at the chosen initial slice, transport its directions and weights w_n=w0 J_Omega. In the atomic frame, D=Gamma(1-beta n_y), nu_a=D nu_n, w_a=w_n/D^2. For an atom-frame frequency cell [nuL,nuR], g_i=2(nuR^3-nuL^3)/(3c^3) is its photon-mode capacity per proper volume per solid angle. The photon count per initial normal comoving volume is N_ai=M_ai f_ai with M_ai=V w_a/D*g_i=V w_n/D^3*g_i. At fixed atom frequency M'/M=3kappa. Streaming in fixed atom-frequency coordinates is conservative frequency advection, dnu_a/dtau=-kappa nu_a; collisions multiply occupation changes by the photon-path clock D/H_n. For angular scattering, M_a D_a=V g_i w_a ensures cancellation of pairwise scattering exchange in the normal-comoving number measure.

Actual CAS checks during this invocation gave zero residuals for surface divergence-3Sigma_nn, collisionless V nu^3 J, atomic capacity derivative-3kappa, and Bose pair equilibrium. Source numerical geometry and finite-difference Jacobians will provide independent implementation checks.

## Explicit collision closure and limits
Use the dilute tagged-photon limit of a thermodynamically corrected Fokker-Planck frequency operator. A reversible adjacent-cell flux is proportional to f_i(1+f_j)-exp[(E_j-E_i)/(k_B T_m)] f_j(1+f_i); it exactly annihilates any same-temperature Bose-Einstein occupation. The actual linear tagged runs drop O(f^2), with their arbitrarily scalable packet amplitude chosen to keep occupation dilute; their stationary spectrum is the Wien limit with the CORRECT nu^2 density of states. Frequency diffusion D_nu=(1/2)Delta_nu_D^2 gamma_sc(nu), gamma_sc=(1-p_ion) gamma_res. Original finite-cascade p_ion is kept distinct from the total resonance rate.

Angular redistribution uses the unpolarized dipole kernel 3(1+cos^2 theta)/(16pi) at common atomic frequency. Angle and frequency generators are ADDITIVE/factorized. This is a declared leading angular-averaged frequency-diffusion plus elastic dipole-angle closure, NOT the full correlated R_II(nu,n;nu',n') redistribution kernel. No claim of exact anisotropic redistribution or polarization. Fokker-Planck validity requires smooth photon spectra over a Doppler width; injected tagged packets will be smooth, with width >=3 Doppler widths, and near-boundary errors are assessed by extending the band.

Use original A_2p1s and E0 from parent Coulomb construction; neutral density is the parent's stationary fixed-ne tracer fraction times conserved nHrest, not a new cosmological population solution. The atomic temperature and tagged excitation fate probability are read from parent sources. All background inputs evolve along the actual original BASS TypeII gamma-law source, unless explicitly using a frozen comparison.

## Numerics and admission
Angular changes: exact semigroup of a reversible finite-angle generator with correct weights and path clock. Frequency diffusion/destruction: positive tridiagonal implicit finite volume with explicit red/blue absorbing-bin-boundary counters and true-ionization counter. Streaming: conservative positive remap between exact source characteristic frequencies. Source coefficients update in time. Internal splitting/time error is measured by refinement, never confused with physical closure or band truncation.

Tagged packet number: surviving+red-band-exit+blue-band-exit+ionization=initial. Band exits are NOT global Ly-alpha escape; no re-entry beyond the declared band is modeled. Atom-frame frequency-scattering heat and angular/frame momentum exchange can be read out but do not backreact on the frozen matter reservoir. Photon/redshift energy bookkeeping is separate from a claim of closed Einstein-matter-radiation evolution.

Acceptance: correct unit/isotropic/boost equilibrium limits, phase-space Jacobian, positivity and number/energy accounting; independent small-generator matrix exponential or ODE comparison; actual TypeII source campaign with convergence and wrong-measure/clock/recoil counterexamples. If convergence fails, preserve the defect and do not promote precision claims.

Primary references: Rybicki(2006), arXiv:astro-ph/0603047 (corrected equilibrium Fokker-Planck); Hirata & Forbes(2009), arXiv:0903.4925; Chluba & Sunyaev(2009), A&A 503,345, doi:10.1051/0004-6361/200912335. These establish isotropic/angle-averaged redistribution methods; the present directional factorization is an explicit added model assumption, not a result attributed to those papers.

## P2 executed verification
Original401 state max gap 5.5511151231257827e-16. Phase-volume invariant max defect 1.2656542480726785e-14. Independent neighbor-characteristic surface Jacobian relative gap 5.4269955196417641e-10; normal-frame integrated radiation energy/stress derivative relative gap 1.8143842532230763e-11.
The initial512-direction sky integral did NOT meet its declared2e-8 global-area target over the full z1700..300 characteristic interval. The per-ray phase invariant stayed near1e-14. Holding physics/tolerances fixed, angular refinement to4608 directions reduces the sky-area gap to6.891e-12. The initial failed log and intermediate32/128/512/2048-resolution diagnosis are preserved. Short tagged-packet intervals use independent angular refinement rather than reusing the full-interval coarse quadrature as exact.
The frequency implicit solver converges against an independent dense matrix exponential, the angle semigroup agrees with another dense exponential, and the nonlinear Bose pair has nonpositive free-energy derivative and exact thermal equilibrium. Actual tagged experiments use the dilute linear limit, not a nonlinear Bose evolution.
