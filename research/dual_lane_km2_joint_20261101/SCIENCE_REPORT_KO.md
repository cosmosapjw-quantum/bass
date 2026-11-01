# BASS KM2 | source-owned Lyα emission-time × exactly-one Thomson-scatter-time decomposition

**Status:** `NUMERICALLY_CHECKED_SCOPED`, 2026-11-01. **Not** an all-order last-scattering probability, CMB visibility or observational likelihood. Original physics unchanged. No owner Einstein–P8–Peebles IVPs newly solved.

## Authority and scientific intent

- Frozen original BASS KM2N [PR #297](https://github.com/cosmosapjw-quantum/bass/pull/297) HEAD `4137f942d2a95999f4e6627b71042e98f7afc1b7`. The directly adjacent [PR #308](https://github.com/cosmosapjw-quantum/bass/pull/308), HEAD `6a5cb5d0f3b838f757901ee30f991e85dd9e9484`, independently computed a *source-free initially existing photon* conditional Thomson opacity hazard/visibility. Its probability-weighted event times should **not** be treated as the brightness- or energy-weighted last collision distribution of photons emitted over time.
- Original KM2N science archive: GitHub Actions artifact `13035232055`, original outer SHA256 `45733f4ca2c0250cc94d934e0c58c7dbb0f6220350b2a303e25e55f77c787ffe`, inner SHA256 `8dd9258a3a50b6d0140c9305040c978f5a0790d907a8927769d3d27b5c63ab0d`. 50/50 original source files read/checked, original 9 data input files verified by individual SHA256.
- Model: original Einstein–Bianchi I/P8–Peebles with tagged escaped Lyα source, cold Thomson scattering, tilted electron bulk velocity, transported screen polarization, finite angular GL12/GL16, exact original 320 time-Gauss packet inputs and Simpson first-gain propagation. Signature (-,+,+,+), original normal time `u=t/Tstar`, `Tstar≈218601.80677272403 Julian years`; explicit `c`, `sigma_T` retained by original live collision coefficient `nu=n_H*x_e*sigma_T*c*Tstar`. Tagged photons remain an existing subset of the coupled grey P8 stress, **not extra gravitating matter**.

## Constructive first-scattering two-time distribution

Let `i=0..319` be original emission Gauss nodes with time `s_i`, original positive tagged energy packet `A_i(a)` on original incoming ray `a`, initial narrow Gaussian log-frequency centre `m_i(a)` and original angular weights. Let `j=1..40` be original possible first-scatter Simpson source edges at times `u_j`, and `k≥j` an observer snapshot at `U=u_k`.

The same original KM2L ballistic packet at the scattering location, **without any preceding scatter**, is

\[
 p_{i\to j,a}=A_i(a)\exp\{-4[R_j(a)-R_i(a)]-[\tau_j(a)-\tau_i(a)]\},\qquad s_i<u_j.
\]

At that edge, for the original Doppler factor `D_j(a)`, electron-screen projector `P^e_{j,a}=F_{j,a}F_{j,a}^{\mathsf T}` and original normal angular measure `w_{j,a}`, its contribution to the **electron-rest 3×3 polarized source moment** is

\[
 M_{j,i}^{ab}={1\over2}\sum_a w_{j,a}D_j(a)^2p_{i\to j,a}\,P_{j,a}^{e,ab}.
\]

The `D^2` is **not guessed**: the original normal packet bolometric energy transforms as `D^4` and the original electron angular weight is `w_e=w_n/D^2`. The computed \(\sum_{i<8j}M_{j,i}\) agrees with the frequency-integrated original `KM2N_FIRST_SOURCE_LEDGER_GL*.npz` moment, across all original 40 physical source times, within the observed maximum relative discrepancy `1.91937e-15`.

For outgoing original ray `\beta`, first-gain cold Thomson differential source and its retarded, **post-scatter no-recollision** transport are

\[
 \begin{split}
 B_{j,i}^{AB}(U,\beta) &=\omega_j^{\rm Simpson}\,{3\nu_j\over8\pi}\,D_j(\beta)^{-3}
 \left({\mu_U(\beta)\over\mu_j(\beta)}\right)^4
 e^{-[\tau_U(\beta)-\tau_j(\beta)]}
 F_{j,\beta,a}^{A}M_{j,i}^{ab}F_{j,\beta,b}^{B},\\
 J_1^{AB}(U,\beta)&=\sum_{j=1}^{k}\sum_{i<8j}B_{j,i}^{AB}(U,\beta).
 \end{split}
\]

The source emission and first collision have different angular labels: Thomson P8 redistributes directions via the full rank-2 source moment. This is not the approximation `emission(t) × source-free g(t)` on one unscattered ray. The physical sky/bolometric time-weight pair is

\[
 W_{j,i}(U)=\sum_\beta w_{U,\beta}\mathrm{tr}\,B_{j,i}(U,\beta)\ge0,
 \qquad \mathcal W_{j,i}=W_{j,i}/\sum_{j',i'}W_{j',i'}.
\]

**\(\mathcal W\) is an *observed-energy-weighted conditional contribution*, not a photon-number probability.** Thus all time means/correlations below are energy-weighted among this exactly-one-scattered tagged photon population. The original line intensity and photon energy vary with frequency and cosmological redshift. No all-order exactly-`N≥0` transport or source-owning CMB visibility is claimed.

We also transport the first log-frequency moment using the original packet Gaussian centres and finite boost to derive a smooth packet estimator. The saved parent spectral field uses 1,200 discrete bins; the two centroids need not be byte- or exactly numerically identical and differ by ≤`8.36e-6` over ten snapshots, below one-half original log-frequency bin. This is a *finite-bin agreement*, not a new spectral continuum certificate.

## Actual physical calculations

| Quantity | GL12, U=.25 | GL16, U=.25 |
|---|---:|---:|
| Reconstructed \(\rho_{J_1}\) (original units) | 1.263424154474874e-9 | 1.263424154712281e-9 |
| Mean emitted source time | .122952730445866 | .122952730451350 |
| Mean exactly-one scatter time | .174374786280442 | .174374786283261 |
| Mean emission→scattering interval | .051422055834576 | .051422055831911 |
| Mean scattering→observer interval | .075625213719558 | .075625213716739 |
| Correlation of emission and scatter time | .689822869498276 | .689822869524655 |
| Mean observer linear polarization | .003617033693890 | .003613978048052 |

The earlier, *different* fixed-ray source-free hazard `g=h exp[-(tau_U−tau)]` had a GL16 conditional mean event time `.1785083546659884`. This source-conditioned exactly-one-scattered energy mean `.174374786283261` differs by `-.0041335683827274` in the original dimensionless clock. This is a real difference in physical conditioning, **not** evidence that the older hazard calculation was erroneous.

**Source epoch composition** GL16 at U=.25:

| Emission interval (u) | Observer energy fraction | Mean linear polarization | Mean observer log-frequency (packet estimator) |
|---|---:|---:|---:|
| [0,.05) | .10502987584 | .00596194784 | -.07969479047 |
| [.05,.10) | .24887228799 | .00481328540 | -.06307390953 |
| [.10,.15) | .31326233435 | .00363657204 | -.04500591396 |
| [.15,.20) | .24429383185 | .00231534722 | -.02739669572 |
| [.20,.25) | .08854166997 | .00102088599 | -.01167748868 |

The oldest source-tagged photons contribute about **10.503%** of the present first-scattered energy and **0.596%** mean linear polarization; the youngest group contributes **8.854%** and **0.102%**, respectively. The five group-centroid log-frequencies are distinct. These correlations are computed from the **same original self-consistent geometry/opacity/emission** and P8 angular gain, with no invented free density or CE1 sky source.

**Physical output:** GL12 and GL16 × five original observation snapshots (10 separately physical original source reductions), **29,120 positive emission/scatter pairs** (no negative/causality-inconsistent events), **4,000 original ray-observer measurements**, final 2× 2×2 observer screen source-binned tensors, 5 PNG+5 SVG original scientific plots. No new Einstein/P8/chemistry initial-value-problem integration (`new_owner_Einstein_IVPs=0`), and no other angular/source/clock model used.

## Validation and hostile controls

- All 9 original science input files SOURCE_BYTE_IDENTITY; original S2 nested archive and manifest 50/50 intact.
- Reconstruct original KM2N **ten** physical `J1` energy snapshots: max relative difference `1.11e-16`; saved endpoint full 2×2 screen tensor for both GL12/GL16: worst relative component discrepancy `1.952e-15`; electron 3×3 source moment at each of 40 times: max relative gap `1.920e-15`. Exact original mean polarization across ten snapshots: max abs gap `4.91e-15`.
- Analytic stationary no-expansion, constant-opacity and constant-emissivity exactly-one scatter limit: \(J_1(U)=j_0\nu\int_0^U(U-t) e^{-\nu(U-t)}dt=j_0\nu^{-1}[1-(1+\nu U)e^{-\nu U}]\); SciPy quadrature and Wolfram symbolic subtraction independently return consistency (Wolfram difference `0`).
- Unittest normal **12/12** and `python -O` **12/12** PASS. Deliberately forged input fails source SHA; changing positive survival exponent to the wrong sign yields a different normalized observer field; source ordering and causal `s_i<u_j≤U` checked. All 5 emission group PSD and photon energy recombination checks PASS.
- Clean restore of exact original parent outer archive, 50/50 source manifest, 9/9 inputs, followed by physical replay in a new directory returns **byte-exact** five generated scientific JSON/CSV/NPZ artifacts at unchanged binary64 stack. This does *not* imply independent-author source audit or rigorous global convergence.
- GL12/GL16 excellent agreement is a source-scoped finite angular-grid observation, not an independently certified continuum angular bound; frequency first-moment comparison limited by original 1200-bin discretization.

## Boundary and smallest next physical action

Not yet modeled: all Thomson scattering orders, thermal Compton and resonant Lyα recoil, coupled chemistry photon spectral backreaction, true CMB photon source weighting, observational surface/likelihood, or a single source-compatible CE1AS distance and KM2 photon-visibility solution. The parent remains **DRAFT/unmerged**, no modifications to protected original owners or scientific tolerances.

**BASS upper 9/15 (scoped/source-mapped), KM-2 PARTIAL, OB-1 PARTIAL, new completed full upper node 0.** This bounded calculation explicitly closes the question of **where and when the observed exactly-one-scattered tagged Lyα photons were emitted and scattered**, with source-owned polarization/frequency diagnostics. Its nonzero correlation and derived screen fields are actual model physics rather than another metadata gate. `production_ready=false;merge_ready=false;auto_next=false;distinct_author_R6_C9=NOT_RUN;native_subagent=NOT_RUN`.

Future **one** scientifically decisive extension: use the *same owner* multi-order or bolometric photon energy/number source in a coupled observed redshift / distance calculation, with proper source equivalence, or stop this lane and return to the autonomous BASS Type-II/VI0 production critical path. Do not use another extra scattering sub-letter merely because the prior one exists.
