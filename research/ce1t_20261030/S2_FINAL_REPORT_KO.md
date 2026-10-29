# CE1-T final scoped science: native BASS Rust Liouville with original 6-cell Gauss quadrature

**Date 2026-10-30, Draft child PR #263.** Parent PR261 exact HEAD `e77626cca186724ea9150cee166848ffa9bfbb1e`, sibling fractional-sky PR262 independent. Original BASS Rust kinetic/comoving source blob `a29b12b5e7b0d529bddaf9eac53cfdb984ddaa84`, unchanged. Parent 41-step GL40 background full CSV Git blob `b7752a67dbc33848f2dc448b79405727d39c24da`, unchanged. Source original six exact-binary64 cells input SHA256 `022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`, E0=.9, 8 reflections, massless collisionless expanding diagonal Bianchi I Λ=0 signature(-,+,+,+), u=t/Tstar. This experiment freezes the inherited GL40 Einstein geometry: it does **not** solve a new Einstein history or re-certify the existing CE1-M h error target 1e-5.

## New mathematical and computational result

Each physical cell `C_ij=[mu_i,mu_{i+1}]×[t_j,t_{j+1}]` retains physical energy E_ij under positive tensor Gauss–Legendre n×n nodes with original 8 reflections. Each stored quadrature ray `w_ijab=E_ij omega_a omega_b/4`; N=6n² rays, original physical source piecewise-constant density unchanged. `t=(2/pi)atan2(|q_y|,|q_x|)`. The reflected even (l,m) Liouville integrand is smooth *inside each original cell*, including mu=1 after cancellation of odd sqrt powers. Standard Gauss error remainder needs `sup |d^(2n) integrand|`, not computed rigorously here: no formal MPFR sky bound.

The native Rust executable is inherited `research/ce1r_20261030/sky_time_derivative.rs` and calls the actual pinned BASS `_rustcore/src/kinetic/comoving.rs` Frame::apply/det/phys_dirs, with proper u not Frame::step e-fold tau. New Python `research/ce1t_20261030/cellwise_gl_rust.py` Git blob `6d254e9efc95acc1fd2079bd047d40662986d135` creates the strictly positive cells/rays, calls Rust for 41 epochs, parses harmonic derivative `C4'=2 Re sum conj(a_4m) da_4m/du /9`, checks E=ΣP and E'=-theta E-Σh_iP_i.

**Live native CI** [GitHub Actions #40916365546](https://github.com/cosmosapjw-quantum/bass/actions/runs/40916365546) **SUCCESS**. It pins the parent source and original BASS live Rust blob, recompiles original Rust with 1.94.1, verifies Rust selftest and executes all 41 epochs for n=1,2,3,4,6,8,12,16,24,40, **19 pytest PASS**. GitHub action artifact #12914614829 ZIP SHA256 `1867c2f4e0ac898595f6088e08711395ac3b8a03c18aaf54ab0a8c3f8a6ea685`, 410 numeric rows and source/mass SHA identities match local runs. Independent SciPy spherical harmonics and finite-difference derivative checked at endpoint.

| n / 6n² rays | max over 41 |C4'(n)-C4'(GL40)| |
|---|---:|
| 2 / 24 | 1.5442379236127262e-5 |
| 3 / 54 | 9.490548495768734e-7 |
| 4 / 96 | 1.0533280483379431e-8 |
| **6 / 216** | **1.3228497073788925e-12** |
| **8 / 384** | **1.4677386910022516e-16** |
| 24 / 3456 | 3.182133376244955e-17 |

GL40 at u=.08 has C4'=-0.00014789130274602829 (prior parent -0.00014789130274602826). At *same GL40 background*, prior stored midpoint ref8 384-ray endpoint C4'=-0.00017004806159896595, **14.9818% relative gap**; maximum across 41 **3.344305218262508e-5**. New positive-cell GL8 384-ray maximum is 1.47e-16. At newly declared **exploratory/nonbinding** absolute threshold 1e-9 for C4' and C4, minimal evaluated n=6 (216 rays). This is powerful source quadrature convergence, **not** a measured wall-time speedup or production solver acceptance. GL40 is a numerical reference, not a certified continuum solution.

**Numerical and provenance limits:** local previously archived BASS Rust comoving bytes differ from live blob; GitHub CI built live original BASS Rust. The local projected 7-column history is not byte-identical to full original CSV; GitHub CI reads/locks full original bytes. Existing CE1-M MPFR192 geometry error is not transferred to new GL source or sky; no polarized/thermal/observed CMB, tilt, collision, likelihood, native production, true independent-author R6/C9, full interval sky proof. Main, parents and sibling untouched, no automatic merge.

**DAG**: upper completed/total **9/15** (21 edges), CE-1 PARTIAL, `production_ready=false`, `merge_ready=false`, `auto_next=false`.

**Single next research unit CE1-U**: derive a general positive within-cell angular quadrature source certificate and run end-to-end MPFR192 source/time/geometry error for new GL6/GL8 binary ray distributions, using Rust E/P/J only as binary64 differential oracle. This bridges new angular-resolution science with the user-locked geometry h target; never substitute nonrigorous GL40 error differences for an interval certificate. Stage S0/S1/S2 source, GitHub CI artifact, figures, Library/Drive/Dropbox receipts in `DELIVERY_RECEIPTS.json` and final ZIP; verify live exact HEAD and provider responses before promotion.
