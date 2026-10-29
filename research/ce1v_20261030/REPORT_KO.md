# CE1-V | 실제 GL6/GL8 결합 Bianchi-I 이력의 두 시점 angular-energy kernel

**2026-10-30 KST · SOURCE-LOCKED PHYSICAL MODEL DATA · UPPER DAG 9/15 · CE1 PARTIAL**

## 핵심 결과

실제 original-six-cell collisionless Einstein–Vlasov GL6 (216 rays), GL8 (384 rays) 각 41 proper-time 관측자 하늘의 기존 저차 조화계수를 이용해 **새로운 41×41 two-epoch cross-power** `K_l^δ(u,v)`와 `r_l(u,v)`를 계산했다. 원본 부모 source data는 CE1-U PR264 head `15bb9fd015570c1562a4a7b9102f25a8481796f5`, ZIP SHA256 `d3f0e8196dc0a4a466cfc1932ed0d9385bcc79175773a5f9ecaee69871527fa4`, binary64 six cell input SHA256 `022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`. 독립 MPFR CE1-U sibling PR265 head `bcbb2ba451b9026608525cce27e26cf1a1288161` is read-only context, not merged.

For each of **two** source channels, 1681 proper-time pairs, each including l=2 and l=4: energy-sky cross-power, fractional-contrast cross-power, derivatives in both times, pattern cosine, squared pattern change, 0/90/180-degree rotation-averaged correlation. Also each channel yields **41×41×181** 2-time/angle truncated SO(3) rotation-averaged `ξ_uv^(≤4)(γ)` as compressed `.npz`. Total new tabular rows: **3362**; angle samples: **2×41×41×181 = 608522**. NOT observed sky data, likelihood, thermodynamic temperature, or a cosmological stochastic ensemble.

## GL8 numeric endpoint comparisons: u=0, v=0.08

| observable | l=2 quadrupole | l=4 hexadecapole |
|---|---:|---:|
| initial C^δ_l | 0.06373396691693015 | 0.010541886035180744 |
| final C^δ_l | 0.054307089776455084 | 0.011060264705922467 |
| cross K^δ_l(0,0.08) | 0.05804585469775584 | 0.010792679546927121 |
| pattern cosine rho_l(0,0.08) | **0.986637163430024** | **0.9995105057889709** |
| squared contrast-pattern difference D²_l(0,0.08) | **0.0019493472978735493** | **1.679164724896834e-5** |
| integrated D²_l(0,u) du | 5.3703904311494324e-5 | 4.896983064969461e-7 |

Physical interpretation: on this original anisotropic initial source, the **quadrupole pattern reorients/shapes more strongly** (rho smaller), while the hexadecapole pattern remains almost parallel despite a modest *increase* in its fractional bolometric angular amplitude. This is a fixed-axis, same-spatially-homogeneous-metric model comparison, not a line-of-sight CMB prediction.

## Numerical and mathematical evidence

- Input 2×41 original coupled physical CSV bytes exactly match parent archived SHA256; original six-cell SHA lock and 41 proper times retained.
- `K_l(u,v)` and normalized `K^δ_l(u,v)` are real symmetric and positive-semidefinite **by Gram representation**. Numerically min eigenvalues ~ -6e-16 are floating-point roundoff; not evidence of loss of positivity. Independent spherical harmonics via `scipy.special.sph_harm_y` directly integrate original GL rays at u=0,0.04,0.08, matching original CE1-U `a_lm` and E within 4e-12 / 2e-12.
- Symmetry max about 1.39e-17 (l2), 1.73e-18 (l4), diagonal C check <6e-20, diagonal time derivative check <9e-19, Cauchy excess zero.
- Independently calculated 5-point finite differences check `∂_u K_l` against source `da_lm`; full input `massless E=P1+P2+P3` and quadrupole moment identities verified.
- Equal-epoch `K(u,u)=C_l(u)` and normalization; gamma parity `xi(γ)=xi(π−γ)` for even l2/l4 truncated angular correlation.
- Max over all 41×41 time pairs GL6 vs GL8 `|K2^δ|` difference **2.0807661149646606e-13**, `|K4^δ|` difference **1.7777413222064276e-11**. **These are empirical discrete quadrature differences, not a continuum error enclosure.**
- Actual scoped `pytest` 18/18 PASS, `compileall` PASS, `source/build_crosstime.py` actual physical data build PASS. See `evidence/` for command outputs and immutable hashes.

## Claim gate and scope

This work provides a deterministic **two-time angular functional** of a specific unpolarized energy sky in normal Bianchi-I tetrads. A common rigid rotation of the spatial axes leaves the cross-spectrum invariant, but arbitrary independent rotations at u and v do not. The rotational-average `xi` is a **truncated** l2/l4 correlation, not the full orientation-dependent anisotropic two-point function. There is no physical blackbody spectrum, collision, recombination, photon polarization, observer boost, lensing, ensemble sampling or observational likelihood.

Source roundoff, exact-real ODE and numeric IVP errors belong to distinct claims. CE1-U #264 proves source comparison only; sibling #265 has conditional separate MPFR four-panel certificate whose hypotheses are not transported to `K_l^δ`. This unit does **not** certify error bars for `K_l` via MPFR; that requires source-to-harmonic functional derivative bounds and time-trajectory enclosures. True distinct-author R6/C9 and native subagents NOT_RUN. Top-level DAG remains **9/15**, 21 edges, CE1 PARTIAL, production_ready=false, merge_ready=false, auto_next=false.

## Next single physics unit

CE1-W proposed: use existing CE1-U source and conditional four-panel interval certificates to prove and compute bounded functional sensitivity `||δa_lm||`, `||δK_l||` on the same original 6-cell source and physically generated coupled histories, then issue a rigorous 41×41 cross-kernel envelope. Do not mislabel it CMB temperature or re-run already completed GL4/6/8 angular quadrature sweeps. Stop after one bounded unit; protect ancestors and independent siblings.
