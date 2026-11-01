# REI S0 photon energy representation → HI ionization and heat: BASS source science

2026-11-01 | Original-source conditional physical experiment | Production HOLD

## Model, provenance, and original authority
This one BASS IGM science unit is stacked on immutable PR321 HEAD 178d93c380a0e868a22869c3160d81c0aa643098; its frozen input provenance is original REI-F08 S0 paired-source identity 0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8 with original 12/12 source SHA checks and original photon-owner checkpoint 4/4 SHA checks, 16001 actual H/He proper-time samples, 128 original q directions and original Verner96 H I fit. The code reads original accepted physical history but never changes original photon source/solver/worker, H/He temperature, ionization or original main. BASS original main and preceding PRs remain unchanged.

The exact characteristic model retains original E_birth=13.7eV and original initial 0.05 photons/H plus constant 5e-15 photons/H/s for each original source q birth. For every birth ray preserve the source energy E(t)=13.7*g(q,t)/g(q,t_birth) for constant original anisotropic Bianchi H=(1.01,.99,1)e-14/s or FLRW H=(1,1,1)e-14/s, compute physical proper H I photoabsorption until original Verner fit cutoff 13.60eV, and keep sub-threshold photons as non-ionizing photons. Original HI chemical binding is 13.598434599702eV distinct from fit threshold. A separate original fixed 17-node hat model replays source remapping and implicit HI removal on the SAME frozen original H/He matter history and matches the published F08-owner gamma as a source-conditional check. These are independent radiation-history reconstructions, not a new original coupled MPRK22/SDIRK2 H/He IVP.

## Actual new original-source physical data
At 15 original accepted proper clocks in BI and FLRW the code produced 30 source history records, 3840 original-direction photon absorption/ionization/heat records (2×15×128 q), and 30 chemically separated binding+photoelectron energy-budget records, total 3900 physical result records. A separate 25-row numerical sensitivity file checks birth and absorption integration, not the physical model error.

At original S0 BI t=10^13s:
| Quantity (per original comoving H) | Source-characteristic model | Frozen original-hat model |
|---|---:|---:|
| Survivors, photons/H | 0.04700114165908084 | 0.05008021641368745 |
| Cumulative HI absorbed photons/H | 0.052998858340919164 | 0.04991978358630956 |
| Excess photoelectron heat, eV/H | 0.003248155427589854 | 0.00357194207117608 |
| HI Gamma per neutral HI, s^-1 | 4.347313478778532e-14 | 4.202736590549483e-14 |

The actual original F08 owner gamma is 4.202712336457183e-14 s^-1, not a third independent new material solution. Characteristic gamma differs from original by +3.44066238% at this last time. At t=2.5e11s it differs +4.9768%, at t=5e11s +37.9805%, at t=1e12s -49.5949%. Rates are physical source-conditioned diagnostics, not a measured CMB or accepted ionization-history modification.

Difference in cumulative HI photoabsorptions exact minus fixed = +0.003079074754609605 photons/H. Ionization chemical binding delta = chi_HI × delta_absorbed = +0.0418705966781522 eV/H (+6.708409164937346e-14 erg/H). Difference in cumulative photoelectron excess heat = -0.00032378664358622593 eV/H (-9.06472269522606%). Difference in total absorbed energy = +0.04154681003457428 eV/H. The photon energy / thermal-gas / chemical-energy accounts are physically DISTINCT. Original F08 saved thermal_work_ev_per_h includes other coupled sources and is never compared directly as photoelectron heat.

At last original FLRW, same source conditional HI absorption difference is +0.003079030699335933 photons/H and excess photoelectron heat difference -9.064884%, whereas the two background models retain original rather than new matter cosmological histories.

## Actual validation and uncertainty
- Original 12/12 parent source SHA256 and 4/4 F08 V1 photon checkpoint SHA256; exact branch parent Git identity.
- Normal 18/18 and optimized 18/18 unit tests PASS on the original frozen input; independently implemented pure Python stdlib data-audit reads and checks all 3900 physical records.
- Max absorption/birth photon ledger residual 1.2836953722228372e-16 photons/H, max chemical binding/heat decomposition residual 8.104628079763643e-15 eV/H, max source-gamma × neutral fraction rate residual 3.7865323450608567e-29 in source units.
- Wolfram independently checked exact Bianchi null redshift energy ODE and source χ_HI chemical threshold gap 0.10156540029799999 eV.
- Convergence study on BI tick400,800,1600,6400,16000 uses 64-512 birth nodes and 16-48 HI optical panels. At last BI time 128birth/24panel to 512birth/48panel gives gamma -1.1735% relative, so 128 was not sufficient for gamma. The selected 512birth/48panel gamma agrees with the same-birth 512/32 setting within binary64; accumulated excess heat differs by 9.275e-5 relative across these two absorption-panel settings. These are sampled numerical sensitivities, not a formal global error bound.
- External different-author blind referee NOT_RUN (no native subagent tools). Same-author hostile check is real, but this is still source-conditional, not original scientifically accepted H/He ionization/thermal IVP.

## Drift watchdog and DAG admission
This was a genuinely new physics observable response beyond BASS PR321 fixed-grid source support and PR319 observer polarization sky. It quantifies H I ionization and separated chemical binding/photoelectron heat on actual original REI material. It does not assert that substituting the spectrum leaves matter unchanged in a fully coupled evolution, or that all 6.13% photon count mismatch is uniquely from fixed-grid hat. Original source state remains F08 HOLD, original F05 first coupled accepted interval remains 160/131072 (tick161 only shadow/pending), F09 atomic-provider source-domain remains BLOCKED.

Canonical REI 28/88 REPORTED Δ0, Working 33/88 NONADDITIVE, PhysicalFast 4/7 REPORTED; BASS upper 9/15 SCOPED/SOURCE-MAPPED, FULL completion unknown, new complete +0. R1-R10/C1-C10 are evidence stages for ONE science unit, NOT 20 new canonical nodes. No original source/worker/main mutation, no merge, no force push, no tolerance relaxation, no production, AUTO_NEXT=false.

Positive next action: REI original source owner may adopt/test an actual birth-energy-preserving photon representation in its coupled H/He/thermal equations and compare source-level gamma, heat, absorbed-photon and chemical binding ledgers under original gates; or unblock true F05 tick160→161 and F09 provider. BASS must not silently upgrade this frozen-matter counterfactual to an accepted physical IGM trajectory.

Primary literature for microscopic cross sections and null propagation: Verner et al., ApJ 465,487 (1996), DOI 10.1086/177435, Fleury/Pitrou/Uzan, Phys. Rev. D 91,043511 (2015), DOI 10.1103/PhysRevD.91.043511. Local original source code is SSOT for all actual original model choices.

## Durable source-inclusive backup and remote admission
Verified independent 37-member source-full archive at /home/cosmosapjw/archives/BASS_REI_F08_S0_CHARACTERISTIC_HI_PHOTOHEAT_20261101.zip has 6,556,825 bytes, SHA256 223c1dc43aad418c2d4b56e2209af4d23a1ebdbd4845e005b5d0f7491516acf4. A fresh cold extraction verified ZIP CRC, original 12+4 source identities, 18 normal and 18 optimized tests, independent source-energy audit and full 512-birth/48-Simpson 3,900-record byte-exact physics recompute. GitHub remote CI on final Draft HEAD not claimed until separately read. No second cloud binary archive provider restore claim. Production/merge remains HOLD.
