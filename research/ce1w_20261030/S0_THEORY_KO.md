# CE1-W S0 | BASS Rust + MPFR192 4/8/16-panel time error experiment

**Source and parent pin (2026-10-30 KST):** PR #266 final HEAD `2d5076ecb2307cea39c1b608396c34050021ebc3`, draft and unmerged. Its parent PR265 and exact rational donor PR264 remain unchanged. `_rustcore/src/kinetic/comoving.rs` Git blob `a29b12b5e7b0d529bddaf9eac53cfdb984ddaa84` is a true BASS-native Rust module (Frame::apply/det/phys_dirs).

## Unchanged physics / acceptance
Original six positive exact-binary angular cells: source SHA256 `022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`, eight coordinate reflections, massless collisionless all-expanding diagonal Bianchi I, Λ=0, signature (-,+,+,+), `u=t/Tstar`, `ell_i=ln a_i`, `h_i=dell_i/du`, shear (.2,-.13,-.07), horizon `u=.08`, strict accepted geometry h upper `1e-5`, MPFR192 directed interval. **Frozen same stored ray/mass arrays for GL6=216 and GL8=384 across all time step counts.** Do not resample source or use GL40 as a certificate.

## Fixed proven source forcing
PR264 exact-rational K=12 source upper:
GL6 `epsilon=3.010630537202566e-12` with exact fraction in committed immutable `research/ce1v_20261030/donor/GL6_source_exact_bound.json`;
GL8 `epsilon=6.164277064237367e-14`, similarly. Both valid for all 0<=ell_i<=.08. Stored GL6/8 SHA and physical source identity checked with PR266 `evidence_lock`. The donor exact fraction is passed to MPFR192 via directed `_iv_fraction`, NEVER rounded down to a binary64 decimal.

## Selected CE1-W scientific experiment
For panel steps N=4,8,16, compute `rk4_path(source, same_initial_state, .08, N)` with the original CE1-B Python RK4 oracle. For each exact-binary Hermite path:
1. Verify N panels and exact binary knot origins, monotone times, all-expanding Bernstein hull `0<=ell_i<.07`, h_i>0.
2. Call `residual_taylor_mpfr(source,path,j,subcells=1)` for every entire panel, preserving 4th-derivative majorant and MPFR192 rounding.
3. Add `_panel_endpoint_jump` at every original binary knot. Propagate unchanged initial, source and time/jump as three separately outward-rounded positive 2x2 Dini carriers with original `Pcap=1`. Never omit the knot jumps.
4. Report every panel residual/jump, exact path source/ray/mass SHA, runtime costs (RK4 generation, MPFR residuals, comparison) and terminal `max |Delta h|`.
5. Compare monotone reducing trends under same fixed time integrator; assert original 4-panel certificate is re-derived and new bounds remain below unchanged `1e-5`; **no a priori claim that 8 or 16 is faster/better**.
6. Actually compile original BASS Rust comoving frame with rustc1.94.1 and run E/P/Eprime parity at 41 matched proper-time samples for both sources and all three panel counts. This Rust diagnostic is binary64, never the certified MPFR192 remainder.

## Scientific trust
Parent PR266 final-head CI #40972935248 SUCCESS; historical final GL6 h upper `8.388531623506172e-7`; GL8 conservative `8.388529254004950e-7`, with cross-run RK4/Hermite byte identity NOT established. New experiment must record exact path SHA and explicitly distinguish scientific equation/ray identity from byte identity of generated numerical paths.

**Upper BASS DAG: 9/15 (21 edges), CE-1 PARTIAL**, new top-level completed nodes 0; production_ready=false, merge_ready=false, auto_next=false. No native subagent dispatch tool exposed in current inventory (NOT_RUN); no distinct-author independent review. No automatic merge. Local current-turn Python and container probes returned SERVICE_ERROR; use actual GitHub Actions, not a speculative local result.

Next S1: scientific code + tests + GitHub native Rust and MPFR CI; S2: analyze measured outputs, stage Git/Drive/Dropbox backup acknowledgements and final copyable handoff.
