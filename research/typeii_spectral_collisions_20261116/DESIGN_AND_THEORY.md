# Electron-frame spectral collision moments: bounded research unit

Immutable parent PR334 `7ad4e4b1cf841e0a974715bcece739ec06b38014`. Four deliverables S1 source/formula contract; S2 implemented kernels plus analytic/source tests; S3 BASS data and fixed-xe thermal response; S4 bounded hostile verification and handoff. Upper DAG9/15 scoped/source-mapped unchanged, new full upper nodes0. Native subagent NOT_RUN; same-author hostile verification only.

## Scope and physical assumptions
Metric (-,+,+,+), beta=v/c, Gamma=(1-beta^2)^(-1/2). Unpolarized radiation is a prescribed isotropic Planck field in the normal frame with T_n=2.7255(1+z_mean)K. In the mean-electron rest frame its occupation per polarization is n(x,mu)=[exp(Gamma x(1+beta mu))-1]^(-1), x=E_e/(k_B T_n). Retain c,h,hbar,k_B explicitly. Electrons are nondegenerate isotropic Maxwellian about that mean velocity. Compton expansion keeps first order k_B T_m/(m_e c^2) and E/(m_e c^2), neglecting their products and squares. Beta enters the prescribed spectrum exactly; no globally evolved Bianchi radiation, polarization or momentum feedback is claimed.

## Photoionization, original cross-section ownership
Use original Verner et al. (1996) ground-state H I, He I and He II fit parameters from the author's photo.dat and original phfit2.f, both archived and SHA256 locked. Native Fortran accepts eV and returns Mb; 1Mb=1e-22 m^2. Fit is sigma=sigma0[(x-1)^2+yw^2]y^(P/2-5.5)(1+sqrt(y/ya))^(-P), x=E/E0-y0, y=sqrt(x^2+y1^2), above threshold and within source Emax. Below threshold sigma=0. This is a fit, not an exact atomic solution; verify our evaluator against the unchanged original single-precision Fortran with predeclared relative tolerance2e-5 away from the threshold boundary.

For targets at rest in the mean-electron frame, the proper photoionization rate is
R_i=8pi/(h^3 c^2) integral[E_th,infty] E^2 sigma_i(E) n0(E) dE,
and the deposited photoelectron energy source replaces sigma by (E-E_th)sigma. n0=<n> is angular average, not a fitted single blackbody. A normal-frame independent calculation uses D=Gamma(1-beta mu_n), dOmega_e=dOmega_n/D^2 and R_i=<R_iso(T_n D)/D^2>_n. It must agree with the direct electron-frame angular integral. Ground-state single-target rates/heating are diagnostics only: do not substitute them for HYREC's excited-level effective rates or net recombination coefficients.

## Compton energy moment, including stimulated angular coupling
Let n_l(x)=(1/2) integral[-1,1]n(x,mu)P_l(mu)dmu. The normalized recoil angular kernel is W(cosTheta)=3/4(1-cosTheta)(1+cosTheta^2). It integrates to one under dOmega'/4pi and expands as P0-(6/5)P1+(1/2)P2-(3/10)P3. Thus
B(x)=<n S[n]>=n0^2-(6/5)n1^2+(1/2)n2^2-(3/10)n3^2,
where S[n](Omega)=integral[dOmega'/4pi] W(Omega.Omega') n(Omega'). Although individual coefficients are negative, the direct double angular integrand is nonnegative for n>=0.

Write U3=integral x^3 n0 dx and J4=integral x^4[n0+B]dx. With Cgamma=8pi/(h^3 c^3), u_e=Cgamma(k_B T_n)^4 U3 and T_C/T_n=J4/(4U3). Proper energy gained per electron is
P_e=4 sigma_T c k_B u_e/(m_e c^2) (T_C-T_m).
The thermal term depends only on the energy monopole; the induced recoil term does not depend only on n0. For unpolarized input, this follows by integrating the thermal/recoil angular collision operator and using self-adjointness of S. The integrated recoil operator is a frequency divergence; photon number is conserved. This scalar moment is not the full polarized collision operator.

At beta=0, B=n^2 and integration by parts gives J4=4U3 for a Planck spectrum, so T_C=T_n. Omitting induced scattering instead gives T_C/T_n=zeta(5)/zeta(4), which is not unity. The same thermal fixed point holds for isotropic Bose-Einstein occupation1/[exp(x+eta)-1], eta>=0.

For the boosted Planck field, a separate small-beta expansion gives
T_C/T_n=1+[2pi^2/9-7/6]beta^2+O(beta^4), coefficient1.02657875579763525.
This differs from the energy-matched scalar temperature T_U/T_n=[Gamma^2(1+beta^2/3)]^(1/4)=1+beta^2/3+O(beta^4). The expansion is a derivation to test, not an assumed exact expression at finite beta.

## Implementation and acceptance
`collisions.py`: SI photon density/heat moments, original fit evaluator, stable threshold/Wien photoionization quadrature, angular Compton bilinear and proper-clock thermal source.
`test_collisions.py`: failing tests first, then Planck/BE balance, exact boosted moments, direct pair-angle versus Legendre bilinear, opposite-beta symmetry, threshold positivity, source Fortran parity, frame/aberration equality and cold-electron recoil sign. Tolerances: independent photo rate quadrature2e-7 relative; photon energy3e-10 relative; Planck/BE T_C3e-10 relative; finite-beta bilinear3e-11 relative; source cross-section2e-5 (original REAL precision). No tolerances widened simply to pass.
`source_campaign.py`: evaluate microscopic rates on the existing source interval and integrate a passive fixed-xe temperature ODE using PR334's separated proper clock/expansion. Compare prescribed scalar bath, energy-matched scalar bath, and the spectral Compton moment. This is not a re-integrated xe history or a full atom/radiation feedback calculation.

## Source references and evidence
Verner, Ferland, Korista, Yakovlev, ApJ465,487(1996), author data/code: https://www.pa.uky.edu/~verner/photo.html .
Pitrou, arXiv:1902.09456v2 (2020), secs VI.A and VII.C-D, especially unpolarized S-kernel multipoles and nonlinear recoil terms. The source text was read; web PDF screenshots failed with cache errors, so no diagram-only evidence is claimed. The angular kernel and moment reduction above are independently derived and tested, not a copied full-operator implementation.
Sazonov & Sunyaev, ApJ543,28(2000), arXiv:astro-ph/9910280, anisotropic Compton redistribution and induced scattering context.
Ford & O'Connell, arXiv:1310.3238: directional boosted Planck distribution context.
Actual Wolfram check returned kernel coefficients{1,-6/5,1/2,-3/10,0,0}, unit normalization and zero Planck-balance residual. Small-beta coefficient simplified to2pi^2/9-7/6.

## S2 executed evidence
Twelve tests were first RED because the implementation was absent, then all twelve passed normally and under Python -O. Original unmodified phfit2.f was compiled into a shared library; 24 HI/HeI/HeII samples agree with the double-precision evaluator within max relative 1.0792268789749926e-06, below the predefined 2e-5 original-REAL tolerance.
An adaptive integral using the analytic angular occupation average independently agrees with directional Gauss quadrature (five cases including a deep Wien tail) to max relative 1.1368683772160957e-13. Independent direct pair-angle Compton integration agrees with the Legendre form; the adaptive frequency calculation gives Tc/Tn=1.0025698013034736 for beta=.05, difference 2.2204460492503131e-16 from the main implementation.
One verification-only normalization defect was diagnosed and repaired without changing any physical threshold or tolerance: converting the exact HI threshold eV->J->eV produced 13.599999999999998 rather than 13.6, so the strict below-threshold sigma=0 branch was incorrectly used as an integration normalization. The independent verifier now reads the original threshold in its native eV units. ADAPTIVE_NORMALIZATION_FAILURE.log preserves the failure; the actual quadrature samples lie strictly above threshold.
