# REI AX03 initial shear + initial anisotropic stress: Einstein–Vlasov background

2026-10-15 KST. Direct coding/scientific research on the user's authorized Ubuntu. No local Codex and no exposed native subagents. Parent BASS C8 source commit f3f741d8731380f734c7c4e6679e87d6a5d3bff3. The authoritative original REI AX03 background family SHA256 is 46f818c2f9de890c72f71fa3cc70366b28c42ca0d65190bd905b6310023e7af0. This is an ADDITIVE initial stress research lane, not a change to the running cold reionization model or its checkpoint.

## Mathematical construction

Metric signature (-,+,+,+), no tilt, LRS Bianchi I:
ds^2=-c^2 dt^2+a^2 exp(-2b)(dx^2+dy^2)+a^2 exp(4b)dz^2;
Hperp=H-s, Hparallel=H+2s, s=db/dt, shear^i_j=diag(-s,-s,2s).
Anisotropic stress^i_j=diag(-DeltaP/3,-DeltaP/3,2DeltaP/3), DeltaP=Pparallel-Pperp.
Conservation + spatial Einstein differences yield
ds/dt+3Hs=(8piG/(3c^2))DeltaP.
This is not the stress-free AX03 decay law unless DeltaP=0.

Split the EXISTING rounded source Omega_r into collisionless fraction eta in [0,1] and remaining perfect isotropic fraction (1-eta). This avoids double-counting existing radiation. At zbar=20 choose initial angular distribution W(mu_ref)=1+A P2(mu_ref) with -1<=A<=2, P2=(3mu_ref^2-1)/2, W>=0 and angular mean W=1. This positive even distribution has zero initial momentum density, and its quadrupole is a separately selectable physically allowed initial stress, not an arbitrary post-hoc forcing function.

With conserved spatial Killing momenta and initial b_ref=0:
R^2=e^(2b)(1-mu_ref^2)+e^(-4b)mu_ref^2;
mu_now=mu_ref e^(-2b)/R;
M0(b,A)=<W R>, Md(b,A)=<W R P2(mu_now)>.
Energy density epsilon_A=3c^2H0^2 eta Omega_r M0/(8piG a^4) and DeltaP=3c^2H0^2 eta Omega_r Md/(8piG a^4).
M0(0,A)=1 and Md(0,A)=A/5, so DeltaP_ref/epsilon_r_ref=eta A/5. Initial q_ref=s_ref/H_FLRW(a_ref) and initial stress eta A/5 are independent physical initial parameters within the positive-distribution domain.

The SELF-CONSISTENT Einstein constraint and Vlasov shear source are:
H^2=H0^2[Omega_m/a^3+Omega_Lambda+Omega_r/a^4((1-eta)+eta*M0)]+s^2,
ds/dt+3Hs=H0^2 eta Omega_r Md/a^4.
With x=ln(a/a_ref), evolve b'=s/H, s'=-3s+H0^2 eta Omega_r Md/(a^4 H), t'=1/H. Crucially dM0/db=-2Md follows exactly from the ray energy R. Hence epsilon_A obeys d epsilon_A/dt+4H epsilon_A+2s DeltaP=0 and the explicit radiation-stress terms cancel in the derivative of the Einstein Hamiltonian constraint. The remaining mean Raychaudhuri derivative is
dH/dx= -[3H0^2 Omega_m/a^3+4H0^2 Omega_r/a^4((1-eta)+eta*M0)+6s^2]/(2H).
Wolfram15.0.1 checked the integrand dR/db+2 R P2(mu_now)=0, initial Md=A/5, angular W normalization and shear-stress algebra.

In the eta=0 limit the code EXACTLY returns the earlier source-frozen stress-free LRS background with s proportional a^-3 (within observed numerical tolerance), for any A. A=0 with eta>0 has initially zero anisotropic pressure but NONZERO subsequently if preexisting shear makes the massless distribution anisotropic. q_ref=0 with A nonzero produces new shear from zero via the Einstein equation.

## Numerical results: actual DOP853 and independent Rust

Original REI cosmology H0=67.4 km/s/Mpc, Omega_m=.315, Omega_r=9.2e-5, Omega_Lambda=.684908, a_ref=1/21, a_end=1/5, T_CMB0=2.7255 K. All times are elapsed SI proper seconds since mean redshift20. Extreme A=+/-1, eta=1 are deliberately a mathematical stress diagnostic, NOT observationally measured primordial CMB/neutrino distributions.

| q_ref | A | eta | b(zbar4) | s/H(zbar4) |
|---:|---:|---:|---:|---:|
| 0 | 0 | 0 | 0 | 0 |
| 0 | +1 | 1 | +0.000420548712 | +0.0002945800 |
| 0 | -1 | 1 | -0.000420663343 | -0.0002947592 |
| +.01 | 0 | 0 | +.005892916695 | +.001154643885 |
| +.01 | 0 | 1 | +.005883516261 | +.001144660158 |
| +.01 | +1 | 1 | +.006302382883 | +.001437461969 |
| +.01 | -1 | 1 | +.005464537835 | +.000851682439 |
| -.01 | +1 | 1 | -.005461241987 | -.000848225884 |

For q_ref=0, A=+1, eta=1 initial pi creates finite shear and a nonzero quadrupolar metric. For fixed q_ref=+.01, varying initial stress sign visibly changes shear and H. This is a controllable theoretical source-family sensitivity, not a fitted anisotropy likelihood.

Source-built deliverables: 17 signed/positive model cases x 501 log-scale nodes = 8,517 explicit table rows, including H,s,b,Hperp/Hpar, physical H/He nuclei density, isotropic REFERENCE CMB T0/a, epsilon_A, Pperp,Pparallel, DeltaP, pi_ab, Hamiltonian source residual and SI clock; 8,585 photon Killing energy/direction/Jacobian rows and SHA-256 source contract.

The original photon Jacobian was briefly written with a spurious exp(-3b) factor in an UNPUBLISHED trial. An exact Wolfram derivative gives dmu_current/dmu_ref=R^-3 (no extra exponential). The wrong values were excluded from the release; an exact negative-control witness with source hash is saved. All published 8,585 photon ray records now pass the correct derivative and number phase-volume invariance.

Actual Python physical/ODE tests: 21 PASS including W positivity, pressure tensor trace, stress conservation dM0/db=-2Md, Hamiltonian, independent Raychaudhuri derivative, q0+initial stress shear creation, stress-free parent model, signed q source, finite-radiation quadrature convergence and precision refinement. Additional 9 delivery tests and 7 native/CAS/evidence tests PASS: 37 NEW. Parent AX03 supplier33 and previous short-step29 also pass: total 99 Python tests across the full research stack.

Independent stdlib Rust solver separately generates Legendre64 nodes by Newton roots and advances the full coupled Einstein-Vlasov system with 4096 RK4 steps for 8 source cases. Against Python DOP853/Legendre128, max endpoint |Delta b|=1.321e-15, max |Delta(s/H)|=2.351e-15 and max relative SI clock difference=5.883e-13. Not a rigorous global error certificate.

Actual original rei_microphysics crate was compiled read-only as a path dependency in a distinct Cargo project. The opt-in source bridge reconstructs 8,517 Rust BackgroundPoint objects and validates their geometry snapshots with the original AX03 geometric representation. Five original eta=0 stress-free Rust sample comparisons have max H relative2.22045e-16 and max |Delta b|2.02e-14. Original REI driver still holds concrete AxbiBackground and does not automatically accept eta>0 coupled stress; the bridge is a typed basis, not native source activation.

Independent stdlib Rust CSV consumer validates all 8,517 Hamiltonian constraints AGAINST source parameters, exact pressure/energy normalization, trace-free pi, H/He nuclei positivity, volume and proper-time monotonicity. It rejects 5-percent corrupted H and an altered pi_parallel with exit code3, without mutating the source. Local Wolfram Engine 15.0.0 plus xTensor1.3.0 actually confirmed eight tensor zero identities including sigma.pi=2s DeltaP and shear^2/2=3s^2.

## Actual optimization and resource results

At 4096 source b values, GL64, same A=0.7, 3 warmed CPU medians:
- Individual Python moment quadrature 0.097715 s;
- fully broadcast vector 0.003344 s, 29.22x speedup, tracemalloc10,652,264 B;
- 128-b chunked vector 0.002701 s, 36.17x speedup, tracemalloc534,496 B.
Both vector representations agree exactly at tested double-precision samples. Chunking is the default recommended batched moment API to limit intermediates. Over 17 independent real DOP853 cases actual 1worker0.30959s, 2workers0.35714s, 4workers0.39968s. Threads are slower. All benchmarks are scoped to source moment evaluation or independent background-only ODE solutions, not the full native REI ionization solver.

## SCIENTIFIC STATUS and next integration boundary

This is an actual **Einstein plus collisionless massless Vlasov radiation** source model. It is self-consistent within the assumed homogeneous non-tilted geometry, positive initial W and free-streaming collisionless sector. It is NOT a complete self-consistent recombination/reionization Einstein-Boltzmann system with realistic photon collisions, neutrinos, ionizing background/gas anisotropic stress, primordial initial distribution inference or observational likelihood.

The source-frozen original AX03 driver cannot be used without modification for eta>0: AxbiBackground hardcodes stress-free s(a)∝a^-3, so a new native provider that evolves b,s and produces H(a) with stress is needed. The native C9 time-increment algorithm must use that NEW H(a,b,s); copying its old stress-free integrand would be physically wrong. Checkpoints/data created by the old binary must not be continued under the changed physical model. A new source/IC clock identity and explicit REI admission gate are required before native full H/He abundance histories are computed.

Source references: Dynamics of the spatially homogeneous Bianchi type I Einstein-Vlasov equations, arXiv:gr-qc/0512031; Ivanov (1981), Bianchi type I anisotropic cosmological model with a collisionless gas, DOI 10.1007/BF00898394. This is a model-specific constructive result, not a claim of primary theoretical novelty.
