# Original BASS Type-II + native HYREC-2 H/He source experiment

## Immutable sources and scientific boundary

- Source parent PR #329 HEAD: 0bee79382753d95c610f5e86431f9e7c318c27d5
- Original BASS main: 9c6506e4e2087129a8b674ff10438e5db1a55c9d
- Existing source photon 401x26 CSV SHA256: 9f1400588d39ba3a61020542e14b0e372c8e9be1af130f8c64ed8829b23ad217
- External original HYREC-2 source: installed original CLASSIER v1_3 HyRec2020 at /home/cosmosapjw/src/TEFF_CLASSIER_CLEAN_BUILD_v1_3/external/HyRec2020. Source/headers/tables exact 18 SHA256 in HYREC2_NATIVE_SOURCE_REPORT.json.
- Native calibrated HYREC-2 input SHA256: ab6268cd2e4d1cf5380455035186d3607980fe6f47100059cf2da234ffec3cb3
- Native calibrated output table SHA256: 5a61a3f0a6219d6840c20624787c2ad50c0349561751bac97438a6f476aacb3f
- Original HYREC-2 8000-row distributed sample reproduced exactly by the original C standalone program.
- This research uses external **FLRW HYREC-2** H/He x_e(z), T_m(z) as a source-locked mean-scale-factor lookup on prescribed Type-II geometry, NOT a self-consistent HyRec Bianchi recombination solve.
- Native fluid gamma-law index 1.3, metric (-,+,+,+), Hubble time d tau_H=H dt_normal, normal-frame photon directions. H(0) remains an explicit FLRW anchor with h=.674, Omega_cb h^2=.143, Omega_b h^2=.0224, YHe=.245, Neff=3.046.
- The Class-A normal conserved hydrogen current N_H=n_Hrest Gamma=N_H(0) exp(-3 tau_H) and electron co-velocity u_e=u_fluid are conditional model hypotheses.

## Reproduction on the authorized owner host

Run from the exact repository root, with the local installed original HYREC-2 source in the path above. A missing different installation cannot be silently substituted as equivalent.

```bash
export PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
python3 research/typeii_hyrec2_history_20261102/run_native_hyrec2.py
python3 research/typeii_hyrec2_history_20261102/typeii_hyrec2_transport.py
python3 research/typeii_hyrec2_history_20261102/typeii_extended_window.py
python3 research/typeii_hyrec2_history_20261102/validate_extended_window.py
python3 research/typeii_hyrec2_history_20261102/model_sensitivity.py
python3 research/typeii_hyrec2_history_20261102/owner_electron_parity.py
python3 research/typeii_hyrec2_history_20261102/hostile_model_checks.py
python3 research/typeii_hyrec2_history_20261102/replay_verify.py
python3 research/typeii_hyrec2_history_20261102/science_figures.py
```

replay_verify.py executes the six source/physics programs both normal and python -O, checks 18 native original C/headers/atomic tables, original BASS 9 Git blobs, parent photon ray CSV, and byte identity of eleven derived science artifacts. Native compiled C binary, its scratch outputs and atomic-table symlinks are kept **only** in ignored research/typeii_hyrec2_history_20261102/native_run/, not committed.

## Physical results and source-conditioned mathematical contracts

- HYREC-2 genuine FLRW H/He x_e(1700)=0.99943036498 and x_e(1392)=0.78550743525; includes x_e>1 in early helium era and source T_m.
- In the original 401-state source window, Thomson depths are +e_y=29.004082003077855 and -e_y=31.95825274956412. This is external FLRW HYREC-2 reweighted by the original Type-II source H and conserved n_H normal current; NOT a native anisotropic recombination.
- At matched source n_H, H, T_CMB and normal-ray geometry, native HYREC-2 vs original hydrogen-only Saha changes depth by 0.73170269..0.80405865 over 26 rays.
- Genuine original Type-II gamma-law and 26 photon geodesic continuation to z_mean=300 produces 1167 timed background/ray samples, source parent 401-state overlap at ~1e-15, Codazzi max 2.78e-16, all positive omega/N1 and |v2|<1.
- Finite observer z_mean=300 attenuation depths: +e_y=42.92120264638825 and -e_y=47.19044021044179, conditional last-event kernel continuous z_mean peaks from 1068.522124 to 1074.888383 across 26 rays. Not observed z=0 CMB visibility.
- Independent five-ray Radau vs Gauss maximum absolute depth gap 6.04724e-9; 1167 vs 1933 temporal quadrature endpoint gap 2.20027e-10.
- Original BASS comoving electron object and transform_photon 401x26 evaluations: SI/CGS rate relative gap 6.66e-16, D absolute gap 0.
- Same-author hostile physics: double q changes axial depths by -1.40548 and +1.54869; missing Gamma max 0.03756; unconserved n_Hrest max 0.002415. No distinct-author review or native subagent.

## Claims and DAG

Source original BASS Bianchi geometry, native FLRW HyRec2 H/He x_e and Tm, original electron frame map are implementation-verified and source-conditioned numeric; NOT established: HyRec internal H(z) recomputed on TypeII q, joint Einstein–baryon–electron thermal closure, Thomson gain/redistribution/polarized hierarchy, today's observed CMB visibility, full RuntimePlan production dispatch, or StageII current canonical proof. BASS upper DAG 9/15 scoped/source-mapped, new fully complete upper production nodes 0, StageII 11/11 historical only, Join J1 0/2 FULL PASS HOLD. Draft PR only; no automatic merge.

Stage-by-stage Git commit/push/remote SHA and archive receipts are in owner-host /home/cosmosapjw/research_backups/bass_typeii_hyrec2_20261102/STAGE_RECEIPTS.tsv. This receipt verifies a durable artifact, not a production claim.
