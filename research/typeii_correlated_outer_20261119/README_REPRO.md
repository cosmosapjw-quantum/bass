# Reproducible BASS Type-II correlated-kernel and outer-matching research

Source branch research/bass-typeii-correlated-outer-20261119-r1, stacked on immutable PR341/55aa1a61ac66019f0901dd2cb02ddfdcbb5fca9c. Original BASS main 9c6506e4e2087129a8b674ff10438e5db1a55c9d. Only new research/typeii_correlated_outer_20261119 files are permitted in the PR; parent/main and production dispatch are protected.

Run from this Git worktree root with Python3, NumPy/SciPy, OpenBLAS and the parent source data in place:

export PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
p=research/typeii_correlated_outer_20261119
python3 "$p/test_correlated.py"
python3 "$p/verify_joint.py"
python3 "$p/outer_transport.py"
python3 "$p/verify_outer.py"

The initial source campaign reproduces six source cases with outer half-width 20, 40, 80, explicit factorized and frozen-source controls and a 128-time-step control. The additional exact files OUTER_REFINEMENT.json and MATCHED_BAND_REFINEMENT.json were produced by invoking outer_transport.evolve(X=40,steps=256/512,frozen=...,factorized=...) and evolve(X=20/80,steps=512); each invocation stores a named source TRACE.csv and RESULT.json.

All science checks are explicit raised exceptions; the unittest tests use unittest assertion methods. Run the tests under normal Python and python -O. Reproducibility of fixed-code source outputs should be checked by physical observables and SHA-256 where source byte identity is required. Prior source original BASS blob identity is strictly Git-locked to parent records.

The coherent Maxwell/Lorentz joint kernel is Hummer-II-inspired with dipole angular redistribution, leading recoil and an explicitly symmetrized finite-grid thermal pair rate, not the full quantum Hummer R_II operator. The six-point sky quadrature is low order; it is not the 26 source photon rays recast as sky integration. Scattering spectrum and angular joint shape is frozen at source start even when H, D, kappa, T_m and ionization fate evolve. Core ±20 boundary crossing and return are gross repeated rates, not terminal probabilities; only the selected outer boundary terminates tagged trajectories.

Output authority: FINAL_REPORT.md, STATUS.json, JOINT_KERNEL_RESULT.json, OUTER_MATCHING_RESULTS.json, OUTER_REFINEMENT.json, MATCHED_BAND_REFINEMENT.json, FINAL_VERIFICATION.json, NEXT_THREAD_HANDOFF.txt and host STAGE_RECEIPTS.tsv. No global Lyα escape, self-consistent photon-gas thermodynamics, exact line R_II, native HYREC population rerun, observed CMB visibility or production-ready result is claimed.

Stage preservation: PUBLISH_STAGE.sh commits only this research path, checks exact remote Git HEAD, creates Git-archive ZIP with CRC and SHA-256, and writes the receipt to /home/cosmosapjw/research_backups/bass_typeii_correlated_outer_20261119/. The fresh 4KB external NTFS/FUSE write probe returned ENOSPC with 1.8TB reported available; no further identical external write attempts should be made without an actual environment repair and user authorization.
