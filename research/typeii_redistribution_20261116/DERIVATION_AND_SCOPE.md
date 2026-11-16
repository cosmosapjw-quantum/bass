# Derived phase-space measure and declared redistribution operator

## Conventions
Metric(-,+,+,+). Normal time t_n in seconds; tau=integral H_n dt_n dimensionless. beta=v/c, Gamma=(1-beta^2)^-1/2. Frequencies are ordinary Hz, E=h nu with h=2pi hbar; temperatures K, proper atom densities m^-3. V=exp[3(tau-tau0)] is physical normal volume relative to its initial value. No normal/atom-volume or reaction/path-clock identification is made.

## Collisionless geometry
The source TypeII angular velocity is v_Omega=-Sigma n+(n.Sigma.n)n+frame rotation+N1 n_x(e_x cross n). For trace Sigma=0, surface divergence is3Sigma_nn. Frame rotation and this TypeII spatial-curvature rotation have zero surface divergence. Thus J'=3Sigma_nn J, while (ln nu_n)'=-(1+Sigma_nn), and V nu_n^3 J is invariant. For homogeneous class-A sources this is the angular/frequency counterpart of the normal-slice Liouville measure; it does not assert flat isotropic spatial geometry.

D=Gamma(1-beta n_y), nu_a=D nu_n, dOmega_a=D^-2 dOmega_n. Directional atomic-tetrad path time is dt_a_ray=D dt_n, not the homogeneous atom-worldline reaction time dt_n/Gamma. Given atom-frame frequency bins, g_i=2/(3c^3)(nu_R^3-nu_L^3) is the mode capacity per physical volume per solid angle. Photon number per reference normal-comoving volume is
N_ai=M_ai f_ai, M_ai=V w_n,a D_a^-3 g_i=V w_a,a D_a^-1 g_i.
The 1/D beyond the atom angular weight is required by the normal spatial slice. The product M_ai D_a=V w_a,a g_i makes reciprocal local angular scattering conserve normal-comoving photon number.

At fixed atom frequency, (ln M)'=3kappa, with kappa=-(ln nu_a)' from the parent exact TypeII Doppler/shear flow. Frequency streaming dnu_a/dtau=-kappa nu_a then has conservative number form partial_tau N+partial_nu[-kappa nu N]=0 along the transported angular labels. Zero tilt/shear reduces to V nu^3=const. Free radiation's normal energy moment independently obeys (V u)'=-V u-V Sigma_ab P^ab in Hubble-normalized units; the source numerical derivative checks this moment, not merely a residual defined as work.

## Reciprocity and detailed balance
In a fixed local atomic frame define delta=(E_j-E_i)/(k_B T_m). The adjacent pair current F_ij=a_ij[f_i(1+f_j)-exp(delta)f_j(1+f_i)], a_ij>=0, conserves photon number and has exact Bose-Einstein equilibrium f(E)=[exp(E/kT+eta)-1]^-1. For dimensionless chemical potential mu_i=ln[f_i/(1+f_i)]+E_i/(kT), the pair contribution to free-energy rate is F_ij(mu_j-mu_i)<=0, since the sign of F is opposite to mu_j-mu_i. A maintained nonthermal background need not be an equilibrium of the full matter system.

The actual tagged runs use f<<1 and drop the O(f^2) induced term. Their reversible stationary count is proportional to g_i exp[-E_i/(k_B T_m)], with the nu^2 density of states retained. The frequency Fokker-Planck form is
partial_s f=(1/nu^2) partial_nu {nu^2 D_nu [partial_nu f+(h/k_B T_m)f]},
with D_nu=(Delta_nu_D^2/2)gamma_sc and Delta_nu_D=nu0 sqrt(2k_B T_m/(m_H c^2)). In the nonlinear local pair check f is replaced by f(1+f) in the recoil/stimulation term. The code uses a Bernoulli/Scharfetter-Gummel edge coefficient: with B(delta)=delta/(exp(delta)-1), the two linear edge rates are proportional to B(delta)/g_i and B(delta)exp(delta)/g_j. This exactly preserves the discrete Wien state. Its units are s^-1 for the photon-count generator; D_nu has Hz^2/s.

The resonance event rate is the declared narrow-line gamma_res(nu)=3 A_21 c^3 n_1s phi(nu)/(8pi nu0^2), phi normalized over frequency in the untruncated Voigt model. The true tagged ionization rate is p_ion gamma_res and the scattering coefficient uses (1-p_ion)gamma_res, with p_ion supplied by the parent's finite n<=3 tagged excitation fate. No global photon death probability or recombination re-entry is inferred from this truncation.

The unpolarized angular kernel K=3(1+cos^2 theta)/(16pi) acts at fixed atomic frequency. On a normal-comoving slice its discrete off-diagonal generator is Q_ab=w_atom,a D_b K_ab, and its stationary angular count pi_a is proportional to w_atom,a/D_a. Elastic angular scattering preserves atom-frame frequency but exchanges normal-frame energy/momentum with the maintained moving material. That energy is recorded separately from frequency-exchange heat.

## What is and is not approximated
The frequency operator is angular-averaged, and angular redistribution is elastic at a common atom frequency. Their sum is a FACTORIZED closure. It is not the full joint R_II(nu,n;nu',n') scattering kernel and does not preserve all angle-frequency correlations of thermal atom velocities. The FP gradient expansion requires spectra smooth over a Doppler width. The initial Gaussian occupation has sigma3 initial Doppler widths; finite absorbing boundaries can create boundary layers, so this is not a uniformly high-order/full-kernel accuracy claim. Narrow-band validity is explicitly checked (max halfwidth/nu0<.05).

The background lower-level abundance is a stationary fixed-ne tracer from the parent, scaled by its conserved proper hydrogen current. Material T, ionization fate, geometry and tilt are prescribed evolving functions, not updated by tagged radiation. Tags are arbitrarily dilute and terminate at a true-ionization event. There is no continuous injection, nonlinear induced-field evolution, populated atom update, thermal/charge/momentum/Einstein backreaction or polarization.

## Numerical conservation and boundaries
Use transported true sphere quadrature, positive conservative frequency remapping, an exact reversible angular semigroup, and implicit M-matrix frequency/ionization steps. Symmetric angular/streaming splitting does not make the whole scheme second order because the frequency implicit step and piecewise-constant remap are first order. Timestep/mesh comparisons report actual observed changes without declaring a global error bound. Tiny semigroup roundoff negatives are bounded, recorded and projected only within stated roundoff tolerances; no physical negative density is repaired by clipping.

The resolved budget is surviving+red-band-exit+blue-band-exit+ionized=initial. Frequency heat is calculated from individual edge currents and their photon energy changes. Geometric work is a discrete normal-energy readout; the separate free-field stress-energy check validates its continuum target. Boundaries are absorbing, not a solution for photons outside the band. A photon crossing a band boundary is NOT globally escaped and may return in a wider true problem.

## Sources
Rybicki(2006), Improved Fokker-Planck Equation for Resonance-Line Scattering, arXiv:astro-ph/0603047, provides the corrected detailed-balance/induced/recoil structure for angle-averaged treatment. Hirata & Forbes(2009), arXiv:0903.4925, and Chluba & Sunyaev(2009), A&A503,345, doi:10.1051/0004-6361/200912335, motivate time-dependent line transfer and frequency diffusion. Their results are not cited as a proof that this factorized anisotropic closure is exact. Original source Git identities, exact CAS residuals, and executable independent checks are stored separately.
