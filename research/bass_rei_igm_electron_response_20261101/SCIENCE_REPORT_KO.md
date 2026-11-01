# BASS KM2 → REI IGM | 800 original Bianchi rays, causal electron-to-visibility response

**Scope:** one BASS photon transport science unit aimed at future REI Bianchi IGM H/He source consumption. Original BASS KM2N Einstein–P8–Peebles parent [PR #297](https://github.com/cosmosapjw-quantum/bass/pull/297) SHA `4137f942d2a95999f4e6627b71042e98f7afc1b7`. Source parent KM2 [PR #308](https://github.com/cosmosapjw-quantum/bass/pull/308) SHA `6a5cb5d0f3b838f757901ee30f991e85dd9e9484`; independent [PR #309](https://github.com/cosmosapjw-quantum/bass/pull/309) builds a different emitted-Lyα first-scatter observable. Distinct [PR #307](https://github.com/cosmosapjw-quantum/bass/pull/307) six-cell FLRW comparator has NO shared electron owner with KM2. REI F05 source remains blocked at tick160/131072. No source swap.

Original GitHub Actions #41181695902 artifact `13035232055`: outer SHA-256 `45733f4ca2c0250cc94d934e0c58c7dbb0f6220350b2a303e25e55f77c787ffe`, inner `8dd9258a3a50b6d0140c9305040c978f5a0790d907a8927769d3d27b5c63ab0d`. All 50 original source-manifest members and CRC verified before computing. In original dimensionless normal time `u=t/Tstar`, exact-source hazard `h(u,n)=Tstar c sigmaT nH(u) xe(u) D(u,n)`, visibility `g=h exp[-∫_u^U h]`, probability `P=1-exp[-∫_0^U h]`, and last-event conditional mean `m=∫u g/P`.

### Constructive exact response

Perturb source electrons ONLY in the original panel p, `ne(u)→(1+eps_p) ne(u)`, holding the BASS Einstein metric, P8 radiation, primary photon emission, normal-frame velocity, ray labels and geometry fixed. Define `B_p(u,n)=∫_u^U h(v,n) 1_p(v) dv` and `DeltaTau_p=∫_panel h du`. **Exact causal first variations**:

```text
d g(u,n)/d eps_p = g(u,n) [1_p(u) - B_p(u,n)]
d P(n)/d eps_p = exp(-tau_U(n)) DeltaTau_p(n)
d m(n)/d eps_p = (1/P) ∫(u-m) d g/d eps_p du
```

This explicitly differentiates survival from the **future** of the last collision and handles within-panel partial optical depth. The second term can reverse conditional time-response sign while every optical-depth/probability response remains positive. Unit: u and m dimensionless BASS time. This is a fixed-background optical transport Fréchet kernel, NOT an Einstein–Boltzmann+H/He coupled solution.

### Actual original-source numeric science (local verification)

40 original time panels × 8 Gauss nodes/panel, 288 GL12 plus 512 GL16 source ray labels. **32,000 new causal panel-ray response rows** and **256,000 source-owned visibility node rows**. All original 50/50 source SHA, outer/inner CRC, original optical identities PASS. Python 11/11 ordinary and 11/11 `python -O` PASS on original physical archive. Independently exact finite panel electron perturbations vs Jacobian max error **6.807e−13**. Source original baseline matches PR308.

| Physics quantity | GL12 | GL16 |
|---|---:|---:|
| Sky-weighted tau(U) | 7.283254163753941 | 7.283254163279436 |
| P(at least one Thomson event) | 0.999310769109869 | 0.9993107691106811 |
| Last-event conditional mean u | 0.17850835467150244 | 0.17850835466598844 |
| d mean u / d uniform electron fraction | 0.04860864967324642 | 0.04860864967528383 |
| Earliest window p=0 d mean u | -6.129719050126401e-5 | -6.129719053548182e-5 |
| Latest window p=39 d mean u | +0.003903550406066825 | +0.003903550405772477 |

All 512 GL16 ray-wise derivatives are negative for original time panels p0–p5 and positive for p6–p39. `P` and `tau` increase with electron density for all panels. This demonstrates a physically meaningful distinction between amplitude and *chronology* of electron ionization, conditional on the original BASS background.

### BASS→REI source-owner adapter contract

REI H/He electron fraction `xe=xHII+yHe(xHeII+2*xHeIII)`. At fixed hydrogen density and He abundance `delta ln ne=(delta xHII+yHe delta xHeII+2 yHe delta xHeIII)/xe`. This is a **symbolic consumer interface**, NOT a numerical transplant: REI F05 is at z≈5.95 with another clock, source, metric, and incomplete canonical first interval. Only an accepted REI H/He timeline with a matched Bianchi Einstein background, proper clock/tetrad, ray/electron owner and source realization may be coupled. No CMB likelihood or all-order polarization produced.

### Same-author hostile checks and admission

- Negative control for forged source SHA, omitted survival factor/negative sign and inexact time-ordering.
- Exact `∫g du=1−e^{-tau_U}`, panel optical depth integral, endpoint response derivative verified at original Gauss nodes.
- Fixed-background `ne` perturbation is not a self-consistent Peebles/Einstein solution; BASS original synthetic baryon density differs from CLASS reference, thermally changing Thomson/Compton and Lyα recoil absent.
- No continuum time/sky guarantee, no real observed CMB or REI F08.
- Native subagent NOT_AVAILABLE, distinct-author independent referee NOT_RUN, same-author analysis only.

**DAG:** BASS upper **9/15 scoped/source mapped**, newly fully closed upper **0**, REI central **28/88 reported**, new central **0**, original F05 still `BLOCKED` at 160/131072 with unchanged strict `2e-4`. NO_MERGE, NO_FORCE_PUSH, PRODUCTION_HOLD, AUTO_NEXT=false.

**Literature context, not an implementation certificate:** [Dvorkin–Smith (2009) anisotropic tau](https://doi.org/10.1103/PhysRevD.79.043003), [Vicente–Pereira–Pitrou (2025) anisotropic LoS](https://arxiv.org/abs/2506.07786), [Fidler–Ringeval (2017) patchy reionization](https://arxiv.org/abs/1709.01395). Scientific code `response_kernel.py`, tests and source-pinned CI are in this BASS-only branch. A separate **source-inclusive full output** archive is preserved outside Git; do not count the GitHub thin branch as 36MB original ZIP.

**NEXT:** only when REI F05 accepted source-compatible H/He physical timeline exists, bind its same-clock electron field and compatible Bianchi ray geometry to this transport response; until then no cross-owner numerical assimilation. 
