# BASS → REI IGM: original S0 photon first-scattering Thomson gain

## Owner, scope, conventions

This is one BASS-owned independent source-prescription-matched photon transport unit on the archived REI F08 S0 FLRW/Bianchi histories. It does not rerun the REI Rust ionization IVP, replace its spectral-state solver, self-consistently solve Einstein's equations, or calculate an observed CMB map. The original F08 scientific admission is HOLD.

Original S0 uses 0.05 initial photons/H plus continuous isotropic birth at 5e-15 photons/(H s), exactly monochromatic at 13.7 eV. Original normal proper time is 0..1e13 s; this is NOT current cosmological z=0. Hubble rates: Bianchi I (1.01,0.99,1.00)e-14 s^-1; comparison FLRW 1e-14 s^-1. Metric signature (-,+,+,+), ds²=-c²dt²+sum a_i(t)² dx_i², a_i=exp(H_i t). Comoving electrons and neutral atoms; original c=2.99792458e10 cm/s; sigma_T=6.6524587051e-25 cm².

The archived paired curves contain 16000 accepted physical epochs, 22 fields including x_HII, x_HeII, x_HeIII, temperature, photons per H, photon-energy per H, absorbing events, guard number/energy. The independently archived electron density gives 16001 rows. At original t_i, n_HI(t_i)=n_H(t_i)[1-x_HII(t_i)] and n_e(t_i)=n_H(t_i)[x_HII(t_i)+0.083(x_HeII(t_i)+2 x_HeIII(t_i))]. Cross-check across 16000 rows: relative electron agreement <=3.34e-16.

## Exact null rays and H I source photoabsorption

For spatial Killing direction b_i at original birth time t_b, sum b_i²=1, the exact prescribed diagonal Bianchi I characteristic obeys:

R(t,t_b,b)=sqrt(sum_i b_i² exp(-2 H_i (t-t_b))),
E(t)=13.7 eV × R,
n_i(t)=b_i exp(-H_i(t-t_b))/R.

Thus all true original-injection photons at 0<=t_b<=t<=1e13 s must have E>=13.7 exp(-1.01e-14×1e13)=12.383882550536338 eV. This is an exact consequence of frozen S0 source energy and positive prescribed expansion, not a numerical approximation or an observed spectral bound.

Original frozen Verner H I ground-state cross-section, fit cutoff Efit=13.60 eV (distinct from binding 13.598434599702 eV):

sigma_HI(E)=0 for E<13.60 eV;
sigma_HI(E)=5.475e4 × (x-1)² × x^(2.963/2-5.5) × (1+sqrt(x/32.88))^(-2.963) × 1e-18 cm² for E>=13.60 eV,
x=E/(0.4298 eV).

This formula is directly transcribed from archived original Rust AtomicProvider::reference (SHA256 b0b572d3940a7a1f740e09d5f43c60236ec61511e8bdbcc68e60395ec7e107d3). Original He I/He II thresholds exceed birth 13.7 eV and the photon only redshifts, so only H I photoabsorption is active. Photon HI-survival S_HI=exp(-∫birth^t c n_HI(u) sigma_HI(E(u)) du). Absorption is integrated over the positive-energy characteristic, splitting the cutoff at Efit exactly; the endpoint uses the ionizing one-sided limit to avoid arbitrary floating-point behavior at a discontinuity. All original n_HI,n_e samples are linearly interpolated, not modified.

For an exactly-once Thomson event at observer-local source time t, upstream no-Thomson-scatter survival is S_T=exp(-c sigma_T∫birth^t n_e(u)du).

## Positive Thomson 3×3 moment and Stokes gain

Use original source birth measure per H:
dN_src=[0.05 delta(t_b)+5e-15 1_(0<t_b<=1e13)] dt_b dOmega_b/(4pi).

Let Ue=∫ E(t) S_HI S_T dN_src [eV/H], and M_ij=∫ E(t) n_i(t)n_j(t) S_HI S_T dN_src [eV/H]. M is positive semidefinite, tr M=Ue. For the outgoing physical direction n and right-handed screen (e_theta,e_phi), the local cold-Thomson energy collision gain is

J_I=(3 c sigma_T n_e/(16pi)) [Ue+n_i M_ij n_j],
J_Q=-(3 c sigma_T n_e/(16pi)) [e_theta M e_theta-e_phi M e_phi],
J_U=-(3 c sigma_T n_e/(8pi)) e_theta M e_phi.

Units of J are eV/(H s sr); P/I=sqrt(J_Q²+J_U²)/J_I. Exact angular integral ∫J_I dOmega_out=c sigma_T n_e Ue. Positive coherency requires J_I>=sqrt(J_Q²+J_U²). For isotropic FLRW, M=Ue I3/3 and Q=U=0; a nonzero isotropic result is a numerical error, not physics. The incoming angular source uses positive Gauss-Legendre μ and uniform φ; it preserves the isotropic second moment. Outgoing 16×32 numerical sky cells are distinct from incoming integration.

This is an INSTANTANEOUS LOCAL FIRST-SCATTER GAIN, not the final polarization an observer receives after scattered photons propagate and interact. It is an energy-weighted first-scatter source, not a probability distribution, an all-orders CMB solution, a real observation or a full Einstein–H/He–photon coevolution.

## Hostile audit, source difference and limits

The original archived F08 photon_n already includes lower_guard_n, and photon_u_ev_per_h includes lower_guard_u. Adding guard twice is invalid; the comparison code explicitly avoids this. Source-image 10 eV lower grid cells can be populated by repeated remapping of finite-energy-bin populations in archived Rust paired_runtime.rs. The archived F08 S0_BI final lower_guard_n=0.0010016543797005872 per H, 2.0004754242263265% of the owner photon_n=0.05007081654542054 per H, despite exact real S0 E>=12.38388 eV. This is a scenario-specific spectral-support fidelity defect in the discrete representation. It is NOT an NG1–NG7 strong no-go for the entire solver or an automatic reason to invalidate otherwise separate conservation checks.

Our independent continuum characteristic at final t gives photon_n=0.047001270459869876/H, whereas original F08 owner gives 0.05007081654542054/H: -6.1304094826698075%. At final, HI gamma differs from original +3.535666311697683%. These differences are not certified as solely caused by lower-guard leakage or by a single implementation issue. Source prescription, H/He history and atomic fit match, but the full photon discretization/closure differs. No new ionization/Einstein IVP or full physical model-error bound was obtained.

Research status: source-conditioned derived/verified and numerically checked; distinct-author referee NOT_RUN, same-author hostile checking applied. REI central 28/88 reported (delta0), REI working 33/88 reported (not additive), BASS upper 9/15 scoped/source-mapped (full complete count unresolved, delta0), original F05 [160,161] blocked, F09 external atomic source-domain blocked, original F08 admitted HOLD.

Primary references: Verner et al. 1996 ApJ 465 487 / arXiv:astro-ph/9601009; Fleury Pitrou Uzan 2015 PRD91 043511 / arXiv:1410.8473; Pontzen Challinor 2007 MNRAS380 1387 / arXiv:0706.2075.
