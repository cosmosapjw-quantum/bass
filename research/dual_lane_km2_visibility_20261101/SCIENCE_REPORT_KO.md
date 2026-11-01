# BASS KM2 directional Thomson visibility and event-redshift bridge | 2026-11-01

## Identity and physical purpose

Authoritative frozen BASS KM2N Draft PR #297, HEAD `4137f942d2a95999f4e6627b71042e98f7afc1b7`; inherited original Einstein–P8–Peebles/tilted electrons and KM2L source at the *same* owner. Original outer CI S2 (`45733f4ca2c0250cc94b03...`), nested S2 (`8dd9258a3a50b6d0140c9305040c978f5a0790d907a8927769d3d27b5c63ab0d`), frozen four input NPZ SHA256 values in `SOURCE_MANIFEST.json`. 41 original source times on normal clock `u=t/Tstar` from 0 to 0.25, GL8 temporal quadrature at 320 nodes, original GL12/GL16 angular rays 288/512. No original Einstein IVP rerun in this calculation, no material source switch, no PR #307 CE1AS collisionless source transplant.

This is a **source-owned Thomson transfer visibility kernel** in the original early-recombination *conditional model*, not the source-weighted physical last-scattering distribution of the emitted Lyα photons and not the observed CMB visibility. A photon that exists at u=0 and follows a fixed original KM2L ray has an inhomogeneous Poisson collision hazard along that ray. Any new collision changes the direction, so this transfer Green weight is not a full multiple-scattering Monte Carlo distribution. It is the positive line-of-sight attenuation/gain kernel for a subsequent source function.

## Equations and conventions

Metric signature (-,+,+,+). Keep c, k_B, h_P and Tstar explicitly in physical inputs. The original source uses electron density from live Peebles `n_e=n_H x_e` and original tilted-normal collision rate

\[h_\alpha(u)=n_H(u)x_e(u)\,\sigma_T c T_\star\,D_\alpha(u),\qquad D_\alpha=\gamma_b(1-\beta_b\cdot n_\alpha) .\]

Here `D` is exactly the KM2N/KM2L original stored factor; the formula is not inferred from unrelated CE1AS or REI. Normal-clock optical depth and observer-relative survival are

\[\tau_\alpha(u)=\int_0^u h_\alpha(s)\,ds,\quad S_\alpha(u;U)=\exp[-(\tau_\alpha(U)-\tau_\alpha(u))],\quad g_\alpha(u;U)=h_\alpha(u) S_\alpha(u;U),\qquad U=0.25.\]

The exact local transport identity is

\[\int_0^U g_\alpha(u;U)du=1-e^{-\tau_\alpha(U)}=:P_{\ge1,\alpha}.\]

Conditional upon at least one event on that fixed ray, the event-time CDF is

\[F_\alpha(u)=\frac{e^{-[\tau_\alpha(U)-\tau_\alpha(u)]}-e^{-\tau_\alpha(U)}}{1-e^{-\tau_\alpha(U)}}.\]

The q-quantile target is \(\tau_\alpha(u_q)=\tau_\alpha(U)+\ln[e^{-\tau_\alpha(U)}+q(1-e^{-\tau_\alpha(U)})]\). Inversion uses monotone interpolation of original quadrature-node optical depths; no fresh Einstein solve. At its median, a same-source conditional geodesic redshift is \(z_{50,\alpha}=\mu_\alpha(u_{50})/\mu_\alpha(U)-1\). This is a geometric redshift within the original KM2 ray source, not the same object as CE1AS `D_A(z,n)`.

The sky moments are \(\bar X=\sum_\alpha w_\alpha X_\alpha/\sum w_\alpha\), \(d_i[X]=\langle (X-\bar X)n_i\rangle_w\), \(Q_{ij}[X]=\langle(X-\bar X)(n_i n_j-\delta_{ij}/3)\rangle_w\). Discrete w is the actual final-observer sky quadrature; normalization by the **measured finite sum of w** prevents spurious angular GL12 normalization drift.

## New computations and numerical results

Original source extraction and NPZ byte validation is complete (4/4 raw source SHA256). Both temporal and angular coordinates are taken from the identical original model. 800 physically source-owned ray profiles ×320 GL8 collision nodes = **256,000 new survival-weighted rate evaluations**, with 800 ray summary records and 82 time-sampled sky profiles. They are numerical model-derived observables, **not new measured or Einstein IVP rows**.

| Quantity | GL12 | GL16 |
|---|---:|---:|
| Original optical τ, physical sky mean | 7.283254163753941 | 7.283254163279436 |
| Original optical τ, ray min–max | 7.144614566 – 7.424804276 | 7.144207040 – 7.424816935 |
| Conditional event probability P(≥1) | 0.999310769109869 | 0.999310769110681 |
| Conditional event time ⟨u⟩ | 0.178508354671502 | 0.178508354665988 |
| Median event time sky mean ⟨u50⟩ | 0.187687649… | 0.187687649… |
| Same-source median-event redshift ⟨z50⟩ | 0.022339468297139 | 0.022339468374122 |
| ⟨P(u_event≥0.2∣event)⟩ | 0.412251693986 | 0.412251693945 |
| τ dipole vector norm | 0.0470559163723 | 0.0470559045974 |
| τ quadrupole tensor Frobenius | 3.385e−9 | 2.005e−12 |
| median-event z quadrupole Frobenius | 0.00163625544 | 0.00163625619 |
| τ reconstructed from independent GL8 rates max abs | 6.22e−15 | 6.22e−15 |
| visibility GL8 integral identity max abs | 2.55e−15 | 2.44e−15 |

These original-model conditions show a predominantly dipolar *optical hazard* (baryon boost/tilt enters D), versus an appreciable quadrupolar same-ray redshift of the event-median (anisotropic geometric redshift enters μ). This is an observed result in two finite original angular grids, **not a general symmetry theorem, nonzero observational CMB low-ℓ detection, or a continuum error enclosure**. The τ quadrupole's near-zero numerical value at GL16 is especially not certified identically zero.

## Falsification and scientific limits

The original time-integrated optical depth is independently reconstructed from the original stored quadrature hazards: max abs ~6.22e−15, not only from the input `tau`. Direct quadrature of the source `g` and the analytic rate-transport probability identity differ ≤2.6e−15 per ray. Independent constant-h analytical event mass and mean-time test, source SHA and original `nu D` event-rate comparison, positivity and event quantile ordering pass. Deliberate wrong ray-hazard permutation and wrong survival exponent are rejected. Python `-O` test mode is run using `unittest` methods rather than disabling raw assertions. No different-author reviewer or native subagent was available in this run.

Scientific ceilings: original baryon density is synthetic and documented as about 5.74× the CLASS reference in the inherited KM2J model; Tm(z) externally imposed, Sobolev/grey chemical energy approximate, thermal first law and full ionizing radiation not closed. This kernel does not supply a source-weighted emitted-photon last-event distribution, full polarized scattered spectral field, real CMB polarization/visibility, posterior or global continuum convergence. Crucially the CE1AS original massless collisionless six-cell source **has no electrons**, so its `D_A(z,n)` cannot be multiplied by this unrelated KM2 transmission as an admitted source-matched observational prediction.

## Counter and next actual obligation

BASS physics upper remains historical **9/15 scoped/source-mapped, 21 edges**; KM-2 PARTIAL; OB-1 PARTIAL; no upper full node promoted. No production or merge readiness. Native subagent NOT_RUN; distinct-author R6/C9 NOT_RUN. The next scientifically justified step would require an actual same-owner joint geometry+electrons+photon source and a properly source-weighted observer quantity on that geometry, or work directly on the BASS Type-II/VI0 unfinished production-critical physical gate. This run stops after this one bounded visibility calculation.