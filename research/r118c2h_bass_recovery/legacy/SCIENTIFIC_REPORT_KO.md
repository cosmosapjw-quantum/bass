# BASS → REI F08: original Rust Krawczyk root on actual continuously evolved S0 photons

2026-11-02. Bounded research unit. Source immutable BASS PR328 HEAD b23c6915aeaeedbabbc8e90ffab74f2afa96c1e6 and original REI F08 source-pair SHA256 0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8. Draft BASS PR331, original source and production unchanged.

## Constructive theory and actually executed physics
Source: original homogeneous Bianchi I S0 constant H=(1.01,.99,1.00)×1e-14/s, matched FLRW (1,1,1)×1e-14/s; metric (-,+,+,+), a_i=e^(H_i t), source proper original dt=625000000 s, original 128 q sky and 13.7 eV monochromatic birth with N_initial=.05/H plus source 5e-15/H/s. Original Verner HI,HeI,HeII threshold and chemical potential retained; c=29979245800 cm/s, k_B=1.380649e-16 erg/K. Physical null energy E(q,t;t_b)=13.7 sqrt(sum_i q_i² exp(-2H_i t)/sum_i q_i² exp(-2H_i t_b)) eV.

PR328's actual fully continuous self-evolved photon+HHe 160-step solutions were re-executed with immutable original Rust primary_stage_step_conservative. Four genuinely different physical sources (BI/FLRW x birth-energy characteristic/original fixed-hat energy remapping) yielded 16 full *real* input photon+gas snapshots at original S0 ticks 1,8,64,160, total **70,656 real photon packet records**. The original source-owned primary_stage_root was invoked with the same input, StepControl(200,1e-15) unchanged, parent exact f64 point intervals. Its original Krawczyk operator requires norm q<1, strict K(Y) subset interior(Y), gas and photon intervals. This root builds centre from original primary_stage_step (non-conservative point), whereas PR328 invokes original primary_stage_step_conservative, so enclosure of the conservative output is a nontrivial compatibility test.

**Observed**: ALL 16/16 actual original source root calls returned PASS, q<1; their root gas intervals contain the source-owned original conservative gas xHII,xHeII,xHeIII,w, and root photon intervals contain every corresponding conservative source packet survivor. Full source-independent standard-library readback verifies conservation inputs against original PR328 gas/trajectory records and original files; PR328 conservative xHII, xHeII, xHeIII and w agree exactly at written precision. Original source SHA 51 Rust+12 HHe photon+4 original V1 checkpoint/header = 67/67 exact. A forged negative photon number in an otherwise valid original S0 input file was explicitly rejected by original Rust parser; PASS_NEGATIVE_TEST, never counted as a valid physical root.

| Original S0 tick | BI characteristic Krawczyk q | BI fixed-hat q | Physical input photons BI characteristic / hat |
|---:|---:|---:|---:|
| 1 | 2.1115752104738245e-15 | 1.8850133788410860e-15 | 256 / 256 |
| 8 | 2.0576073532724640e-15 | 2.3191677392528030e-15 | 1152 / 1152 |
| 64 | 3.6678203741346792e-15 | 2.2165683324177841e-15 | 8320 / 1792 |
| 160 | 6.0424535248395886e-15 | 2.1540674653057838e-15 | 20608 / 1792 |

FLRW at identical ticks likewise passes all 8/8 root enclosure/containment checks. The observed maximum all-geometries Krawczyk factor is 6.043239571414641e-15; largest reported relative gas interval width is 5.143880414834546e-14. Difference between original root centre and conservative point is at most approximately 1.7763568394002505e-15 in the corresponding gas physical coordinates. The native original root self-certifies strict enclosure in this exact point-parent input.

## Physically significant support statistic, not a root acceptance result
The actual retained photon input below the true original monochromatic null-energy minimum was:
| S0 proper tick | Original Bianchi fixed-hat unsupported photon fraction | Exact birth-energy characteristic |
|---:|---:|---:|
| 1 | 0.003424775247270876 | 0 |
| 8 | 0.027065536097753966 | 0 |
| 64 | 0.1967060487517463 | 0 |
| 160 | 0.42018352218694077 | 0 |
Matched FLRW fixed-hat fraction at tick160 = 0.4201858277869133, showing the source fixed-grid defect is not specific to anisotropy. These are photon-number-weighted support violations evaluated at the selected original source inputs, NOT inferred from the interval root, and not identical to the original 16000-step F08 final owner distribution. Importantly, original numerical root containment does NOT imply that original fixed-hat transport preserves the intended physical source support.

## Mathematical claim ceiling and remaining blocker
A primary_stage_root PASS for an *exact binary64 point input* provides local source-conditioned Krawczyk gas+photon enclosure using original Rust interval operators at that input. It DOES NOT propagate intervals of previous birth-time quadrature weights, spatial q, redshift energy, previous gas root or the original F08 per-direction source through 160 consecutive steps. It is NOT a globally interval-certified PR328 characteristic IVP or the original full paired_runtime MPRK/SDIRK/14-ledger source-owner acceptance. The post-root scientific blocker is constructing a source-support-preserving, outward-enclosed energy/birth representation and carrying joint parent photon-gas intervals into the next source step while avoiding invalid point-input-only claims. Need then integrate in the *actual* original REI owner paired_runtime and compare its original point and interval contracts. F05 accepted tick160/131072 and unaccepted tick161 refer to different source-owner clock; F09 provider domain remains BLOCKED.

## Verification
- 16/16 original Rust source root calls PASS with 70,656 actual original S0 photon input packets; all conservative gas and photons enclosed, q<1 and source support checked.
- Source identity: 51/51 Rust original source, 12/12 original S0 H/He photon physical input, 4/4 original V1 checkpoint headers, SHA256 exact.
- Python independent same-author standard-library hostile audit PASS. Normal 12/12 tests PASS, optimized 12/12 tests PASS. Forged original S0 negative packet rejected in actual Rust executable (exit nonzero). Original source input number differences <=1.6653345369377348e-15 photons/H, source packet energy differences <=3.2529534621517087e-14 eV/H. Original PR328 gas xHII, xHeII, xHeIII and w input/output parity exact at stored precision.
- Rust source-owned interval code unchanged, only an additive BASS example and capture/audit code. Do not claim distinct-author blind referee or native subagent where tools are not exposed.
- Inherited PR328's previous 160 continuous actual native H/He steps per model (640 model states) remain independently verified, but the new 16 root checks sample four epochs per model; not all 640 stage roots.
- Original REI central 28/88 reported delta0, Working 33/88 nonadditive, Physical Fast 4/7, BASS upper 9/15 scoped/source-mapped no new fully admitted upper. F08 production source admission HOLD, F05 official tick160/131072, tick161 NOT_ACCEPTED, F09 provider BLOCKED. NO_MERGE, NO_FORCE_PUSH, NO_SOURCE_MUTATION, NO_TOLERANCE_RELAXATION, PRODUCTION_HOLD, AUTO_NEXT=false.

Primary literature methodological context: Abel, Norman & Madau (1999), ApJ 523:66 DOI 10.1086/307739; Pawlik & Schaye (2011), MNRAS 412:1943 DOI 10.1111/j.1365-2966.2010.18032.x. Project physics is governed by the exact original REI source and actual local results rather than these papers.

## Source inclusive cold storage and publication boundary
Archive /home/cosmosapjw/archives/BASS_REI_F08_S0_NATIVE_KRAWCZYK_ROOT_SOURCE_FULL_20261102.zip; bytes=7027426; files=113; SHA256=e591afcad573ae64f223ce307ffd26dc66d9eba8ed49671ffab6b9dbf8dd4fe1. Independent cold extraction CRC PASS, 51+12+4 original source SHA PASS, original Rust native root release compilation PASS, all 16 original photon/gas root cases BYTE_EXACT PASS, all 16 independent physical-support rows BYTE_EXACT PASS, 12/12 normal and 12/12 optimized tests PASS, forged negative source input REJECTED PASS. This ZIP was created before final GitHub CI evidence publication; current PR head is authoritative for the CI result. Secondary external-provider binary restore NOT_VERIFIED.
