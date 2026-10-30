# BASS KM-2G S0: neutral e–p cold baryons × original full polarized photons × Einstein–Bianchi I

Date 2026-10-30; exact read-only parent Draft BASS PR278 HEAD `29ee9114856d493dac2f5e8328c145050169c13e`. Existing physical parent source `research/dual_lane_km2f_20261030/einstein_bianchi.py` Git blob `457790df7aba6d82326ac6f3be5814851b970b1d` and original `KM2A/C/D/E` photon/Thomson/geometry Git blobs unchanged. BASS upper DAG 9/15, KM-2 PARTIAL. Next bounded science unit selected: **KM-2G cold exactly charge-neutral hydrogen plasma in the infinite electron–proton Coulomb momentum-lock limit**, with physically dimensioned opacity and explicit ion/electron inertia. Research selected R2/R5/R6/R7/C5/C6/C7/C9/C10; no whole-DAG promotion. Native subagents not exposed, self-hostile referee one bounded pass.

## Source decisions and exact physics assumptions

Metric signature (-,+,+,+), c retained in dimensionalization; time u=t/Tstar. Original normal-frame photon P8 Hermitian S+iA, positive quadrature, momentum coframe A and 5-component tracefree shear remain unchanged. Λ=0. **Bianchi-I spatially homogeneous** normal frame, electron and proton proper densities exactly equal n_e*=n_p*=n*, both with identical timelike four-velocity U^a=gamma(1,beta). The original photon collision interacts ONLY with electrons; proton mass supplies almost all recoil inertia. This is the ideal Coulomb-locked (zero-slip) limit, **not** a finite-conductivity Maxwell-Vlasov electron-ion solver. No ion thermal pressure, recombination, helium, neutral hydrogen, photoionization, electron heating or frequency-redistributing Compton source. It is also not an observationally calibrated Universe.

Published context to reuse, not silently transplant gauge-dependent perturbation formulas: Ma & Bertschinger (1995), ApJ 455 7-25, doi:10.1086/176550, arXiv astro-ph/9506072; Hannestad (2000), *On the coupling between different species during recombination*, arXiv:astro-ph/0008452; Pookkillath, De Felice & Mukohyama (2020), Universe 6(1) 6, doi:10.3390/universe6010006; Cyr-Racine & Sigurdson (2011), PRD 83 103521 doi:10.1103/PhysRevD.83.103521. These establish the baryon/electron-ion tight coupling construction in cosmological Boltzmann theory; the full nonlinear homogeneous Bianchi-I polarized implementation below is newly derived, not covered by those references.

## Mathematical construction

Let exact physical mass ratio r=m_p/m_e and mass fractions mu_e=m_e/(m_e+m_p)=1/(1+r), mu_p=r/(1+r). Total cold baryon normal frame stress T_b^{ab}=rho_b (1,beta)^a (1,beta)^b with rho_b=M_b zeta gamma, Q_b=M_b zeta p, P_b=rho_b beta beta^T. Electron and proton stress are **separately defined** by T_e=mu_e T_b, T_p=mu_p T_b. Electron and proton numbers: n_e*=n_p*=n_rest0 zeta gamma0/gamma, n_lab,e=n_lab,p=n_lab0 zeta. Thus total electric charge density and spatial current vanish identically: j^a=e(n_p* U^a - n_e* U^a)=0, for e>0. This algebraic neutrality constraint does not imply a dynamically solved electromagnetic field.

Photon original Thomson covariant fourforce F_gamma^a remains the KM-2F instantaneous source computed from full polarized ray stress and electron beta and rest opacity nu(u)=sigma_T c n_e*(u) Tstar. The original finite positive-quadrature P8 photon collision force F_raw may differ from F_cov; deltaF=F_raw-F_cov is **measured** and never projected away. Electron receives -F_gamma, proton zero Thomson direct. Introduce *internal Coulomb locking fourforce*, electron +mu_p F_gamma and proton -mu_p F_gamma; electron net F_e=(-1+mu_p)F_gamma=-mu_e F_gamma, proton net F_p=-mu_p F_gamma. All lie orthogonal to U because U_a F_gamma^a=0. Summing gives -F_gamma. These internal forces are ideal non-dissipative Lagrange multipliers for common p, not a finite-Coulomb-rate claim, and their magnitude is a new resolved species-level physical observable.

Each species satisfies the normal-time pressureless energy/momentum law with its own stress and net force:

    R_s' = -3H R_s -(H I+sigma):P_s +F_s^0,
    Q_s' = -(4H I+sigma)Q_s+F_s^sp,

where F_s is the **net force INTO that matter species**. The shared physical momentum p=gamma beta thus follows

    zeta'=-3H zeta,
    p'=-(H I+sigma) p-F_gamma^sp/(M_b zeta).

The original photon equation is untouched. The full Einstein source is rho_total=rho_gamma+R_e+R_p; P_total=P_gamma+P_e+P_p. The constraints 3H²=kappa rho_total+sigma² and q_total=0 are fixed at u=0 by beta_b0=-q_gamma0/R_b0, H0 positive. Dynamic constraint propagation retains the measured finite-angular force gap: C_H'=-kappa deltaF^0, Q_total'=-(4H I+sigma)Q_total+deltaF^sp.

### Dimensional closure missing from KM-2F

BASS source rho_gamma0≈39.01110262768746 is **dimensionless**, not an observed blackbody spectrum. Fix synthetic initial ratio R_b0/rho_gamma0=3.0 (same as KM-2F) and kappa=8pi G rho_unit Tstar²/c²=0.003. For physical ion+electron baryon mass m_b=m_p+m_e and Tstar seconds, the physical normalized energy scale is

    rho_unit = kappa c²/(8pi G Tstar²) [J m^-3],
    n_e*(0)=n_p*(0) = R_b0 rho_unit/(m_b c² gamma0²) [m^-3],
    nu0=n_e*(0) sigma_T c Tstar
       = R_b0 kappa sigma_T c/(8pi G m_b gamma0² Tstar).

No independent arbitrary nu0 once Tstar,kappa,R_b0 and the electron-proton mass are specified. For matched dimensionless KM-2F nu0=1.3 this determines Tstar≈5.7883065×10^7 yr; for Tstar=10^7 yr it gives nu0≈7.52479849, with the original photon source and Einstein constraints otherwise unchanged. These are **alternative synthetic scale normalizations, not recombination-epoch fits**; original bolometric ray data cannot specify photon spectrum, ionization history or measured baryon-to-photon ratio. Without those inputs, one cannot call this observationally realistic baryon physics.

The dimensionless matrix RHS is the parent EinsteinCoupledBianchi with M0 interpreted as **total e+p inertia**, not the electron-only mass, and its opacity nu0 **computed from the above SI relation**. New output must explicitly split electron/proton stresses, show electric current=0, forces/energy and partition, and produce actual independent Bianchi-I evolution at at least two Tstar values. Recompute ntheta12/16 physical five-epoch rows; compare shear sourcing, H, photon anisotropic pressure, optical depth, and force exchange with the previous source at matched t=0. No altered original KM-2F tests or source files.

Hostile referee tests: signs of internal exchange, electron/proton individual continuity, c/G/sigmaT dimensions, gamma0² factor (not gamma0), physical vacuum opacity limit, source tampering, Hamiltonian and momentum constraints at all epochs, observer geometry, exact neutrality and stiffness, cross-grid variability, honest stage code tests. A physically false option where photon recoil is divided by electron mass instead of total baryon mass must be caught by checking species net forces and total stress balance.

## Stop condition

S0 theory and sources, S1 executable scientific code and physical JSON/CSV, S2 independent hostile tests, finite-scope scientific report and exact hash-preserving package. GitHub Draft PR independently branched from PR278; Google Drive and Library stage checkpoints with actual receipts; Dropbox only if connector actually supports attaching the source. No automatic transition to temperature/recombination or Einstein-Boltzmann perturbation, no production promotion or merge. Upper count **9/15**, KM-2 PARTIAL, zero newly completed upper DAG nodes. One scoped physical subgate may close, nothing else.
