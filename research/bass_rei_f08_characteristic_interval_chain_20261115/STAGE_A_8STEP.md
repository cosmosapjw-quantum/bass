# Stage-A R5/R7, C5/C6/C7 original characteristic packet and native interval root chain

Unit: BASS_REI_F08_S0_CHARACTERISTIC_8_CONSECUTIVE_SOURCE_ROOT_INTERVAL
Owner: BASS PR #331, base f61dcb4314eed3897106c0e6177f043c770325de
Inputs: original REI 13.7eV birth photons, 128 q rays, source rate 5e-15 photons/H/s, dt 625000000 s, original H/He microphysics, S0 BI/FLRW, original primary_stage_root.
Theory: true photon birth energy support E=E_b*g(q,t)/g(q,tb); analytic interval E_b exp(-Hmax age)<=E<=E_b exp(-Hmin age), original Rust interval exp. Previous gas and packet-N root bounds carried into next native root, no point-parent interval reset.

Actual numerical experiment: S0 BI 8/8 consecutive native roots PASS, S0 FLRW 8/8 PASS. The original PR328 characteristic photon/HHe point observables agree (xHII,HeII,HeIII,N within 2e-12, T within 5e-8 K). Native original root gas/packet count enclosure includes point at all steps, q<1; original StageControl(200,1e-15) unchanged. Hostile same-author independent stdlib audit: 4864 source-born packet records include valid original q, causal birth ages, correct energy analytic intervals, conserved photon point ledgers, no spurious spectral support below physical floor; 4/4 forged-negative cases rejected. Ordinary and Python -O auditor output byte identical.
Scientific claim: SOURCE_CONDITIONED_POINT_ENERGY_GAS_AND_NUMBER_INTERVAL_CHAIN_PASS_SCOPED for original finite 8 steps; physical support preserved at each packet. No formal q/energy interval influence propagated into gas root, no original 14 interval ledgers or global error theorem. REI owner F08 HOLD, production HOLD.

Reproduction:
  bash research/bass_rei_f08_characteristic_interval_chain_20261115/replay.sh 8 /tmp/bass_f08_chain_cold
  python3 research/bass_rei_f08_characteristic_interval_chain_20261115/audit_characteristic.py --dir /tmp/bass_f08_chain_cold --negative

DAG: REI central 28/88 reported; working 33/88 nonadditive; physical fast 4/7; BASS upper 9/15 scoped. Canonical Δ0, full BASS-upper Δ0. No merge/force push/source owner mutation/tolerance relaxation.
Next: run 32 original consecutive stages for each geometry and independent hostile science audit; extend only if original interval root remains within its unchanged guards. Watchdog: do not rebuild unrelated sky atlas or treat 8-source roots as original full F08 paired-runtime production admission.
