# Milne normalization, conservation and finite-network interpretation

## 1. Explicit conventions and the independent inverse integral
Use h=2 pi hbar, g_i=2(2l+1), g_plus=1, electron spin2. The nucleus is infinitely massive, electrons are nonrelativistic and Maxwellian, nl magnetic sublevels are unaligned and the photons are unpolarized. The source hydrogenic level scale is retained; no reduced-mass/fine-structure precision claim is made. Photon energies E=chi_i+K, K=m_e v^2/2, are measured in the common matter rest frame. The bulk radiation boost is distinct from this thermal relative electron velocity.

Time reversal gives sigma_RR(v)=(g_i/g_plus) E^2/(m_e^2 c^2 v^2) sigma_PI(E). The two photon polarizations and electron spin are not both counted again: g_e=2 appears in S0_i below. For a normalized Maxwell speed density
f_MB(v)=4pi [m_e/(2pi k_B T_m)]^(3/2) v^2 exp[-m_e v^2/(2k_B T_m)],
alpha_i=int_0^vmax v f_MB(v) sigma_RR(v) [1+nbar(E)] dv.
Using dK=m_e v dv produces
alpha_i=(g_i/g_plus) sqrt(2/pi)/(m_e^(3/2)c^2(k_B T_m)^(3/2))
        *int_chi^Emax E^2 sigma_PI(E) exp[-(E-chi)/(k_B T_m)] [1+nbar(E)] dE.
Writing S0_i=[g_i/(2g_plus)] [h^2/(2pi m_e k_B T_m)]^(3/2) and A=8pi/(h^3c^2) gives the implementation's alpha_i=S0_i A int(...). The velocity integrator evaluates the original v f_MB sigma_RR expression independently. A Saha identity is a test of the resulting kernels, not the definition of the reverse rate.

For isotropic thermal electron velocities and unaligned levels, averaging over electron directions makes the stimulated capture factor depend on the photon angular monopole. Sublevel polarization/alignment, photon momentum transfer and thermal-motion Doppler terms are not evolved by this scalar rate interface. The Lorentz-transformed bath is prescribed locally, not a globally solved Bianchi radiation field.

## 2. Detailed balance on an explicitly finite common band
Forward beta_i=A int_chi^Emax E^2 sigma_PI(E) nbar(E)dE. At zero bulk tilt and common T, Planck n satisfies exp[-K/(kBT)](1+n)=exp[chi/(kBT)]n pointwise. Hence alpha_i/beta_i=S0_i exp[chi/(kBT)], independent of the cross-section shape provided BOTH directions use the same support and microscopic source. With Bose-Einstein occupation [exp(E/kBT+eta)-1]^-1 the ratio gains exp(eta). The equilibrium relation for eta=0 is Saha; eta>0 represents the specified photon chemical potential, not an ordinary zero-chemical-potential blackbody.

The equality holds on a finite common band. It therefore does not prove that the band approximates an integral to infinity. The original table has Kmax approximately9.99chi_i; high-n data are finite-band diagnostics. No unmeasured tail is extrapolated. For the primary n<=3 TypeII source campaign, Kmax/kT_hot>=35.9573. This scale separation is reported, but no rigorous missing-tail bound is claimed without a high-energy cross-section assumption.

At exact thermal equilibrium, the photoelectron-excess-energy moment and reverse captured-electron kinetic moment also match, not only total number rates. This is checked numerically per selected state. The source binding and kinetic-energy columns define E=chi+K; separately rounded photon-energy values are retained in the archive but not mixed into this identity.

## 3. Particle and energy exchange
Let P_i=n_i beta_i and C_i=n_e n_plus alpha_i. Then F_i=P_i-C_i,
(dn_i/ds,dn_plus/ds,dn_e/ds)=(-F_i,F_i,F_i).
Nuclei and charge are conserved channel by channel. In the no-recoil approximation,
Q_kinetic=P_i <K>_PI - C_i <K>_RR,
Q_ionization=chi_i(P_i-C_i),
Q_photon=-P_i(chi_i+<K>_PI)+C_i(chi_i+<K>_RR).
Their sum is zero. These are signed proper-volume source terms; a fixed external photon bath need not have zero Q_photon away from equilibrium. No inferred change in its spectrum is made without evolving a radiation equation. In the original homogeneous BASS variables, a fraction source divides by n_Hrest Gamma H_normal. This is the proper reaction-clock conversion, not an extra photon-relative-flux factor.

## 4. Isolated reversible 2s/2p/continuum network
This small test is deliberately not a cosmological atom model. Bound-bound processes, ground-state cascades and photons/electron-temperature feedback are omitted. With y_i=n_i/n_H, x=n_e/n_H=n_plus/n_H=1-y_2s-y_2p,
y_i'=a_i x^2-b_i y_i,
where prime denotes u=t_proper*max(beta_i), a_i=n_H alpha_i/max(beta_i), b_i=beta_i/max(beta_i). All coefficients are positive. The nonnegative simplex is invariant: y_i'=a_i x^2>=0 at y_i=0 and x'=sum b_i y_i>=0 at x=0.

Let A0=sum(a_i/b_i). The unique positive stationary solution is
x*=2/[1+sqrt(1+4A0)], y_i*=(a_i/b_i)(x*)^2.
For common-temperature Planck radiation, equal hydrogenic n=2 binding energies imply y_2p*/y_2s*=g_2p/g_2s=3. A nonthermal bath changes alpha_i/beta_i differently because sigma_2s(E) and sigma_2p(E) differ; that stationary ratio need not be3.

Define D=2[x ln(x/x*)-x+x*]+sum_i[y_i ln(y_i/y_i*)-y_i+y_i*]. Its derivative is
D'=-sum_i(f_i-r_i)ln(f_i/r_i)<=0,
f_i=b_i y_i, r_i=a_i x^2.
This is a mathematical Lyapunov property of the finite fixed-rate mass-action system. It is not a thermodynamic free-energy assertion for the anisotropic photon bath or an H theorem for the full atom-radiation system. Two independent stiff integrators and an independently calculated stationary solution test the code.

## 5. Source provenance and interpretation
The raw author table labels itself S.N.Nahar '(unpublished)'. The related Nahar2021 Atoms9,73 paper describes nl-resolved photoionization/recombination methodology; the raw file is not falsely identified as an exact output of a recovered Fortran program. An independent Coulomb 1s formula agrees with the finite-precision source to7.44e-5 relative. Excited-state fit/interpolation accuracy is not thereby certified.

Current coefficients are microscopic state rates, NOT HYREC effective multilevel coefficients. Those effective coefficients already include elimination/cascade probabilities of internal states and radiation-transfer assumptions. Adding a direct rate to an effective rate could double-count channels. The next construction must add source-resolved bound-bound transitions and an explicit conservative elimination map before native population replacement.
