# KM2K S0 | Directional frequency-resolved *escaped* Lyα spectrum on the real KM2J Einstein–P8 IVP

**2026-10-31 KST. Single bounded unit.** Immutable parent BASS KM2J Draft PR291 HEAD `63147c01f1b1fd3f0cf698c919db25d9bd2ef80b` with independently integrated four Einstein/P8/chemistry IVPs, 164 epochs, conserved synthetic grey chemical binding exchange. The unrelated CE1AK Vlasov branch is neither rebased nor merged. Original KM2F–J sources and initial P8 sky are read-only. Upper BASS DAG **9/15 (21 edges)**, KM2 **PARTIAL**, +0 upper nodes.

## What is being computed and what it is not

Build a genuinely **frequency-resolved tagged Lyα escaping-photon distribution** on top of two ACTUALLY re-integrated **KM2J full** Einstein–Bianchi-I/fully polarised P8/Peebles IVPs with grid nθ=12 and 16. The emitted line photons are an **energy-tagged subset** of the total grey chemical radiation already in KM2J: they are **NOT added again to P8 stress, Einstein, or recombination rate**. Thus there is no energy double count. This is *post-Sobolev escaped-line propagation*, NOT resonant Lyα radiative transfer through the highly opaque core. No claim of line trapping/scattering/recoil/frequency redistribution, nonthermal photo-excitation feedback, thermal first-law closure or observational cosmology. Unlike KM2I and KM2J, this new unit actually resolves the frequency distribution of the outgoing escaped-line component and its anisotropic geodesic redshift.

## Definitions and derivation

Conventions: metric (-,+,+,+), normal-proper `u=t/T_*`, `T_*=218601.80677272403 Julian years`; retain c, h_P, k_B, e and SI units. From the *same live KM2J state*, normal direction `n_a(u)`, normalized BASS `H(u),σ_ij(u)`, baryon velocity `β_b(u)` and `γ_b(u)`. Define frequency `y=ln(ν_normal/ν_α)`, `ν_α=c/λ_α`, `λ_α=121.567 nm`; normal-frame emitted central frequency `ν_em(n)=D_b(n)ν_α`, `D_b=[γ_b(1−β_b·n)]^(-1)`. Along a source-locked original photon geodesic `h_∥(u,n)=H+σ_ij n_i n_j` and `dy/du=−h_∥`; electron tilt does not alter the collision-free photon geodesic. Define `R_i(u)=∫_0^u h_∥(v,n_i(v))dv`, `q_i=y+R_i` (constant for free photon), and `K_i(q,u)=ν I_ν` per normal solid angle and log-frequency. **Collision-free scalar spectral** intensity obeys `dK_i/du|q=−4h_∥ K_i + j_i(q,u)`. Accordingly, exact characteristic Green function for initially zero tagged line field:

`K_i(y,u)= ∫_0^u dt j_{α,i}(t) exp[−4(R_i(u)−R_i(t))] G(y−ln D_b(t,n_i(t))+R_i(u)−R_i(t);σ_D(t))`,

where `G(y;σ)=(2πσ²)^(-1/2)exp(−y²/(2σ²))`, normalized by `∫G dy=1`; `σ_D=√[k_B T_m/(m_H c²)]` is the 1D Maxwell Doppler standard deviation in log-frequency to leading nonrelativistic order, `m_H≈m_p+m_e`; finite Doppler thermal profile yes, redistribution/recoil no. This is an initial-value frequency-resolved **linear transport integral** with actual time-dependent anisotropic geodesics, not a synthetic static spectrum.

KM2J original chemical rest-frame energy release is `s_chem=−M0 η ζ x'_e` in BASS stress-energy units per normal u, `η=(1−YHe)χ_H/[(m_e+m_p)c²]`, `χ_H=13.6eV`. The finite original P8 angular quadrature `n,w` has source-locked four-moment grey chemistry emissivity `j_grey,i=trace angular_grey_emission(n,w,β,s_chem)`, `∑_i w_i j_grey,i(1,n_i)=s_chem(γ,γβ)` to floating accuracy. Peebles effective-three-level net downward-channel branching `b_α=Λ_α/(Λ_α+Λ_2s)`, `Λ_2s=8.2245809 s^-1`. **Scoped branching approximation:** the tagged escaped line energy at each event is

`j_{α,i}=f_α j_grey,i`, `f_α=(E_α/χ_H) b_α`, `E_α=10.2 eV`, `0<f_α<1` when `x'_e<0`.

This energy partition is a Peebles-level *effective net* escape heuristic, not a frequency-dependent atomic population solver. The remainder stays as the preexisting untagged grey photons. Source normal four-momentum `∑w j_{α,i}(1,n_i)=f_α s_chem(γ,p)`, and the tagged integrated spectrum's incoming energy equals exactly the fraction of the pre-existing grey source up to inherited angular quadrature errors. **Do not add a new independent T^{μν}_line to the gravitational total.** This creates an internally non-duplicated diagnostic of a physically motivated spectral component.

Radiative observables at each u are actual `ρ_α(u)=Σ_i w_i(u) ∫K_i(y,u)dy`, `q_{α,j}(u)=Σ_i w_i n_{ij}∫K_i dy`, centroid `<y>`, variance `Var(y)=<y_c²+σ_D²>−<y>²`, red wing fraction `P(y<−0.01)`, angular `Q_{ij}=<n_i n_j>_K−δ_ij/3`, plus 5 frequency histograms for each grid/scenario. Use time-order accurate 8-point GL quadrature over 40 intervals and an analytically integrated 8-point Lagrange basis for `R_i(t)`, rather than arbitrary semi-Lagrangian diffusion. The frequency histogram bins are coarse aggregated CDF integrals of each physical Doppler Gaussian; centroid and variance are computed **without** histogram discretization.

**Two physical transport scenarios on the identical dynamical geometry/emission**: (A) `h_∥=H+σ:nn`, and (B) `h_∥=H` as a counterfactual isotropic-redshift-only propagator. The latter retains the same original anisotropic directions, Doppler and source, not a distinct FLRW Einstein solution. Meaningful differences isolate anisotropic photon frequency drift, not the source itself.

## Falsifiable quantitative checks and boundary

1. Real source guard for KM2J, historical original Einstein/P8 Git blob identity and original full IVP initial ray/hash identity; no prior file modifications.
2. `K(u=0)=0`, `j_α≥0`, `h_∥>0`, `∫Gdy=1`, `0<f_α<1`, norm of `n_i` unity, all physical photon weights positive.
3. Four-moment incoming `j_α` equals `f_α F_chem` with the original *finite* P8 ray grid. `ρ_α` is a tagged subset and is not re-added to Einstein.
4. **Static homogeneous analytic reference:** h>0, injection j0>0 at y=0 with σ_D→0, `K(y,u)=(j0/h) exp(4y)` for `−hu<y<0`, and `∫Kdy=j0(1−exp(−4hu))/(4h)`; verify with independent quadrature (Wolfram symbolic integral already performed in this session).
5. Actual GL12/GL16 physically distinct spectral response from shear-vs-H-only controls; compare `ρ, q, <y>, Var(y), F_red`, and 5 frequency spectra. Nonzero bounded anisotropic geodesic frequency effect **without** claiming true resonance feedback.
6. Verify histogram energy sum vs direct Green function (including Gaussian tails), exact positive source fraction, finite GL8 vs GL12 time integration on same original GL12 source where practical, constraints of original Einstein/P8 from inherited KM2J (not modified), 41 spectral epoch rows/scenario, 6 science PNGs, source-data CSV and strict no-false-production labels.
7. Native subagent NOT_RUN unless actual delegation tool exists; self hostile audit separately verifies saved physical/spectral energy and radiative inequalities.

Primary literature context: Hirata & Forbes, **Physical Review D 80 023001** (2009), DOI 10.1103/PhysRevD.80.023001 (arXiv:0903.4925) explicitly shows real Lyα resonant scattering, recoil, absorption and spectral feedback require a more complex Fokker–Planck/atomic-level system; Seager, Sasselov & Scott **ApJ 523 L1** (1999) DOI 10.1086/312250; Lee & Ali-Haïmoud **PRD 102 083517** (2020), DOI 10.1103/PhysRevD.102.083517 for modern recombination fidelity. This pilot deliberately does **not** claim their accuracy.

DAG lock **upper 9/15**, `KM2=PARTIAL`, `KM2K_SCOPED=0/1` pending actual execution. Production HOLD, merge HOLD, auto-next false, STOP after this bounded physical unit.
