# BASS Type II correlated redistribution and outer-band matching, 2026-11-19

Authority: source parent PR341 SHA 55aa1a61ac66019f0901dd2cb02ddfdcbb5fca9c. New Draft PR342. Signature (-,+,+,+), h=2πħ, c and k_B explicit. All changes are confined to the research/typeii_correlated_outer_20261119 directory. Production solver/main/parent are preserved.

## Scientific statement and model

The microscopic conditional angle-frequency law is built from the Maxwellian reduced line-of-sight atomic velocity u, a finite Lorentz absorption profile L_a(x-u), and coherent outgoing frequency in the atom's rest frame. In dimensionless Doppler units, conditional on incoming x and scattering cosine μ, outgoing x has mean x+(μ−1)u−ε_r(1−μ) and conditional variance (1−μ²)/2, with recoil ε_r=hν0/[m_H c² sqrt(2k_B T_m/(m_Hc²))]. The dipole phase is 3(1+μ²)/4 per normalized solid angle.

This is an idealized Hummer-II-inspired coherent atom kernel; it is NOT the exact full angle-dependent Hummer R_II or polarized frequency-redistribution operator. A source-explicit reversible pair correction symmetrizes the finite raw transition flux using the finite Wien weights π_(a,j) ∝ w_a ν_j² Δν_j exp[−h(ν_j−ν0)/(k_B T_m)]. This supplies positive rates, normalized photon number and stimulated Bose thermal reciprocity, but changes the original raw scattering kernel. Original numerical conditionals are not advertised as an exact microscopic R_II.

For fixed T_m=3000 K the six-direction ×36-frequency conditional generator has shape 216×216. Raw joint versus independently factorized outgoing-angle/frequency L1 difference is 1.228292640440575. Its relative column closure residual is 3.2157126105457025e-16 and Wien pair balance defect 1.8711605193568036e-16. The incident x=+2 conditional outgoing finite-bin mean is 2.125 for μ=+1 (center of the containing frequency cell), 0.0153541435371 for μ=0, −2.0063926874 for μ=−1. This is a real correlation at single scattering, not a directly predicted cosmological observable.

Original Type-II source inputs at z_mean=1100: H_n=4.488813430160247e−14 s−1, T_m=3000.745332620248 K, fixed neutral 1s tracer n_l=253341572.44286457 m−3, finite n≤3 ionization fate p_ion=7.247978213593499e−8. The source-dependent opacity, Doppler frame factor D, original directional frequency drift κ, Hubble, trace 1s density, T_m, and p_ion vary during Δτ_H=1.5e−4. The angular-frequency kernel shape is frozen at the initial T and angular configuration: this is a declared approximation, not the full time-varying correlated kernel.

The photon number evolves on the original parent normal-hypersurface measure, using source D/H and the advected angular labels/Jacobian. Internal ±20 Doppler-width core fluxes are *tracked*, not absorbed when the outer domain is wider. Scattered photons beyond the true outer band are counted as red/blue terminal channels, and a separate tagged-ionization channel is counted. All terminal categories sum to one within the actual numerical ledger tolerance. Gross core↔outer crossings may exceed unity because individual photons can cross repeatedly.

## Actual matched-time 512-step results

| outer halfwidth | remaining | red terminal | blue terminal | tagged ionized |
|---|---:|---:|---:|---:|
| 20 Doppler widths | 4.20802239652e-11 | 0.276896662993 | 0.268991480237 | 0.454111856914 |
| 40 Doppler widths | 0.0375632902748 | 0.0164856683950 | 0.000895936773369 | 0.945055104636 |
| 80 Doppler widths | 0.0541647920460 | 0.000254462450325 | 2.27118428310e-25 | 0.945580745879 |

The matched 40-width source has gross core→outer transfers 1.706067223478205 and outer→core returns 1.6613247214377551. With a 40-width boundary, the difference in tagged ionization of correlated versus factorized source kernels at 512 steps is −4.03776012625201e−10: the strong raw conditional correlation is washed out in this highly optically thick, nearly isotropic terminal statistic. This does not imply a general negligible effect.

The source 64→128→256→512 time-step tagged-ionization differences are 7.30544480546e−4, 3.64382984128e−4, 1.81991565081e−4. The evolved-minus-frozen difference at matched 512 steps is −6.01420333737e−5, smaller than the remaining timestep change; it is not a precision-resolved physical source variation claim. Even ±40 versus ±80 outer-boundary ionization differs by +5.25641242477e−4 at fixed resolution. No global escape or continuum-time exact answer is established.

## Independent verification

The static correlated generator was solved by sparse Krylov matrix exponential and independent BDF, agreeing to 1.39484604422e−12 maximum state-vector absolute error. Backward Euler errors with 4,8,16,32,64 uniform steps decrease 8.39417e−6, 4.26870e−6, 2.15278e−6, 1.08107e−6, 5.41711e−7, verifying convergence on the finite source matrix. The raw finite inside-plus-outer scattering conditional probabilities sum to unity within 1.80691295260e−9 absolute defect. All original protected BASS 9/9 Git blobs are source-locked.

One bounded same-author hostile verification identified the following physical/implementation limitations: the thermodynamic symmetrization changes microscopic scattering weights; initial kernel shape is frozen while sources evolve; an internal core absorption boundary destroys true returns; the time-error budget cannot validate differences below ~1e−4 in this run; the photon–atomic-gas energy reservoir is not dynamically closed. Six malformed kernel inputs were rejected. No native subagent or distinct-author blind referee was dispatched, and none is claimed.

## Preservation and gate

Stages M1–M4 are individually committed, pushed and read back to the source branch with separate Git archives and SHA256+ZIP integrity. The host backups are under /home/cosmosapjw/research_backups/bass_typeii_correlated_outer_20261119/. A single 4KiB write probe on a freshly created project directory under /mnt/extdrive/research_backups failed OSError ENOSPC despite filesystem capacity showing ~1.8TB available on fuseblk. The probe was not repeated, no unrelated files were deleted and no NTFS/FUSE mount settings were changed. New external backups are NOT VERIFIED.

Admit: correlated source-conditioned finite kernel, thermo-conservative static Markov construction, moving source conditional tagged photon runs and explicit core return, bounded convergence diagnostics. Hold: the full R_II kernel, wing/global escape, self-consistent atomic levels and recombination, actual CMB visibility, complete polarized Einstein–Boltzmann transfer and production dispatch. BASS upper DAG 9/15 scoped/source-mapped, new full upper nodes 0, historic StageII 11/11 current canonical unproven, Join J1 0/2 FULL PASS HOLD. production_ready=false, merge_ready=false, auto_next=false.

Next science unit: SOURCE_MATCHED_FULL_RII_KERNEL_AND_OUTER_SPECTRAL_BOUNDARY_VALIDATION. Benchmark an actually sourced full angle-frequency redistribution kernel including thermodynamic reversibility, time-dependent line-shape, and outer wing reentry until the truncation dependence is controlled. Independently recover StageII canonical evidence. Do not enlarge scope through repeated process-only audit.

Primary literature: Hummer (1962), MNRAS 125,21; Rybicki (2006), ApJ 647,709, arXiv:astro-ph/0603047; Hirata & Forbes (2009), arXiv:0903.4925; Dijkstra (2017), arXiv:1704.03416.
