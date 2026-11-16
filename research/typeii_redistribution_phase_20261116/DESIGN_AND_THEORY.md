# Time-dependent resonance redistribution and phase-space measure

Immutable parent PR339 / 0577ef0a40cf10130a5933eb52c7230d4de1f11b. Original BASS main 9c6506e4e2087129a8b674ff10438e5db1a55c9d. Scope: four bounded phases P1..P4, with constructive derivation, source-conditioned computation and one same-author hostile pass. Upper DAG remains 9/15 scoped/source-mapped, new full production upper nodes0. No native subagent available; distinct-author referee NOT_RUN.

## P1: selected positive scientific objective
Construct the next executable approximation beyond frozen independent-ray bands: evolving source TypeII characteristics with the correct normal-slice volume/solid-angle measure; a conservative thermal/recoil frequency redistribution kernel; an explicit all-sky angular quadrature with Rayleigh angular redistribution; actual tagged-photon time evolution with source-defined destruction probability and finite-band exits. Preserve separate states for survival, red-band exit, blue-band exit and true tagged ionization. Do not identify any band exit with global escape.

The scattering approximation is explicitly **factorized**: leading thermal/recoil Fokker-Planck diffusion in frequency plus an elastic electric-dipole angular generator. This retains frequency and angular redistribution moments, but does not solve their full correlated R_II redistribution kernel, polarization, or the atomic population backreaction. Actual tagged line photons are dilute; stimulated frequency scattering is implemented and checked in separate BE equilibrium tests, but the main tagged linear source calculation uses the justified dilute limit. Primary references: Rybicki, ApJ647709(2006), arXiv:astro-ph/0603047; Hirata & Forbes, PRD80023001(2009), arXiv:0903.4925. Rybicki's angle-averaged FP approximation requires spectra smooth on the Doppler scale; a finite-width tagged Gaussian packet is a diagnostic initial condition, not a universal line-emission spectrum.

## Exact geometric derivation
Signature (-,+,+,+); c,h=2pi*hbar,kB retained. d tau_H=H_n dt_n. Normal-frame ray directions obey V=-Sigma n+(n.Sigma.n)n plus a tetrad rotation and TypeII curvature vector N1*n_x*(e_x cross n). Trace Sigma=0; the latter two vector fields have zero spherical divergence, so div_S2 V=3S with S=n.Sigma.n. Frequency y_n=ln(nu_n) obeys y_n'=-(1+S). The angular flow Jacobian J obeys (ln J)'=3S. Consequently a^3 nu_n^3 J is constant along a collisionless characteristic (a=exp(tau_H)).

On a normal hypersurface the invariant photon count is proportional to a^3 nu_n^3 f dy_n dOmega_n, not simply f times fixed solid-angle weights. In the atom tetrad nu_a=D nu_n, D=Gamma(1-beta*n_y), dOmega_a=D^-2 dOmega_n, so the same count is a^3 nu_a^3 f/D dy_a dOmega_a. Using initial normal angular labels and a fixed atom-frequency grid, the cell capacity is proportional to a^3 J D^-3 dOmega_n0 integral_cell nu_a^2 dnu_a. Its logarithmic time derivative is 3kappa, with kappa=1+S-(ln D)'. Therefore conservative frequency advection with nu_a'=-kappa nu_a already incorporates the volume/angle terms; adding an independent -3H dilution would double count them.

The collision occupation source in normal time uses D/H_n times the atom-frame photon collision operator. This yields a^3 dOmega_a/H_n times the proper-frame number source, ensuring collision photon-number conservation on the normal slice. Atomic homogeneous reaction clock 1/(Gamma H_n) is NOT the photon path clock.

## Frequency redistribution and boundaries
Adopt proper-frame frequency diffusion D_nu=(kB Tm/(m_H c^2))*nu^2*R_sc(nu), R_sc=(1-p_ion)*R_res. In occupation form C[f]=nu^-2 d_nu{nu^2 D_nu[d_nu f+h/(kB Tm) f(1+f)]}. Its coefficients are the declared leading, dilute-gas FP closure, not an exact core redistribution function. A fitted pair flux with B(x)=x/expm1(x), delta=h(nu_j-nu_i)/(kBT), is proportional to B(delta)f_i(1+f_j)-B(-delta)f_j(1+f_i). It conserves photons, annihilates any local Bose-Einstein distribution, and admits nonnegative linear dilute transition rates. Frequency-redistribution heat is minus the atom-frame photon energy change. Angular changes are elastic in the atom tetrad but exchange normal-frame bulk energy/momentum; evaluate both frames, rather than calling the normal energy change heat.

Finite frequency bands have explicit absorbing or reflecting redistribution boundaries and red-advection outflow. Default source experiments use absorbing band exits; boundary/time/angular/frequency refinements must be reported, without restoring missing wings by renormalization. Initial tagged packet is prescribed and its sum is one; it is not the normalized full Voigt emission rate.

## Execution and preservation
P1 source/derivation contracts and RED tests; P2 conservative kernels, geometry and equilibrium checks; P3 evolving source packet runs and refinement; P4 same-author hostile audit, verified artifacts, report and handoff. Each phase is committed/pushed with exact remote readback and host ZIP SHA/CRC. Parent external-backup ENOSPC remains known; do not retry or delete user files. Use GitHub + host verified archive and accurately state external NOT_ATTEMPTED_KNOWN_ENOSPC.

## P2 actual evidence
All12 implementation contracts passed after the recorded RED run. Original401-state overlap8.88e-16; finite-difference sphere divergence gap5.51e-10; independently perturbed-ray solid-angle determinant gap1.03e-11. The normal comoving measure is preserved to1.11e-16 locally. Across the original finite source interval, correct comoving photon number is0.9999999999999982 while dropping J produces3.5061314987410097 in the specified collisionless control. This is a concrete measure error, not a dynamical photon source.

The nonlinear stimulated pair model relaxes toward its number-matched Bose-Einstein equilibrium with max occupation gap1.06e-8, number defect6.66e-16, energy-plus-reservoir defect1.78e-15 and nonincreasing free energy. A cancellation-free positive tridiagonal recurrence preserves a stiff closed linear test with rates1e13 and time step1, avoiding subtraction of the unit storage from huge diffusion terms.

In an elastic angular-scattering control, normal photon energy changes0.04751498 per initial atom-frame photon energy, while the atom-frame energy change from the transformed four-force is4.03e-16. Thus that normal energy change is bulk exchange, not atom heat. The source local4x8 angular quadrature has solid-angle defect7.30e-9 over0.02 Hubble-normalized time; higher angular resolution must be checked in the packet campaign.

Actual Wolfram Language residuals: sphere divergence, stimulated BE pair flux and normal comoving measure all zero. These are external CAS algebra checks, not independent-author review.

## P3 actual source campaign
The starting state is mean-z1100 and the interval ends at mean-z1089.04486696 (delta tauH=0.01). All cases use the same tagged Gaussian atom-frame occupation, width3 Doppler units centered at+3. The population/fate and temperature histories are the parent fixed-ne source, not newly solved cosmological populations.
- frequency_double: red=0.29944403589082297, blue=0.29500367249292508, ionized=0.40555229161631245, remaining=3.77426e-110.
- angular_refined: red=0.29944403589079488, blue=0.29500367249290504, ionized=0.40555229161629247, remaining=3.77426e-110.
- band40: red=0.085592523583775407, blue=0.06734254003213111, ionized=0.84706493638415925, remaining=7.54982e-54.
- frozen: red=0.29943644626847044, blue=0.29499658741583706, ionized=0.40556696631590655, remaining=9.55506e-111.
- no_frequency: red=0.061796781448506199, blue=0, ionized=0.93820321855155764, remaining=1.93659e-59.
- no_redistribution: red=0.061570135962576759, blue=0, ionized=0.93842986403742379, remaining=8.63209e-50.
- no_destruction: red=0.50747837172210764, blue=0.49252162827795581, ionized=0, remaining=7.26542e-91.
The 32-to72 direction comparison holds frequency/time resolution fixed. A tighter matched evolving/frozen refinement and an independent unsplit sparse stiff solve are reserved for the final validation phase. The explicit boundary change is a different finite-domain problem, not an accuracy estimate for global escape. The corrected count measure is now used during coupled angular/frequency evolution, not just tested on isolated rays.
