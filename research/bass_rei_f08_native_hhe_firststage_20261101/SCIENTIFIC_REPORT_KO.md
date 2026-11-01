# BASS → REI F08 S0 | Original Rust coupled H/He response to photon spectral support

Date: 2026-11-02. Status: DERIVED / NUMERICALLY_CHECKED / IMPLEMENTATION_VERIFIED_SCOPED, original-owner admission HOLD. One BASS IGM science unit; source parent BASS PR323 head c0e965ba21892346feef9ecb2389932c34f3fc82, Draft PR326. No original REI, main, worker, history, accepted DAG or tolerances mutated.

## Source authority and physical construction
- Source: original REI F08 S0 13.7 eV photon births (0.05 per original H at t=0 plus 5e-15 per H per s thereafter), original 16,001-sample proper H/He matter history, 128 original q-directions, 17 original fixed energy nodes; FLRW H=(1,1,1)e-14/s and BI H=(1.01,.99,1)e-14/s, metric signature (-,+,+,+), c=29979245800 cm/s, nH0=1e-4 cm^-3, fHe=.083, dt=625000000 s. Original S0 source SHA12/12 and checkpoint SHA4/4 checks inherited and rerun.
- Original historical REI Rust source 51/51 original SHA256 byte-identical. Native H/He/thermal stage function is primary_stage_step_conservative from unchanged coupled_primary.rs SHA256 915d0a898100a54d04a525227e7fbeb870e321fcc14aaa91afd61352b6d4cf4b. Original atomic_provider.rs SHA256 b0b572d3940a7a1f740e09d5f43c60236ec61511e8bdbcc68e60395ec7e107d3. A research-only BASS wrapper excludes unrelated historical missing compile-time contract files; original Rust source bytes remain unchanged.
- Incoming photon states differ: (A) off-grid 13.7 eV source birth-energy characteristic E(t)=13.7 g(q,t)/g(q,tbirth), g=sqrt(sum_i q_i² exp(-2 H_i t)), original angular birth weights and HI absorption before parent on frozen ORIGINAL H/He; (B) original 17 fixed energy-node hat/HI-frozen prior transport with original source guard retained as one below-10-eV inert photon packet (number and energy). Both input states use the SAME original gas parent: xHII, xHeII, xHeIII, thermal w_eV/H, escaped energy, original proper nH at next-stage endpoint, Hmean and dt.
- The next ONE stage then actually evolves photon absorption, H/He ionization/recombination/collisions and thermal/escape energy together using exact original native Rust conservative stage and UNCHANGED StepControl(max_iterations=200,residual_tolerance=1e-15). Unlike prior BASS PR323, the gas changes in this step.
- Each selected parent is conditioned on prior frozen F08 H/He history. Five separately selected parent times are NOT a new continuous 16k-step coupled IVP and not an original paired_runtime owner replacement. The differences involve both photon spectral shape and surviving count. Do not attribute differences solely to support leakage.

## Actual new data and scientific results
Local physical data: 20 original-native Rust source-matched coupled H/He cases across 2 backgrounds x5 source parent ticks (0,800,1600,6400,15999) x2 photon models. Baseline stage source packets: 133,748. Additional high-birth 512GL/48-opacity-panel control: 12 native cases across ticks 800/1600/15999, 2 backgrounds and 2 models, 394,836 source packet inputs. Paired response = 10 physical records, 38 fields per native case; output stored as native_stage.csv, native_high_stage.csv, F08_S0_ORIGINAL_RUST_HHE_COUPLED_FEEDBACK.csv.gz and RESULT.json.

| Original BI parent tick | Characteristic minus original-hat xHII after | Characteristic minus hat T after (K) | Characteristic minus hat HI absorption events/H |
|---:|---:|---:|---:|
| 0 | -3.194000619544113e-12 | +1.64181983564049e-7 | -3.194164456044903e-12 |
| 800 | +5.697847437646786e-6 | -0.13032340516656404 | +5.6980678990575875e-6 |
| 1600 | -1.7187626040193749e-6 | +0.03813593421364203 | -1.7188245031793008e-6 |
| 6400 | +7.771123455846407e-8 | -0.0016412469412898645 | +7.771316375885185e-8 |
| 15999 | +1.9136322082502488e-8 | -0.00037190916191320866 | +1.9136547098029948e-8 |

The fixed-hat native HII endpoint is close to original F08 saved endpoint at sampled parents, typically at roughly 1e-9 or 1e-8, but does not reproduce the full original photon-chemistry step/operator. In the original first interval, the old hat photon input contains ~0.00017124946 photon/H below the physical source energy support, whereas exact characteristic packets contain zero.

## Physics, mathematical and runtime validation
- Native original HII event identity: dxHII = HI photon absorption + HI collisional - HI recombination. Max independent absolute residual 1.6361001542927632e-16.
- Native photon source count conservation max absolute residual 3.065462211057201e-15/H. Native total chemical+thermal+photon+escape energy balance residual max 1.650031023273102e-14 eV/H; original native solver residual ~1e-16..1e-15 and original 1e-15 stage threshold unaltered.
- Direct same-author stdlib source/physics adversarial audit PASS: source SHA 51 Rust + 12 original S0 input +4 photon checkpoint; same parent state BI/FLRW, nonnegative packet/rates, original HII/HeII/HeIII physical domains, source gamma Verner checks, 20 cases, 10 paired records.
- 12/12 standard Python and 12/12 optimized Python tests PASS. Rust original scoped lib build and native release example PASS. Historical copied crate cargo test --lib compiles and runs ZERO Rust test cases; do not claim 51 source Rust unit tests were executed.
- Input negative photon weights are rejected by new BASS example, original source unchanged. Symbolically independent Wolfram identity confirms hydrogen implicit update x1=(x0+hI)/(1+h(I+R)) and ideal-gas temperature response decomposition exactly (residual 0).
- High-birth sensitivity 128GL/24 vs 512GL/48: original BI tick800 gamma relative -9.39433975056e-10, tick1600 +0.000181690595533, tick15999 -0.011723706074668. The late-time BI delta xHII sensitivity ≈1.01141e-8, which is material relative to the tiny reported late response (~1.91363e-8). All high-native cases ran successfully, but global model error and source-owner full-IVP parity are NOT certified.

## Science, DAG and future decision
This BASS result closes a BASS-only science gap: original REI Rust HI/HeI/HeII chemical and thermal single-step feedback actually responds to changed source photons at same original H/He parent. Owner REI PR361 already addressed first-step photon-only events; PR362 source angular PSTF is separate. The actual critical follow-up is an approved source-preserving photon representation in the original coupled F08 full history with native photoionization/energy/OTS/14-ledger gates, or clearing original F05 tick160→161 and F09 provider. Do not create another source-only ray atlas.

REI central 28/88 REPORTED delta0; working 33/88 nonadditive; fast 4/7; BASS upper 9/15 scoped/source-mapped, full completed count not substantiated, delta 0. Original F05 accepted tick160/131072; tick161 is not official; original F08 historical source scientific admission HOLD, F09 provider blocked. No production, merge, force push, original source mutation, tolerance relaxation or automatic next node. Distinct-author blind referee / native subagent NOT_RUN (unavailable); same-author adversarial check done.

Primary references: Verner et al. (1996), ApJ 465 487, DOI 10.1086/177435 (actual source atomic fits); Reynolds, Paschos and Norman, arXiv:0901.1110 (coupled radiation-HHe/thermal equations). Source owner code, not literature, binds all project constants and stage operators.

## Source-inclusive cold backup, independent restoration
Archive /home/cosmosapjw/archives/BASS_REI_F08_S0_NATIVE_HHE_COUPLED_SOURCE_20261102.zip: 7890855 bytes, 98 members, SHA256 0e104454b45d10f3921ffc37237e862a96cf7f6157aade69a9a30446f802c43c. Independent fresh-directory extraction CRC PASS; Rust original51 + S0 source12 + checkpoint4 SHA PASS; ordinary and optimized 12/12; same-author data-level audit PASS; native release Rust offline rebuild PASS; all baseline 20 and high-resolution 12 native outputs byte-exact replay PASS. GitHub CI requires separate exact-HEAD readback; external-provider second binary restore not verified.
