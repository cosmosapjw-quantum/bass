# REI AX03: independent initial shear and initial anisotropic stress background

2026-10-15 KST. This is a NEW source-matched theory/construction and runnable coding lane, not a claim that the legacy AX08 scientific admission is complete. PhysMath constructive theory and actual Ubuntu Python/Rust implementation; no local Codex. Native subagent NOT_RUN because unavailable. Original REI owner checkout, historical checkpoints and signed chemistry solver not mutated or restarted.

## Physical model and conventions

Original REI AX03 source-family SHA256:
46f818c2f9de890c72f71fa3cc70366b28c42ca0d65190bd905b6310023e7af0.
Keep H0=67.4km/s/Mpc, Omega_m=.315, Omega_r=.000092, Omega_Lambda=.684908, a_ref=1/21, a_end=1/5, proper time elapsed from zbar20, signature(-,+,+,+), non-tilted normal frame, metric axes a_perp=a exp(-b), a_parallel=a exp(2b), sigma diag(-s,-s,2s), s=dot b, q_ref=s_ref/H_FLRW(a_ref) in {0,+/-.005,+/-.01}.

This lane adds an INDEPENDENT initial anisotropic stress pi^i_j=diag(-pi_s,-pi_s,2pi_s) in SI J/m3. Its temporal evolution comes from a nonnegative free-streaming massless radiation angular distribution at zbar20:
W(mu_ref)=1+kappa P2(mu_ref), P2(mu)=(3mu^2-1)/2, |kappa|<=1/2, W>=1/2.
Mean W=1 and pi_s_ref / epsilon_rad_ref = kappa/15. q_ref and kappa are separately selected initial conditions.

Conserved Bianchi-I Killing momenta yield:
R^2(b,u)=exp(2b)(1-u^2)+exp(-4b)u^2,
mu_late=exp(-2b)u/R,
M(b,kappa)=<W R>,
P(b,kappa)=<W R P2(mu_late)>/3,
where <...>=(1/2) integral from -1 to1.

Physical radiation energy and anisotropic pressure use the SAME original Omega_r at the reference event:
eps_r=eps_crit0 Omega_r a^-4 M,
pi_s=eps_crit0 Omega_r a^-4 P,
eps_crit0=3 H0^2 c^2/(8piG).
The physical and exact angular identity is dM/db=-6P because dR/db=-2R P2(mu_late).
Therefore dot eps_r+4H eps_r+6s pi_s=0 and sigma:pi=6s pi_s. Matter and Lambda separately conserved. No arbitrary pi(t) closure is imposed.

Einstein density constraint and exact LRS shear difference equation:
H^2=H0^2 [Omega_m a^-3+Omega_Lambda+Omega_r a^-4 M]+s^2,
dot s+3Hs= (8piG/c^2) pi_s =3 H0^2 Omega_r a^-4 P.
With x=ln(a/a_ref), tau=H_FLRW,ref*t, S=s/H_FLRW,ref, E=H/H_FLRW,ref and f0=(H0/H_FLRW,ref)^2:
tau'=1/E, b'=S/E,
S'=-3S+3 f0 Omega_r a^-4 P/E,
E^2=f0(Omega_m/a^3+Omega_Lambda+Omega_r M/a^4)+S^2.
IC (tau,b,S)=(0,0,q_ref). Case q=0,kappa=0 is exactly FLRW; q!=0,kappa=0 generates pi(t) despite zero INITIAL stress, so it need not agree with the old stress-free source s proportional to a^-3.

**Crucial model scope**: the entire effective Omega_r is treated as collisionless massless background radiation after zbar20, with initial Planck-shaped energy and tunable directional quadrupole. This is a conditional Einstein-Vlasov scenario, not the real partially collisional CMB+neutrino+ionizing radiation/Thomson kinetics in a full EoR calculation. Historical AX03 with prescribed zero pi remains an independent, immutable physical lane.

## Actual local scientific calculations

DOP853 Python on user Ubuntu 24.04 and separately implemented native Rust GL32/RK4:
- q=0,kappa=0 => b_end=0, s/H=0 exact.
- q=0,kappa=+0.2 => b_end=+8.411890570790299e-5, s/H_end=+5.893032805463658e-5, shear generated ONLY by initial pi.
- q=0,kappa=-0.2 => b_end=-8.41234909519269e-5, s/H_end=-5.893749791405375e-5.
- q=+.005,kappa=0 => b_end=.0029417934117742244, generated pi from shear, differing from original stress-free b_end=.002946499991410212.
- q=+.005,kappa=+.2 => b_end=.0030257441516673904, s/H_end=.0006310738985269642.
- q=+.005,kappa=-.2 => b_end=.0028578381432722696, s/H_end=.0005135624238729375.
- q=+.01,kappa=+.2 => b_end=.005967298522706553, s/H_end=.0012032345816972113.

Ten full cases x501 mean-redshift nodes exported: 5010 physical background rows, source-bound total energy density, pi_s and pi_x,y,z (SI J/m3), b,s,H, perpendicular/longitudinal metric and proper time, and Hamiltonian residual. Maximum sampled relative constraint residual 6.66134e-16.

Validation evidence:
- Independent mpmath75 exact angular integral vs NumPy GL64 for 12 b,kappa pairs: max abs M=4.44e-16, max abs P=5.26e-16.
- Native rei_microphysics::axbi_stress_background opt-in Rust source, 32-point independent Gaussian quadrature and RK4 1024 steps: 10 q,kappa endpoint parity with Python DOP853 max |delta b|=1.45837525e-14; max |delta(s/H)|=2.10400138e-14; max relative proper time=7.556178e-13. Actual native Rust tests 7 PASS. Native library module exported, NO adoption in historical axbi_driver.rs.
- New Python tests 18 PASS: nonnegative W, initial pi=kappa/15, dM/db=-6P, stress/radiation positivity, Hamiltonian constraint, exact zero FLRW, signed source control, angular quadrature and vector RK4 parity.
- Native local Wolfram Engine15.0.0+xTensor1.3.0 eight exact zero tensor residual groups: pi trace-free, shear trace-free, sigma:pi=6s*pi, sigma norm, photon null and screen. Wolfram15.0.1 cloud exact initial pi ratio and dM/db=-6P.
- First test falsely assumed min W>=.75 for negative kappa; the actual restricted family bound is >=.5. Corrected the test without modifying the model or an externally locked physics threshold.

Optimization: 10-case fused NumPy vector RK4 with GL16 angular and 128 time steps median .0384 s, max |delta b| 1.795e-12 against DOP853 and max relative t 2.17e-11; 10 individual DOP853 median .1460 s. Actual thread 2/4 DOP853 .1695/.1738 s, so parallelization is slower on this fixed CPU workload. Vectorization is an empirical producer, not exact global numerical error enclosure or actual HII chemistry speedup.

## Native REI integration boundary

Actual REI crate exports opt-in AxbiInitialStressBackground with original Cosmology, source q whitelist and separate kappa. The old AX03 native stress-free background, chemistry driver, all previous trial/checkpoint identities, source radiation/opacity and signed completed ionization histories remain untouched. This new module does not automatically supply ionizing photoevents/thermal source; AX11/AX12 and full scientific admission remain unresolved.

For future use, create a new explicitly named source scenario with q,kappa, new source/checkpoint identities, matching short-step SI proper-time clock, exact physical Killing photon transport and actual CMB/ionizing radiation stress coupling. The conditional collisionless cosmic Omega_r reference alone is not a rigorous bound on the full coupled photon anisotropy. This branch is not an observational constraints/publishability claim.

Literature: Ivanov (1981) DOI 10.1007/BF00898394; Lee, Nungesser and Tod, General Relativity and Gravitation (2020), DOI 10.1007/s10714-020-02699-7; both support research context for homogeneous Einstein–Vlasov but do not independently certify this numerical implementation or new astrophysical fit.
