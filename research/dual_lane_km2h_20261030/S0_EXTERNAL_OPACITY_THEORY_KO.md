# KM-2H S0 | FLRW HYREC-2/CLASS 이온화율을 사용한 *조건부* Einstein–Bianchi I 편광 Thomson 응답

Date 2026-10-30. Immutable parent: BASS Draft PR282 HEAD `0815ff69fb8be7123deb04a09fc54f15fbf6edd1`, its physics parent PR279 `b7faa761af032c68b86aec0ae30b61b817171669`. Original physical BASS KM2A/C/D/E/F/G git blobs and original polarized P8 ray data must remain untouched. Original user HYREC-2 ZIP SHA256 `f0b8bba1547ae9da83a0e663f57056884c689683396e1cf9a58bee1904040ac0`, CLASS ZIP `d1b2e1ce2b49de472e2cca9a327dc51c351e75bc0a2ad37d2e6538df76b289b7`. FLRW 1600-row source table Git blob from PR282, SHA256 `7f2c47c70dfab95e9ababed481db2c8d78429c0402ba1a85faeccb73df14d4da`. Confirm literal source bytes before computation. Top DAG **9/15**, 21 edges, `KM2=PARTIAL`, new upper completed=0; no merging/production.

## Scientific question and domain

For original full polarized 2×2 (real P8) Bianchi I rays and original self-consistent Einstein H/shear/cold baryon common velocity, how do external *original-source-generated* FLRW electron histories modify directional Thomson optical depths, photon anisotropic stress and gravitational shear sourcing relative to the identical-IC frozen electron fraction? Compare two source histories, HYREC-2 vs CLASS HyRec2020, but do **not** call them different atomic models (they share C source); the scientifically dominant contrast is time-varying ionization vs frozen ionization. No cosmological inference or observationally realistic matched universe is claimed.

### Explicit units and species assumptions

Metric (-,+,+,+), Λ=0. Original `u=t/Tstar` and real P8, normal ray screen, quadrature, Einstein equations and cold baryon fourforce are unchanged. The FLRW table uses `z`, `x_e=n_e^{free}/n_H`, with `n_H` all hydrogen nuclei, CLASS `H` in 1/Mpc and `κ'_conf` in 1/Mpc. Original HYREC-2/CLASS native outputs use matched FLRW h=.6735837, Omega_b=.0494142797907188, YHe=.245, no reionization. Interpolation of xe only supported at `900<=z<=1200`; `T_m` saved as diagnostic, not used to infer thermal pressure or Compton frequency energy redistribution.

The **synthetic initial BASS cold baryon** has `R_b0/rho_gamma0=3`, `κ=0.003` and original photon seed and constrained electron/baryon velocity `beta_b0=-q_gamma0/R_b0`; these are not the CLASS total stress-energy nor CLASS cosmological matter normalization. Define `z_ref=1200` and *volume-redshift proxy*, **not directional observed redshift**:

`1+z_vol(u)=(1+z_ref)*zeta(u)^(1/3)`, with `zeta(u)=n_lab,b(u)/n_lab,b(0)=det A(u)`.

Choose `Tstar=H_BASS(0) / H_CLASS_phys(z_ref)` so only **initial normal H** matches CLASS. Here `H_CLASS_phys(z) = H_CLASS_1/Mpc(z)*c/Mpc_m`. Then `rho_unit = κ c^2/(8πG Tstar^2)` in J/m³. Define `M0=R_b0/gamma0`, `mu_H_mass=m_p+m_e` (hydrogen mass with binding energies explicitly neglected), `YHe=.245`:

`n_H_rest(0) = (1-YHe)*M0*rho_unit/[gamma0*mu_H_mass*c²]` [m^-3].
`n_H_rest(u)=n_H_rest(0)*zeta(u)*gamma0/gamma(u)`.
`n_e_free_rest(u) = x_e^{FLRW}(z_vol(u))*n_H_rest(u)`.
`nu_rest(u) = n_e_free_rest(u)*sigma_T*c*Tstar` (dimensionless BASS normal proper time).
`D_q=gamma(1-beta_b dot n_q)`, `d tau_q/du=nu_rest D_q` (original normal-frame P8 Thomson ray factor).

For pressureless bulk stress, partition baryon total energy fractions at each epoch into charged-electron `f_e=(1-YHe)x_e*m_e/(m_p+m_e)`, charged-proton `f_p=(1-YHe)x_e*m_p/(m_p+m_e)`, neutral hydrogen `f_H0=(1-YHe)(1-x_e)`, neutral He `f_He0=YHe`. Fractions sum exactly 1 within floating point and positive; ion four-current `j=e(n_p_free-n_e_free)U` cancels, **total** electron+proton count of each atom is still in neutral H after recombination, not lost. This partition neglects binding energy (~13.6eV per H atom) and relies on externally specified neutralization without reaction-energy evolution. All species are *ideal infinitely momentum-locked* and have common U even when neutral, which is a model assumption, not a solved rate. Collision still acts **only on free electrons** and total baryon recoil remains `-F_gamma`. Field-theoretic energy source from changing ion fractions is externally imposed; no solved species reaction master equation, entropy or chemical heating. Do not claim each species is separately conserved with zero reaction source.

## Structural invariants and tests

Parent Einstein–Bianchi I equations:
`H'=-κ(rho_tot+p_tot)/2-sigma²`;
`sigma'=-3H sigma+κ pi_tot`;
`C_H=3H²-κrho_tot-sigma²`, `Q_tot=q_gamma+q_b=0` at initial time. The original linear collision and stress give independent raw quadrature 4-force gap `deltaF=F_raw_P8-F_cov`, hence `C_H'=-κ deltaF0`, `Q'_tot=-(4HI+sigma)Q_tot+deltaF_spatial`. Time-varying *externally specified* nu(u) multiplies collision but introduces no extra photon stress 4-force by itself. Euler baryon rest mass remains conserved even when ionization changes.

Required physical contrast at fixed photon initial data and constrained Einstein initial state: HYREC xe(z_vol), CLASS xe(z_vol), frozen HYREC xe(z_ref); same Tstar and same initial zeta=1. Run ntheta=12/16, 5 epochs and independent 24-node time balances, directional tau_q, actual photon anisotropic pi, sourced sigma, H and electron density. Fail closed for z_vol outside source support, negative/out-of-range xe, any original source SHA mutation, bad positivity, nonzero charge-current beyond tolerance. Record original P8 finite angular quadrature gap and two-grid observed error; no certified angular continuum bound.

### Required hostile review/claim ceiling

The initial baryon number density inferred from the synthetic BASS κ and H calibration differs from CLASS FLRW n_H(z_ref) by order unity, expected approximately 5.74×; **compute and print this ratio**, never claim CLASS-universe baryon abundance. CLASS H matches only at u=0; calculate later H_BASS/H_CLASS(z_vol) mismatch to illustrate the mismatch. FLRW xe(z) assumes isotropic homogeneous radiation and thermal history; importing xe by z_vol is an externally prescribed microphysics sensitivity test, not a solved anisotropic recombination model, not a thermal/spectral Boltzmann solver, not prediction of real CMB observables. Distinct-author R6/C9 NOT_RUN. Prefer one constructive physical run + one bounded hostile self-audit over more meta gates.

**Stop** after S0 theory, S1 real physics data/code and S2 scoped tests, plots, report, Git Draft PR, real backup receipts and one handoff. Keep top `9/15`, KM2 `PARTIAL`, `new_upper_completed=0`, `production_ready=false`, `merge_ready=false`, `auto_next=false`.

**Literature:** Lee & Ali-Haïmoud, Phys. Rev. D 102, 083517 (2020), doi:10.1103/PhysRevD.102.083517 (FLRW recombination effective four-level atom); Ma & Bertschinger, Astrophys. J. 455, 7 (1995), doi:10.1086/176550 (baryon–photon Thomson), CLASS thermodynamics source and HYREC-2 original code attached by user. No Bianchi model claim imported from these papers.
