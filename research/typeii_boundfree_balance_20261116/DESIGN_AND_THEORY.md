# Level-resolved bound-free detailed-balance bridge

Frozen parent PR336: ad4bda34a833d215aa49037d7cb4d609e5cee04b. Original BASS main: 9c6506e4e2087129a8b674ff10438e5db1a55c9d. Four bounded local deliverables B1..B4, not new upper production nodes. Native subagent NOT_RUN; one same-author hostile verification pass, not a distinct-author blind referee.

## B1: scope and authoritative microscopic input
The author's nl-resolved H photoionization table h1.px.txt was actually obtained from S.N.Nahar's Ohio State page. Raw SHA256=4150287531cc642ecf837fa253b22f5158bd189b3f2c9ce634010b2e4b5ee44c. Preserve its own header attribution '(unpublished)'; the related 2021 Atoms paper describes the methodology, but the table is not falsely identified as a particular code release. It contains separate 1s through n=10,l=9 states. Photon/excess energy are in Ry and cross section in Mb (1Mb=1e-22m^2). We will retain the finite tabulation and rounding, interpolate positive cross sections only inside their support, and measure interpolation sensitivity separately from quadrature. No high-energy extrapolation, helium-excited-state invention or effective HYREC-rate replacement.

## Definition and derivation contract
Signature (-,+,+,+); keep c,h=2pi hbar,k_B. The state is an unpolarized nl level, g_i=2(2l+1); ion core degeneracy g_+=1, electron spin g_e=2. Nuclear spin cancels and is omitted. Use an infinitely heavy nucleus/nonrelativistic hydrogenic convention matching the source Ry level scale, m=m_e. This is not a finite-mass or fine-structure accuracy claim.

E=chi_i+K, K=m_e v^2/2. Time-reversal/detailed balance gives the Milne capture cross section
sigma_RR(v)=(g_i/g_+) [E/(m_e c v)]^2 sigma_PI(E).
This is spontaneous capture; stimulated emission multiplies the angle-averaged kernel by 1+nbar(E), for isotropic thermal electron velocities and unaligned nl populations. A direction-dependent photon occupation is allowed, but sublevel alignment and finite thermal Doppler/recoil in atomic kinematics are not included.

Let A=8pi/(h^3 c^2), S0_i(Tm)=[g_i/(2g_+)] [h^2/(2pi m_e k_B Tm)]^(3/2).
Gamma_PI=A integral E^2 sigma_PI(E) nbar(E) dE [s^-1].
alpha_i=S0_i A integral E^2 sigma_PI(E) exp[-(E-chi_i)/(k_B Tm)] [1+nbar(E)] dE [m^3 s^-1].
An independent velocity-space integral int v f_MB(v) sigma_RR(v)[1+nbar(E)]dv must agree; it is not defined using a Saha identity.

For Tm=Tr=T, beta=0, n=1/(exp[E/(kBT)]-1), pointwise exp(-K/kBT)(1+n)=exp(chi/kBT)n. Thus alpha_i/Gamma_PI=S0_i exp(chi/kBT), including spontaneous AND stimulated capture. For a Bose-Einstein occupation exp(E/kBT+eta), the corresponding chemical ratio gains exp(eta); ordinary Saha is not asserted for nonzero photon chemical potential.

Rate per proper volume: F_i=n_i Gamma_PI - n_e n_+ alpha_i. Then dn_i/ds=-F_i, dn_+/ds=dn_e/ds=sum F_i conserve nuclei and charge. Each energy bin transfers E to/from photons, K to/from electron kinetic energy, and chi_i to/from ionization energy, with E=K+chi_i. The three signed energy ledgers must sum to zero and each net spectrum vanish at Planck/Saha equilibrium. The same parent clock conversion 1/(Gamma_bulk H_n) applies to the population RHS; it is not an extra photon flux factor.

A finite, closed 2s/2p/continuum kinetics test will check conservation, positivity and equilibrium. It is an isolated reaction-network verification with a prescribed bath, not a cosmological recombination history or a replacement for bound-bound cascades and radiation transfer.

## Chosen construction and acceptance
B1: source lock, analytic contracts, tests recorded RED before implementation.
B2: source-tabulated sigma, Milne forward/reverse kernels including stimulated capture, energy/charge conservation; Planck and BE balance, independent velocity quadrature and threshold checks.
B3: actual parent TypeII states, state-specific beta/alpha and stationary ratios, finite-population kinetics and interpolation/order diagnostics. No new native HYREC xe or optical depth unless genuinely computed.
B4: one self-hostile pass, fresh executable verification, local/external backups, Draft PR and handoff. Stop at this bounded bridge.

Primary literature: https://doi.org/10.3390/atoms9040073 (Milne relation and nl-resolved methodology); https://arxiv.org/abs/1006.1355 (microscopic versus effective multilevel rates). Original data URL and retrieval identity are in sources/PROVENANCE.json.

Upper BASS DAG=9/15 scoped/source-mapped; new full upper nodes=0; StageII historical11/11 current canonical not established; JoinJ1 0/2 HOLD. Production_ready=false; merge_ready=false; auto_next=false.

## B2: finite-support implementation and verification
The source has 55 nl states and 1000 energies per state. Its maximum electron kinetic energy is approximately 9.99 times the state binding energy, not a common high-energy cutoff. Therefore all reported kernels are explicitly finite-band integrals. High-n rates are not promoted to total recombination coefficients. The actual source campaign concentrates on n<=3, while higher-n finite-band tests quantify induced recombination and support sensitivity.
The photon-energy and photoelectron-energy columns are separately rounded in the author table; maximum disagreement with chi+K is 0.00020000000000274158 Ry. The implemented spectral axis is defined by the binding line plus the photoelectron-energy column, never an inconsistent mixture of both. Raw input is preserved.
Independent 1s Coulomb-formula comparison gives max relative source-table difference 7.4432196531581951e-05, accepted at the predeclared 5e-4 tolerance for finite-precision source data. This is not a precision statement for excited-state interpolation.
Actual finite-band Planck/BE balance checks: 165 cases, maximum log residual 3.5527136788005009e-14. Independent Maxwell-speed capture and photon-energy integration agree; angular aberration frame transformation and adaptive QUAD checks are separately stored. Maximum non-equilibrium energy-ledger relative residual 1.1289775791157189e-16.
Twelve analytic tests passed normally and under Python -O. The velocity-space coefficient is computed from sigma_RR and the normalized Maxwell speed density, not defined by imposing Saha. All physical rates use explicit checks rather than removable Python assertions.
