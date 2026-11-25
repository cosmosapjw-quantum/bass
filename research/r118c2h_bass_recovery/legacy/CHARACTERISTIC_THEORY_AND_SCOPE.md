# BASS → REI F08: source-preserving continuous photon/HHe IVP

Owner: original REI F08 S0 paired pair SHA256 0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8. Immutable BASS parent PR326 head 4984b42a9ed4025e4b3f20a3a61355a448e522ab. Historical REI Rust coupled_primary.rs and atomic_provider.rs plus all 51 source files remain byte-identical; inherited original F08 source SHA12 and checkpoint SHA4 remain immutable. No REI owner, original worker or acceptance policy mutation.

Metric signature (-,+,+,+). ds²=-c²dt²+sum_i a_i(t)² dx_i², a_i=exp(H_i t), original prescribed Bianchi I H_i=(1.01,0.99,1)e-14 /s and FLRW H_i=(1,1,1)e-14 /s. Original F08 S0 source proper time starts at zero, step dt=625000000 seconds, nH(t)=1e-4 exp[-sum H_i t] cm^-3, fHe=.083. Original source initially 0.05 photons/H at 13.7 eV and continuously emits 5e-15 photons/H/s at the same birth energy, isotropically in each source proper matter rest frame. q directions are the original source 8×16 angular nodes, source birth q weights exp[-sum H_i*t_b]/g(q,t_b)^3 normalized, g(q,t)=sqrt(sum_i q_i² exp[-2 H_i t]). Exact photon characteristic E(q,t,t_b)=13.7eV * g(q,t)/g(q,t_b). Keep c=29979245800 cm/s, k_B=1.380649e-16 erg/K, and original Verner1996 photo cross sections and original H/He binding energies separate from numerical fit thresholds.

Two true continuous photon+HHe gas solutions start at the SAME original physical S0 initial state:
(A) source-preserving exact-energy characteristic packets with conserved q labels and birth tags.
(B) original source 17 fixed-grid hat energy remap plus original <10eV guard energy and photon number.
Each step: Bianchi redshift of all survivors; source injection with original q angular weights; unchanged source-pinned Rust primary_stage_step_conservative updates photon absorption, H/He non-equilibrium fractions, recombination/collisional events, thermal w and escaped energy. Each output gas state and each surviving packet are carried to the next step. Original StepControl max_iterations=200, residual_tolerance=1e-15, unchanged. No resetting gas to historical F08 values after step 1.

Source external evolution:
N_pre=N_previous+source_rate*dt.
U_pre=U_previous - redshift_work_step +13.7eV*source_rate*dt.
Native chemistry stage:
E_gas_pre+U_pre=E_gas_post+U_post+W_thermal_native_step.
Global cumulative:
0.05+source_rate*t=N_surviving(t)+N_photoabsorbed(t).
E_initial_gas+0.05*13.7eV+13.7eV*source_rate*t =
 E_final_gas+U_final_photons+W_redshift_cumulative+W_thermal_cumulative.
Matter energy E_gas=w+CHI_HI*xHII+fHe*(CHI_HeI*xHeII+(CHI_HeI+CHI_HeII)*xHeIII)+escaped.
Native stage HII identity: delta xHII = HI photo event + HI collisional event - HI recombination event.

Target: two original backgrounds times two photon representations times 160 actual consecutive original proper steps = 640 state records, plus 320 paired time response rows. Use original F08 saved S0 HHe time series first 160 rows for an external reference, not to reset gas. Source characteristics preserve physical energy support; original hat may leak energy below exact monochromatic null support. Preserve original physical source laws and original test gates. Retain 64-step prefix numerical replay and at least one scientifically appropriate small-step limiting and negative control.

Claim limitation: This is a new continuous model coupling exact S0 photons to the original source-owned Rust conservative microphysics but does NOT rerun the original interval-certified F08 paired_runtime MPRK/SDIRK source owner, nor reproduce F05 four-group 26event OTS or Einstein-constrained Bianchi geometry. New scientific rows are source-conditional and HOLD for canonical adoption. REI central 28/88, Working 33/88 nonadditive, Physical Fast 4/7; BASS upper 9/15 scoped/source-mapped, new fully accepted +0. F05 tick161 not accepted, F09 provider domain blocked. No merge, force push, source-owner mutation, tolerance relaxation or production. AUTO_NEXT=false.

Drift watchdog: This continuous coupled IVP is the genuinely new physical advance beyond BASS PR326 disjoint one-step evaluations. Do not proliferate unrelated ray/sky atlases. After data+verification+backup+Draft, stop at this bounded scope. Next REI original-owner decision is a controlled test of source-support-aware photon representation under all original photon/HHe/thermal interval ledgers and actual accepted canonical gates.
