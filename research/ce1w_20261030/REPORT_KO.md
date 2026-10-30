# CE1-W S2 | BASS angular-energy geometry transfer: actual coupled physics result

**Date 2026-10-30 KST.** Parent PR267 `45efec543faa2997c5918f320b41c6b4cd9bddb1`; sibling pressure-source PR264 and conditional MPFR RK4/Hermite PR266 are separate verified donors, not merged. Frozen original 6 exact binary64 cells SHA256 `022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`. Positive reflection-even massless collisionless diagonal Bianchi I, Λ=0, (-,+,+,+), proper u=t/Tstar 0..0.08, shear(.2,-.13,-.07).

## New physical calculation
For observer sky `W=det(M)r dE0`, `t_i=s_i²`, differentiate every source ray exactly at fixed conserved momentum:
`∂_j t_i=2t_i(t_j-δij)`, `∂_j W=-(1+t_j)W`, `∂_j E=-(E+P_j)`, `∂_j alpha_lm=(4π/E)[∂_j a_lm+a_lm(1+P_j/E)]`.
The five real independent even Condon–Shortley harmonics (l,m)=(2,0),(2,2),(4,0),(4,2),(4,4) yield **82 source-locked 41-time GL6/GL8 response records** and **3362 unequal-time kernel derivative records**. The new raw matrices, 2×41×41×3×2×2 components, reside in the complete checkpoint ZIP and downloadable CI artifact. Source code in this Draft regenerates full physical results without any matter closure, blackbody or polarization.

At (u,v)=(0,.08), GL8:
`K2delta=.05804585469775579`, `K4delta=.01079267954692735`.
Initial epoch three-axis K2 logscale response `[-.09171433511535199,+.39895795644597787,-.3072436213306261]` and K4 `[+.014172582662747239,-.010510077423291646,-.00366250523945557]`.
Numerical GL6/GL8 cross-kernel maximum gaps K2 `2.06904e-13`, K4 `1.77772e-11`; these are empirical, NOT rigorous continuum enclosures.

## New analytic bound and essential scope split
Common-mode isotropic rescaling gives `sum_j ∂_j alpha_lm=0`. Spherical harmonic addition theorem gives, for positive fixed angular source, the uniform **per-axis** bound
`|∂_(ell_j(u)) K_l^delta(u,v)| ≤ 4π[1+sqrt(l(l+1))/2]`: l2=27.95696857630154, l4=40.66562953852208.
For two geometric logscale perturbations of max norm 1e-7 each, the guaranteed differential-path bounds are 1.677418114578e-5 and 2.439937772311e-5. These are hypothetical input-geometry perturbation budgets, **not a certified DOP853 solution error**.

Under **identical geometry** and the independent PR264 exact-rational `|Delta P_i|≤eps_P`, `E=sum P_i`, `E≥0.6`, the l2 continuum-source-only kernel difference obeys `|Delta K2delta|≤354.682eps_P`. Donor eps gives GL6 <=1.06782e-9, GL8 <=2.18636e-11. It does **not** give l4: positive distinct distributions `U±=(E0/4π)(1±eta P4(nz))` have equal E,P_i yet different a40. Wolfram exact `∫P4=∫z²P4=0`, `∫P4²=2/9` verified. PR266 conditional MPFR192 four-panel certificate applies to RK4/Hermite, NOT automatically to CE1-V DOP853 input.

## Evidence
Full independent local source bundle restored into an empty directory; original source file hashes retained, model data regenerated, **18/18** scientific pytest PASS and compileall/plot PASS. Current remote source/physics GitHub Actions https://github.com/cosmosapjw-quantum/bass/actions/runs/40985249699 **SUCCESS** with all source SHA locks, remote scoped tests, regenerated 82+3362 physical rows and 4 NPZ arrays. Remote vs archived local full K matrix element gap <=1.81e-16, response component gap <=7.78e-16. CI artifact #12945649968 SHA256 `2e9cea188e6436a47120a37ee1ae4f20ca22515a2ec9ebb42aec13ce7c6fc8dd` was downloaded, checked ZIP CRC and actual numerical payloads.

Research package S2 includes **20 individual R/C checkpoint ZIPs**, all raw source inputs, 18 scientific tests, full output, plots and a copyable handoff. Original top-level DAG **9/15** with 21 edges, CE1 PARTIAL; scoped 18/20; genuine distinct-author R6/C9 NOT_RUN, native subagents NOT_EXPOSED. No parent/sibling merge, production, thermal CMB, polarization or observational likelihood.

## Storage
- Google Drive stage S0: https://drive.google.com/file/d/1YlTD9pISb8G7Tm211fNF1BNMdrRGLd0y/view
- Google Drive stage S1: https://drive.google.com/file/d/12PBRvKpjGqyCT3bhdzi_LjzbVjKcQz_w/view
- Google Drive S2 original science source/data package: https://drive.google.com/file/d/11yV9e4ElWm8fhaTVaenXBNoqFOPHzTV7/view
- Google Drive actual final GitHub CI artifact: https://drive.google.com/file/d/1KV-YJt8FGXpoWnvHO5R8WBikI5YiwUqk/view
- Full locally restored final S2 version (includes current workflow) SHA256 `6aa3e0e1a72bafca594b7e2317d6ccb5cda4b8f6615258126516844f36308d26`, 76 ZIP entries, 75 payload SHA/CRC verified. Its extra Drive upload is NOT_RUN due to file-session expiry; do not substitute an older Drive ZIP's hash. Dropbox NOT_RUN.

Next bounded physics: direct certified high-order l4 angular quadrature source discrepancy, and binding PR266 RK4/Hermite carrier to PR267 DOP853 41-time samples. Do not repeat solved 41×41 construction, merge PRs, or promote upper DAG without genuine node closure.
